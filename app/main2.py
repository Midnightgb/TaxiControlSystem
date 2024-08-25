# main2.py 
from fastapi import APIRouter, FastAPI
from starlette.middleware.sessions import SessionMiddleware
from Api.routes.auth import auth 
from core.config import settings
from fastapi.staticfiles import StaticFiles
from Api.routes.users import user

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"]) 

app = FastAPI(
    title=settings.PROJECT_NAME, 
    version=settings.PROJECT_VERSION, 
    description=settings.PROJECT_DESCRIPTION
)

app.mount("/static", StaticFiles(directory="public/dist"), name="static")

app.include_router(api_router)