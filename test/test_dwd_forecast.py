import unittest, os
import pandas as pd

from pv_forecast.dwd_forecast import DWD_Forecast

class TestDWDForecast(unittest.TestCase):
    def setUp(self) -> None:
        self.dwd_fc = DWD_Forecast("P0031")


    def test_dwd_data_access_p0031(self):
        # Test if accessing the DWD Data is working and a dataset will be returned
        # Dataset must be pandas Dataframe and have certain columns
        my_df = self.dwd_fc.retrieve_data()
        self.assertTrue(isinstance(my_df, pd.DataFrame))
        self.assertTrue("RADIATION_GLOBAL" in my_df.columns)
        self.assertTrue(len(my_df["RADIATION_GLOBAL"]) > 1)

if __name__ == '__main__':
    unittest.main()