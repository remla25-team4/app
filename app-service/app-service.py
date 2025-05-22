from flask import Flask, request, jsonify, send_from_directory
from prometheus_flask_exporter import PrometheusMetrics
import os
import requests
from dotenv import load_dotenv
import random
from lib_version import *
import importlib.util
init_path = os.path.join(os.path.dirname(__file__), "__init__.py")
spec = importlib.util.spec_from_file_location("init_module", init_path)
init_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(init_module)

load_dotenv()

app = Flask(__name__, static_folder='../app-frontend/dist')
metrics = PrometheusMetrics(app)

PORT = int(os.environ.get("PORT", 3001))
MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL", "http://host.docker.internal:8080")
vu = VersionUtil()
LIBVERSION = vu.get_package_version()

metrics.info('app_info', 'Application info', version=LIBVERSION)

wrong_prediction_counter = metrics.counter(
    'wrong_prediction_counter', 'Number of wrong sentiment predictions',
    labels={
        'predicted_sentiment': lambda: request.json.get('sentiment'),
        'actual_sentiment': lambda: 'negative' if request.json.get('sentiment') == 'positive' else 'positive',
        'review_length': lambda: lenn(request.json.get('text'))
    }
)

prediction_requests_gauge = metrics.gauge(
    'active_prediction_requests', 'Number of active prediction requests'
)

failed_prediction_requests = metrics.counter(
    'failed_prediction_requests', 
    'Number of failed requests to the reviews POST endpoint',
    labels={'error_type': lambda: 'unknown'}
)

reviews = [
    {
        "id": 1,
        "text": "What a lovely restaurant!",
        "sentiment": "positive"
    }
]

def generate_id():
    return random.randint(1, 5000)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if path == 'metrics':
        abort(404) 
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/reviews', methods=["GET"])
def get_reviews():
    return jsonify(reviews)

@app.route('/api/versions', methods=["GET"])
def get_versions():
    modelVersion = requests.get(f"{MODEL_SERVICE_URL}/version")
    versions = (
        {
            "modelVersion": modelVersion.json()["version"],
            "appVersion": init_module.__version__,
            "libVersion": LIBVERSION
        }
    )
    return jsonify(versions)

@app.route('/api/reviews', methods=["POST"])
def add_review():
    prediction_requests_gauge.inc()
    try:
        body = request.json
        
        model_response = requests.post(f"{MODEL_SERVICE_URL}/predict", 
                                      json={"text": body["text"]})
        model_response.raise_for_status()
        
        new_review = {
            "id": generate_id(),
            "text": body["text"],
            "sentiment": model_response.json()["prediction"]
        }
        
        reviews.append(new_review)
        
        return jsonify(new_review)
        
    except requests.exceptions.RequestException as error:
        failed_prediction_requests.labels(error_type='model_service').inc()
        print(f"Error connecting to model service: {str(error)}")
        return jsonify({"error": "Failed to connect to model service"}), 500
    except Exception as error:
        failed_prediction_requests.labels(error_type='server').inc()
        print(f"Unexpected error: {str(error)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    finally:
         prediction_requests_gauge.dec()

@app.route('/api/feedback', methods=["POST"])
@wrong_prediction_counter
def send_feedback():
    #just send success status for now until model service is setup to do something with it
    body = request.json
    return jsonify({"message": "Feedback received successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)