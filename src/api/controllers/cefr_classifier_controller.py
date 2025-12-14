from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import CEFRClassifier
from services.cefr_classifier import CEFREstimationService
from http import HTTPStatus

cefr_classifier_controller = Blueprint('cefr_classifier_controller', __name__)

@cefr_classifier_controller.route("/estimate", methods=["POST"])
@validate()
def estimate_cefr(body: CEFRClassifier):
    cefr_classifier = CEFREstimationService(language=body.language)
    result = cefr_classifier.estimate(body.text)
    return result, HTTPStatus.OK

