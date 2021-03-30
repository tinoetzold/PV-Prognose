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
    solar_proc = Solar_Processing(mylatitude, mylongitude, myaltitude, mytimezone)

    

    # Now get the latest weather data:
    dwddata = dwd_fc.retrieve_data()
    dwddata = dwddata.loc['2021-03-30 6:00':'2021-03-30 19:00']

    # Use the time range of the DWD Data as basis for further calculations
    time_range = dwddata.index

    # Now set up the weather data
    solar_proc.process_weather_data(time_range)

    # Calc DNI using DISC model:
    dni_disc = solar_proc.calc_dni_disc(time_range=time_range, ghi=dwddata.RAD_WH)

    # Calc DNI using DIRINT model:
    dni_dirint = solar_proc.calc_dni_dirindex(time_range=time_range, ghi=dwddata.RAD_WH, dew_point=dwddata.DEW_POINT_DEGC)
    #print(dni_dirint)

    # Calc DHI using the ERBS model
    dhi_erbs = solar_proc.calc_dhi_erbs(ghi=dwddata.RAD_WH, time_range=time_range)
    #print(dhi_erbs)

    # Build up common dataframe:
    whole_df = dwddata
    whole_df.columns = whole_df.columns.add_categories(["DHI_ERBS", "DNI_DISC", "DNI_DIRINDEX"])
    whole_df["DHI_ERBS"] = dhi_erbs["dhi"]
    whole_df["DNI_DISC"] = dni_disc["dni"]
    whole_df["DNI_DIRINDEX"] = dni_dirint.values

    whole_df.columns = whole_df.columns.add_categories(["GHI_CLEARSKY", "DNI_CLEARSKY", "DHI_CLEARSKY"])
    whole_df["GHI_CLEARSKY"] = solar_proc.clearsky.ghi
    whole_df["DNI_CLEARSKY"] = solar_proc.clearsky.dni
    whole_df["DHI_CLEARSKY"] = solar_proc.clearsky.dhi

    whole_df.to_csv("new.csv")

if __name__ == "__main__":
    main()