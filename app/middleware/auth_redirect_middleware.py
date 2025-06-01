from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlencode

PUBLIC_PATHS = {"/", "/sign-in", "/sign-up", "finish-sign-up", "/recovery", "/password-reset", "/terms-of-service", "/privacy", "/refund", "/contact"}  # Add any public paths

class AuthRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip check for public paths and static files
        if any(path.startswith(p) for p in PUBLIC_PATHS) or path.startswith("/static"):
            return await call_next(request)

        # Attempt to get and validate the access token
        token = request.cookies.get("access_token")
        user = None
        if token:
            from app.modules.services.auth.auth_utils import AuthenticationUtils
            decoded_token = AuthenticationUtils.decode_and_validate_jwt(token)
            if decoded_token and "sub" in decoded_token:
                request.state.user_sub = decoded_token["sub"]
                return await call_next(request)

        # Redirect to /sign_in with ?next param
        next_url = urlencode({"next": str(path)})
        return RedirectResponse(f"/sign_in?{next_url}")
