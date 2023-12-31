from locust import HttpUser, task, between
import random
import csv
from faker import Faker
    

class MyUser(HttpUser):
    host = "https://safe-refuge-07153-b08bc7602499.herokuapp.com"
    wait_time = between(1, 5)  # Time between consecutive requests


    def on_start(self):
        self.user_id = None 
        self.users = self.read_users_csv("mock_collections/all_users.csv")
        self.faker = Faker()

    def read_users_csv(self, csv_file):
        users = []
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                users.append(row)  # Assuming user IDs are in the first column
        return users



    @task       
    def GetUserAdventures(self):
                # Define the URL you want to test
        user = random.choice(self.users)  # Select a random user
        self.user_id = user[0]
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
                response.success()
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got wrong response: {response.status_code}")