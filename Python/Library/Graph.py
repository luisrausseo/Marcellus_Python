import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model
import matplotlib.dates as mdates
from datetime import datetime
import math
from scipy.stats import norm,rayleigh
import matplotlib.mlab as mlab
from scipy import stats
import seaborn as sns

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

def graph_histogram(data, counties):
    fig, ax = plt.subplots(1,1)
    for county in counties:
        df = get_rows(data, [county], 'county')
        df['date_spud'] = pd.to_datetime(df['date_spud'].str.strip(), format='%Y-%m-%d')
        df = df.loc[(df['date_spud'].dt.month >= 1) & (df['date_spud'].dt.month < 5)]
        df = df['date_spud']
        df.groupby(df.dt.year).count().plot(kind='bar', color='blue', label=county)
    fig.autofmt_xdate()
    plt.legend()
    plt.show()
    return 0

def reject_outliers(data, m):
    return data[abs(data - np.mean(data)) < m * np.std(data)]

def graph_histogram2(data, counties):
    fig, ax = plt.subplots(1,1)
    for county in counties:
        #get data and fix it
        df = get_rows(data, [county], 'county')
        df['date_spud'] = pd.to_datetime(df['date_spud'].str.strip(), format='%Y-%m-%d')
        df = df.loc[(df['date_spud'].dt.month >= 1) & (df['date_spud'].dt.month < 5)]
        dates = pd.DatetimeIndex(df['date_spud'])
        dates_fix = reject_outliers(dates.year.values, 2)
        #calculate number of bins and graph bars
        unique, counts = np.unique(dates_fix, return_counts=True)
        num_bins = len(range(min(unique),max(unique),1)) + 1
        plt.xlim((min(unique)-2, max(unique)+2))
        plt.hist(dates_fix, 'auto', normed=True, align='mid')

#graph curves
        xt = plt.xticks()[0]  
        xmin, xmax = min(xt), max(xt)
        lnspc = np.linspace(xmin, xmax, len(dates_fix))
        #normal
        m, s = stats.norm.fit(dates_fix) # get mean and standard deviation  
        pdf_g = stats.norm.pdf(lnspc, m, s) # now get theoretical values in our interval  
        plt.plot(lnspc, pdf_g, label="Norm") # plot it
        #Gamma
        ag,bg,cg = stats.gamma.fit(dates_fix)  
        pdf_gamma = stats.gamma.pdf(lnspc, ag, bg,cg)  
        plt.plot(lnspc, pdf_gamma, label="Gamma")
        #Beta
        ab,bb,cb,db = stats.beta.fit(dates_fix)  
        pdf_beta = stats.beta.pdf(lnspc, ab, bb,cb, db)  
        plt.plot(lnspc, pdf_beta, label="Beta")
    fig.autofmt_xdate()
    plt.legend()
    plt.show()
    return 0
