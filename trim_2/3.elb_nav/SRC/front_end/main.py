from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pymongo import MongoClient
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Conectar a MongoDB
client = MongoClient(
    "mongodb+srv://juanjuanddev:hR7m3QxGgMf5BOKv@cluster0.mnzsa9g.mongodb.net/LuckasEnt?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
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

@app.post("/olvidar", name="olvidar_post")
async def olvidar_post(request: Request, email: str = Form(...)):
    if not users_collection.find_one({"correo": email}):
        return templates.TemplateResponse(
            "olvidar_contraseña.html", {"request": request, "error": "El correo no está registrado"}
        )

    # Recuperar la contraseña del usuario
    password = users_collection.find_one({"correo": email}).get("password")

    # Configurar el correo electrónico
    sender_email = "luckas.entorno@gmail.com"
    sender_password = "CorpLuckas3241"
    subject = "Recuperación de contraseña - LuckasEnt"
    body = f"Hola {users_collection.find_one({"correo": email}).get('nombre')},\n\nTu contraseña es: {password}\n\nPor favor, cámbiala si crees que alguien más tiene acceso a ella.\n\nSaludos,\nLuckasEnt"

    # Crear el mensaje de correo
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Enviar el correo
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        return templates.TemplateResponse(
            "olvidar_contraseña.html", {"request": request, "success": "Se ha enviado un correo con tu contraseña"}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "olvidar_contraseña.html", {"request": request, "error": f"No se pudo enviar el correo: {e}"}
        )

@app.get("/page", name="page")
async def page(request: Request):
    return templates.TemplateResponse("page.html", {"request": request})



@app.get("/cuenta", name="cuenta")
async def cuenta(request: Request):
    email = request.query_params.get("email")
    if not email:
        return RedirectResponse(url="/login", status_code=303)

    usuario = users_collection.find_one({"correo": email})
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "Mi_Cuenta.html", {"request": request, "usuario": usuario}
    )


@app.get("/perfil", name="perfil")
async def perfil(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("mi_informacion.html", {"request": request})

@app.post("/perfil", name="actualizar_perfil")
async def actualizar_perfil(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    password: str = Form(...),
    foto: bytes = Form(None),
):
    # Actualiza los datos del usuario en la base de datos
    users_collection.update_one(
        {"correo": email},
        {
            "$set": {
                "nombre": nombre,
                "apellido": apellido,
                "telefono": telefono,
                "password": password,
                "foto": foto,  # Guarda la foto como bytes o en un servicio externo
            }
        },
    )
    return templates.TemplateResponse(
        "mi_informacion.html",
        {"request": request, "success": "Tus datos han sido actualizados."},
    )

@app.post("/eliminar_cuenta", name="eliminar_cuenta")
async def eliminar_cuenta(request: Request, email: str = Form(...)):
    users_collection.delete_one({"correo": email})
    return RedirectResponse(url="/registro", status_code=303)

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


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "status_code": 422, "detail": "Error de validación"},
        status_code=422,
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "status_code": 500, "detail": "Error interno del servidor"},
        status_code=500,
    )


