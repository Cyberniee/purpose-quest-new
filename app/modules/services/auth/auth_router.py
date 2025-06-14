### AUTH ROUTER ###
import os
import time
import logging
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse

from app.config.auth_config import supabase_client as supabase
from app.config.auth_config import AuthSettings
from app.modules.services.users.user_services import get_user_by_supabase_auth_id
from app.utils.common_utils import detailed_exception_handler
from app.modules.services.auth.auth_utils import AuthenticationUtils
from app.modules.services.users.user_services import create_user
from app.utils.helpers import generate_user_cookies


# Load environment variables
root_dir = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

router = APIRouter()

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class AuthenticationException(Exception):
    def __init__(self, redirect_url: str, message: str = ""):
        self.redirect_url = redirect_url
        self.message = message

# -----------------------
# Session Helper
# -----------------------
async def set_supabase_session(request: Request, response: Response):
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token')

    if not access_token or not refresh_token:
        raise HTTPException(status_code=401, detail="No session tokens found")

    decoded_access_token = AuthenticationUtils.decode_and_validate_jwt(access_token)

    if decoded_access_token is None or decoded_access_token["exp"] < time.time() + 60 * 30:
        tokens = await refresh_token_with_supabase(refresh_token=refresh_token)
        response.set_cookie(key="access_token", secure=True, samesite='Lax', value=tokens["access_token"], httponly=True, path='/')
        response.set_cookie(key="refresh_token", secure=True, samesite='Lax', value=tokens["refresh_token"], httponly=True, path='/')

async def refresh_token_with_supabase(refresh_token: str):
    res = supabase.auth.refresh_session(refresh_token)
    return {"access_token": res.session.access_token, "refresh_token": res.session.refresh_token}

# -----------------------
# Routes
# -----------------------
@router.post("/sign_up", tags=["auth"])
@detailed_exception_handler
async def sign_up(request: Request, response: Response):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "").strip()
    logger.info(f"redir for signup: {AuthSettings.sign_up_redirect_url}")
    try:       
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"redirect_to": AuthSettings.sign_up_redirect_url}
        })
        # logger.info(f"Sign-up response: {res}")

        try:
            # Create user in the database    
            await create_user(res.user.id, email, name=body.get("name", ""))
            
        except Exception as e:
            logger.error(f"Error creating user in DB: {e}")
            return JSONResponse(status_code=500, content={
                "status": "error",
                "message": "User created but failed to save in database. Please contact support."
            })

        # In Supabase, users may need to confirm their email before session is returned
        if not res.session:
            return JSONResponse(status_code=200, content={
                "status": "pending",
                "message": "Sign-up successful. Please check your email to confirm your account."
            })     

    except Exception as e:
        logging.error(f"Sign-up error: {e}")
        detail = str(e)
        user_friendly_message = "User already exists or invalid email/password" if "User already registered" in detail else "Something went wrong. Please try again."
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": user_friendly_message
        })

@router.post("/sign_in", tags=["auth"])
@detailed_exception_handler
async def sign_in(request: Request, response: Response):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "").strip()

    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        decoded_token = AuthenticationUtils.decode_and_validate_jwt(res.session.access_token)
        if not decoded_token:
            return JSONResponse(status_code=401, content={
                "status": "error",
                "message": "Invalid token received. Please try again."
            })
        
        user = await get_user_by_supabase_auth_id(decoded_token["sub"])
        
        # ✅ Set cookies (still works with fetch if not blocked by CORS)
        response = JSONResponse(status_code=200, content={
            "status": "success",
            "message": "You are signed in!"
        })

        for cookie in generate_user_cookies({
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "email": email,
            "user_id": user.get('id', ''),
            "name": user.get('name', ''),  # Optional
            "first_login": user.get('first_login', False)  # Optional, default to False
        }):
            response.set_cookie(**cookie)

        return response

    except Exception as e:
        logging.error(f"Sign-in error: {e}")
        detail = str(e)
        user_friendly_message = "Password was incorrect or user does not exist" if "Invalid login credentials" in detail else "Something went wrong. Please try again."
        return JSONResponse(status_code=401, content={
            "status": "error",
            "message": user_friendly_message
        })
        

@router.get("/sign_out", tags=["auth"])
@detailed_exception_handler
async def sign_out(response: Response):
    try:
        supabase.auth.sign_out()
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        response.delete_cookie(key="user_id", path="/")
        response.delete_cookie(key="sub", path="/")
        response.delete_cookie(key="user_data", path="/")
        return response
    except Exception as e:
        logging.error(f"Sign-out error: {e}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Failed to sign out. Please try again."
        })

@router.get("/refresh_session", tags=["auth"])
@detailed_exception_handler
async def refresh_session(response: Response, _=Depends(set_supabase_session)):
    return {"status": "Session refreshed"}

@router.post("/password_recovery_request", tags=["auth"])
@detailed_exception_handler
async def password_recovery_request(request: Request):
    body = await request.json()
    email = body.get("email")
    options = {"redirect_to": AuthSettings.recovery_redirect_url}

    try:
        supabase.auth.reset_password_email(email, options)
        return {
            "status": "success",
            "message": "If this email is registered, a recovery email has been sent."
        }
    except Exception as e:
        logging.error(f"Password recovery error: {e}")
        return {
            "status": "error",
            "message": "Something went wrong. If the email is registered, you will receive a recovery email."
        }

@router.post("/password_reset", tags=["auth"])
@detailed_exception_handler
async def password_reset(request: Request, _=Depends(set_supabase_session)):
    body = await request.json()
    new_password = body.get("new_password")

    try:
        supabase.auth.update_user(attributes={"password": new_password})
        return {"status": "success", "message": "Password updated successfully"}
    except Exception as e:
        logging.error(f"Password reset error: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/api/validate_token", response_class=JSONResponse)
async def validate_token(token: Token, response: Response):
    logger.info(f"validating some token: {token}")
    try:
        # Assuming decodeJWT is a function that decodes and verifies the JWT
        decoded_token = AuthenticationUtils.decode_and_validate_jwt(token.access_token)
        logger.info(f"Decoded token: {decoded_token}")
        
        
        if decoded_token:
            
            user = await get_user_by_supabase_auth_id(decoded_token['sub'])
            if not get_user_by_supabase_auth_id:
                logger.error(f"User with sub {decoded_token['sub']} not found in database")
                raise AuthenticationException("/sign-in", "You need to be authenticated in to access this page.")
            user_id = user.get('id', '')
            
            response.set_cookie(key="user_id", secure=True, samesite='Lax', value=user_id, httponly=True, path='/')
            response.set_cookie(key="refresh_token", secure=True, samesite='Lax', value=token.refresh_token, httponly=True, path='/')
            response.set_cookie(key="access_token",  secure=True, samesite='Lax', value=token.access_token, httponly=True, path='/')
            
            return {"status": "success", "message": "Authentication successful"}
        
        else:
            logger.error(f"error validating token, invalid or expired {decoded_token}")
            raise AuthenticationException("/sign-in", "You need to be authenticated in to access this page.")
            
    except Exception as e:
        # raise HTTPException(status_code=401, detail=str(e))
        logger.warning(f"invalid or expired token: {e}")
        raise AuthenticationException("/sign-in", "You need to be authenticated in to access this page.")
