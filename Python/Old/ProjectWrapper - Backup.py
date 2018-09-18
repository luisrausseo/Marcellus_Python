
### --- Config ---
print("Config: Begin")
import datetime as dt
import math
from Library import Reader
import pandas as Pd
import time
import numpy as np    

start = time.time()


class Directories:
    InputDirectory = 'C:\\Users\luisr\\Documents\\MEGAsync\\Python\\TEST FOLDER\\Project WW\\Data\\'
    #Wells = InputDirectory + 'CSV\\Wells.csv'
    #Productions = InputDirectory + 'CSV\\Productions.csv'
    #Wastes = InputDirectory + 'CSV\\Wastes.csv'
        #MID are data files produced by previous steps, to avoid long debug time.
    Wells = InputDirectory + 'MID\\Wells.csv'
    Productions = InputDirectory + 'MID\\Productions.csv'
    Wastes = InputDirectory + 'MID\\Wastes.csv'
    Facilities = InputDirectory + 'CSV\\Facilities.csv'
    DrillingKernelDensity = InputDirectory + 'GIS\\DrillingActivityKernel\\DrillingActivityKernel.txt'


class Dates:
    BaseDate = dt.datetime(2008, 1, 1);
    PaperDate = dt.datetime(2018, 1, 1);
    LastProductionDate = dt.datetime(2017,6,30);

class Controls:
    PrintProgress = True;
    Plotting = False;
    class Fitting:
        NoFitCriteria = 'r2';
        LateTimeWeight = '';
        NormalizePenalties = '';
        OutlierDetection = True;
        Fraction = 0.10;

Formations = ['marcellus', 'marcellus shale', 'marcellus shale (unconventional)'];
Wastes_Types = ['produced fluid', 'brine'];
print("Config: Done");
### --- End Config ---

### --- Import ---
print("Import: Begin");
    #Colums with dates must be included in the parse_dates list.
Wells = Pd.read_csv(Directories.Wells,  infer_datetime_format='true', parse_dates=[16, 17, 18, 19, 20, 21]);
Productions = Pd.read_csv(Directories.Productions, infer_datetime_format='true', parse_dates=[1]);
Wastes = Pd.read_csv(Directories.Wastes, infer_datetime_format='true', parse_dates=[2,3]);
print("Import: Done");
### --- End Import ---

### --- Select ---
print("Select: Begin");
Wells = Reader.get_rows(Wells, Formations, 'Formation');
Productions = Productions.loc[(Productions['Date']>= Dates.BaseDate)];
Wastes = Wastes.loc[(Wastes['BeginDate']>= Dates.BaseDate)];
Wastes = Reader.get_rows(Wastes, Wells['API'].values, 'API');
Wastes = Reader.get_rows(Wastes, Wastes_Types, 'Type');
print("Select: Done");
### --- End Select ---

### --- Derive ---
print("Derive: Begin");
NumberOfWells = len(Wells.index);
print("Derive: Done");
### --- End Derive ---

### --- DateToNum ---
print("DateToNum: Begin");
##ProductionAPIs = Productions['API'];
##WasteAPIs = Wastes['API'];
##for i in range(0, NumberOfWells):
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
print("DatetoNum: Done");
### --- End DateToNum ---

### --- FitDCA --- ###
print("FitDCA: Begin");
#----------------------
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
##    ##    GasFit = Reader.objectiveFunction(Month, qi, Dinf, Di, n);
##    ##    GasNoOutliers = Gas.loc[~Gas.index.isin(OutlierIndex)];
##    ##    GasFitNoOutliers = GasFit.loc[~GasFit.index.isin(OutlierIndex)];
##    ##    Gas1 = (GasNoOutliers - GasFitNoOutliers)**2;
##    ##    Gas2 = (GasNoOutliers - GasNoOutliers.mean())**2;
##    ##    r2 = 1 - (Gas1.sum()/Gas2.sum());
##        Wells['PLEr2'][i] = r2;
###----------------------
print("FitDCA: Done");
### --- End FitDCA ---


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
print("Yearly: Done");
### --- End Yearly ---

### --- Regress --- ###
print("Regress: Begin");
#----------------------
for i in range(0, NumberOfWells):
#i = 512;
    print(i);
    Waste = Wells[['WasteYear1','WasteYear2','WasteYear3','WasteYear4','WasteYear5','WasteYear6','WasteYear7','WasteYear8','WasteYear9','WasteYear10']].loc[i];
    Gas = Wells[['GasYear1','GasYear2','GasYear3','GasYear4','GasYear5','GasYear6','GasYear7','GasYear8','GasYear9','GasYear10']].loc[i];
    num = ((i-1) % 9) + 1;
    if (len(Gas.dropna().index) >= 5) and (len(Waste.dropna().index) >= 5): #Changed because the function requirements. [4 paramenters + 1 header]
        NormalizedGas = Gas/Gas.mean();
        NormalizedWaste = Waste/Waste.mean();
        Data = Pd.DataFrame(data={'NormalizedGas': NormalizedGas.values, 'NormalizedWaste': NormalizedWaste.values}).dropna();
        [A,B,C,K,Q,V,r2] = Reader.fitGeneralisedLogistic(Data.NormalizedGas, Data.NormalizedWaste, Controls);
        C = C/Waste.mean()**V;
        Q = Q/Waste.mean()**V;
        B = B/Gas.mean();
        Wells.LogisticB.loc[i] = B;
        Wells.LogisticC.loc[i] = C;
        Wells.LogisticQ.loc[i] = Q;
        Wells.LogisticV.loc[i] = V;
        Wells.Logisticr2.loc[i] = r2;
#----------------------
print("Regress: Done");
### --- End Regress ---

Wells.to_csv('Result/Wells.csv', sep=',');
##Productions.to_csv('Result/Productions.csv', sep=',');
##Wastes.to_csv('Result/Wastes.csv', sep=',');
end = time.time();
print(end - start);
