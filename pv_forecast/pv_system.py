import os
import pvlib
import pandas as pd
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

TEMP_MOD_PARA = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
AOI_MODEL = "no_loss"
SPECTRAL_MODEL = "no_loss"
MYINV = {"Vac":400.0,"Pso":20.0,"Paco":4200.0,"Pdco":4325.437693099,"Vdco":570.0,"C0":0.000001335,"C1":0.0,"C2":0.0,"C3":-0.0004768538,"Pnt":7.9,"Vdcmax":900.0,"Idcmax":13.0,"Mppt_low":120.0,"Mppt_high":720.0}

class PVSystem:
    def __init__(self, inverter: str, pv_module: str, albedo: float, pvlib_location) -> None:
        
        self.pv_systems = {}
        self.model_chain = {}
        self.inverter_id = inverter
        self.module_id = pv_module
        self.albedo = albedo
        self.pvlib_location = pvlib_location
        self.model_data = pd.DataFrame()

        # Setup pv-modules
        if "LG_Electronics_Inc__LG355N1C_V5" in pv_module:
            # This step is necessary since my LG_Electronics_Inc__LG355N1C_V5 - Modules
            # are currently not included in pvlib module library. Therefore I took it from
            # cec-module repository and stored it locally until it will be included in pvlib.
            # see https://github.com/NREL/SAM/tree/develop/deploy/libraries for latest cec-modules
            file_path = os.path.dirname(__file__)
            self.pv_module = pd.read_pickle(os.path.join(file_path, "data", "LG355N1C_V5_Module.p"))
        else:
            sandia_modules = pvlib.pvsystem.retrieve_sam('cecmod')
            self.pv_module = sandia_modules[pv_module]

        # Setup inverter:
        # I am using Kostal Plenticore Plus 4.2 iverter, which is unfortunatelly not part of
        # the cec-inverter libary (see https://github.com/NREL/SAM/tree/develop/deploy/libraries).
        # I set up the data in the github repo https://github.com/tinoetzold/KostalPlenticoreData-for-PVLIB
        # TODO: bring data to pickle file or something.
        if "Kostal_Plenticore__Plus_4_2" in inverter:
            # My inverter (setu)
            self.inverter = pd.Series(MYINV)
        else:
            cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
            self.inverter = cec_inverters[inverter]
        

    def add_pv_system(self, id: str, surface_tilt: float, surface_azimuth: float, modules_per_string: int) -> None:
        """
        This function is used to add a solar configuration, e.g. if modules are mounted with different
        directions of the roof like EAST and WEST. The pvlib-inverter model (currently) does not support
        strings with different azimuths, where each has a specific module load.
        """
        solar_sys = pvlib.pvsystem.PVSystem(surface_tilt=surface_tilt,
                                            surface_azimuth=surface_azimuth,
                                            module=self.module_id,
                                            module_parameters=self.pv_module,
                                            inverter=self.inverter_id,
                                            inverter_parameters=self.inverter,
                                            albedo=self.albedo,
                                            modules_per_string=modules_per_string,
                                            racking_model="open_rack",
                                            temperature_model_parameters=TEMP_MOD_PARA,
                                            strings_per_inverter=1,
                                            )
        # Store the configuration
        self.pv_systems[id] = solar_sys

        # Now set up a model chain with the defined pvsystem:
        model_chain = pvlib.modelchain.ModelChain(system=solar_sys,
                                                location=self.pvlib_location,
                                                aoi_model=AOI_MODEL,
                                                orientation_strategy=None,
                                                spectral_model=SPECTRAL_MODEL
                                                )
        self.model_chain[id] = model_chain
    
    def setup_weather_data(self, ghi, dhi, dni, temp_air=None, wind_speed=None):
        weather_data = {"ghi": ghi, "dni": dni, "dhi": dhi,
                        "temp_air": temp_air, "wind_speed": wind_speed}
        weather_df = pd.DataFrame(weather_data)
        return weather_df

    def run_model(self, wheater_data) -> None:
        for id, pv_system in self.model_chain.items():
            pv_system.run_model(wheater_data)

    def combine_data(self, current_mode: str):
        data_dict = pd.DataFrame()
        plain_series = ["ac", "aoi", "cell_temperature", "effective_irradiance",]
        nested_series = ["dc", "diode_params", "total_irrad"]

        # Loop about each pv system and build up unique column names
        for id, pv_system in self.model_chain.items():
            # Assign plain stored Series:
            for pv_key in plain_series:
                data_ = getattr(pv_system, pv_key)
                data_dict[id + "_" + pv_key + "_" + current_mode] = data_
            
            # Assign nested stored Series:
            for pv_key in nested_series:
                data_ = getattr(pv_system, pv_key)
                for column in data_.columns:
                    data_dict[id + "_" + pv_key + "_" + column + "_" + current_mode] = data_[column]
        
        column_names = data_dict.columns
        all_ac_columns =[col_name for col_name in column_names if "_ac" in col_name]
        data_dict["ALL_AC_POWER" + "_" + current_mode] = 0
        for col in all_ac_columns:
            data_dict["ALL_AC_POWER" + "_" + current_mode] = data_dict["ALL_AC_POWER" + "_" + current_mode] + data_dict[col]
        return data_dict
