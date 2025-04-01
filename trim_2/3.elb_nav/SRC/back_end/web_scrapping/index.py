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
        return IOSuccess(pd.read_csv(exelFile, header=None))
    except Exception as Error:
        return IOFailure(ReadExcelPyError(Error))


# Extrae solo la Columna donde estan la URLS 
def extract_urls(pd: DataFrame) -> IOResult[Series, ExtractUrlsError]:
    try:
        return IOSuccess(pd[1])  # Changed from pd[0] to pd[1] to get URL column
    except Exception as Error:
        return IOFailure(ExtractUrlsError(Error))


# Usa la Libreria PlayWright para abir un Browser y asi obtener el HTML de la Pagina Web
def extraer_info(URL: str) -> IOResult[str, extraer_infoError]:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(URL)
            page.wait_for_URL(URL)
            content = page.content()
            browser.close()
            return content
    except Exception as Error:
        return IOFailure(extraer_infoError(Error))


# Crea un DOM para BS4 lo entienda
def soup_bs4(
    HTML: str, features: str = "html.parser"
) -> IOResult[BeautifulSoup, soup_bs4error]:
    try:
        return IOSuccess(BeautifulSoup(HTML, features))
    except Exception as Error:
        return IOFailure(soup_bs4error(Error))


# Extrae el PLP("Product Listing Page")
def scrapper(
    soup: BeautifulSoup, Tag: Tag = "div", attrs: str = "grid-pod"
) -> IOResult[ResultSet[Tag], scrapperError]:
    try:
        return (
            IOSuccess(soup.find_all(Tag, class_=attrs))
            if soup.find_all(Tag, class_=attrs)
            else IOSuccess(NOT_FOUND)
        )
    except Exception as Error:
        return IOFailure(scrapperError(Error))


# Crea una funcion dry(No te repitas a ti mismo) para raspar la informacion de cada tag
def access_to_HTML(CardsTag: ResultSet[Tag]) -> IOResult[Tag, access_to_HTMLError]:
    try:
        return IOSuccess(extract_object_PLP(card) for card in CardsTag)
    except Exception as Error:
        return IOFailure(access_to_HTMLError(Error))


def extract_object_PLP(card: Tag) -> IOResult[str | int | float, access_to_HTMLError]:
    return IOResult.do(
        {"Brand": Brand, "Product Name": Product_name, "Total_price": Total_price}
        for Brand in card.select_one('b[class*="title-rebrand"]').text
        for Product_name in card.select_one('b[class*="subTitle-rebrand"]').text
        for Total_price in card.select_one('span[class*="line-height-22"]').text
    )
