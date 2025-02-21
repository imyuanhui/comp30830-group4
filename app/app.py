from flask import Flask
from dotenv import load_dotenv
import os
from db_config import close_db
from routes import register_blueprints  # Import the function that registers Blueprints

# Load environment variables
load_dotenv()

app = Flask(__name__)
register_blueprints(app) # Register Blueprints

# Ensure database connections are properly closed
@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

if __name__ == "__main__":
    app.run(debug=True)
