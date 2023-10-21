from locust import HttpUser, task, between, SequentialTaskSet, events, User

import random
import csv
from faker import Faker
from locust.exception import RescheduleTask
    
class LoginTaskSet(SequentialTaskSet):
    

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
    def login_user(self):        
        if self.users:
            user = random.choice(self.users)  # Select a random user
            email = user[2]
            password = user[3]
            self.user_id = user[0]
    
    # Define the URL you want to test
        endpoint = "/api/v0/user"

        # Define the JSON body
        payload = {
            "data": {
                "type": "user",
                "attributes": {
                    "email": f"{email}",
                    "password": f"{password}"
                }
            }
        }

        # Set the request headers
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
                response.success()
            else:
                response.failure(f"Got wrong response: {response.status_code}")

    
class MyUser(HttpUser):
    host = "https://safe-refuge-07153-b08bc7602499.herokuapp.com"
    wait_time = between(1, 5)  # Time between consecutive requests
    tasks = [LoginTaskSet]
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.failure_count = 0
#         self.success_count = 0
#         self.max_failure_rate = 0.4  # 40% failure rate threshold

#     # ... (other methods)

# @events.request.add_listener
# def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
#     if exception and "failure" in str(exception):
#         user = kwargs['request_meta']['locust_user']
#         user.failure_count += 1
#         check_failure_rate(user)

# @events.request.add_listener
# def on_request_success(request_type, name, response_time, response_length, **kwargs):
#     user = kwargs['request_meta']['locust_user']
#     user.success_count += 1
#     check_failure_rate(user)

# def check_failure_rate(user):
#     total_requests = user.failure_count + user.success_count
#     failure_rate = user.failure_count / total_requests if total_requests > 0 else 0
#     if failure_rate >= user.max_failure_rate:
#         user.environment.runner.quit()
