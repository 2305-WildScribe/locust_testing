from locust import HttpUser, task, between
import random
from faker import Faker
    

class MyUser(HttpUser):
    host = "https://wildscribe-rails-test-3a5fcd1ed43b.herokuapp.com/"
    wait_time = between(1, 5)  # Time between consecutive requests


    def on_start(self):
        self.faker = Faker()


    @task       
    def GetUserAdventures(self):

        self.user_id = random.randint(1, 2000)
        endpoint = "/api/v0/user/adventures"
        # Define the JSON body
        payload = { 
        "data": {
            "type": "adventures",
            "attributes": {
                "user_id": f"{self.user_id}"
                }
            }
        }

        # Set the request headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Send a POST request to the /user endpoint with the JSON body
        
        with self.client.post(endpoint, json=payload, headers=headers, catch_response=True) as response:
            if response.elapsed.total_seconds() > 1.0:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()} seconds")
            elif response.status_code == 404:
                response.failure()
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got wrong response: {response.status_code}")