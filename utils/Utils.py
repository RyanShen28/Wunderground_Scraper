import config
from datetime import timedelta, date
import lxml.html as lh

class Utils:
    weather_station_url = None


    def __init__(self, weather_station_url):
        self.weather_station_url = weather_station_url
        
    @classmethod
    def date_range(cls, start, end = date.today()):
        for i in range(int ((end - start).days) + 1):
            yield start + timedelta(i)

    @classmethod
    def date_url_generator(cls, weather_station_url, start_date, end_date = date.today()):
        date_range = Utils.date_range(start_date, end_date)
        for date in date_range:

            date_string = "{}-{}-{}".format (date.year, date.month, date.day)

            url = f'{weather_station_url}/{date_string}'

            yield date_string, url



