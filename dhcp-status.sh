#!/bin/bash

LOGFILE=/home/pi/doorguard/dhcp-log.txt
PIPE=/tmp/doorguard_dhcp_pipe

echo $@ >> $LOGFILE  # write to logfile, just for logging

if [[ ! -p $PIPE ]]; then
    # no checker-running to read from pipe...
    exit 0;
fi

echo $@ >> $PIPE & 
