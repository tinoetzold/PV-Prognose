import pandas as pd
import pvlib

class Weather_Processing:

    def __init__(self, config) -> None:
        self.mylatitude = config.getfloat("SolarSystem", "Latitude", raw=True)
        self.mylongitude = config.getfloat("SolarSystem", "Longitude", raw=True)
        self.myaltitude = config.getfloat("SolarSystem", "Altitude", raw=True)
        self.mytimezone = config.get("SolarSystem", "MyTimezone", raw=True)
        self.solpos = None

        # Set up location object:
        self.location = pvlib.location.Location(longitude=self.mylongitude,
                                                latitude=self.mylatitude,
                                                altitude=self.myaltitude,
                                                tz=self.mytimezone)

    def process_weather_data(self, start_time, end_time):
        pass
    
    def get_clearsky_weather(self, time_range):
        return self.location.get_clearsky(time_range, model='ineichen')