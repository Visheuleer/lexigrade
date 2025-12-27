from pydantic import BaseModel


class CEFRClassifier(BaseModel):
    language: str
    text: str



