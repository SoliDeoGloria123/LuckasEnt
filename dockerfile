# Usa una imagen base de Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia todo el proyecto al contenedor
COPY . /app/

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto donde Uvicorn correrá
EXPOSE 8000

# Ejecuta Uvicorn para iniciar la aplicación FastAPI
CMD ["uvicorn", "front_end.main:app", "--host", "0.0.0.0", "--port", "8000"]


#https://www.youtube.com/watch?v=DoZZiSxXLJs

#docker build -t luckasent .                                                              NOTA: PARA CREAR LA IMAGEN
#docker run -p 5001:5001 --network=host luckasent                                         NOTA: PARA VERLO EN EL LOCAL UNA VEZ SIN RECARGAR
#docker run -p 8000:8000 --network=host -v $(pwd)/SRC:/app/SRC luckasent                  NOTA:LO MISMO QUE EL ANTERIOR SOLO QUE CADA VEZ QUE SE HAGA CAMBIOS EN EL CODIGO SE ACTUALIZA
#docker image rmi -f luckasent                                                            NOTA: se utiliza para eliminar una imagen de Docker de tu sistema
