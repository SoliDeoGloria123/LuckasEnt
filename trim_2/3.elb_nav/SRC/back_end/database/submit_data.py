from pymongo import MongoClient

# Conectar a MongoDB
client = MongoClient(
    "mongodb+srv://juanjuanddev:hR7m3QxGgMf5BOKv@cluster0.mnzsa9g.mongodb.net/LuckasEnt?retryWrites=true&w=majority"
)
db = client.LuckasEnt  # Cambia 'nombre_de_tu_bd' por el nombre de tu base de datos
collection = db["productos"]  # type: ignore # Cambia 'nombre_de_tu_coleccion' por el nombre de tu colección


def insert_date(producto_data: dict) -> None:
    try:
        # Insertar el documento en MongoDB
        collection.insert_one(producto_data)
        print("Producto guardado")
    except Exception as e:
        print(f"Error al guardar el producto: {e}")
