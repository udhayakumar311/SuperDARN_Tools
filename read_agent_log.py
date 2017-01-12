# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 20:08:27 2017

@author: mguski

"""
# %%
import remote_command
import gzip
import os
import datetime
import sys
import re
import datetime
# %%
path_localLogCache = 'log_cache/'
if not os.path.exists(path_localLogCache):
    os.makedirs(path_localLogCache)
    
path_liveData = 'status_website/liveData/'
if not os.path.exists(path_liveData):
    os.makedirs(path_liveData)


# check remote log file via ssh and transfer it compressed
class monitorTextFile():
    def __init__(self, logFileName, userName, remotePC, port=22):
        self.remote_fileName = logFileName
        self.userName = userName
        self.remotePC = remotePC
        self.port = port
        self.oldLines = None

        self.local_fileName = os.path.join(path_localLogCache, self.remote_fileName.split('/')[-1])
        
        if os.path.isfile(self.local_fileName):
            print("reading local file")
            with open(self.local_fileName, "r") as f:
                oldLines = f.read()
            oldLines = oldLines.split("\n")[:-1]
            self.currentLine  = len(oldLines)
            self.oldLines = oldLines
        else:
            self.currentLine = 1
        
            
        
        
    def get_new_lines(self):
        welcomeMSG = remote_command.remote_command_echo(self.userName, self.remotePC, " ", verbose = True, port = self.port)
        command = "tail -n +" + str(self.currentLine ) + " " + self.remote_fileName + " | gzip -cf"
        out = remote_command.remote_command_echo(self.userName, self.remotePC, command, verbose = True, port = self.port)
        #out = remote_command.remote_command("radar", "137.229.27.238", command)
        out = out[len(welcomeMSG):]
        newLines = gzip.decompress(out).decode('utf-8')
        if newLines == "":
            print("nothing new")
            newLines = None
        else:
            with open(self.local_fileName, "a") as f:
                f.write(newLines)
            newLines = newLines.split("\n")[:-1]
            nLines = len(newLines)
            print("reading line {} + {} = {}".format(self.currentLine, nLines, self.currentLine + nLines))
            self.currentLine += nLines
        
        return newLines
        




# %%


class hddPartitionStatus():
    reHDDspaceCheck_data = re.compile("(.*)[ \t]+:[ \t]+(.*) MB \/[ \t]+(\d*) MB [ \t]+(.*) \%[ \t]+(.*)")
    reIsHeaderLine = re.compile('Device.*Used.*Available.*Capacity.*Comment')

    def __init__(self):
        self.devNames = []
        self.usedList = []
        self.availableList = []
        self.percentageList = []
        self.commentList = []
        
    def addNewStatus(self, line):
        if self.reIsHeaderLine.match(line):
            return
            
        res = self.reHDDspaceCheck_data.search(line)
       # devName, used, available, percentage, comment = res.groups()
        devName = res.group(1).strip()
        used = float(res.group(2))
        available= float(res.group(3))
        percentage = float(res.group(4))
        comment = res.group(5).strip()
        
        if devName in self.devNames:
            idx = self.devNames.index(devName)
            self.usedList[idx] = used
            self.availableList[idx] = available
            self.percentageList[idx] = percentage
            self.commentList[idx] = comment
        else:
            self.devNames.append(devName)
            self.usedList.append(used)
            self.availableList.append(available)
            self.percentageList.append(percentage)
            self.commentList.append(comment)
            
    def get_status(self):
        out =  "{0: <20}: {1: >12}   {2: >12}    {3: >7}   {4}\n".format("Device", "Used", "Available", "Capacity", "Comment")
        for iPart in range(len(self.devNames)):
            out += "{0: <20}: {1: >9.0f} MB / {2: >9.0f} MB    {3:3.2f} % \t {4}\n".format(self.devNames[iPart], self.usedList[iPart], self.availableList[iPart], self.percentageList[iPart], self.commentList[iPart] ) 
        return out
        
# %%

class PCtemperatureStatus():
    reTempLine = re.compile(".* =[ \t]+(.*) C,.* \(<(.*)C\)")
  

    def __init__(self):
        self.statusLines = []
        self.tempList = []
        self.limitList = []
        
    def addNewStatus(self, line):
            
        if self.reTempLine.match(line): # initial log msg
            res = self.reTempLine.search(line)
            self.statusLines.append(line + '\n')
            self.tempList.append(res.group(1))
            self.limitList.append(res.group(2))
        elif line.startswith('Temperatures: '):
            for iTemp, temp in enumerate(line[14:].split("|")[:-1]):
                statLine = self.statusLines[iTemp]
                res = self.reTempLine.search(statLine)
                statLine = statLine[:res.span(1)[0]] + temp + statLine[res.span(1)[1]:] 
                self.statusLines[iTemp] = statLine
                self.tempList[iTemp] = float(temp)
       
    def get_status(self):
        out =  ""
        for statLine in self.statusLines:
            out += statLine
        return out        

        
        
# %%              

class romLogInterpreter():
    reStartMonitor = re.compile("Starting monitor agent on (.*) \((.*)\)")
    reHDDspaceCheck = re.compile("HDD space check \((.*)\)")
    rePCtempCheck = re.compile("Computer temperature check \((.*)\)")
    def __init__(self):
        self.hddPartitionStatus = hddPartitionStatus()
        self.PCtemperatureStatus = PCtemperatureStatus()
        self.computerName = 'unknown'

    def update(self, newLines):
        idxLine = 0
        while (idxLine < len(newLines)):   
            if len(newLines[idxLine]) == 0:
                idxLine += 1
            
            elif self.reStartMonitor.match(newLines[idxLine]):
                res = self.reStartMonitor.search(newLines[idxLine])
                self.computerName = res.group(1)
                self.monitorAgent_startTime = datetime.datetime.strptime(res.group(2), "%Y-%m-%d %H:%M")
                idxLine += 1
                
            elif self.reHDDspaceCheck.match(newLines[idxLine]):
                res = self.reHDDspaceCheck.search(newLines[idxLine])
                self.hdd_check_lastUpdate = datetime.datetime.strptime(res.group(1), "%Y-%m-%d %H:%M")
                idxLine += 1
            
                while (len(newLines[idxLine])):
                    self.hddPartitionStatus.addNewStatus(newLines[idxLine])
                    idxLine += 1
                idxLine += 1
            elif self.rePCtempCheck.match(newLines[idxLine]):
                res = self.rePCtempCheck.search(newLines[idxLine])
                self.temperature_lastUpdate = datetime.datetime.strptime(res.group(1), "%Y-%m-%d %H:%M")
                idxLine += 1
            
                while (len(newLines[idxLine])):
                    self.PCtemperatureStatus.addNewStatus(newLines[idxLine])
                    idxLine += 1
                idxLine += 1
            
            else:
                print("unkown: {}".format(newLines[idxLine]))
                idxLine += 1
    def summary_status(self):
        stat = "Computer: {} (Report created: {} UTC)\n\n".format(self.computerName, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
        
        if len(self.PCtemperatureStatus.statusLines) != 0:
            stat += "Temperature Status (last update on {} UTC):\n".format(self.temperature_lastUpdate.strftime("%Y-%m-%d %H:%M"))
            stat += self.PCtemperatureStatus.get_status() + '\n\n'
            
        if len(self.hddPartitionStatus.devNames) != 0:
            stat += "HDD Status (last update on {} UTC):\n".format(self.hdd_check_lastUpdate.strftime("%Y-%m-%d %H:%M"))
            stat += self.hddPartitionStatus.get_status() + '\n\n'
        return stat

    def print_all_status(self):    
        print(self.summary_status())
    
    
# %%
class liveMonitor():
    def __init__(self, nMinutesCheckPeriod):
        self.nMinutesCheckPeriod = nMinutesCheckPeriod
        self.lastRunTime = []
        
    def minutes_to_next_check(self):
        if self.lastRunTime == []:
            return 0
        
        time2nextRun = self.lastRunTime + datetime.timedelta(minutes=self.nMinutesCheckPeriod) - datetime.datetime.utcnow()
        return time2nextRun.seconds /60
    
    def run(self):
        print("run of parent class is doing nothing!")
        self.lastRunTime = datetime.datetime.utcnow()    
#
class monitor_agent_log(liveMonitor):
    def __init__(self, nMinutesCheckPeriod, logFileName, userName, ip, outputFile, port=22):
        self.nMinutesCheckPeriod = nMinutesCheckPeriod
        self.lastRunTime = []
        self.isInitialCheck = True
        self.outputFile = outputFile
        
#        self.logFileName = logFileName
#        self.userName = userName
#        self.ip = ip
#        self.port = port
        
        self.logFileMonitor = monitorTextFile(logFileName, userName, ip, port=port)
        self.logInterpreter = romLogInterpreter()
        if self.logFileMonitor.oldLines != None:
            self.logInterpreter.update(self.logFileMonitor.oldLines)
    
    
    def run(self):
        self.lastRunTime = datetime.datetime.utcnow() 
        newLines = self.logFileMonitor.get_new_lines()
        self.logInterpreter.update(newLines)
        
    def update_html(self):
        with open(self.outputFile, 'w+') as f:
            f.write(self.logInterpreter.summary_status())
        
# %%

ri = romLogInterpreter()
lm = monitorTextFile("/home/radar/repos/SuperDARN_Tools/rom_kodiak-aux__2017-01-11.log", "radar", "137.229.27.238", port=22)
ri.update(lm.oldLines)
nl = lm.get_new_lines()

# %%
logFileName = "/home/radar/repos/SuperDARN_Tools/rom_kodiak-aux__2017-01-12.log"
outputFile = 'status_website/liveData/agent_summary_kod-aux'
userName = 'radar'
ip = "137.229.27.238"
rom_watcher = monitor_agent_log( 11, logFileName, userName, ip, outputFile)
rom_watcher.update_html()

