#!/usr/bin/python3
# 
# function to:
#   - read UAF schedules from github and original SWG schedule
#   - check UAF schedules for errrors
#   - visualize schedules
#
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
import numpy as np

class structDummy:
    pass

now = datetime.datetime.now()
# %%



def read_schedule(url_schedule, checkForGaps=True):
    errorMSG = ""
    schedule_txt = urllib.request.urlopen(url_schedule)
    parameterList = ['path', 'default', 'stationid', 'sitelib', 'channel', 'priority', 'duration']
    parameterDict = dict()
    isMainFile = not (('special' in url_schedule) or ('campaign' in url_schedule))
    if isMainFile:
        while True:
            currLine = schedule_txt.readline().decode('utf-8')[:-1] 
            if len(currLine) == 0:
                break
            parameter = currLine.split(" ")[0]
            if parameter in parameterList:
                parameterDict[parameter] = currLine[len(parameter)+1:]
            else:
                #raise ValueError("Paramater {} unkown in file  : {}".format(parameter,  url_schedule))
                errorMSG += "Paramater {} unkown in file  : {}\n".format(parameter,  url_schedule)

            
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
            if isMainFile:
                errorMSG += "Parameter {} in in the middle of the file! ({})\n".format(line.split(" ")[0], url_schedule)
            continue
        try: 
           # startTimeList.append(datetime.datetime.strptime(line[:16], "%Y %m %d %H %M"))
           # durationList.append(int(line[16:23]))
           # priorityList.append(int(line[23:27]))
           # controlProgramList.append( line[28:-1])
            
            elements = [element for element in line.split(' ') if element !=""]
            startTimeList.append(datetime.datetime(int(elements[0]), int(elements[1]), int(elements[2]), int(elements[3]), int(elements[4])))
            durationList.append(int(elements[5]))
            priorityList.append(int(elements[6]))
            controlProgramList.append( " ".join(elements[7:]))
        except:
            errorMSG += "Error for parsing line:\n  {}  from file {}\n".format(line, url_schedule)
            
    
    nEntries = len(controlProgramList)

    #% check file for some errors
    errorFound = False

    if not 'channel' in parameterDict.keys():
        if isMainFile:
            errorMSG += 'No channel defined in {}. \n'.format(url_schedule)
            errorMSG += "Assuming channel {} (from file name)!\n".format(url_schedule.split("/")[-1][4:5])
        parameterDict['channel'] = url_schedule.split("/")[-1][4:5]
            
    if not 'stationid' in parameterDict.keys():
        if isMainFile:
            errorMSG += 'No stationid defined in {}. \n'.format(url_schedule)
            errorMSG += "Assuming channel {} (from file name)!\n".format(url_schedule.split("/")[-1][0:3])
        parameterDict['stationid'] = url_schedule.split("/")[-1][0:3]


    
    # check for gapless and non overlapping schedule
    if checkForGaps and isMainFile:
        for iEntry in range(nEntries-1):
            endTime = startTimeList[iEntry] + datetime.timedelta( minutes=durationList[iEntry])
            if not (endTime == startTimeList[iEntry+1]):
                errorFound = True
                errorMSG += "Error in time schedule (duration or start time of next entry):\n"
                errorMSG += "  {} {} {} {}".format(startTimeList[iEntry],durationList[iEntry], priorityList[iEntry], controlProgramList[iEntry])
                errorMSG += "  {} {} {} {}".format(startTimeList[iEntry+1],durationList[iEntry+1], priorityList[iEntry+1], controlProgramList[iEntry+1])
        
    # check for correct station name and channel number in command
    channelNo = ' abcd'.index(parameterDict['channel'])
    requiredStringList  = ["-c {}".format(channelNo), "-stid {}".format(parameterDict['stationid'])]
    for requiredString in requiredStringList:
        for iEntry in range(nEntries):
            if not requiredString in controlProgramList[iEntry]:
                errorMSG += "command does not include '{}' :\n".format(requiredString)
                errorMSG += "  {} {} {} {}".format(startTimeList[iEntry],durationList[iEntry], priorityList[iEntry], controlProgramList[iEntry])
                errorFound = True
    
    
    if errorFound:
        print("Error found in scheduling file {}\n".format(url_schedule))
   # else:
   #     print("Looks good: {}".format(url_schedule))
        
    output = structDummy()
    output.url_schedule = url_schedule
    output.isMainSchedule = isMainFile
    output.parameterDict = parameterDict
    output.startTimeList = startTimeList
    output.durationList = durationList
    output.priorityList = priorityList
    output.controlProgramList = controlProgramList
    output.nEntries = nEntries
    output.errorFound = errorFound
    output.errorMSG = errorMSG
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
def create_figure(scheduale_list, plotRange, labelSWGschedule = True):
    fig = plt.figure(figsize=[16, 10])
    ax = plt.subplot2grid((1,9), (0,0), colspan=8)
    
    controlProgramColor = dict(normalscan="limegreen", normalsound="darkolivegreen", themisscan='royalblue', pcodescan_15km='purple',  codescan_15km="magenta", pcodescan='indigo' ,rbspscan='orange', iwd_normalscan='y',noopscan='lightgray', iwdscan='darkturquoise', interleavescan='springgreen', spaletascan='yellow')
    
    yLabelList = []
    yTickList = []
    iSchedule = 0
    
    now = datetime.datetime.utcnow()
    xLimStart = now.date() + datetime.timedelta(days=plotRange[0])
    xLimEnd = now.date() + datetime.timedelta(days=plotRange[1])
    
    for iRadar in range(len(schedule_list)):
        if iRadar == 0 or schedule_file_list[iRadar][0].split("/")[-1][:1] != schedule_file_list[iRadar-1][0].split("/")[-1][:1]:
            iSchedule += 1
        else:
            iSchedule += 0.3
        for iSchedInRadar, currSchedule in enumerate(schedule_list[iRadar]):
            iSchedule += 0.8
            yLabelList.append(schedule_file_list[iRadar][iSchedInRadar].split("/")[-1][:-4])
            yTickList.append(iSchedule)
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
                ax.barh(iSchedule,  duration, left=startPoint, align='center', color=plotColor, alpha=0.75)
                textPosition = startPoint+datetime.timedelta(minutes=currSchedule.durationList[iEntry]/2)
    #            if textPosition.date() < xLimEnd and textPosition.date() > xLimStart: # if in xLim range
                if now > startPoint and now < (startPoint + datetime.timedelta(minutes=currSchedule.durationList[iEntry])):  # if is current program
                    ax.text(textPosition, iSchedule, currProgram , rotation=0, backgroundcolor='w', alpha=0.5, ha='center', va='center' )
                
            # plt.gcf().autofmt_xdate()
    
    
    # plot SWG schedule
    
    swg_schedule_color = dict(Common="IndianRed", Special="LightSalmon", Discretionary="DarkRed")
    iSchedule += 2
    for iEntry in range(len(swg_schedule.phaseNameList)):
        startPoint = swg_schedule.startTimeList[iEntry]
        duration = swg_schedule.durationInDays[iEntry].total_seconds()/3600/24
        ax.barh(iSchedule,  duration, left=startPoint, align='center', height=1.6, color=swg_schedule_color[swg_schedule.phaseNameList[iEntry].split(' ')[0]
    ])
        textPosition = startPoint+swg_schedule.durationInDays[iEntry]/2
        if textPosition.date() < xLimEnd and textPosition.date() > xLimStart and labelSWGschedule: # if in xLim range
            printText = swg_schedule.phaseNameList[iEntry]
            if "(see Note" in printText: # remove note
                printText = printText[:printText.index("(see Note")-1]
            ax.text(textPosition, iSchedule, printText , rotation=45, backgroundcolor='w', alpha=0.5, ha='center', va='center' )
    
    
    if swg_plotNextMonth:
        for iEntry in range(len(swg_schedule_nextMonth.phaseNameList)):
            startPoint = swg_schedule_nextMonth.startTimeList[iEntry]
            duration = swg_schedule_nextMonth.durationInDays[iEntry].total_seconds()/3600/24
            ax.barh(iSchedule,  duration, left=startPoint, align='center', height=1.6, color=swg_schedule_color[swg_schedule_nextMonth.phaseNameList[iEntry].split(' ')[0]
        ])
            textPosition = startPoint+swg_schedule_nextMonth.durationInDays[iEntry]/2
            if textPosition.date() < xLimEnd and textPosition.date() > xLimStart and labelSWGschedule: # if in xLim range
                printText = swg_schedule_nextMonth.phaseNameList[iEntry]
                if "(see Note" in printText: # remove note
                    printText = printText[:printText.index("(see Note")-1]
                ax.text(textPosition, iSchedule, printText , rotation=45, backgroundcolor='w', alpha=0.5, ha='center', va='center' )
      
    yTickList.append(iSchedule)
    yLabelList.append("SWG schedule")
                
    # plot line for now
    plt.plot([now, now], ax.get_ylim(), color='red', linewidth=3)
    
    # format plot
    ax.set_xlim(xLimStart, xLimEnd)
    ax.xaxis.set_major_formatter( FuncFormatter(dateFormatter) ) 
    ax.grid(True)
    plt.xticks(rotation=0)
    ax.set_yticks(yTickList)
    ax.set_yticklabels(yLabelList)
    ax.set_xlabel("time")
    
    
    nowUTC   =  datetime.datetime.utcnow()
    nowLocal =  datetime.datetime.now()
    plt.title("Current now: {} (UTC)  || {}  (local)".format(nowUTC.strftime("%Y-%m-%d %H:%M"), nowLocal.strftime("%Y-%m-%d %H:%M")))
    
    #make legends
    import matplotlib.patches as mpatches
    allPrograms = controlProgramColor.keys()
    legendPatches = []
    for program in allPrograms:
        legendPatches.append(mpatches.Patch(color=controlProgramColor[program], label=program))
    
    legend_handle = plt.legend(handles=legendPatches, bbox_to_anchor=(1.025, 0.5), loc=2, borderaxespad=0.)
    
    ax.add_artist(legend_handle)
    
    allPrograms = swg_schedule_color.keys()
    legendPatches = []
    for program in allPrograms:
        legendPatches.append(mpatches.Patch(color=swg_schedule_color[program], label=program))
    legend_handle = plt.legend(handles=legendPatches, bbox_to_anchor=(1.025, 1), loc=2, borderaxespad=0.)
    
    return fig
# %% 
# check status and create html text file
def write_status_html_text(fileName,schedule_list):
    
    nMonth2show = 3
    now = datetime.datetime.now()
    dateList = []
    monthNameList = []
    SWG_schedule_available = []
    for iMonth in range(nMonth2show+1):
        dateList.append(datetime.datetime(now.year+int(np.floor((now.month-1+iMonth)/12)), int(np.mod(now.month-1+iMonth,12)+1), 1))
        url = "http://sdnet.thayer.dartmouth.edu/web_data/schedules/swg/{}{:>02d}.swg".format(dateList[-1].year, dateList[-1].month)
        
        try:
            schedule_txt = urllib.request.urlopen(url)
            SWG_schedule_available.append(True)
        except:
            SWG_schedule_available.append(False)
    
    githubSchedAvaiable = []
    
    for iMonth in range(nMonth2show):
        monthNameList.append(dateList[iMonth].strftime("%B"))
        githubSchedAvaiable.append( [])
        for iSchedule in range(len(schedule_list)):
            scheule_end = schedule_list[iSchedule][0].startTimeList[-1] + datetime.timedelta(minutes=schedule_list[iSchedule][0].durationList[-1])
            githubSchedAvaiable[iMonth].append(scheule_end >= dateList[iMonth+1])
    
    githubSchedErrors = []
    allErrorMSGs = ""
    for iSchedule in range(len(schedule_list)):
        githubSchedErrors.append(schedule_list[iSchedule][0].errorFound)
        allErrorMSGs += schedule_list[iSchedule][0].errorMSG
        
    # construt html code
    htmlTable = '<table>\n'
    htmlTable += "<tr> <th> Schedule </th> <th> " + " </th> <th> ".join(monthNameList) + "</th> </tr> \n"
    
    htmlTable +=  '<tr> <td>Software Working Group</td> '
    for iMonth in range(nMonth2show):
        if SWG_schedule_available[iMonth]:
             htmlTable +=  " <td id=green>Avaiable</td> "
        else:
             htmlTable +=  " <td id=nothing>Not Avaiable</td> "
    htmlTable += "</tr> \n"
    
    htmlTable +=  '<tr> <td>Git Schedule </td> '
    for iMonth in range(nMonth2show):
        if all(githubSchedAvaiable[iMonth]):
             htmlTable +=  " <td id=green>Avaiable</td> "
        else:
             if SWG_schedule_available[iMonth]:
                 
                 daysLeft = (dateList[iMonth] - datetime.datetime.now() ).days
                 if  daysLeft < 10:
                     htmlTable +=  " <td id=red>Not Avaiable (" + str(int(daysLeft)) + " days left)</td> "
                 else:
                     htmlTable +=  " <td id=orange>Not Avaiable (" + str(int(daysLeft)) + " days left)</td> "
             else:
                 htmlTable +=  " <td id=green>Not Avaiable</td> "
    htmlTable += "</tr> \n"
    
    
    htmlTable +=  '<tr> <td>Git Errors </td> '
    for iMonth in range(nMonth2show):
        if any(githubSchedErrors):
             htmlTable +=  " <td id=orange>Found</td> "
        else:
             htmlTable +=  " <td id=green>Ok</td> "
    htmlTable += "</tr> \n"
    
    htmlTable += "</table>\n"
    
    htmlTable += '\n\n<h3> Error messages: </h3>\n<Pre>\n<p style="margin-left:30px;">\n'
    htmlTable += allErrorMSGs #.replace('\n', '<br>\n')
    htmlTable += '\n</p></Pre>\n'
    
    htmlTable += '\n[ last update ' + now.strftime("%Y/%m/%d %H:%M %Z") + '] \n'
    
    # write
    
    with open(fileName, "w") as f:
        f.write(htmlTable)


# %%

def save_figure(fileName, schedule_list):
    plotRange = [-1, 3] # in days from today
    fig = create_figure(schedule_list, plotRange)
    fig.savefig(fileName)
    plt.close(fig)


# %%    
    

root_schedule_url = 'https://raw.githubusercontent.com/UAF-SuperDARN-OPS/schedule_files/'

schedule_file_list = [["adak/ade/ade.a.scd", "adak/ade/ade.a.special"], ["adak/adw/adw.a.scd", "adak/adw/adw.a.special"], ["kodiak/kod/kod.c.scd", "kodiak/kod/kod.c.campaign.scd"], ["kodiak/kod/kod.d.scd", "kodiak/kod/kod.d.campaign.scd"], ['mcmurdo/mcm/mcm.a.scd'], ['mcmurdo/mcm/mcm.b.scd'], ['southpole/sps/sps.a.scd']]
#schedule_file_list = [[]]
#, 'kodiak/kod/kod.c.campaign.scd', 'kodiak/kod/kod.d.campaign.scd'
schedule_file_list.reverse() # reverse order to have adak at the top
schedule_list = []

for radar_file_list in schedule_file_list:
    schedule_list.append([])
    for url_schedule in radar_file_list:
        schedule_list[-1].append(read_schedule(root_schedule_url + url_schedule))

now = datetime.datetime.now()
swg_schedule = read_swg_schedule(now.month, now.year)

swg_plotNextMonth = now.day > 15
if swg_plotNextMonth:
    nextMonth = now + datetime.timedelta(days=30)
    swg_schedule_nextMonth = read_swg_schedule(nextMonth.month, nextMonth.year)

# %% write data for website
fileName_txt = 'status_website/schedule_status_text'
fileName_png = "status_website/schedule_plot.png"

save_figure(fileName_png, schedule_list)
write_status_html_text(fileName_txt,schedule_list)

# %%

# %%
plotRange = [-1, 3] # in days from today
##fig = create_figure(schedule_list, plotRange)

#plotRange = [-25, 35] # in days from today
#labelSWGschedule = False

##plt.show()
#savefig('foo.png')