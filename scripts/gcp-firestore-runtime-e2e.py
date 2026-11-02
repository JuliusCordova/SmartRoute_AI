#!/usr/bin/env python3
"""Bounded real Firestore synthetic integration using *impersonated runtime* ADC token.

ONLY database smartroute in project proyectopersonal-480420.
Creates a single driver, route and order, tests atomic assignment, then deletes
only these exact synthetic records in finally. No Firebase Auth bypass in the app.
"""
import os
import subprocess
import sys
from uuid import uuid4

PROJECT = "proyectopersonal-480420"
DATABASE = "smartroute"
RUNTIME = f"smartroute-runtime@{PROJECT}.iam.gserviceaccount.com"


def guard() -> None:
    if os.environ.get("FIRESTORE_EMULATOR_HOST"):
        raise RuntimeError("Emulator env is present; refusing real-database test")
    if os.environ.get("GOOGLE_CLOUD_PROJECT") != PROJECT:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT must be the exact approved project")
    if os.environ.get("FIRESTORE_DATABASE_ID") != DATABASE:
        raise RuntimeError("FIRESTORE_DATABASE_ID must equal 'smartroute'")
    if os.environ.get("CONFIRM_SMARTROUTE_FIRESTORE_TEST") != f"{PROJECT}/{DATABASE}":
        raise RuntimeError("Explicit Firestore write-test confirmation required")


def main() -> None:
    guard()
    from google.cloud import firestore
    from google.oauth2.credentials import Credentials
    from app.firestore_repo import FirestoreOrderRepository
    from app.firestore_routes import FirestoreRouteRepository
    from app.orders import Geo, OrderCreate, new_order
    from app.routes import RouteCreate, new_route

    # Uses ephemeral token minted for exact Cloud Run runtime identity. No keyfiles.
    # If operator lacks getAccessToken on runtime SA, fail without changing IAM.
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token",
         "--impersonate-service-account=" + RUNTIME,
         "--project=" + PROJECT],
        text=True, stderr=subprocess.DEVNULL,
    ).strip()
    if not token:
        raise RuntimeError("Unable to obtain short-lived runtime token")
    db = firestore.Client(
        project=PROJECT, database=DATABASE, credentials=Credentials(token=token)
    )
    if db.project != PROJECT or db._database != DATABASE:
        raise RuntimeError("Unexpected Firestore client configuration")
    print("PASS: database and impersonated runtime identity pinned; token not logged", flush=True)

    suffix = uuid4().hex
    driver_id = "smartroute-e2e-driver-" + suffix
    driver_ref = db.collection("drivers").document(driver_id)
    geo = Geo(latitude=-12.09, longitude=-77.04)
    order = new_order(OrderCreate(address_label="SYNTHETIC-E2E-" + suffix, geo=geo),
                      actor_uid="synthetic-e2e-operator")
    route = new_route(RouteCreate(driver_id=driver_id, depot=geo))
    order_ref = db.collection("orders").document(order.id)
    route_ref = db.collection("routes").document(route.id)
    # Conservative cleanup: only unique known IDs; no collection scans/deletes.
    refs = [order_ref, route_ref, driver_ref]
    try:
        driver_ref.create({"id": driver_id, "user_id": "synthetic-e2e",
                           "gps_consent": False, "data_origin": "synthetic"})
        FirestoreOrderRepository(db).create(order)
        assert order_ref.get().to_dict()["status"] == "PENDING"
        print("PASS: create/read synthetic order as runtime", flush=True)
        FirestoreRouteRepository(db).create(route)
        result = FirestoreRouteRepository(db).assign(route.id, [order.id])
        assert result["assigned"] == 1
        saved_order = order_ref.get().to_dict()
        saved_route = route_ref.get().to_dict()
        assert saved_order["status"] == "ASSIGNED"
        assert saved_order["route_id"] == route.id
        assert saved_order["version"] == 2
        assert saved_route["order_ids"] == [order.id]
        print("PASS: atomic synthetic route assignment and persisted read", flush=True)
    finally:
        cleanup_errors = []
        for ref in refs:
            try:
                ref.delete()
            except Exception as exc:
                cleanup_errors.append(f"{ref.id}: {type(exc).__name__}")
        if cleanup_errors:
            print("ERROR: manual cleanup required for synthetic IDs: " +
                  ", ".join(cleanup_errors), file=sys.stderr, flush=True)
            raise RuntimeError("Synthetic cleanup failed")
        print("PASS: removed only 3 uniquely identified synthetic test documents", flush=True)
    print("PASS: real Firestore named-database E2E with impersonated runtime", flush=True)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError:
        sys.exit("ERROR: cannot impersonate runtime SA; request narrow authorization, do not add broad IAM roles")
