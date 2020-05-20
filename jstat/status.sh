#!/bin/bash

# clear old
rm status
rm storage

# machine status
neo=$(neofetch)

os=$(echo "$neo" | grep 'OS')
host=$(echo "$neo" | grep 'Host')
uptime=$(echo "$neo" | grep 'Uptime')
kernel=$(echo "$neo" | grep 'Kernel')
cpu=$(echo "$neo" | grep 'CPU')
memory=$(echo "$neo" | grep 'Memory')

{
echo "$os"
echo "$host"
echo "$uptime"
echo "$kernel"
echo "$cpu"
echo "$memory"
} >> status

# storage
drives=$(df -h | grep '/dev/sd')

echo "$drives" >> storage