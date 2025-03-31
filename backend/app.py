from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
import os
from services import close_db
from routes import register_blueprints  # Import the function that registers Blueprints

# Load environment variables
load_dotenv()

app = Flask(__name__)
# CORS(app)
CORS(app, origins=["http://127.0.0.1:3000"])
register_blueprints(app) # Register Blueprints

# Ensure database connections are properly closed
@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
