import mlflow
import mlflow.sklearn
import os
import joblib

MODEL_NAME = "BestModelRF"

# Ruta al modelo en tu máquina local
model_path = "airflow/models/mejor_rf_model.pkl"

# Cargar el modelo con joblib (opcional si quieres validar)
model = joblib.load(model_path)

# Iniciar sesión de MLflow
mlflow.set_tracking_uri("http://localhost:5000")

with mlflow.start_run(run_name="registro_manual"):
    # Registrar el modelo como artefacto
    mlflow.sklearn.log_model(sk_model=model, artifact_path="model", registered_model_name=MODEL_NAME)
    mlflow.log_param("source", "registro_manual")
    mlflow.log_param("script", "register_model.py")







