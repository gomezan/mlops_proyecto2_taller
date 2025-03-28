from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import pandas as pd
import mlflow
import mlflow.sklearn
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

DATA_PATH = "/opt/airflow/datasets/processed/covertype_preprocessed.csv"
MODEL_PATH = "/opt/airflow/models/mejor_rf_model.pkl"

def train_rf_model():
    df = pd.read_csv(DATA_PATH)
    X = pd.get_dummies(df.drop(columns=["Cover_Type"]), drop_first=True)
    y = df["Cover_Type"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("covertype_rf_search")

    best_acc = 0
    best_model = None

    # Hiperparámetros definidos manualmente
    param_grid = [
        {"n_estimators": 50, "max_depth": 5},
        {"n_estimators": 50, "max_depth": 10},
        {"n_estimators": 100, "max_depth": 10},
        {"n_estimators": 100, "max_depth": 20},
        {"n_estimators": 150, "max_depth": 20},
    ]

    for i, params in enumerate(param_grid):
        clf = RandomForestClassifier(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            random_state=42
        )
        clf.fit(X_train, y_train)
        acc = accuracy_score(y_test, clf.predict(X_test))

        with mlflow.start_run(run_name=f"rf_run_{i}"):
            mlflow.log_param("n_estimators", params["n_estimators"])
            mlflow.log_param("max_depth", params["max_depth"])
            mlflow.log_metric("accuracy", acc)
            mlflow.sklearn.log_model(clf, "modelo_rf")

        if acc > best_acc:
            best_acc = acc
            best_model = clf

    # Guardar mejor modelo localmente
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)
    print(f"Mejor modelo RandomForest guardado con accuracy: {best_acc}")

with DAG(
    dag_id="train_rf_model",
    start_date=datetime(2025, 3, 25),
    schedule_interval="@weekly",
    catchup=False,
    description="Entrena modelos RandomForest con hiperparámetros definidos"
) as dag:
    
    task = PythonOperator(
        task_id="train_rf_task",
        python_callable=train_rf_model
    )

task



