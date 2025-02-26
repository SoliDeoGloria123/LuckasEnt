from fasthtml.common import *

app, rt = fast_app(live=True)

def title():
    return Div(
         Span("LUCHASENT", style="font-size: 24px; font-weight: bold; text-transform: uppercase; font-family: sans-serif; position: absolute; top: 20px; left: 20px;"),
        style="position: absolute; top: 20px; left: 20px; font-family: sans-serif; color: black;"
    )



def login_form():
    return Section(
        H2("Iniciar Sesión", style="text-align: center; margin-bottom: 10px; font-family: Arial; font-weight: bold;"),
        P("Accede a tu cuenta para comparar precios", style="text-align: center; margin-bottom: 20px; font-size: 14px; color: #555;"),
        Form(
            Label("Correo Electrónico", For="username"),
            Input(id="username", type="text", placeholder="Ingresa tu Correo Electrónico", required=True),
            Label("Contraseña", For="password"),
            Input(id="password", type="password", placeholder="Ingresa tu contraseña", required=True),
            Button("Ingresar", type="submit", style="background-color:#335CFF; color: white; border-radius: 10px; padding: 10px;"),
            Button("Iniciar sesión con Google", type="submit", style="background-color:white; color:black; border-radius: 10px; padding: 10px;"),
            A("Olvidaste tu contraseña", href="/reset-password",style="display: block; text-align: center; margin-top: 10px; color: blue; text-decoration: none;"),
            method="post",
            
        ),
       style="width: 550px; margin: auto; padding:30px; border-radius:50px;"
    )

def centered_page():
    return Div(
        title(),
        login_form(),
        A("No tienes cuenta? Regístrate", href="/register", style="position: absolute; top: 20px; right: 20px; font-size: 14px; color: blue; text-decoration: none;"),
        style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; position: relative;"
    )

@rt("/")
def get():
    return Body(centered_page())

serve()