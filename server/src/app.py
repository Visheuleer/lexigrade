from flask import Flask
from flask_cors import CORS
from api.controllers import generator_controller, reviewer_controller, nlp_tests_controller, cefr_classifier_controller, main_controller


app = Flask(__name__)
CORS(app)
app.register_blueprint(generator_controller, url_prefix="/llm-generator")
app.register_blueprint(reviewer_controller, url_prefix="/llm-reviewer")
app.register_blueprint(nlp_tests_controller, url_prefix="/nlp-tests")
app.register_blueprint(cefr_classifier_controller, url_prefix="/cefr-classifier")
app.register_blueprint(main_controller, url_prefix="/main")

@app.route("/")
def home():
    return "App is running."



if __name__ == "__main__":
    app.run(debug=True)