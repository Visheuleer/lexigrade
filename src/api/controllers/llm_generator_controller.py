from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import LLMGeneratorInterface, LLMRegeneratorInterface
from config import settings
from http import HTTPStatus
import requests

generator_controller = Blueprint('genarator_controller', __name__)

@generator_controller.route("/generate", methods=["POST"])
@validate()
def generate_simplify(body: LLMGeneratorInterface):
    response = requests.post(settings.llm_models_service_url,
                             json={
                            "model": "lexigrade-generator",
                            "prompt": f"CEFR TARGET: {body.cefr_level_target}. Sentence: {body.text}",
                            "stream": False
                            }
                             )
    if response.ok:
        return response.json(), HTTPStatus.OK
    return response.json(), HTTPStatus.INTERNAL_SERVER_ERROR


@generator_controller.route("/regenerate", methods=["POST"])
@validate()
def regenerate_simplify(body: LLMRegeneratorInterface):
    response = requests.post(settings.llm_models_service_url,
                             json={
                            "model": "lexigrade-generator",
                            "prompt": f"""
                                        Your previous simplification: '{body.previous_simplification}' failed to meet the CEFR level target of '{body.cefr_level_target}' because: {body.feedback}
                                        Please provide a new simplification for the following sentence that meets the CEFR level target of '{body.cefr_level_target}': '{body.text}'""",
                            "stream": False
                            }
                             )
    if response.ok:
        return response.json(), HTTPStatus.OK
    return response.json(), HTTPStatus.INTERNAL_SERVER_ERROR