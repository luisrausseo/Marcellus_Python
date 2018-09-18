import datetime as dt
import math
from Library import Reader
from Library import functionFiles
import pandas as pd
import time
import numpy as np    
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
import gdal
from gdalconst import * 

def Import(Directories):
	print("Import: Begin")
	# Columns with dates must be included in the parse_dates list.
	Wells = pd.read_csv(Directories.Wells,  infer_datetime_format='true', parse_dates=[16, 17, 18, 19, 20, 21])
	Productions = pd.read_csv(Directories.Productions, infer_datetime_format='true', parse_dates=[1])
	Wastes = pd.read_csv(Directories.Wastes, infer_datetime_format='true', parse_dates=[2, 3])
	Raster_h = gdal.Open(Directories.DrillingKernelDensity, GA_ReadOnly)
	print("Done")
	return [Wells, Productions, Wastes, Raster_h]


def Select(Wells, Productions, Wastes, Dates, Formations, Wastes_Types):
	print("Select: Begin")
	Wells = Reader.get_rows(Wells, Formations, 'Formation')
	Productions = Productions.loc[(Productions.Date >= Dates.BaseDate)]
	Wastes = Wastes.loc[(Wastes.BeginDate >= Dates.BaseDate)]
	Wastes = Reader.get_rows(Wastes, Wells.API.values, 'API')
	Wastes = Reader.get_rows(Wastes, Wastes_Types, 'Type')
	print("Done")
	return [Wells, Productions, Wastes]

def DateToNum(Wells, Productions, Wastes, NumberOfWells, Dates):
	print("DateToNum: Begin")
	ProductionAPIs = Productions.API
	WasteAPIs = Wastes.API
	for i in range(0, NumberOfWells):
		WellAPI = Wells.API.iloc[i]
		ProductionDates = Productions.Date.ix[ProductionAPIs == WellAPI]
		#Progress status (every 10%)
		if (((i/NumberOfWells)*100) % 10 == 0):
			print("{0:.0f}%".format((i/NumberOfWells)*100))
		if (len(ProductionDates.index) != 0):
			FirstProductionDatePostBaseDate = [min(ProductionDates)]
			LastProductionDatePostBaseDate = [max(ProductionDates)]
			
			if(FirstProductionDatePostBaseDate != None):
				Wells.set_value(i, 'FirstProductionDatePostBaseDate', FirstProductionDatePostBaseDate[0])
				Wells.set_value(i, 'FirstProductionMonthsFromBaseDate', functionFiles.monthDifference(FirstProductionDatePostBaseDate[0], Dates.BaseDate))
				Productions.set_value(ProductionDates.index, 'MonthsFromFirst', functionFiles.monthDifference5(ProductionDates, FirstProductionDatePostBaseDate[0]))
		
			if (LastProductionDatePostBaseDate != None):
				Wells.set_value(i, 'LastProductionDatePostBaseDate', LastProductionDatePostBaseDate[0])
				Wells.set_value(i, 'LastProductionMonthsFromBaseDate', functionFiles.monthDifference(LastProductionDatePostBaseDate[0], Dates.BaseDate))
				
			WasteIndex = WasteAPIs.ix[WasteAPIs == WellAPI].index
			BeginDate = Wastes.BeginDate.ix[WasteIndex]
			EndDate = Wastes.EndDate.ix[WasteIndex]
			if ~(BeginDate.empty):
				if(FirstProductionDatePostBaseDate != None):
					Wastes.set_value(WasteIndex, 'BeginMonthsFromFirst', functionFiles.monthDifference5(BeginDate, FirstProductionDatePostBaseDate[0]))
				else:
					Wastes.set_value(WasteIndex, 'BeginMonthsFromFirst', functionFiles.monthDifference5(BeginDate, Wells.SpudDate[i]))
			if ~(EndDate.empty):
				if(FirstProductionDatePostBaseDate != None):
					Wastes.set_value(WasteIndex, 'EndMonthsFromFirst', functionFiles.monthDifference5(EndDate, FirstProductionDatePostBaseDate[0]))
				else:
					Wastes.set_value(WasteIndex, 'EndMonthsFromFirst', functionFiles.monthDifference5(EndDate, Wells.SpudDate[i]))
	                
	Wells.set_value(Wells.index, 'SpudMonthsFromBaseDate', functionFiles.monthDifference5(Wells.SpudDate, Dates.BaseDate))
	Wells.set_value(Wells.index, 'CompletionMonthsFromBaseDate', functionFiles.monthDifference5(Wells.CompletionDate, Dates.BaseDate))
	Wastes.set_value(Wastes.index, 'BeginMonthsFromJan2008', functionFiles.monthDifference5(Wastes.BeginDate, Dates.BaseDate))
	Wastes.set_value(Wastes.index, 'EndMonthsFromJan2008', functionFiles.monthDifference5(Wastes.EndDate, Dates.BaseDate))
	print("Done")
	return [Wells, Productions, Wastes]
	
	
def FitDCA(Wells, Productions, NumberOfWells, Controls):
	print("FitDCA: Begin")
	WellAPIs = Wells.API
	for i in range(0, NumberOfWells):
		#Progress status (every 10%)
		if (((i/NumberOfWells)*100) % 10 == 0):
			print("{0:.0f}%".format((i/NumberOfWells)*100))
		WellProduction = Productions.loc[Productions.API.isin([WellAPIs[i]])]
		Gas = WellProduction.Gas
		Month = WellProduction.MonthsFromFirst
		NormalizedGas = Gas/Gas.mean()
		if ~(Gas.empty) and (len(Gas.index)>5) and (Gas.mean() != 0):
			[qi,Di,Dinf,n,r2,OutlierIndex] = functionFiles.fitPowerLawExponential(NormalizedGas, Month, Controls)
			Wells.set_value(i, 'PLEqi', qi*Gas.mean())
			Wells.set_value(i, 'PLEDi', Di)
			Wells.set_value(i, 'PLEDinf', Dinf)
			Wells.set_value(i, 'PLEn', n)
			Wells.set_value(i, 'PLEr2', r2)
	print("Done")
	return Wells
	
	
def Yearly(Wells, Productions, Wastes, NumberOfWells):
	print("Yearly: Begin")
	WellAPIs = Wells.API
	for i in range(0, NumberOfWells):
		#Progress status (every 10%)
		if (((i/NumberOfWells)*100) % 10 == 0):
			print("{0:.0f}%".format((i/NumberOfWells)*100))
		WellAPI = WellAPIs[i]
		WellGas = Productions.loc[Productions.API.isin([WellAPI])]
		WellWaste = Wastes.loc[Wastes.API.isin([WellAPI])]
		Well = Wells.iloc[i]
		if not (WellGas.Gas.empty):
			FirstCalendarYear = Well.FirstProductionDatePostBaseDate.year;
			LastCalendarYear = Well.LastProductionDatePostBaseDate.year;
			if not ((math.isnan(FirstCalendarYear)) or (math.isnan(LastCalendarYear))):
				for Year in range(FirstCalendarYear,LastCalendarYear+1):
					YearlyGas = WellGas.Gas.loc[(WellGas.Date.dt.year == Year)].sum()
					if (YearlyGas > 0):
						Wells.set_value(i, 'Gas' + str(Year), YearlyGas)
		if not (type(Well.LastProductionDatePostBaseDate) is pd.tslib.NaTType):
			MonthsOfProduction = functionFiles.monthDifference(Well.LastProductionDatePostBaseDate, Well.FirstProductionDatePostBaseDate)
			Month_val = int(MonthsOfProduction/12) + 1
			for Year in range(1,Month_val+1):
				if (Year < Month_val):
					YearlyGas = WellGas.Gas.loc[WellGas.MonthsFromFirst.isin(range((Year - 1) * 12, (Year * 12) + 1))].sum()
				else:
					YearlyGas = WellGas.Gas.loc[WellGas.MonthsFromFirst.isin(range((Year - 1) * 12, MonthsOfProduction + 1))].sum()
				if (YearlyGas > 0):
					Wells.set_value(i, 'GasYear' + str(Year), YearlyGas)
			if not (WellWaste.Volume.empty):
				FirstWasteDate = min(WellWaste.BeginDate)
				LastWasteDate = max(WellWaste.EndDate)
				if not ((math.isnan(FirstWasteDate.year)) or (math.isnan(LastWasteDate.year))):
					for Year in range(FirstWasteDate.year, LastWasteDate.year + 1):
						YearlyWaste = WellWaste.Volume.loc[(WellWaste.BeginDate.dt.year == Year)].sum()
						if (YearlyWaste > 0):
							Wells.set_value(i, 'Waste' + str(Year), YearlyWaste)
					Month_val = int(max(WellWaste.EndMonthsFromFirst) / 12) + 1
					for Year in range(1, Month_val + 1):
						if (Year < Month_val):
							EndOfTheYear = Year * 12
						else:
							EndOfTheYear = max(WellWaste.EndMonthsFromFirst)
						BeginOfTheYear = (Year - 1) * 12 + 1
						Frac_1 = (WellWaste.BeginMonthsFromFirst.loc[(WellWaste.BeginMonthsFromFirst >= BeginOfTheYear)] * (EndOfTheYear - WellWaste.BeginMonthsFromFirst + 1))/(WellWaste.EndMonthsFromFirst - WellWaste.BeginMonthsFromFirst)
						Frac_2 = (WellWaste.BeginMonthsFromFirst.loc[(WellWaste.BeginMonthsFromFirst < BeginOfTheYear)] * (WellWaste.EndMonthsFromFirst - BeginOfTheYear))/(WellWaste.EndMonthsFromFirst - WellWaste.BeginMonthsFromFirst)
						Fraction = Frac_1.fillna(0) + Frac_2.fillna(0)
						Fraction.loc[(Fraction > 1)] = 1
						Fraction.loc[(Fraction < 0)] = 0
						YearlyWaste = WellWaste.Volume * Fraction
						YearlyWaste = YearlyWaste.sum()
						if (YearlyWaste > 0):
							Wells.set_value(i, 'WasteYear' + str(Year), YearlyWaste) 
	print("Done")
	return Wells
	

def Regress(Wells, NumberOfWells, Controls):
	print("Regress: Begin")
	for i in range(0, NumberOfWells):
	    #Progress status (every 10%)
		if (((i/NumberOfWells)*100) % 10 == 0):
			print("{0:.0f}%".format((i/NumberOfWells)*100))
		Waste = Wells[['WasteYear1', 'WasteYear2', 'WasteYear3', 'WasteYear4', 'WasteYear5', 'WasteYear6', 'WasteYear7',
					   'WasteYear8', 'WasteYear9', 'WasteYear10']].loc[i]
		Gas = Wells[['GasYear1', 'GasYear2', 'GasYear3', 'GasYear4', 'GasYear5', 'GasYear6', 'GasYear7', 'GasYear8',
					 'GasYear9', 'GasYear10']].loc[i]
		num = ((i-1) % 9) + 1
		# Changed because the function requirements. [4 parameters + 1 header]
		if (len(Gas.dropna().index) >= 5) and (len(Waste.dropna().index) >= 5):
			NormalizedGas = Gas/Gas.mean()
			NormalizedWaste = Waste/Waste.mean()
			Data = pd.DataFrame(data={'NormalizedGas': NormalizedGas.values,
									  'NormalizedWaste': NormalizedWaste.values}).dropna()
			[A, B, C, K, Q, V, r2] = functionFiles.fitGeneralisedLogistic(Data.NormalizedGas, Data.NormalizedWaste, Controls)
			C = C / Waste.mean() ** V
			Q = Q / Waste.mean() ** V
			B = B / Gas.mean()
			Wells.set_value(i, 'LogisticB', B)
			Wells.set_value(i, 'LogisticC', C)
			Wells.set_value(i, 'LogisticQ', Q)
			Wells.set_value(i, 'LogisticV', V)
			Wells.set_value(i, 'Logisticr2', r2)
	print("Done")
	return Wells
	
	
def Impute(Wells, Productions, Wastes, NumberOfWells, Dates):
	print("Impute: Begin")
	for i in range(0, NumberOfWells):
		#Progress status (every 10%)
		if (((i/NumberOfWells)*100) % 10 == 0):
			print("{0:.0f}%".format((i/NumberOfWells)*100))
		Well = Wells.iloc[i]
		if (Well.Status == "active") and (Well.PLEr2 > 0.25):
			MonthsToJan2018 = functionFiles.monthDifference(Dates.PaperDate, Well.FirstProductionDatePostBaseDate) + 1
			aux_num1 = [0, 13, 25, 37, 49, 61]
			aux_num2 = [12, 24, 36, 48, 60 ,72]	
			for j in range(0, 6):
				# Range goes until the previous of the last number, so 1 is addedd to the last number
				GasYear = functionFiles.powerLawExponential(range(MonthsToJan2018 + aux_num1[j], MonthsToJan2018 + aux_num2[j] + 1), 
				                                            Well.PLEqi, Well.PLEDinf, Well.PLEDi, Well.PLEn)
				Well.set_value('Gas' + str(2018 + j), GasYear.sum())
			if (Well.Logisticr2 > 0.25):
				for k in range(0, 6):
					WasteYear = functionFiles.generalisedLogistic(Well['Gas' + str(2018 + k)], Well.LogisticB, Well.LogisticC,
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
			ProductionsDates = Productions.loc[Productions.API.isin([Well.API])]
			FirstProductionDate = min(ProductionsDates.Date)
			LastProductionDate = max(ProductionsDates.Date)
			if (Well.PLEr2 > 0.25):
				for Year in range(math.ceil((Reader.monthDifference(LastProductionDate, FirstProductionDate) + 1) / 12), 16):
					YGas = functionFiles.powerLawExponential(range((Year - 1) * 12 + 1, Year * 12 + 1), Well.PLEqi, Well.PLEDinf, Well.PLEDi, Well.PLEn)
					YearlyGas = YGas.sum()
					if (Well.Logisticr2 > 0.25):
						YearlyWaste = functionFiles.generalisedLogistic(YearlyGas, Well.LogisticB, Well.LogisticC, Well.LogisticQ, Well.LogisticV)
					else:
						YearlyWaste = np.nan
					Well.set_value('GasYear' + str(Year), YearlyGas)
					Well.set_value('WasteYear' + str(Year), YearlyWaste)
					if not (Well.FlagLastYear is 1):
						MonthsOfProduction = functionFiles.monthDifference(Well.LastProductionDatePostBaseDate, Well.FirstProductionDatePostBaseDate)
						LastYear = int(MonthsOfProduction / 12) + 1
						if (LastYear < 11):
							GasLastYear = Well['GasYear' + str(LastYear)]
						if (GasLastYear > 0):
							if (Well.PLEr2 > 0.25):
								MonthsOfProduction = int(Well.LastProductionMonthsFromBaseDate - Well.FirstProductionMonthsFromBaseDate) + 1
								AdditionalGasLastYear = functionFiles.powerLawExponential(range(MonthsOfProduction + 1, (int(MonthsOfProduction / 12) + 1) * 12 + 1), Well.PLEqi, Well.PLEDinf, Well.PLEDi, Well.PLEn)
							else:
								AdditionalGasLastYear = GasLastYear
							Well.set_value('GasYear' + str(LastYear), GasLastYear + AdditionalGasLastYear.sum())
						WastesEnd = Wastes.loc[Wastes.API.isin([Well.API])]
						if not (WastesEnd.EndMonthsFromFirst.empty):
							LastYear2 = int(max(WastesEnd.EndMonthsFromFirst) / 12) + 1
							if (LastYear2 == LastYear):
								if (Well.Logisticr2 > 0.25):
									AdditionalWasteLastYear = functionFiles.generalisedLogistic(AdditionalGasLastYear.sum(), Well.LogisticB, Well.LogisticC, Well.LogisticQ, Well.LogisticV)
								else:
									AdditionalWasteLastYear = Waste2017;
								Well.set_value('WasteYear' + str(LastYear2), Well['WasteYear' + str(LastYear2)] + AdditionalWasteLastYear) # ?????
						Well.set_value('FlagLastYear', 1)
		Wells.iloc[i] = Well
	print("Done")
	return Wells	
	
	
