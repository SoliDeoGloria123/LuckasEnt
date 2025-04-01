from pandas import Series
from returns.io import IOResult, IOSuccess, IOFailure
from class_error import unite_indexError
from index import (
    access_to_HTML,
    extract_urls,
    extraer_info,
    read_exel_py,
    scrapper,
    soup_bs4,
)


def unite_index(URLS: Series) -> IOResult[str | int | float, unite_indexError]:
    try:
        return IOSuccess(
            extraer_info(URL)
            .bind(soup_bs4)
            .bind(scrapper)
            .bind(lambda ResultSet: access_to_HTML(ResultSet))
            for URL in URLS 
        )
    except Exception as Error:
        return IOFailure(unite_indexError(Error))


def main() -> None:
    read_exel_py("SRC/back_end/web_scrapping/Makro/Makro_URLs.csv").bind(extract_urls).bind(unite_index)


main()
