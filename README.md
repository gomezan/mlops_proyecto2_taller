
MLOps: Taller Locust

Integrantes: 

•	Maria del Mar Montenegro Mafla

•	Andrés Gómez

•	Juan Felipe Forero 

1. Creación de API de inferencia con FastAPI

Se desarrolló una API RESTful utilizando FastAPI con el objetivo de exponer el modelo de predicción de cobertura forestal previamente entrenado y registrado en MLflow bajo el nombre BestModelRF, en estado Production. El modelo se cargadesde MLflow Registry a traves de .py (estado: Production), realiza inferencia en el endpoint /predict, preprocesa datos para compatibilidad con el modelo

Caracteristicas principales:
* La API se conecta a MLflow a través de la URI:
  MODEL_URI = "models:/BestModelRF/Production"
  model = mlflow.pyfunc.load_model(MODEL_URI)

* El modelo se carga dinámicamente desde el MLflow Registry usando el cliente mlflow.pyfunc
* El modelo es un RandomForestClassifier entrenado mediante Airflow y registrado en MLflow con sus hiperparámetros y artefactos asociados
* La configuración se conecta a MinIO como almacenamiento de artefactos, usando las siguientes variables de entorno:
  MLFLOW_TRACKING_URI
  MLFLOW_S3_ENDPOINT_URL
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY

* El modelo requiere una matriz de entrada que incluya 54 columnas, las cuales consisten en:
  10 columnas numéricas base (e.g. Elevation, Aspect, Slope, etc.)
  4 columnas generadas por codificación one-hot de Wilderness_Area
  40 columnas generadas por codificación one-hot de Soil_Type
La API implementa esta lógica manualmente, asegurando la consistencia con las columnas esperadas del modelo. JSON de entrada esperado ejemplo:

{
  "features": [
    3000.0, 45.0, 10.0,
    100.0, 20.0, 200.0,
    220.0, 230.0, 180.0, 150.0,
    0, 0
  ]
}

![api](https://github.com/user-attachments/assets/39a21de4-ae01-4e45-a10c-70a791e51a67)


2. Publicación de la imagen en DockerHub

La imagen fue subida a DockerHub desde la terminal, Etiqueta: montenegromm/inference-api:latest

![subir imagen a dockerhub](https://github.com/user-attachments/assets/9433c565-af58-47cb-a672-db819de186f6)

![imagen dockerhub](https://github.com/user-attachments/assets/7282daab-8035-414e-8ad0-d0ce0778cbfc)


3. Despliegue con docker-compose
El objetivo de este punto fue desplegar el servicio de inferencia desarrollado en FastAPI dentro de un contenedor Docker, utilizando Docker Compose para simplificar la orquestación y asegurar la correcta conexión con los servicios de MLflow y MinIO.

Se creó un archivo docker-compose-inference.yaml con los sigueintes componentes clave:

* image: utiliza la imagen publicada previamente en DockerHub
* ports: expone el puerto 8000 al host para acceder a la API
* environment: configura variables necesarias para que el contenedor se conecte a MLflow y MinIO desde el host local
  
Las variables de entorno permiten que el servicio dentro del contenedor acceda a MLflow Tracking Server en el host local (http://host.docker.internal:5000) y MinIO como backend de almacenamiento de modelos (http://host.docker.internal:9000)

![api con imagen docker hub](https://github.com/user-attachments/assets/78b06014-2cad-4c0d-984d-fbcfe6c28e1d)

4. Pruebas de carga con Locust

Se construyó los siguientes documentos:

* locustfile.py: cliente Locust para POST /predict:
Este archivo define la clase que simula los usuarios virtuales. La tarea predict() realiza peticiones POST al endpoint /predict de la API y utiliza datos de prueba compatibles con el modelo BestModelRF.

* docker-compose-locust.yaml: levanta inference-api + Locust
 Este archivo permite levantar dos servicios: inference-api y locust
 - inference-api: Usa la imagen publicada montenegromm/inference-api:latest, esta configurado con variables de entorno para conectarse a MLflow y MinIO y expone el puerto 8000 para recibir peticiones.
 - locust: Expone la interfaz gráfica de Locust en http://localhost:8089 y se conecta internamente al contenedor inference-api en la misma red

* Se realizaron pruebas con distintos niveles de concurrencia y ramp-up recopilando : № de usuarios activos, Porcentaje de fallos,Tiempo medio de respuesta.

![locust con inferencia a la api](https://github.com/user-attachments/assets/d0fef7ac-c342-4055-b72f-877000dc0a0a)

5. Ajuste de recursos para soportar 10,000 usuarios

Tras experimentar con múltiples configuraciones:

2.8 CPUs Y 5.5 GB RAM permitieron responder a 10,000 usuarios concurrentes sin errores.Se confirmó que recursos menores generaban latencia alta y fallos.

Resultados de las experimentaciones:

 Usuarios simulados	| Falla en /predict |	Tiempo medio (ms) |	Máximo (ms)	| Memoria límite	| CPU límite |	Observaciones
       1	           |       si	         |         4	        |      7877	  |       256M	    |     0,25	  | Falla en todas las predicciones
       1	           |       no	         |       27,13	      |        42	  |        6G	     |       3	   | Sin falla
     10000	         |       si	         |        846	       |     11,028	 |        5G	     |      2,5	  | Falla en 34% de predicciones
     10000	         |       no	         |       16700	      |      31524	 |        6G	     |       3	   | Sin falla
     10000	         |       no	         |       11834	      |      23659	 |       5,5G	    |      2,5	  | Sin falla

| Usuarios simulados | Falla en /predict | Tiempo medio (ms) | Máximo (ms) | Memoria límite | CPU límite | Observaciones                        |
|--------------------|-------------------|--------------------|-------------|----------------|------------|--------------------------------------|
| 1                  | sí                | 4                  | 7877        | 256M           | 0,25       | Falla en todas las predicciones      |
| 1                  | no                | 27,13              | 42          | 6G             | 3          | Sin falla                             |
| 10000              | sí                | 846                | 11028       | 5G             | 2,5        | Falla en 34% de predicciones         |
| 10000              | no                | 16700              | 31524       | 6G             | 3          | Sin falla                             |
| 10000              | no                | 11834              | 23659       | 5,5G           | 2,5        | Sin falla                             |


Prueba 1:
![1 usuario](https://github.com/user-attachments/assets/3fbfa13d-c550-4b2e-89e0-7691c8084717)

Prueba 2:
![1 usuario sin falla](https://github.com/user-attachments/assets/2e37c704-07b3-44b5-b133-7c64f926179f)

Prueba 3:
![10000 fallo 2 y 5](https://github.com/user-attachments/assets/313caaee-c064-4287-844e-cd4f17990636)

Prueba 4:
![10000 sin fallos](https://github.com/user-attachments/assets/c1896c1d-221c-4b2c-9daa-d65534777d62)

Prueba 5 (Recuersos minimos): 
![10000 sin fallos 2 8 y 5 5](https://github.com/user-attachments/assets/6dd6b66a-11a6-417f-b4d6-8f8c5cb055a4)

6. Escalamiento horizontal con réplicas

Se intentó usar docker-compose con deploy.replicas: 3. Se evidencia que el sistema no logró sostener la carga sin errores, a pesar de tener 3 contenedores con 1.5 CPUs y 2.5 GB de RAM cada uno. es decir el escalado con 3 instancias no es suficiente. Sin balanceador de carga, las peticiones no se distribuyen correctamente.  Para cumplir el objetivo del punto 6 correctamente, se debe escalar con instancias de 2.8/5.5 (igual que el mínimo viable individual).

![Captura de pantalla 2025-04-05 164620](https://github.com/user-attachments/assets/1b533a29-2525-418e-8cbe-0cd8367b6908)

