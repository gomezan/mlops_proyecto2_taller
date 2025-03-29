from fastapi import FastAPI
import mlflow.pyfunc
import numpy as np
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

# Cargar el modelo desde MLflow
MODEL_URI = "models:/BestModelRF/Production"
model = mlflow.pyfunc.load_model(MODEL_URI)

# Columnas que espera el modelo
expected_cols = [
    'Elevation', 'Aspect', 'Slope', 'Horizontal_Distance_To_Hydrology',
    'Vertical_Distance_To_Hydrology', 'Horizontal_Distance_To_Roadways',
    'Hillshade_9am', 'Hillshade_Noon', 'Hillshade_3pm',
    'Horizontal_Distance_To_Fire_Points',
    'Wilderness_Area_Cache', 'Wilderness_Area_Commanche', 'Wilderness_Area_Neota', 'Wilderness_Area_Rawah',
    'Soil_Type_C2702', 'Soil_Type_C2703', 'Soil_Type_C2704', 'Soil_Type_C2705', 'Soil_Type_C2706',
    'Soil_Type_C2717', 'Soil_Type_C3501', 'Soil_Type_C3502', 'Soil_Type_C4201', 'Soil_Type_C4703',
    'Soil_Type_C4704', 'Soil_Type_C4744', 'Soil_Type_C4758', 'Soil_Type_C5101', 'Soil_Type_C5151',
    'Soil_Type_C6101', 'Soil_Type_C6102', 'Soil_Type_C6731', 'Soil_Type_C7101', 'Soil_Type_C7102',
    'Soil_Type_C7103', 'Soil_Type_C7201', 'Soil_Type_C7202', 'Soil_Type_C7700', 'Soil_Type_C7701',
    'Soil_Type_C7702', 'Soil_Type_C7709', 'Soil_Type_C7710', 'Soil_Type_C7745', 'Soil_Type_C7746',
    'Soil_Type_C7755', 'Soil_Type_C7756', 'Soil_Type_C7757', 'Soil_Type_C7790', 'Soil_Type_C8703',
    'Soil_Type_C8707', 'Soil_Type_C8708', 'Soil_Type_C8771', 'Soil_Type_C8772', 'Soil_Type_C8776'
]

# Mapas de codificación
wilderness_map = {
    0: "Wilderness_Area_Cache",
    1: "Wilderness_Area_Commanche",
    2: "Wilderness_Area_Neota",
    3: "Wilderness_Area_Rawah"
}

soil_type_map = {
    i: f"Soil_Type_C{code}" for i, code in enumerate([
        2702, 2703, 2704, 2705, 2706, 2717, 3501, 3502, 4201, 4703,
        4704, 4744, 4758, 5101, 5151, 6101, 6102, 6731, 7101, 7102,
        7103, 7201, 7202, 7700, 7701, 7702, 7709, 7710, 7745, 7746,
        7755, 7756, 7757, 7790, 8703, 8707, 8708, 8771, 8772, 8776
    ])
}

class InputData(BaseModel):
    features: list

@app.post("/predict")
def predict(data: InputData):
    try:
        input_array = np.array(data.features).reshape(1, -1)
        base_features = [
            "Elevation", "Aspect", "Slope", "Horizontal_Distance_To_Hydrology",
            "Vertical_Distance_To_Hydrology", "Horizontal_Distance_To_Roadways",
            "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm",
            "Horizontal_Distance_To_Fire_Points", "Wilderness_Area", "Soil_Type"
        ]
        df = pd.DataFrame(input_array, columns=base_features)

        # Inicializar todas las columnas con cero
        input_final = pd.DataFrame(columns=expected_cols)
        input_final.loc[0] = 0

        # Asignar valores continuos
        for col in base_features[:10]:
            input_final.at[0, col] = df.at[0, col]

        # One-hot manual
        wilderness_col = wilderness_map.get(int(df.at[0, "Wilderness_Area"]))
        if wilderness_col in input_final.columns:
            input_final.at[0, wilderness_col] = 1

        soil_col = soil_type_map.get(int(df.at[0, "Soil_Type"]))
        if soil_col in input_final.columns:
            input_final.at[0, soil_col] = 1

        # Predicción
        prediction = model.predict(input_final)
        return {"prediction": prediction.tolist()}

    except Exception as e:
        return {"error": f"Error del modelo: {str(e)}"}

@app.get("/")
def home():
    return {"message": "API de inferencia en ejecución"}



