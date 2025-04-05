
MLOps: Taller Locust

Integrantes: 
•	Maria del Mar Montenegro Mafla
•	Andrés Gómez
•	Juan Felipe Bocanegra

1. Creación de API de inferencia con FastAPI

Se implementó un servicio FastAPI en inference/main.py que:

* Carga el modelo desde MLflow Registry a traves de .py (estado: Production)
* Realiza inferencia en el endpoint /predict
* Preprocesa datos para compatibilidad con el modelo
* Fue empaquetado en una imagen Docker funcional

!!!!!!!!! IMAGEN DE MLFLOW Y API!!!!!!!!!!!!!!

2. Publicación de la imagen en DockerHub

La imagen fue subida a DockerHub desde la terminal, Etiqueta: montenegromm/inference-api:latest

!!!!!!!!!!!  IMAGEN DE DOCKER HUB!!!!!

3. Despliegue con docker-compose

Se creó un archivo docker-compose-inference.yaml que incluye:

* Contenedor de FastAPI (inference-api)
* Variables necesarias para conectarse a MLflow y MinIO
* Se verificó acceso correcto al modelo registrado y predicciones válidas en Swagger.

!!!!!!!!IMAGEN DE PRUEBA DE INFERENCE API!!!!!!

4. Pruebas de carga con Locust

Se construyó los siguientes documentos:

* locustfile.py: cliente Locust para POST /predict
* docker-compose-locust.yaml: levanta inference-api + Locust
* Se realizaron pruebas con distintos niveles de concurrencia y ramp-up recopilando : № de usuarios activos, Porcentaje de fallos,Tiempo medio de respuesta.

!!!! IMAGEN DE LOCUST 1!!!!!

5. Ajuste de recursos para soportar 10,000 usuarios

Tras experimentar con múltiples configuraciones:

2.8 CPUs Y 5.5 GB RAM permitieron responder a 10,000 usuarios concurrentes sin errores.Se confirmó que recursos menores generaban latencia alta y fallos.

Resultados de las experimentaciones:

 Usuarios simulados	Falla en /predict	Tiempo medio (ms)	Máximo (ms)	Memoria límite	CPU límite	Observaciones
1	si	4	7877	256M	0,25	Falla en todas las predicciones
1	no	27,13	42	6G	3	Sin falla
10000	si	846	11,028	5G	2,5	Falla en 34% de predicciones
10000	no	16700	31524	6G	3	Sin falla
10000	no	11834	23659	5,5G	2,5	Sin falla

!!!!!!!! IMAGENES DE CADA ITERACIONE!!!!!

6. Escalamiento horizontal con réplicas

Se intentó usar docker-compose con deploy.replicas: 3. Se evidencia que el sistema no logró sostener la carga sin errores, a pesar de tener 3 contenedores con 1.5 CPUs y 2.5 GB de RAM cada uno. es decir el escalado con 3 instancias no es suficiente. Sin balanceador de carga, las peticiones no se distribuyen correctamente.  Para cumplir el objetivo del punto 6 correctamente, se debe escalar con instancias de 2.8/5.5 (igual que el mínimo viable individual).

!!!!!!! IMAGEN DE LOCUST CON ESCALAMIENTO!!!!!!
