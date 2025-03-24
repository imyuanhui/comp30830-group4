from bike_scraper import BikeScraper
from weather_scraper import WeatherScraper
from db_setup import DBSetUp
from datetime import datetime
import time


def get_next_5_minute_time():
    now = datetime.now()
    next_minute = (now.minute // 5 + 1) * 5
    if next_minute >= 60:
        next_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
    else:
        next_time = now.replace(minute=next_minute, second=0, microsecond=0)
    return next_time


if __name__ == "__main__":
    # Note: DBSetUp() will drop the table if exists and recreate with the latest SQL
    # So after setting up the database, remember to remark the code
    db_set_up = DBSetUp()
    db_set_up.run()

    last_weather_time = 0
    last_bike_time = 0

    bs = BikeScraper()
    bs.run()
    
    # while True:
    #     now = datetime.now()
    #     if now.minute % 5 == 0:
    #         bs = BikeScraper()
    #         bs.run()

    #     # No need to save weather info for this project
    #     # if now.minute == 0:
    #     #     ws = WeatherScraper()
    #     #     ws.run()
    #     #     run_hour = now.hour

    #     next_minute = (now.minute // 5 + 1) * 5
    #     wait_seconds = next_minute * 60 - now.minute * 60 - now.second

    #     time.sleep(wait_seconds)
