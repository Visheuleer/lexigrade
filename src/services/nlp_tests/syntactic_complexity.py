import spacy


class SyntacticComplexityTests:
    def __init__(self, language: str, target_level: str):
        self.language = language
        self.target_level = target_level
        self.nlp = spacy.load(self._get_language_model())

    def _get_language_model(self):
        if self.language == "spanish":
            return "es_core_news_sm"
        else:
            return "en_core_web_sm"

    def check_clause_count(self, text: str):
        doc = self.nlp(text)

        clause_deps = {
            "advcl",
            "ccomp",
            "xcomp",
            "acl",
            "relcl"
        }

        clause_count = 1

        for token in doc:
            if token.dep_ in clause_deps:
                clause_count += 1

        thresholds = {
            "A1": 1,
            "A2": 1,
            "B1": 2,
            "B2": 3,
            "C1": 4,
            "C2": 10
        }

        limit = thresholds.get(self.target_level, 10)
        status = "pass" if clause_count <= limit else "fail"

        return {
            "test_name": "Clause Count",
            "status": status,
            "details": {
                "clause_count": clause_count,
                "threshold": limit
            }
        }

    def check_average_word_length(self, text: str):
        doc = self.nlp(text)
        total_chars = 0
        total_words = 0

        for token in doc:
            clean = token.text.strip(".,!?;:()[]{}'\"")

            if not clean.isalpha():
                continue
            if token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            total_chars += len(clean)
            total_words += 1

        if total_words == 0:
            return {
                "test_name": "Average Word Length",
                "status": "pass",
                "details": {
                    "avg_word_length": 0.0,
                    "threshold": 0.0,
                    "total_words": 0
                }
            }

        avg_length = total_chars / total_words

        thresholds = {
            "A1": 4.5,
            "A2": 5.0,
            "B1": 5.5,
            "B2": 6.0,
            "C1": 6.5,
            "C2": 10.0
        }

        limit = thresholds.get(self.target_level, 10.0)
        status = "pass" if avg_length <= limit else "fail"

        return {
            "test_name": "Average Word Length",
            "status": status,
            "details": {
                "avg_word_length": avg_length,
                "threshold": limit,
                "total_words": total_words
            }
        }