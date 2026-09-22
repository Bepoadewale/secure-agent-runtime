"""Small HS256 JWT implementation for the local control-plane identity fixture.

Production deployments replace the local shared signer with an enterprise OIDC/JWKS verifier.
"""

import base64
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime, timedelta

ISSUER = "secure-agent-runtime.local"
AUDIENCE = "secure-agent-runtime"
DEFAULT_LOCAL_SIGNING_KEY = "local-fixture-key-not-for-production"


class TokenError(ValueError):
    """Raised when a token cannot be trusted."""


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _key() -> bytes:
    return os.getenv("AGENT_RUNTIME_JWT_SIGNING_KEY", DEFAULT_LOCAL_SIGNING_KEY).encode()


def issue_local_token(
    tenant_id: str,
    subject: str,
    roles: list[str],
    principal_type: str = "human",
    expires_in_seconds: int = 600,
    issuer: str = ISSUER,
    audience: str = AUDIENCE,
) -> str:
    now = datetime.now(UTC)
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    claims = _b64encode(
        json.dumps(
            {
                "iss": issuer,
                "aud": audience,
                "sub": subject,
                "tenant": tenant_id,
                "roles": roles,
                "principal_type": principal_type,
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
            },
            separators=(",", ":"),
        ).encode()
    )
    signed = f"{header}.{claims}".encode()
    signature = _b64encode(hmac.new(_key(), signed, hashlib.sha256).digest())
    return f"{header}.{claims}.{signature}"


def verify(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        parsed_header = json.loads(_b64decode(header))
        claims = json.loads(_b64decode(payload))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise TokenError("malformed token") from error

    if parsed_header != {"alg": "HS256", "typ": "JWT"}:
        raise TokenError("unsupported token algorithm")
    expected = _b64encode(hmac.new(_key(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(expected, signature):
        raise TokenError("invalid token signature")
    if claims.get("iss") != ISSUER or claims.get("aud") != AUDIENCE:
        raise TokenError("invalid issuer or audience")
    if not isinstance(claims.get("sub"), str) or not isinstance(claims.get("tenant"), str):
        raise TokenError("missing subject or tenant")
    if not isinstance(claims.get("roles"), list) or not isinstance(claims.get("principal_type"), str):
        raise TokenError("missing identity claims")
    if not isinstance(claims.get("exp"), int) or claims["exp"] <= int(datetime.now(UTC).timestamp()):
        raise TokenError("expired token")
    return claims
