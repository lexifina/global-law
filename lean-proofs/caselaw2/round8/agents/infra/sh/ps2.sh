ps -eo pid,etime,pcpu,args | grep -v grep | grep -E 'caselaw2_|r8_run|xargs' | cut -c1-200 | head
uptime
