import os
import dotenv


class Settings:
    def __init__(self):
        dotenv.load_dotenv()
        self.models_service_url = os.getenv('MODELS_SERVICE_URL')

settings = Settings()