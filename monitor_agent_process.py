#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 11:32:45 2017

@author: mguski
"""
import re
import time 
import datetime

import hdd_monitor
import hwmonitor_read_thermal

# %% read config file
fileName = 'monitor.cfg'

f = open(fileName, 'r')

re4section = re.compile("\[(.*)\]")
configDict = dict()
with open(fileName, 'r') as f:
    for line in f:
       if line.endswith("\n"):
            line = line[:-1]
       line = line.strip()

       if line == "" or  line.startswith("#"):
           continue
    
       if re4section.match(line):
           sectionName = re4section.search(line).group(1)
           configDict[sectionName] = dict()
           continue
    
       key, value = line.split(" ", 2)
       configDict[sectionName][key] = value
    
    
# %%      

    
logFile = None
monitorList = []
if "hdd_monitor" in configDict.keys():
    monitorList.append(hdd_monitor.hddSpaceMonitor(float(configDict["hdd_monitor"]['checkPeriod']), ))

if "computer_temperature" in configDict.keys():
    monitorList.append(hwmonitor_read_thermal.computer_temperature_monitor(float(configDict["computer_temperature"]['checkPeriod']), ))

  
while True:
    # create new log file
    if logFile == None or datetime.datetime.now().day != startTime.day:
        startTime = datetime.datetime.now()
        logFile = "rom_" + configDict["general"]["name"] +  startTime.strftime("__%Y-%m-%d") + ".log"
        with open(logFile, 'w+') as f:
            f.write("Starting monitor agent on " + configDict["general"]['name'] + " (" + str(startTime) + ")\n\n")
    

    for mon in monitorList:
        if mon.minutes_to_next_check() <= 0:
            logMSG = mon.run()
            with open(logFile, "a" ) as f:
                f.write(logMSG)
            print(logMSG)
            
    timeForNextCheck = min([mon.minutes_to_next_check() for mon in monitorList])
    print("waiting for {0:2.1f} min...".format(timeForNextCheck))
    time.sleep(timeForNextCheck*60)
        
