from locust import HttpUser, task, between
import random
from faker import Faker
    

class MyUser(HttpUser):
    host = "https://wildscribe-rails-be-faa8001cbf6c.herokuapp.com"
    wait_time = between(1, 5)  # Time between consecutive requests


    def on_start(self):
        self.faker = Faker()


    @task       
    def CreateAdventure(self):
        self.user_id = random.randint(1, 2000)
        endpoint = "/api/v0/adventure"

        payload = {
                    "data": {
                        "type": "adventure",
                        "attributes": {
                            "user_id": self.user_id,
                            "activity": self.faker.word(),
                            "date": self.faker.date(),
                            "image_url": self.faker.image_url(),
                            "stress_level": self.faker.random_element(elements=("Low", "Medium", "High", "Very High")),
                            "hours_slept": self.faker.random_int(min=4, max=12),
                            "sleep_stress_notes": self.faker.sentence(),
                            "hydration": self.faker.random_element(elements=("Hydrated", "Not Hydrated")),
                            "diet": self.faker.random_element(elements=("Good Diet", "Poor Diet")),
                            "diet_hydration_notes": self.faker.sentence(),
                            "beta_notes": self.faker.paragraph(),
                        }
                    }
                }

        headers = {
            "Content-Type": "application/json"
        }

        with self.client.post(endpoint, json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.elapsed.total_seconds() > 1.0:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()} seconds")
            else:
                response.success()