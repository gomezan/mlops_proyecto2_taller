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

![Screenshot from 2025-03-29 15-23-28](https://github.com/user-attachments/assets/cf0b0eef-c357-42b8-9931-12e3775bb9c1)

•	mlflow/: Contiene las configuraciones y datos relacionados con el seguimiento y gestión de experimentos mediante MLflow.

Experimentos:

1. covertype_logreg_search
Este experimento está orientado a la evaluación de distintos modelos de Regresión Logística aplicados al dataset Covertype. A través de múltiples ejecuciones automatizadas (runs), se variaron los hiperparámetros relevantes con el objetivo de minimizar el error cuadrático medio (MSE).

Se realizaron al menos 15 ejecuciones (logreg_run_0 a logreg_run_9, entre otros). Todas las ejecuciones almacenaron sus métricas (mse, accuracy, etc.) y modelos asociados utilizando el backend de MLflow.
No se promovió ningún modelo de este experimento a producción, lo que indica que no se alcanzó un rendimiento satisfactorio en comparación con otras alternativas.

2. covertype_rf_search
El segundo experimento corresponde a una búsqueda sistemática de hiperparámetros para modelos de tipo Random Forest. Cada ejecución representa una configuración específica del modelo, con métricas y artefactos almacenados para su análisis posterior.
Se ejecutaron múltiples pruebas con Random Forest (rf_run_0 a rf_run_6, incluyendo repeticiones). Uno de los modelos (rf_run_3) fue registrado formalmente como BestModelRF y se promovió exitosamente al estado de producción (Production).

Cada ejecución registrada en MLflow proviene de la fuente airflow, lo que indica que la generación, entrenamiento y evaluación de modelos fue orquestada mediante DAGs definidos previamente en Apache Airflow. 

Gestión del modelo en producción
El modelo BestModelRF fue gestionado a través del sistema de Model Registry de MLflow:
Fue registrado a partir de una de las ejecuciones exitosas del DAG correspondiente al experimento covertype_rf_search. Fue etiquetado como versión v3 y promovido al entorno de producción, permitiendo su consumo mediante la API desarrollada con FastAPI.

![Screenshot from 2025-03-29 15-39-22](https://github.com/user-attachments/assets/dec2b179-ab45-4216-986f-4f3f982be512)

![Screenshot from 2025-03-29 15-39-34](https://github.com/user-attachments/assets/ffaeb26d-8824-4f0e-a781-fc00df6a94ef)


•	inference/: Incluye el código y los recursos necesarios para el servicio de inferencia del modelo.

main.py (API de inferencia con FastAPI)
Este archivo implementa una API RESTful usando FastAPI para exponer el modelo de predicción de cobertura forestal entrenado con MLflow, permitiendo realizar inferencias desde aplicaciones externas como la interfaz gráfica.

Componentes clave:
Carga del modelo: Se conecta al modelo registrado como BestModelRF en estado Production dentro del registro de modelos de MLflow.
Estructura esperada: El modelo requiere 54 columnas, la mayoría generadas por codificación one-hot para los campos Wilderness_Area y Soil_Type.
Se define un conjunto de columnas expected_cols para asegurar consistencia del input.
Ruta /predict (POST): Recibe un JSON con una lista de 13 características base. Convierte el input en un DataFrame con columnas codificadas manualmente. Realiza la predicción y devuelve el resultado como JSON.
Ruta / (GET):Endpoint de prueba para verificar que la API está en ejecución.
Codificación manual (one-hot): Para compatibilidad con el modelo, se implementa codificación manual de:
Wilderness_Area → columnas como Wilderness_Area_Cache, etc.
Soil_Type → columnas como Soil_Type_C2702, etc.
Rol en el pipeline MLOps:
Esta API representa la fase de despliegue e inferencia en el ciclo MLOps, haciendo posible que aplicaciones front-end (como la interfaz Streamlit) puedan consumir el modelo sin necesidad de lógica de machine learning adicional.

![Screenshot from 2025-03-29 15-56-39](https://github.com/user-attachments/assets/e7ff34d6-cea0-4c30-b52e-4a5b13580893)


•	ui/: Contiene el codigo de la interfaz de usuario desarrollada con Streamlit para interactuar con el modelo y visualizar resultados.

app.py (Interfaz gráfica con Streamlit): 
Este archivo implementa una interfaz gráfica web construida con Streamlit para facilitar la interacción con el modelo de machine learning entrenado. Está diseñado como la capa de presentación del pipeline MLOps, permitiendo a cualquier usuario hacer predicciones de forma sencilla.

Componentes clave:
Título y descripción visual: HTML embebido con estilo personalizado para mejorar la presentación.
Campos de entrada:
Incluye 13 características numéricas y categóricas (ej. Elevación, Pendiente, Tipo de suelo, Área silvestre). Se emplean number_input, slider y selectbox para recoger los datos de forma amigable.
Botón "Predecir": Al hacer clic, los datos del formulario se transforman en un JSON con estructura {"features": [...]}.
Se realiza una solicitud POST a un backend alojado en http://inference:8000/predict. Si el backend responde correctamente, se muestra el resultado de la predicción. Se manejan errores de forma clara para el usuario final.

![Screenshot from 2025-03-29 15-57-07](https://github.com/user-attachments/assets/b113c8c9-9ba8-466a-9755-69e3e8d78dfc)

![Screenshot from 2025-03-29 15-57-20](https://github.com/user-attachments/assets/9279ea30-6dd1-4192-a1c3-891df0720411)


•	postgres/: Contiene las configuraciones para la base de datos PostgreSQL utilizada en el proyecto.

•	minio/: MinIO actúa como un sistema de almacenamiento de objetos donde se guardan todos los artefactos del modelo registrados por MLflow.

![Screenshot from 2025-03-29 15-57-36](https://github.com/user-attachments/assets/7ba454eb-716f-4d66-9f89-a2b444d6214c)

•	mySQL/: Es la base de datos donde se almacenan todos los metadatos de los experimentos y ejecuciones

•	docker-compose.yaml: 
Este archivo define y orquesta todos los servicios necesarios para el funcionamiento del pipeline MLOps, desde la recolección de datos hasta la inferencia y visualización de resultados. Utiliza la herramienta Docker Compose para levantar entornos aislados y reproducibles.

Servicios definidos:
* postgres: Base de datos para Airflow.
Imagen: postgres:13
Volumen persistente
Red: mlops_network
airflow-webserver y airflow-scheduler
Ejecutan Airflow con LocalExecutor y almacenan los DAGs, logs y modelos.
Imagen personalizada custom-airflow
Se conectan a Postgres y MinIO
Puerto expuesto: 8080

* mlflow: Plataforma para seguimiento de experimentos y gestión de modelos.
Se conecta a una base de datos MySQL y MinIO como backend de artefactos.
Puerto expuesto: 5000

* mysql: Base de datos para MLflow.
Imagen: mysql:8.0
Volumen persistente
Puerto expuesto: 3306

* minio: Almacenamiento de objetos compatible con S3 usado por MLflow.
Imagen: minio/minio
Puerto de consola: 9001, API: 9000

* inference: Servicio FastAPI para inferencia del modelo.
Se conecta a MLflow y MinIO
Puerto expuesto: 8000

* ui: Interfaz de usuario en Streamlit para ingresar datos y visualizar predicciones.
Puerto expuesto: 8503
Red definida:
mlops_network: red bridge para comunicación entre contenedores.

•	.gitignore: Especifica los archivos y directorios que deben ser ignorados por Git.

Contraseñas:
* POSTGRES: usuario: airflow  - contraseña: airflow
* MYSQL: usuario: root  - contraseña: root
* AIRFLOW: usuario: admin  - contraseña: admin
* MINIO: usuario: minioadmin  - contraseña: minioadmin



