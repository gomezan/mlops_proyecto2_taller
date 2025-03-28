from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import pandas as pd

RAW_DATA_DIR = "/opt/airflow/datasets"
OUTPUT_DIR = os.path.join(RAW_DATA_DIR, "processed")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "covertype_preprocessed.csv")

def preprocess_covertype():
    all_dataframes = []

    # ✅ Definir nombres de columnas esperados (13 columnas reales)
    columnas = [
        "Elevation", "Aspect", "Slope",
        "Horizontal_Distance_To_Hydrology", "Vertical_Distance_To_Hydrology",
        "Horizontal_Distance_To_Roadways", "Hillshade_9am", "Hillshade_Noon",
        "Hillshade_3pm", "Horizontal_Distance_To_Fire_Points",
        "Wilderness_Area", "Soil_Type", "Cover_Type"
    ]

    for group in range(1, 11):
        group_path = os.path.join(RAW_DATA_DIR, f"group_{group}")
        if not os.path.exists(group_path):
            continue

        for file in os.listdir(group_path):
            if file.endswith(".csv"):
                file_path = os.path.join(group_path, file)
                # ✅ Leer CSV sin encabezado, asignando los nombres correctos
                df = pd.read_csv(file_path, header=None, names=columnas)
                all_dataframes.append(df)

    if not all_dataframes:
        raise Exception("No se encontraron archivos CSV para procesar.")

    df_final = pd.concat(all_dataframes, ignore_index=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_final.to_csv(OUTPUT_FILE, index=False, header=True)
    print(f"✅ Datos preprocesados guardados en: {OUTPUT_FILE}")


with DAG(
    dag_id="preprocess_covertype",
    start_date=datetime(2025, 3, 25),
    schedule_interval="@daily",
    catchup=False,
    description="Preprocesa los datos descargados de la API y guarda CSV unificado"
) as dag:

    preprocess_task = PythonOperator(
        task_id="preprocess_covertype_task",
        python_callable=preprocess_covertype
    )

preprocess_task


