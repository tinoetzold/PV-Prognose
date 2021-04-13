# PV-Prognose
Model to determine the expected power output of Photovoltaik-System (PV-System) based on DWD weather forecast data.


The basic procedure of the program has been derived from Kilian Knoll "DWDForecast" tool: 
https://github.com/kilianknoll/DWDForecast
Many thanks for the ideas!


The following libraries are used:
- PVLIB: Library for photovoltaic system modelling including irradiance calculation etc. (https://pvlib-python.readthedocs.io/en/stable/)
- wetterdienst: Python library to access DWD (Deutscher Wetter Dienst) forecast model. (https://pypi.org/project/wetterdienst/)
- Pandas Library, Dataframes are used as basic data model.

## Installation

Create a virtual environment using Python > 3.8.1 interpreter (Python 3.7.x  may cause issues with pytables.)

Then install packages from requirements.txt

## Purpose
This implementation is used to verify a forecast-model against the measured valus from the PV-System

Thefore, the following plan was initiated:
- set up the PV-System representing my configuration
- get current wheather forecast data from DWD for upcoming 48 h and use irradiaton data for calculating expected power output in this time range
- compare forecasted data with production data provided by the Inverter (via Web-Frontend)

## Plans for furter development

Later, the results of this verification will be the baseline for production forecast to schedule the optimal order of utilization of...
- Electric Vehicle loading
- laundry
- dishwasher
- ...

where the target is to maximize own consumption of self generated electicity.

Therefore, the forecast will be set up as a regularly running thread that will update the forecast each e.g. 6 hours.
Then, the forecast data will be stored in a SQL-Library to be displayed in a Node-Red environment.

The current values of the PV inverter will be stored on a regular basis (e.g. minutely) in an InfluxDB.

# Usage of the Tool
## Configuration

### Weather Forecast Data

The weather forecast is taken from DWD Mosmix model. The station closest to the location of the PV system is defined in the configuration.ini file in the Section "DWD".

Basically, for validation purpose, it is possible to base the simulation on forecast data as well as on historical data (measured values). The historical data includes global irradiation as well as diffuse irradiation
### My PV-Installation

Since the available rooftop area is quite limited, I have a small PV System installed.

Configuration:
- PV-Panels: LG LG355N1C,V5, installed as a East-West-configuration
- Installed panels on East side rooftop (azimuth = 101 deg east): 7 x 355 W = 2485 W
- Installed panels on West side rooftop (azimuth = 281 deg west): 8 x 355 W = 2840 W
- Inverter: Kostal Plenticore Plus 4.2 (4.2 kWp)

The basic configuration of the PV System is done in the configuration.ini-file  in the SolarSystem-Section. 

# Verification
## Irradiation Models

The DWD Mosmix forecast provides global irradiation (ghi) values in a hourly resulution. To run the PVLIB Model Chain, also the diffuse horizontal irradiation (dhi) and the direct normal irradiation (dni) is required.

## Direct Normal Irradiation (dni)

PVLIB comes up with a couple of alogrithms to determine dni from ghi. Here we use multiple of them, but the DISC model seems to work good.

## Diffuse Horizontal Irradiation (dhi)
For dhi computation, the Erbs model is used. It showed a good compliance between forecasted and measured (by DWD) values.

# Outputs
## CSV-File with all data

After running the main.py, a csv-file carrying wheater data, irradiation and computet PV system results. This file is stored in the "output" directory.

# Internals
## DC-Paramters (from PVLIB source code)

        * i_sc : Short-circuit current (A)
        * i_mp : Current at the maximum-power point (A)
        * v_oc : Open-circuit voltage (V)
        * v_mp : Voltage at maximum-power point (V)
        * p_mp : Power at maximum-power point (W)
        * i_x : Current at module V = 0.5Voc, defines 4th point on I-V
          curve for modeling curve shape
        * i_xx : Current at module V = 0.5(Voc+Vmp), defines 5th point on
          I-V curve for modeling curve shape

