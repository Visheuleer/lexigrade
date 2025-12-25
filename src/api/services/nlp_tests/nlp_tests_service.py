from api.services.nlp_tests.lexical_complexity import LexicalComplexityTests
from api.services.nlp_tests.lexical_rarity import LexicalRarityTest
from api.services.nlp_tests.syntactic_complexity import SyntacticComplexityTests
from api.services.nlp_tests.constraints_evaluator import evaluate_hard_constraints, evaluate_soft_constraints


class NLPTestsService:
    def __init__(self, language: str, target_level: str):
        self.language = language
        self.target_level = target_level
        self.lexical_complexity_tester = LexicalComplexityTests(language=language, target_level=target_level)
        self.lexical_rarity_tester = LexicalRarityTest(language=language, target_level=target_level)
        self.syntactic_complexity_tester = SyntacticComplexityTests(language=language, target_level=target_level)


    def run_hard_constraints_tests(self, text: str) -> dict:
        result = {
            "cefr_validity": self.lexical_complexity_tester.check_cefr_validity(text),
            "oov": self.lexical_complexity_tester.check_oov(text),
            "difficult_word_ratio": self.lexical_complexity_tester.check_difficult_word_ratio(text)
        }
        return evaluate_hard_constraints(result)


    def run_soft_constraints_tests(self, text: str) -> dict:
        result = {
            "morphological_complexity": self.lexical_complexity_tester.check_morphological_complexity(text),
            "lexical_rarity": self.lexical_rarity_tester.calculate(text),
            "clause_count": self.syntactic_complexity_tester.check_clause_count(text),
            "average_word_length": self.syntactic_complexity_tester.check_average_word_length(text)
        }
        return evaluate_soft_constraints(result)