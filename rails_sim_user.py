from locust import HttpUser, task, between
import random
import csv
from faker import Faker

class MyUser(HttpUser):
    host = "https://wildscribe-rails-test-3a5fcd1ed43b.herokuapp.com"
    wait_time = between(1, 5)  

    def on_start(self):
            self.user_id = None     
            self.adventure_id = None
            self.faker = Faker()
            self.index = random.randint(1, 2000)


    @task
    def login_user(self):
        fake = Faker()
        email = fake.email()
        password = fake.password()

        email = f"me+{self.index}@gmail.com"
        password = f"password+{self.index}"

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
                json_response = response.json()
                self.user_id = json_response["data"]["attributes"]["user_id"]
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
                "user_id": self.user_id
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
                if json_response["data"]["attributes"]["adventures"] != []:
                    adventures = json_response["data"]["attributes"]["adventures"]
                    random_adventure = random.choice(adventures)
                    self.adventure_id = random_adventure["id"]
                response.success()
            elif response.status_code == 404:
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
                        }
                    }
                }

        headers = {
            "Content-Type": "application/json"
        }

        with self.client.post(endpoint, json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                json_response = response.json()
                self.adventure_id = json_response["data"]["attributes"]["adventure"]["id"]
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

    @task
    def cleanup(self):
        if self.user_id is not None:
            self.DeleteAdventure()
            self.Logout()