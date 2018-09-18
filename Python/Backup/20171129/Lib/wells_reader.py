import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model

def get_data(path, mode):
    if mode == 'prod':
        df = pd.read_csv(path, infer_datetime_format='true', parse_dates=[1])
    if mode == 'wells':
        df = pd.read_csv(path)
        df = df[['id', 'latitude', 'longitude', 'county', 'formation','date_spud']]
    return df

def get_rows(df, lookup, where):
    df_temp = df[df[where].isin(lookup)]
    df_temp = df_temp.reset_index(drop=True)
    return df_temp

def graph_WellData(data, well_id):
    fig, ax = plt.subplots(1,1)
    for well in well_id:
        data_temp = get_rows(data, [well], 'well_id')
        data_temp['date'] = pd.to_datetime(data_temp['date'])
        data_temp.plot(x='date',y='gas', linestyle='None', marker='.', label=well, ax=ax)
    plt.xlabel('Year')
    plt.ylabel('Gas')
    plt.legend()
    plt.show()
    return 0

def EPL(t, qi, Diff, Di, n):
    return qi*np.exp((-Diff*t)+(-Di*(t**n)))

def graph_EPL(data, well, p0):
    data_temp = get_rows(data, [well], 'well_id')
    gmodel = Model(EPL)
    result = gmodel.fit(data_temp['gas'], t=data_temp['month_from_first'], qi=data_temp['gas'][0], Diff=p0[0], Di=p0[1], n=p0[2])
    print(result.fit_report())
    popt = (result.best_values.get("qi"),result.best_values.get("Diff"),result.best_values.get("Di"),result.best_values.get("n"))
    plt.plot(data_temp['month_from_first'], result.best_fit, label='fit: qi=%5.3f, Diff=%5.3f, Di=%.2E, n=%5.3f' % tuple(popt))
    plt.plot(data_temp['month_from_first'], data_temp['gas'], marker='.',linestyle='None',label=well)
    plt.xlabel('Month from First')
    plt.ylabel('Gas')
    plt.legend()
    plt.show()
    return popt
