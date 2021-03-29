"""
Class to handle the DWD Weather forecast data and do first modifications
to fit the data for pvlib calculations.

Therefore, some temperature values need to be transforemed from Kelvin to DegC.
The global radiation values need to be transformed to Wh/m^2

Details on DWD weather forecast data may be found here:
https://www.dwd.de/DE/leistungen/met_verfahren_mosmix/met_verfahren_mosmix.html

"""
import pandas as pd
from wetterdienst.dwd.forecasts import DwdMosmixRequest, DwdMosmixType
from wetterdienst.dwd.forecasts.metadata.dates import DwdForecastDate

# Conversion factor: kJ/m^2 to Wh/m^2 (only valid for hourly time interval)
J_to_KW = 0.277778

# List of parameters to determine from DWD data, see following link for details:
# https://opendata.dwd.de/weather/lib/MetElementDefinition.xml
MOSMIX_ELEMENTS = ["DD", "ww", "Rad1h", "RRad1", "TTT", "FF", "PPPP", "Td", "N"]

class DWD_Forecast:
    def __init__(self, station_id) -> None:

        # create request
        self.request = DwdMosmixRequest(
        parameter=MOSMIX_ELEMENTS,
        start_issue=DwdForecastDate.LATEST,  # automatically set if left empty
        mosmix_type=DwdMosmixType.LARGE,     # SMALL (hourly) or LARGE (every 6 hours)
        tidy_data=True,
        humanize_parameters=True,
        )
        # Assign the station:
        self.stations = self.request.filter(station_id=station_id)


    def retrieve_data(self):
        """ Get data from DWD server. """
        respone = next(self.stations.values.query())
        
        # Reshape the data for later use.
        data = self.reshape_data(respone.df)
        
        return data

    def reshape_data(self, raw_data):
        """
        input:
        raw_data: pandas Dataframe having DWD Mosmix shape.
        """
        # First, create a table from plain DWD data using DATE as index
        reshaped_data = pd.pivot_table(raw_data, values="VALUE", index=["DATE"], columns="PARAMETER", aggfunc='first')
        # Add some columns in advance (otherwise will not work since columns are categorical)
        reshaped_data.columns = reshaped_data.columns.add_categories(["TEMPERATURE_AIR_200DEGC", "DEW_POINT_DEGC", "RAD_WH"])
        # For pvlib, temperatures need to be available in degC:
        reshaped_data["TEMPERATURE_AIR_200DEGC"] = reshaped_data["TEMPERATURE_AIR_200"].apply(lambda x: x - 273.15)
        reshaped_data["DEW_POINT_DEGC"] = reshaped_data["TEMPERATURE_DEW_POINT_200"].apply(lambda x: x - 273.15)
        # Given global radiation is in kJ/m^2, tranform into Wh/m^2
        reshaped_data["RAD_WH"] = reshaped_data["RADIATION_GLOBAL"].apply(lambda x: x * J_to_KW)

        return reshaped_data


if __name__ == "__main__":
    dwd_fc = DWD_Forecast("P0031")
    mydata = dwd_fc.retrieve_data()
    print(mydata.columns)
