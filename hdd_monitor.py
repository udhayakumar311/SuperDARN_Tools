#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 11:24:20 2017

@author: mguski
"""


import subprocess
import datetime
import sys
# %%


class hddPartitionInfo():
    def __init__(self, df_string):
        elements = [ el for el in df_string.split(" ") if el != ""]
        self.used = float(elements[2])
        self.available = float(elements[3])
        self.name = elements[5]
# %%
class liveMonitor():
    def __init__(self, nMinutesPerCheck):
        self.nMinutesPerCheck = nMinutesPerCheck
        self.lastRunTime = []
        
    def minutes_to_next_check(self):
        if self.lastRunTime == []:
            return 0
        
        time2nextRun = self.lastRunTime + datetime.timedelta(minutes=self.nMinutesPerCheck) - datetime.datetime.now()
        return time2nextRun.seconds /60
    
    def run(self):
        print("run of parent class is doing nothing!")
        self.lastRunTime = datetime.datetime.now()


class hddSpaceMonitor(liveMonitor):
    def __init__(self, nMinutesPerCheck):
        if sys.version_info[0] == 3:
            super().__init__(nMinutesPerCheck)
        else:
            liveMonitor.__init__(self,nMinutesPerCheck)
        self.nDaysLeft = []
        
    def get_partition_infos(self):
        command = "df -P"
        return_code = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.readlines()
        
        allPartitions = []
        for iLine in range(1,len(return_code)):
            allPartitions.append(hddPartitionInfo(return_code[iLine][:-1].decode("UTF-8")))
        return allPartitions
        
    def run(self):
        newPartInfo = self.get_partition_infos()
        newTime     = datetime.datetime.now()
        
        # check
        
        print("HDD space check ({0})".format(newTime))
        print("  {0: <20}: {1: >12}   {2: >12}    {3: >7}   {4}".format("Device", "Used", "Available", "Capacity", "Comment"))
        nDaysLeft = []
        for iPart, part in enumerate(newPartInfo):
            if self.lastRunTime != []:
                if part.name != self.lastPartInfo[iPart].name:
                    print("error: order of partitions in df changed!")
                    return -1
                kilobytesPerDay = (part.used  -  self.lastPartInfo[iPart].used)/ ( float((newTime - self.lastRunTime).seconds) / 3600/24)
                if kilobytesPerDay == 0:
                    estFullString = 'no data written'
                    nDaysLeft.append(-1)
                elif kilobytesPerDay < 0:
                    estFullString = 'no data written (only deleted)'
                    nDaysLeft.append(-1)
                else:
                    daysUntilFull = (part.available ) / kilobytesPerDay 
                    nDaysLeft.append(daysUntilFull)
                    estFullString = "{0:5.0f} days left ({1:2.3f} MB/day)".format(daysUntilFull, kilobytesPerDay/1024)
            else:
                estFullString = '(first run)'
                
            print("  {0: <20}: {1: >9.0f} MB / {2: >9.0f} MB    {3:3.2f} % \t {4}".format(part.name, part.used/1024, part.available/1024, part.used/ (part.used+part.available) *100, estFullString ))
        self.nDaysLeft = nDaysLeft
        print('\n')
        self.lastPartInfo = newPartInfo
        self.lastRunTime = newTime

# %%      
import time 
monitorList = []

monitorList.append(hddSpaceMonitor(60.0))
  
while True:
    
    for mon in monitorList:
        if mon.minutes_to_next_check() <= 0:
            mon.run()
            
    timeForNextCheck = min([mon.minutes_to_next_check() for mon in monitorList])
    print("waiting for {0:2.1f} min...".format(timeForNextCheck))
    time.sleep(timeForNextCheck*60)
        
# %%        

