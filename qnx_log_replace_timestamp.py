# -*- coding: utf-8 -*-
"""
Function to replace timestamps of qnx log/err files with readable time
Created on Tue Jan 24 17:02:22 2017

@author: mguski
"""

# %%
fileName = 'server_err.txt'
#fileName = 'server_log.py'
with open(fileName, 'r') as f:
    log = f.read()
    
    
# %%
import re
import datetime

def niceTime(t_stamp):
    print(t_stamp)
    x = datetime.datetime.utcfromtimestamp(int(t_stamp.group(0)))
    return x.strftime("[%m/%d %H:%M:%S]")

res = re.sub("\d{10}", niceTime, log)
print(res)
