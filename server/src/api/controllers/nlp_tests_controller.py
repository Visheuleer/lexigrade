from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import NLPTests
from api.services import NLPTestsService
from http import HTTPStatus

nlp_tests_controller = Blueprint('nlp_tests_controller', __name__)

@nlp_tests_controller.route("/hard-constraints/execute", methods=["POST"])
@validate()
def execute_hard_constraints_tests(body: NLPTests):
    nlp_tests = NLPTestsService(language=body.language, target_level=body.cefr_level_target)
    decision = nlp_tests.run_hard_constraints_tests(body.simplified_text)
    return decision, HTTPStatus.OK


@nlp_tests_controller.route("/soft-constraints/execute", methods=["POST"])
@validate()
def execute_soft_constraints_tests(body: NLPTests):
    nlp_tests = NLPTestsService(language=body.language, target_level=body.cefr_level_target)
    decision = nlp_tests.run_soft_constraints_tests(body.simplified_text, min_pass_ratio=0.6)
    return decision, HTTPStatus.OK
