#!/bin/bash
# Fetch statute XML (point in time 2025-04-06) from legislation.gov.uk, politely (sequential, 1.5 s apart)
cd ~/cmp/uk/refs/leg
UA="Mozilla/5.0 (compatible; research-fetch)"
PIT=${PIT:-2025-04-06}
while read name path; do
  [ -z "$name" ] && continue
  out="$name.xml"
  [ -s "$out" ] && continue
  code=$(curl -sS -A "$UA" -o "$out" -w "%{http_code}" "https://www.legislation.gov.uk/$path/$PIT/data.xml")
  if [ "$code" != "200" ]; then
     sleep 1.5
     code2=$(curl -sS -A "$UA" -o "$out" -w "%{http_code}" "https://www.legislation.gov.uk/$path/data.xml")
     echo "$name $path PIT=$code current=$code2"
  else
     echo "$name $path PIT=200"
  fi
  sleep 1.5
done <<'LIST'
ita_p2c1 ukpga/2007/3/part/2/chapter/1
ita_p2c2 ukpga/2007/3/part/2/chapter/2
ita_p2c3 ukpga/2007/3/part/2/chapter/3
ita_p3c1 ukpga/2007/3/part/3/chapter/1
ita_p3c2 ukpga/2007/3/part/3/chapter/2
ita_p3c3 ukpga/2007/3/part/3/chapter/3
ita_p3c3A ukpga/2007/3/part/3/chapter/3A
ita_p3c4 ukpga/2007/3/part/3/chapter/4
ita_p8c2 ukpga/2007/3/part/8/chapter/2
ita_s989 ukpga/2007/3/section/989
ita_s1011 ukpga/2007/3/section/1011
itepa_p10c8 ukpga/2003/1/part/10/chapter/8
fa2004_s188 ukpga/2004/12/section/188
fa2004_s189 ukpga/2004/12/section/189
fa2004_s190 ukpga/2004/12/section/190
fa2004_s191 ukpga/2004/12/section/191
fa2004_s192 ukpga/2004/12/section/192
fa2004_s194 ukpga/2004/12/section/194
tcga_s1 ukpga/1992/12/section/1
tcga_s1A ukpga/1992/12/section/1A
tcga_s1B ukpga/1992/12/section/1B
tcga_s1H ukpga/1992/12/section/1H
tcga_s1I ukpga/1992/12/section/1I
tcga_s1J ukpga/1992/12/section/1J
tcga_s1K ukpga/1992/12/section/1K
tcga_s1L ukpga/1992/12/section/1L
tcga_s1M ukpga/1992/12/section/1M
tcga_s1N ukpga/1992/12/section/1N
tcga_s3 ukpga/1992/12/section/3
tcga_s4 ukpga/1992/12/section/4
sscba_s1 ukpga/1992/4/section/1
sscba_s5 ukpga/1992/4/section/5
sscba_s6 ukpga/1992/4/section/6
sscba_s8 ukpga/1992/4/section/8
sscba_s11 ukpga/1992/4/section/11
sscba_s11A ukpga/1992/4/section/11A
sscba_s15 ukpga/1992/4/section/15
sscba_s16 ukpga/1992/4/section/16
sscba_s17 ukpga/1992/4/section/17
sscba_s18 ukpga/1992/4/section/18
sscba_sch1 ukpga/1992/4/schedule/1
sscba_sch2 ukpga/1992/4/schedule/2
sscba_s141 ukpga/1992/4/section/141
sscba_s142 ukpga/1992/4/section/142
sscba_s145 ukpga/1992/4/section/145
fa2025_contents ukpga/2025/8/contents
fa2021_s5 ukpga/2021/26/section/5
sscr2001_r10 uksi/2001/1004/regulation/10
sscr2001_r11 uksi/2001/1004/regulation/11
sscr2001_r125 uksi/2001/1004/regulation/125
sscr2001_r131 uksi/2001/1004/regulation/131
cbrates2006_r2 uksi/2006/965/regulation/2
LIST
echo ALLDONE
