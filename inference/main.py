from fastapi import FastAPI
import mlflow.pyfunc
import numpy as np
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

# Cargar el modelo desde MLflow
MODEL_URI = "models:/covertype_model/production"
model = mlflow.pyfunc.load_model(MODEL_URI)

class InputData(BaseModel):
    features: list

@app.post("/predict")
def predict(data: InputData):
    try:
        input_array = np.array(data.features).reshape(1, -1)
        prediction = model.predict(pd.DataFrame(input_array))
        return {"prediction": prediction.tolist()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def home():
    return {"message": "API de inferencia en ejecución"}
