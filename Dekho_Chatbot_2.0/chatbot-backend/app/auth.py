"""
JWT Authentication — FastAPI dependency for validating Bearer tokens from V2 main app.

Contract (from co-founder, 2026-06-30):
  - Algorithm:  HS256
  - Secret:     JWT_SECRET_KEY env var  (default: "dekho-super-secret-key-change-in-production")
  - User ID:    sub claim — stringified integer, e.g. "1", "42"
  - Transport:  Authorization: Bearer <token> header
  - Token type: type claim must equal "access" (not "refresh")
  - Payload:    {"sub": "1", "type": "access", "exp": 1719888800}
  - No iss claim.
  - Access token lifetime: 24h

Usage in routes:
    from app.auth import get_current_user

    @router.post("")
    async def chat(req: ChatRequest, user_id: str = Depends(get_current_user)):
        ...

The chatbot is stateless with respect to tokens — it only validates what the
frontend sends. Token refresh is handled by the V2 frontend (24h lifetime is
long enough that the chatbot never needs to call /auth/refresh itself).
"""

from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import settings

logger = logging.getLogger("dekho.auth")

# HTTPBearer extracts the token from "Authorization: Bearer <token>"
# auto_error=False lets us return a custom 401 instead of FastAPI's default
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """
    FastAPI dependency — validates the JWT and returns the user_id (str).

    Raises HTTP 401 if:
      - No Authorization header present
      - Token is malformed or has wrong algorithm
      - Token is expired
      - type claim is not "access" (prevents refresh tokens being used here)
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"],
        )
    except ExpiredSignatureError:
        logger.warning("JWT expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired — please log in again",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning("JWT validation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Ensure this is an access token, not a refresh token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type — access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("JWT valid | user_id=%s", user_id)
    return user_id


# ── Optional: dev bypass ──────────────────────────────────────────────────────
# When AUTH_ENABLED=false in .env, this dependency skips JWT validation and
# reads user_id from the request body directly (for local dev / testing only).
# Production must always use get_current_user.

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str | None:
    """
    Like get_current_user but returns None instead of raising 401.
    Use this for endpoints that work both authenticated and unauthenticated.
    """
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
