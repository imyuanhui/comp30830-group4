from flask import Blueprint, jsonify
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Create a Blueprint for configuration-related routes
config_bp = Blueprint("config", __name__)

# Retrieve the Google Maps API Key from environment variables
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


@config_bp.route("/config", methods=["GET"])
def get_google_maps_config():
    """
    API Endpoint: /api/config
    Method: GET

    Description:
    - Provides the Google Maps API Key.
    - The frontend can call this API to dynamically retrieve the API key for loading Google Maps.

    Example Response:
    {
        "GOOGLE_MAPS_API_KEY": "YOUR_API_KEY"
    }

    Returns:
    - 200 OK: JSON object containing the Google Maps API Key.
    """
    return jsonify({"GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY})
