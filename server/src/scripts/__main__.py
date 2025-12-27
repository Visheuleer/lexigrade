from scripts.building_datasets import load_cefr_lexicon, calibrate_cefr_rarity, calibrate_cefr_metric_ranges, build_subtlex_frequency_map

LANGUAGES =['spanish']

def main():
    # load_cefr_lexicon(LANGUAGES)
    # calibrate_cefr_rarity(LANGUAGES)
    # calibrate_cefr_metric_ranges(LANGUAGES)
    build_subtlex_frequency_map(LANGUAGES)


if __name__ == "__main__":
    main()