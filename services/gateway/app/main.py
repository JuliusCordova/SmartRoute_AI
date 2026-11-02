"""Public *Firebase-authenticated* edge; private API stays behind Cloud Run IAM.

The Android/browser client NEVER sees an IAM token. The gateway verifies Firebase
and uses its own Cloud Run service identity to invoke the private backend.
"""
import asyncio
import os
import re
from functools import lru_cache

import firebase_admin
from firebase_admin import auth
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token
import httpx

PROJECT = "proyectopersonal-480420"
PRIVATE_API_URL = "https://smartroute-api-staging-913797829604.us-central1.run.app"
ORDER_PATH = re.compile(r"^/api/v1/orders$")
ROUTE_PATH = re.compile(r"^/api/v1/routes$")
ASSIGN_PATH = re.compile(r"^/api/v1/routes/[0-9a-fA-F-]{36}/orders$")
MAX_BODY = 16_384
ALLOWED = {
    ("GET", "/api/v1/orders"),
    ("POST", "/api/v1/orders"),
    ("POST", "/api/v1/routes"),
}
app = FastAPI(title="SmartRoute authenticated gateway", docs_url=None, redoc_url=None,
              openapi_url=None)


def require_config() -> None:
    if os.getenv("GOOGLE_CLOUD_PROJECT") != PROJECT:
        raise RuntimeError("Gateway pinned to approved project")
    if os.getenv("SMARTROUTE_BACKEND_URL") != PRIVATE_API_URL:
        raise RuntimeError("Gateway pinned to approved private Cloud Run backend")
    if os.getenv("SMARTROUTE_GATEWAY_ENABLED") != "true":
        raise RuntimeError("Gateway not enabled")


@lru_cache(maxsize=1)
def firebase_app():
    return firebase_admin.initialize_app(
        name="smartroute-gateway", options={"projectId": PROJECT}
    )


def verified_firebase_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Firebase bearer token required")
    token = authorization[7:].strip()
    if not token or len(token) > 4096 or any(ch.isspace() for ch in token):
        raise HTTPException(401, "Invalid Firebase bearer token")
    try:
        decoded = auth.verify_id_token(token, app=firebase_app(), check_revoked=False)
        if not isinstance(decoded.get("uid"), str) or not decoded["uid"]:
            raise ValueError("UID missing")
    except Exception:
        raise HTTPException(401, "Invalid Firebase identity") from None
    return token


def private_id_token() -> str:
    # Google-signed token is obtained from metadata/ADC on Cloud Run and never
    # returned to client. No service account keys or token in logs.
    return id_token.fetch_id_token(GoogleAuthRequest(), PRIVATE_API_URL)


@app.get("/health")
def health():
    return {"status": "ok", "service": "smartroute-gateway"}


@app.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(path: str, request: Request):
    try:
        require_config()
    except RuntimeError:
        raise HTTPException(503, "Gateway not configured") from None

    target_path = "/api/v1/" + path
    if ((request.method, target_path) not in ALLOWED
            and not (request.method == "POST" and ASSIGN_PATH.fullmatch(target_path))):
        raise HTTPException(404, "Endpoint not supported")

    # A native client may omit Origin. Browser cross-origin access is denied
    # unless specifically configured, with no wildcard origin.
    origin = request.headers.get("origin")
    origins = {x.strip() for x in os.getenv("SMARTROUTE_ALLOWED_ORIGINS", "").split(",") if x.strip()}
    if origin is not None and origin not in origins:
        raise HTTPException(403, "Origin not allowed")

    firebase_token = verified_firebase_token(request.headers.get("authorization"))
    if request.headers.get("content-length"):
        try:
            if int(request.headers["content-length"]) > MAX_BODY:
                raise HTTPException(413, "Request too large")
        except ValueError:
            raise HTTPException(400, "Invalid Content-Length") from None
    body = await request.body()
    if len(body) > MAX_BODY:
        raise HTTPException(413, "Request too large")

    try:
        iam_token = await asyncio.to_thread(private_id_token)
        # Explicit header allowlist. No forwarding of arbitrary headers, cookies,
        # Host or caller-controlled IAM Authorization.
        headers = {
            "X-Serverless-Authorization": "Bearer " + iam_token,
            "Authorization": "Bearer " + firebase_token,
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
            upstream = await client.request(
                method=request.method,
                url=PRIVATE_API_URL + target_path,
                params=request.query_params,
                content=body if request.method != "GET" else None,
                headers=headers,
            )
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, "Private API unavailable") from None
    except Exception:
        raise HTTPException(503, "Gateway credentials unavailable") from None

    # Bound only response content and type; never forward Set-Cookie or backend
    # internal headers. API response data is from the authenticated backend.
    output_headers = {"Cache-Control": "no-store"}
    if origin in origins:
        output_headers["Access-Control-Allow-Origin"] = origin
        output_headers["Vary"] = "Origin"
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type="application/json",
        headers=output_headers,
    )


@app.options("/api/v1/{path:path}")
def preflight(path: str, request: Request):
    origin = request.headers.get("origin")
    origins = {x.strip() for x in os.getenv("SMARTROUTE_ALLOWED_ORIGINS", "").split(",") if x.strip()}
    method = request.headers.get("access-control-request-method", "")
    target_path = "/api/v1/" + path
    if origin not in origins or (
        (method, target_path) not in ALLOWED
        and not (method == "POST" and ASSIGN_PATH.fullmatch(target_path))
    ):
        raise HTTPException(403, "CORS preflight not allowed")
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": method,
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
        "Access-Control-Max-Age": "300",
        "Vary": "Origin",
    })
