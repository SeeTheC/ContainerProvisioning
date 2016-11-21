#!/bin/bash

trap "echo 'Killing Process' && pkill -9 stress && exit" INT
echo "Press Ctrl + C to stop"
while [[ 1 ]]
do
    threshold=`echo "$(( RANDOM % 100 + 1 )) / 100" | bc -l`
    totalSystemMemory=`awk '/MemTotal/{print $2;}' < /proc/meminfo`
    freeMemory=`awk '/MemFree/{print $2;}' < /proc/meminfo`
    usedMemory=`echo "$totalSystemMemory - $freeMemory" | bc`
    totalMemoryToUse=`echo "$totalSystemMemory * $threshold" | bc`
    extraMemoryToUse=`echo "$totalMemoryToUse - $usedMemory" | bc`

    if [[ `echo "$extraMemoryToUse > 0" | bc -l` -eq 0  ]]
    then
        continue
    fi
    echo "Total System Memory: $totalSystemMemory kB"
    echo "Extra Memory to use: $extraMemoryToUse kB (threshold = $threshold)"

    randomTime=$(( RANDOM % 15 + 1 ))
    echo "Load Duration: $randomTime"
    stress --vm-bytes `echo "$extraMemoryToUse""k"` --vm-keep -m 1 &
    sleep $randomTime
    pkill stress
done
