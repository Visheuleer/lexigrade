import requests
from config import settings


class LLMReviewerService:

    def __init__(
            self,
            language: str,
            original_text: str,
            simplified_text: str = "",

    ):
        self.language = language
        self.original_text = original_text
        self.simplified_text = simplified_text


    def review(self) -> str:
        response = requests.post(
        settings.llm_models_service_url,
            json={
                "model": "lexigrade-reviewer",
                "prompt": (
                    f"LANGUAGE: {self.language}\n"
                    f"ORIGINAL TEXT: {self.original_text}\n"
                    f"SIMPLIFIED TEXT: {self.simplified_text}"
                    ),
                "stream": False
                }
                                )

        if response.ok:
            return response.json()["response"]
        return ""
