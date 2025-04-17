import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from pandas import Series
from returns.io import IOResult, IOSuccess, IOFailure
from SRC.back_end.web_scrapping.class_error import unite_indexError
from SRC.back_end.web_scrapping.index import (
    access_to_HTML_general,
    extract_urls,
    extraer_info,
    read_exel_py,
    scrapper,
    soup_bs4,
)


def unite_index(URLS: Series) -> IOResult[list[str | int | float], unite_indexError]:
    try:
        return IOSuccess(
            [
                extraer_info(URL)
                .bind(soup_bs4)  # Aquí se obtiene el objeto BeautifulSoup
                .bind(
                    lambda soup: scrapper(  # Pasa el objeto soup a scrapper
                        soup=soup,
                        Tag="article",
                        attrs="productCard_productCard__M0677", 
                       
                     
                    )
                )
                .bind(lambda ResultSet: access_to_HTML_general(ResultSet, parner="Exito"))
                .unwrap()
                for URL in URLS
            ]
        )
    except Exception as Error:
        return IOFailure(unite_indexError(Error))


def main() -> None:
    read_exel_py("SRC/back_end/web_scrapping/Exito/exito_URLs.csv").bind(
        extract_urls
    ).bind(
        unite_index
    )  # Depuración


main()
