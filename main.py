import configparser
import os
from datetime import datetime
import pandas as pd
from pvlib.irradiance import dni
from pv_forecast.dwd_forecast import DWD_Forecast
from pv_forecast.solar_parameters import Solar_Processing
from pv_forecast.pv_system import PVSystem

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
    dwddata = dwddata.loc['2021-04-02 6:00':'2021-04-07 20:00']

    # Use the time range of the DWD Data as basis for further calculations
    time_range = dwddata.index

    # Now set up the weather data
    solar_proc.process_weather_data(time_range)
 
    # Calc DNI using DISC model:
    dni_disc = solar_proc.calc_dni_disc(time_range=time_range, ghi=dwddata.RAD_WH, mypressure=dwddata.PRESSURE_AIR_SURFACE_REDUCED)

    # Calc DNI using DIRINT model:
    dni_dirint = solar_proc.calc_dni_dirindex(time_range=time_range, ghi=dwddata.RAD_WH, dew_point=dwddata.DEW_POINT_DEGC)
    #print(dni_dirint)

    # Calc DHI using the ERBS model
    dhi_erbs = solar_proc.calc_dhi_erbs(ghi=dwddata.RAD_WH, time_range=time_range)
    #print(dhi_erbs)

    # Initiate PV System
    pvlib_location = solar_proc.location
    pv_system = PVSystem(inverter=config.get("SolarSystem", "InverterName", raw=True),
                        pv_module=config.get("SolarSystem", "ModuleName", raw=True),
                        albedo=config.getfloat("SolarSystem", "Albedo", raw=True),
                        pvlib_location=pvlib_location)

    pv_system.add_pv_system(id="Ost",
                            surface_tilt=config.getfloat("SolarSystem", "Elevation", raw=True),
                            surface_azimuth=config.getfloat("SolarSystem", "Azimuth_1", raw=True),
                            modules_per_string=config.getint("SolarSystem", "NumPanels_1", raw=True))

    pv_system.add_pv_system(id="West",
                            surface_tilt=config.getfloat("SolarSystem", "Elevation", raw=True),
                            surface_azimuth=config.getfloat("SolarSystem", "Azimuth_2", raw=True),
                            modules_per_string=config.getint("SolarSystem", "NumPanels_2", raw=True))

    # the following list represents different calculation approaches to determine 
    # several algorithmst to find the best-suiting approach for the calculation
    # model.
    list_of_modes = ["clearsky", "disc", "dirint"]

    calc_data = pd.DataFrame()
    for current_mode in list_of_modes:
        if current_mode == "clearsky":
            # Using Clearsky-Irradiance (no clouds - theoretical model) to compute
            # theoretical generation potential for pv system.
            weather_data = pv_system.setup_weather_data(ghi=solar_proc.clearsky.ghi,
                                                        dhi=solar_proc.clearsky.dhi,
                                                        dni=solar_proc.clearsky.dni,
                                                        temp_air=dwddata.TEMPERATURE_AIR_200DEGC,
                                                        wind_speed=dwddata.WIND_SPEED)
        elif current_mode == "disc":
            # Modue using DWD Forecast for calculation
            weather_data = pv_system.setup_weather_data(ghi=dwddata.RAD_WH,
                                                        dhi=dhi_erbs.dhi,
                                                        dni=dni_disc.dni,
                                                        temp_air=dwddata.TEMPERATURE_AIR_200DEGC,
                                                        wind_speed=dwddata.WIND_SPEED)
        elif current_mode == "dirint":
            weather_data = pv_system.setup_weather_data(ghi=dwddata.RAD_WH,
                                                        dhi=dni_dirint.values,
                                                        dni=dni_disc.dni,
                                                        temp_air=dwddata.TEMPERATURE_AIR_200DEGC,
                                                        wind_speed=dwddata.WIND_SPEED)     

        pv_system.run_model(wheater_data=weather_data)
        my_data = pv_system.combine_data(current_mode)
        calc_data = pd.concat([calc_data, my_data], axis=1)
    
    # Build up common dataframe to collect complete calculation data:
    whole_df = dwddata
    whole_df.columns = whole_df.columns.add_categories(["DHI_ERBS", "DNI_DISC", "DNI_DIRINDEX"])
    whole_df["DHI_ERBS"] = dhi_erbs["dhi"]
    whole_df["DNI_DISC"] = dni_disc["dni"]
    whole_df["DNI_DIRINDEX"] = dni_dirint.values

    whole_df.columns = whole_df.columns.add_categories(["GHI_CLEARSKY", "DNI_CLEARSKY", "DHI_CLEARSKY"])
    whole_df["GHI_CLEARSKY"] = solar_proc.clearsky.ghi
    whole_df["DNI_CLEARSKY"] = solar_proc.clearsky.dni
    whole_df["DHI_CLEARSKY"] = solar_proc.clearsky.dhi

    whole_df.columns = whole_df.columns.add_categories(["AZIMUTH", "ZENITH", "ELEVATION"])
    whole_df["AZIMUTH"] = solar_proc.solpos.azimuth
    whole_df["ZENITH"] = solar_proc.solpos.zenith
    whole_df["ELEVATION"] = solar_proc.solpos.elevation
    # Remove categorical index
    whole_df.columns = whole_df.columns.tolist()

    # Mege single datasets into one to have a common csv file.
    result = pd.concat([whole_df, calc_data], axis=1)
    #result = pd.merge(whole_df,my_data, left_index=True)
    csv_filename = datetime.now().strftime("%Y_%m_%d_%H_%M_Uhr.csv")
    result.to_csv(os.path.join("output", csv_filename))

if __name__ == "__main__":
    main()