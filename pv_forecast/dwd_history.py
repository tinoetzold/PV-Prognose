"""
Class to handle the DWD Weather forecast data and do first modifications
to fit the data for pvlib calculations.

Therefore, some temperature values need to be transforemed from Kelvin to DegC.
The global radiation values need to be transformed to Wh/m^2

Details on DWD weather forecast data may be found here:
https://www.dwd.de/DE/leistungen/met_verfahren_mosmix/met_verfahren_mosmix.html

"""
import pandas as pd

from wetterdienst.provider.dwd.observation import (DwdObservationParameter,
                                                  DwdObservationRequest,
                                                  DwdObservationResolution,
                                                  DwdObservationParameter,
                                                  DwdObservationPeriod)

# Conversion factor: kJ/cm^2 to W/m^2 (only valid for 10 minute intervall)
J_to_KW = 16.666666667

# List of parameters to determine from DWD data, see following link for details:
# https://opendata.dwd.de/weather/lib/MetElementDefinition.xml
MOSMIX_ELEMENTS = ["DD", "ww", "Rad1h", "RRad1", "TTT", "FF", "PPPP", "Td", "N"]

class DWD_History:
    def __init__(self, station_id) -> None:

        # create request
        self.request = DwdObservationRequest(
        parameter=[
        DwdObservationParameter.MINUTE_10.TEMPERATURE_AIR_200,
        DwdObservationParameter.MINUTE_10.RADIATION_GLOBAL,
        DwdObservationParameter.MINUTE_10.RADIATION_SKY_DIFFUSE,
        DwdObservationParameter.MINUTE_10.TEMPERATURE_DEW_POINT_200,
        DwdObservationParameter.MINUTE_10.PRESSURE_AIR_STATION_HEIGHT,
        DwdObservationParameter.MINUTE_10.WIND_SPEED,
        ],
        resolution=DwdObservationResolution.MINUTE_10,
        period=DwdObservationPeriod.NOW
        ).filter(station_id=(station_id, ))      # 1078 = Duesseldorf Flughafen
        # Assign the station:
        #self.stations = self.request.filter(station_id=station_id)


    def retrieve_data(self):
        """ Get data from DWD server. """
        #respone = next(self.stations.values.query())
        station_data = self.request.values.all().df
        # Reshape the data for later use.
        data = self.reshape_data(station_data)
        
        return data

    def reshape_data(self, raw_data):
        """
        input:
        raw_data: pandas Dataframe having DWD Mosmix shape.
        """
        # First, create a table from plain DWD data using DATE as index
        reshaped_data = pd.pivot_table(raw_data, values="value", index=["date"], columns="parameter", aggfunc='first')
        # Now, shift values by 1h to the past, since the DWD Values are assigned to the end of the periode, whereas the
        # PVLIB values are assigned to the beginning of a cycle.
        reshaped_data.index = reshaped_data.index# - pd.offsets.Hour(1)
        # Add some columns in advance (otherwise will not work since columns are categorical)
        reshaped_data.columns = reshaped_data.columns.add_categories(["RAD_WH", "RAD_DIFFUS", "PRESSURE_AIR_SURFACE_REDUCED","WIND_SPEED", "TEMPERATURE_AIR_200DEGC", "DEW_POINT_DEGC"])
        # For pvlib, temperatures need to be available in degC:
        reshaped_data["TEMPERATURE_AIR_200DEGC"] = reshaped_data["temperature_air_200"]
        reshaped_data["DEW_POINT_DEGC"] = reshaped_data["temperature_dew_point_200"]
        # Given global radiation is in kJ/m^2, tranform into Wh/m^2
        reshaped_data["RAD_WH"] = reshaped_data["radiation_global"].apply(lambda x: x * J_to_KW)
        reshaped_data["RAD_DIFFUS"] = reshaped_data["radiation_sky_diffuse"].apply(lambda x: x * J_to_KW)
        reshaped_data['WIND_SPEED'] = reshaped_data['wind_speed'].astype(float)
        reshaped_data["PRESSURE_AIR_SURFACE_REDUCED"] = reshaped_data["pressure_air_station_height"].astype(float)

        return reshaped_data


if __name__ == "__main__":
    dwd_fc = DWD_History(1078)
    mydata = dwd_fc.retrieve_data()
    print(mydata.columns)
