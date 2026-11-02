"""US-009: deterministic, in-process route evaluation with a synthetic matrix.

Node 0 is the depot, nodes 1..N correspond to order_ids in baseline order.
This module does NOT call Google Maps, Gemini, Firestore or external services.
OR-Tools returns a feasible/best-found solution, not a proven global optimum.
"""
import hashlib
import json
from pydantic import BaseModel, ConfigDict, Field, model_validator
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


class MatrixInvalid(ValueError):
    pass


class RouteInfeasible(ValueError):
    pass


class EvaluationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_ids: list[str] = Field(min_length=1, max_length=10)
    durations_seconds: list[list[int]]
    data_origin: str = "synthetic"

    @model_validator(mode="after")
    def validate_fixture(self):
        if self.data_origin != "synthetic":
            raise ValueError("Only synthetic fixtures are permitted in this endpoint")
        if len(set(self.order_ids)) != len(self.order_ids):
            raise ValueError("order IDs must be unique")
        if any(not order_id or len(order_id) > 128 for order_id in self.order_ids):
            raise ValueError("invalid order ID")
        n = len(self.order_ids) + 1
        if len(self.durations_seconds) != n or any(len(row) != n for row in self.durations_seconds):
            raise ValueError("travel matrix must be square including depot")
        for i, row in enumerate(self.durations_seconds):
            for j, value in enumerate(row):
                if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 86400:
                    raise ValueError("travel durations must be integers between 0 and 86400 seconds")
                if i == j and value != 0:
                    raise ValueError("travel matrix diagonal must be zero")
        return self


class EvaluationResult(BaseModel):
    ordered_order_ids: list[str]
    baseline_seconds: int
    optimized_seconds: int
    improvement_pct: float
    matrix_fingerprint: str
    data_origin: str
    warnings: list[str]


def evaluate_synthetic_route(payload: EvaluationInput) -> EvaluationResult:
    matrix = payload.durations_seconds
    size = len(matrix)
    manager = pywrapcp.RoutingIndexManager(size, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def transit(from_index, to_index):
        return matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_idx = routing.RegisterTransitCallback(transit)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
    search = pywrapcp.DefaultRoutingSearchParameters()
    search.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    # Fixed solution budget prevents runaway compute: one feasible heuristic solution.
    search.solution_limit = 1
    solution = routing.SolveWithParameters(search)
    if solution is None:
        raise RouteInfeasible("No valid route found")

    current = routing.Start(0)
    visits = []
    while not routing.IsEnd(current):
        node = manager.IndexToNode(current)
        if node != 0:
            visits.append(node)
        current = solution.Value(routing.NextVar(current))
    if len(visits) != size - 1 or len(set(visits)) != size - 1:
        raise RouteInfeasible("Solver returned incomplete visit list")

    baseline_nodes = list(range(size)) + [0]
    baseline = sum(matrix[a][b] for a, b in zip(baseline_nodes, baseline_nodes[1:]))
    ordered_nodes = [0, *visits, 0]
    optimized = sum(matrix[a][b] for a, b in zip(ordered_nodes, ordered_nodes[1:]))
    # Never report a worse sequence as an improvement: retain baseline if needed.
    if optimized > baseline:
        visits = list(range(1, size))
        optimized = baseline
    improvement = round(100.0 * (baseline - optimized) / baseline, 2) if baseline else 0.0
    fingerprint = hashlib.sha256(
        json.dumps({"matrix": matrix, "order_ids": payload.order_ids},
                   sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return EvaluationResult(
        ordered_order_ids=[payload.order_ids[index - 1] for index in visits],
        baseline_seconds=baseline,
        optimized_seconds=optimized,
        improvement_pct=improvement,
        matrix_fingerprint=fingerprint,
        data_origin="synthetic",
        warnings=["Heuristic OR-Tools result; not proof of a global optimum",
                  "Synthetic cost matrix; not measured delivery performance"],
    )
