"""US-016 gateway tests: public tracking is the only bearer-free, opt-in path."""
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app, PRIVATE_API_URL
import httpx

client=TestClient(app)
ENV={
 "GOOGLE_CLOUD_PROJECT":"proyectopersonal-480420",
 "SMARTROUTE_BACKEND_URL":PRIVATE_API_URL,
 "SMARTROUTE_GATEWAY_ENABLED":"true",
 "SMARTROUTE_ALLOWED_ORIGINS":"https://customer.example",
}

def test_public_tracking_is_disabled_by_default():
    with patch.dict(os.environ,ENV,clear=True), patch("app.main.private_id_token") as mint:
        response=client.post("/api/v1/public/tracking",json={"token":"x"*43})
        assert response.status_code==404
        mint.assert_not_called()

def test_only_public_tracking_skips_firebase():
    observed={}
    async def fake_request(self, *, method, url, params, content, headers):
        observed.update({"url":url,"headers":headers,"body":content})
        return httpx.Response(200,json={"order_reference":"fake","status":"IN_TRANSIT","eta_minutes":None})
    with patch.dict(os.environ,{**ENV,"SMARTROUTE_PUBLIC_TRACKING_ENABLED":"true"},clear=True), \
         patch("app.main.private_id_token",return_value="iam"), \
         patch("app.main.httpx.AsyncClient.request",new=fake_request), \
         patch("app.main.verified_firebase_token") as firebase:
        response=client.post("/api/v1/public/tracking",
            headers={"Origin":"https://customer.example"},json={"token":"x"*43})
        assert response.status_code==200
        assert observed["url"]==PRIVATE_API_URL+"/api/v1/public/tracking"
        assert "Authorization" not in observed["headers"]
        assert observed["headers"]["X-Serverless-Authorization"]=="Bearer iam"
        assert response.headers["cache-control"]=="no-store"
        firebase.assert_not_called()
        from fastapi import HTTPException
        firebase.side_effect = HTTPException(401, "Firebase required")
        assert client.get("/api/v1/orders").status_code==401
        firebase.assert_called_once()

def test_unknown_origin_or_method_rejected_before_iam():
    with patch.dict(os.environ,{**ENV,"SMARTROUTE_PUBLIC_TRACKING_ENABLED":"true"},clear=True), \
         patch("app.main.private_id_token") as mint:
        assert client.post("/api/v1/public/tracking",headers={"Origin":"https://wrong.example"},json={"token":"x"*43}).status_code==403
        assert client.get("/api/v1/public/tracking").status_code==404
        assert client.post("/api/v1/public/tracking/anything",json={"token":"x"*43}).status_code==404
        mint.assert_not_called()
