from pydantic import BaseModel


class OrchestratorInterface(BaseModel):
    language: str
    original_text: str
    cefr_level_target: str