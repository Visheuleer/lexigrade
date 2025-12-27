from config import settings
import json
import spacy
import os


class LexicalComplexityTests:
    def __init__(self, language: str, target_level: str):
        self.language = language
        self.target_level = target_level
        self.lexicon = self._get_lexicon()
        self.frequency = self._get_frequency()
        self.nlp = spacy.load(self._get_language_model())

    def _get_language_model(self):
        if self.language == "spanish":
            return "es_core_news_sm"
        else:
            return "en_core_web_sm"


    def _get_lexicon(self):
        with open(os.path.join(settings.datasets_base_path, self.language, "cefr_lexicon.json"), "r", encoding="utf-8") as f:
            return json.load(f)



    def _get_frequency(self):
        path = os.path.join(
            settings.datasets_base_path, self.language, "subtlex_word_frequencies.json"
        )

        if not os.path.exists(path):
            return {}

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _compare_levels(self, l1, l2):
        order = ["A1", "A2", "B1", "B2", "C1", "C2"]
        return order.index(l1) - order.index(l2)

    def _lexical_cost(self, lemma, word_level):
        dist = self._compare_levels(word_level, self.target_level)
        zipf = self.frequency.get(lemma, {}).get("zipf", 0.0)

        if zipf >= 5.5:
            freq_weight = 0.25
        elif zipf >= 5.0:
            freq_weight = 0.4
        elif zipf >= 4.5:
            freq_weight = 0.6
        elif zipf >= 4.0:
            freq_weight = 0.8
        else:
            freq_weight = 1.0

        abstract = lemma.endswith((
            "ity", "ness", "ance", "ence",
            "ment", "ship", "hood", "acy"
        ))

        abstract_weight = 1.4 if abstract else 0.8

        return dist * freq_weight * abstract_weight

    def check_cefr_validity(self, text: str):
        doc = self.nlp(text)

        COST_BUDGET = {
            "A1": 0.0,
            "A2": 3.0,
            "B1": 6.0,
            "B2": 10.0,
            "C1": 20.0,
            "C2": 999.0
        }

        total_cost = 0.0
        flagged = []

        for token in doc:
            if not token.is_alpha:
                continue
            if token.pos_ == "PROPN" or token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            lemma = token.lemma_.lower()

            if lemma in self.lexicon:
                word_level = self.lexicon[lemma]

                if self._compare_levels(word_level, self.target_level) > 0:
                    cost = self._lexical_cost(lemma, word_level)
                    if cost >= 1.2:
                        total_cost += cost
                        flagged.append({
                            "word": token.text,
                            "lemma": lemma,
                            "level": word_level,
                            "cost": round(cost, 2)
                        })
        status = (
            "pass"
            if total_cost <= COST_BUDGET[self.target_level]
            else "fail"
        )

        return {
            "test_name": "CEFR Lexical Validity (Gradient)",
            "status": status,
            "details": {
                "total_cost": round(total_cost, 2),
                "budget": COST_BUDGET[self.target_level],
                "flagged_words": flagged,
            },
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
            "A1": 0.18,
            "A2": 0.15,
            "B1": 0.25,
            "B2": 0.35,
            "C1": 0.45,
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

        complex_words = []
        total_words = 0

        for token in doc:
            if not token.is_alpha:
                continue
            if token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            lemma = token.lemma_.lower()
            text_form = token.text.lower()

            total_words += 1

            is_derived_noun = (
                    token.pos_ == "NOUN"
                    and token.dep_ in ["nsubj", "dobj", "pobj", "obj", "obl"]
                    and lemma != text_form
            )

            is_derived_adv = (
                    token.pos_ == "ADV"
                    and lemma != text_form
            )

            zipf = self.frequency.get(lemma, {}).get("zipf", 0.0)
            low_frequency = zipf < 4.0

            if (is_derived_noun or is_derived_adv) and low_frequency:
                complex_words.append({
                    "word": token.text,
                    "lemma": lemma,
                    "pos": token.pos_,
                    "zipf": zipf,
                    "type": "derived_noun" if is_derived_noun else "derived_adverb"
                })

        if total_words == 0:
            return {
                "test_name": "Morphological Complexity",
                "status": "pass",
                "details": {
                    "ratio": 0.0,
                    "threshold": 0.0,
                    "complex_words": [],
                    "total_words": 0
                }
            }

        ratio = len(complex_words) / total_words

        thresholds = {
            "A1": 0.05,
            "A2": 0.10,
            "B1": 0.18,
            "B2": 0.30,
            "C1": 0.45,
            "C2": 1.00
        }

        limit = thresholds.get(self.target_level, 1.0)
        status = "pass" if ratio <= limit else "fail"

        top_complex_words = complex_words[:5]

        return {
            "test_name": "Morphological Complexity",
            "status": status,
            "details": {
                "ratio": ratio,
                "threshold": limit,
                "complex_words": top_complex_words,
                "total_words": total_words
            }
        }




