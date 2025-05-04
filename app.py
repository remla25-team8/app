import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from lib_version import get_version

# If you're using version-util, import it here
# from version_util import VersionUtil

load_dotenv()

app = Flask(__name__)

# Configuration
PORT = int(os.environ.get("PORT", 3000))
MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL", "http://localhost:5000")

# If you're using version-util
# TODO: version_util = VersionUtil()
# TODO: APP_VERSION = version_util.get_version()
APP_VERSION = get_version()

@app.route("/")
def index():
    """Display the main application page."""
    return render_template("index.html", app_version=APP_VERSION)

@app.route("/info")
def info():
    """Get version information."""
    # Get model service info
    try:
        model_info = requests.get(f"{MODEL_SERVICE_URL}/info", timeout=5).json()
    except requests.RequestException:
        model_info = {"error": "Could not connect to model service"}
    
    return jsonify({
        "app_version": APP_VERSION,
        "model_service_url": MODEL_SERVICE_URL,
        "model_service_info": model_info
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze a restaurant review.
    
    Expected JSON payload:
    {
        "review": "The restaurant was fantastic!"
    }
    """
    data = request.get_json()
    
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
    Submit feedback for an incorrect prediction.
    
    Expected JSON payload:
    {
        "review": "The restaurant was fantastic!",
        "prediction": 1,
        "actual_sentiment": 0
    }
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
    app.run(host="0.0.0.0", port=PORT, debug=False)