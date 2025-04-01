import pandas as pd
from pandas import DataFrame, Series
from bs4 import BeautifulSoup, ResultSet, Tag
from playwright.sync_api import sync_playwright
from returns.io import IOResult, IOSuccess, IOFailure
import colorama

from class_error import (
    NOT_FOUND,
    ReadExcelPyError,
    ExtractUrlsError,
    access_to_HTMLError,
    extraer_infoError,
    scrapperError,
    soup_bs4error,
)

# Inicializa colorama
colorama.init()


# Lee el archivo Excel
def read_exel_py(exelFile: str) -> IOResult[DataFrame, ReadExcelPyError]:
    try:
        return IOSuccess(pd.read_excel(exelFile, header=None))
    except Exception as Error:
        return IOFailure(ReadExcelPyError(Error))


# Extrae solo la columna donde están las URLs
def extract_urls(pd: DataFrame) -> IOResult[Series, ExtractUrlsError]:
    try:
        return IOSuccess(pd[1])
    except Exception as Error:
        return IOFailure(ExtractUrlsError(Error))


# Usa Playwright para obtener el HTML de la página web
def extraer_info(URL: str) -> IOResult[str, extraer_infoError]:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(URL)
            page.wait_for_load_state("networkidle")
            content = page.content()
            browser.close()
            return IOSuccess(content)
    except Exception as Error:
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
    soup: BeautifulSoup, Tag: str = "div", attrs: str = "grid-pod"
) -> IOResult[ResultSet[Tag], scrapperError]:
    try:
        elements = soup.find_all(Tag, class_=attrs)
        return IOSuccess(elements) if elements else IOSuccess(NOT_FOUND)
    except Exception as Error:
        return IOFailure(scrapperError(Error))


# Extrae la información de cada producto
def access_to_HTML(
    CardsTag: ResultSet[Tag],
) -> IOResult[list[dict], access_to_HTMLError]:
    try:
        return IOSuccess([extract_object_PLP(card) for card in CardsTag])
    except Exception as Error:
        return IOFailure(access_to_HTMLError(Error))


# Extrae los datos de un producto específico
def extract_object_PLP(card: Tag) -> dict:
    try:
        return {
            "Brand": (
                card.select_one('b[class*="title-rebrand"]').text.strip()
                if card.select_one('b[class*="title-rebrand"]')
                else "N/A"
            ),
            "Product Name": (
                card.select_one('b[class*="subTitle-rebrand"]').text.strip()
                if card.select_one('b[class*="subTitle-rebrand"]')
                else "N/A"
            ),
            "Total Price": (
                card.select_one('span[class*="line-height-22"]').text.strip()
                if card.select_one('span[class*="line-height-22"]')
                else "N/A"
            ),
        }
    except Exception:
        return {"Brand": "N/A", "Product Name": "N/A", "Total Price": "N/A"}
