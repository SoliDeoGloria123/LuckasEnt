from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Conexión a MongoDB
client = MongoClient("mongodb+srv://juanjuanddev:hR7m3QxGgMf5BOKv@cluster0.mnzsa9g.mongodb.net/LuckasEnt?retryWrites=true&w=majority")
db = client.LuckasEnt
collection = db["productos"]

@app.route('/categorias')
def categorias():
    productos = list(collection.find()) # Obtener los productos de la colección
    return render_template('categorias.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)