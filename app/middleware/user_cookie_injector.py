# app/middleware/user_cookie_injector.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class UserDataCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        user_cookie = getattr(request.state, "set_user_cookie", None)
        if user_cookie:
            response.set_cookie(
                key=user_cookie["key"],
                value=user_cookie["value"],
                httponly=user_cookie["httponly"],
                secure=user_cookie["secure"],
                max_age=user_cookie["max_age"]
            )
        return response
