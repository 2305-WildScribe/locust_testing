from locust import HttpUser, task, between, SequentialTaskSet
import json



class MyUser(HttpUser):
    host = "https://safe-refuge-07153-b08bc7602499.herokuapp.com"
    wait_time = between(1, 2)  # Time between consecutive requests
    user_id = None 

    @task
    def login_user(self):
        # Define the URL you want to test
        endpoint = "/api/v0/user"

        # Define the JSON body
        payload = {
            "data":{
                "type": "user",
                "attributes": {
                    "email": "me@gmail.com",
                    "password": "hi"
                }
            }
        }

        # Set the request headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Send a POST request to the /user endpoint with the JSON body
        response = self.client.post(endpoint, json=payload, headers=headers)

        # You can add assertions to validate the response
        # For example, checking if the response status code is 201 (Created)

        if response.status_code == 200:
            try:
                response_data = json.loads(response.content)
                self.user_id = response_data["data"]["attributes"]["user_id"]
                # print(f"User ID: {self.user_id}")
            except json.JSONDecodeError:
                print("Failed to parse JSON response.")
            self.environment.events.request.fire(
                request_type="POST",
                name=endpoint,
                response_time=response.elapsed.total_seconds(),
                response_length=len(response.content),
            )
        else:
            self.environment.events.request.fire(
                request_type="POST",
                name=endpoint,
                response_time=response.elapsed.total_seconds(),
                exception=response.status_code,
            )

    # @task
    def GetUserAdventures(self):
                # Define the URL you want to test
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
        response = self.client.post(endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            self.environment.events.request.fire(
                request_type="POST",
                name=endpoint,
                response_time=response.elapsed.total_seconds(),
                response_length=len(response.content),
            )
        else:
            self.environment.events.request.fire(
                request_type="POST",
                name=endpoint,
                response_time=response.elapsed.total_seconds(),
                exception=response.status_code,
            )
