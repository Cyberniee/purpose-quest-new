# app/dependencies/auth.py
from fastapi import Request
from app.modules.services.auth.auth_utils import AuthenticationUtils

async def get_current_user_required(request: Request) -> dict:
    return AuthenticationUtils.get_authenticated_user(request, require_auth=True)

async def get_current_user_optional(request: Request) -> dict | None:
    return AuthenticationUtils.get_authenticated_user(request, require_auth=False)
