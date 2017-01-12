#!/usr/bin/python3
# %%
import os
import glob 


# %%
def read_hardware_monitor_status(hwmonPath = "/sys/class/hwmon/", verbose=False):
    allDirs = os.listdir(hwmonPath)
    output = []
    for currDir in allDirs: 
        
        nameFile = os.path.join(hwmonPath, currDir, "name")
        if os.path.exists(nameFile):
            with open(nameFile) as f:
                hwmonName = f.read()[:-1]
        else:
            hwmonName = ""
        
        allTempFiles = glob.glob(os.path.join(hwmonPath, currDir, "temp*_input"))
        
        for iTemp, currTempFile in enumerate(allTempFiles):
            with open(currTempFile) as f:
                    temp = float(f.read())/1000
            
            # read critical temperature        
            critFileName =  currTempFile[:-5] + "crit"
            if os.path.exists(critFileName):
                with open(critFileName) as f:
                    tempCrit = float(f.read())/1000
                if temp < tempCrit:
                    status = "ok (< {} C)".format(tempCrit)
                else:
                    status = "critical! (> {} C)".format(tempCrit)
            else:
                status = "unknown"
                
            # read sensor name     
            sensorFileName =  currTempFile[:-5] + "label"
            if os.path.exists(sensorFileName):
                with open(sensorFileName) as f:
                    sensorName = f.read()[:-1]
            else:
                sensorName = "sensor " + str(iTemp+1)      
            if verbose:    
                print("{}: {: <8} {: >15} = {: >5} C,  status: {}".format(currDir,hwmonName, sensorName, temp , status))
            output.append(dict(dirName=currDir,hwmonName=hwmonName, sensorName=sensorName, temperature=temp, status=status ))
            
    return output
# %%
# %%
# todo: put this class in one file
import datetime

class liveMonitor():
    def __init__(self, nMinutesCheckPeriod):
        self.nMinutesCheckPeriod = nMinutesCheckPeriod
        self.lastRunTime = []
        self.isInitialCheck = True
        
    def minutes_to_next_check(self):
        if self.lastRunTime == []:
            return 0
        
        time2nextRun = self.lastRunTime + datetime.timedelta(minutes=self.nMinutesCheckPeriod) - datetime.datetime.now()
        return time2nextRun.seconds /60
    
    def run(self):
        print("run of parent class is doing nothing!")
        self.lastRunTime = datetime.datetime.now()    
    
class computer_temperature_monitor(liveMonitor):
    def run(self):
        newTime     = datetime.datetime.now()
        self.lastRunTime = newTime
        # check
        data = read_hardware_monitor_status()
        
        logMSG = ""
        logMSG += "Computer temperature check ({0})\n".format(newTime.strftime("%Y-%m-%d %H:%M"))
        if self.isInitialCheck:
            for sensor in data:
                logMSG += "{}: {: <8} {: >15} = {: >5} C,  status: {}\n".format(sensor['dirName'], sensor['hwmonName'], sensor['sensorName'], sensor['temperature'] , sensor['status'])
            logMSG += '\n'
            self.isInitialCheck = False
        else:
            logMSG += "Temperatures: "
            logMSG += "|".join([str(sensor['temperature']) for sensor in data])
            logMSG += '\n\n'            
        return logMSG

# %%
# degreeC = u"\u2103"
#data = read_hardware_monitor_status()

# %% OLD 
#thermalPath = "/sys/devices/virtual/thermal/"
#==============================================================================
# thermalPath = "/sys/class/thermal/"
# allDirs = os.listdir(thermalPath)
# 
# allDirs = [iDir for iDir in allDirs if iDir.startswith("thermal_zone")]
# 
# allTemps = []
# allStatus = []
# for iDir in allDirs:
#     with open(os.path.join(thermalPath, iDir, "temp")) as f:
#         temp = float(f.read())/1000
#         allTemps.append(temp)    
#     iTripPoint = 0    
#     while (True):
#         tripFileName = os.path.join(thermalPath, iDir, "trip_point_{}_temp".format(iTripPoint))
#         if os.path.exists(tripFileName):
#             with open(tripFileName) as f:
#                 tripTemp = float(f.read())/1000
#             if tripTemp > temp:
#                 iTripPoint += 1
#             else: # found status
#                 with open(os.path.join(thermalPath, iDir, "trip_point_{}_type".format(iTripPoint))) as f:
#                     allStatus.append(f.read()[:-1])
#                 break
#         else:
#             allStatus.append("unknown")
#             break
#         
# 
# 
# for iDir, currDir in enumerate(allDirs):
#     print("{} : {} C Status: {}".format(currDir, allTemps[iDir], allStatus[iDir]))
# 
#==============================================================================
