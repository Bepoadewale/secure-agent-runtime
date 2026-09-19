from fastapi import Header, HTTPException


def principal(authorization: str | None = Header(default=None)) -> tuple[str, str]:
    tokens = {
        "Bearer tenant-a-token": ("team-a", "user:alice"),
        "Bearer tenant-b-token": ("team-b", "user:bob"),
        "Bearer admin-token": ("platform", "platform-admin"),
    }
    if authorization not in tokens:
        raise HTTPException(401, "invalid runtime credential")
    return tokens[authorization]


def admin(authorization: str | None = Header(default=None)) -> str:
    if authorization != "Bearer admin-token":
        raise HTTPException(403, "platform-admin required")
    return "platform-admin"
