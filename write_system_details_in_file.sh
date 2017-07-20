#/bin/hash
###########################################################################################################
# script copied from http://www.techpaste.com/2012/01/shell-script-collect-system-information/



#/bin/hash
# copied (with modifications)  from http://www.techpaste.com/2012/01/shell-script-collect-system-information/

DATE=`/bin/date +date_%d-%m-%y_time_%H-%M-%S`
Time(){

echo " Computer Time : `date` "
}
GenInfo(){
echo "___________________________________________________________________________________"
echo "**** General Information About This Computer ****"
echo "___________________________________________________________________________________"
echo "This Computer Using `uname -m` architecture ;"
echo "The Linux Kernel Used on this computer `uname -r`"
echo -e "This Linux Distro. Used On this computer `head -n1 /etc/issue`"
echo "The Host Name Of this computer is `hostname`"
echo "The Name Of the user Of this computer is `whoami` "
echo "The Number Of The Users That Using This Computer `users | wc -w` Users "
echo "The System Uptime = `uptime | awk '{ gsub(/,/, ""); print $3 }'` (Hrs:Min)"
echo "The Run level Of Current OS is `runlevel`"
echo "The Number OF Running Process :`ps ax | wc -l`"
echo "___________________________________________________________________________________"
}

CPUInfo(){ 
echo "___________________________________________________________________________________"
echo "****The CPU Infromation****"
echo "___________________________________________________________________________________"
echo "You Have `grep -c 'processor' /proc/cpuinfo` CPU(s)"
echo "Your CPU model name is `awk -F':' '/^model name/ { print $2 }' /proc/cpuinfo`"
echo "Your CPU vendor`awk -F':' '/^vendor_id/ { print $2 }' /proc/cpuinfo`"
echo "Your CPU Speed`awk -F':' '/^cpu MHz/ { print $2 }' /proc/cpuinfo`"
echo "Your CPU Cache Size`awk -F':' '/^cache size/ { print $2 }' /proc/cpuinfo`"
echo "___________________________________________________________________________________"
}

CPUFullInfo(){ 
echo "___________________________________________________________________________________"
echo "****Full CPU Infromation: /proc/cpuinfo****"
echo "_ Start of /proc/cpuinfo __________________________________________________________"
echo "`cat /proc/cpuinfo`"
echo "_ End of /proc/cpuinfo_____________________________________________________________"
}


MemInfo(){
echo "___________________________________________________________________________________"
echo " ****The Memory Information****"
echo "___________________________________________________________________________________"
echo "`cat /proc/meminfo`"
echo "___________________________________________________________________________________"
echo "`free -m`"
echo "___________________________________________________________________________________"
}

FileSInfo(){
echo "___________________________________________________________________________________"
echo "*****File Systems Infromation******"
echo "___________________________________________________________________________________"
echo "`df -h`"
echo "___________________________________________________________________________________"
}

PCIInfo(){
echo "___________________________________________________________________________________"
echo "******PCI devices on motherboard information {detailed}******"
echo "___________________________________________________________________________________"
echo "`lspci -tv`"
echo "___________________________________________________________________________________"
}


CronInfo(){
echo "___________________________________________________________________________________"
echo "****** cron jobs (crontab -l) ******"
echo "___________________________________________________________________________________"
echo "`crontab -l`"
echo "___________________________________________________________________________________"

}



NetInfo(){
echo "___________________________________________________________________________________"
echo "********Network Information********"
echo "___________________________________________________________________________________"
echo "`/sbin/ifconfig -a`"
echo "___________________________________________________________________________________"

}


Run(){
Time
GenInfo
CPUInfo
CPUFullInfo
MemInfo
FileSInfo
PCIInfo
CronInfo
NetInfo
}
log=Sysinfo_$DATE
Run | tee $log.txt
