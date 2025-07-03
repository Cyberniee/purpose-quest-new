import logging, sys, uvicorn
import sys

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
from app.config import config
from app.middleware.user_cookie_injector import UserDataCookieMiddleware
from app.middleware.auth_redirect_middleware import AuthRedirectMiddleware


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if config.project.log_level == "DEBUG" else logging.INFO)

app = FastAPI(
    title=config.project.project_name,
    version=config.project.project_version,
    debug=True
)

app.add_middleware(UserDataCookieMiddleware)
app.add_middleware(AuthRedirectMiddleware)


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router)

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", reload=True, port=8000)
