from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()

# 📂 Base directory dinámico (donde está este archivo)
BASE_DIR = Path(__file__).resolve().parent

# ✅ Servir archivos estáticos con el path absoluto
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# ✅ Configurar templates con el path absoluto
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/registro", name="registro")
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.get("/olvidar", name="olvidar")
async def olvidar(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("olvidar_contraseña.html", {"request": request})

@app.get("/page", name="page")
async def page(request: Request):
    return templates.TemplateResponse("page.html", {"request": request})

@app.get("/cuenta", name="cuenta")
async def cuenta(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("Mi_Cuenta.html", {"request": request})

@app.get("/perfil", name="perfil")
async def perfil(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("mi_informacion.html", {"request": request})

@app.get("/precioproduc", name="precioproduc")
async def precioproduc(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("productoprecio.html", {"request": request})

@app.get("/ubicacionproduc", name="ubicacionproduc")
async def ubicacionproduc(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("productoubica.html", {"request": request})

@app.get("/reseñaproduc", name="reseñaproduc")
async def reseñaproduc(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("productoreseña.html", {"request": request})

@app.get("/tulista", name="tulista")
async def tulista(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("cardgrid.html", {"request": request})

@app.get("/termino", name="termino")
async def termino(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("Termino_uso.html", {"request": request})

@app.get("/home", name="home")
async def home(request: Request): # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("home.html", {"request": request})



