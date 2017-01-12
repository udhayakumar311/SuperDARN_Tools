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

# %%
path_localLogCache = 'log_cache/'
if not os.path.exists(path_localLogCache):
    os.makedirs(path_localLogCache)

# %%
class liveMonitor():
    def __init__(self, nMinutesCheckPeriod):
        self.nMinutesCheckPeriod = nMinutesCheckPeriod
        self.lastRunTime = []
        
    def minutes_to_next_check(self):
        if self.lastRunTime == []:
            return 0
        
        time2nextRun = self.lastRunTime + datetime.timedelta(minutes=self.nMinutesCheckPeriod) - datetime.datetime.now()
        return time2nextRun.seconds /60
    
    def run(self):
        print("run of parent class is doing nothing!")
        self.lastRunTime = datetime.datetime.now()

# check remote log file via ssh and transfer it compressed
class monitorLogFile(liveMonitor):
    def __init__(self, nMinutesCheckPeriod,logFileName, userName, remotePC, port=22):
        if sys.version_info[0] == 3:
            super().__init__(nMinutesCheckPeriod)
        else:
            liveMonitor.__init__(self,nMinutesCheckPeriod)
        self.nDaysLeft = []
        self.remote_fileName = logFileName
        self.userName = userName
        self.remotePC = remotePC
        self.port = port
        
        
        self.local_fileName = os.path.join(path_localLogCache, self.remote_fileName.split('/')[-1])
        
        if os.path.isfile(self.local_fileName):
            pass # TODO
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
            return None
        with open(self.local_fileName, "a") as f:
            f.write(newLines)
        newLines = newLines.split("\n")
        newLines = newLines[:-1]
        nLines = len(newLines)
        print("reading line {} + {} = {}".format(self.currentLine, nLines, self.currentLine + nLines))
        self.currentLine += nLines
        return newLines
        
    def run(self):
        newLines = self.get_new_lines()
        newTime     = datetime.datetime.now()
        
        # check
        logMSG = ""
        newLine = '\n'
        logMSG += "HDD space check ({0})".format(newTime)  + newLine

        self.lastRunTime = newTime
        logMSG += newLine
        return newLines

# %%


lm = monitorLogFile( 11,"/home/radar/repos/SuperDARN_Tools/test.log", "radar", "137.229.27.238", port=22)
nl = lm.run()
