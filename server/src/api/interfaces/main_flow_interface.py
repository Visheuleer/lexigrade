from pydantic import BaseModel


class MainFlowInterface(BaseModel):
    language: str
    original_text: str
    cefr_level_target: str