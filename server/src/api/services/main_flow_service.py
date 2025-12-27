import json
from api.services import CEFRClassifierService, LLMGeneratorService, LLMReviewerService, NLPTestsService
from api.enums import StrategySimplificationEnum
from api.services import utils


ORDER = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']


class MainFlowService:

    def __init__(
            self,
            language: str,
            original_text: str,
            target_cefr: str

    ):
        self.language = language
        self.original_text = original_text
        self.target_cefr = target_cefr


    def execute_flow(self) -> dict:
        original_cefr_level = self._estimate_cefr_level()
        strategy = self._define_simplification_strategy(original_cefr_level)

        if strategy == StrategySimplificationEnum.NOT_NECESSARY:
            return {
                "accepted": True,
                "strategy": strategy.value,
                "original_cefr": original_cefr_level,
                "target_cefr": self.target_cefr,
                "text": self.original_text,
            }

        if strategy == StrategySimplificationEnum.SIMPLE:
            simplified_text = self._generate_simple_simplification()
        else:
            simplified_text = self._generate_simplification_in_stages(original_cefr_level)

        nlp_tests_service = NLPTestsService(
            language=self.language,
            target_level=self.target_cefr
        )
        final_hard = nlp_tests_service.run_hard_constraints_tests(simplified_text)
        final_soft = nlp_tests_service.run_soft_constraints_tests(simplified_text)
        semantic_review = None
        if final_hard["accepted"] and final_soft["accepted"]:
            llm_reviewer_service = LLMReviewerService(
                language=self.language,
                original_text=self.original_text,
                simplified_text=simplified_text
            )
            review_text = llm_reviewer_service.review()
            try:
                semantic_review = json.loads(review_text)
            except json.JSONDecodeError:
                semantic_review = {
                    "final_decision": "FAIL",
                    "brief_explanation": "Invalid JSON from semantic reviewer",
                    "raw_output": review_text
                }

        if semantic_review is not None and semantic_review['final_decision'] == 'FAIL':
            semantic_alert = semantic_review['brief_explanation']
        else:
            semantic_alert = None

        return {
            "accepted": final_hard["accepted"] and final_soft["accepted"],
            "strategy": strategy.value,
            "original_cefr": original_cefr_level,
            "target_cefr": self.target_cefr,
            "final_hard_tests": final_hard,
            "final_soft_tests": final_soft,
            "soft_relaxed": final_soft.get("accepted") and bool(final_soft.get("failed_tests")),
            "semantic_alert": semantic_alert,
            "text": simplified_text,
        }

    def _estimate_cefr_level(self) -> str:
        cefr_level_service = CEFRClassifierService(language=self.language)
        return cefr_level_service.classify(self.original_text)['estimated_level']


    def _define_simplification_strategy(self, original_cefr_level: str):
        if ORDER.index(original_cefr_level) <= ORDER.index(self.target_cefr):
            return StrategySimplificationEnum.NOT_NECESSARY
        elif ORDER.index(original_cefr_level) - ORDER.index(self.target_cefr) <= 2:
            return StrategySimplificationEnum.SIMPLE
        else:
            return StrategySimplificationEnum.IN_STAGES

    def _generate_with_retry(
            self,
            text: str,
            target_cefr: str,
            max_retries: int = 2
    ) -> str:

        llm_generator_service = LLMGeneratorService(
            language=self.language,
            original_text=text,
            target_cefr=target_cefr
        )

        output = llm_generator_service.generate()

        nlp_tests_service = NLPTestsService(
            language=self.language,
            target_level=target_cefr
        )

        retries = 0

        while retries < max_retries:
            hard_results = nlp_tests_service.run_hard_constraints_tests(output)

            if not hard_results["accepted"]:
                invalid_words = self._get_invalid_words_from_tests(hard_results)

                feedback = (
                    f"The text contains words above CEFR {target_cefr}: "
                    f"{', '.join(invalid_words)}. \n"
                    f"Rewrite the text without using these words."
                )

            else:
                soft_results = nlp_tests_service.run_soft_constraints_tests(output)
                if soft_results["accepted"]:
                    return output
                feedback = self._build_soft_feedback(soft_results, target_cefr)
                if not feedback:
                    feedback = (
                        f"Simplify the text slightly to better match CEFR {target_cefr}.\n"
                    )

            llm_generator_service.previous_simplification = output
            llm_generator_service.feedback = feedback
            output = llm_generator_service.regenerate()

            retries += 1

        return output


    @staticmethod
    def _get_invalid_words_from_tests(test_results) -> list:
        invalid_words = []
        failed_tests = test_results['failed_tests']
        if failed_tests:
            for test in failed_tests:
                if test == 'cefr_validity':
                    cefr_validity = failed_tests[test]
                    for word in cefr_validity['details']['flagged_words']:
                        invalid_words.append(word['word'])
                elif test == 'oov':
                    oov = failed_tests[test]
                    for word in oov['details']['oov_words']:
                        invalid_words.append(word)
            return invalid_words
        return []


    def _generate_simple_simplification(self) -> str:
        simplification = ""
        text_chunks = utils.chunk_text_by_words(self.original_text)

        for text_chunk in text_chunks:
            simplification += self._generate_with_retry(
                text=text_chunk,
                target_cefr=self.target_cefr
            )

        return simplification


    def _generate_simplification_in_stages(self, original_cefr_level: str) -> str:
        simplification = self.original_text

        original_index = ORDER.index(original_cefr_level)
        target_index = ORDER.index(self.target_cefr)

        for index in range(original_index - 1, target_index - 1, -1):
            intermediate_target_cefr = ORDER[index]

            text_chunks = utils.chunk_text_by_words(simplification)
            new_simplification = ""

            for text_chunk in text_chunks:
                new_simplification += self._generate_with_retry(
                    text=text_chunk,
                    target_cefr=intermediate_target_cefr
                )

            simplification = new_simplification

        return simplification

    def _build_soft_feedback(self, soft_results, target_cefr: str):
        messages = []

        failed = soft_results.get("failed_tests", {})

        if "clause_count" in failed:
            details = failed["clause_count"]["details"]

            max_clauses = details.get("max_clauses_per_sentence")
            threshold = details.get("threshold")
            sentences = details.get("sentences", [])

            if max_clauses > threshold + 1:
                worst = sentences[0]
                messages.append(
                    f"The following sentence has {worst['clauses']} clauses, "
                    f"but CEFR {target_cefr} allows at most {threshold}:\n"
                    f"\"{worst['text']}\"\n"
                    f"Rewrite it as multiple very short sentences, each with one idea only."
                )

        if "lexical_rarity" in failed:
            details = failed["lexical_rarity"]["details"]
            rare_words = details.get("top_rare_words", [])

            if rare_words:
                words = ", ".join(w["word"] for w in rare_words)
                messages.append(
                    f"The following words are too rare for CEFR {target_cefr}: "
                    f"{words}. Replace them with very common, everyday words."
                )

        if "average_word_length" in failed:
            details = failed["average_word_length"]["details"]
            long_words = details.get("long_words", [])

            if long_words:
                words = ", ".join(long_words)
                messages.append(
                    f"The following words are too long for CEFR {target_cefr}: "
                    f"{words}. Replace them with shorter, simpler words."
                )

        if "morphological_complexity" in failed:
            details = failed["morphological_complexity"]["details"]
            complex_words = details.get("complex_words", [])

            if complex_words:
                words = ", ".join(w["word"] for w in complex_words)
                messages.append(
                    f"The following words are morphologically complex for CEFR {target_cefr}: "
                    f"{words}. Replace them with simpler word forms."
                )

        if not messages:
            return None
        return "\n\n".join(messages)





