import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from sklearn.preprocessing import StandardScaler 
from sklearn.ensemble import RandomForestClassifier

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.LuckasEnt

# Colección de productos
collection = db["productos"]

# Ruta para guardar los modelos
KMEANS_MODEL_PATH = "kmeans_model.pkl" #.pkl significa que es un archivo de Python para almacenar objetos de Python
BEST_OFFER_MODEL_PATH = "best_offer_model.pkl"

# Función para entrenar y guardar el modelo de clustering
def train_kmeans_model(df):
    vectorizer = TfidfVectorizer() #Esta función sirve para convertir texto en una matriz de características
    product_name_features = vectorizer.fit_transform(df["Product_Name"])#La función fit_transform convierte el texto en una matriz de características
    kmeans = KMeans(n_clusters=10, random_state=42)#kmeans es un algoritmo de agrupamiento que divide los datos en k grupos, lo que significa que el número de grupos es 10 y la k significa que el número de grupos es 10
    kmeans.fit(product_name_features)#Esto sirve para ajustar el modelo a los datos 
    joblib.dump(kmeans, KMEANS_MODEL_PATH)# Esto sirve para guardar el modelo entrenado en un archivo erprise, es decir, el modelo se guarda en un archivo llamado kmeans_model.pkl
    return kmeans

# Función para entrenar y guardar el modelo supervisado
def train_best_offer_model(df):
    X = df[["Precio_Por_Peso", "Weight", "Cluster"]] #Datos de entrada para el modelo de forma controlada
    y = df["Best_Offer"]
    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)
    joblib.dump(model, BEST_OFFER_MODEL_PATH)
    return model

# Función principal para analizar productos y mostrar las mejores ofertas
def data_analist_products(search_query: str = "", page: int = 1, page_size: int = 10):
    # Obtener datos de MongoDB
    df = pd.DataFrame(
        list(
            collection.find(
                {"Product_Name": {"$regex": search_query, "$options": "i"}},
                {"Product_Name": 1, "Total_Price": 1, "Weight": 1, "Parner": 1, "Imagen": 1},
            )
        )
    )

    if df.empty:
        return {"productos": [], "total_productos": 0}

    # Preprocesar datos
    df = df.assign(
        Weight=lambda df: pd.to_numeric(df["Weight"].str.extract(r"(\d+\.?\d*)")[0], errors="coerce"),
        Total_Price=lambda df: pd.to_numeric(
            df["Total_Price"]
            .str.replace(r"[^\d.,]", "", regex=True)
            .str.replace(r"\.(?=\d{3}(,|$))", "")
            .str.replace(",", "."),
            errors="coerce",
        ),
        Precio_Por_Peso=lambda df: df["Total_Price"] / df["Weight"],
    ).dropna(subset=["Precio_Por_Peso"])

    # Cargar o entrenar el modelo de clustering
    if os.path.exists(KMEANS_MODEL_PATH):
        kmeans = joblib.load(KMEANS_MODEL_PATH)
    else:
        kmeans = train_kmeans_model(df)

    # Asignar clústeres a los productos
    vectorizer = TfidfVectorizer()
    df["Cluster"] = kmeans.predict(vectorizer.fit_transform(df["Product_Name"]))

    # Seleccionar las mejores ofertas por clúster
    best_offers = df.groupby("Cluster").apply(lambda grupo: grupo.loc[grupo["Precio_Por_Peso"].idxmin()]).reset_index(drop=True)

    # Cargar o entrenar el modelo supervisado
    if os.path.exists(BEST_OFFER_MODEL_PATH):
        best_offer_model = joblib.load(BEST_OFFER_MODEL_PATH)
    else:
        # Etiquetar datos para entrenamiento supervisado (esto es un ejemplo, debes ajustar según tus datos)
        best_offers["Best_Offer"] = 1  # Etiqueta ficticia para entrenamiento inicial
        best_offer_model = train_best_offer_model(best_offers)

    # Predecir las mejores ofertas
    best_offers["Predicted_Best_Offer"] = best_offer_model.predict(best_offers[["Precio_Por_Peso", "Weight", "Cluster"]])

    # Filtrar las mejores ofertas predichas
    filtered_offers = best_offers[best_offers["Predicted_Best_Offer"] == 1]

    # Paginación
    total_productos = len(filtered_offers)
    productos_paginados = filtered_offers.iloc[(page - 1) * page_size : page * page_size].assign(
        Total_Price=lambda df: df["Total_Price"].apply(lambda x: f"${int(x * 10):,}00".replace(",", ".")),
        Weight=lambda df: df["Weight"].apply(lambda x: f"{x:.0f}G" if x < 1 else f"{x:.0f}KG"),
    ).to_dict(orient="records")

    return {"productos": productos_paginados, "total_productos": total_productos}