#!/bin/bash

PIPE=/tmp/t3guard_dhcp_pipe

if [[ ! -p $PIPE ]]; then
    # no checker-running to read from pipe...
    exit 0;
fi

echo $@ >> $PIPE & 
