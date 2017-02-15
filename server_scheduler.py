#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 10:04:13 2017

@author: mguski
"""

#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 11:32:45 2017

@author: mguski
"""

import time 

import helper_functions
import read_agent_log
import updateWebsite_schedules
# %% read config
fileName = 'monitor_server.cfg'
configDict = helper_functions.read_config_file(fileName)    
    
# %%    
logFile = None
processList = []
for key in configDict.keys():
    key = key.lower().strip()
    if key == "agent_log":
        print("skipping agent_log")
#        processList.append(read_agent_log.monitor_agent_log( float(configDict[key]['checkPeriod']), configDict[key]['logFileName'], configDict[key]['userName'], configDict[key]['ip'], configDict[key]['outputFile']))
    elif key == "schedules":
        processList.append(updateWebsite_schedules.scheduleUpdater( float(configDict[key]['checkPeriod'])))
    else:
        print("unknown key: " + key + "")
    

  
while True:

    for process in processList:
        print("Checking process: {0} (NminLeft: {1})".format(str(process.__class__).split(".")[-1].split(" ")[0], process.minutes_to_next_check()))
        if process.minutes_to_next_check() <= 0:
            print("Running process: {0}".format(str(process.__class__).split(".")[-1].split(" ")[0]))
            process.run() # TODO: output is warning/error msg 

            
    timeForNextCheck = min([process.minutes_to_next_check() for process in processList])
    print("waiting for {0:2.1f} min...".format(timeForNextCheck))
    time.sleep(timeForNextCheck*60)
        
