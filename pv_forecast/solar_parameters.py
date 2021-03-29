import pandas as pd
import pvlib

class Solar_Processing:

    def __init__(self, latitude: float, longitude: float, altitude: float, timezone: str) -> None:
        self.mylatitude = latitude
        self.mylongitude = longitude
        self.myaltitude = altitude
        self.mytimezone = timezone
        self.solpos = None
        self.clearsky = None

        # Set up location object:
        self.location = pvlib.location.Location(longitude=self.mylongitude,
                                                latitude=self.mylatitude,
                                                altitude=self.myaltitude,
                                                tz=self.mytimezone)

    def process_weather_data(self, time_range):
        
        self.clearsky = self.get_clearsky_weather(time_range)
        self.solpos = self.get_solar_postition(time_range)
    
    def get_clearsky_weather(self, time_range):
        """ Determine clearsky irradiation conditions. """
        return self.location.get_clearsky(time_range, model='ineichen')

    def get_solar_postition(self, time_range):
        """ Get the sun position within the given time range. """
        solpos = pvlib.solarposition.get_solarposition(time = time_range,
                                                        latitude=self.mylatitude, 
                                                        longitude=self.mylongitude, 
                                                        altitude=self.myaltitude)
        return solpos


if __name__ ==  "__main__":

    wp = Solar_Processing(51.2, 6.8, 90, 'utc')
    time_range = pd.date_range(start="2021-03-29 04:00", end="2021-03-29 18:00", freq='1h', tz='utc')

    wp.process_weather_data(time_range)