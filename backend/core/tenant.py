from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import db


user_security = HTTPBearer(auto_error=False)


def _raw_db():
    return getattr(db, "_raw", db)


def user_session(credentials: HTTPAuthorizationCredentials | None) -> dict | None:
    if not credentials or credentials.scheme.lower() != "bearer":
        return None
    now = datetime.now(timezone.utc)
    session = _raw_db().user_sessions.find_one({"$and": [
        {"$or": [{"token": credentials.credentials}, {"access_token": credentials.credentials}]},
        {"status": {"$nin": ["revoked", "expired"]}},
        {"$or": [{"expires_at": {"$exists": False}}, {"expires_at": {"$gt": now}}]},
    ]})
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Login again.")
    return session


def bind_request_identity(payload, credentials: HTTPAuthorizationCredentials | None) -> None:
    session = user_session(credentials)
    if session:
        payload.client_id = str(session["client_id"])
        payload.user_id = str(session["user_id"])
        return
    legacy = os.getenv("ALLOW_LEGACY_GAME_IDENTITY", "true").lower() in {"1", "true", "yes"}
    if not legacy:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User login required")
    if not getattr(payload, "client_id", None) or not getattr(payload, "user_id", None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Casino and user identity required")


def query_identity(user_id: str, client_id: str, credentials: HTTPAuthorizationCredentials | None) -> tuple[str, str]:
    session = user_session(credentials)
    if session:
        return str(session["user_id"]), str(session["client_id"])
    legacy = os.getenv("ALLOW_LEGACY_GAME_IDENTITY", "true").lower() in {"1", "true", "yes"}
    if not legacy:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User login required")
    return str(user_id), str(client_id)
