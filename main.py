import configparser
from pv_forecast.dwd_forecast import DWD_Forecast
from pv_forecast.solar_parameters import Solar_Processing

def main():
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    
    # Initialize class for retrieving DWD Data:
    dwd_fc = DWD_Forecast(config.get("DWD", "DWDStation", raw=True))
    
    # Initialize class for getting basic solar parameters:
    mylatitude = config.getfloat("SolarSystem", "Latitude", raw=True)
    mylongitude = config.getfloat("SolarSystem", "Longitute", raw=True)
    myaltitude = config.getfloat("SolarSystem", "Altitude", raw=True)
    mytimezone = config.get("SolarSystem", "MyTimezone", raw=True)

    # Solar parameter processing:
    solar_proc = Solar_Processing(myaltitude, mylongitude, myaltitude, mytimezone)

    

    # Now get the latest weather data:
    dwddata = dwd_fc.retrieve_data()

    # Use the time range of the DWD Data as basis for further calculations
    time_range = dwddata.index

    # Now set up the weather data
    solar_proc.process_weather_data(time_range)

if __name__ == "__main__":
    main()