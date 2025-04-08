from flask import Flask, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS
import os
from services import close_db
from routes import register_blueprints  # Import the function that registers Blueprints

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend/static')
CORS(app)
register_blueprints(app) # Register Blueprints

# Serve the frontend (HTML, JS, CSS) from Flask
@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')  # Serve index.html as the main page

# Ensure database connections are properly closed
@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
