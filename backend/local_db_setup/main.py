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
    db_set_up = DBSetUp() # Comment out the code after initialization
    db_set_up.run()

    last_weather_time = 0
    last_bike_time = 0

    bs = BikeScraper()
    bs.run()

    ws = WeatherScraper()
    ws.run()
