import configparser
from pv_forecast.dwd_forecast import DWD_Forecast
from pv_forecast.weather_processing import Weather_Processing

def main():
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    
    dwd_fc = DWD_Forecast(config.get("DWD", "DWDStation", raw=True))
    
    mylatitude = config.getfloat("SolarSystem", "Latitude", raw=True)
    mylongitude = config.getfloat("SolarSystem", "Longitude", raw=True)
    myaltitude = config.getfloat("SolarSystem", "Altitude", raw=True)
    mytimezone = config.get("SolarSystem", "MyTimezone", raw=True)

    weather = Weather_Processing()

if __name__ == "__main__":
    pass