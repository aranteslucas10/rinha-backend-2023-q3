from locust import HttpUser, task


class StressTestApi(HttpUser):
    @task
    def contagem_pessoas(self):
        self.client.get(f"/contagem-pessoas")
