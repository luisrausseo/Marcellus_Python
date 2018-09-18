import datetime as dt
import math
from Library import Reader
import pandas as Pd
import time
import numpy as np    
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
import gdal
from gdalconst import * 


# --- Config ---
print("Config: Begin")
start = time.time()


class Directories:
    InputDirectory = '/home/lrausseo/MEGAsync/Project WW/Data/'
    """
    Wells = InputDirectory + 'CSV\\Wells.csv'
    Productions = InputDirectory + 'CSV\\Productions.csv'
    Wastes = InputDirectory + 'CSV\\Wastes.csv'
    """
    # MID is data files produced by previous steps, to avoid long debug time.
    Wells = InputDirectory + 'MID/Wells.csv'
    Productions = InputDirectory + 'MID/Productions.csv'
    Wastes = InputDirectory + 'MID/Wastes.csv'
    Facilities = InputDirectory + 'CSV/Facilities.csv'
    DrillingKernelDensity = InputDirectory + 'GIS/DrillingActivityKernel/DrillingActivityKernel.txt'


class Dates:
    BaseDate = dt.datetime(2008, 1, 1)
    PaperDate = dt.datetime(2018, 1, 1)
    LastProductionDate = dt.datetime(2017, 6, 30)


class Controls:
    PrintProgress = True
    Plotting = False

    class Fitting:
        NoFitCriteria = 'r2'
        LateTimeWeight = ''
        NormalizePenalties = ''
        OutlierDetection = True
        Fraction = 0.10


Formations = ['marcellus', 'marcellus shale', 'marcellus shale (unconventional)']
Wastes_Types = ['produced fluid', 'brine']
print("Done")
# --- End Config ---

# --- Import ---
print("Import: Begin")
# Columns with dates must be included in the parse_dates list.
Wells = Pd.read_csv(Directories.Wells,  infer_datetime_format='true', parse_dates=[16, 17, 18, 19, 20, 21])
Productions = Pd.read_csv(Directories.Productions, infer_datetime_format='true', parse_dates=[1])
Wastes = Pd.read_csv(Directories.Wastes, infer_datetime_format='true', parse_dates=[2, 3])
Raster_h = gdal.Open(Directories.DrillingKernelDensity, GA_ReadOnly)
print("Done")
# --- End Import ---

# --- Select ---
print("Select: Begin")
Wells = Reader.get_rows(Wells, Formations, 'Formation')
Productions = Productions.loc[(Productions['Date'] >= Dates.BaseDate)]
Wastes = Wastes.loc[(Wastes['BeginDate']>= Dates.BaseDate)]
Wastes = Reader.get_rows(Wastes, Wells['API'].values, 'API')
Wastes = Reader.get_rows(Wastes, Wastes_Types, 'Type')
print("Done")
# --- End Select ---

# --- Derive ---
print("Derive: Begin")
NumberOfWells = len(Wells.index)
gt = Raster_h.GetGeoTransform()
class Raster:
	GridSize = gt[1]
	### WHAT?
print("Done")
# --- End Derive ---

# --- DateToNum ---
print("DateToNum: Begin")
##ProductionAPIs = Productions['API'];
##WasteAPIs = Wastes['API'];
##for i in range(0, NumberOfWells + 1):
##    WellAPI = Wells['API'].iloc[[i]].values
##    Index = ProductionAPIs.loc[ProductionAPIs.isin(WellAPI)].index.tolist();
##    ProductionDates = Productions['Date'].loc[Index];
##    print((i/10029)*100);
##    if (len(ProductionDates.index) != 0):
##        FirstProductionDatePostBaseDate = [min(ProductionDates)];
##        LastProductionDatePostBaseDate = [max(ProductionDates)];
##        if(FirstProductionDatePostBaseDate != None):
##            Wells['FirstProductionDatePostBaseDate'][i] = FirstProductionDatePostBaseDate[0];
##            Wells['FirstProductionMonthsFromBaseDate'][i] = Reader.monthDifference(FirstProductionDatePostBaseDate[0], Dates.BaseDate);
##            Productions['MonthsFromFirst'][Index] = Reader.monthDifference3(ProductionDates, FirstProductionDatePostBaseDate[0]);
##            
##        if(LastProductionDatePostBaseDate != None):
##            Wells['LastProductionDatePostBaseDate'][i] = LastProductionDatePostBaseDate[0];
##            Wells['LastProductionMonthsFromBaseDate'][i] = Reader.monthDifference(LastProductionDatePostBaseDate[0], Dates.BaseDate);
##            
##        WasteIndex = WasteAPIs.loc[WasteAPIs.isin(WellAPI)].index.tolist();
##        BeginDate = Wastes['BeginDate'].loc[WasteIndex];
##        EndDate = Wastes['EndDate'].loc[WasteIndex];
##        if ~(BeginDate.empty):
##            if(FirstProductionDatePostBaseDate != None):
##                Wastes['BeginMonthsFromFirst'][WasteIndex] = Reader.monthDifference3(BeginDate, FirstProductionDatePostBaseDate[0]);
##            else:
##                Wastes['BeginMonthsFromFirst'][WasteIndex] = Reader.monthDifference3(BeginDate, Wells['SpudDate'][i]);
##        if ~(EndDate.empty):
##            if(FirstProductionDatePostBaseDate != None):
##                Wastes['EndMonthsFromFirst'][WasteIndex] = Reader.monthDifference3(EndDate, FirstProductionDatePostBaseDate[0]);
##            else:
##                Wastes['EndMonthsFromFirst'][WasteIndex] = Reader.monthDifference3(EndDate, Wells['SpudDate'][i]);
##                
##Wells['SpudMonthsFromBaseDate'] = Reader.monthDifference4(Wells['SpudDate'], Dates.BaseDate);
##Wells['CompletionMonthsFromBaseDate'] = Reader.monthDifference4(Wells['CompletionDate'], Dates.BaseDate);
##Wastes['BeginMonthsFromJan2008'] = Reader.monthDifference4(Wastes['BeginDate'], Dates.BaseDate);
##Wastes['EndMonthsFromJan2008'] = Reader.monthDifference4(Wastes['EndDate'], Dates.BaseDate);
print("Done")
# --- End DateToNum ---

# --- FitDCA ---
print("FitDCA: Begin")
##WellAPIs = Wells['API'];
##for i in range(0, NumberOfWells):
##    print(i);
##    WellProduction = Productions.loc[Productions['API'].isin([WellAPIs[i]])];
##    WellProduction = WellProduction[['MonthsFromFirst','Gas']];
##    Gas = WellProduction['Gas'];
##    Month = WellProduction['MonthsFromFirst'];
##    NormalizedGas = Gas/Gas.mean();
##    if ~(Gas.empty) and (len(Gas.index)>5) and (Gas.mean() != 0):
##        [qi,Di,Dinf,n,r2,OutlierIndex] = Reader.fitPowerLawExponential(NormalizedGas, Month, Controls);
##        qi = qi*Gas.mean();
##        Wells['PLEqi'][i] = qi;
##        Wells['PLEDi'][i] = Di;
##        Wells['PLEDinf'][i] = Dinf;
##        Wells['PLEn'][i] = n;
##    ##    GasFit = Reader.powerLawExponential(Month, qi, Dinf, Di, n);
##    ##    GasNoOutliers = Gas.loc[~Gas.index.isin(OutlierIndex)];
##    ##    GasFitNoOutliers = GasFit.loc[~GasFit.index.isin(OutlierIndex)];
##    ##    Gas1 = (GasNoOutliers - GasFitNoOutliers)**2;
##    ##    Gas2 = (GasNoOutliers - GasNoOutliers.mean())**2;
##    ##    r2 = 1 - (Gas1.sum()/Gas2.sum());
##        Wells['PLEr2'][i] = r2;
print("Done")
# --- End FitDCA ---


### --- Yearly --- ###
print("Yearly: Begin");
#----------------------
##WellAPIs = Wells['API'];
##for i in range(0, NumberOfWells):
###i = 31;
##    print(i);
##    WellAPI = WellAPIs[i];
##    WellGas = Productions.loc[Productions['API'].isin([WellAPI])];
##    WellWaste = Wastes.loc[Wastes['API'].isin([WellAPI])];
##    Well = Wells.loc[i];
##    if not (WellGas['Gas'].empty):
##        FirstCalendarYear = Well['FirstProductionDatePostBaseDate'].year;
##        LastCalendarYear = Well['LastProductionDatePostBaseDate'].year;
##        if not ((math.isnan(FirstCalendarYear)) or (math.isnan(LastCalendarYear))):
##            for Year in range(FirstCalendarYear,LastCalendarYear+1):#+1
##                YearlyGas = WellGas['Gas'].loc[(WellGas['Date'].dt.year == Year)].sum();
##                if (YearlyGas > 0):
##                    Wells['Gas' + str(Year)][i] = YearlyGas;
##    if not (type(Well['LastProductionDatePostBaseDate']) is Pd._libs.tslib.NaTType):
##        MonthsOfProduction = Reader.monthDifference(Well['LastProductionDatePostBaseDate'],Well['FirstProductionDatePostBaseDate']);
##        Month_val = int(MonthsOfProduction/12) + 1;
##        for Year in range(1,Month_val+1):#+1
##            if (Year < Month_val):
##                YearlyGas = WellGas['Gas'].loc[WellGas['MonthsFromFirst'].isin(range((Year - 1)*12,(Year*12)+1))].sum();#+1
##            else:
##                YearlyGas = WellGas['Gas'].loc[WellGas['MonthsFromFirst'].isin(range((Year - 1)*12,MonthsOfProduction+1))].sum(); #+1
##            if (YearlyGas > 0):
##                Wells['GasYear' + str(Year)][i] = YearlyGas;
##        if not (WellWaste['Volume'].empty):
##            FirstWasteDate = min(WellWaste['BeginDate']);
##            LastWasteDate = max(WellWaste['EndDate']);
##            if not ((math.isnan(FirstWasteDate.year)) or (math.isnan(LastWasteDate.year))):
##                for Year in range(FirstWasteDate.year, LastWasteDate.year + 1):
##                    YearlyWaste = WellWaste['Volume'].loc[(WellWaste['BeginDate'].dt.year == Year)].sum();
##                    if (YearlyWaste > 0):
##                        Wells['Waste' + str(Year)][i] = YearlyWaste;
##                Month_val = int(max(WellWaste['EndMonthsFromFirst'])/12) + 1;
##                for Year in range(1, Month_val + 1):
##                    if (Year < Month_val):
##                        EndOfTheYear = Year*12;
##                    else:
##                        EndOfTheYear = max(WellWaste['EndMonthsFromFirst']);
##                    BeginOfTheYear = (Year - 1)*12 + 1;
##                    Frac_1 = (WellWaste['BeginMonthsFromFirst'].loc[(WellWaste['BeginMonthsFromFirst'] >= BeginOfTheYear)] * (EndOfTheYear - WellWaste['BeginMonthsFromFirst'] + 1))/(WellWaste['EndMonthsFromFirst'] - WellWaste['BeginMonthsFromFirst']);
##                    Frac_2 = (WellWaste['BeginMonthsFromFirst'].loc[(WellWaste['BeginMonthsFromFirst'] < BeginOfTheYear)] * (WellWaste['EndMonthsFromFirst'] - BeginOfTheYear))/(WellWaste['EndMonthsFromFirst'] - WellWaste['BeginMonthsFromFirst']);
##                    Fraction = Frac_1.fillna(0) + Frac_2.fillna(0);
##                    Fraction.loc[(Fraction > 1)] = 1;
##                    Fraction.loc[(Fraction < 0)] = 0;
##                    YearlyWaste = WellWaste.Volume * Fraction;
##                    YearlyWaste = YearlyWaste.sum();
##                    if (YearlyWaste > 0):
##                        Wells['WasteYear' + str(Year)][i] = YearlyWaste; 
#----------------------
print("Done")
# --- End Yearly ---


# --- Regress ---
print("Regress: Begin")
'''
for i in range(0, NumberOfWells):
    # i = 512;
    print(i)
    Waste = Wells[['WasteYear1', 'WasteYear2', 'WasteYear3', 'WasteYear4', 'WasteYear5', 'WasteYear6', 'WasteYear7',
                   'WasteYear8', 'WasteYear9', 'WasteYear10']].loc[i]
    Gas = Wells[['GasYear1', 'GasYear2', 'GasYear3', 'GasYear4', 'GasYear5', 'GasYear6', 'GasYear7', 'GasYear8',
                 'GasYear9', 'GasYear10']].loc[i]
    num = ((i-1) % 9) + 1
    # Changed because the function requirements. [4 parameters + 1 header]
    if (len(Gas.dropna().index) >= 5) and (len(Waste.dropna().index) >= 5):
        NormalizedGas = Gas/Gas.mean()
        NormalizedWaste = Waste/Waste.mean()
        Data = Pd.DataFrame(data={'NormalizedGas': NormalizedGas.values,
                                  'NormalizedWaste': NormalizedWaste.values}).dropna()
        [A, B, C, K, Q, V, r2] = Reader.fitGeneralisedLogistic(Data.NormalizedGas, Data.NormalizedWaste, Controls)
        C = C/Waste.mean()**V
        Q = Q/Waste.mean()**V
        B = B/Gas.mean()
        Wells.LogisticB.loc[i] = B
        Wells.LogisticC.loc[i] = C
        Wells.LogisticQ.loc[i] = Q
        Wells.LogisticV.loc[i] = V
        Wells.Logisticr2.loc[i] = r2
'''
print("Done")
# --- End Regress ---


# --- Impute ---
print("Impute: Begin")
#for i for i in range(0, NumberOfWells):
'''
i = 3
Well = Wells.iloc[i]
if (Well['Status'] == "active") and (Well['PLEr2'] > 0.25):
	MonthsToJan2018 = Reader.monthDifference(Dates.PaperDate, Well.FirstProductionDatePostBaseDate) + 1
	aux_num1 = [0, 13, 25, 37, 49, 61]
	aux_num2 = [12, 24, 36, 48, 60 ,72]	
	for j in range(0, 6):
		# Range goes until the previous of the last number, so 1 is addedd to the last number
		GasYear = Reader.powerLawExponential(range(MonthsToJan2018 + aux_num1[j], MonthsToJan2018 + aux_num2[j] + 1), 
		                                     Well.PLEqi, Well.PLEDinf, Well.PLEDi, Well.PLEn)
		Well.set_value('Gas' + str(2018 + j), GasYear.sum())
	if (Well.Logisticr2 > 0.25):
		for k in range(0, 6):
			WasteYear = Reader.generalisedLogistic(Well['Gas' + str(2018 + k)], Well.LogisticB, Well.LogisticC,
			                                Well.LogisticQ, Well.LogisticV)
			Well.set_value('Waste' + str(2018 + k), WasteYear)
	if not (Well.Flag2017 is 1):
		Gas2017 = Well.Gas2017
		Waste2017 = Well.Waste2017
		if (Gas2017 > 0):
			if (Well.PLEr2 > 0.25):
				MonthsOfProduction = int(Well.LastProductionMonthsFromBaseDate - Well.FirstProductionMonthsFromBaseDate)
				AdditionalGas2017 = Reader.powerLawExponential(range(MonthsOfProduction+1, MonthsOfProduction+7), Well.PLEqi, Well.PLEDinf, Well.PLEDi, Well.PLEn)
				AdditionalGas2017 = AdditionalGas2017.sum()
			else:
				AdditionalGas2017 = Gas2017
				Well.set_value('Gas2017', Gas2017 + AdditionalGas2017)
				if (Well.Logisticr2 > 0.25):
					AdditionalWaste2017 = Reader.generalisedLogistic(AdditionalGas2017, Well.LogisticB, Well.LogisticC, Well.LogisticQ, Well.LogisticV)
				else:
					AdditionalWaste2017 = Waste2017
				Well.set_value('Waste2017', Waste2017 + AdditionalWaste2017)
			Well.set_value('Flag2017', 1)
	ProductionsDates = Productions.loc[Productions['API'].isin([Well.API])]
	FirstProductionDate = min(ProductionsDates.Date)
	LastProductionDate = max(ProductionsDates.Date)
	if (Well.PLEr2 > 0.25):
		for Year in range(math.ceil((Reader.monthDifference(LastProductionDate,FirstProductionDate)+1)/12),16):
			YGas = Reader.powerLawExponential(range((Year-1)*12+1,Year*12+1),Well.PLEqi,Well.PLEDinf,Well.PLEDi,Well.PLEn)
			YearlyGas = YGas.sum()
			if (Well.Logisticr2 > 0.25):
				YearlyWaste = Reader.generalisedLogistic(YearlyGas, Well.LogisticB, Well.LogisticC, Well.LogisticQ, Well.LogisticV)
			else:
				YearlyWaste = np.nan
			Well.set_value('GasYear' + str(Year), YearlyGas)
			Well.set_value('WasteYear' + str(Year), YearlyWaste)
			if not (Well.FlagLastYear is 1):
				MonthsOfProduction = Reader.monthDifference(Well.LastProductionDatePostBaseDate, Well.FirstProductionDatePostBaseDate)
				LastYear = int(MonthsOfProduction/12) + 1
				if (LastYear < 11):
					GasLastYear = Well['GasYear' + str(LastYear)]
				if (GasLastYear > 0):
					if (Well.PLEr2 > 0.25):
						MonthsOfProduction = int(Well.LastProductionMonthsFromBaseDate - Well.FirstProductionMonthsFromBaseDate) + 1
						AdditionalGasLastYear = Reader.powerLawExponential(range(MonthsOfProduction + 1, (int(MonthsOfProduction / 12) + 1) * 12 + 1), Well.PLEqi, Well.PLEDinf, Well.PLEDi, Well.PLEn)
					else:
						AdditionalGasLastYear = GasLastYear
					Well.set_value('GasYear' + str(LastYear), GasLastYear + AdditionalGasLastYear.sum())
				WastesEnd = Wastes.loc[Wastes['API'].isin([Well.API])]
				LastYear2 = int(max(WastesEnd.EndMonthsFromFirst) / 12) + 1
				if (LastYear2 == LastYear):
					if (Well.Logisticr2 > 0.25):
						AdditionalWasteLastYear = Reader.generalisedLogistic(AdditionalGasLastYear.sum(), Well.LogisticB, Well.LogisticC, Well.LogisticQ, Well.LogisticV)
					else:
						AdditionalWaste2017 = Waste2017;
					Well.set_value('WasteYear' + str(LastYear2), Well['WasteYear' + str(LastYear2)] + AdditionalWasteLastYear) # ?????
				Well.set_value('FlagLastYear', 1)
Wells.iloc[i] = Well
'''
print("Done")
# --- End Impute ---

# --- NewDrills ---
print("NewDrills: Begin")
Wells_nd = Wells.ix[range(0, NumberOfWells + 1)]
SelectedWells = Wells_nd.loc[(Wells_nd['SpudDate'] >= Dates.BaseDate)]
GroupData = SelectedWells
SpudYear = GroupData.SpudDate.dt.year + ((1/12) * (GroupData.SpudDate.dt.month + 1)) + ((1/365.25) * GroupData.SpudDate.dt.day)
'''
[N, T] = np.histogram(SpudYear, bins=40)
# Fix bins to be at center
T_centers = []
for i in range(0,len(T)-1):
	T_centers.append((T[i]+ ((T[i+1] - T[i])/2)))
'''
# Fix SpudYear into logisctic mixture with 3 samples
LogisticMixtureModel = GaussianMixture(3)
LMM = LogisticMixtureModel.fit(X = np.expand_dims(SpudYear.values, 1))
LMM_x = np.linspace(min(SpudYear), max(SpudYear)+5, 5000)
LMM_y = np.exp(LMM.score_samples(LMM_x.reshape(-1, 1)))
#Creates new well
Ramainder = 0
WellNumber = 0
for Month in range(1, (6*12) + 1):
	NumberOfNewWells = LMM.predict(2018 + Month / 12) + Ramainder
	Ramainder = NumberOfNewWells % 1
	NumberOfNewWells = 	int(math.floor(NumberOfNewWells))
	CurrentDate = Reader.GetDateTime(Month)
	for j in range(0, NumberOfNewWells + 1):
		WellAPI = 'AJ0000' + str(1000 + WellNumber)
		WellNumber += 1
############### I'M HERE


# Plot histogram and curve
fig, ax = plt.subplots(nrows = 1, ncols = 1)
ax.hist(SpudYear, bins=40, edgecolor='black', normed=True, linewidth=1)
ax.plot(LMM_x, LMM_y)
plt.show()
print("Done")
# --- End NewDrills ---

# --- SaveResults ---
print("SaveResults: Begin")
'''
Wells.to_csv('Result/Wells.csv', sep=',', index=False)
Productions.to_csv('Result/Productions.csv', sep=',')
Wastes.to_csv('Result/Wastes.csv', sep=',')
print("Done")
'''
# --- Save Results End---


end = time.time()
print(end - start)
