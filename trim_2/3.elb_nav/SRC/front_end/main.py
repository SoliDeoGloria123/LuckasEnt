from fastapi import FastAPI, File, HTTPException, Query, Request, Form,  Response, UploadFile, Depends, status
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

# Cargar variables de entorno desde .env
load_dotenv()

# Conectar a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.LuckasEnt

#colecciones
collection = db["productos"]  # type: ignore 
listas_collection = db["lists"]
users_collection = db["users"]

# Configurar correo electrónico
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Configurar clave secreta
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(SECRET_KEY)

# Crear la aplicación principal de FastAPI
app = FastAPI()

# Crear la subaplicación Flask
flask_app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")
flask_app.secret_key = SECRET_KEY
serializer = URLSafeSerializer(SECRET_KEY)

#Hash de la contraseña:
bcrypt = Bcrypt(flask_app)

# Configurar la Implementación de Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"), #Esto sirve para identificar la aplicación
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),#Esto sirve para autenticar la aplicación
    redirect_to=None, # Usa None para que Flask-Dance genere automáticamente el URI correcto
    scope=["openid", 
           "https://www.googleapis.com/auth/userinfo.profile", # #Mediante esto se obtiene el nombre y la foto
           "https://www.googleapis.com/auth/userinfo.email",# #Mediante esto se obtiene el correo
           "https://www.googleapis.com/auth/user.phonenumbers.read"], #Mediante esto se obtiene el numero de telefono
            
)

#Aqui se une fastapi y flask en una sola aplicación para que funcione el login de google, ejecutando fastapi y flask al mismo tiempo
flask_app.register_blueprint(google_bp, url_prefix="/login/google")

# Configurar la ruta de inicio de sesión de Google
# Esto redirige a la ruta de inicio de sesión de Google
# y luego redirige a la ruta de callback
# que maneja la respuesta de Google
@flask_app.route("/login/google")
def google_login():
    return redirect(url_for("google.login"))

@flask_app.route("/google_login_callback")
def google_login_callback():
    print("--- DEBUG: Entrando a google_login_callback ---")
    if 'usuario' in session:
        print(f"--- DEBUG: Usuario ya en sesión: {session['usuario']} ---")
        return redirect(url_for("page"))  # Redirige a 'page'
    if not google.authorized:
        print("--- DEBUG: Usuario no autorizado con Google ---")
        return redirect(url_for('google.login'))
    
    resp = google.get("https://www.googleapis.com/oauth2/v3/userinfo")
    if not resp.ok:
        print("--- DEBUG: Error al obtener información del usuario ---")
        flash("Error al obtener información del usuario de Google.", "error")
        return redirect(url_for('login'))
    
    user_info = resp.json()
    print(f"--- DEBUG: Información del usuario de Google: {user_info} ---")
    
    if 'email' not in user_info:
        print("--- DEBUG: No se pudo obtener el correo electrónico del usuario ---")
        flash("No se pudo obtener el correo electrónico del usuario.", "error")
        return redirect(url_for('login'))
    
    google_id = user_info.get("sub")
    user = users_collection.find_one({"google_id": google_id})
    if not user:
        print("--- DEBUG: Usuario no encontrado en la base de datos, creando uno nuevo ---")
        users_collection.insert_one({
            "google_id": google_id,
            "email": user_info["email"],
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "phone_number": user_info.get("phone_number")
        })
    
    session['usuario'] = user_info.get("email")  # Configura la sesión en Flask
    print(f"--- DEBUG: Sesión configurada: {session['usuario']} ---")
    
    response = redirect(url_for("page"))  # Redirige a 'page'
    response.set_cookie("session", serializer.dumps({"email": user_info.get("email")}), httponly=True)
    return response

#-----------------------------------------------------------------------------------------------------------

# Montar la subaplicación Flask en FastAPI
app.mount("/flask", WSGIMiddleware(flask_app))

# 📂 Base directory dinámico (donde está este archivo)
BASE_DIR = Path(__file__).resolve().parent

# ✅ Servir archivos estáticos con el path absoluto
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# ✅ Configurar templates con el path absoluto
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Agregar un filtro personalizado para codificar en Base64
def b64encode_filter(data):
    if data:
        return base64.b64encode(data).decode("utf-8")
    return ""

# Registrar el filtro en Jinja2
templates.env.filters["b64encode"] = b64encode_filter

# Registrar el filtro personalizado
templates.env.filters["b64encode"] = b64encode_filter


#-----------------------------------------------------------------------------------------------------------
#Esto sirve para obtener el usuario actual de la cookie usando el serializer de Flask
def get_current_user(request: Request):
    print("--- DEBUG: Entrando a get_current_user ---")  # DEBUG
    session_cookie = request.cookies.get("session")
    print(f"--- DEBUG: Cookie 'session' encontrada: {session_cookie is not None} ---")  # DEBUG
    if not session_cookie:
        print("--- DEBUG: No hay cookie, retornando None ---")  # DEBUG
        return None
    try:
        data = serializer.loads(session_cookie)
        print(f"--- DEBUG: Cookie decodificada: {data} ---")  # DEBUG
        return data
    except Exception as e:
        print(f"--- DEBUG: ERROR al decodificar cookie: {e} ---")  # DEBUG
        print("--- DEBUG: Retornando None por error en cookie ---")  # DEBUG
        return None

async def require_login(request: Request):
    print(">>> DEBUG: Entrando a require_login <<<")  # DEBUG
    user_session_data = get_current_user(request)
    print(f">>> DEBUG: user_session_data es: {user_session_data} <<<")  # DEBUG
    if not user_session_data:
        print(">>> DEBUG: NO hay sesión, REDIRIGIENDO a login <<<")  # DEBUG
        login_url = request.url_for('login')
        return RedirectResponse(url=login_url, status_code=status.HTTP_303_SEE_OTHER)

    print(">>> DEBUG: SI hay sesión, PERMITIENDO acceso <<<")  # DEBUG
    return user_session_data
#-----------------------------------------------------------------------------------------------------------


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
async def cuenta(request: Request, current_user: dict = Depends(require_login)): # <-- Usar dependencia
    # La dependencia ya verificó que current_user existe
    usuario = users_collection.find_one({"correo": current_user["email"]})
    if not usuario:
        # Esto no debería pasar si la base de datos es consistente, pero es una buena verificación.
        # Podrías redirigir al login o mostrar un error interno.
        return RedirectResponse(url=request.url_for('login'), status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("Mi_Cuenta.html", {"request": request, "usuario": usuario})



@app.get("/logout", name="logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session")
    return response


@app.get("/perfil", name="perfil")
async def perfil(request: Request, current_user: dict = Depends(require_login)): # <-- Usar dependencia
    usuario = users_collection.find_one({"correo": current_user["email"]})
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
         # Podrías mostrar un mensaje indicando que no hubo cambios
         pass

    # --- OPCIONAL PERO RECOMENDADO: Redirigir a la página de cuenta ---
    # para que vea los cambios reflejados (incluida la nueva foto).
    return RedirectResponse(url=request.url_for('cuenta'), status_code=303)

@app.get("/page", name="page")
async def page(request: Request, current_user = Depends(require_login)):
    print("### DEBUG: Ejecutando ruta /page ###")
    if isinstance(current_user, RedirectResponse):
        print("### DEBUG: current_user es RedirectResponse, retornando... ###")
        return current_user
    print(f"### DEBUG: Usuario en /page: {current_user.get('email')} ###")
    return templates.TemplateResponse("page.html", {"request": request, "usuario": current_user})



@app.post("/eliminar_cuenta", name="eliminar_cuenta")
async def eliminar_cuenta(request: Request, email: str = Form(...)):
    users_collection.delete_one({"correo": email})
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

    # 3. (Opcional pero recomendado) Verificar si el producto existe en la colección original
    if not collection.find_one({"_id": obj_product_id}):
         raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 4. Añadir el ID del producto a la lista del usuario en la colección 'listas_usuarios'
    #    Usamos $addToSet para evitar duplicados y upsert=True para crear el documento si no existe.
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

    productos_lista_completa = [] # Lista para los datos completos
    if lista_doc & "productos_ids" in lista_doc: 
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
async def categoria(request: Request, q: str = "", page: int = Query(1, gt=0), current_user = Depends(require_login)):
    """
    Muestra una lista paginada de productos con opción de búsqueda.

    Args:
        request: El objeto de solicitud.
        q: Término de búsqueda opcional.
        page: Número de página actual.

    Returns:
        Plantilla con productos filtrados y paginados.
    """
    
    if isinstance(current_user, RedirectResponse):
        print("### DEBUG: categoria - current_user es RedirectResponse, retornando... ###")
        return current_user
    print(f"### DEBUG: categoria - Usuario en /categoria: {current_user.get('email')} ###")
    productos_por_pagina = 38
    skip = (page - 1) * productos_por_pagina

    # Si hay término de búsqueda, filtra
    filtro = {}
    if q:
        filtro = {
            "Product_Name": {"$regex": re.escape(q), "$options": "i"}
        }

    # Consulta MongoDB con filtro + paginación
    productos = list(collection.find(filtro).skip(skip).limit(productos_por_pagina))

    # Total de productos para la paginación
    total_productos = collection.count_documents(filtro)
    total_paginas = (total_productos + productos_por_pagina - 1) // productos_por_pagina

    return templates.TemplateResponse("categorias.html", {
        "request": request,
        "productos": productos,
        "pagina_actual": page,
        "total_paginas": total_paginas,
        "query": q  # para mantener el valor en el input de búsqueda
    })


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


