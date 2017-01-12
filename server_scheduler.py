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

# %% read config
fileName = 'monitor_server.cfg'
configDict = helper_functions.read_config_file(fileName)    
    
# %%    
logFile = None
processList = []
for key in configDict.keys():
    if key == "agent_log":
        configDict[key]
        processList.append(read_agent_log.monitor_agent_log( float(configDict[key]['checkPeriod']), configDict[key]['logFileName'], configDict[key]['userName'], configDict[key]['ip'], configDict[key]['outputFile']))
    else:
        print("unknown key: " + key)
    

  
while True:

    for process in processList:
        if process.minutes_to_next_check() <= 0:
            process.run() # TODO: output is warning/error msg 

            
    timeForNextCheck = min([process.minutes_to_next_check() for process in processList])
    print("waiting for {0:2.1f} min...".format(timeForNextCheck))
    time.sleep(timeForNextCheck*60)
        
