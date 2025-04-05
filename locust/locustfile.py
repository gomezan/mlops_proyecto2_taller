from locust import HttpUser, task, between
import random

class InferenceUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def predict(self):
        payload = {
            "features": [
                3000.0, 45.0, 10.0,
                100.0, 20.0, 200.0,
                220.0, 230.0, 180.0, 150.0,
                random.randint(0, 3),
                random.randint(0, 39)
            ]
        }
        self.client.post("/predict", json=payload)



