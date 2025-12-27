from pydantic import BaseModel


class LLMReviewerInterface(BaseModel):
    language: str
    original_text: str
    simplified_text: str



