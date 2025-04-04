NOT_FOUND = "NOT_FOUND"  # Define un valor para NOT_FOUND


class ReadExcelPyError(Exception):
    def _init_(self, error):
        self.message = f"Sorry, something happened when reading the excel, the error is this, it says that: {error}"
        print(self.message)  # Imprime el mensaje automáticamente
        super()._init_(self.message)


class ExtractUrlsError(Exception):
    def _init_(self, error):
        self.message = f"Sorry, something has happened when trying to extract the URLs, the error is this, it says that: {error}"
        print(self.message)  # Imprime el mensaje automáticamente
        super()._init_(self.message)


class extraer_infoError(Exception):
    def _init_(self, error):
        self.message = f"Sorry, something happened when I tried to extract the HTML using Playwright, the error is this, it says that: {error}"
        print(self.message)  # Imprime el mensaje automáticamente
        super()._init_(self.message)


class soup_bs4error(Exception):
    def _init_(self, error):
        self.message = f"Sorry, something happened when I tried to create the DOM with BeautifullSoup, the error is this, it says that: {error}"
        print(self.message)  # Imprime el mensaje automáticamente
        super()._init_(self.message)


class scrapperError(Exception):
    def _init_(self, error):
        self.message = f"Sorry, something happened when I tried to create the DOM with BeautifullSoup, the error is this, it says that: {error}"
        print(self.message)  # Imprime el mensaje automáticamente
        super()._init_(self.message)


class access_to_HTMLError(Exception):
    def _init_(self, error):
        self.message = f"Sorry, something happened when I tried to use the general function to extract the information from a selector, the error is this, it says that: {error}"
        print(self.message)  # Imprime el mensaje automáticamente
        super()._init_(self.message)


class unite_indexError(Exception):
    def _init_(self, error):
        self.message = f"Sorry, something happened when I tried to use a function in the process of joining functions, the error is this, it says that: {error}"
        print(self.message)  # Imprime el mensaje automáticamente
        super()._init_(self.message)


class extract_object_PLPError(Exception):
    def _init_(self, error):
        self.message = f"Sorry, something happened in the extract_object_PLP function, the error is: {error}"
        print(self.message)  # Imprime el mensaje automáticamente
        super()._init_(self.message)
