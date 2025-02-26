from fasthtml.common import *

app, rt = fast_app(live=True)

def head():
    return Head(
        Title("LuckasEnt - Comparador de Precios"),
        Link(href="https://cdn.jsdelivr.net/npm/@picocss/pico@1.5.0/css/pico.min.css", rel="stylesheet"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Style("""
            .hero {
                background: url('/static/hero.jpg') center/cover;
                padding: 4rem 1rem;
                color: white;
                text-align: center;
            }
            .partners img {
                height: 50px;
                margin: 0 10px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
            }
            .highlight {
                background-color: var(--card-background-color);
                padding: 2rem;
                border-radius: 10px;
            }
        """)
    )

def navbar():
    return Nav(
        Div(
            Ul(
                Li(Strong("LuckasEnt"))
            ),
            Ul(
                Li(A("Inicio", href="/")),
                Li(A("Comparar Productos", href="/comparar")),
                Li(A("Ofertas", href="/ofertas")),
                Li(A("Más Opciones", href="/opciones"))
            ),
            cls="container-fluid"
        )
    )

def hero_section():
    return Header(
        Div(
            H1("Compara precios y ahorra en tus compras"),
            P("LuckasEnt te permite comparar precios de productos de la canasta familiar en diferentes supermercados de Colombia."),
            A("Descubre", href="/descubre", role="button"),
            cls="hero"
        )
    )

def partners():
    return Section(
        H2("Nuestros Partners"),
        Div(
            Img(src="/static/makro.png", alt="Makro"),
            Img(src="/static/exito.png", alt="Éxito"),
            Img(src="/static/carulla.png", alt="Carulla"),
            Img(src="/static/jumbo.png", alt="Jumbo"),
            Img(src="/static/ara.png", alt="Ara"),
            cls="partners"
        )
    )

def main_content():
    return Main(
        hero_section(),
        Section(
            H2("¡Compara precios y ahorra hoy!"),
            P("Regístrate ahora y descubre las mejores ofertas."),
            A("Registrate", href="SRC/front_end/sign_in.py", role="button"),
            A("Más información", href="/info", role="button", cls="secondary"),
            cls="container"
        ),
        partners(),
        Section(
            H2("Comparativas precisas para que tomes decisiones informadas en tus compras."),
            Div(
                Div(
                    H3("Actualización en tiempo real"),
                    P("Nuestro servicio se actualiza constantemente para darte los mejores precios."),
                    A("Descubre", href="/descubre", role="button"),
                    cls="highlight"
                ),
                Div(
                    H3("Acceso a múltiples supermercados"),
                    P("Encuentra precios de varias tiendas en un solo lugar."),
                    A("Comienza", href="/comienza", role="button"),
                    cls="highlight"
                ),
                Div(
                    H3("Interfaz amigable"),
                    P("Fácil de usar y diseñada para todos."),
                    A("Explora", href="/explora", role="button"),
                    cls="highlight"
                ),
                cls="grid"
            )
        )
    )

def footer():
    return Footer(
        P("© 2024 LuckasEnt. Todos los derechos reservados."),
        Nav(
            Ul(
                Li(A("Inicio", href="/")),
                Li(A("Contáctanos", href="/contacto")),
                Li(A("Ayuda Online", href="/ayuda")),
                Li(A("Política de Privacidad", href="/privacidad")),
                Li(A("Términos de Uso", href="/terminos"))
            )
        ),
        cls="container"
    )

@rt("/")
def get():
    return Html(
        head(),
        Body(
            navbar(),
            main_content(),
            footer()
        )
    )

serve()