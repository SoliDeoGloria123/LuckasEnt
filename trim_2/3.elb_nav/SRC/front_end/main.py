from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pymongo import MongoClient

# Conectar a MongoDB
client = MongoClient(
    "mongodb+srv://juanjuanddev:hR7m3QxGgMf5BOKv@cluster0.mnzsa9g.mongodb.net/LuckasEnt?retryWrites=true&w=majority"
)
db = client.LuckasEnt  # Cambia 'nombre_de_tu_bd' por el nombre de tu base de datos
collection = db["productos"]  # type: ignore # Cambia 'nombre_de_tu_coleccion' por el nombre de tu colección
users_collection = db[
    "users"
]  # Cambia 'users' por el nombre de tu colección de usuarios


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

@app.post("/login", name="login_post")
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    # Verifica si los campos están vacíos
    if not email or not password:
        error = "Todos los campos son obligatorios"
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": error}
        )

    # Verifica si el usuario existe en la base de datos
    usuario = users_collection.find_one({"correo": email, "password": password})

    if usuario:
        # Si el usuario existe, redirige a la página principal
        return RedirectResponse(url="/page", status_code=303)
    else:
        # Si no existe, muestra un mensaje de error
        error = "Correo o contraseña incorrectos"
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": error}
        )

@app.get("/registro", name="registro")
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})


@app.post("/register", name="register_post")
async def register_post(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    # Verifica si las contraseñas coinciden
    if password != confirm_password:
        error = "Las contraseñas no coinciden"
        return templates.TemplateResponse(
            "registro.html", {"request": request, "error": error}
        )

    # Verifica si el correo ya está registrado
    usuario_existente = users_collection.find_one({"correo": correo})
    if usuario_existente:
        error = "El correo ya está registrado"
        return templates.TemplateResponse(
            "registro.html", {"request": request, "error": error}
        )

    # Inserta el nuevo usuario en la base de datos
    nuevo_usuario = {
        "nombre": nombre,
        "apellido": apellido,
        "correo": correo,
        "telefono": telefono,
        "password": password,  # Nota: Considera encriptar la contraseña antes de guardarla
    }
    users_collection.insert_one(nuevo_usuario)

    # Redirige al usuario a la página de inicio de sesión
    return RedirectResponse(url="/login", status_code=303)


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
async def home(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/tienda", name="tienda")
async def tienda(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("tienda.html", {"request": request})


@app.get("/productlista", name="productlista")
async def productlista(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("categorias.html", {"request": request})


@app.get("/detalle_producto", name="detalle_producto")
async def detalleproducto(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("detalleproduct.html", {"request": request})


@app.get("/categoria", name="categoria")
async def categoria(request: Request):  # ✔️ Nombre correcto de la función
    productos = list(collection.find())  # Obtiene los productos de MongoDB
    return templates.TemplateResponse(
        "categorias.html", {"request": request, "productos": productos}
    )


@app.get("/tienda", name="tienda")
async def tienda(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("tienda.html", {"request": request})


@app.get("/nosotros", name="nosotros")
async def nosotros(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("nosotros.html", {"request": request})


@app.get("/categoria_carne", name="categoria_carne")
async def categoria_carne(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("categoria_carne.html", {"request": request})


@app.get("/categoria_pescado", name="categoria_pescado")
async def categoria_pescado(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("categoria_pescado.html", {"request": request})


@app.get("/categoria_pan", name="categoria_pan")
async def categoria_pan(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("categoria_pan.html", {"request": request})


@app.get("/categoria_dulce", name="categoria_dulce")
async def categoria_dulce(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("categoria_dulce.html", {"request": request})


@app.get("/categoria_bebida", name="categoria_bebida")
async def categoria_bebida(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("categoria_bebida.html", {"request": request})
