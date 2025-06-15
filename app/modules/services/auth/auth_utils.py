# app/modules/services/auth/auth_utils.py
import logging, json
import time
import urllib.parse

from jose import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config.auth_config import AuthSettings
from app.config.auth_config import supabase_client as supabase
from app.utils.common_utils import validate_data_presence
from app.utils.helpers import parse_user_data_cookie

logger = logging.getLogger(__name__)

class AuthenticationUtils:
    @staticmethod
    def decode_and_validate_jwt(token: str) -> dict | None:
        try:
            decoded_token = jwt.decode(token, AuthSettings.jwt_secret, algorithms=["HS256"], audience="authenticated")
            if decoded_token["exp"] < time.time():
                return None
            return decoded_token
        except Exception as e:
            logging.error(f"JWT decoding/validation error: {e}")
            return None

    @staticmethod
    def get_user_auth_status(request: Request) -> dict:
        jwt_token = request.cookies.get('access_token')
        user_info = {"is_logged_in": False, "user_id": None}

        if jwt_token:
            payload = AuthenticationUtils.decode_and_validate_jwt(jwt_token)
            if payload:
                user_info["is_logged_in"] = True
                user_info["sub"] = payload.get("sub")

        return user_info

    @staticmethod
    def get_authenticated_user(request: Request, require_auth: bool = True, allow_cookie: bool = True) -> dict | None:
        access_token = request.cookies.get("access_token")
        if not access_token:
            if require_auth:
                raise HTTPException(status_code=401, detail="Missing access token")
            logger.info("No access token provided")
            return None

        decoded_token = AuthenticationUtils.decode_and_validate_jwt(access_token)
        if not decoded_token:
            if require_auth:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            logger.info("Invalid or expired access token")
            return None

        auth_user_id = decoded_token.get("sub")
        if not auth_user_id:
            if require_auth:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            logger.info("Token payload missing 'sub'")
            return None

        # ✅ Try cookie if allowed
        if allow_cookie:
            raw_cookie = request.cookies.get("user_data")
            user_data = parse_user_data_cookie(raw_cookie)
            if user_data and user_data.get("sub") == auth_user_id:
                logger.info(f'user_data from cookie: {user_data}')
                return user_data

        # 🧠 Otherwise fetch from Supabase
        user_result = supabase.table("users").select("*").eq("sub", auth_user_id).single().execute()

        if not validate_data_presence(user_result):
            if require_auth:
                raise HTTPException(status_code=404, detail="User not found")
            logger.info("User not found in database")
            return None

        logger.info(f"Authenticated user: {user_result.data}")
        return user_result.data




class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, role: str = None):
        super().__init__(auto_error=auto_error)
        self.role = role

    async def __call__(self, request: Request):
        token = request.cookies.get('access_token') or await self.get_token_from_header(request)
        if token:
            decoded = AuthenticationUtils.decode_and_validate_jwt(token)
            if decoded:
                request.state.user = decoded
                return token

        self.raise_authentication_exception()

    async def get_token_from_header(self, request: Request):
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            return credentials.credentials if credentials else None
        except HTTPException:
            return None

    def raise_authentication_exception(self):
        redirect_url = "/web/sign-in-coach" if self.role == 'coach' else "/web/sign-in"
        raise AuthenticationException(redirect_url, "You need to be logged in to access that page.")


class AuthenticationException(Exception):
    def __init__(self, redirect_url: str, message: str = ""):
        self.redirect_url = redirect_url
        self.message = message


class JWTSubMiddleware(BaseHTTPMiddleware):

    @staticmethod
    def get_access_token(request: Request) -> dict:
        authorization: str = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Access token is missing or invalid format")

        token = authorization.split(" ")[1]
        decoded_token = AuthenticationUtils.decode_and_validate_jwt(token)
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return decoded_token

    @staticmethod
    def get_refresh_token(request: Request) -> str:
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token is missing")

        decoded_token = AuthenticationUtils.decode_and_validate_jwt(refresh_token)
        sub = decoded_token.get('sub') if decoded_token else None
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        return refresh_token

    @staticmethod
    def get_authenticated_user(request: Request):
        decoded_token = JWTSubMiddleware.get_access_token(request)
        sub = decoded_token.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return sub
