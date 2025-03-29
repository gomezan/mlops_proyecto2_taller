# ui/app.py
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Predicción de Cobertura", layout="centered")

st.markdown(
    """
    <h2 style='text-align: center; color: #826A5C;'>Predicción del tipo de cobertura forestal</h2>
    <p style='text-align: center; color: #A49E8D;'>Completa los datos y obtén la predicción del modelo.</p>
    """,
    unsafe_allow_html=True
)

# Campos de entrada
fields = {
    "Elevation": st.number_input("Elevación (m)", 0, 5000, 2500),
    "Aspect": st.slider("Orientación (0-360)", 0, 360, 180),
    "Slope": st.slider("Pendiente (°)", 0, 90, 10),
    "Horizontal_Distance_To_Hydrology": st.number_input("Distancia horizontal al agua (m)", 0, 10000, 50),
    "Vertical_Distance_To_Hydrology": st.number_input("Distancia vertical al agua (m)", -500, 500, 0),
    "Horizontal_Distance_To_Roadways": st.number_input("Distancia a caminos (m)", 0, 10000, 500),
    "Hillshade_9am": st.slider("Sombra 9am", 0, 255, 200),
    "Hillshade_Noon": st.slider("Sombra mediodía", 0, 255, 220),
    "Hillshade_3pm": st.slider("Sombra 3pm", 0, 255, 180),
    "Horizontal_Distance_To_Fire_Points": st.number_input("Distancia a puntos de fuego (m)", 0, 10000, 1000),
    "Wilderness_Area": st.selectbox("Área silvestre", [0, 1, 2, 3]),
    "Soil_Type": st.selectbox("Tipo de suelo", list(range(40)))
}

if st.button("Predecir"):
    # Convertir a JSON
    input_data = {"features": list(fields.values())}

    try:
        response = requests.post("http://inference:8000/predict", json=input_data)
        result = response.json()

        if "prediction" in result:
            st.success(f"Tipo de cobertura predicho: {result['prediction'][0]}")
        elif "error" in result:
            st.error(f"Error del modelo: {result['error']}")
        else:
            st.error("Respuesta inesperada del backend.")
    except Exception as e:
        st.error(f"Error procesando la respuesta: {str(e)}")






