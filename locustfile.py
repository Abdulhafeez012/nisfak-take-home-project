from locust import HttpUser, task, between
import json

class SurveyLoadTest(HttpUser):
    wait_time = between(1, 2)
    token = None
    username = None # EDIT THIS LINE
    password = None # EDIT THIS LINE

    def on_start(self):
        response = self.client.post('/api/v1/token/', json={'username': self.username, 'password': self.password})
        response.raise_for_status()
        self.token = response.json().get('access')

    @task
    def get_surveys(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/api/v1/surveys/', headers=headers)
        response.raise_for_status()

    @task
    def get_sections(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/api/v1/sections/', headers=headers)
        response.raise_for_status()

    @task
    def get_fields(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/api/v1/fields/', headers=headers)
        response.raise_for_status()

    @task
    def get_surveys_responses(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/api/v1/survey-responses/', headers=headers)
        response.raise_for_status()
