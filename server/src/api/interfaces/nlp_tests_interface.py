from pydantic import BaseModel


class NLPTests(BaseModel):
    language: str
    simplified_text: str
    cefr_level_target: str



