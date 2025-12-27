from config import settings
import os
import json
from datasets import load_dataset
import spacy
from collections import Counter
from tqdm import tqdm
from scripts.logger import setup_logger


logger = setup_logger()
universal_cefr_dataset = {}
lexicon = {}
frequencies = {}



def load_cefr_lexicon(languages: list[str]) -> bool:
    logger.info("Starting CEFR lexicon generation")

    for language in languages:
        logger.info(f"Language: {language.capitalize()}")

        logger.info("Loading CEFR building_datasets...")
        texts_by_level = build_texts_by_level_dataset(language)

        logger.info("Loading SpaCy model...")
        nlp = load_spacy_model(language)

        logger.info("Processing texts...")
        process_language_texts(nlp, texts_by_level)

        logger.info("Saving outputs...")
        save_language_outputs(language)

        clear_memory()
        logger.info("Done")

    logger.info("All languages processed successfully")
    return True


def process_language_texts(nlp, texts_by_level: dict):
    update_universal_cefr_dataset(texts_by_level)
    for level, texts in texts_by_level.items():
        logger.info(f"Level {level} — {len(texts)} texts")

        counter = count_tokens(nlp, texts, level)
        update_lexicon_and_frequencies(counter, level)



def count_tokens(nlp, texts: list, level:str) -> Counter:
    counter = Counter()

    for doc in tqdm(
            nlp.pipe(texts, batch_size=1000),
            total=len(texts),
            desc=f"  Tokenizing {level}",
            unit="text",
            delay=0.5
    ):
        tokens = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha
        ]
        counter.update(tokens)

    return counter


def update_lexicon_and_frequencies(counter: Counter, level: str):
    for word, freq in counter.items():
        update_lexicon(word, level)
        update_frequencies(word, freq)


def update_universal_cefr_dataset(texts_by_level: dict):
    for level, texts in texts_by_level.items():
        if level not in universal_cefr_dataset:
            universal_cefr_dataset[level] = []
        universal_cefr_dataset[level].extend(texts)


def update_lexicon(word: str, level: str):
    if word not in lexicon:
        lexicon[word] = level
    else:
        lexicon[word] = min(lexicon[word], level)


def update_frequencies(word: str, freq: int):
    frequencies[word] = frequencies.get(word, 0) + freq


def save_language_outputs(language: str):
    output_dir = os.path.join(settings.datasets_base_path, language)
    os.makedirs(output_dir, exist_ok=True)

    total_tokens = sum(frequencies.values())

    logger.info(f"Total tokens: {total_tokens:,}")
    logger.info(f"Lexicon size: {len(lexicon):,} words")

    save_json(
        os.path.join(output_dir, "universal_cefr_dataset.json"),
        universal_cefr_dataset,
        indent=2
    )

    save_json(
        os.path.join(output_dir, "cefr_lexicon.json"),
        lexicon,
        indent=4
    )

    save_json(
        os.path.join(output_dir, "cefr_frequencies.json"),
        {
            "total_tokens": total_tokens,
            "freqs": frequencies
        },
        indent=2
    )


def save_json(path: str, data: dict, indent: int):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def clear_memory():
    lexicon.clear()
    frequencies.clear()


def build_texts_by_level_dataset(language: str) -> dict:
    datasets = get_universal_cefr_datasets(language)

    texts_by_level = {
        'A1': [], 'A2': [], 'B1': [],
        'B2': [], 'C1': [], 'C2': []
    }

    for dataset_name in datasets.split(','):
        logger.info(f"Loading dataset: {dataset_name}")

        dataset = load_dataset(dataset_name, split="train")

        for item in tqdm(
                dataset,
                desc="  Reading samples",
                unit="sample",
        ):
            cefr = normalize_cefr_level(item["cefr_level"])
            if cefr:
                texts_by_level[cefr].append(item["text"])

    return texts_by_level


def get_universal_cefr_datasets(language: str) -> str:
    if language == 'english':
        return settings.universal_cefr_english_datasets
    return settings.universal_cefr_spanish_datasets


def normalize_cefr_level(level: str) -> str | None:
    if level == 'NA':
        return None
    return level.replace('+', '')


def load_spacy_model(language: str):
    model = get_nlp_model(language)
    return spacy.load(model)


def get_nlp_model(language: str) -> str:
    return "en_core_web_sm" if language == 'english' else "es_core_news_sm"