from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd
import os
import logging

# Configuración
API_URL = "http://10.43.101.187/data"
OUTPUT_DIR = "/opt/airflow/datasets"

def obtener_datos(grupo):
    try:
        response = requests.get(API_URL, params={"group_number": grupo}, timeout=10)
        response.raise_for_status()  # Lanza error si hay problema HTTP

        data = response.json()
        df = pd.DataFrame(data["data"])
        batch = data["batch_number"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        group_dir = os.path.join(OUTPUT_DIR, f"group_{grupo}")
        os.makedirs(group_dir, exist_ok=True)

        filename = f"batch_{batch}_{timestamp}.csv"
        filepath = os.path.join(group_dir, filename)

        df.to_csv(filepath, index=False)
        logging.info(f"[Grupo {grupo}] Datos guardados en: {filepath}")

    except Exception as e:
        logging.error(f"[Grupo {grupo}] Error al obtener datos: {e}")
        raise

# Configuración del DAG
default_args = {
    'start_date': datetime(2024, 3, 23),
}

with DAG(
    dag_id="descargar_datos_api",
    schedule_interval="*/5 * * * *",
    catchup=False,
    default_args=default_args,
    description="DAG para obtener datos desde la API por grupo"
) as dag:

    for grupo in range(1, 11):
        PythonOperator(
            task_id=f"obtener_datos_grupo_{grupo}",
            python_callable=obtener_datos,
            op_args=[grupo]
        )

