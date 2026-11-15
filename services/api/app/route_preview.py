"""Operator-only road-matrix preview; no Firestore writes.

Coordinates are synthetic pilot inputs. Travel times/distances are road estimates
from openrouteservice, not observed savings. Secrets remain server-side.
"""
import hashlib
import json
import math
import os

import httpx
from fastapi import HTTPException
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from pydantic import BaseModel, ConfigDict, Field, model_validator

ORS_MATRIX = "https://api.heigit.org/openrouteservice/v2/matrix/driving-car"
ORS_DIRECTIONS = "https://api.heigit.org/openrouteservice/v2/directions/driving-car/geojson"


class StopPoint(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: str = Field(min_length=1, max_length=128)
    latitude: float = Field(ge=-12.30, le=-11.80, allow_inf_nan=False)
    longitude: float = Field(ge=-77.20, le=-76.80, allow_inf_nan=False)


class PreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    depot: StopPoint
    stops: list[StopPoint] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def distinct(self):
        points = [self.depot, *self.stops]
        if len({p.id for p in points}) != len(points):
            raise ValueError("Duplicate point id")
        if len({(p.latitude, p.longitude) for p in points}) != len(points):
            raise ValueError("Duplicate coordinates")
        return self


class PreviewResult(BaseModel):
    ordered_order_ids: list[str]
    baseline_seconds: int
    optimized_seconds: int
    baseline_meters: int
    optimized_meters: int
    improvement_pct: float
    matrix_fingerprint: str
    data_origin: str = "estimated"
    matrix_provider: str = "openrouteservice"
    route_geometry: list[list[float]] | None = None
    warnings: list[str]


def _sum_cycle(matrix, visits):
    path = [0, *visits, 0]
    return sum(matrix[a][b] for a, b in zip(path, path[1:]))


def compute_preview(req: PreviewRequest, *, api_key: str | None = None) -> PreviewResult:
    key = api_key or os.getenv("ORS_API_KEY")
    if not key:
        raise HTTPException(503, "Road matrix provider not configured")
    nodes = [req.depot, *req.stops]
    coords = [[n.longitude, n.latitude] for n in nodes]
    headers = {"Authorization": key, "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=12.0) as client:
            response = client.post(ORS_MATRIX, json={"locations": coords, "metrics": ["duration", "distance"]}, headers=headers)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, "Road matrix provider unavailable") from None

    n = len(nodes)
    durations, distances = payload.get("durations"), payload.get("distances")
    if (not isinstance(durations, list) or not isinstance(distances, list)
        or len(durations) != n or len(distances) != n
        or any(not isinstance(row, list) or len(row) != n for row in durations + distances)):
        raise HTTPException(422, "ROUTE_INFEASIBLE: incomplete matrix")

    def normalize(matrix):
        out = []
        for i, row in enumerate(matrix):
            clean = []
            for j, value in enumerate(row):
                if not isinstance(value, (float, int)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
                    raise HTTPException(422, "ROUTE_INFEASIBLE: unreachable stop")
                if i == j and value != 0:
                    raise HTTPException(422, "ROUTE_INFEASIBLE: invalid matrix diagonal")
                clean.append(round(value))
            out.append(clean)
        return out

    seconds, meters = normalize(durations), normalize(distances)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def travel(i, j):
        return seconds[manager.IndexToNode(i)][manager.IndexToNode(j)]

    callback = routing.RegisterTransitCallback(travel)
    routing.SetArcCostEvaluatorOfAllVehicles(callback)
    search = pywrapcp.DefaultRoutingSearchParameters()
    search.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search.time_limit.seconds = 3
    solution = routing.SolveWithParameters(search)
    if solution is None:
        raise HTTPException(422, "ROUTE_INFEASIBLE: no route found")
    current, visits = routing.Start(0), []
    while not routing.IsEnd(current):
        idx = manager.IndexToNode(current)
        if idx:
            visits.append(idx)
        current = solution.Value(routing.NextVar(current))
    if len(visits) != n-1 or len(set(visits)) != n-1:
        raise HTTPException(422, "ROUTE_INFEASIBLE: incomplete solution")

    base = list(range(1, n))
    if _sum_cycle(seconds, visits) > _sum_cycle(seconds, base):
        visits = base
    fingerprint = hashlib.sha256(json.dumps({"nodes": [p.model_dump() for p in nodes], "seconds": seconds, "meters": meters}, sort_keys=True).encode()).hexdigest()
    baseline_s, optimized_s = _sum_cycle(seconds, base), _sum_cycle(seconds, visits)
    route_geometry = None
    warnings = ["Estimated road travel times; not observed delivery outcomes", "OR-Tools best-found solution; no global optimality guarantee"]
    # Optional road-snapped geometry, best effort. Never replace route computation when it fails.
    try:
        order = [0, *visits, 0]
        with httpx.Client(timeout=8.0) as client:
            path_resp = client.post(ORS_DIRECTIONS, json={"coordinates": [coords[i] for i in order]}, headers=headers)
            path_resp.raise_for_status()
            segments = path_resp.json().get("features", [])
        if segments and isinstance(segments[0].get("geometry", {}).get("coordinates"), list):
            route_geometry = segments[0]["geometry"]["coordinates"]
    except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError):
        warnings.append("Road path geometry unavailable; map may show straight connectors")
    return PreviewResult(
        ordered_order_ids=[req.stops[i-1].id for i in visits],
        baseline_seconds=baseline_s,
        optimized_seconds=optimized_s,
        baseline_meters=_sum_cycle(meters, base),
        optimized_meters=_sum_cycle(meters, visits),
        improvement_pct=round(100*(baseline_s-optimized_s)/baseline_s, 2) if baseline_s else 0,
        matrix_fingerprint=fingerprint,
        route_geometry=route_geometry,
        warnings=warnings,
    )
