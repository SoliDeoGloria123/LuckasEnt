from fastapi import FastAPI, File, HTTPException, Query, Request, Form, Response, UploadFile, Depends, status
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from flask import Flask, session, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_dance.contrib.google import make_google_blueprint, google
from pymongo import MongoClient
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeSerializer
from bson import ObjectId
import secrets
import base64
import re
from dotenv import load_dotenv
import os
from typing import List

# Mapeo de categorías a términos de búsqueda
CATEGORIAS_MAPPING = {
    "frutas_verduras": ["fruta", "verdura", "hortaliza", "aguacate", "manzana", "plátano", "tomate", "cebolla", "papa"],
    "carnicos": ["carne", "res", "cerdo", "pollo", "pechuga", "lomo", "costilla", "hamburguesa", "salchicha"],
    "pescados": ["pescado", "mariscos", "atún", "salmón", "camarón", "tilapia", "trucha"],
    "panaderia": ["pan", "pastel", "torta", "galleta", "croissant", "dona", "muffin", "bizcocho"],
    "dulces_abarrotes": ["dulce", "chocolate", "caramelo", "azúcar", "arroz", "frijol", "pasta", "aceite", "conserva"],
    "bebidas": ["agua", "jugo", "refresco", "gaseosa", "cerveza", "vino", "leche", "café", "té"]
}
# Cargar variables de entorno desde .env
load_dotenv()

# Conectar a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.LuckasEnt

# Colecciones
collection = db["productos"]
listas_collection = db["lists"]
users_collection = db["users"]

# Configurar correo electrónico
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Configurar clave secreta, el cual, sirve para firmar cookies y datos, y firmar significa que se puede verificar su autenticidad.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurada en el archivo .env")
print(f"--- DEBUG: SECRET_KEY cargada: {SECRET_KEY} ---")

serializer = URLSafeSerializer(SECRET_KEY)
print(f"--- DEBUG: Serializer inicializado: {serializer} ---")

# Crear la aplicación principal de FastAPI
app = FastAPI()

# Crear la subaplicación Flask
flask_app = Flask(__name__)
flask_app.secret_key = SECRET_KEY

# Hash de la contraseña
bcrypt = Bcrypt(flask_app)

# Configurar la Implementación de Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to="google_login_callback",
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
)

# Registrar el blueprint de Google OAuth
flask_app.register_blueprint(google_bp, url_prefix="/login/google")

# Ruta de inicio de sesión de Google
@flask_app.route("/login/google")
def google_login():
    return redirect(url_for("google.login"))

# Callback de Google OAuth
@flask_app.route("/google_login_callback")
def google_login_callback():
    print(f"--- DEBUG: Serializer en google_login_callback: {serializer} ---")
    print("--- DEBUG: Entrando a google_login_callback ---")
    
    # Verificar si el usuario ya está en sesión
    if 'usuario' in session:
        print(f"--- DEBUG: Usuario ya en sesión: {session['usuario']} ---")
        return redirect("/page")

    # Verificar si el usuario está autorizado con Google
    if not google.authorized:
        print("--- DEBUG: Usuario no autorizado con Google ---")
        return redirect(url_for('google.login'))
    
    # Obtener información del usuario desde Google
    resp = google.get("https://www.googleapis.com/oauth2/v3/userinfo")
    if not resp.ok:
        print("--- DEBUG: Error al obtener información del usuario ---")
        flash("Error al obtener información del usuario de Google.", "error")
        return redirect("/login")
    
    user_info = resp.json()
    print(f"--- DEBUG: Información del usuario de Google: {user_info} ---")
    
    if 'email' not in user_info:
        print("--- DEBUG: No se pudo obtener el correo electrónico del usuario ---")
        flash("No se pudo obtener el correo electrónico del usuario.", "error")
        return redirect("/login")
    
    # Guardar o actualizar la información del usuario en la base de datos
    users_collection.update_one(
        {"correo": user_info.get("email")},
        {
            "$set": {
                "nombre": user_info.get("given_name"),
                "apellido": user_info.get("family_name"),
                "foto": user_info.get("picture"),  # Guardar la URL de la foto de perfil
            }
        },
        upsert=True  # Crear el documento si no existe
    )

    # Depuración: Verifica si la foto se guardó correctamente
    usuario = users_collection.find_one({"correo": user_info.get("email")})
    print(f"--- DEBUG: Usuario actualizado en la base de datos: {usuario} ---")
    
    # Configurar la cookie de sesión
    cookie_value = serializer.dumps({"email": user_info.get("email")})
    print(f"--- DEBUG: Valor de la cookie firmada: {cookie_value} ---")
    response = redirect("/page")
    response.set_cookie(
        "session",
        cookie_value,
        httponly=True,
        max_age=86400,
        secure=False,
        samesite="Lax"
    )
    return response

# Montar la subaplicación Flask en FastAPI
app.mount("/flask", WSGIMiddleware(flask_app))

# Configurar templates y archivos estáticos
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Filtro personalizado para codificar en Base64
def b64encode_filter(data):
    if isinstance(data, bytes):  # Si es binario, codificar en Base64
        return base64.b64encode(data).decode("utf-8")
    elif isinstance(data, str):  # Si es una URL, devolverla tal cual
        return data
    return ""  # Si no hay datos, devolver una cadena vacía
templates.env.filters["b64encode"] = b64encode_filter

# Obtener el usuario actual desde la cookie
def get_current_user(request: Request):
    print("--- DEBUG: Entrando a get_current_user ---")
    session_cookie = request.cookies.get("session")
    print(f"--- DEBUG: Valor de la cookie recibida: {session_cookie} ---")
    if not session_cookie:
        print("--- DEBUG: No hay cookie, retornando None ---")
        return None
    try:
        data = serializer.loads(session_cookie)
        print(f"--- DEBUG: Cookie decodificada: {data} ---")
        return data
    except Exception as e:
        print(f"--- DEBUG: ERROR al decodificar cookie: {e} ---")
        return None
    
# Dependencia para verificar inicio de sesión
async def require_login(request: Request):
    print(">>> DEBUG: Entrando a require_login <<<")
    user_session_data = get_current_user(request)
    print(f">>> DEBUG: user_session_data es: {user_session_data} <<<")
    if not user_session_data:
        print(">>> DEBUG: NO hay sesión, REDIRIGIENDO a login <<<")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    print(">>> DEBUG: SI hay sesión, PERMITIENDO acceso <<<")
    return user_session_data

# Ruta protegida de ejemplo
@app.get("/page", name="page")
async def page(request: Request, current_user=Depends(require_login)):
    print("### DEBUG: Ejecutando ruta /page ###")
    if isinstance(current_user, RedirectResponse):
        return current_user
    print(f"### DEBUG: Usuario en /page: {current_user.get('email')} ###")
    return templates.TemplateResponse("page.html", {"request": request, "usuario": current_user})

# Rutas de la aplicación FastAPI para manejar la autenticación y el acceso a las páginas del sitio LuckasEnt
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login", name="login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

async def require_api_login(request: Request):
    """
    Dependencia para rutas API. Verifica login y devuelve 401 si no está autenticado.
    """
    user_session_data = get_current_user(request)
    if not user_session_data:
        # Para APIs, es estándar devolver 401 Unauthorized, no redirigir.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_session_data

@app.post("/login", name="login_post")
async def login_post(request: Request, response: Response, email: str = Form(...), password: str = Form(...)):
    print(f"--- DEBUG: Serializer en login_post: {serializer} ---")
    # Verifica si los campos están vacíos
    if not email or not password:
        error = "Todos los campos son obligatorios"
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": error}
        )

    # Verifica si el usuario existe en la base de datos
    usuario = users_collection.find_one({"correo": email})

    if usuario and bcrypt.check_password_hash(usuario["password"], password):
        session_data = {"email": email}
        session_cookie = serializer.dumps(session_data)
        response = RedirectResponse(url="/page", status_code=303)
        response.set_cookie(key="session", value=session_cookie, httponly=True)
        return response
    else:
        # Si no existe o la contraseña no coincide, muestra un mensaje de error
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

    # Encriptar la contraseña antes de guardarla
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Inserta el nuevo usuario en la base de datos
    nuevo_usuario = {
        "nombre": nombre,
        "apellido": apellido,
        "correo": correo,
        "telefono": telefono,
        "password": hashed_password,  # Guardar la contraseña encriptada
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
    sender_email = SENDER_EMAIL
    sender_password = SENDER_PASSWORD
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
            "olvidar_contraseña.html", {"request": request, "error": f"No se pudo enviar el correo: {e}"})


@app.get("/cuenta", name="cuenta")
async def cuenta(request: Request, current_user: dict = Depends(require_login)):
    usuario = users_collection.find_one({"correo": current_user["email"]})
    print(f"--- DEBUG: Usuario obtenido para /cuenta: {usuario} ---")  # Depuración
    if not usuario:
        return RedirectResponse(url=request.url_for('login'), status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("Mi_Cuenta.html", {"request": request, "usuario": usuario})


@app.get("/logout", name="logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session")
    return response

@app.get("/clear_cookies")
async def clear_cookies(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session")
    return response

@app.get("/perfil", name="perfil")
async def perfil(request: Request, current_user: dict = Depends(require_login)):
    usuario = users_collection.find_one({"correo": current_user["email"]})
    print(f"--- DEBUG: Usuario obtenido para /perfil: {usuario} ---")  # Depuración
    if not usuario:
        return RedirectResponse(url=request.url_for('login'), status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("mi_informacion.html", {"request": request, "usuario": usuario})


@app.post("/perfil", name="actualizar_perfil")
async def actualizar_perfil(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    password: str = Form(...),
    foto: UploadFile = File(None),
    current_user: dict = Depends(require_login)
):
        # Validar que el email del formulario coincide con el de la sesión
    if email != current_user["email"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para actualizar este perfil")
     
    # Actualiza los datos del usuario en la base de datos
    update_data = {
        "nombre": nombre,
        "apellido": apellido,
        "telefono": telefono,
        "foto": foto,
        "correo": email,
        "password": password,
    }
   # Lee los bytes de la foto si se subió una
    if foto and foto.filename: # Verifica que se subió un archivo y tiene nombre
        contenido_foto = await foto.read() # Lee el contenido del archivo como bytes
        update_data["foto"] = contenido_foto # Añade los bytes al diccionario de actualización

    # Actualiza los datos del usuario en la base de datos
    result = users_collection.update_one(
        {"correo": email}, # Usa el email correcto para encontrar al usuario
        {"$set": update_data},
    )
    # Verifica si la actualización fue exitosa (opcional pero recomendado)
    if result.modified_count == 0 and not (foto and foto.filename):
         pass
    return RedirectResponse(url=request.url_for('cuenta'), status_code=303)

@app.get("/page", name="page")
async def page(request: Request, current_user=Depends(require_login)):
    print("### DEBUG: Ejecutando ruta /page ###")
    if isinstance(current_user, RedirectResponse):
        print("### DEBUG: current_user es RedirectResponse, retornando... ###")
        return current_user
    print(f"### DEBUG: Usuario en /page: {current_user.get('email')} ###")
    return templates.TemplateResponse("page.html", {"request": request, "usuario": current_user})



@app.post("/eliminar_cuenta", name="eliminar_cuenta")
async def eliminar_cuenta(request: Request, email: str = Form(...)):
    # Elimina el usuario de la base de datos
    result = users_collection.delete_one({"correo": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return RedirectResponse(url="/registro", status_code=303)

@app.get("/precioproduc", name="precioproduc")
async def precioproduc(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("productoprecio.html", {"request": request})

@app.get("/Tiendas", name="Tiendas")
async def Tiendas(request: Request):
    usuario = {"nombre": "Luis Felipe"}  # o lo que corresponda según tu app
    return templates.TemplateResponse("Tiendas.html", {"request": request, "usuario": usuario})


@app.get("/ubicacionproduc", name="ubicacionproduc")
async def ubicacionproduc(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("productoubica.html", {"request": request})


@app.get("/reseñaproduc", name="reseñaproduc")
async def reseñaproduc(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("productoreseña.html", {"request": request})

@app.post("/agregar_a_lista/{product_id}", name="agregar_a_lista")
async def agregar_a_lista(request: Request, product_id: str, current_user: dict = Depends(require_api_login)):
    user_email = current_user["email"]
    # 1. Verificar si el usuario está logueado
    user_session_data = get_current_user(request)
    if not user_session_data:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión para agregar productos")

    user_email = user_session_data["email"]

    # 2. Validar el product_id (que es el _id de MongoDB)
    try:
        obj_product_id = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    if not collection.find_one({"_id": obj_product_id}):
         raise HTTPException(status_code=404, detail="Producto no encontrado")
    result = listas_collection.update_one(
        {"user_email": user_email}, # Busca el documento por el email del usuario
        {"$addToSet": {"productos_ids": obj_product_id}}, # Añade el ObjectId al array
        upsert=True # Crea el documento si el usuario no tiene lista aún
    )

    # 5. Devolver una respuesta
    if result.upserted_id:
        return {"status": "success", "message": "Producto agregado a tu lista"}
    elif result.modified_count > 0:
        return {"status": "success", "message": "Producto agregado a tu lista"}
    elif result.matched_count > 0:
         # Si encontró el documento pero no modificó (el producto ya estaba)
         return {"status": "info", "message": "Este producto ya está en tu lista"}
    else:
         # Error inesperado
         raise HTTPException(status_code=500, detail="Error al actualizar la lista")


@app.get("/tulista", name="tulista")
async def tulista(request: Request, current_user: dict = Depends(require_login)):
    
    if isinstance(current_user, RedirectResponse):
        print("### DEBUG: categoria - current_user es RedirectResponse, retornando... ###")
        return current_user
    print(f"### DEBUG: categoria - Usuario en /categoria: {current_user.get('email')} ###")
    
    user_email = current_user["email"]

    # 2. Buscar la lista del usuario en 'listas_usuarios'
    lista_doc = listas_collection.find_one({"user_email": user_email})
    productos_lista_completa = [] # Lista paand los datos completand
    if lista_doc and "productos_ids" in lista_doc: 
        lista_ids = lista_doc.get("productos_ids", []) # Obtiene el array de ObjectIds
        if lista_ids:
            # 3. Buscar los productos completos en la colección 'productos' usando los IDs
            productos_lista_completa = list(collection.find({"_id": {"$in": lista_ids}}))

    # 4. (Opcional pero necesario para la foto de perfil en cardgrid.html) Obtener datos del usuario
    usuario_info = users_collection.find_one({"correo": user_email})
    if not usuario_info:
         # Si por alguna razón no se encuentra, usa un default para evitar errores
         usuario_info = {'foto': None, 'nombre': 'Usuario', 'apellido': ''}

    # 5. Renderizar cardgrid.html pasando la lista de productos y la info del usuario
    return templates.TemplateResponse(
        "cardgrid.html",
        {
            "request": request,
            "productos_lista": productos_lista_completa, # La lista de productos encontrados
            "usuario": usuario_info # Para la foto de perfil en la barra de navegación
        }
    )

@app.post("/eliminar_de_lista/{product_id}", name="eliminar_de_lista") # Puedes usar POST o DELETE
async def eliminar_de_lista(request: Request, product_id: str):
    user_session_data = get_current_user(request)
    if not user_session_data:
        raise HTTPException(status_code=401, detail="No autenticado")

    user_email = user_session_data["email"]

    try:
        obj_product_id = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de producto inválido")

    # Elimina el ObjectId del producto del array 'productos_ids' usando $pull
    result = listas_collection.update_one(
        {"user_email": user_email},
        {"$pull": {"productos_ids": obj_product_id}}
    )

    if result.modified_count > 0:
        return {"status": "success", "message": "Producto eliminado de la lista"}
    elif result.matched_count == 0:
         raise HTTPException(status_code=404, detail="Lista de usuario no encontrada")
    else:
         # No se modificó (quizás el producto ya no estaba en la lista)
         return {"status": "info", "message": "Producto no encontrado en la lista"}


@app.get("/termino", name="termino")
async def termino(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("Termino_uso.html", {"request": request})


@app.get("/home", name="home")
async def home(request: Request):  # ✔️ Nombre correcto de la función  # noqa: F811
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/tienda", name="tienda")
async def tienda(request: Request, current_user = Depends(require_login)): 
    if isinstance(current_user, RedirectResponse):
        print("### DEBUG: tienda - current_user es RedirectResponse, retornando... ###")
        return current_user
    # Si no es una redirección, entonces es el diccionario del usuario.
    # Ahora podemos usar ["email"] de forma segura.
    print(f"### DEBUG: tienda - Usuario en /tienda: {current_user.get('email')} ###")
    # Busca los datos completos del usuario usando el email de la sesión
    usuario = users_collection.find_one({"correo": current_user["email"]})

    # Manejar el caso (raro) de que el usuario exista en la sesión pero no en la BD
    if not usuario:
        # Redirigir a logout es una opción segura para limpiar la cookie
        return RedirectResponse(url=request.url_for('logout'), status_code=status.HTTP_303_SEE_OTHER)

    # Pasa los datos completos del usuario al template
    return templates.TemplateResponse("tienda.html", {"request": request, "usuario": usuario})


@app.get("/productlista", name="productlista")
async def productlista(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("categorias.html", {"request": request})


@app.get("/detalle_producto", name="detalle_producto")
async def detalleproducto(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("detalleproduct.html", {"request": request})


@app.get("/categoria", name="categoria")
async def categoria(
    request: Request, 
    q: str = "", 
    page: int = Query(1, gt=0), 
    stores: List[str] = Query(None),
    categoria_id: str = None,
    current_user = Depends(require_login)
):
    """
    Muestra una lista paginada de productos con opción de búsqueda y filtros.
    """
    
    if isinstance(current_user, RedirectResponse):
        print("### DEBUG: categoria - current_user es RedirectResponse, retornando... ###")
        return current_user
    print(f"### DEBUG: categoria - Usuario en /categoria: {current_user.get('email')} ###")
    
    productos_por_pagina = 38
    skip = (page - 1) * productos_por_pagina

    # Construir filtro
    filtro = {}
    
    # Filtrar por categoría si se especificó
    if categoria_id in CATEGORIAS_MAPPING:
        # Crear expresión regular para buscar términos relacionados con la categoría
        terminos = CATEGORIAS_MAPPING[categoria_id]
        regex_pattern = "|".join(terminos)
        filtro["Product_Name"] = {"$regex": regex_pattern, "$options": "i"}
    
    # Filtrar por tiendas si se seleccionaron
    if stores:
        filtro["Parner"] = {"$in": stores}
    
    # Si hay término de búsqueda adicional, añadir al filtro
    if q:
        # Si ya hay un filtro de Product_Name, lo combinamos con el término de búsqueda
        if "Product_Name" in filtro:
            # Guardamos el filtro original de categoría
            categoria_regex = filtro["Product_Name"]["$regex"]
            # Creamos un nuevo filtro que combine ambos criterios
            filtro["$and"] = [
                {"Product_Name": {"$regex": categoria_regex, "$options": "i"}},
                {"Product_Name": {"$regex": re.escape(q), "$options": "i"}}
            ]
            # Eliminamos el filtro original para evitar conflictos
            del filtro["Product_Name"]
        else:
            filtro["Product_Name"] = {"$regex": re.escape(q), "$options": "i"}

    # Consulta MongoDB con filtro + paginación
    productos = list(collection.find(filtro).skip(skip).limit(productos_por_pagina))

    # Total de productos para la paginación
    total_productos = collection.count_documents(filtro)
    total_paginas = (total_productos + productos_por_pagina - 1) // productos_por_pagina

    # Determinar qué categoría está activa
    categorias_activas = {
        "frutas_verduras": categoria_id == "frutas_verduras",
        "carnicos": categoria_id == "carnicos",
        "pescados": categoria_id == "pescados",
        "panaderia": categoria_id == "panaderia",
        "dulces_abarrotes": categoria_id == "dulces_abarrotes",
        "bebidas": categoria_id == "bebidas"
    }

    # Determinar el título de la página según la categoría
    titulo_pagina = "Productos"
    if categoria_id:
        titulo_pagina = categoria_id.replace("_", " ").title()

    return templates.TemplateResponse("categorias.html", {
        "request": request,
        "productos": productos,
        "pagina_actual": page,
        "total_paginas": total_paginas,
        "query": q,
        "stores": stores or [],
        "categoria_actual": categoria_id,
        "categorias_activas": categorias_activas,
        "total_productos": total_productos,
        "titulo_pagina": titulo_pagina
    })

@app.get("/categoria_frutas", name="categoria_frutas")
async def categoria_frutas(request: Request, q: str = "", page: int = Query(1, gt=0), stores: List[str] = Query(None), current_user = Depends(require_login)):
    return await categoria(request, q, page, stores, "frutas_verduras", current_user)

@app.get("/categoria_carne", name="categoria_carne")
async def categoria_carne(request: Request, q: str = "", page: int = Query(1, gt=0), stores: List[str] = Query(None), current_user = Depends(require_login)):
    return await categoria(request, q, page, stores, "carnicos", current_user)

@app.get("/categoria_pescado", name="categoria_pescado")
async def categoria_pescado(request: Request, q: str = "", page: int = Query(1, gt=0), stores: List[str] = Query(None), current_user = Depends(require_login)):
    return await categoria(request, q, page, stores, "pescados", current_user)

@app.get("/categoria_pan", name="categoria_pan")
async def categoria_pan(request: Request, q: str = "", page: int = Query(1, gt=0), stores: List[str] = Query(None), current_user = Depends(require_login)):
    return await categoria(request, q, page, stores, "panaderia", current_user)

@app.get("/categoria_dulce", name="categoria_dulce")
async def categoria_dulce(request: Request, q: str = "", page: int = Query(1, gt=0), stores: List[str] = Query(None), current_user = Depends(require_login)):
    return await categoria(request, q, page, stores, "dulces_abarrotes", current_user)

@app.get("/categoria_bebida", name="categoria_bebida")
async def categoria_bebida(request: Request, q: str = "", page: int = Query(1, gt=0), stores: List[str] = Query(None), current_user = Depends(require_login)):
    return await categoria(request, q, page, stores, "bebidas", current_user)

@app.get("/nosotros", name="nosotros")
async def nosotros(request: Request):  # ✔️ Nombre correcto de la función
    return templates.TemplateResponse("nosotros.html", {"request": request})


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


