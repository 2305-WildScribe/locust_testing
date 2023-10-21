    
import json
import csv
from locust import HttpUser, task, between, SequentialTaskSet
from faker import Faker
import os

class AdventureSeederTaskSet(SequentialTaskSet):
    def on_start(self):
        self.seed_amount = 5
        # Creates output_csvs if they don't exist
        self.create_output_csv_if_not_exists()
        # Loads all user IDs present.
        self.users = self.read_users_csv("mock_collections/all_users.csv")
        self.faker = Faker()
      
        # Change this to change how many adventures are created per user ID


    def create_output_csv_if_not_exists(self):
        adventures_output_csv = "mock_collections/all_adventures.csv"
        users_output_csv = f"mock_collections/users_with_{self.seed_amount}_adventures.csv"
        if not os.path.exists(users_output_csv):
            with open(users_output_csv, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["user_id", "name", "email", "password"])
        if not os.path.exists(adventures_output_csv):
            with open(adventures_output_csv, mode="w", newline="") as file:
                fieldnames = [
                    "user_id",
                    "adventure_id",
                    "activity",
                    "date",
                    "image_url",
                    "stress_level",
                    "hours_slept",
                    "sleep_stress_notes",
                    "hydration",
                    "diet",
                    "diet_hydration_notes",
                    "beta_notes"
                ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    def remove_user_from_csv(self, user_id):
        # Remove the user with the specified user_id
        self.users = [user for user in self.users if user[0] != user_id]
        # Write the updated list of users back to the CSV
        with open("mock_collections/all_users.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["user_id", "name", "email", "password"])
            for user in self.users:
                writer.writerow([user[0], user[1], user[2], user[3]])

    def read_users_csv(self, csv_file):
        users = []
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                users.append(row)  # Assuming user IDs are in the first column
        return users
    
    @task   
    def create_adventures(self):
        # Create 10 adventures for each user ID and remove the user ID from the list
        if self.users:
            user = self.users.pop(0)
            self.user_id = user[0]
            self.name = user[1]
            self.email = user[2]
            self.password = user[3]
            self.remove_user_from_csv(self.user_id)
            self.save_user_id_to_csv(self.user_id, self.name, self.email, self.password)

            adventures = []

            for _ in range(self.seed_amount):
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
                print(payload)
                response = self.client.post("/api/v0/adventure", json=payload, headers=headers)

                if response.status_code == 201:
                    # If the response is successful, extract the user ID from the response JSON
                    response_data = json.loads(response.content)
                    adventure_id = response_data["data"]["attributes"]["adventure_id"]
                    adventure_data = {
                        "user_id": self.user_id,
                        "adventure_id": adventure_id,
                        "activity": payload["data"]["attributes"]["activity"],
                        "date": payload["data"]["attributes"]["date"],
                        "image_url": payload["data"]["attributes"]["image_url"],
                        "stress_level": payload["data"]["attributes"]["stress_level"],
                        "hours_slept": payload["data"]["attributes"]["hours_slept"],
                        "sleep_stress_notes": payload["data"]["attributes"]["sleep_stress_notes"],
                        "hydration": payload["data"]["attributes"]["hydration"],
                        "diet": payload["data"]["attributes"]["diet"],
                        "diet_hydration_notes": payload["data"]["attributes"]["diet_hydration_notes"],
                        "beta_notes": payload["data"]["attributes"]["beta_notes"],
                    }
                    adventures.append(adventure_data)

            # Save the user ID to a CSV file
            # Remove the user from the CSV
            self.save_adventures_to_csv(adventures)
            # Save the adventure attributes to a CSV file

    def save_adventures_to_csv(self, adventures):
        with open("mock_collections/all_adventures.csv", mode="a", newline="") as file:
            fieldnames = ["user_id", "adventure_id", "activity", "date", "image_url", "stress_level", "hours_slept",
                          "sleep_stress_notes", "hydration", "diet", "diet_hydration_notes", "beta_notes"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            for adventure in adventures:
                writer.writerow(adventure)

    def save_user_id_to_csv(self, user_id, name, email, password):
        with open(f"mock_collections/users_with_{self.seed_amount}_adventures.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([user_id, name, email, password])

class AdventureSeeder(HttpUser):
    host = "https://safe-refuge-07153-b08bc7602499.herokuapp.com"  # Replace with your API endpoint
    tasks = [AdventureSeederTaskSet]
    wait_time = between(1, 2)  # Time between consecutive requests