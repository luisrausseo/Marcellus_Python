import datetime as dt
import math
from Library import Reader
from Library import scriptFiles
from Library import functionFiles
import pandas as pd
import time
import numpy as np    
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
import gdal
from gdalconst import * 
import matplotlib.mlab as mlab


# --- Config ---
print("Config: Begin")
start = time.time()


class Directories:
    InputDirectory = '/home/lrausseo/MEGAsync/Project WW/Data/'
    
    #Wells = InputDirectory + 'CSV/Wells.csv'
    #Productions = InputDirectory + 'CSV/Productions.csv'
    #Wastes = InputDirectory + 'CSV/Wastes.csv'
    
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


# --- Import ---
[Wells, Productions, Wastes, Raster_h] = scriptFiles.Import(Directories)


# --- Select ---
[Wells, Productions, Wastes] = scriptFiles.Select(Wells, Productions, Wastes, Dates, Formations, Wastes_Types)


# --- Derive ---
print("Derive: Begin")
NumberOfWells = len(Wells.index)
gt = Raster_h.GetGeoTransform()
class Raster:
	GridSize = gt[1]
	### WHAT?
print("Done")


# --- DateToNum ---
#[Wells, Productions, Wastes] = scriptFiles.DateToNum(Wells, Productions, Wastes, NumberOfWells, Dates)


# --- FitDCA ---
#Wells = scriptFiles.FitDCA(Wells, Productions, NumberOfWells, Controls)


# --- Yearly ---
#Wells = scriptFiles.Yearly(Wells, Productions, Wastes, NumberOfWells)


# --- Regress ---
#Wells = scriptFiles.Regress(Wells, NumberOfWells, Controls)


# --- Impute ---
#Wells = scriptFiles.Impute(Wells, Productions, Wastes, NumberOfWells, Dates)


# --- NewDrills ---
print("NewDrills: Begin")
Wells_nd = Wells.ix[range(0, NumberOfWells + 1)]
SelectedWells = Wells_nd.loc[(Wells_nd.SpudDate >= Dates.BaseDate)]
GroupData = SelectedWells
SpudYear = GroupData.SpudDate.dt.year + ((1/12) * (GroupData.SpudDate.dt.month + 1)) + ((1/365.25) * GroupData.SpudDate.dt.day)
# Fix SpudYear into logistic mixture with 3 samples
[n, bins, patches] = plt.hist(SpudYear, bins=40, edgecolor='black')
'''
# Fix bins to be at center
T_centers = []
for i in range(0,len(T)-1):
	T_centers.append((T[i]+ ((T[i+1] - T[i])/2)))
'''
LogisticMixtureModel = GaussianMixture(3, means_init=[2011.2, 2014.5, 2018])
LMM = LogisticMixtureModel.fit(X = np.expand_dims(SpudYear.values, 1))
LMM_x = np.linspace(min(SpudYear), max(SpudYear) + 5, 2000)
LMM_y = np.exp(LMM.score_samples(LMM_x.reshape(-1, 1)))
#~ #Creates new well
#~ Ramainder = 0
#~ WellNumber = 0
#~ for Month in range(1, (6*12) + 1):
	#~ NumberOfNewWells = LMM.predict(2018 + Month / 12) + Ramainder
	#~ Ramainder = NumberOfNewWells % 1
	#~ NumberOfNewWells = 	int(math.floor(NumberOfNewWells))
	#~ CurrentDate = functionFiles.GetDateTime(Month)
	#~ for j in range(0, NumberOfNewWells + 1):
		#~ WellAPI = 'AJ0000' + str(1000 + WellNumber)
		#~ WellNumber += 1
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
#Wells.to_csv('Result/Wells.csv', sep=',', index=False)
#Productions.to_csv('Result/Productions.csv', sep=',', index=False)
#Wastes.to_csv('Result/Wastes.csv', sep=',', index=False)
print("Done")
# --- Save Results End---



end = time.time()
print(end - start)
