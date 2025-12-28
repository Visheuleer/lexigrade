from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import OrchestratorInterface
from api.services import OrchestratorService
from http import HTTPStatus

orchestrator_controller = Blueprint('orchestrator_controller', __name__)

@orchestrator_controller.route("/execute", methods=["POST"])
@validate()
def execute_flow(body: OrchestratorInterface):
    flow = OrchestratorService(language=body.language, original_text=body.original_text, target_cefr=body.cefr_level_target)
    return flow.execute_flow(), HTTPStatus.OK
