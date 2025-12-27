import json
import os
import numpy as np
from collections import defaultdict
from pathlib import Path
from tqdm import tqdm

from config import settings
from scripts.logger import setup_logger

from api.services.nlp_tests.lexical_complexity import LexicalComplexityTests
from api.services.nlp_tests.lexical_rarity import LexicalRarityTest
from api.services.nlp_tests.syntactic_complexity import SyntacticComplexityTests


logger = setup_logger("cefr_metric_ranges")
CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


def calibrate_cefr_metric_ranges(languages: list[str]):
    for language in languages:
        logger.info(f"Calibrating metric ranges for language: {language.upper()}")

        texts_by_level = load_texts_by_level(language)
        tests = initialize_tests(language)

        collected = collect_metrics(
            texts_by_level,
            tests
        )

        ranges = compute_metric_ranges(collected)
        save_metric_ranges(language, ranges)

        logger.info(f"Metric calibration finished for language: {language.upper()}")


def load_texts_by_level(language: str) -> dict:
    path = Path(
        os.path.join(
            settings.datasets_base_path,
            language,
            "universal_cefr_dataset.json"
        )
    )

    logger.info("Loading CEFR texts by level")
    return json.loads(path.read_text(encoding="utf-8"))


def initialize_tests(language: str):
    lexical = LexicalComplexityTests(language, "A1")
    rarity = LexicalRarityTest(language, "A1")
    syntactic = SyntacticComplexityTests(language, "A1")

    return {
        "lexical": lexical,
        "rarity": rarity,
        "syntactic": syntactic
    }


def collect_metrics(texts_by_level: dict, tests: dict):
    collected = defaultdict(list)

    for level, texts in texts_by_level.items():
        if level not in CEFR_ORDER:
            continue

        logger.info(f"Processing level {level} ({len(texts)} texts)")

        for text in tqdm(
            texts,
            desc=f"Scoring {level}",
            unit="text",
            leave=False,
            delay=0.5
        ):
            process_text_metrics(
                text,
                collected,
                tests
            )

    return collected


def process_text_metrics(text: str, collected: dict, tests: dict):
    if not isinstance(text, str) or not text.strip():
        return

    lexical = tests["lexical"]
    rarity = tests["rarity"]
    syntactic = tests["syntactic"]

    r = rarity.calculate(text)
    collected["lexical_rarity"].append(
        r["details"]["rarity_score"]
    )

    dwr = lexical.check_difficult_word_ratio(text)
    collected["difficult_word_ratio"].append(
        dwr["details"]["ratio"]
    )

    morph = lexical.check_morphological_complexity(text)
    collected["morphological_ratio"].append(
        morph["details"]["ratio"]
    )

    clauses = syntactic.check_clause_count(text)
    collected["clause_count"].append(
        clauses["details"]["clause_count"]
    )

    awl = syntactic.check_average_word_length(text)
    collected["avg_word_length"].append(
        awl["details"]["avg_word_length"]
    )


def compute_metric_ranges(collected: dict, low: int = 5, high: int = 95):
    ranges = {}

    for metric, values in collected.items():
        clean_values = [v for v in values if v is not None]

        if len(clean_values) < 50:
            logger.warning(
                f"Few samples for metric '{metric}' ({len(clean_values)})"
            )

        ranges[metric] = compute_percentiles(
            clean_values,
            low,
            high
        )

    return ranges


def compute_percentiles(values: list[float], low: int, high: int):
    return {
        "p05": float(np.percentile(values, low)),
        "p95": float(np.percentile(values, high))
    }


def save_metric_ranges(language: str, ranges: dict):
    out_path = os.path.join(
        settings.datasets_base_path,
        language,
        "cefr_metric_ranges.json"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ranges, f, indent=2, ensure_ascii=False)

    logger.info(f"Metric ranges saved at: {out_path}")
