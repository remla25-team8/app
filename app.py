import os
import requests
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from lib_version import VersionUtil
from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge, Histogram

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if app.config.get('DEBUG', False) else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.environ.get("PORT", 8080))
MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL", "http://0.0.0.0:5000")
APP_VERSION = os.environ.get("APP_VERSION", "0.0.0")
MODEL_SERVICE_VERSION = os.environ.get("MODEL_SERVICE_VERSION", "0.0.0")

LIB_VERSION = VersionUtil.get_version()

# Configure Prometheus metrics
metrics = PrometheusMetrics(app, path='/metrics')
metrics.info('app_info', 'Application info', version=APP_VERSION)

# Define custom metrics
sentiment_analysis_requests = Counter(
    'sentiment_analysis_total', 
    'Number of sentiment analysis requests',
    ['sentiment']  # Label to track positive vs negative predictions
)

model_response_time = Histogram(
    'model_response_time_seconds', 
    'Model service response time in seconds',
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5]  # Buckets in seconds
)

active_users = Gauge(
    'active_users', 
    'Number of active users on the application',
    ['page']  # Label to track which page users are on
)

feedback_counter = Counter(
    'user_feedback_total', 
    'Number of feedback submissions',
    ['correct', 'predicted_sentiment', 'actual_sentiment']  # Labels for tracking feedback types
)

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger = Swagger(app, config=swagger_config, template={
    "info": {
        "title": "Restaurant Review Sentiment API - Team 8",
        "description": "API for analyzing sentiment in restaurant reviews",
        "version": APP_VERSION,
    }
})

@app.route("/")
def index():
    """Display the main application page."""
    active_users.labels(page='index').inc()
    return render_template("index.html", 
        app_version=APP_VERSION,
        lib_version=LIB_VERSION,
        model_service_version=MODEL_SERVICE_VERSION,
    )

@app.route("/info")
def info():
    """
    Get version information
    ---
    tags:
      - System
    responses:
      200:
        description: Version information
        schema:
          type: object
          properties:
            lib_version:
              type: string
              description: Version of the lib_version package
            model_service_version:
              type: string
              description: Version of the model service
            app_version:
              type: string
              description: Version of the app
            model_service_url:
              type: string
              description: URL of the model service
            model_service_info:
              type: object
              description: Information about the model service
    """
    # Get model service info
    active_users.labels(page='info').inc()
    try:
        model_info = requests.get(f"{MODEL_SERVICE_URL}/health", timeout=5).json()
    except requests.RequestException:
        model_info = {"error": "Could not connect to model service"}
    
    return jsonify({
        "lib_version": LIB_VERSION,
        "model_service_version": MODEL_SERVICE_VERSION,
        "app_version": APP_VERSION,
        "model_service_url": MODEL_SERVICE_URL,
        "model_service_info": model_info
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze sentiment of a restaurant review
    ---
    tags:
      - Sentiment Analysis
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - review
          properties:
            review:
              type: string
              example: "The restaurant was fantastic!"
    responses:
      200:
        description: Sentiment analysis result
        schema:
          type: object
          properties:
            sentiment:
              type: string
              description: Predicted sentiment (positive or negative)
            prediction:
              type: integer
              description: Numeric prediction (0 for negative, 1 for positive)
            review:
              type: string
              description: Original review text
      400:
        description: Bad request (e.g., missing review field)
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.get_json()
    logger.debug(f"Received data: {data}")
    active_users.labels(page='analyze').inc()
    
    if not data or "review" not in data:
        return jsonify({
            "error": "Missing 'review' field in request"
        }), 400
    
    review = data["review"]
    
    # Call model service
    try:
        with model_response_time.time():
            response = requests.post(
                f"{MODEL_SERVICE_URL}/predict",
                json={"review": review},
                timeout=5
            )
        
        if response.status_code == 200:
            result = response.json()
            sentiment = 'positive' if result.get('prediction', 0) == 1 else 'negative'
            sentiment_analysis_requests.labels(sentiment=sentiment).inc()
            return jsonify(result), 200
        else:
            return jsonify({
                "error": f"Model service returned error: {response.text}"
            }), 500
    
    except requests.RequestException as e:
        return jsonify({
            "error": f"Could not connect to model service: {str(e)}"
        }), 500

@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Submit feedback for an incorrect prediction
    ---
    tags:
      - Feedback
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - review
            - prediction
            - actual_sentiment
          properties:
            review:
              type: string
              example: "The restaurant was fantastic!"
            prediction:
              type: integer
              example: 1
              description: The model's prediction (0 or 1)
            actual_sentiment:
              type: integer
              example: 0
              description: The correct sentiment (0 or 1)
    responses:
      200:
        description: Feedback received
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
    """
    data = request.get_json()
    # In a real app, you would store this feedback for model improvement
    # For this demo, we'll just log it
    print(f"Feedback received: {data}")
    active_users.labels(page='feedback').inc()
    
    # Track feedback metrics
    review = data.get("review", "")
    prediction = data.get("prediction", -1)
    actual_sentiment = data.get("actual_sentiment", -1)
    
    # Determine if prediction was correct
    correct = "true" if prediction == actual_sentiment else "false"
    predicted_sentiment = "positive" if prediction == 1 else "negative"
    actual = "positive" if actual_sentiment == 1 else "negative"
    
    feedback_counter.labels(
        correct=correct,
        predicted_sentiment=predicted_sentiment,
        actual_sentiment=actual
    ).inc()
    
    return jsonify({
        "status": "success",
        "message": "Feedback received"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)