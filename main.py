import configparser
from pv_forecast.dwd_forecast import DWD_Forecast

def main():
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    
    dwd_fc = DWD_Forecast(config.get("DWD", "DWDStation", raw=True))
    


if __name__ == "__main__":
    pass