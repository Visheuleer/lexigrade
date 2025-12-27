import requests
from config import settings


class LLMGeneratorService:

    def __init__(
            self,
            language: str,
            original_text: str,
            target_cefr: str,
            previous_simplification: str = "",
            feedback: str = ""

    ):
        self.language = language
        self.original_text = original_text
        self.target_cefr = target_cefr
        self.previous_simplification = previous_simplification
        self.feedback = feedback


    def generate(self) -> str:
        response = requests.post(
        settings.llm_models_service_url,
            json={
                "model": "lexigrade-generator",
                "prompt": (
                    "[NO META TEXT — OUTPUT ONLY THE REWRITTEN CONTENT]\n"
                    f"LANGUAGE: {self.language}\n"
                    f"CEFR TARGET: {self.target_cefr}\n"
                    f"Text: {self.original_text}"
                    ),
                "options": {
                    "stop": ["Here is the rewritten"]
                    },
                "stream": False
                }
                                )

        if response.ok:
            return response.json()["response"]
        return ""

    def regenerate(self) -> str:

        response = requests.post(
            settings.llm_models_service_url,
            json={
                "model": "lexigrade-generator",
                "prompt": (
                    "[NO META TEXT — OUTPUT ONLY THE REWRITTEN CONTENT]\n"
                    f"LANGUAGE: {self.language}\n"
                    f"The original sentence: '{self.original_text}'\n"
                    f"Your previous simplification: '{self.previous_simplification}'\n"
                    f"Failed to meet the CEFR level target of: '{self.target_cefr}'\n"
                    f"Because: {self.feedback}\n"
                    f"Please provide a new simplification respecting the feeedback."
                ),
                "stream": False
            }
        )

        response.raise_for_status()
        return response.json()["response"]
