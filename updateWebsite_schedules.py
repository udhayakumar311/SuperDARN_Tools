# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 11:10:29 2017

@author: mguski
"""
import datetime
import read_schedules

class liveMonitor():
    def __init__(self, nMinutesCheckPeriod):
        self.nMinutesCheckPeriod = nMinutesCheckPeriod
        self.lastRunTime = []
        
    def minutes_to_next_check(self):
        if self.lastRunTime == []:
            return 0
        
        time2nextRun = self.lastRunTime + datetime.timedelta(minutes=self.nMinutesCheckPeriod) - datetime.datetime.utcnow()
        return time2nextRun.total_seconds() /60
    
    def run(self):
        print("run of parent class is doing nothing!")
        self.lastRunTime = datetime.datetime.utcnow()    
        
class scheduleUpdater(liveMonitor):
    def run(self):
        self.lastRunTime = datetime.datetime.utcnow() 
        # %% input 
        root_schedule_url = 'https://raw.githubusercontent.com/UAF-SuperDARN-OPS/schedule_files/'
        schedule_file_list = [["adak/ade/ade.a.scd", "adak/ade/ade.a.special"], ["adak/adw/adw.a.scd", "adak/adw/adw.a.special"], ["kodiak/kod/kod.c.scd", "kodiak/kod/kod.c.campaign.scd"], ["kodiak/kod/kod.d.scd", "kodiak/kod/kod.d.campaign.scd"], ['mcmurdo/mcm/mcm.a.scd'], ['mcmurdo/mcm/mcm.b.scd'], ['southpole/sps/sps.a.scd']]
        
        # %% output
        fileName_txt = 'status_website/liveData/schedule_status_text'
        fileName_png = "status_website/liveData/schedule_plot.png"
        
        # %% read git schedules
        
        schedule_file_list.reverse() # reverse order to have adak at the top
        schedule_list = []
        
        for radar_file_list in schedule_file_list:
            schedule_list.append([])
            for url_schedule in radar_file_list:
                schedule_list[-1].append(read_schedules.read_schedule(root_schedule_url + url_schedule))
          
        # %% write data for website
    
        read_schedules.save_figure(fileName_png, schedule_list)
        read_schedules.write_status_html_text(fileName_txt,schedule_list)
    
if __name__ == '__main__':
    su = scheduleUpdater(11)
    su.run()    
    