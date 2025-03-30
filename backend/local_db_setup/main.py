from bike_scraper import BikeScraper
from weather_scraper import WeatherScraper
from db_setup import DBSetUp

if __name__ == "__main__":
    # Initialize the database setup (commenting out the execution to avoid re-running setup every time)
    db_set_up = DBSetUp()
    db_set_up.run() # This will create necessary tables and perform initial setup if needed.

    # Initialize and run the bike scraper to fetch and store bike station availability data
    bs = BikeScraper()
    bs.run()

    # Initialize and run the weather scraper to fetch and store weather data for bike stations
    ws = WeatherScraper()
    ws.run()
