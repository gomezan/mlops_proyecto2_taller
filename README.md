Proyecto 2 
MLOps: Modelo de Clasificación de Cobertura Forestal

Integrantes: 
•	Maria del Mar Montenegro Mafla
•	Andrés Gómez
•	Juan Felipe Bocanegra

Introducción:
En este proyecto se busca desarrollar, entrenar e implementar un modelo para la clasificación de tipos de cobertura foresta, utilizando las herramientas Airflow como orquestador, MLFlow, para registrar experimentos y el modelo final; Minio como almacenamiento de objetos y MySQL como base de datos de la metada.

API de datos:....

Estructura del Repositorio:

El repositorio está organizado de la siguiente manera:
•	airflow/: Contiene los DAGs y configuraciones para la orquestación de flujos de trabajo utilizando Apache Airflow.

Dags:
1. descargar_datos_api.py
Este archivo automatiza el proceso de recolección de datos desde una API externa (API Descrita anteriormente)
Objetivo:
Automatizar la descarga periódica (cada 5 minutos) de datos en formato JSON desde un endpoint API, organizarlos por grupo, convertirlos en CSV y almacenarlos localmente para su posterior procesamiento o entrenamiento de modelos de ML.
Componentes clave:
API_URL: URL base de la API desde donde se extraen los datos.
OUTPUT_DIR: Ruta local donde se almacenarán los archivos CSV.
obtener_datos(grupo): Función Python que realiza la solicitud HTTP, transforma la respuesta a un DataFrame de pandas y guarda los datos en un archivo CSV, organizando los datos por grupo.
PythonOperator: Crea una tarea por cada grupo (1 al 10), ejecutando la función anterior en paralelo.

2. preprocess_covertype.py
Este archivo define un segundo DAG encargado del preprocesamiento de los datos descargados, consolidando y transformando los archivos CSV en un único dataset limpio y estructurado.
Componentes clave:
RAW_DATA_DIR: Directorio donde se almacenan los archivos crudos por grupo.
OUTPUT_FILE: Ruta del archivo CSV unificado y procesado.
preprocess_covertype():
Define 13 columnas esperadas.
Recorre los subdirectorios group_1 a group_10, leyendo los CSV sin encabezado. Asigna nombres correctos de columnas. Concatena todos los DataFrames. Crea el directorio de salida si no existe. Guarda el archivo final covertype_preprocessed.csv.

3. train_logreg_model.py
Este archivo define un DAG de Airflow para el entrenameinto de un modelo de regresión logística con validación de hiperparámetros y seguimiento de experimentos mediante MLflow.
Su objetivo es entrenar múltiples modelos de regresión logística con distintas configuraciones de hiperparámetros, evaluar su desempeño, registrar los resultados con MLflow y guardar el modelo con mejor accuracy para su posterior uso en inferencia o despliegue.
Componentes clave:
DATA_PATH: Ruta del dataset preprocesado usado para entrenar.
MODEL_PATH: Ruta donde se guarda el mejor modelo (.pkl).
train_logreg_model():
Lee el CSV preprocesado. Separa variables predictoras (X) y objetivo (y). Codifica variables categóricas usando one-hot encoding. Divide el dataset en entrenamiento y prueba (80/20). Configura MLflow y define el experimento. Realiza 10 entrenamientos variando el hiperparámetro C. Registra métricas y parámetros en MLflow. Guarda localmente el mejor modelo en disco usando pickle.

4. train_logreg_model2.py
Este archivo define un DAG de un modelo de regresión logística, usando un conjunto predefinido de hiperparámetros y registro detallado con MLflow.

DATA_PATH: Ruta al dataset preprocesado.
MODEL_PATH: Ruta donde se guarda el mejor modelo (.pkl).
train_logreg_model():
Carga el dataset y muestra la cantidad de filas. Separa X e y, y aplica codificación one-hot. Divide en conjuntos de entrenamiento y prueba (80/20). Define una grilla fija de hiperparámetros C y solver.
Para cada combinación:
Entrena el modelo. Evalúa con accuracy_score. Registra en MLflow: parámetros, métrica y modelo. Compara el desempeño y guarda el mejor.Persistencia del modelo óptimo con pickle.

5. train_rf_model.py
Este archivo define un DAG de Airflow enfocado en el entrenamiento de modelos Random Forest, con diferentes combinaciones de hiperparámetros definidos manualmente, evaluando su rendimiento con accuracy y registrando cada experimento con MLflow.

Componentes clave:
DATA_PATH: Ruta al archivo de datos preprocesados.
MODEL_PATH: Ruta del archivo .pkl donde se almacena el mejor modelo.
train_rf_model():
Carga y codifica los datos. Divide en conjuntos de entrenamiento y prueba. Define una grilla manual de hiperparámetros (n_estimators y max_depth). Entrena un modelo por configuración y evalúa con accuracy_score. Registra cada corrida en MLflow, incluyendo:
* Parámetros (log_param)
* Métricas (log_metric)
* Modelo serializado (log_model)
* Guarda el mejor modelo localmente usando pickle.

Screenshot from 2025-03-29 15-23-28
 
