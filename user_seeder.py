import json
import csv
import os
from locust import HttpUser, task, between, SequentialTaskSet
from faker import Faker


class UserSeederTaskSet(SequentialTaskSet):
    max_request = 1000

    def on_start(self):
        self.faker = Faker()


    def create_output_csv_if_not_exists(self):
        users_output_csv = "mock_collections/all_users.csv"
        if not os.path.exists(users_output_csv):
            with open(users_output_csv, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["user_id", "name", "email", "password"])

    @task
    def create_user(self):
        # Generate a random email with a non-repeating number between 1 and 100
        email = self.faker.email()
        name = self.faker.name()
        password = self.faker.word()
        
        # Define the JSON payload for creating a user
        payload = {
            "data": {
                "type": "user",
                "attributes": {
                    "name": name,
                    "email": email,
                    "password": password
                }
            }
        }

        # Set the request headers
        headers = {
            "Content-Type": "application/json"
        }

        # Send a POST request to create a new user
        response = self.client.post("/user", json=payload, headers=headers)

        if response.status_code == 201:
            # If the response is successful, extract the user ID from the response JSON
            response_data = json.loads(response.content)
            user_id = response_data["data"]["attributes"]["user_id"]
            
            # Save the user ID to a CSV file
            self.save_user_id_to_csv(user_id, name, email, password)
        
    def save_user_id_to_csv(self, user_id, name, email, password):
        with open("mock_collections/all_users.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([user_id, name, email, password])

class UserSeeder(HttpUser):
    host = "https://safe-refuge-07153-b08bc7602499.herokuapp.com"  # Replace with your API endpoint
    tasks = [UserSeederTaskSet]
    wait_time = between(1, 2)  # Time between consecutive requests