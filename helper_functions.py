# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 10:04:51 2017

@author: mguski
"""

import re

# %% read config file
def read_config_file(fileName):
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
        
    return configDict