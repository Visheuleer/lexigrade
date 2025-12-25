import json
import math
import os
import numpy as np
from typing import Dict
from api.services.nlp_tests.lexical_complexity import LexicalComplexityTests
from api.services.nlp_tests.lexical_rarity import LexicalRarityTest
from api.services.nlp_tests.syntactic_complexity import SyntacticComplexityTests
from config import settings


class NLPBasedCEFRClassifier:
    CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

    def __init__(self, language: str):
        self.language = language

        self.lexical_complexity = LexicalComplexityTests(language, "A1")
        self.lexical_rarity = LexicalRarityTest(language, "A1")
        self.syntactic_complexity = SyntacticComplexityTests(language, "A1")

        self.metric_ranges = self._load_metric_ranges()

        self.weights = self._get_language_weights()

        self.cefr_score_bands = {
            "A1": (0.00, 0.18),
            "A2": (0.18, 0.33),
            "B1": (0.33, 0.48),
            "B2": (0.48, 0.63),
            "C1": (0.63, 0.80),
            "C2": (0.80, 1.00),
        }


    def _load_metric_ranges(self) -> Dict:
        path = os.path.join(
            settings.datasets_base_path,
            self.language,
            "cefr_metric_ranges.json"
        )

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


    def _get_language_weights(self) -> Dict[str, float]:
        if self.language == "english":
            return {
                "lexical_rarity": 0.40,
                "syntactic_complexity": 0.35,
                "morphological_complexity": 0.15,
                "difficult_word_ratio": 0.10,
            }
        else:
            return {
                "lexical_rarity": 0.30,
                "syntactic_complexity": 0.45,
                "morphological_complexity": 0.10,
                "difficult_word_ratio": 0.15,
            }

    @staticmethod
    def _normalize(value: float, p05: float, p95: float) -> float:
        if p95 <= p05:
            return 0.0
        value = max(p05, min(p95, value))
        return (value - p05) / (p95 - p05)

    def _log_normalize(self, value: float, p05: float, p95: float) -> float:
        return self._normalize(
            math.log1p(value),
            math.log1p(p05),
            math.log1p(p95),
        )


    def _extract_metrics(self, text: str) -> Dict[str, float]:
        metrics = {}


        rarity = self.lexical_rarity.calculate(text)
        metrics["lexical_rarity"] = rarity["details"]["rarity_score"]


        dwr = self.lexical_complexity.check_difficult_word_ratio(text)
        morph = self.lexical_complexity.check_morphological_complexity(text)

        metrics["difficult_word_ratio"] = dwr["details"]["ratio"]
        metrics["morphological_ratio"] = morph["details"]["ratio"]


        clauses = self.syntactic_complexity.check_clause_count(text)
        avg_len = self.syntactic_complexity.check_average_word_length(text)

        metrics["clause_count"] = clauses["details"]["mean_clauses_per_sentence"]
        metrics["avg_word_length"] = avg_len["details"]["avg_word_length"]

        return metrics


    def _compute_complexity_score(self, metrics: Dict[str, float]) -> float:
        r = self.metric_ranges

        rarity = self._normalize(
            metrics["lexical_rarity"],
            r["lexical_rarity"]["p05"],
            r["lexical_rarity"]["p95"],
        )

        dwr = self._normalize(
            metrics["difficult_word_ratio"],
            r["difficult_word_ratio"]["p05"],
            r["difficult_word_ratio"]["p95"],
        )

        morph = self._normalize(
            metrics["morphological_ratio"],
            r["morphological_ratio"]["p05"],
            r["morphological_ratio"]["p95"],
        )

        clauses = self._log_normalize(
            metrics["clause_count"],
            r["clause_count"]["p05"],
            r["clause_count"]["p95"],
        )

        avg_len = self._normalize(
            metrics["avg_word_length"],
            r["avg_word_length"]["p05"],
            r["avg_word_length"]["p95"],
        )

        syntactic = (clauses + avg_len) / 2

        score = (
            rarity * self.weights["lexical_rarity"]
            + syntactic * self.weights["syntactic_complexity"]
            + morph * self.weights["morphological_complexity"]
            + dwr * self.weights["difficult_word_ratio"]
        )

        return round(score, 4)


    def _map_score_to_cefr(self, score: float):
        for level, (low, high) in self.cefr_score_bands.items():
            if low <= score < high:
                confidence = 1.0 - abs(score - (low + high) / 2) / ((high - low) / 2)
                return level, round(max(0.0, confidence), 3)

        return "C2", 0.9

    def _lexical_control_ratio(self, text: str) -> float:
        doc = self.lexical_complexity.nlp(text)

        controlled = 0
        total = 0

        for token in doc:
            if not token.is_alpha:
                continue
            if token.pos_ == "PROPN" or token.ent_type_ in ["PERSON", "GPE", "ORG"]:
                continue

            total += 1
            lemma = token.lemma_.lower()

            level = self.lexical_complexity.lexicon.get(lemma)
            if level in {"A1", "A2", "B1"}:
                controlled += 1

        if total == 0:
            return 1.0

        return controlled / total


    @staticmethod
    def _length_dampening(token_count: int, l: int = 40) -> float:
        if token_count <= 0:
            return 0.0
        return min(1.0, math.log(token_count + 1) / math.log(l))

    @staticmethod
    def split_into_windows(doc, window_size=2):
        sentences = list(doc.sents)

        if len(sentences) <= window_size:
            return [sentences]

        windows = []
        for i in range(0, len(sentences), window_size):
            window = sentences[i:i + window_size]
            windows.append(window)

        return windows


    def estimate(
            self,
            text: str,
            window_size: int = 2,
            return_debug: bool = False
    ) -> dict:
        if not text.strip():
            return {
                "estimated_level": "A1",
                "confidence": 0.0,
                "error": "Empty text"
            }

        doc = self.lexical_complexity.nlp(text)
        windows = self.split_into_windows(doc, window_size)

        window_scores = []
        window_levels = []
        window_metrics = []

        for window in windows:
            window_text = " ".join(sent.text for sent in window)

            metrics = self._extract_metrics(window_text)
            score = self._compute_complexity_score(metrics)
            level, _ = self._map_score_to_cefr(score)

            window_scores.append(score)
            window_levels.append(level)

            window_metrics.append({
                "text": window_text,
                "score": round(score, 4),
                "level": level,
                "metrics": metrics
            })

        mean_score = float(np.mean(window_scores))
        p75_score = float(np.percentile(window_scores, 75))

        final_score = 0.6 * p75_score + 0.4 * mean_score

        lcr = self._lexical_control_ratio(text)
        lcr_penalty = 1.0 - lcr
        final_score *= (1.0 - 0.25 * lcr_penalty)

        token_count = sum(
            1 for token in doc
            if token.is_alpha
        )
        length_factor = self._length_dampening(token_count)

        final_score *= length_factor

        estimated_level, base_confidence = self._map_score_to_cefr(final_score)

        agreement = sum(
            1 for lvl in window_levels if lvl == estimated_level
        ) / len(window_levels)

        std = float(np.std(window_scores))
        stability = max(0.0, 1.0 - std)

        confidence = (
                0.6 * agreement +
                0.4 * stability
        )

        confidence *= length_factor

        confidence = round(min(1.0, max(0.0, confidence)), 3)

        result = {
            "estimated_level": estimated_level,
            "confidence": confidence,
            "complexity_score": round(final_score, 4),
            "aggregation": {
                "mean": round(mean_score, 4),
                "p75": round(p75_score, 4),
                "windows": len(window_scores),
                "agreement": round(agreement, 3),
                "stability": round(stability, 3),
                "length_factor": round(length_factor, 3),
                "lexical_control_ratio": round(lcr, 3)
            }
        }

        if return_debug:
            result["windows"] = window_metrics

        return result

