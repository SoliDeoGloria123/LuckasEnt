# Cargar variables de entorno
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from apscheduler.schedulers.blocking import BlockingScheduler

from pytz import timezone as pytz_timezone # Usa un alias para claridad
from datetime import datetime

from SRC.back_end.web_scrapping.Carulla.index_carulla import main_carulla
from SRC.back_end.web_scrapping.D1.unite_D1 import main_d1
from SRC.back_end.web_scrapping.Exito.index_exito import main_exito
from SRC.back_end.web_scrapping.Jumbo.index_Jumbo import main_jumbo
from SRC.back_end.web_scrapping.Makro.unite_makro import main_makro


load_dotenv()

# Conectar a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.LuckasEnt
collection = db["productos"]

def delete_documents():
    try:
        print("Iniciando limpieza de base de datos...")
        # Eliminar la colección
        db.drop_collection("productos")
        print("Colección 'productos' eliminada.")

        # Volver a crear la colección
        db.create_collection("productos")
        print("Colección 'productos' creada nuevamente.")
    except Exception as e:
        print(f"Error al eliminar y recrear la colección: {e}")

def run_scraping():
    try:
        print("Iniciando scraping...")
        delete_documents()
        print("Limpieza completada.")
        #-------------------------------------#
        main_makro()
        print("Scraping de Makro completado.")
        main_d1()
        print("Scraping de D1 completado.")
        main_exito()
        print("Scraping de Éxito completado.")
        main_carulla()
        print("Scraping de Carulla completado.")
        main_jumbo()
        print("Scraping de Jumbo completado.")
        #-------------------------------------#
        print("Scraping completado.")
    except Exception as e:
        print(f"Error en el scraping: {e}, en la función run_scapping()")
        
def main():
    try:
        bogota_tz_str = "America/Bogota"
        bogota_tz_obj = pytz_timezone(bogota_tz_str)
        scheduler = BlockingScheduler(timezone=bogota_tz_str)
        now_in_bogota = datetime.now(bogota_tz_obj)
        scheduler.add_job(run_scraping, 'interval', hours=2, next_run_time=now_in_bogota)

        print(f"Programador iniciado. El scraping se ejecutará ahora ({now_in_bogota.strftime('%Y-%m-%d %H:%M:%S %Z%z')}) y luego cada 2 horas.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("Programador detenido.")
    except Exception as e:
        print(f"Error en la función main: {e}")

if __name__ == "__main__":
    main()