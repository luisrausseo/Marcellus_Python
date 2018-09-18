### --- Config ---
import datetime as dt
from Library import Reader
import pandas as Pd

class Directories:
    InputDirectory = 'C:\\Users\\luisrausseo\\Desktop\\Project WW\\Data\\';
    Wells = InputDirectory + 'CSV\\Wells.csv';
    Productions = InputDirectory + 'CSV\\Productions.csv';
    Wastes = InputDirectory + 'CSV\\Wastes.csv';
    Facilities = InputDirectory + 'CSV\\Facilities.csv';
    DrillingKernelDensity = InputDirectory + 'GIS\\DrillingActivityKernel\\DrillingActivityKernel.txt';

class Dates:
    BaseDate = dt.datetime(2008,1,1);
    PaperDate = dt.datetime(2018,1,1);
    LastProductionDate = dt.datetime(2017,6,30);

Formations = ['marcellus', 'marcellus shale', 'marcellus shale (unconventional)'];
Wastes_Types = ['produced fluid', 'brine'];
### --- End Config ---

### --- Import ---
    #Colums with dates must be included in the parse_dates list.
Wells = Pd.read_csv(Directories.Wells,  infer_datetime_format='true', parse_dates=[16, 17, 18, 19, 20, 21]);
Productions = Pd.read_csv(Directories.Productions, infer_datetime_format='true', parse_dates=[1]);
Wastes = Pd.read_csv(Directories.Wastes, infer_datetime_format='true', parse_dates=[2,3]);
### --- End Import ---

### --- Select ---
Wells = Reader.get_rows(Wells, Formations, 'Formation');
Productions = Productions.loc[(Productions['Date']>= Dates.BaseDate)];
Wastes = Wastes.loc[(Wastes['BeginDate']>= Dates.BaseDate)];
Wastes = Reader.get_rows(Wastes, Wells['API'].values, 'API');
Wastes = Reader.get_rows(Wastes, Wastes_Types, 'Type');
### --- End Select ---

### --- Derive ---
NumberOfWells = len(Wells.index);
### --- End Derive ---

### --- DateToNum ---
ProductionAPIs = Productions['API'];
WasteAPIs = Wastes['API'];
#for i in range(0, NumberOfWells):
i = 1
WellAPI = Wells['API'].iloc[[i]].values
Index = ProductionAPIs.loc[ProductionAPIs.isin(WellAPI)].index.tolist();
ProductionDates = Productions['Date'].loc[Index];
FirstProductionDatePostBaseDate = min(ProductionDates);
LastProductionDatePostBaseDate = max(ProductionDates);
if(FirstProductionDatePostBaseDate != None):
    Wells['FirstProductionDatePostBaseDate'][i] = FirstProductionDatePostBaseDate;
    Wells['FirstProductionMonthsFromBaseDate'][i] = Reader.monthDifference(FirstProductionDatePostBaseDate, Dates.BaseDate);
    Productions['MonthsFromFirst'][Index] = Reader.monthDifference2(ProductionDates, FirstProductionDatePostBaseDate);
if(LastProductionDatePostBaseDate != None):
    Wells['LastProductionDatePostBaseDate'][i] = LastProductionDatePostBaseDate;
    Wells['LastProductionMonthsFromBaseDate'][i] = Reader.monthDifference(LastProductionDatePostBaseDate, Dates.BaseDate);

WasteIndex = WasteAPIs.loc[WasteAPIs.isin(WellAPI)].index.tolist();
BeginDate = Wastes['BeginDate'].loc[WasteIndex];
EndDate = Wastes['EndDate'].loc[WasteIndex];
if ~(BeginDate.empty):
    if(FirstProductionDatePostBaseDate != None):
        Wastes['BeginMonthsFromFirst'][WasteIndex] = Reader.monthDifference2(BeginDate, FirstProductionDatePostBaseDate);
    else:
        Wastes['BeginMonthsFromFirst'][WasteIndex] = Reader.monthDifference2(BeginDate, Wells['SpudDate'][i]);
if ~(EndDate.empty):
    if(FirstProductionDatePostBaseDate != None):
        Wastes['EndMonthsFromFirst'][WasteIndex] = Reader.monthDifference2(EndDate, FirstProductionDatePostBaseDate);
    else:
        Wastes['EndMonthsFromFirst'][WasteIndex] = Reader.monthDifference2(EndDate, Wells['SpudDate'][i]);

Wells['SpudMonthsFromBaseDate'][i] = Reader.monthDifference(Wells['SpudDate'][i], Dates.BaseDate);
Wells['CompletionMonthsFromBaseDate'][i] = Reader.monthDifference(Wells['CompletionDate'][i], Dates.BaseDate);
#Wastes['BeginMonthsFromBaseDate'][i] = Reader.monthDifference(Wastes['BeginDate'][i], Dates.BaseDate);
#Wastes['EndMonthsFromBaseDate'][i] = Reader.monthDifference(Wastes['EndDate'][i], Dates.BaseDate);
### --- End DateToNum ---


Wells.to_csv('Result/Wells_result.csv', sep=',');
Productions.to_csv('Result/Prod_result.csv', sep=',');
Wastes.to_csv('Result/Wastes_result.csv', sep=',');
