from locust import HttpUser, task, between
import random
import csv
from faker import Faker

class MyUser(HttpUser):

    host = "https://safe-refuge-07153-b08bc7602499.herokuapp.com"
    wait_time = between(1, 5)  

    def on_start(self):
            self.user_id = None 
            self.adventure_id = None
            self.users = self.read_users_csv("mock_collections/all_users.csv")
            self.faker = Faker()

    def read_users_csv(self, csv_file):
        users = []
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                users.append(row)  
        return users
    
    @task
    def login_user(self):        
        if self.users:
            user = random.choice(self.users)
            name = user[1] 
            email = user[2]
            password = user[3]
            self.user_id = user[0]

        endpoint = "/api/v0/user"

        payload = {
            "data":{
                "type": "user",
                "attributes": {
                    "email": f"{email}",
                    "password": f"{password}"
                }
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        with self.client.post(endpoint, json=payload, headers=headers, catch_response=True) as response:
            if response.elapsed.total_seconds() > 1.0:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()} seconds")
            elif response.status_code == 404:
                response.failure("Bad Request")
            elif response.status_code == 401:
                response.success()
            elif response.status_code == 200:
                print(f"User: {name}")
                response.success()
            else:
                response.failure(f"Got wrong response: {response.status_code}")



    @task
    def GetUserAdventures(self):
        if self.user_id is None:
            self.login_user

        endpoint = "/api/v0/user/adventures"

        payload = { 
        "data": {
            "type": "adventures",
            "attributes": {
                "user_id": f"{self.user_id}"
                }
            }
        }

        headers = {
            "Content-Type": "application/json"
        }
                
        with self.client.post(endpoint, json=payload, headers=headers, catch_response=True) as response:
            if response.elapsed.total_seconds() > 1.0:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()} seconds")
            elif response.status_code == 200:
                json_response = response.json()
                if json_response["data"]["attributes"] is not None:
                    adventures = json_response["data"]["attributes"]
                    random_adventure = random.choice(adventures)
                    self.adventure_id = random_adventure["adventure_id"]
                print(f"Got User Adventures")
                response.success()
            else:
                response.failure(f"Got wrong response: {response.status_code}")

    @task
    def CreateAdventure(self):
        if self.user_id is None:
            self.login_user()

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
            if response.status_code == 201:
                json_response = response.json()
                self.adventure_id = json_response["data"]["attributes"]["adventure_id"]
                print(f"Adventure Created: {self.adventure_id}")
                response.success()
                self.GetUserAdventures()
            elif response.elapsed.total_seconds() > 1.0:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()} seconds")
            else:
                response.failure(f"Got wrong response: {response.status_code}")

    @task
    def GetAnAdventure(self):
        if self.user_id is None:
            self.login_user()
        if self.adventure_id is None:
            self.CreateAdventure()
        
        endpoint = "/api/v0/user/adventure"
        print(f"Get An Adventure ID: {self.adventure_id}")

        payload = { 
        "data": {
            "type": "adventures",
            "attributes": {
                "adventure_id": f"{self.adventure_id}"
                }
            }
        }

        headers = {
            "Content-Type": "application/json"
        }
        
        with self.client.post(endpoint, json=payload, headers=headers, catch_response=True) as response:
            if response.elapsed.total_seconds() > 1.0:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()} seconds")
            elif response.status_code == 200:
                print("Got An Adventure")
                response.success()
            elif response.status_code == 400: 
                response.success()
            else:
                response.failure(f"Got wrong response: {response.status_code}")

    @task
    def UpdateAdventure(self):
        if self.user_id is None:
            self.login_user()
        if self.adventure_id is None:
            self.CreateAdventure()

        
        endpoint = "/api/v0/adventure"

        payload = {
                    "data": {
                        "type": "adventure",
                        "attributes": {
                            "user_id": self.user_id,
                            "adventure_id": self.adventure_id,
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
        
                        
        with self.client.put(endpoint, json=payload, headers=headers, catch_response=True) as response:
            if response.elapsed.total_seconds() > 1.0:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()} seconds")
            elif response.status_code == 200:
                print("Adventure Updated")
                response.success()
                self.GetUserAdventures()
            elif response.status_code == 400: 
                response.success()
            else:
                response.failure(f"Got wrong response: {response.status_code}")

    @task
    def DeleteAdventure(self):
        if self.user_id is None:
            self.login_user()
        if self.adventure_id is None:
            self.CreateAdventure()

        endpoint = "/api/v0/adventure"

        payload = {
                    "data": {
                        "type": "adventure",
                        "attributes": {
                            "adventure_id": self.adventure_id,
                        }
                    }
                }
        
        headers = {
            "Content-Type": "application/json"
        }
        
                
        with self.client.delete(endpoint, json=payload, headers=headers, catch_response=True) as response:
            if response.elapsed.total_seconds() > 1.0:
                response.failure(f"Request took too long: {response.elapsed.total_seconds()} seconds")
            elif response.status_code == 200:
                print("Adventure Deleted")
                response.success()
                self.GetUserAdventures()
                self.adventure_id = None
            elif response.status_code == 400: 
                response.success()
            else:
                response.failure(f"Got wrong response: {response.status_code}")

    @task
    def Logout(self):
        self.user_id = None
        print("User Logged Out")