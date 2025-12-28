import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import settings

LABELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

class SupervisedCEFREstimationService:
    def __init__(self, language: str):
        self.device = torch.device("cpu") #torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = os.path.join(settings.cefr_classifier_model_base_path, language)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path, local_files_only=True)

        self.model.to(self.device)
        self.model.eval()

    def estimate(self, text: str) -> dict:
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        pred_id = int(np.argmax(probs))

        return {
            "estimated_level": LABELS[pred_id],
            "confidence": float(probs[pred_id]),
            "probabilities": {
                LABELS[i]: float(probs[i]) for i in range(len(LABELS))
            }
        }