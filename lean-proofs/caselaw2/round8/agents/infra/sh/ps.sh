ps -eo pid,etime,pcpu,args | grep -v grep | grep -E 'cmp|r8_run|caselaw2_|cp ' | head
ls ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/base_r8_v3.tmp 2>/dev/null | wc -l
