import math
import numpy as np
import pandas as pd
from lmfit import Model
import datetime as dt


def get_rows(df, lookup, where):
    df_temp = df[df[where].isin(lookup)]
    df_temp = df_temp.reset_index(drop=True)
    return df_temp
