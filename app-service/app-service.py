from flask import Flask, request, jsonify, send_from_directory, abort, Response
from prometheus_client import Counter, Gauge, Info, Histogram, generate_latest, CONTENT_TYPE_LATEST
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

app = Flask(__name__, static_folder='../app-frontend/dist', static_url_path='')

PORT = int(os.environ.get("PORT", 3001))
MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL", "http://host.docker.internal:8080")
vu = VersionUtil()
LIBVERSION = vu.get_package_version()

app_info = Info('app_info', 'Application info')
app_info.info({'version': LIBVERSION})

##### METRICS ###### 

wrong_prediction_counter = Counter(
    'wrong_prediction_counter', 
    'Number of wrong sentiment predictions',
    ['predicted_sentiment', 'actual_sentiment', 'review_length']
)

prediction_requests_gauge = Gauge(
    'active_prediction_requests', 
    'Number of active prediction requests'
)

failed_prediction_requests = Counter(
    'failed_prediction_requests', 
    'Number of failed requests to the reviews POST endpoint',
    ['error_type']
)

time_to_click = Histogram(
    'time_to_click_seconds',
    'Time between page load and button click reported by frontend'
)

failed_prediction_requests.labels(error_type='model_service').inc(0)
failed_prediction_requests.labels(error_type='server').inc(0)


def generate_id():
    return random.randint(1, 5000)

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/')
def index():
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
def send_feedback():
    #just send success status for now until model service is setup to do something with it
    body = request.json

    predicted_sentiment = body.get('sentiment', 'unknown')
    actual_sentiment = 'negative' if predicted_sentiment == 'positive' else 'positive'
    review_length = str(len(body.get('text', '')))

    wrong_prediction_counter.labels(
        predicted_sentiment=predicted_sentiment,
        actual_sentiment=actual_sentiment,
        review_length=review_length
    ).inc()
    
    return jsonify({"message": "Feedback received successfully"}), 200


@app.route('/api/time-to-click', methods=["POST"])
def record_time_to_click():
    body = request.json
    elapsed_time = body.get("elapsedTime")

    if elapsed_time is not None:
        try:
            elapsed_seconds = float(elapsed_time)
            time_to_click.observe(elapsed_seconds)
            return jsonify({"message": "Time recorded"}), 200
        except ValueError:
            return jsonify({"error": "Invalid elapsedTime format"}), 400
    else:
        return jsonify({"error": "elapsedTime not provided"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)