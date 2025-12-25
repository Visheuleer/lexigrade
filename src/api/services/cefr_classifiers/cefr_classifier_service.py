from api.services.cefr_classifiers.supervised_cefr_classifier import SupervisedCEFREstimationService
from api.services.cefr_classifiers.nlp_cefr_classifier import NLPBasedCEFRClassifier

class CEFRClassifierService:
    def __init__(self, language: str):
        if language == "english":
            self.classifier = SupervisedCEFREstimationService(language=language)
        else:
            self.classifier = NLPBasedCEFRClassifier(language=language)

    def classify(self, sentence: str):
        return self.classifier.estimate(sentence)