from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


app = FastAPI()

app.mount("/static", StaticFiles(directory="public/dist"), name="static")

templates = Jinja2Templates(directory="public/templates")


@app.get("/", response_class=HTMLResponse, tags=["root"])
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": Request})
