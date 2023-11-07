from fastapi import HTTPException
from typing import Optional
from fastapi import (
    FastAPI,
    Request,
    Form,
    status,
    Depends,
    HTTPException,
    Cookie,
    Query,
    Response,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

app = FastAPI()

app.mount("/static", StaticFiles(directory="public/dist"), name="static")

templates = Jinja2Templates(directory="public/templates")

@app.get("/", response_class=HTMLResponse, tags=["root"])
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
