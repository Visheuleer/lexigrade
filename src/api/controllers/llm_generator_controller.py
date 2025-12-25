from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import LLMGeneratorInterface, LLMRegeneratorInterface
from api.services import LLMGeneratorService
from http import HTTPStatus


generator_controller = Blueprint('genarator_controller', __name__)

@generator_controller.route("/generate", methods=["POST"])
@validate()
def generate_simplify(body: LLMGeneratorInterface):
    service = LLMGeneratorService(original_text=body.original_text, target_cefr=body.cefr_level_target)
    text = service.generate()
    return {"text": text}, HTTPStatus.OK


@generator_controller.route("/regenerate", methods=["POST"])
@validate()
def regenerate_simplify(body: LLMRegeneratorInterface):
    service = LLMGeneratorService(original_text=body.original_text, target_cefr=body.cefr_level_target,
                                  previous_simplification=body.previous_simplification, feedback=body.feedback)
    text = service.regenerate()
    return {"text": text}, HTTPStatus.OK
