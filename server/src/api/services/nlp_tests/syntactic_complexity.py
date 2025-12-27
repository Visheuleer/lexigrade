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

        sentence_details = []

        for sent in doc.sents:
            clauses = 1
            for token in sent:
                if token.dep_ in clause_deps:
                    clauses += 1

            sentence_details.append({
                "text": sent.text.strip(),
                "clauses": clauses
            })

        thresholds = {
            "A1": 1,
            "A2": 1,
            "B1": 2,
            "B2": 3,
            "C1": 4,
            "C2": 10
        }

        limit = thresholds.get(self.target_level, 10)

        max_clauses = max(s["clauses"] for s in sentence_details) if sentence_details else 0
        mean_clauses = sum(s["clauses"] for s in sentence_details) / len(sentence_details) if sentence_details else 0.0

        status = "pass" if max_clauses <= limit else "fail"

        worst_sentences = sorted(
            sentence_details,
            key=lambda x: -x["clauses"]
        )[:2]

        return {
            "test_name": "Clause Count",
            "status": status,
            "details": {
                "max_clauses_per_sentence": max_clauses,
                "mean_clauses_per_sentence": mean_clauses,
                "threshold": limit,
                "sentences": worst_sentences
            }
        }

    def check_average_word_length(self, text: str):
        doc = self.nlp(text)

        words = []
        total_chars = 0

        for token in doc:
            clean = token.text.strip(".,!?;:()[]{}'\"")

            if not clean.isalpha():
                continue
            if token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            words.append(clean)
            total_chars += len(clean)

        total_words = len(words)

        if total_words == 0:
            return {
                "test_name": "Average Word Length",
                "status": "pass",
                "details": {
                    "avg_word_length": 0.0,
                    "threshold": 0.0,
                    "total_words": 0,
                    "long_words": []
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

        long_words = sorted(
            [w for w in words if len(w) > limit],
            key=len,
            reverse=True
        )[:5]

        return {
            "test_name": "Average Word Length",
            "status": status,
            "details": {
                "avg_word_length": avg_length,
                "threshold": limit,
                "total_words": total_words,
                "long_words": long_words
            }
        }
