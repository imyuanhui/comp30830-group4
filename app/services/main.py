from bike_scraper import BikeScraper
from weather_scraper import WeatherScraper
from db_setup import DBSetUp
import time

if __name__ == "__main__":
    
    # Note: DBSetUp() will drop the table if exists and recreate with the latest SQL
    # So after setting up the database, remember to remark the code
    # db_set_up = DBSetUp()
    # db_set_up.run()
    
    ws = WeatherScraper()
    bs = BikeScraper()
    
    last_weather_time = 0
    last_bike_time = 0

    while True:
        current_time = time.time()

        # Run WeatherScraper every hour (3600 seconds)
        if current_time - last_weather_time >= 3600:
            ws.run()
            print('run weather scraper')
            last_weather_time = current_time

        # Run BikeScraper every 5 minutes (300 seconds)
        if current_time - last_bike_time >= 300:
            bs.run()
            print('run bike scraper')
            last_bike_time = current_time

        time.sleep(10)  # Small sleep to reduce CPU usage