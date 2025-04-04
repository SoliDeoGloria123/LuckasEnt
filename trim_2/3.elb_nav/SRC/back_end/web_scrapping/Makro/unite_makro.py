import sys
import os
from pandas import Series
from returns.io import IOResult, IOSuccess, IOFailure
from SRC.back_end.web_scrapping.class_error import unite_indexError
from SRC.back_end.web_scrapping.index import (
    access_to_HTML,
    extract_urls,
    extraer_info,
    read_exel_py,
    scrapper,
    soup_bs4,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))


def unite_index(URLS: Series) -> IOResult[list[str | int | float], unite_indexError]:
    try:
        return IOSuccess(
            [
                extraer_info(URL)
                .bind(soup_bs4)  # Aquí se obtiene el objeto BeautifulSoup
                .bind(
                    lambda soup: scrapper(  # Pasa el objeto soup a scrapper
                        soup=soup,
                        Tag="div",
                        attrs="card-product-vertical",
                    )
                )
                .bind(lambda ResultSet: access_to_HTML(ResultSet, parner="Makro"))
                .unwrap()
                for URL in URLS
            ]
        )
    except Exception as Error:
        return IOFailure(unite_indexError(Error))


def main() -> None:
    read_exel_py("SRC/back_end/web_scrapping/Makro/Makro_URLs.csv").bind(
        extract_urls
    ).bind(
        unite_index
    )  # Depuración


main()
