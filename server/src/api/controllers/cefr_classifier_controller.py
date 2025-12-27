from flask import Blueprint
from flask_pydantic import validate
from api.interfaces import CEFRClassifier
from api.services import CEFRClassifierService
from http import HTTPStatus

cefr_classifier_controller = Blueprint('cefr_classifier_controller', __name__)

@cefr_classifier_controller.route("/estimate", methods=["POST"])
@validate()
def estimate_cefr(body: CEFRClassifier):
    cefr_classifier = CEFRClassifierService(language=body.language)

    result = cefr_classifier.classify(body.text)
    return result, HTTPStatus.OK

