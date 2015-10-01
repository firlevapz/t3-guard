#!/bin/bash

LOGFILE=/home/pi/doorguard/dhcp-log.txt
BASEDIR=$(dirname $0)

echo $@ >> $LOGFILE

$BASEDIR/dhcp-wake-device.py $@ &
