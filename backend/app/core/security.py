import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings


password_hash = PasswordHash.recommended()


def generate_password_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_password_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    password_hash_value: str,
) -> bool:
    return password_hash.verify(
        password,
        password_hash_value,
    )


def create_access_token(user_id: str) -> str:
    settings = get_settings()

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": user_id,
        "jti": str(uuid4()),
        "iat": now,
        "exp": expires_at,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.secret_key_value,
        algorithm="HS256",
    )


def decode_access_token(token: str) -> dict:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.secret_key_value,
            algorithms=["HS256"],
        )
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid authentication token") from exc

    if payload.get("type") != "access":
        raise ValueError("Invalid authentication token")

    if not payload.get("sub"):
        raise ValueError("Invalid authentication token")

    if not payload.get("jti"):
        raise ValueError("Invalid authentication token")

    return payload