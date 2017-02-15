#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Script for cronjob to update schedule plots and copy to chiniak
"""
import os
import updateWebsite_schedules

postCommand = "scp /home/radar/repos/SuperDARN_Tools/status_website/liveData/* ak_data@chiniak:/home/ak_data/repos/SuperDARN_Tools/status_website/liveData/"
    

process = updateWebsite_schedules.scheduleUpdater(60000 )
process.run() 
os.system(postCommand) 
