import subprocess
import time
import pdb
import signal
TIMEOUT = 40

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Exception("command timed out")

signal.signal(signal.SIGALRM, alarm_handler)


# runs a command over ssh, returns response
# this version is a bit more robust.. uses echo to pipe in commands
def remote_command_echo(user, radar, command, verbose = True, port = 22):
    commandecho = subprocess.Popen(['echo', command], stdout=subprocess.PIPE)

    try:
        signal.alarm(TIMEOUT)
        failed = True
        out = ''
        cmdlist = ["ssh", '-T', user + '@' + radar, '-p', str(port)]
        s = subprocess.Popen(cmdlist, stdin = commandecho.stdout, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        commandecho.stdout.close()
        if verbose:
            print(' '.join(cmdlist) + ' ' + command)
        out, err = s.communicate()
    except:
        print('command ' + command + ' radar ' + radar + ' failed')

    signal.alarm(0)
    return out


# runs a command over ssh, returns response
def remote_command(user, radar, command):
	try:
		signal.alarm(TIMEOUT)
		failed = True
		out = ''
		cmdlist = ["ssh", user + '@' + radar, '"' + command + '"']
		if radar[0] == 'a':
			if 'linux' in radar or 'lnx' in radar:
				cmdlist = ["ssh", user + '@' + radar, '-p', '7022', '"' + command + '"']
			if 'qnx' in radar or 'ros' in radar:
				cmdlist = ["ssh", user + '@' + radar, '-p', '8022', '"' + command + '"']
		
		print( cmdlist)
		s = subprocess.Popen(cmdlist, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		out, err = s.communicate()
	except:
		print('command ' + command + ' radar ' + radar + ' failed' )
	
	signal.alarm(0)	
	return out

def adak_ddscheck(hours = 3):
	fails = []
	try:
		west = remote_command('radar','ade-lnx','ddscheck_west')
		east = remote_command('radar','ade-lnx','ddscheck_east')
		
		current_time = time.time()
		
		threshold = 60 * 60 * hours # warn if dds fault in past 3 hours..
		
		if west != '\n':
			westfault = int(west.split(' ')[2])
			if current_time - westfault < threshold:
				fails.append('adw dds failure in past ' + str(hours) + ' hours')
				print ('west dss fail')
			else:
				print('west dds check pass')

		if east != '\n':
			eastfault = int(east.split(' ')[2])			
			if current_time - eastfault < threshold:
				fails.append('ade dds failure in past ' + str(hours) + ' hours')
				print('east dss fail')
			else:
				print('east dds check pass')
	except:
		fails = ['dds check completely failed..']
	return fails


def qnx_roscheck(radar, fails, user = 'root'):
	ret = remote_command('root',radar,'ros_ps_check')	
	print (ret)
	if int(ret) != 0:
		fails.append('ros process check of ' + radar + ' failed') 
		print( radar + ' failed ros process check')
	else:
		print(radar + ' passed ros process check')

def twohourcheck(radar, fails, ratio = 10):
	ret = remote_command('radar',radar,'twohourcheck')	
	print(radar + ' two hour slist ratio of ' + str(ret))
	try:
		if int(ret) > ratio:
			fails.append('radar ' + radar + ' failed two hour nlag/slist ratio check') 
	except ValueError:
		fails.append('radar ' + radar + ' failed two hour nlag/slist ratio check - could not connect') 

def fitacftime(radar, fails):
	ret = remote_command('radar',radar,'fitacf_time')	
	print( radar + ' time since last fitacf write ' + str(ret))
	try:
		if int(ret) > 120:
			fails.append('radar ' + radar + ' last wrote a fitacf ' + ret + ' seconds ago') 
	except ValueError:
		fails.append('radar ' + radar + ' failed fitacf write time check - could not connect') 

def nave_check(radar, fails):
	ret = remote_command('radar',radar,'integration_check')	
	print( radar + ' nave in last two hours' + str(ret))
	try:
		if int(ret) < 100:
			fails.append('radar ' + radar + ' only completed ' + ret + ' pulse sequences in the past hour') 
	except ValueError:
		fails.append('radar ' + radar + ' nave check failed - could not connect') 



def twohourchecks():
	fails = []
	twohourcheck('adak-lnx', fails)
	twohourcheck('mcm-lnx', fails)
	twohourcheck('ksr-lnx', fails, ratio = 14)
	twohourcheck('kod-lnx', fails, ratio = 12)
	#twohourcheck('sps-lnx', fails)
	return fails

def integration_period_nave():
	fails = []
	nave_check('adak-lnx', fails)
	nave_check('mcm-lnx', fails)
	nave_check('kod-lnx', fails)

def fitacftimes():
	fails = []
	fitacftime('mcm-lnx', fails)
	fitacftime('ksr-lnx', fails)
	fitacftime('adak-lnx', fails)
	fitacftime('kodiak-lnx', fails)
	#fitacftime('sps-lnx', fails)
	return fails


def qnx_roschecks():
	fails = []
	qnx_roscheck('adak-qnx', fails, user = 'root')
	qnx_roscheck('mcm-qnx', fails, user = 'root')
#	qnx_roscheck('kodiak-dds', fails, user = 'radar')
#	qnx_roscheck('kodiak-imaging', fails, user = 'radar')
	return fails

def timedelta(user, radar, command, fails, threshold):
	print('checking ' + radar)
	radartime = int(remote_command(user, radar, command))
		#radartime = time.time() # ignore connection loss, this will be picked up by other modules..
	#	print radar + ' connection lost, skipping'

	current_time = time.time()
	print('delta: ' + str(current_time - radartime))
	if abs(current_time - radartime) > threshold:
		print( radar + ' fails time threshold check') 	
		fails.append(radar)
	return fails

def timechecks(maxdiff = 60):
	fails = []
	
	#fails = timedelta('radar', 'mcm-lnx', '"ssh root@mcm-qnx \"date -t\""', fails, maxdiff)
	fails = timedelta('radar', 'kod-lnx', '"ssh radar@kodiak-dds \"date -t\""', fails, maxdiff)
	fails = timedelta('radar', 'kod-lnx', '"ssh radar@kodiak-imaging \"date -t\""', fails, maxdiff)
	#fails = timedelta('radar', 'sps-lnx', '"ssh root@sps-ros \"date -t\""', fails, maxdiff)
	#fails = timedelta('radar', 'adak-qnx',  '"\"date -t\""', fails, maxdiff)
	#fails = timedelta('radar', 'mcm-lnx', '"date +\"%s\""', fails, maxdiff)
	#fails = timedelta('radar', 'sps-lnx', '"\"date +\"%s\""', fails, maxdiff)
	#fails = timedelta('radar', 'adak-lnx', '"\"date +\"%s\""', fails, maxdiff)
	#fails = timedelta('radar', 'kod-lnx', '"\"date +\"%s\""', fails, maxdiff)

	return fails

if __name__ == '__main__':
	fails = []
	qnx_roschecks()

	print( fails)
