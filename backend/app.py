from flask import Flask, send_from_directory, render_template_string
from dotenv import load_dotenv
from flask_cors import CORS
import os
from services import close_db, load_model
from routes import register_blueprints  # Import the function that registers Blueprints

# Load environment variables
load_dotenv()

# Global variable to store the model in memory
bike_model = None
stand_model = None

app = Flask(__name__, static_folder='../frontend/static')
CORS(app)
register_blueprints(app) # Register Blueprints

# Load the model only once when the server starts
with app.app_context():
    load_model()

# Serve the frontend (HTML, JS, CSS) from Flask
@app.route("/")
def index():
    # Read the HTML file as a template
    # index_path = os.path.join("../frontend", 'index.html')
    with open("../frontend/index.html", encoding='utf-8') as f:
        index_html = f.read()

    # Replace placeholder with actual base URL from environment variable
    base_url = os.getenv("BASE_URL")
    rendered_html = index_html.replace("{{ BASE_URL }}", base_url)

    return render_template_string(rendered_html)

# Ensure database connections are properly closed
@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
