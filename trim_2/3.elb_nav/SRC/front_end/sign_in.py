from fasthtml.common import *

app, rt = fast_app(live=True)

def registro():
    return Section(
        H2("Registrarse", style="text-align: center; margin-bottom: 10px; font-family: Arial; font-weight: bold;"),
        P("Accede a tu cuenta para comparar precios", style="text-align: center; margin-bottom: 20px; font-size: 14px; color: #555;"),
        Form(
            Div(
                Div(
                    Label("Nombre",For="nombre"),
                    Input(id="nombre",type="text",placeholder="Ingrese su nombre",required=True),
                    style="width: 70%; display: inline-block; margin-right: 4%;"
                ),
                Div(
                    Label("Apellido",For="apellido"),
                    Input(id="apellido",type="text",placeholder="Ingrese su apellido",required=True),
                    style="width: 70%; display: inline-block; margin-right: 4%;"
                ),
                style="display: flex; justify-content: space-between;"
            ), 
            
            Div(
                Div(
                    Label("Correo Electrónico",For="correo"),
                    Input(id="correo",type="text",placeholder="Ingrese su correo electrónico",required=True),
                    style="width: 70%; display: inline-block; margin-right: 4%;"
                ),
                Div(
                    Label("Número de teléfono",For="telefono"),
                    Input(id="telefono",type="text",placeholder="Ingrese su teléfono",required=True),
                    style="width: 70%; display: inline-block; margin-right: 4%;"
                ),
                
                style="display: flex; justify-content: space-between; margin-top: 15px;"
           ),
            
            
            Label("Contraseña", For="password"),
            Input(id="password", type="password", placeholder="Ingresa tu contraseña", required=True),
            Label("Confirmar contraseña", For="password"),
            Input(id="password", type="password", placeholder="Ingresa tu contraseña", required=True),
            Button("Registrarse", type="submit", style="background-color:#335CFF; color: white; border-radius: 10px; padding: 10px;"),
            Button("Iniciar sesión con Google", type="submit", style="background-color:white; color:black; border-radius: 10px; padding: 10px;"),
            A("Olvidaste tu contraseña", href="/reset-password",style="display: block; text-align: center; margin-top: 10px; color: blue; text-decoration: none;"),
            method="post",
            
            
        ),
       style="width: 550px; margin: auto; padding:30px; border-radius:50px;"
    )
def centered_page():
    return Div(
        registro(),
        A("Ya tienes cuenta? Inicia Sesión", href="/register", style="position: absolute; top: 20px; right: 20px; font-size: 14px; color: blue; text-decoration: none;"),
        style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; position: relative;"
    )

@rt("/")
def get():
    return Body(centered_page())


serve()