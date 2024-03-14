from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        # Cette méthode est appelée lorsque Locust commence à simuler un utilisateur spécifique
        self.client.post("/", {"email": "john@simplylift.co"})

    @task
    def load_protected_page(self):
        # Après la connexion, l'utilisateur simulé peut charger des pages protégées
        self.client.get("/")
        self.client.get("/showSummary")
        self.client.get("/book/Spring Festival/Simply Lift")
        self.client.get("/book/Fall Classic/Simply Lift")
