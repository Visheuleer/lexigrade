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
                                        Original sentence: '{body.original_text}'\n
                                        Simplified sentence: '{body.simplified_text}'
                                        """,
                            "stream": False
                            }
                             )
    if response.ok:
        return response.json(), HTTPStatus.OK
    return response.json(), HTTPStatus.INTERNAL_SERVER_ERROR