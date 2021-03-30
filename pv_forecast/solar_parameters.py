from datetime import time
import pandas as pd
import pvlib
from pvlib.irradiance import erbs, disc, dirindex

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
    
    def calc_dni_disc(self, time_range, ghi, mypressure=101325):
        dni = disc(ghi=ghi, solar_zenith=self.solpos.zenith, datetime_or_doy=time_range)
        return dni

    def calc_dni_dirindex(self, time_range, ghi, mypressure=101325, dew_point=None):
        dni = dirindex(dni_clearsky=self.clearsky.dni, ghi_clearsky=self.clearsky.ghi, ghi=ghi,
                times=time_range, pressure=mypressure, zenith=self.solpos.zenith, temp_dew=dew_point)
        return dni

    def calc_dhi_erbs(self, time_range, ghi):
        dhi = erbs(ghi=ghi, zenith=self.solpos.zenith, datetime_or_doy=time_range)
        return dhi

if __name__ ==  "__main__":

    wp = Solar_Processing(51.2, 6.8, 90, 'utc')
    time_range = pd.date_range(start="2021-03-29 04:00", end="2021-03-29 18:00", freq='1h', tz='utc')

    wp.process_weather_data(time_range)