#!/bin/bash

PIPE=/tmp/doorguard_dhcp_pipe

if [[ ! -p $PIPE ]]; then
    # no checker-running to read from pipe...
    exit 0;
fi

echo $@ >> $PIPE & 
