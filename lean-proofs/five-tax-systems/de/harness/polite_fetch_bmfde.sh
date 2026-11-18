#!/bin/bash
# polite_fetch_bmfde.sh LISTFILE OUTDIR : fetch "name url" lines from bundesfinanzministerium.de, 185 s apart (robots.txt Crawl-delay: 180)
LIST=$1; OUT=$2; mkdir -p $OUT
UA="Mozilla/5.0 (compatible; tax-model-test; non-commercial research)"
sleep 5
while read -r name url; do
  [ -z "$name" ] && continue
  if [ -s "$OUT/$name" ]; then continue; fi
  echo "$(date +%T) GET $url -> $name"
  curl -sSL -m 180 -A "$UA" -o "$OUT/$name" "$url"; echo "  status $? size $(stat -c %s $OUT/$name 2>/dev/null)"
  sleep 185
done < $LIST
echo DONE
