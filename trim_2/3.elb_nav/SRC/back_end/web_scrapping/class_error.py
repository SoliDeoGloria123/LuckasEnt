from typing import Literal


NOT_FOUND: TypeError = Literal["NOT FOUND"]


class ReadExcelPyError(Exception):
    def __init__(self, error):
        self.message = f"Sorry, something happened when reading the excel, the error is this, it says that: {error}"
        super().__init__(self.message)


class ExtractUrlsError(Exception):
    def __init__(self, error):
        self.message = f"Sorry, something has happened when trying to extract the URLs, the error is this, it says that: {error}"
        super().__init__(self.message)


class extraer_infoError(Exception):
    def __init__(self, error):
        self.message = f"Sorry, something happened when I tried to extract the HTML using Playwright, the error is this, it says that: {error}"
        super().__init__(self.message)


class soup_bs4error(Exception):
    def __init__(self, error):
        self.message = f"Sorry, something happened when I tried to create the DOM with BeautifullSoup, the error is this, it says that: {error}"
        super().__init__(self.message)


class scrapperError(Exception):
    def __init__(self, error):
        self.message = f"Sorry, something happened when I tried to create the DOM with BeautifullSoup, the error is this, it says that: {error}"
        super().__init__(self.message)


class access_to_HTMLError(Exception):
    def __init__(self, error):
        self.message = f"Sorry, something happened when I tried to use the general function to extract the information from a selector, the error is this, it says that: {error}"
        super().__init__(self.message)


class unite_indexError(Exception):
    def __init__(self, error):
        self.message = f"Sorry, something happened when I tried to use a function in the process of joining functions, the error is this, it says that: {error}"
        super().__init__(self.message)
