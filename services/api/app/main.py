"""SmartRoute API: US-003/004, Firebase auth and Firestore Standard."""
from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException, Query, status
from .auth import UserContext, require_operator
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
