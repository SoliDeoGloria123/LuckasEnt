import re
import pandas as pd
import colorama
from pandas import DataFrame, Series
from bs4 import BeautifulSoup, ResultSet, Tag
from playwright.sync_api import sync_playwright
from returns.io import IOResult, IOSuccess, IOFailure
from SRC.back_end.database.submit_data import insert_date
from SRC.back_end.web_scrapping.class_error import (
    NOT_FOUND,
    ReadExcelPyError,
    ExtractUrlsError,
    access_to_HTMLError,
    extract_object_PLPError,
    extraer_infoError,
    scrapperError,
    soup_bs4error,
)

# Inicializa colorama
colorama.init()


# Lee el archivo Excel
def read_exel_py(exelFile: str) -> IOResult[DataFrame, ReadExcelPyError]:
    try:
        return IOSuccess(pd.read_csv(exelFile))
    except Exception as Error:
        return IOFailure(ReadExcelPyError(Error))


# Extrae solo la columna donde están las URLs
def extract_urls(pd: DataFrame) -> IOResult[Series, ExtractUrlsError]:
    try:
        if "URL" in pd.columns:
            return IOSuccess(
                pd["URL"].dropna().reset_index(drop=True)
            )  # Selecciona la columna "URL" por nombre
        else:
            raise ValueError("La columna 'URL' no existe en el archivo CSV.")
    except Exception as Error:
        return IOFailure(ExtractUrlsError(Error))


# Usa Playwright para obtener el HTML de la página web
def extraer_info(URL: str) -> IOResult[str, extraer_infoError]:
    try:
        print(f"Launching Playwright for URL: {URL}")  # Mensaje de depuración
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True
            )  # Asegúrate de que headless=False
            print("Browser launched successfully.")  # Mensaje de depuración
            page = browser.new_page()
            page.goto(URL, timeout=60000)
            print(f"Navigated to URL: {URL}")  # Mensaje de depuración
            page.wait_for_load_state("networkidle")
            content = page.content()
            print("Page content retrieved.")  # Mensaje de depuración
            browser.close()
            return IOSuccess(content)
    except Exception as Error:
        print(f"Error occurred: {Error}")  # Mensaje de depuración
        return IOFailure(extraer_infoError(Error))


# Crea un DOM para BeautifulSoup
def soup_bs4(
    HTML: str, features: str = "html.parser"
) -> IOResult[BeautifulSoup, soup_bs4error]:
    try:
        return IOSuccess(BeautifulSoup(HTML, features))
    except Exception as Error:
        return IOFailure(soup_bs4error(Error))


# Extrae los productos de la página (PLP)
def scrapper(
    soup: BeautifulSoup, Tag: str = "", attrs: str = ""
) -> IOResult[ResultSet[Tag], scrapperError]:
    try:
        print(f"Scrapper called with Tag: {Tag}, attrs: {attrs}")  # Depuración
        elements = soup.find_all(Tag, class_=attrs)
        print(f"Found elements: {len(elements)}")  # Depuración
        return IOSuccess(elements) if elements else IOSuccess(NOT_FOUND)
    except Exception as Error:
        print(f"Error in scrapper: {Error}")  # Depuración
        return IOFailure(scrapperError(Error))


# Extrae la información de cada producto
def access_to_HTML(
    CardsTag: ResultSet[Tag], parner: str = ""
) -> IOResult[list[dict], access_to_HTMLError]:
    try:
        return IOSuccess(
            [print_and_return(extract_object_PLP(card, parner)) for card in CardsTag]
        )
    except Exception as Error:
        return IOFailure(access_to_HTMLError(Error))
    
def access_to_HTML_general(
    CardsTag: ResultSet[Tag], parner: str = ""
) -> IOResult[list[dict], access_to_HTMLError]:
    try:
        return IOSuccess(
            [print_and_return(extract_object_PLP_general(card, parner)) for card in CardsTag]
        )
    except Exception as Error:
        return IOFailure(access_to_HTMLError(Error))
        


def print_and_return(result: dict) -> dict:
    print("")  # Imprime una línea en blanco
    print(
        f"{colorama.Fore.GREEN}{result}{colorama.Style.RESET_ALL}"
    )  # Imprime el resultado
    insert_date(result)  # Inserta los datos en MongoDB
    return result  # Devuelve el resultado


# Ajusta los precios según la lógica
def adjust_prices(total_price: str, discount_price: str) -> tuple:
    return (
        (discount_price, NOT_FOUND)
        if total_price == NOT_FOUND
        else (total_price, discount_price)
    )


# Extrae los datos de un producto específico
def extract_object_PLP(
    card: Tag, parner: str = ""
) -> IOResult[dict, extract_object_PLPError]:
    try:
        return {
            "Parner": parner,
            "Imagen": extract_image_src(card),
            "Product_Name": (
                re.sub(
                    r"\b\d+(\.\d+)?\s?(pesos|PESOS|COP|usd|USD)?\b",  # Elimina precios del nombre
                    "",
                    (
                        card.select_one('p[class*="prod__name"]').text.strip()
                        if card.select_one('p[class*="prod__name"]')
                        else NOT_FOUND
                    ),
                )
                .strip()
                .rsplit(" ", 1)[0]
                if (
                    card.select_one('p[class*="prod__name"]')
                    and re.search(
                        r"(\d+\s?(?:kg|KG|g|ml|l|un|unidad|gr))$",
                        card.select_one('p[class*="prod__name"]').text.strip(),
                        re.IGNORECASE,
                    )
                )
                else re.sub(
                    r"\b\d+(\.\d+)?\s?(pesos|PESOS|COP|usd|USD)?\b",  # Elimina precios del nombre
                    "",
                    (
                        card.select_one('p[class*="prod__name"]').text.strip()
                        if card.select_one('p[class*="prod__name"]')
                        else NOT_FOUND
                    ),
                ).strip()
            ),
            "Weight": (
                re.search(
                    r"(\d+\s?(?:kg|g|ml|l|un|unidad|gr))$",
                    card.select_one('p[class*="prod__name"]').text.strip(),
                    re.IGNORECASE,
                )
                .group(1)
                .upper()
                if (
                    card.select_one('p[class*="prod__name"]')
                    and re.search(
                        r"(\d+\s?(?:kg|g|ml|l|un|unidad|gr))$",
                        card.select_one('p[class*="prod__name"]').text.strip(),
                        re.IGNORECASE,
                    )
                )
                else NOT_FOUND
            ),
            "Total_Price": adjust_prices(
                (
                    card.select_one(
                        'p[class*="prod-crossed-out_price_old"]'
                    ).text.strip()
                    if card.select_one('p[class*="prod-crossed-out_price_old"]')
                    else NOT_FOUND
                ),
                (
                    card.select_one('p[class*="base__price"]').text.strip()
                    if card.select_one('p[class*="base__price"]')
                    else NOT_FOUND
                ),
            )[0],
            "Precio_con_Descuento": adjust_prices(
                (
                    card.select_one(
                        'p[class*="prod-crossed-out_price_old"]'
                    ).text.strip()
                    if card.select_one('p[class*="prod-crossed-out_price_old"]')
                    else NOT_FOUND
                ),
                (
                    card.select_one('p[class*="base__price"]').text.strip()
                    if card.select_one('p[class*="base__price"]')
                    else NOT_FOUND
                ),
            )[1],
        }
    except Exception as Error:
        return extract_object_PLPError(Error)
    
        
def extract_object_PLP_general(card: Tag, partner: str = "") -> IOResult[dict, extract_object_PLPError]:
     try:
        if partner == "Jumbo":
            product_name_raw = (
                card.select_one('h3[class*="vtex-product-summary-2-x-productNameContainer"]').text.strip()
                if card.select_one('h3[class*="vtex-product-summary-2-x-productNameContainer"]')
                else NOT_FOUND
            )

            # Limpiar nombre quitando precios y cortar última palabra si es peso
            product_name = (
                re.sub(r"\b\d+(\.\d+)?\s?(pesos|PESOS|COP|usd|USD)?\b", "", product_name_raw)
                .strip()
                .rsplit(" ", 1)[0]
                if re.search(r"(\d+\s?(?:kg|g|ml|l|un|unidad|gr))$", product_name_raw, re.IGNORECASE)
                else re.sub(r"\b\d+(\.\d+)?\s?(pesos|PESOS|COP|usd|USD)?\b", "", product_name_raw).strip()
            )

            # Buscar peso
            peso = (
                re.search(r"(\d+\s?(?:kg|g|ml|l|un|unidad|gr))$", product_name_raw, re.IGNORECASE)
                .group(1)
                .upper()
                if re.search(r"(\d+\s?(?:kg|g|ml|l|un|unidad|gr))$", product_name_raw, re.IGNORECASE)
                else NOT_FOUND
            )

            return IOSuccess({
                "Partner": partner,
                "Imagen": extract_image_src(card),
                "Product Name": product_name,
                "Weight": peso,
                "Total Price": adjust_prices(
                    (
                        card.select_one('div[class*="pr2 items-stretch"]').text.strip()
                        if card.select_one('div[class*="pr2 items-stretch"]')
                        else NOT_FOUND
                    ),
                    (
                        card.select_one('div[class*="pr2 items-stretch"]').text.strip()
                        if card.select_one('div[class*="pr2 items-stretch"]')
                        else NOT_FOUND
                    )
                )[0],
                "Precio con Descuento": adjust_prices(
                    (
                        card.select_one('spadivn[class*="flex items-center justify-center tiendasjumboqaio-jumbo-minicart-2-x-containerFlag "]').text.strip()
                        if card.select_one('div[class*="flex items-center justify-center tiendasjumboqaio-jumbo-minicart-2-x-containerFlag"]')
                        else NOT_FOUND
                    ),
                    (
                        card.select_one('div[class*="flex items-center justify-center tiendasjumboqaio-jumbo-minicart-2-x-containerFlag"]').text.strip()
                        if card.select_one('div[class*="flex items-center justify-center tiendasjumboqaio-jumbo-minicart-2-x-containerFlag"]')
                        else NOT_FOUND
                    )
                )[1],
            })

        else:
            return IOFailure(extract_object_PLPError(Exception(f"Partner '{partner}' no implementado aún.")))
     except Exception as Error:
         return extract_object_PLPError(Error)
         
         
def extract_object_PLP_general(card: Tag, partner: str = "") -> IOResult[dict, extract_object_PLPError]:
     try:
        if partner == "Jumbo":
            product_name_raw = (
                card.select_one('h3[class*="vtex-product-summary-2-x-productNameContainer mv0"]').text.strip()
                if card.select_one('h3[class*="vtex-product-summary-2-x-productNameContainer mv0"]')
                else NOT_FOUND
            )

            # Limpiar nombre quitando precios y cortar última palabra si es peso
            product_name = (
                re.sub(r"\b\d+(\.\d+)?\s?(pesos|PESOS|COP|usd|USD)?\b", "", product_name_raw)
                .strip()
                .rsplit(" ", 1)[0]
                if re.search(r"(\d+\s?(?:kg|g|ml|l|un|unidad|gr))$", product_name_raw, re.IGNORECASE)
                else re.sub(r"\b\d+(\.\d+)?\s?(pesos|PESOS|COP|usd|USD)?\b", "", product_name_raw).strip()
            )

            # Buscar peso
            peso = (
                re.search(r"(\d+\s?(?:kg|g|ml|l|un|unidad|gr))$", product_name_raw, re.IGNORECASE)
                .group(1)
                .upper()
                if re.search(r"(\d+\s?(?:kg|g|ml|l|un|unidad|gr))$", product_name_raw, re.IGNORECASE)
                else NOT_FOUND
            )

            return IOSuccess({
                "Partner": partner,
                "Imagen": extract_image_src(card),
                "Product Name": product_name,
                "Weight": peso,
                "Total Price": adjust_prices(
                    (
                        card.select_one('div[class*="tiendasjumboqaio-jumbo-minicart-2-x-price"]').text.strip()
                        if card.select_one('div[class*="tiendasjumboqaio-jumbo-minicart-2-x-price"]')
                        else NOT_FOUND
                    ),
                    (
                        card.select_one('div[class*="tiendasjumboqaio-jumbo-minicart-2-x-price"]').text.strip()
                        if card.select_one('div[class*="tiendasjumboqaio-jumbo-minicart-2-x-price"]')
                        else NOT_FOUND
                    )
                )[0],
                "Precio con Descuento": adjust_prices(
                    (
                        card.select_one('spadivn[class*="flex items-center justify-center tiendasjumboqaio-jumbo-minicart-2-x-containerFlag "]').text.strip()
                        if card.select_one('div[class*="flex items-center justify-center tiendasjumboqaio-jumbo-minicart-2-x-containerFlag"]')
                        else NOT_FOUND
                    ),
                    (
                        card.select_one('div[class*="flex items-center justify-center tiendasjumboqaio-jumbo-minicart-2-x-containerFlag"]').text.strip()
                        if card.select_one('div[class*="flex items-center justify-center tiendasjumboqaio-jumbo-minicart-2-x-containerFlag"]')
                        else NOT_FOUND
                    )
                )[1],
            })

        else:
            return IOFailure(extract_object_PLPError(Exception(f"Partner '{partner}' no implementado aún.")))
     except Exception as Error:
         return extract_object_PLPError(Error) 




# Extrae el atributo 'src' de una etiqueta <img> directamente con funciones encadenadas
def extract_image_src(card: Tag) -> str:
    try:
        return (
            card.select_one("img")["src"]
            if card.select_one("img") and "src" in card.select_one("img").attrs
            else NOT_FOUND
        )
    except Exception:
        return NOT_FOUND
