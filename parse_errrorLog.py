#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 12:57:31 2016

@author: mguski
"""
# TODO
# write fuctions: 
# parese_file
# parse_file_and_save_to_file
# plot overview

# %%

import re
import datetime
import matplotlib.pyplot as plt

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
    reObj_connectionInfos     = re.compile("Error attaching to .*")
    
    
    # just ignore this messages
    passLogList = ["Starting Integration.", "Setting SND beam.", "Sending SND messages.", "Opening new files.", "Waiting for scan boundary.", "Clear Search Skipped, next search in .* secs", "Attached to .*"]
    reObjList_pass = [re.compile(pattern) for pattern in passLogList]
    
    def __init__(self, programName):
        self.programName = programName
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
        unknownMessage = False
        
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
           # import time            
           # time.sleep(1)
            unknownMessage = True

        if not unknownMessage:
            self.add_date(date)
            
        return unknownMessage
            
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



# %%

def parse_errlog_file(errorLogFileName):
    controlProgramNames = ["normalsound (fast)","normalscan (fast)", "rbspscan", "themisscan", "pcodescan_bm9_15km", "pcodecamp_bm3_15km (fast)","pcodescan_bm3_15km", "pcodecamp_bm9_15km (onesec)", "pcodescan (fast)"] # known and tested control programs
    dataProcesses       = ["rawacfwrite","fitacfwrite", "rtserver" ]
    dataProcessIgnoreLogs = ["Opening file." , "Closing file.", "Reset.", "Child (S|s)erver process (starting|terminating)", "\[.*\] : (Open|Close) Connection.", "(Parent|Child) PID \d*", "Listening on port \d*."]
    
    dataProcessIgnoreLogs_re = [re.compile(s) for s in dataProcessIgnoreLogs]
    re_errlog_openMsg = re.compile("/.*/" + errorLogFileName.split("/")[-1] + " opened at .*")
    
    scanList = []
    unknownLogs = []
    
    f = open(errorLogFileName)
    nLines = 0
    
    for line in f:
        line = line[:-1]
        nLines +=1
        if re_errlog_openMsg.match(line) or len(line) == 0: # skip open messsage
            continue 
        
        date = datetime.datetime.strptime(line[:24], '%a %b %d %H:%M:%S %Y')
        processName, msg = line[26:].split(":",1)
        processName = processName.strip()
        
        if (processName in controlProgramNames):
    
            if len(scanList) == 0  or scanList[-1].sequenceFinished  or scanList[-1].programName != processName:
                scanList.append(scanClass(processName))    
            msgUnkown = scanList[-1].parse_log_msg(msg,date)
            if msgUnkown:
                unknownLogs.append(line)
    
                
        elif processName in dataProcesses:
            if msg == "Received Data.":
                scanList[-1].data_received( processName)
            elif any([re.match(msg) for re in dataProcessIgnoreLogs_re]):    
                pass
            else:
                print("Unknow msg: " + line)
                unknownLogs.append(line)
        else:
            print("Unknown process: {}".format(processName))
            import time 
            time.sleep(1)
    
    f.close()   
    
    print("Finished:\n  nLines:        {}\n  nSequences:    {}\n  unknown lines: {}\n".format(nLines, len(scanList), len(unknownLogs)))
    
    return scanList, unknownLogs

# %%

#fileName = "errlog.kod.c.20161230"

#fileName = "errlog.kod.d.20161230"
##fileName = "errlog.adw.a.20161221"
#errorLogFileName = '/home/mguski/Documents/exampleLogFiles/' + fileName



errorLogFileName = "/home/mguski/Documents/exampleLogFiles/2017-01-21-mcm_restart_problem/errlog.mcm.b.20170123"
errorLogFileName = "/home/mguski/Documents/exampleLogFiles/errlog.kod.d.20170204"


scanList, unknownLogs = parse_errlog_file(errorLogFileName)


#%%
loadData = False
if loadData:
    import pickle
    
    # obj0, obj1, obj2 are created here...
    
    # Saving the objects:
    pickleFileName = errorLogFileName + '_parsed.pickle'
    with open(pickleFileName, 'wb') as f:
        pickle.dump([scanList, unknownLogs], f)
    
    import gzip
    import shutil
    with open(pickleFileName, 'rb') as f_in:
        with gzip.open(pickleFileName + '.gzip', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    
    # Getting back the objects:
    with open('objs.pickle', 'rb') as f:  # Python 3: open(..., 'rb')
        scanList, unknownLogs = pickle.load(f)

# %%

timeVec = [seq.date_start  for seq in scanList]

scanChangeList = [[scanList[0].programName, scanList[0].date_start]]
for iScan in range(1,len(scanList)):
    if scanChangeList[-1][0] != scanList[iScan].programName:
        scanChangeList.append([scanList[iScan].programName, scanList[iScan].date_start])
scanChangeList.append(["End of Log file", timeVec[-1]])


# %%

#fig = plt.figure(figsize=[16, 10])
#ax = plt.subplot(211)
#plt.plot(t_a,nSeq_a, 'o',label="mcm.a" )
#plt.grid(True)
#plt.legend()

#plt.subplot(212, sharex=ax)

#plt.plot(t_b,nSeq_b, 'o',label="mcm.b" )
#plt.grid(True)
#plt.legend()
# %% plot some things

fig = plt.figure(figsize=[16, 10])



# -%%
ax1 = plt.subplot2grid((20,1), (1,0), rowspan=3)
nSeqPerSecList = [seq.nSequences for seq in scanList]
plt.plot(timeVec, nSeqPerSecList, "+")
ax1.set_ylabel("number of seq")
plt.grid(True)
#ax1.set_xticklabels([])
masterAx = ax1

ax = plt.subplot2grid((20,1), (0,0), sharex=masterAx)
for iScan in range(len(scanChangeList)-1):
    ax.barh(1,  (scanChangeList[iScan+1][1] - scanChangeList[iScan][1]).total_seconds()/60/60/24, left=scanChangeList[iScan][1], align='center')
    textPosition = scanChangeList[iScan][1] +  (scanChangeList[iScan+1][1] - scanChangeList[iScan][1])/2
    ax.text(textPosition, 1, scanChangeList[iScan][0] , rotation=0, backgroundcolor='w', alpha=0.5, ha='center', va='center' )    
#ax.set_xlim(timeVec[0], timeVec[-1])
ax.axis('off')
plt.title(errorLogFileName.split("/")[-1][7:12] + "  " + str(timeVec[0].date()))


ax = plt.subplot2grid((5,1), (1,0), sharex=masterAx)
freqVec = [seq.tx_freq/1000 for seq in scanList]
plt.plot(timeVec, freqVec, '+')
ax.set_ylabel("Freq in MHz")
plt.grid(True)
#ax.set_xticklabels([])


ax = plt.subplot2grid((5,1), (2,0), sharex=masterAx)
noiseVec = [seq.noise for seq in scanList]
plt.plot(timeVec, noiseVec, 'o')
plt.grid(True)
#ax.set_xticklabels([])
ax.set_ylabel("Noise energy ???")


ax = plt.subplot2grid((5,1), (3,0), sharex=masterAx)
plotData = [seq.beamNumber for seq in scanList]
plt.plot(timeVec, plotData, '|')
ax.set_ylabel("beam number")
plt.grid(True)
#ax.set_xticklabels([])


ax = plt.subplot2grid((5,1), (4,0), sharex=masterAx)
plotData = [seq.intus/1e6 for seq in scanList]
plt.plot(timeVec, plotData, label="insus", linewidth=2)
plotData = [seq.intsc for seq in scanList]
plt.plot(timeVec, plotData, label="inssc", linewidth=2)
ax.set_ylim(ax.get_ylim()[0]-0.1 , ax.get_ylim()[1]+0.1)
ax.set_ylabel("intt in s")
plt.grid(True)
plt.legend()


#plt.show()

# %% plot some things

fig = plt.figure(figsize=[16, 10])
# -%%

ax = plt.subplot2grid((20,1), (0,0))
for iScan in range(len(scanChangeList)-1):
    ax.barh(1,  (scanChangeList[iScan+1][1] - scanChangeList[iScan][1]).total_seconds()/60/60/24, left=scanChangeList[iScan][1], align='center')
    textPosition = scanChangeList[iScan][1] +  (scanChangeList[iScan+1][1] - scanChangeList[iScan][1])/2
    ax.text(textPosition, 1, scanChangeList[iScan][0] , rotation=0, backgroundcolor='w', alpha=0.5, ha='center', va='center' )    
ax.set_xlim(timeVec[0], timeVec[-1])
ax.axis('off')
plt.title(errorLogFileName.split("/")[-1][7:12] + "  " + str(timeVec[0].date()))
ax = masterAx

ax = plt.subplot2grid((5,1), (1,0), sharex=masterAx)
freqVec = [seq.newOptFreq for seq in scanList]
plt.plot(timeVec, freqVec, '+')
ax.set_ylabel("New opt freq")
plt.grid(True)
#ax.set_xticklabels([])
ax.set_ylim(min(ax.get_ylim()[0], 0) , max(ax.get_ylim()[1], 1))




ax = plt.subplot2grid((20,1), (1,0), rowspan=3, sharex=masterAx)
for seq in scanList:
    if seq.connectionInfos != []:
        ax.text(seq.date_start, 0, "\n".join(seq.connectionInfos))
        plt.plot([seq.date_start, seq.date_start], [0,1])
ax.set_xlim(timeVec[0], timeVec[-1])
ax.set_ylabel("connection messages")
plt.grid(True)
#ax.set_xticklabels([])
ax.axis('off')

ax = plt.subplot2grid((5,1), (2,0), sharex=masterAx)
cf_start = []
cf_range = []
for seq in scanList:
    if seq.clearFreq_start == -1:
        cf_start.append(None)
        cf_range.append(None)
    else:
        cf_start.append(seq.clearFreq_start/1000 )   
        cf_range.append((seq.clearFreq_range)/1000)      

#plt.errorbar(timeVec, cf_start, yerr=cf_range, capsize=0, fmt='none')
plt.grid(True)
#ax.set_xticklabels([])
ax.set_ylabel("Clear Freq (in Mhz)")
ax.set_ylim([max(ax.get_ylim()[0]-1,8), min(ax.get_ylim()[1]+2,18)])


ax = plt.subplot2grid((5,1), (3,0), sharex=masterAx)
plotData = [seq.data_received_rawacfwrite for seq in scanList]
plt.plot(timeVec, plotData, 'x', label='rawacfwrite')
plotData = [float(seq.data_received_fitacfwrite)+0.1 for seq in scanList]
plt.plot(timeVec, plotData, 'x', label='fitacfwrite')
plotData = [float(seq.data_received_rtserver)-0.1 for seq in scanList]
plt.plot(timeVec, plotData, 'x', label='rtserver')
ax.set_ylabel("data received")
ax.set_ylim(-0.15 ,1.15)
ax.set_yticks([0,1])
ax.set_yticklabels(["no", "yes"])
plt.grid(True)
plt.legend()
#ax.set_xticklabels([])




ax = plt.subplot2grid((5,1), (4,0), sharex=masterAx)
plotData = [seq.snd_beam_count for seq in scanList]
plt.plot(timeVec, plotData, 'x', label="snd_beam_count")
plotData = [seq.snd_freq_count for seq in scanList]
plt.plot(timeVec, plotData, '+', label="snd_freq_count")
ax.set_ylim(-0.1 , max(ax.get_ylim()[1], 1))
ax.set_ylabel("SND Mode")
plt.grid(True)
plt.legend()


plt.show()

# %%

#self.isStartOfScan = False
#self.sequenceFinished = False
#self.program_start = ""
#self.date_start = []
#self.date_end   = []
        

