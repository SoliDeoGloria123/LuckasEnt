from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="front_end/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="front_end/templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/registro", name="registro")
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.get("/page", name="page")
async def registro(request: Request):
    return templates.TemplateResponse("page.html", {"request": request})