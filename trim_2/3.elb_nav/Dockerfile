FROM mcr.microsoft.com/playwright/python:v1.50.0-jammy

WORKDIR /app

# Copiar los requisitos del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

ENV PYTHONPATH=/app

# Comando para ejecutar el scraping
CMD ["python", "SRC/back_end/web_scrapping/ent.py"]

#docker build -t scraping-service -f Dockerfile.scrapper .     NOTA: Esto es para crear la imagen
#docker run --env-file .env scraping-service                   NOTA: Esto es para ejecutar la imagen