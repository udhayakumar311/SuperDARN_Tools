# Show status of the satellite conntection to south pole
# Parse satellite schedule of USAP and list last, current and next connection.
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 22:32:19 2016

@author: mguski
"""

# %% 
import urllib
import urllib.request
import datetime
from pytz import timezone

# %%
verbose = True
spSatURL = 'https://www.usap.gov/USAPgov/technology/documents/cel.txt'


# %% parse data from url

satRiseTimeList  = []
satSetTimeList   = []
completeDataSets = []

txt = urllib.request.urlopen(spSatURL)
isTableContend = False
for line in txt:
    line = line.decode('utf-8')
    if '-------------' in line: # this marks start and end of real data
            isTableContend = not isTableContend
            continue
    if isTableContend:
        elementsInLine = line.split(' ')
        elementsInLine = [el for el in elementsInLine if el != '']
        if len(elementsInLine) < 6:
            continue
        satRiseTimeList.append( datetime.datetime.strptime(elementsInLine[3], '%y/%j/%H%M%S'))
        duration = datetime.datetime.strptime(elementsInLine[5], '%H%M%S')
        satSetTimeList.append(satRiseTimeList[-1] + datetime.timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second))
        completeDataSets.append(elementsInLine)
        
nSats = len(satRiseTimeList)

# %% look for current, next and last satellites

now = datetime.datetime.utcnow()

idxVisibleSat = [iSat for iSat in range(nSats) if now > satRiseTimeList[iSat] and now < satSetTimeList[iSat]]

#last sat
timeDiffSinceSatSet = [now - setTime for setTime in satSetTimeList]
idxLastSat = 0
for iSat in range(1,nSats):
    if (timeDiffSinceSatSet[iSat] < timeDiffSinceSatSet[idxLastSat]) and timeDiffSinceSatSet[iSat] > datetime.timedelta(0):
        idxLastSat = iSat
        
# next sat
timeDiffToRise = [riseTime - now  for riseTime in satRiseTimeList]
idxNextRise = nSats-1
for iSat in range(nSats-2,0,-1):
    if (timeDiffToRise[iSat] < timeDiffToRise[idxNextRise]) and timeDiffToRise[iSat] > datetime.timedelta(0):
        idxNextRise = iSat

# print info
if verbose:
    print("UTC time: {}".format(now))
    print('\t Found data for {} satellites.\n'.format(nSats))
    
    if len(idxVisibleSat) == 0:
        print("No satellite available at the moment")
    else:
        print('Available Satellites at the moment ({}):'.format(len(idxVisibleSat)))
        print("\t time left: {}".format(-timeDiffSinceSatSet[idxNextRise]))

#    for iSat in idxVisibleSat:
#        print(completeDataSets[iSat])
    print("\n")
    
   
    print('Next Satellite:')
    print("\t rise at {}".format(satRiseTimeList[idxNextRise]))
    print("\t rise in {}".format(timeDiffToRise[idxNextRise]))
    print("\t online for {}".format(satSetTimeList[idxNextRise] - satRiseTimeList[idxNextRise]))
    print("\t {}".format(completeDataSets[idxNextRise]))
    
    print('Last Satellite:')
    print("\t set at {}".format(satRiseTimeList[idxLastSat]))
    print("\t set before {}".format(timeDiffSinceSatSet[idxLastSat]))
    print("\t was online for {}".format(satSetTimeList[idxLastSat] - satRiseTimeList[idxLastSat]))
    print("\t {}".format(completeDataSets[idxLastSat])  ) 