#!/bin/bash
cd ~/cmp/uk/refs/leg
UA="Mozilla/5.0 (compatible; research-fetch)"
while read name path pit; do
  [ -z "$name" ] && continue
  out="$name.xml"
  [ -s "$out" ] && continue
  if [ "$pit" = "-" ]; then url="https://www.legislation.gov.uk/$path/data.xml"; else url="https://www.legislation.gov.uk/$path/$pit/data.xml"; fi
  code=$(curl -sS -A "$UA" -o "$out" -w "%{http_code}" "$url")
  echo "$name $url $code"
  sleep 1.5
done <<'LIST'
fa2025_s1 ukpga/2025/8/section/1 -
fa2025_s2 ukpga/2025/8/section/2 -
fa2025_s3 ukpga/2025/8/section/3 -
fa2025_s4 ukpga/2025/8/section/4 -
fa2025_s7 ukpga/2025/8/section/7 -
cbrates2006_r2_0407 uksi/2006/965/regulation/2 2025-04-07
sscr2001_r91 uksi/2001/1004/regulation/91 2025-04-06
sscr2001_r93 uksi/2001/1004/regulation/93 2025-04-06
sscr2001_r94 uksi/2001/1004/regulation/94 2025-04-06
sscba_s141_cur ukpga/1992/4/section/141 -
ita_s1012 ukpga/2007/3/section/1012 2025-04-06
ita_s1025 ukpga/2007/3/section/1025 2025-04-06
ittoia_s783A ukpga/2005/5/section/783A 2025-04-06
ittoia_s783AR ukpga/2005/5/section/783AR 2025-04-06
ittoia_s783B ukpga/2005/5/section/783B 2025-04-06
ittoia_s783BA ukpga/2005/5/section/783BA 2025-04-06
LIST
curl -sS -A "$UA" -o feed_uprating.xml -w "feed %{http_code}\n" "https://www.legislation.gov.uk/uksi/2025/data.feed?title=up-rating"
echo ALLDONE
