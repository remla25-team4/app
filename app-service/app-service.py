from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv
import random

load_dotenv()

app = Flask(__name__, static_folder='../app-frontend/dist')

PORT = int(os.environ.get("PORT", 3001))
MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL", "http://host.docker.internal:8080")
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
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/reviews', methods=["GET"])
def get_reviews():
    return jsonify(reviews)

@app.route('/api/reviews', methods=["POST"])
def add_review():
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
        print(f"Error connecting to model service: {str(error)}")
        return jsonify({"error": "Failed to connect to model service"}), 500
    except Exception as error:
        print(f"Unexpected error: {str(error)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)