from sqlalchemy import create_engine
from flask import g
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
PORT = os.getenv("DB_PORT")
# DB = os.getenv("DB_NAME")
URI = os.getenv("DB_URI")

# Connect to the database and create the engine
def connect_to_db(db_name):
    connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/{db_name}"
    engine = create_engine(connection_string, echo=True)
    return engine

# Store and reuse the database connection in Flask's 'g'
def get_db(db_name):
    if 'db_engine' not in g:
        g.db_engine = connect_to_db(db_name)
    return g.db_engine

# Close the database connection at the end of each request
def close_db(error=None):
    db_engine = g.pop('db_engine', None)
    if db_engine is not None:
        db_engine.dispose()  # Properly close the connection
