from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from app.procesos.agendamiento import router as agendamiento_router
from app.procesos.inventario import router as inventario_router

# 🔹 PRIMERO se define la app
app = FastAPI(title="Portal de Procesos Mexicargo")

# 🔹 Templates y static
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 🔹 Routers (DESPUÉS de crear app)
app.include_router(agendamiento_router)
app.include_router(inventario_router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
