#!/usr/bin/python2.7


# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 15:40:22 2017

@author: mguski
"""

import dmap
import datetime
import matplotlib.pyplot as plt
import os
import re
# %%

dataPath = "sampleData"

year = 2017
month = 1
#day = 1
radarList = ["ade.a", "adw.a"]
nRadars = len(radarList)
allFilesInDir = os.listdir(dataPath)
allFilesInDir.sort()

for day in range(1,12):

    fig = plt.figure(figsize=[18, 10])
    
    for iRadar, radar in enumerate(radarList):
        
        allFiles = [file for file in allFilesInDir if re.match("{0:04d}{1:02d}{2:02d}\..*\.{3}\.fitacf".format(year, month, day, radar), file) ]
        # %
        dateList = []
        nAveList = []
        nValidRangesList = []
        nTotalRangesList = []
        noiseSkyList = []
        
        scanChangeList = None
        
        for fileName in allFiles:
            print(fileName)
            records = dmap.parse_dmap_format_from_file(os.path.join(dataPath, fileName))
            for iRec, rec  in enumerate(records):
                nAveList.append(rec[b'nave'])
                nTotalRangesList.append(rec[b'nrang'])
                noiseSkyList.append(rec[b'noise.sky'])
                if b'slist' in rec.keys():
                    nValidRangesList.append(len(rec[b'slist']))
                else:
                    nValidRangesList.append(-1)
                dateList.append(datetime.datetime(rec[b'time.yr'], rec[b'time.mo'], rec[b'time.dy'], rec[b'time.hr'], rec[b'time.mt'], rec[b'time.sc']))
                
                if scanChangeList != None:
                    if scanChangeList[-1][0] != rec[b'combf']:
                        scanChangeList.append([ rec[b'combf'],  dateList[-1]])
                else: # first entry
                    scanChangeList = [ [ rec[b'combf'], dateList[0]]]
                
        scanChangeList.append(["End of Log file", dateList[-1]])
        # %
        ax = plt.subplot2grid((20,nRadars), (0,iRadar))
        for iScan in range(len(scanChangeList)-1):
            ax.barh(1,  (scanChangeList[iScan+1][1] - scanChangeList[iScan][1]).total_seconds()/60/60/24, left=scanChangeList[iScan][1], align='center')
            textPosition = scanChangeList[iScan][1] +  (scanChangeList[iScan+1][1] - scanChangeList[iScan][1])/2
            ax.text(textPosition, 1, scanChangeList[iScan][0].decode("utf-8") , rotation=0, backgroundcolor='w', alpha=0.5, ha='center', va='center' )    
        ax.set_xlim(dateList[0], dateList[-1])
        ax.axis('off')
        plt.title("{0} {1:04d}-{2:02d}-{3:02d}".format(radar,year, month, day))
        
        ax = plt.subplot2grid((20,nRadars), (1,iRadar), rowspan=6)
        plt.plot(dateList, nAveList, '+')
        ax.set_ylabel("seq / sec")
        plt.grid(True)
        ax.set_xticklabels([])
        
        
        
        ax = plt.subplot2grid((20,nRadars), (7,iRadar), rowspan=6)
        plt.plot(dateList, nValidRangesList, '+', label='valid ranges')
        plt.plot(dateList, nTotalRangesList,label='total ranges')
        plt.grid(True)
        plt.legend()
        ax.set_xticklabels([])
        
        ax = plt.subplot2grid((20,nRadars), (13,iRadar), rowspan=6)
        plt.semilogy(dateList, noiseSkyList,'+')
        plt.grid(True)
        ax.set_ylabel("noise.sky")
    
    
    fig.savefig("adak_{0:04d}-{1:02d}-{2:02d}".format(year, month, day))
    plt.close(fig)
# %%
