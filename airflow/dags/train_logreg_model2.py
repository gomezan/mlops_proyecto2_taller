from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import mlflow
import mlflow.sklearn
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

DATA_PATH = "/opt/airflow/datasets/processed/covertype_preprocessed.csv"
MODEL_PATH = "/opt/airflow/models/mejor_logreg_model2.pkl"

def train_logreg_model():
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"Filas cargadas del CSV: {len(df)}")

        X = pd.get_dummies(df.drop(columns=["Cover_Type"]), drop_first=True)
        y = df["Cover_Type"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        mlflow.set_tracking_uri("http://mlflow:5000")
        mlflow.set_experiment("covertype_logreg_search")

        best_acc = 0
        best_model = None

        param_grid = [
            {"C": 0.01, "solver": "lbfgs"},
            {"C": 0.1,  "solver": "lbfgs"},
            {"C": 1.0,  "solver": "lbfgs"},
      
        ]

        for i, params in enumerate(param_grid):
            clf = LogisticRegression(
                C=params["C"],
                penalty="l2",
                solver=params["solver"],
                max_iter=200,
                multi_class='multinomial'
            )
            clf.fit(X_train, y_train)
            acc = accuracy_score(y_test, clf.predict(X_test))

            with mlflow.start_run(run_name=f"logreg_run_{i}"):
                mlflow.log_param("C", params["C"])
                mlflow.log_param("penalty", "l2")
                mlflow.log_param("solver", params["solver"])
                mlflow.log_metric("accuracy", acc)
                mlflow.sklearn.log_model(clf, "modelo_logreg")

            if acc > best_acc:
                best_acc = acc
                best_model = clf

        with open(MODEL_PATH, "wb") as f:
            pickle.dump(best_model, f)

        print(f"Mejor modelo LogisticRegression guardado con accuracy: {best_acc}")

    except Exception as e:
        print(f"Error durante el entrenamiento: {e}")
        raise

with DAG(
    dag_id="train_logreg_model2",
    start_date=datetime(2025, 3, 25),
    schedule_interval="@weekly",
    catchup=False,
    description="Entrena modelos LogisticRegression con parámetros definidos"
) as dag:
    
    task = PythonOperator(
        task_id="train_logreg_task2",
        python_callable=train_logreg_model,
        execution_timeout=timedelta(minutes=30)
    )

task

            
