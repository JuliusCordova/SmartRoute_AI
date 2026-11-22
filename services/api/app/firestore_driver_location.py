"""Last-only GPS projection. No GPS history, no background access."""
from datetime import datetime, timezone
from google.cloud import firestore

from .firestore_config import firestore_client
from .qa_write_guard import enforce_qa_write_guard
from .driver_location import GPSFix, GPSReceipt, LastGPS, GPSDenied, GPSMissing, freshness


class FirestoreDriverLocationRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    def record(self, *, driver_uid: str, fix: GPSFix) -> GPSReceipt:
        if not driver_uid or "/" in driver_uid or len(driver_uid)>128 or "/" in fix.route_id:
            raise GPSDenied("Invalid driver or route")
        enforce_qa_write_guard(driver_uid=driver_uid, route_id=fix.route_id)
        driver_ref=self.db.collection("drivers").document(driver_uid)
        user_ref=self.db.collection("users").document(driver_uid)
        booking_ref=self.db.collection("driver_assignments").document(driver_uid)
        route_ref=self.db.collection("routes").document(fix.route_id)
        location_ref=self.db.collection("driver_last_locations").document(fix.route_id)

        @firestore.transactional
        def commit(tx):
            user=user_ref.get(transaction=tx)
            driver=driver_ref.get(transaction=tx)
            booking=booking_ref.get(transaction=tx)
            route=route_ref.get(transaction=tx)
            prior=location_ref.get(transaction=tx)
            if (not user.exists or not driver.exists or
                (user.to_dict() or {}).get("role")!="DRIVER" or
                (user.to_dict() or {}).get("active") is not True or
                (driver.to_dict() or {}).get("active") is not True):
                raise GPSDenied("Driver identity invalid")
            b=booking.to_dict() if booking.exists else {}
            r=route.to_dict() if route.exists else {}
            if (b.get("driver_id")!=driver_uid or b.get("route_id")!=fix.route_id or b.get("status")!="ACTIVE"
                or r.get("driver_id")!=driver_uid or r.get("status")!="ACTIVE" or r.get("route_type")!="OPTIMIZED"):
                raise GPSDenied("GPS only permitted on active assigned route")
            old=prior.to_dict() if prior.exists else {}
            if old.get("captured_at") and old["captured_at"]>fix.captured_at:
                raise GPSDenied("Out of order GPS fix")
            now=datetime.now(timezone.utc)
            tx.set(location_ref,{
                "route_id":fix.route_id,"driver_id":driver_uid,
                "latitude":fix.latitude,"longitude":fix.longitude,
                "accuracy_m":fix.accuracy_m,"captured_at":fix.captured_at,"stored_at":now,
                "data_origin":"observed",
            })
            return GPSReceipt(route_id=fix.route_id,stored_at=now)
        return commit(self.db.transaction())

    def latest(self, *, route_id: str) -> LastGPS:
        if not route_id or "/" in route_id or len(route_id)>128:
            raise GPSMissing("Route not found")
        route=self.db.collection("routes").document(route_id).get()
        if not route.exists or (route.to_dict() or {}).get("status")!="ACTIVE":
            raise GPSMissing("No live location available")
        snap=self.db.collection("driver_last_locations").document(route_id).get()
        if not snap.exists:
            raise GPSMissing("No GPS fix recorded")
        data=snap.to_dict() or {}
        if data.get("driver_id")!=(route.to_dict() or {}).get("driver_id"):
            raise GPSMissing("Location owner mismatch")
        return LastGPS(**{k:data[k] for k in ("route_id","driver_id","latitude","longitude","accuracy_m","captured_at","stored_at")},
                       status=freshness(data["captured_at"]))
