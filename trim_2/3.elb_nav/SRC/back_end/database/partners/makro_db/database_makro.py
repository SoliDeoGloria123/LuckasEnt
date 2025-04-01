#from pymongo import MongoClient
#import requests
#from io import BytesIO
#from PIL import Image

# Conexión a MongoDB
#client = MongoClient(
#    "mongodb://localhost:27017/"
#)  # Reemplaza con tu conexión si es diferente
#db = client["makro"]
#coleccion = db["productos"]

# Datos del producto (obtenidos mediante web scraping)
#producto_data = {
#    "nombre": "Tamarindo Momposino",
#    "precio_total": 5550,  # En centavos
#    "precio_descuento": 4160,  # En centavos
#    "descuento": 1390,  # En centavos
#    "url": "URL_DEL_PRODUCTO",  # Reemplaza con la URL real
#    "imagen": None,  # Se añadirá la imagen más adelante
#}

# Obtener la imagen (asumiendo que tienes la URL de la imagen)
#try:
##    response = requests.get(URL_DE_LA_IMAGEN)  # Reemplaza con la URL de la imagen
 #   response.raise_for_status()  # Verifica si hubo un error en la solicitud
 #   image = Image.open(BytesIO(response.content))
 #   # Convertir la imagen a un formato adecuado para MongoDB (ej. bytes)
 #   with BytesIO() as buffer:
 #       image.save(buffer, "PNG")  # Puedes usar otros formatos como JPEG
#        producto_data["imagen"] = buffer.getvalue()
#except requests.exceptions.RequestException as e:
#    print(f"Error al obtener la imagen: {e}")
#except Exception as e:
#    print(f"Error al procesar la imagen: {e}")


# Insertar el documento en MongoDB
#try:
#    coleccion.insert_one(producto_data)
#    print("Producto insertado correctamente.")
#except Exception as e:
#    print(f"Error al insertar el producto: {e}")
#
#client.close()
# Cerrar la conexión a MongoDB
