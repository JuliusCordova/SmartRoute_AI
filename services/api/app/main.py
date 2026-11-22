"""SmartRoute API: US-003/004, Firebase auth and Firestore Standard."""
from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from .auth import UserContext, require_operator, require_driver
from .orders import Order, OrderCreate, OrderPage, new_order
from .firestore_repo import FirestoreOrderRepository

app = FastAPI(title="SmartRoute AI", version="0.2.0")

@lru_cache(maxsize=1)
def get_repository() -> FirestoreOrderRepository:
    return FirestoreOrderRepository()

@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "smartroute-api"}

@app.get("/ready", tags=["health"])
def ready() -> dict[str, str]:
    return {"status": "ready", "scope": "process-only"}

@app.post("/api/v1/orders", response_model=Order, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(
    payload: OrderCreate,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreOrderRepository = Depends(get_repository),
):
    order = new_order(payload, actor_uid=actor.uid)
    try:
        repo.create(order)
    except Exception:
        raise HTTPException(status_code=503, detail="Order storage unavailable") from None
    return order

@app.get("/api/v1/orders", response_model=OrderPage, tags=["Orders"])
def list_orders(
    limit: int = Query(default=20, ge=1, le=50),
    cursor: str | None = Query(default=None, min_length=1, max_length=128),
    actor: UserContext = Depends(require_operator),
    repo: FirestoreOrderRepository = Depends(get_repository),
):
    try:
        return repo.list(limit=limit, after=cursor)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid pagination cursor") from None
    except Exception:
        raise HTTPException(status_code=503, detail="Order storage unavailable") from None

# US-005: Firestore routes and transactional assignment
from .routes import Route, RouteCreate, OrderAssignment, new_route, RecordMissing, AssignmentConflict
from .firestore_routes import FirestoreRouteRepository

@lru_cache(maxsize=1)
def get_route_repository() -> FirestoreRouteRepository:
    return FirestoreRouteRepository()

@app.post("/api/v1/routes", response_model=Route, status_code=201, tags=["Routes"])
def create_route(
    payload: RouteCreate,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreRouteRepository = Depends(get_route_repository),
):
    route = new_route(payload)
    try:
        repo.create(route)
    except RecordMissing as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Route storage unavailable") from None
    return route

@app.post("/api/v1/routes/{route_id}/orders", tags=["Routes"])
def assign_orders(
    route_id: str,
    payload: OrderAssignment,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreRouteRepository = Depends(get_route_repository),
):
    try:
        return repo.assign(route_id, payload.order_ids)
    except RecordMissing as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except AssignmentConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Route assignment unavailable") from None


# US-009 pilot: operator-only routing preview; no mutation of orders/routes.
from .route_preview import PreviewRequest, PreviewResult, compute_preview

@app.post("/api/v1/optimization/preview", response_model=PreviewResult, tags=["Optimization"])
def optimization_preview(payload: PreviewRequest, actor: UserContext = Depends(require_operator)):
    return compute_preview(payload)

# Address autocomplete for operator; key stays in private API runtime.
from .geocoding import AddressSuggestions, lookup_addresses

@app.get("/api/v1/geocoding/autocomplete", response_model=AddressSuggestions, tags=["Geocoding"])
def autocomplete_address(q: str = Query(min_length=3, max_length=120), actor: UserContext = Depends(require_operator)):
    return lookup_addresses(q)


# US-010: optimized route persistence; matrix is recomputed on private API.
from .optimized_routes import (
    OptimizedRoute, OptimizedRouteCreate, OptimizedRoutePage,
    OptimizedRouteConflict, OptimizedRouteMissing, OptimizedRouteDetail,
)
from .firestore_optimized_routes import FirestoreOptimizedRouteRepository

@lru_cache(maxsize=1)
def get_optimized_route_repository() -> FirestoreOptimizedRouteRepository:
    return FirestoreOptimizedRouteRepository()

@app.post("/api/v1/optimized-routes", response_model=OptimizedRoute, status_code=201, tags=["Optimized routes"])
def save_optimized_route(
    payload: OptimizedRouteCreate,
    response: Response,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreOptimizedRouteRepository = Depends(get_optimized_route_repository),
):
    try:
        route, created = repo.save(payload, actor_uid=actor.uid)
    except OptimizedRouteMissing as exc:
        raise HTTPException(404, str(exc)) from None
    except OptimizedRouteConflict as exc:
        raise HTTPException(409, str(exc)) from None
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Route storage unavailable") from None
    if not created:
        response.status_code = 200
    return route

@app.get("/api/v1/optimized-routes", response_model=OptimizedRoutePage, tags=["Optimized routes"])
def list_optimized_routes(
    limit: int = Query(default=20, ge=1, le=50),
    cursor: str | None = Query(default=None, min_length=1, max_length=128),
    actor: UserContext = Depends(require_operator),
    repo: FirestoreOptimizedRouteRepository = Depends(get_optimized_route_repository),
):
    try:
        return repo.list(limit=limit, after=cursor)
    except ValueError:
        raise HTTPException(422, "Invalid cursor") from None
    except Exception:
        raise HTTPException(503, "Route storage unavailable") from None

@app.get("/api/v1/optimized-routes/{route_id}", response_model=OptimizedRouteDetail, tags=["Optimized routes"])
def get_optimized_route(
    route_id: str,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreOptimizedRouteRepository = Depends(get_optimized_route_repository),
):
    try:
        return repo.detail(route_id)
    except OptimizedRouteMissing as exc:
        raise HTTPException(404, str(exc)) from None
    except Exception:
        raise HTTPException(503, "Route storage unavailable") from None


# US-011: driver assignment, only callable by an authenticated OPERATOR.
from .driver_assignment import AssignDriverRequest, DriverRoute, DriverPage
from .firestore_driver_assignment import (
    FirestoreDriverAssignmentRepository, DriverAssignmentConflict,
    DriverAssignmentMissing,
)

@lru_cache(maxsize=1)
def get_driver_assignment_repository() -> FirestoreDriverAssignmentRepository:
    return FirestoreDriverAssignmentRepository()

@app.post(
    "/api/v1/optimized-routes/{route_id}/assign-driver",
    response_model=OptimizedRoute, tags=["Driver assignment"],
)
def assign_optimized_route_driver(
    route_id: str,
    payload: AssignDriverRequest,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreDriverAssignmentRepository = Depends(get_driver_assignment_repository),
):
    try:
        return repo.assign(route_id, payload, operator_uid=actor.uid)
    except DriverAssignmentMissing as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except DriverAssignmentConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Driver assignment unavailable") from None


@app.get("/api/v1/driver/me/route", response_model=DriverRoute,
         responses={204: {"description": "No route assigned"}}, tags=["Driver route"])
def get_my_driver_route(
    response: Response,
    actor: UserContext = Depends(require_driver),
    repo: FirestoreDriverAssignmentRepository = Depends(get_driver_assignment_repository),
):
    try:
        route = repo.own_route(driver_uid=actor.uid)
    except DriverAssignmentConflict:
        raise HTTPException(status_code=409, detail="Assigned route unavailable") from None
    except Exception:
        raise HTTPException(status_code=503, detail="Driver route unavailable") from None
    if route is None:
        # Return an actual empty HTTP response, bypassing DriverRoute
        # response-model serialization for the no-assignment case.
        return Response(status_code=204)
    return route


@app.get("/api/v1/drivers", response_model=DriverPage, tags=["Driver assignment"])
def list_available_drivers(
    available: bool = Query(default=True),
    limit: int = Query(default=20, ge=1, le=20),
    cursor: str | None = Query(default=None, min_length=1, max_length=128),
    actor: UserContext = Depends(require_operator),
    repo: FirestoreDriverAssignmentRepository = Depends(get_driver_assignment_repository),
):
    if not available:
        raise HTTPException(status_code=422, detail="Only available drivers can be listed")
    try:
        return repo.list_available(limit=limit, after=cursor)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid driver cursor") from None
    except Exception:
        raise HTTPException(status_code=503, detail="Driver list unavailable") from None


# US-012/013/014: authenticated mobile DRIVER workflow.
from .driver_workflow import WorkflowRequest, StopResultRequest, RouteReceipt, StopReceipt
from .qa_write_guard import QaWriteGuardDenied
from .firestore_driver_workflow import (
    FirestoreDriverWorkflowRepository, WorkflowConflict, WorkflowMissing,
)


@lru_cache(maxsize=1)
def get_driver_workflow_repository() -> FirestoreDriverWorkflowRepository:
    return FirestoreDriverWorkflowRepository()


def _execute_driver_workflow(
    *, actor: UserContext, action: str, payload: WorkflowRequest | StopResultRequest,
    repo: FirestoreDriverWorkflowRepository, order_id: str | None = None,
):
    try:
        return repo.execute(driver_uid=actor.uid, action=action, payload=payload, order_id=order_id)
    except WorkflowMissing as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except WorkflowConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    except QaWriteGuardDenied:
        raise HTTPException(status_code=403, detail="Driver write not permitted in QA") from None
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Driver workflow unavailable") from None


@app.post("/api/v1/driver/me/route/start", response_model=RouteReceipt,
          tags=["Driver workflow"])
def start_my_route(
    payload: WorkflowRequest,
    actor: UserContext = Depends(require_driver),
    repo: FirestoreDriverWorkflowRepository = Depends(get_driver_workflow_repository),
):
    return _execute_driver_workflow(
        actor=actor, action="start", payload=payload, repo=repo,
    )


@app.post("/api/v1/driver/me/route/stops/{order_id}/deliver",
          response_model=StopReceipt, tags=["Driver workflow"])
def deliver_my_stop(
    order_id: str, payload: StopResultRequest,
    actor: UserContext = Depends(require_driver),
    repo: FirestoreDriverWorkflowRepository = Depends(get_driver_workflow_repository),
):
    return _execute_driver_workflow(
        actor=actor, action="deliver", payload=payload, repo=repo, order_id=order_id,
    )


@app.post("/api/v1/driver/me/route/stops/{order_id}/fail",
          response_model=StopReceipt, tags=["Driver workflow"])
def fail_my_stop(
    order_id: str, payload: StopResultRequest,
    actor: UserContext = Depends(require_driver),
    repo: FirestoreDriverWorkflowRepository = Depends(get_driver_workflow_repository),
):
    return _execute_driver_workflow(
        actor=actor, action="fail", payload=payload, repo=repo, order_id=order_id,
    )


@app.post("/api/v1/driver/me/route/complete", response_model=RouteReceipt,
          tags=["Driver workflow"])
def complete_my_route(
    payload: WorkflowRequest,
    actor: UserContext = Depends(require_driver),
    repo: FirestoreDriverWorkflowRepository = Depends(get_driver_workflow_repository),
):
    return _execute_driver_workflow(
        actor=actor, action="complete", payload=payload, repo=repo,
    )


# US-017: persistent operator-managed distribution center catalog.
from .distribution_centers import (
    CenterCreate, CenterUpdate, CenterDeactivate, DistributionCenter, CenterPage,
    CenterNotFound, CenterConflict,
)
from .firestore_distribution_centers import FirestoreCenterRepository

@lru_cache(maxsize=1)
def get_center_repository() -> FirestoreCenterRepository:
    return FirestoreCenterRepository()


@app.post("/api/v1/distribution-centers", response_model=DistributionCenter, status_code=201, tags=["Distribution centers"])
def add_distribution_center(
    payload: CenterCreate,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreCenterRepository = Depends(get_center_repository),
):
    try:
        return repo.create(payload, actor_uid=actor.uid)
    except CenterConflict as exc:
        raise HTTPException(409, str(exc)) from None
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    except Exception:
        raise HTTPException(503, "Distribution center storage unavailable") from None


@app.get("/api/v1/distribution-centers", response_model=CenterPage, tags=["Distribution centers"])
def list_distribution_centers(
    limit: int = Query(default=20, ge=1, le=50),
    cursor: str | None = Query(default=None, min_length=1, max_length=128),
    actor: UserContext = Depends(require_operator),
    repo: FirestoreCenterRepository = Depends(get_center_repository),
):
    try:
        return repo.list(limit=limit, after=cursor)
    except ValueError:
        raise HTTPException(422, "Invalid distribution center cursor") from None
    except Exception:
        raise HTTPException(503, "Distribution center storage unavailable") from None


@app.get("/api/v1/distribution-centers/{center_id}", response_model=DistributionCenter, tags=["Distribution centers"])
def get_distribution_center(
    center_id: str,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreCenterRepository = Depends(get_center_repository),
):
    try:
        return repo.get(center_id)
    except CenterNotFound as exc:
        raise HTTPException(404, str(exc)) from None
    except Exception:
        raise HTTPException(503, "Distribution center storage unavailable") from None


@app.put("/api/v1/distribution-centers/{center_id}", response_model=DistributionCenter, tags=["Distribution centers"])
def update_distribution_center(
    center_id: str, payload: CenterUpdate,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreCenterRepository = Depends(get_center_repository),
):
    try:
        return repo.update(center_id, payload)
    except CenterNotFound as exc:
        raise HTTPException(404, str(exc)) from None
    except CenterConflict as exc:
        raise HTTPException(409, str(exc)) from None
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    except Exception:
        raise HTTPException(503, "Distribution center storage unavailable") from None


@app.delete("/api/v1/distribution-centers/{center_id}", response_model=DistributionCenter, tags=["Distribution centers"])
def deactivate_distribution_center(
    center_id: str, payload: CenterDeactivate,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreCenterRepository = Depends(get_center_repository),
):
    try:
        return repo.deactivate(center_id, expected_version=payload.expected_version)
    except CenterNotFound as exc:
        raise HTTPException(404, str(exc)) from None
    except CenterConflict as exc:
        raise HTTPException(409, str(exc)) from None
    except Exception:
        raise HTTPException(503, "Distribution center storage unavailable") from None


# US-V1-008: consented GPS on ACTIVE assigned route, operator reads latest fix.
from .driver_location import GPSFix, GPSReceipt, LastGPS, GPSDenied, GPSMissing
from .firestore_driver_location import FirestoreDriverLocationRepository

@lru_cache(maxsize=1)
def get_driver_location_repository() -> FirestoreDriverLocationRepository:
    return FirestoreDriverLocationRepository()


@app.post("/api/v1/driver/me/location", response_model=GPSReceipt, tags=["GPS"])
def report_driver_location(
    payload: GPSFix,
    actor: UserContext = Depends(require_driver),
    repo: FirestoreDriverLocationRepository = Depends(get_driver_location_repository),
):
    try:
        return repo.record(driver_uid=actor.uid, fix=payload)
    except (GPSDenied, QaWriteGuardDenied) as exc:
        raise HTTPException(403, str(exc)) from None
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    except Exception:
        raise HTTPException(503, "GPS storage unavailable") from None


@app.get("/api/v1/routes/{route_id}/location", response_model=LastGPS, tags=["GPS"])
def get_last_driver_location(
    route_id: str,
    actor: UserContext = Depends(require_operator),
    repo: FirestoreDriverLocationRepository = Depends(get_driver_location_repository),
):
    try:
        return repo.latest(route_id=route_id)
    except GPSMissing as exc:
        raise HTTPException(404, str(exc)) from None
    except Exception:
        raise HTTPException(503, "GPS lookup unavailable") from None
