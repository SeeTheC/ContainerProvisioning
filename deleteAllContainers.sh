#!/bin/bash

serverList=`grep host server.config | awk -F'"' '{print $4}'`
match=`echo $serverList | grep -o "\b$1\b"`
if [ "$match" != "" ]
then
    echo "Deleting all containers on $match"
    lxc list $match: | head -n -1 | tail -n +4 | awk '{if (NR % 2 == 1) {print "lxc delete match:"$2" --force"}}' | sed 's/match/'$match'/g' | bash
else
    echo "Deleting all containers on this machine"
    lxc list | head -n -1 | tail -n +4 | awk '{if (NR % 2 == 1) {print "lxc delete "$2" --force"}}' | bash
fi
