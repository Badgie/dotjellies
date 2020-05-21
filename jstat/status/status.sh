#!/bin/bash

### machine
neo=$(neofetch)

os=$(echo "$neo" | grep 'OS' | tr "/" "!")
host=$(echo "$neo" | grep 'Host')
uptime=$(echo "$neo" | grep 'Uptime')
kernel=$(echo "$neo" | grep 'Kernel')
cpu=$(echo "$neo" | grep 'CPU')
memory=$(echo "$neo" | grep 'Memory' | tr "/" "!")
# rpi only
temp=$(vcgencmd measure_temp | sed -r "s/temp=//g" | sed -r "s/'//g")

sed -i "s/os=.*/os=$os/g" jstat.conf
sed -i "s/host=.*/host=$host/g" jstat.conf
sed -i "s/uptime=.*/uptime=$uptime/g" jstat.conf
sed -i "s/kernel=.*/kernel=$kernel/g" jstat.conf
sed -i "s/cpu=.*/cpu=$cpu/g" jstat.conf
sed -i "s/memory=.*/memory=$memory/g" jstat.conf
# rpi only
sed -i "s/temp=.*/temp=Core temp: $temp/g" jstat.conf

### storage
# get drives
drives=$(df -h | grep '/dev/sd')
# replace newline and percentage, and regex out paths
drives=$(echo "$drives" | tr "\n" ":" | tr "%" "P" | sed -r "s/(\/[a-zA-Z0-9]*)+//g")
sed -i "s/drives=.*/drives=$drives/g" jstat.conf

### CPU
cpus=$(< /proc/stat grep 'cpu' | tr "\n" ":")
cpu_old=$(< jstat.conf grep 'cpu_new')

if [[ "$cpu_old" == 'cpu_new=' ]]; then
    cpu_old=''
else
    cpu_old=$(echo "$cpu_old" | sed -r "s/cpu_new=//g")
fi

sed -i "s/cpu_new=.*/cpu_new=$cpus/g" jstat.conf
sed -i "s/cpu_old=.*/cpu_old=$cpu_old/g" jstat.conf
