"""Firestore Emulator integration: conflict and no partial writes (no GCP billing)."""
import os
from uuid import uuid4
import pytest

def test_atomic_assignment_rejects_second_route():
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        if os.environ.get("FIRESTORE_EMULATOR_REQUIRED")=="1":
            pytest.fail("FIRESTORE_EMULATOR_HOST required for integration")
        pytest.skip("Requires Firebase Firestore emulator")
    from google.cloud import firestore
    from app.firestore_routes import FirestoreRouteRepository
    from app.routes import RouteCreate, new_route, AssignmentConflict
    from app.orders import OrderCreate, new_order

    db=firestore.Client(project="demo-smartroute")
    repo=FirestoreRouteRepository(db)
    suffix=uuid4().hex[:12]
    driver_id="synthetic-driver-"+suffix
    db.collection("drivers").document(driver_id).set({"id":driver_id,"user_id":"synthetic","gps_consent":False})
    from app.orders import Geo
    route1=new_route(RouteCreate(driver_id=driver_id,depot=Geo(latitude=-12.09,longitude=-77.04)))
    route2=new_route(RouteCreate(driver_id=driver_id,depot=Geo(latitude=-12.09,longitude=-77.04)))
    repo.create(route1)
    repo.create(route2)
    order=new_order(OrderCreate(address_label="Synthetic stop "+suffix,
                               geo=Geo(latitude=-12.09,longitude=-77.04)),actor_uid="synthetic")
    db.collection("orders").document(order.id).create(order.model_dump(mode="python"))

    output=repo.assign(route1.id,[order.id])
    assert output["assigned"]==1
    with pytest.raises(AssignmentConflict):
        repo.assign(route2.id,[order.id])
    snap=db.collection("orders").document(order.id).get().to_dict()
    assert snap["route_id"]==route1.id and snap["status"]=="ASSIGNED" and snap["version"]==2
    assert db.collection("routes").document(route1.id).get().to_dict()["order_ids"]==[order.id]
    assert db.collection("routes").document(route2.id).get().to_dict()["order_ids"]==[]
