from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import LLMReviewerInterface
from config import settings
from http import HTTPStatus
import requests

reviewer_controller = Blueprint('reviewer_controller', __name__)

@reviewer_controller.route("/review", methods=["POST"])
@validate()
def review_simplify(body: LLMReviewerInterface):
    response = requests.post(settings.llm_models_service_url,
                             json={
                            "model": "lexigrade-reviewer",
                            "prompt": f"""
                                        Original sentence: '{body.original_text}'
                                        Simplified sentence: '{body.simplified_text}'
                                        Review the simplified sentence and provide feedback on whether it meets the CEFR level target of '{body.cefr_level_target}'
                                        Give the final answer: approved or rejected simplification.
                                        """,
                            "stream": False
                            }
                             )
    if response.ok:
        return response.json(), HTTPStatus.OK
    return response.json(), HTTPStatus.INTERNAL_SERVER_ERROR


# @reviewer_controller.route("/regenerate", methods=["POST"])
# @validate()
# def regenerate_simplify(body: LLMRegeneratorInterface):
#     response = requests.post(settings.generator_service_url,
#                       json={
#                             "model": "lexigrade-generator",
#                             "prompt": f"""
#                                         Your previous simplification: '{body.previous_simplification}' failed to meet the CEFR level target of '{body.cefr_level_target}' because: {body.feedback}
#                                         Please provide a new simplification for the following sentence that meets the CEFR level target of '{body.cefr_level_target}': '{body.text}'""",
#                             "stream": False
#                             }
#                       )
#     if response.ok:
#         return response.json(), HTTPStatus.OK
#     return response.json(), HTTPStatus.INTERNAL_SERVER_ERROR