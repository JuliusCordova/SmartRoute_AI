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


# US-012: start only the authenticated DRIVER's reserved optimized route.
from .route_execution import (
    StartRouteRequest, RouteExecutionResult,
    RouteExecutionMissing, RouteExecutionConflict,
)
from .firestore_route_execution import FirestoreRouteExecutionRepository

@lru_cache(maxsize=1)
def get_route_execution_repository() -> FirestoreRouteExecutionRepository:
    return FirestoreRouteExecutionRepository()

@app.post("/api/v1/driver/me/route/start", response_model=RouteExecutionResult,
          tags=["Route execution"])
def start_my_driver_route(
    payload: StartRouteRequest,
    actor: UserContext = Depends(require_driver),
    repo: FirestoreRouteExecutionRepository = Depends(get_route_execution_repository),
):
    try:
        return repo.start(driver_uid=actor.uid, payload=payload)
    except RouteExecutionMissing as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except RouteExecutionConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Route execution unavailable") from None
