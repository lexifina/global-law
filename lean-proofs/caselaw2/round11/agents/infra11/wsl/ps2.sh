#!/bin/bash
ps -eo pid,etime,args | grep "[r]11_run.sh" | awk '{print $1, $2, $NF}' | sort -u -k3
