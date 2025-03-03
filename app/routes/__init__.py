# Import individual route modules
from .bikes import bikes_bp
from .weather import weather_bp
from .stations import stations_bp
from .config import config_bp


# Define a function to register Blueprints
def register_blueprints(app):
    app.register_blueprint(bikes_bp, url_prefix="/api")
    app.register_blueprint(weather_bp, url_prefix="/api")
    app.register_blueprint(stations_bp, url_prefix="/api")
    app.register_blueprint(config_bp, url_prefix="/api")
