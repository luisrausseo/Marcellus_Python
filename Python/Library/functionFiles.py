import math
import numpy as np
import pandas as pd
from lmfit import Model
import datetime as dt


def monthDifference(LargeDate, SmallDate):
    month = (LargeDate.year - SmallDate.year) * 12 + (LargeDate.month - SmallDate.month) + \
            math.ceil((LargeDate.day - SmallDate.day) / 365.25 * 12) + 1
    return month


def monthDifference5(LargeDate, SmallDate):
	LargeDate = LargeDate.fillna(0)
	f = lambda x: (x.year - SmallDate.year) * 12 + (x.month - SmallDate.month) + \
	    math.ceil((x.day - SmallDate.day) / 365.25 * 12) + 1
	return LargeDate.map(f)
	
	
def powerLawExponential(t, qi, Diff, Di, n):
    return qi * np.exp((-Diff * t) + (-Di * (t ** n)))


def fitPowerLawExponential(Gas, Time, Controls):
	x0 = [(min(Gas)+max(Gas))/2, 0.5, 0.5, 0.5]
	gmodel = Model(powerLawExponential)
	gmodel.set_param_hint('qi', value=x0[0], min=0, max=np.inf)
	gmodel.set_param_hint('Diff', value=x0[1], min=0.01, max=0.2)
	gmodel.set_param_hint('Di', value=x0[2], min=0.01, max=0.2)
	gmodel.set_param_hint('n', value=x0[3], min=0.02, max=1)
	result = gmodel.fit(Gas, t=Time)
	r2 = 1 - result.residual.var() / np.var(Gas)
	fit = [result.best_values.get("qi"),result.best_values.get("Diff"),result.best_values.get("Di"),result.best_values.get("n"), r2]
	if (Controls.Fitting.OutlierDetection):
		GasFit = powerLawExponential(Time, fit[0], fit[1], fit[2], fit[3])
		Residual=abs(GasFit-Gas)
		CutOffResidual = Residual.quantile(1-Controls.Fitting.Fraction)
		ind = Residual.loc[(Residual < CutOffResidual)].index
		Gas2 = Gas[ind]
		Time2 = Time[ind]
		OutlierIndex = Residual.loc[(Residual >= CutOffResidual)].index
		fit.append(OutlierIndex)
	return fit
	
	
def generalisedLogistic(t,B,C,Q,V):
    A = 0
    K = 1
    return A + (K - A) / (C + Q * np.exp(-B * t)) ** (1 / V)


def fitGeneralisedLogistic(Gas,Waste,Controls):
    lb = [0, 0, 0, 0.25]
    ub = [5, 5, 5, 1]
    #Numpy allows to perform element wise operations easier. 
    lb_l = np.array([0, 0, 0, 0.25])
    ub_l = np.array([5, 5, 5, 1])
    x0 = (lb_l + ub_l)/2
    #Go back to list
    x0 = x0.tolist()
    gmodel = Model(generalisedLogistic)
    gmodel.set_param_hint('B', value=x0[0], min=lb[0], max=ub[0])
    gmodel.set_param_hint('C', value=x0[1], min=lb[1], max=ub[1])
    gmodel.set_param_hint('Q', value=x0[2], min=lb[2], max=ub[2])
    gmodel.set_param_hint('V', value=x0[3], min=lb[3], max=ub[3])
    result = gmodel.fit(Gas, t = Waste)
    r2 = 1 - result.residual.var() / np.var(Gas)
    fit = [result.best_values.get("A"), result.best_values.get("B"), result.best_values.get("C"), 
           result.best_values.get("K"), result.best_values.get("Q"), result.best_values.get("V"), r2]
    return fit

def GetDateTime(Month):
	year = 2018 + math.floor(Month / 12)
	if (Month % 12 == 0):
		Month = 12
	else:
		Month = Month % 12
	return dt.datetime(year, Month, 1)
