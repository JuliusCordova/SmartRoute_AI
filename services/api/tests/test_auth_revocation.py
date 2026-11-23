"""SEC-01: Firebase revocation must be enforced by the private API too.

Uses mocked Firebase Auth and Firestore; no external calls or real credentials.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from firebase_admin import auth

from app.auth import current_user


def credential(value="fixture"):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=value)


@pytest.mark.parametrize(
    "denied_error",
    [
        auth.RevokedIdTokenError("Token revoked"),
        auth.UserDisabledError("User disabled"),
        auth.InvalidIdTokenError("Invalid token"),
    ],
)
def test_sec01_revoked_disabled_or_invalid_token_returns_401(denied_error):
    with (
        patch("app.auth._firebase_app", return_value=object()),
        patch("firebase_admin.auth.verify_id_token", side_effect=denied_error) as verify,
        patch("app.firestore_config.firestore_client") as db,
    ):
        with pytest.raises(HTTPException) as caught:
            current_user(credential())
    assert caught.value.status_code == 401
    assert caught.value.detail == "Invalid identity or auth configuration"
    assert verify.call_args.kwargs["check_revoked"] is True
    db.assert_not_called()


def test_sec01_valid_token_still_resolves_role_after_revocation_check():
    db = MagicMock()
    profile = db.collection.return_value.document.return_value.get.return_value
    profile.exists = True
    profile.to_dict.return_value = {"role": "DRIVER", "active": True}
    with (
        patch("app.auth._firebase_app", return_value=object()),
        patch("firebase_admin.auth.verify_id_token", return_value={"uid":"synthetic-driver"}) as verify,
        patch("app.firestore_config.firestore_client", return_value=db),
    ):
        resolved = current_user(credential())
    assert resolved.uid == "synthetic-driver"
    assert resolved.role == "DRIVER"
    assert verify.call_args.kwargs["check_revoked"] is True
    db.collection.assert_called_with("users")
    db.collection.return_value.document.assert_called_with("synthetic-driver")
