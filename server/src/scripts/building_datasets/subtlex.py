import json
import os
from config import settings


def build_subtlex_frequency_map(languages:list[str]):
    for language in languages:
        file_path = os.path.join(settings.datasets_base_path, language, "subtlex_word_frequencies.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        freq_map = {}
        if language == "english":
            for entry in data['out1g']:
                word = entry["Word"].lower()
                zipf = float(entry["Zipf-value"])
                pos = entry.get("Dom_PoS_SUBTLEX", "").upper()

                freq_map[word] = {
                    "zipf": zipf,
                    "pos": pos
                }
        else:
            for entry in data["Subtlex-Esp"]:
                for suffix in ["", "_1", "_2"]:
                    word_key = f"Word{suffix}"
                    log_key = f"Log freq.{suffix}"

                    if word_key not in entry or log_key not in entry:
                        continue

                    word = entry[word_key].strip().lower()
                    if not word:
                        continue

                    try:
                        log_freq = float(entry[log_key])
                    except ValueError:
                        continue

                    freq_map[word] = {
                        "zipf": log_freq,
                        "pos": ""
                    }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(freq_map, f, indent=2, ensure_ascii=False)