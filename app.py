import os
import requests
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from lib_version import VersionUtil
from flasgger import Swagger

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
    
    if not data or "review" not in data:
        return jsonify({
            "error": "Missing 'review' field in request"
        }), 400
    
    review = data["review"]
    
    # Call model service
    try:
        response = requests.post(
            f"{MODEL_SERVICE_URL}/predict",
            json={"review": review},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
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
    
    return jsonify({
        "status": "success",
        "message": "Feedback received"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)