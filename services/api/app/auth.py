"""Firebase ID token verification and SERVER-SIDE role lookup."""
import os
from dataclasses import dataclass
from functools import lru_cache
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)

@dataclass(frozen=True)
class UserContext:
    uid: str
    role: str

@lru_cache(maxsize=1)
def _firebase_app():
    import firebase_admin
    project_id = os.environ.get("FIREBASE_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise RuntimeError("FIREBASE_PROJECT_ID or GOOGLE_CLOUD_PROJECT is required")
    if not firebase_admin._apps:
        return firebase_admin.initialize_app(options={"projectId": project_id})
    return firebase_admin.get_app()

def current_user(credentials: HTTPAuthorizationCredentials | None = Security(bearer)) -> UserContext:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    try:
        from firebase_admin import auth
        from .firestore_config import firestore_client
        decoded = auth.verify_id_token(credentials.credentials, app=_firebase_app(), check_revoked=False)
        uid = decoded.get("uid")
        if not uid or not isinstance(uid, str):
            raise ValueError("Firebase token missing UID")
        profile = firestore_client().collection("users").document(uid).get()
        if not profile.exists:
            raise HTTPException(status_code=403, detail="User not registered")
        data = profile.to_dict() or {}
        if data.get("active") is not True or data.get("role") not in ("OPERATOR", "DRIVER"):
            raise HTTPException(status_code=403, detail="User not permitted")
        return UserContext(uid=uid, role=data["role"])
    except HTTPException:
        raise
    except (ValueError, RuntimeError):
        raise HTTPException(status_code=401, detail="Invalid identity or auth configuration") from None
    except Exception:
        raise HTTPException(status_code=503, detail="Identity service unavailable") from None

def require_operator(user: UserContext = Security(current_user)) -> UserContext:
    if user.role != "OPERATOR":
        raise HTTPException(status_code=403, detail="Operator role required")
    return user
