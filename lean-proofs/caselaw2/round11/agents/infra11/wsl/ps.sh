#!/bin/bash
ps -eo pid,ppid,etime,stat,args --forest | grep -A5 "r11_run" | grep -v grep | cut -c1-200
