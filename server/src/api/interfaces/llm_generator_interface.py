from pydantic import BaseModel


class LLMGeneratorInterface(BaseModel):
    language: str
    original_text: str
    cefr_level_target: str

class LLMRegeneratorInterface(BaseModel):
    language: str
    original_text: str
    cefr_level_target: str
    previous_simplification: str
    feedback: str


