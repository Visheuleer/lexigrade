from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import MainFlowInterface
from api.services import MainFlowService
from http import HTTPStatus

main_controller = Blueprint('main_controller', __name__)

@main_controller.route("/execute", methods=["POST"])
@validate()
def execute_flow(body: MainFlowInterface):
    flow = MainFlowService(language=body.language, original_text=body.original_text, target_cefr=body.cefr_level_target)
    return flow.execute_flow(), HTTPStatus.OK
