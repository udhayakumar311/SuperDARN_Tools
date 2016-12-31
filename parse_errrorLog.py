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
    reObj_nSequances          = re.compile("Number of (?:SND ){0,1}sequences: (\d*)")     
    reObj_integrateBeam       = re.compile("Integrating (?:SND ){0,1}beam:(\d{1,2}?) intt:(\d*)s.(\d*)us .*") 
    reObj_clearFreqpar        = re.compile("FRQ: (\d*) (\d*)")
    reObj_txFreqAndNoise      = re.compile("Transmitting (?:SND ){0,1}on: (\d*) \(Noise=(.*)\)")
    reObj_snd_beamCount       = re.compile("SBC: (\d*)  SFC: (\d*)")
    reObj_newOptFreq          = re.compile("New Opt Freq; (\d*)")
    reObj_connectionInfos     = re.compile("Error attaching to .*|Attached to .*")
    
    
    # just ignore this messages
    passLogList = ["Starting Integration.", "Setting SND beam.", "Sending SND messages.", "Opening new files.", "Waiting for scan boundary." ]
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
    pass

class normalsoundFastSequence(scanClass):
    dev = True


# %%
controlProgramNames = ["normalsound (fast)", "rbspscan"]

dataProcesses = ["rawacfwrite","fitacfwrite", "rtserver" ]
dataProcessIgnoreLogs = ["Opening file." , "Closing file.", "Reset.", "Child server process starting"]
# %%

errorLogFileName = '/home/mguski/Documents/exampleLogFiles/errlog.adw.a.20161221'
f = open(errorLogFileName)

errorLogFileName = "/data/ros/errlog/errlog.adw.a.20161221" # TODO remove later


sequenceList = []

for line in f:
    line = line[:-1]
    
    if line.startswith(errorLogFileName) or len(line) == 0: # skip open messsage
        continue 
    
    date = datetime.datetime.strptime(line[:24], '%a %b %d %H:%M:%S %Y')
    processName, msg = line[26:].split(":",1)
    processName = processName.strip()
    
    if (processName in controlProgramNames):
        # like this re.sub(" \((.)", r'_\1', "abc (def)") ?
        if processName == "normalsound (fast)":
            if len(sequenceList) == 0  or sequenceList[-1].sequenceFinished  or not isinstance(sequenceList[-1],  normalsoundFastSequence):
                sequenceList.append(normalsoundFastSequence())    
            sequenceList[-1].parse_log_msg(msg,date)
        elif processName == "rbspscan":
            if len(sequenceList) == 0  or sequenceList[-1].sequenceFinished  or not isinstance(sequenceList[-1],  rbspscanSequence):
                sequenceList.append(rbspscanSequence())    
            sequenceList[-1].parse_log_msg(msg,date)
    elif processName in dataProcesses:
        if msg == "Received Data.":
            sequenceList[-1].data_received( processName)
        elif msg in dataProcessIgnoreLogs  or msg.endswith(" Open Connection.") or msg.endswith(" Close Connection."):
            pass
        else:
            print("Unknow msg: " + line)
    else:
        print("Unknown process: {}".format(processName))
        import time 
        time.sleep(1)

f.close()   