import os
import math
import spacy
import json
from config import settings

class LexicalRarityTest:
    def __init__(self, language: str, target_level: str):
        self.language = language
        self.target_level = target_level
        self.frequencies = self._get_frequencies()["freqs"]
        self.total_tokens = self._get_frequencies()["total_tokens"]
        self.nlp = spacy.load(self._get_language_model())

        with open(os.path.join(settings.datasets_base_path, self.language, "cefr_rarity_thresholds.json")) as f:
            config = json.load(f)
        self.level_thresholds = config["thresholds"]

        self.V = max(1, len(self.frequencies))


    def _get_language_model(self):
        if self.language == "spanish":
            return "es_core_news_sm"
        else:
            return "en_core_web_sm"

    def _get_frequencies(self):
        with open(os.path.join(settings.datasets_base_path, self.language, "cefr_frequencies.json"), "r", encoding="utf-8") as f:
            return json.load(f)

    def _word_rarity(self, lemma: str):
        freq = self.frequencies.get(lemma, 0)

        prob = (freq + 1) / (self.total_tokens + self.V)  # probability mass
        rarity = -math.log(prob)

        return {
            "lemma": lemma,
            "freq": freq,
            "prob": prob,
            "rarity": rarity
        }

    def calculate(self, text: str, debug: bool = False):
        doc = self.nlp(text)
        rarity_values = []
        per_word = []

        for token in doc:
            if not token.is_alpha:
                continue
            if token.pos_ == "PROPN" or token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            lemma = token.lemma_.lower()
            info = self._word_rarity(lemma)
            rarity_values.append(info["rarity"])
            per_word.append({
                "token": token.text,
                **info
            })

        if not rarity_values:
            return {
                "test_name": "Lexical Rarity Score",
                "status": "pass",
                "details": {"rarity_score": 0.0, "words_evaluated": 0}
            }

        rarity_score = sum(rarity_values) / len(rarity_values)
        threshold = self.level_thresholds.get(self.target_level, float("inf"))
        status = "pass" if rarity_score <= threshold else "fail"

        result = {
            "test_name": "Lexical Rarity Score",
            "status": status,
            "details": {
                "rarity_score": rarity_score,
                "threshold": threshold,
                "words_evaluated": len(rarity_values),
            }
        }

        if debug:
            result["details"]["per_word"] = sorted(per_word, key=lambda x: -x["rarity"])

        return result

# test = LexicalRarityTest("english", "A1")
# out = test.calculate("Her perseverance was indispensable to the accomplishment of the mission.", debug=False)
# print(json.dumps(out, indent=2))