import os
import dotenv


class Settings:
    def __init__(self):
        dotenv.load_dotenv()
        self.llm_models_service_url = os.getenv('MODELS_SERVICE_URL')
        self.universal_cefr_spanish_datasets = os.getenv('UNIVERSAL_CEFR_SPANISH_DATASETS')
        self.universal_cefr_english_datasets = os.getenv('UNIVERSAL_CEFR_ENGLISH_DATASETS')
        self.datasets_base_path = os.getenv('DATASETS_BASE_PATH')
        self.cefr_classifier_model_base_path = os.getenv('CEFR_CLASSIFIER_BASE_MODEL_PATH')
settings = Settings()