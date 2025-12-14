from config import settings
import json
import spacy
import os


class LexicalComplexityTests:
    def __init__(self, language: str, target_level: str):
        self.language = language
        self.target_level = target_level
        self.lexicon = self._get_lexicon()
        self.nlp = spacy.load(self._get_language_model())

    def _get_language_model(self):
        if self.language == "spanish":
            return "es_core_news_sm"
        else:
            return "en_core_web_sm"


    def _get_lexicon(self):
        with open(os.path.join(settings.datasets_base_path, self.language, "cefr_lexicon.json"), "r", encoding="utf-8") as f:
            return json.load(f)

    def check_cefr_validity(self, text: str):
        doc = self.nlp(text)
        invalid = []

        for token in doc:
            if not token.is_alpha:
                continue
            if token.pos_ == "PROPN" or token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            lemma = token.lemma_.lower()

            if lemma in self.lexicon:
                word_level = self.lexicon[lemma]

                if self._compare_levels(word_level, self.target_level) > 0:
                    invalid.append({
                        "word": token.text,
                        "lemma": lemma,
                        "level": word_level,
                        "allowed": self.target_level
                    })

        return {
            "test_name": "CEFR Lexical Validity Check",
            "status": "fail" if invalid else "pass",
            "details": {"invalid_words": invalid}
        }

    def check_oov(self, text: str):
        doc = self.nlp(text)
        oov = []

        for token in doc:
            if token.pos_ == "PROPN" or token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue
            if token.is_alpha:
                lemma = token.lemma_.lower()
                if lemma not in self.lexicon:
                    oov.append(lemma)

        return {
            "test_name": "OOV Vocabulary Detection",
            "status": "fail" if oov else "pass",
            "details": {"oov_words": oov}
        }

    def check_difficult_word_ratio(self, text: str):
        doc = self.nlp(text)
        difficult_count = 0
        total_count = 0

        for token in doc:
            if not token.is_alpha:
                continue
            if token.pos_ == "PROPN" or token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            lemma = token.lemma_.lower()
            total_count += 1

            if lemma in self.lexicon:
                word_level = self.lexicon[lemma]

                if self._compare_levels(word_level, self.target_level) > 0:
                    difficult_count += 1

            else:
                difficult_count += 1

        if total_count == 0:
            return {
                "test_name": "Difficult Word Ratio",
                "status": "pass",
                "details": {
                    "ratio": 0.0,
                    "difficult_words": 0,
                    "total_words": 0
                }
            }

        ratio = difficult_count / total_count

        thresholds = {
            "A1": 0.03,
            "A2": 0.10,
            "B1": 0.20,
            "B2": 0.30,
            "C1": 0.40,
            "C2": 1.00
        }

        limit = thresholds.get(self.target_level, 1.0)
        status = "pass" if ratio <= limit else "fail"

        return {
            "test_name": "Difficult Word Ratio",
            "status": status,
            "details": {
                "ratio": ratio,
                "threshold": limit,
                "difficult_words": difficult_count,
                "total_words": total_count
            }
        }

    def check_morphological_complexity(self, text: str):
        doc = self.nlp(text)

        complex_suffixes = [
            "tion", "sion", "ment", "ness", "ity", "ance", "ence",
            "ship", "hood", "acy", "ology",
            "able", "ible", "ous", "ive", "ical", "ant", "ent", "ary"
        ]

        difficult_words = 0
        total_words = 0

        for token in doc:
            clean = token.text.strip(".,!?;:()[]{}'\"").lower()

            if not clean.isalpha():
                continue
            if token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            total_words += 1

            for suf in complex_suffixes:
                if clean.endswith(suf):
                    difficult_words += 1
                    break

            if clean.endswith("ly") and token.pos_ == "ADV":
                lemma = token.lemma_.lower()
                if lemma.endswith(("ous", "able", "ive", "ical", "ant", "ent")):
                    difficult_words += 1

        if total_words == 0:
            return {
                "test_name": "Morphological Complexity",
                "status": "pass",
                "details": {
                    "ratio": 0.0,
                    "threshold": 0.0,
                    "complex_words": 0,
                    "total_words": 0
                }
            }

        ratio = difficult_words / total_words

        thresholds = {
            "A1": 0.03,
            "A2": 0.08,
            "B1": 0.15,
            "B2": 0.25,
            "C1": 0.35,
            "C2": 1.00
        }

        limit = thresholds.get(self.target_level, 1.0)
        status = "pass" if ratio <= limit else "fail"

        return {
            "test_name": "Morphological Complexity",
            "status": status,
            "details": {
                "ratio": ratio,
                "threshold": limit,
                "complex_words": difficult_words,
                "total_words": total_words
            }
        }

    def _compare_levels(self, l1, l2):
        order = ["A1", "A2", "B1", "B2", "C1", "C2"]
        return order.index(l1) - order.index(l2)



