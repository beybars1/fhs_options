import os
import numpy as np
import pandas as pd
from datetime import datetime


class Data:
    def __init__(self, file_name):
        self.file_name = file_name

    def create_df(self):
        pb_df = pd.read_csv(self.file_name)
        date_np = pb_df.iloc[1:, 0].to_numpy()
        er_11_np = pb_df.iloc[1:, 1].to_numpy()
        return date_np, er_11_np

    def difference_day(self, start_date, finish_date):
        date_format = "%d.%m.%y"
        a = datetime.strptime(start_date, date_format)
        b = datetime.strptime(finish_date, date_format)
        diff_day = b - a
        return diff_day
