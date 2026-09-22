from dataclasses import dataclass

from agent_runtime.auth.jwt import TokenError, verify
from fastapi import Depends, Header, HTTPException


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    subject: str
    roles: frozenset[str]
    principal_type: str


def principal(authorization: str | None = Header(default=None)) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "invalid runtime credential")
    try:
        claims = verify(authorization.removeprefix("Bearer "))
    except TokenError as error:
        raise HTTPException(401, "invalid runtime credential") from error
    return Principal(
        tenant_id=claims["tenant"],
        subject=claims["sub"],
        roles=frozenset(claims["roles"]),
        principal_type=claims["principal_type"],
    )


def admin(who: Principal = Depends(principal)) -> Principal:
    if "platform-admin" not in who.roles:
        raise HTTPException(403, "platform-admin required")
    return who
