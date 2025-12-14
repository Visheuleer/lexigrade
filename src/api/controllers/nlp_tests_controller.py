from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import NLPTests
from services.nlp_tests import LexicalComplexityTests, LexicalRarityTest, SyntacticComplexityTests, evaluate_hard_constraints, evaluate_soft_constraints
from http import HTTPStatus

nlp_tests_controller = Blueprint('nlp_tests_controller', __name__)

@nlp_tests_controller.route("/hard-constraints/execute", methods=["POST"])
@validate()
def execute_hard_constraints_tests(body: NLPTests):
    complexity_tester = LexicalComplexityTests(language=body.language, target_level=body.cefr_level_target)

    results = {
        "cefr_validity":
            complexity_tester.check_cefr_validity(body.simplified_text),

        "oov":
            complexity_tester.check_oov(body.simplified_text),

        'difficult_word_ratio':
            complexity_tester.check_difficult_word_ratio(body.simplified_text)
    }
    decision = evaluate_hard_constraints(results)
    return decision, HTTPStatus.OK


@nlp_tests_controller.route("/soft-constraints/execute", methods=["POST"])
@validate()
def execute_soft_constraints_tests(body: NLPTests):
     complexity_tester = LexicalComplexityTests(language=body.language, target_level=body.cefr_level_target)
     rarity_tester = LexicalRarityTest(language=body.language, target_level=body.cefr_level_target)
     syntactic_tester = SyntacticComplexityTests(language=body.language, target_level=body.cefr_level_target)

     results = {
         "morphological_complexity":
             complexity_tester.check_morphological_complexity(body.simplified_text),

         "lexical_rarity":
             rarity_tester.calculate(body.simplified_text),

         "clause_count":
                syntactic_tester.check_clause_count(body.simplified_text),

         "average_word_length":
                syntactic_tester.check_average_word_length(body.simplified_text)
     }
     decision = evaluate_soft_constraints(results, min_pass_ratio=0.6)
     return decision, HTTPStatus.OK
