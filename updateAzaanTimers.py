#!/usr/bin/env python

import datetime
from datetime import timedelta
import time
import sys
import os
import random
import getpass

home = os.path.expanduser("~")
user = getpass.getuser()
sys.path.insert(0, home+'/adhan/crontab')

from praytimes import PrayTimes
PT = PrayTimes() 

from crontab import CronTab
system_cron = CronTab(user=user)

#Get list of available adhaans
adhan_list = os.listdir(home+'/adhan/adhans-normal')

def generateRandomAdhanPlayCommand(adhan_list):
	return 'omxplayer -o local %s/adhan/adhans-normal/%s > /dev/null 2>&1'%(home,random.choice(adhan_list))

now = datetime.datetime.now()
strPlayFajrAzaanMP3Command = 'omxplayer -o local %s/adhan/Adhan-fajr.mp3 > /dev/null 2>&1'%home
strPlayAzaanMP3Command = 'omxplayer -o local %s/adhan/Adhan-Makkah.mp3 > /dev/null 2>&1'%home
strUpdateCommand = 'python %s/adhan/updateAzaanTimers.py >> %s/adhan/adhan.log 2>&1'%(home,home)
strClearLogsCommand = 'truncate -s 0 %s/adhan/adhan.log 2>&1'%home
strJobComment = 'rpiAdhanClockJob'

#Set latitude and longitude here
#--------------------
lat = 34.126271
long = -117.6758092

#Set calculation method, utcOffset and dst here
#By default system timezone will be used
#--------------------
PT.setMethod('Makkah')
utcOffset = -(time.timezone/3600)
isDst = time.localtime().tm_isdst

#HELPER FUNCTIONS
#---------------------------------
#---------------------------------
#Function to add azaan time to cron
def addAzaanTime (strPrayerName, strPrayerTime, objCronTab, strCommand):
  job = objCronTab.new(command=strCommand,comment=strPrayerName)  
  timeArr = strPrayerTime.split(':')
  hour = timeArr[0]
  min = timeArr[1]
  job.minute.on(int(min))
  job.hour.on(int(hour))
  job.set_comment(strJobComment)
  print job
  return

def addUpdateCronJob (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.minute.on(30)
  job.hour.on(2)
  job.set_comment(strJobComment)
  print job
  return

def addClearLogsCronJob (objCronTab, strCommand):
  job = objCronTab.new(command=strCommand)
  job.day.on(1)
  job.minute.on(0)
  job.hour.on(0)
  job.set_comment(strJobComment)
  print job
  return
#---------------------------------
#---------------------------------
#HELPER FUNCTIONS END

# Remove existing jobs created by this script
system_cron.remove_all(comment=strJobComment)

# Calculate prayer times
times = PT.getTimes((now.year,now.month,now.day), (lat, long), utcOffset, isDst) 
print times['fajr']
print times['dhuhr']
print times['asr']
print times['maghrib']
print times['isha']

#Tiny isha hack to add 3 hours -- I have NO idea if it'll work long term!
isha_hours = times['isha'].split(':')[0]
isha_mins = times['isha'].split(':')[1]
isha_hours = str((int(isha_hours)+3)%24)
times['isha'] = isha_hours +':' +isha_mins


# Add times to crontab
addAzaanTime('fajr',times['fajr'],system_cron,strPlayFajrAzaanMP3Command)
addAzaanTime('dhuhr',times['dhuhr'],system_cron,generateRandomAdhanPlayCommand(adhan_list))
addAzaanTime('asr',times['asr'],system_cron,generateRandomAdhanPlayCommand(adhan_list))
addAzaanTime('maghrib',times['maghrib'],system_cron,generateRandomAdhanPlayCommand(adhan_list))
addAzaanTime('isha',times['isha'],system_cron,generateRandomAdhanPlayCommand(adhan_list))

# Run this script again overnight
addUpdateCronJob(system_cron, strUpdateCommand)

# Clear the logs every month
addClearLogsCronJob(system_cron,strClearLogsCommand)

system_cron.write_to_user(user=user)
print 'Script execution finished at: ' + str(now)
