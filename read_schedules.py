# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 11:48:59 2016

@author: mguski
"""
# TODO:
# nice colors, and legend
# options:
#    - export png -1 day to +4 days
#    - export png this / next month
#    - check radar schedule from github
#    - return current scan mode


# %%

import urllib
import urllib.request
import datetime
import matplotlib.pyplot as plt

class structDummy:
    pass


# %%



def read_schedule(url_schedule, checkForGaps=True):
    
    schedule_txt = urllib.request.urlopen(url_schedule)
    parameterList = ['path', 'default', 'stationid', 'sitelib', 'channel', 'priority', 'duration']
    parameterDict = dict()
    if not 'campaign' in url_schedule:
        while True:
            currLine = schedule_txt.readline().decode('utf-8')[:-1] 
            if len(currLine) == 0:
                break
            parameter = currLine.split(" ")[0]
            if parameter in parameterList:
                parameterDict[parameter] = currLine[len(parameter)+1:]
            else:
                raise ValueError("Paramater {} unkown in file  : {}".format(parameter,  url_schedule))

            
    startTimeList = []
    durationList = []
    priorityList = []
    controlProgramList = []
    
    for line in schedule_txt:
        line = line.decode('utf-8')
      #  print("line: {}".format(line[:-1]))
        if line.isspace() or line.startswith("#") :
            continue
        if line.split(" ")[0] in parameterList:
            parameterDict[line.split(" ")[0]] = line[len(line.split(" ")[0])+1:]
            print("Parameter {} in in the middle of the file! ({})".format(line.split(" ")[0], url_schedule))
            continue
        try: 
            startTimeList.append(datetime.datetime.strptime(line[:16], "%Y %m %d %H %M"))
            durationList.append(int(line[16:23]))
            priorityList.append(int(line[23:27]))
            controlProgramList.append( line[28:-1])
        except:
            print("Error for parsing line:\n  {}  from file {}".format(line, url_schedule))
            
    
    nEntries = len(controlProgramList)

    #% check file for some errors
    errorFound = False

    if not 'channel' in parameterDict.keys():
        print('No channel defined in {}. '.format(url_schedule))
        print("Assuming channel {} (from file name)!".format(url_schedule.split("/")[-1][4:5]))
        parameterDict['channel'] = url_schedule.split("/")[-1][4:5]
            
    if not 'stationid' in parameterDict.keys():
        print('No stationid defined in {}. '.format(url_schedule))
        print("Assuming channel {} (form file name)!".format(url_schedule.split("/")[-1][0:3]))
        parameterDict['stationid'] = url_schedule.split("/")[-1][0:3]


    
    # check for gapless and non overlapping schedule
    if checkForGaps:
        for iEntry in range(nEntries-1):
            endTime = startTimeList[iEntry] + datetime.timedelta( minutes=durationList[iEntry])
            if not (endTime == startTimeList[iEntry+1]):
                errorFound = True
                print("Error in time schedule (duration or start time of next entry):")
                print("  {} {} {} {}".format(startTimeList[iEntry],durationList[iEntry], priorityList[iEntry], controlProgramList[iEntry]))
                print("  {} {} {} {}".format(startTimeList[iEntry+1],durationList[iEntry+1], priorityList[iEntry+1], controlProgramList[iEntry+1]))
        
    # check for correct station name and channel number in command
    channelNo = ' abcd'.index(parameterDict['channel'])
    requiredStringList  = ["-c {}".format(channelNo), "-stid {}".format(parameterDict['stationid'])]
    for requiredString in requiredStringList:
        for iEntry in range(nEntries):
            if not requiredString in controlProgramList[iEntry]:
                print("command does not include '{}' ".format(requiredString))
                print("  {} {} {} {}".format(startTimeList[iEntry],durationList[iEntry], priorityList[iEntry], controlProgramList[iEntry]))
                errorFound = True
    
    
    if errorFound:
        print("Error found in scheduling file {}\n\n".format(url_schedule))
   # else:
   #     print("Looks good: {}".format(url_schedule))
        
    output = structDummy()
    output.url_schedule = url_schedule
    output.parameterDict = parameterDict
    output.startTimeList = startTimeList
    output.durationList = durationList
    output.priorityList = priorityList
    output.controlProgramList = controlProgramList
    output.nEntries = nEntries
    output.errorFound = errorFound
    return output
#%

from matplotlib.ticker import FuncFormatter
def dateFormatter(value, pos):
    dateValue = datetime.datetime.fromordinal(int(value))
    remDays = value % 1
    if remDays == 0:
        label = dateValue.strftime("%Y-%m-%d")
    else:
        dateValue = datetime.datetime.combine(dateValue,datetime.time(0)) + datetime.timedelta(days=remDays) 
        #label = dateValue.strftime("%Y-%m-%d %H:%M")
        label = dateValue.strftime("%H:%M")
    
    return label    
    #return str(value)
    


# %% 
def read_swg_schedule(month, year):
    url = "http://sdnet.thayer.dartmouth.edu/web_data/schedules/swg/{}{:>02d}.swg".format(year, month)
    schedule_txt = urllib.request.urlopen(url)
    
    line = schedule_txt.readline().decode("UTF-8")
    dateFromFile = datetime.datetime.strptime(line, "%B %Y\n")
    if not dateFromFile == datetime.datetime(year, month, 1):
        print("First line ('{}') of file ({})  is not as expecte!".format(line[:-1], url))
    
    startTimeList = []
    endTimeList   = []
    phaseNameList = []
    additionList  = []
    
    
    for line in schedule_txt:
        line = line.decode('UTF-8')[:-1]
        if line.startswith('# Notes:'):
            break
        if line.isspace() or line.startswith('#') or len(line) == 0:
            continue
        elementsInLine = line.split(" ")
        elementsInLine = [element for element in elementsInLine if len(element)]
        if elementsInLine[0].startswith('['):
            additionList[-1] = line
        else:
            dateChunk = datetime.datetime.strptime(elementsInLine[0], "%d:%H")
            startTimeList.append(datetime.datetime(year, month, dateChunk.day, dateChunk.hour))
    
            dateChunk = datetime.datetime.strptime(elementsInLine[1][0:2], "%d")
            endTimeList.append(datetime.datetime(year, month, dateChunk.day) + datetime.timedelta(hours=int(elementsInLine[1][3:]))) # because last entry is 24h
            phaseNameList.append(" ".join(elementsInLine[2:]))
            additionList.append("")
            
    notes = schedule_txt.read().decode('UTF-8')        
    output = structDummy()
    output.startTimeList = startTimeList
    output.endTimeList = endTimeList
    output.phaseNameList = phaseNameList
    output.additionList = additionList
    output.durationInDays = [endTimeList[iEntry] - startTimeList[iEntry] for iEntry in range(len(startTimeList))]
    output.notes = notes
    return output
    
    
    
# %%
    
    
url_schedule = 'https://raw.githubusercontent.com/UAF-SuperDARN-OPS/schedule_files/adak/ade/ade.a.scd'
root_schedule_url = 'https://raw.githubusercontent.com/UAF-SuperDARN-OPS/schedule_files/'

schedule_file_list = [["adak/ade/ade.a.scd"], ["adak/adw/adw.a.scd"], ["kodiak/kod/kod.c.scd"], ["kodiak/kod/kod.d.scd", "kodiak/kod/kod.d.campaign.scd"], ['mcmurdo/mcm/mcm.a.scd'], ['mcmurdo/mcm/mcm.b.scd'], ['southpole/sps/sps.a.scd']]
#, 'kodiak/kod/kod.c.campaign.scd', 'kodiak/kod/kod.d.campaign.scd'
schedule_list = []

for radar_file_list in schedule_file_list:
    schedule_list.append([])
    for url_schedule in radar_file_list:
        schedule_list[-1].append(read_schedule(root_schedule_url + url_schedule))



now = datetime.datetime.now()
swg_schedule = read_swg_schedule(now.month, now.year)


# %%

plotRange = [-1, 3] # in days from today
#plotRange = [-25, 35] # in days from today

fig, ax = plt.subplots()

controlProgramColor = dict(normalscan="green", normalsound="royalblue", themisscan='darkred', pcodescan_15km='purple', rbspscan='orange', iwd_normalscan='y',noopscan='white', iwdscan='darkturquoise')

yLabelList = [""]
iSchedule = 0

now = datetime.datetime.utcnow()
xLimStart = now.date() + datetime.timedelta(days=plotRange[0])
xLimEnd = now.date() + datetime.timedelta(days=plotRange[1])

for iRadar in range(len(schedule_list)):
    iSchedule += 1
    yLabelList.append("")
    for iSchedInRadar, currSchedule in enumerate(schedule_list[iRadar]):
        iSchedule += 1
        yLabelList.append(schedule_file_list[iRadar][iSchedInRadar].split("/")[-1][:-4])
        for iEntry in range(len(currSchedule.durationList)):
            #if currSchedule.startTimeList[iEntry] > now + datetime.timedelta(days=plotRange[1]) or (currSchedule.startTimeList[iEntry] + datetime.timedelta( minutes=currSchedule.durationList[iEntry])) < now + datetime.timedelta(days=plotRange[0]):
            #    continue
            currProgram = currSchedule.controlProgramList[iEntry].split(" ")[0]
            if currProgram in controlProgramColor:
                plotColor = controlProgramColor[currProgram]
            else:
                print("no color for " + currProgram)
                plotColor = 'gray'
            startPoint = currSchedule.startTimeList[iEntry]
            duration = currSchedule.durationList[iEntry]/60/24
            ax.barh(iSchedule,  duration, left=startPoint, align='center', color=plotColor)
            textPosition = startPoint+datetime.timedelta(minutes=currSchedule.durationList[iEntry]/2)
            if textPosition.date() < xLimEnd and textPosition.date() > xLimStart:
                ax.text(textPosition, iSchedule, currProgram , rotation=0, backgroundcolor='w', alpha=0.5, ha='center', va='center' )
            
        # plt.gcf().autofmt_xdate()

iSchedule += 2
for iEntry in range(len(swg_schedule.phaseNameList)):
    startPoint = swg_schedule.startTimeList[iEntry]
    duration = swg_schedule.durationInDays[iEntry].total_seconds()/3600/24
    ax.barh(iSchedule,  duration, left=startPoint, align='center', height=1.6, color=plotColor)
    textPosition = startPoint+swg_schedule.durationInDays[iEntry]/2
    ax.text(textPosition, iSchedule, swg_schedule.phaseNameList[iEntry] , rotation=45, backgroundcolor='w', alpha=0.5, ha='center', va='center' )
  

            

plt.plot([now, now], [0, iSchedule+1], color='red')
ax.set_xlim(xLimStart, xLimEnd)


ax.xaxis.set_major_formatter( FuncFormatter(dateFormatter) ) 
ax.grid(True)
plt.xticks(rotation=0)
ax.set_yticks(range(0, len(yLabelList)))
ax.set_yticklabels(yLabelList)

nowUTC   =  datetime.datetime.utcnow()
nowLocal =  datetime.datetime.now()

plt.title("Current now: {} (UTC)  || {}  (local)".format(nowUTC.strftime("%Y-%m-%d %H:%M"), nowLocal.strftime("%Y-%m-%d %H:%M")))


    
