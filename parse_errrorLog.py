#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 12:57:31 2016

@author: mguski
"""

# %%


import re
import datetime

UNKNOWN  = -1
DEBUG    = 10
INFO     = 20
WARNING  = 30 
ERROR    = 40
CRITICAL = 50
FATAL    = 60 



# %% 
class scanClass():
    reObj_startScan           = re.compile("Starting scan.")
    reObj_ProgramStart        = re.compile("PROGRAM START->(.*)")
    reObj_endSND              = re.compile("Polling SND for exit.")

    reObj_doClearFreqSearch   = re.compile("Doing (?:SND ){0,1}clear frequency search.")
  #  reObj_skipClearFreqSearch = re.compile("Clear Search Skipped, next search in .* secs")
    reObj_clearFreqpar        = re.compile("FRQ: (\d*) (\d*)")

    reObj_nSequances          = re.compile("Number of (?:SND ){0,1}sequences: (\d*)")     
    reObj_integrateBeam       = re.compile("Integrating (?:SND ){0,1}beam:(\d{1,2}?) intt:(\d*)s.(\d*)us .*") 
    reObj_txFreqAndNoise      = re.compile("Transmitting (?:SND ){0,1}on: (\d*) \(Noise=(.*)\)")
    reObj_snd_beamCount       = re.compile("SBC: (\d*)  SFC: (\d*)")
    reObj_newOptFreq          = re.compile("New Opt Freq; (\d*)")
    reObj_connectionInfos     = re.compile("Error attaching to .*|Attached to .*")
    
    
    # just ignore this messages
    passLogList = ["Starting Integration.", "Setting SND beam.", "Sending SND messages.", "Opening new files.", "Waiting for scan boundary.", "Clear Search Skipped, next search in .* secs"]
    reObjList_pass = [re.compile(pattern) for pattern in passLogList]
    
    def __init__(self):
        self.isStartOfScan = False
        self.beamNumber = -1
        self.intsc = -1
        self.intus = -1
        self.clearFreqSearchDone = False
        self.clearFreq_start = -1
        self.clearFreq_range = -1
        self.tx_freq  = -1
        self.noise = -1
        self.nSequences = -1
        self.sequenceFinished = False
        self.newOptFreq = -1
        
        self.program_start = ""
        self.connectionInfos= []
        
        self.snd_mode = False
        self.snd_beam_count = -1
        self.snd_freq_count = -1
        
        self.data_received_rawacfwrite = False
        self.data_received_fitacfwrite = False
        self.data_received_rtserver    = False
        
        self.date_start = []
        self.date_end   = []
        
        self.set_scan_name()
        
    def parse_log_msg(self, msg, date):
        if self.reObj_startScan.match(msg):
            self.isStartOfScan = True
        elif any([re.match(msg) for re in self.reObjList_pass]):
            pass 
        elif self.reObj_endSND.match(msg):
            self.sequenceFinished = True   
        elif self.reObj_ProgramStart.match(msg):
            self.program_start = self.reObj_ProgramStart.search(msg).group(1)

        elif self.reObj_doClearFreqSearch.match(msg):
            self.clearFreqSearchDone = True
        elif self.reObj_nSequances.match(msg):
            self.nSequences = int(self.reObj_nSequances.search(msg).group(1))
            self.sequenceFinished = not self.snd_mode 
        elif self.reObj_integrateBeam.match(msg):
            res = self.reObj_integrateBeam.search(msg)
            self.beamNumber = float(res.group(1))
            self.intsc      = float(res.group(2))
            self.intus      = float(res.group(3))
            self.snd_mode = re.match(".* SND .*", msg) != None
            
        elif self.reObj_clearFreqpar.match(msg):
            res = self.reObj_clearFreqpar.search(msg)
            self.clearFreq_start = float(res.group(1))
            self.clearFreq_range = float(res.group(2))
            
        elif self.reObj_snd_beamCount.match(msg):
            res = self.reObj_snd_beamCount.search(msg)
            self.snd_beam_count = float(res.group(1))
            self.snd_freq_count = float(res.group(2))

        elif self.reObj_txFreqAndNoise.match(msg):
            res = self.reObj_txFreqAndNoise.search(msg)
            self.tx_freq = float(res.group(1))
            self.noise   = float(res.group(2))
        elif self.reObj_newOptFreq.match(msg):
            res = self.reObj_newOptFreq.search(msg)
            self.new_opt_freq = float(res.group(1))
        elif self.reObj_connectionInfos.match(msg):
            self.connectionInfos.append(msg)
            
        else:
            print("Unknown log msg:{} {} ".format(date, msg))
            import time            
            time.sleep(1)
            date = []

        self.add_date(date)
            
    def data_received(self, process):
        if process == 'rawacfwrite':
            self.data_received_rawacfwrite = True
        elif process == 'fitacfwrite':
            self.data_received_fitacfwrite = True 
        elif process == 'rtserver':
            self.data_received_rtserver = True 

            
    def add_date(self,date):
        if date == []:
            return
            
        if self.date_start == []:
           self.date_start = date
        else:
           self.date_start = min(self.date_start, date)
           
        if self.date_end == []:
           self.date_end = date
        else:
           self.date_end = max(self.date_end, date)
           


class rbspscanSequence(scanClass):
    def set_scan_name(self):
        self.program_name = "rbspscan"

class normalsoundFastSequence(scanClass):
    def set_scan_name(self):
        self.program_name = "normalsound (fast)"

class normalscanFastSequence(scanClass):
    def set_scan_name(self):
        self.program_name = "normalscan (fast)"


class themisscanSequence(scanClass):
    def set_scan_name(self):
        self.program_name = "themisscan"
        
        



# %%
controlProgramNames = ["normalsound (fast)","normalscan (fast)", "rbspscan", "themisscan" ]

dataProcesses = ["rawacfwrite","fitacfwrite", "rtserver" ]
dataProcessIgnoreLogs = ["Opening file." , "Closing file.", "Reset.", "Child server process starting"]
# %%


fileName = "errlog.kod.c.20161230"
#fileName = "errlog.adw.a.20161221"


errorLogFileName = '/home/mguski/Documents/exampleLogFiles/' + fileName

f = open(errorLogFileName)

errorLogFileName = "/data/ros/errlog/" + fileName # TODO remove later
nLines = 0

scanList = []

for line in f:
    line = line[:-1]
    nLines +=1
    if line.startswith(errorLogFileName) or len(line) == 0: # skip open messsage
        continue 
    
    date = datetime.datetime.strptime(line[:24], '%a %b %d %H:%M:%S %Y')
    processName, msg = line[26:].split(":",1)
    processName = processName.strip()
    
    if (processName in controlProgramNames):
        # like this re.sub(" \((.)", r'_\1', "abc (def)") ?
        if processName == "normalsound (fast)":
            if len(scanList) == 0  or scanList[-1].sequenceFinished  or not isinstance(scanList[-1],  normalsoundFastSequence):
                scanList.append(normalsoundFastSequence())    
            scanList[-1].parse_log_msg(msg,date)
        elif processName == "rbspscan":
            if len(scanList) == 0  or scanList[-1].scanList  or not isinstance(scanList[-1],  rbspscanSequence):
                scanList.append(rbspscanSequence())    
            scanList[-1].parse_log_msg(msg,date)
        elif processName == "themisscan":
            if len(scanList) == 0  or scanList[-1].sequenceFinished  or not isinstance(scanList[-1],  themisscanSequence):
                scanList.append(themisscanSequence())    
            scanList[-1].parse_log_msg(msg,date)
        elif processName == "normalscan (fast)":
            if len(scanList) == 0  or scanList[-1].sequenceFinished  or not isinstance(scanList[-1],  normalscanFastSequence):
                scanList.append(normalscanFastSequence())    
            scanList[-1].parse_log_msg(msg,date)
        else:
            print("Process: {} not implemnted".format(processName))

            
            
    elif processName in dataProcesses:
        if msg == "Received Data.":
            scanList[-1].data_received( processName)
        elif msg in dataProcessIgnoreLogs  or msg.endswith(" Open Connection.") or msg.endswith(" Close Connection."):
            pass
        else:
            print("Unknow msg: " + line)
    else:
        print("Unknown process: {}".format(processName))
        import time 
        time.sleep(1)

f.close()   


print("Finished:\n  nLines: {}\n  nSequences: {}\n\n".format(nLines, len(scanList)))

# %%
import matplotlib.pyplot as plt
import numpy as np




fig = plt.figure(figsize=[16, 10])

# -%% plot some things

timeVec = [seq.date_start  for seq in scanList]


scanChangeList = [[scanList[0].program_name, scanList[0].date_start]]
for iScan in range(1,len(scanList)):
    if scanChangeList[-1][0] != scanList[iScan].program_name:
        scanChangeList.append([scanList[iScan].program_name, scanList[iScan].date_start])
scanChangeList.append(["End of Log file", timeVec[-1]])

ax = plt.subplot2grid((20,1), (0,0))
for iScan in range(len(scanChangeList)-1):
    ax.barh(1,  (scanChangeList[iScan+1][1] - scanChangeList[iScan][1]).total_seconds()/60/60/24, left=scanChangeList[iScan][1], align='center')
    textPosition = scanChangeList[iScan][1] +  (scanChangeList[iScan+1][1] - scanChangeList[iScan][1])/2
    ax.text(textPosition, 1, scanChangeList[iScan][0] , rotation=0, backgroundcolor='w', alpha=0.5, ha='center', va='center' )
    
ax.set_xlim(timeVec[0], timeVec[-1])
ax.axis('off')
plt.title(errorLogFileName.split("/")[-1][7:12] + "  " + str(timeVec[0].date()))

# -%%
ax = plt.subplot2grid((20,1), (1,0), rowspan=3)

nSeqPerSecList = [seq.nSequences for seq in scanList]
plt.plot(timeVec, nSeqPerSecList, "+")
plt.grid(True)
ax.set_xticklabels([])

ax.set_ylabel("seq / sec")

ax = plt.subplot2grid((5,1), (1,0))
freqVec = [seq.tx_freq/1000 for seq in scanList]
plt.plot(timeVec, freqVec, '+')
plt.grid(True)
ax.set_xticklabels([])
ax.set_ylabel("Freq in MHz")


ax = plt.subplot2grid((5,1), (2,0))
#noiseVec = 10*np.log10([seq.noise for seq in scanList])
noiseVec = [seq.noise for seq in scanList]
plt.plot(timeVec, noiseVec, 'o')
plt.grid(True)
ax.set_xticklabels([])
ax.set_ylabel("Noise in dB ???")


ax = plt.subplot2grid((5,1), (3,0))
plotData = [seq.beamNumber for seq in scanList]
plt.plot(timeVec, plotData, '|')
plt.grid(True)
ax.set_xticklabels([])
ax.set_ylabel("beam number")


ax = plt.subplot2grid((5,1), (4,0))
plotData = [seq.snd_beam_count for seq in scanList]
plt.plot(timeVec, plotData, 'x', label="snd_beam_count")
plotData = [seq.snd_freq_count for seq in scanList]
plt.plot(timeVec, plotData, '+', label="snd_freq_count")


ax = plt.subplot2grid((5,1), (4,0))
plotData = [seq.intus/1e6 for seq in scanList]
plt.plot(timeVec, plotData, label="insus", linewidth=2)
plotData = [seq.intsc for seq in scanList]
plt.plot(timeVec, plotData, label="inssc", linewidth=2)
ax.set_ylim(ax.get_ylim()[0]-0.1 , ax.get_ylim()[1]+0.1)

plt.grid(True)

ax.set_ylabel("intt in s")
plt.legend()



plt.show()

# %%
plotData = [(seq.date_end - seq.date_start).total_seconds() for seq in scanList]