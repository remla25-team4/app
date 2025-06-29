from flask import Flask, request, jsonify, send_from_directory, abort, Response
from prometheus_client import Counter, Gauge, Info, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import requests
from dotenv import load_dotenv
import random
from lib_version import *
import importlib.util
import time


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

total_prediction_requests = Counter(
    'total_prediction_requests',
    'Total amount of requests to the reviews POST endpoint',
    ['sentiment']
)

time_to_click = Histogram(
    'time_to_click_seconds',
    'Time between page load and button click reported by frontend',
    ['version']
)

prediction_request_latency = Histogram(
    "prediction_request_latency",
    "Time spent running the restaurant-sentiment model",
    ["status"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2)
)

# Initialize metrics
failed_prediction_requests.labels(error_type='model_service').inc(0)
failed_prediction_requests.labels(error_type='server').inc(0)

total_prediction_requests.labels(sentiment='positive').inc(0)
total_prediction_requests.labels(sentiment='negative').inc(0)

wrong_prediction_counter.labels(
    predicted_sentiment="positive",
    actual_sentiment="negative",
    review_length="0"
).inc(0)
wrong_prediction_counter.labels(
    predicted_sentiment="negative",
    actual_sentiment="positive",
    review_length="0"
).inc(0)

prediction_requests_gauge.set(0)

time_to_click.labels(version='main').observe(0)
time_to_click.labels(version='canary').observe(0)

prediction_request_latency.labels(status='success').observe(0)
prediction_request_latency.labels(status='error').observe(0)

reviews = [
    {
        "id": 1,
        "text": "What a lovely restaurant!",
        "sentiment": "positive"
    }
]

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
        start_time = time.time()
        body = request.json
        
        model_response = requests.post(f"{MODEL_SERVICE_URL}/predict", 
                                      json={"text": body["text"]})
        model_response.raise_for_status()

        elapsed_time = time.time() - start_time
        prediction_request_latency.labels(status="success").observe(elapsed_time)
        total_prediction_requests.labels(sentiment=model_response.json()["prediction"]).inc()

        new_review = {
            "id": generate_id(),
            "text": body["text"],
            "sentiment": model_response.json()["prediction"]
        }
        
        reviews.append(new_review)
        
        return jsonify(new_review)
        
    except requests.exceptions.RequestException as error:
        failed_prediction_requests.labels(error_type='model_service').inc()
        elapsed_time = time.time() - start_time
        prediction_request_latency.labels(status="error").observe(elapsed_time)
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
    elapsed_time = body.get("time")
    version = body.get("version")

    if elapsed_time is not None:
        try:
            elapsed_seconds = float(elapsed_time)
            if(version == "main"):
                time_to_click.labels(version='main').observe(elapsed_seconds)
            else:
                time_to_click.labels(version='canary').observe(elapsed_seconds)

            return jsonify({"message": f"{version} Time recorded - {elapsed_seconds}"}), 200
        except ValueError:
            return jsonify({"error": "Invalid elapsedTime format"}), 400
    else:
        return jsonify({"error": "elapsedTime not provided"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)