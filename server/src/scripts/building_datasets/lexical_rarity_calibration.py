from config import settings
import os
import json
import math
import statistics
from pathlib import Path
import spacy
from tqdm import tqdm
from scripts.logger import setup_logger

logger = setup_logger("cefr_rarity_calibration")

ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


def calibrate_cefr_rarity(languages: list[str]):
    for language in languages:
        logger.info(f"Starting calibration for language: {language.upper()}")

        nlp, base_path = load_language_resources(language)
        texts_by_level = load_cefr_texts(base_path)
        freqs, total_tokens = load_frequencies(base_path)

        logger.info(
            f"Frequencies loaded: {len(freqs):,} lemmas, {total_tokens:,} tokens"
        )

        thresholds, stats = calibrate_thresholds(
            texts_by_level,
            nlp,
            freqs,
            total_tokens
        )

        save_thresholds(base_path, thresholds, stats)

        logger.info(f"Calibration finished for language: {language.upper()}")


def load_language_resources(language: str):
    if language == "english":
        spacy_model = "en_core_web_sm"
    else:
        spacy_model = "es_core_news_sm"

    base_path = os.path.join(settings.datasets_base_path, language)

    logger.info(f"Loading spaCy model: {spacy_model}")
    nlp = spacy.load(spacy_model)

    return nlp, base_path


def load_cefr_texts(base_path) -> dict:
    logger.info("Loading CEFR texts by level")
    texts_by_level_file = Path(os.path.join(base_path, "universal_cefr_dataset.json"))
    return json.loads(texts_by_level_file.read_text(encoding="utf-8"))


def load_frequencies(base_path: str):
    freq_file = Path(os.path.join(base_path, "cefr_frequencies.json"))
    data = json.loads(freq_file.read_text(encoding="utf-8"))

    if "freqs" in data:
        return data["freqs"], data["total_tokens"]

    freqs = data
    return freqs, sum(freqs.values())


def normalize_level(level_raw: str) -> str | None:
    if not isinstance(level_raw, str):
        return None

    level = level_raw.strip().upper()
    return level if level in ORDER else None


def compute_rarity(freq: int, total_tokens: int, vocab_size: int) -> float:
    prob = (freq + 1) / (total_tokens + vocab_size)
    return -math.log(prob)


def rarity_for_text(text: str, nlp, freqs: dict, total_tokens: int) -> float | None:
    doc = nlp(text)
    vocab_size = len(freqs)
    rarities = []

    for token in doc:
        if not token.is_alpha:
            continue
        if token.pos_ == "PROPN" or token.ent_type_ in {"PERSON", "GPE", "ORG"}:
            continue

        lemma = token.lemma_.lower()
        freq = freqs.get(lemma, 0)

        rarity = compute_rarity(freq, total_tokens, vocab_size)
        rarities.append(rarity)

    if not rarities:
        return None

    return sum(rarities) / len(rarities)


def calibrate_thresholds(texts_by_level, nlp, freqs, total_tokens):
    thresholds = {}
    stats = {}

    for level_raw, texts in texts_by_level.items():
        level = normalize_level(level_raw)
        if level is None:
            logger.warning(f"Ignored invalid CEFR level: {level_raw}")
            continue

        logger.info(f"Calibrating level {level} ({len(texts)} texts)")

        rarity_scores = compute_level_rarities(
            texts,
            nlp,
            freqs,
            total_tokens,
            level
        )

        if len(rarity_scores) < 10:
            logger.warning(
                f"Level {level} has few samples ({len(rarity_scores)})"
            )

        thresholds[level], stats[level] = compute_statistics(
            rarity_scores
        )

    return thresholds, stats


def compute_level_rarities(texts, nlp, freqs, total_tokens, level: str):
    scores = []

    for text in tqdm(
        texts,
        desc=f"Scoring {level}",
        unit="text",
        delay=0.5
    ):
        score = rarity_for_text(text, nlp, freqs, total_tokens)
        if score is not None:
            scores.append(score)

    scores.sort()
    return scores


def compute_statistics(scores: list[float]):
    if not scores:
        return None, {"samples": 0}

    p90 = scores[int(len(scores) * 0.90)]
    mean = statistics.mean(scores)
    std = statistics.pstdev(scores) if len(scores) > 1 else 0

    return p90, {
        "samples": len(scores),
        "mean": mean,
        "std": std,
        "p90": p90
    }


def save_thresholds(base_path: str, thresholds: dict, stats: dict):
    out_file = Path(os.path.join(base_path, "cefr_rarity_thresholds.json"))

    out_file.write_text(
        json.dumps(
            {
                "thresholds": thresholds,
                "statistics": stats
            },
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
        errors="replace"
    )

    logger.info(f"Thresholds saved at: {out_file.absolute()}")
