from bike_scraper import BikeScraper
from weather_scraper import WeatherScraper
from db_setup import DBSetUp

if __name__ == "__main__":
    
    # Note: DBSetUp() will drop the table if exists and recreate with the latest SQL
    # So after setting up the database, remember to remark the code
    db_set_up = DBSetUp()
    db_set_up.run()
    
    ws = WeatherScraper()
    ws.run()

    bs = BikeScraper()
    bs.run()