#!/bin/bash

threshold=0.8

totalSystemMemory=`awk '/MemTotal/{print $2;}' < /proc/meminfo`
freeMemory=`awk '/MemFree/{print $2;}' < /proc/meminfo`
usedMemory=`echo "$totalSystemMemory - $freeMemory" | bc -l`
totalMemoryToUse=`echo "$totalSystemMemory * $threshold" | bc -l`
extraMemoryToUse=`echo "$totalMemoryToUse - $usedMemory" | bc -l`

echo "Total System Memory: $totalSystemMemory kB"
echo "Total Memory to use: $totalMemoryToUse kB (threshold = $threshold)"

echo "Press Ctrl + C to exit"
stress --vm-bytes `echo "$totalMemoryToUse""k"` --vm-keep -m 1
