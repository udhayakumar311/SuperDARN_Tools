# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 10:09:04 2016

@author: mguski
"""



import httplib2
import re
import datetime

UNKNOWN  = -1
DEBUG    = 10
INFO     = 20
WARNING  = 30 
ERROR    = 40
CRITICAL = 50
FATAL    = 60 

levelValueList = [UNKNOWN, DEBUG,INFO, WARNING, ERROR, CRITICAL, FATAL]
levelNameList = ['UNKNOWN', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL']

# define font color and style
cHEADER = '\033[95m'
cOKBLUE = '\033[94m'
cOKGREEN = '\033[92m'
cWARNING = '\033[93m'
cFAIL = '\033[91m'
cENDC = '\033[0m'
cBOLD = '\033[1m'
cUNDERLINE = '\033[4m'

#level2colorDict = dict(UNKNOWN=FAIL)

# %%

class logMessages():
   
    def __init__(self, source):
        self.source = source
        self.dateList = []
        self.levelList = []
        self.msgList = []
        
    def add_log(self,  level, msg , date=datetime.datetime.now()):
        self.dateList.append(date.replace(microsecond=0))
        self.levelList.append(level)
        self.msgList.append(msg)
        
    def print_log(self, level=WARNING):
        self.sort_log()
        
        for iLog in range(self.nLogs):
            if self.levelList[iLog] >= level or self.levelList[iLog] == UNKNOWN:
                print("{} {: <8} {}".format(self.dateList[iLog], levelNameList[levelValueList.index(self.levelList[iLog])], self.msgList[iLog]))
        
    def sort_log(self):
        print("TODO sort logs")
        

    @property    
    def nLogs(self):
        return len(self.msgList)
        
    



# %%


def get_outlet_status(ipAddress, auth):
    # output is [ [switchNo_int, switchName_str, powered_bool], [switchNo_int, ...] ... ]
    url = 'http://' + ipAddress + '/index.htm'
    h = httplib2.Http()
    resp, content = h.request( url, 'GET', headers = { 'Authorization' : 'Basic ' + auth })
    content = content.decode("UTF-8")
    
    nSwitches = 8 
    switchData = []
    
    idxStatus_end = content.find('<tr ', content.find('Individual Control')) +4
    for iSwitch in range(nSwitches):
        switchData.append([])
        idxStatus_start = content.find('<tr ', idxStatus_end)
        idxStatus_end = content.find('</tr>', idxStatus_start)
        currentPart = content[idxStatus_start:idxStatus_end]
        switchData[-1].append(int(re.search('<td align=center>(.?)</td>', currentPart).group(1)))
        switchData[-1].append(re.search('<td>(.*?)</td>', currentPart).group(1))
        switchData[-1].append(re.search('<b><.*>(.*?)<.*></b>(.*?)</td>', currentPart).group(1) == 'ON')
    
    return switchData


    


def get_syslog(ipAddress, auth):
    #% get syslog html
    url = 'http://' + ipAddress + '/syslog.htm'
    h = httplib2.Http()
    resp, content = h.request( url, 'GET', headers = { 'Authorization' : 'Basic ' + auth })
    content = content.decode("UTF-8")
    #%
    
    startTag = '<div id="syslog" '
    endTag   = "</div>"
    
    startIdx = content.find(startTag)
    if startIdx == -1:
        print("error")
        print(content)
        return content
    endIdx = content.find(endTag, startIdx)
    
    log_content = content[startIdx:endIdx]
    
    startTag_line = '<tr><td nowrap>'
    endTag_line = '</td></tr>'
    currentChar = 0
    allLogLines = []
    
    while True:
        lineStartIdx = log_content.find(startTag_line, currentChar)
        if lineStartIdx == -1:
            break
        lineEndIdx = log_content.find(endTag_line, lineStartIdx)
        allLogLines.append(log_content[lineStartIdx+len(startTag_line):lineEndIdx])
        currentChar = lineEndIdx + len(endTag_line)
        
    return allLogLines


def check_outlet_status(logs, outletStatus):

    for switchStatus in outletStatus:
        if not switchStatus[2]:
            logs.add_log( ERROR, "Error: Web Power Switch Outlet {} ({}) is OFF.".format(switchStatus[0], switchStatus[1]))
        else:
            logs.add_log( DEBUG, "Web Power Switch Outlet {} ({}) is ON.".format(switchStatus[0], switchStatus[1]))        

            
def check_log_messages(logs, allLogLines, lastKnownPowerLoss):
    # part 1: rating of log messages
    debugPatterList = ['.*: Successful .* authentication for .* from .*', '.* has logged out from .*', '.* System time set by hardware clock .*', '.* booted OK.*', '.*: Network cable [plugged in|unplugged]', '.* Session for .* is timed out']
    infoPatternList = ['.* has changed .*', '.*: WebI: .* has requested to .*', '.*: Outlet .* is .*']
    lastPowerLoss = "NO ENTRY"
    nFailedAuthentications = 0
    
    for line in allLogLines:
        if len(line) == 0:
            continue
        
        if any([re.match(pattern, line)!= None for pattern in debugPatterList]):
            parse_date_and_add_log(logs, line, DEBUG )
            continue
        
        if any([re.match(pattern, line)!= None for pattern in infoPatternList]):
            parse_date_and_add_log(logs, line, INFO )
            continue 
        
        if re.match(".* Failed .* authentication attempt for .*", line):
            parse_date_and_add_log(logs, line, INFO )
            nFailedAuthentications +=1
            continue 
        
        
        if re.match(".*: Power Loss Recovery: .*", line):
            lastPowerLoss = datetime.datetime.strptime(line[:16], "%b %d %H:%M:%S ")

            if re.match(".*: Power Loss Recovery: all Outlets ON.*", line):
                parse_date_and_add_log(logs, line, DEBUG )
            else:
                line += "<== Configuration Error: Not all Outlets will turn on after power loss. Change in web interface to ALL OUTLETS ON!"
                parse_date_and_add_log(logs, line, ERROR )
            continue
        print("Unknwn : "  + line)
        parse_date_and_add_log(logs, line, UNKNOWN ) 
    
    # PART 2: analysis

    # failed logins
    if nFailedAuthentications > 0: # TODO: check in which time period they occured
        msg = "Analysis: {} failed attempts to log in.".format(nFailedAuthentications)
        if nFailedAuthentications > 100:
            logs.add_log(  CRITICAL, msg)
        elif nFailedAuthentications > 10:
            logs.add_log(WARNING, msg)
        else:
            logs.add_log( INFO, msg)

    # new power loss?
            
    # since no year is given, take last possible year
    returnPowerLoss = []
    if lastPowerLoss != "NO ENTRY":
        lastPowerLoss = lastPowerLoss.replace(year=int(datetime.datetime.now().year))
        while lastPowerLoss > datetime.datetime.now():
            lastPowerLoss = lastPowerLoss.replace(year=int(lastPowerLoss.year-1))
        
        if lastPowerLoss != lastKnownPowerLoss:
            logs.add_log("New power loss. Power recovery on {}. (Last registered recover was {})".format(lastPowerLoss, lastKnownPowerLoss), WARNING)
            returnPowerLoss = lastPowerLoss

    return returnPowerLoss
    
def parse_date_and_add_log(log, line, level):

     date = datetime.datetime.strptime(line[:16], "%b %d %H:%M:%S ").replace(year=int(datetime.datetime.now().year))
     while date > datetime.datetime.now():
         date = date.replace(year=int(date.year-1))
     log.add_log(level, line[16:], date)
# %%

ipAddress = '192.168.0.100'
# import base64
# auth = base64.encodestring( b'admin:dorian').decode("UTF-8")
auth = 'YWRtaW46ZG9yaWFu\n'

switchLogs = logMessages("PDU-1")

# Status of outlets
outletStatus = get_outlet_status(ipAddress, auth)
check_outlet_status(switchLogs, outletStatus)

# analyse logs
allLogLines  = get_syslog(ipAddress, auth)
lastKnownPowerLoss = datetime.datetime(2016, 12, 29, 12, 12, 42)
returnPowerLoss = check_log_messages(switchLogs, allLogLines, lastKnownPowerLoss)

if returnPowerLoss != []:
    print("TODO")
    



# %%

switchLogs.print_log(level=INFO)