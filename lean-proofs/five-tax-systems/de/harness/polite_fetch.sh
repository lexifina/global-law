#!/bin/bash
# polite_fetch.sh LISTFILE OUTDIR : fetch "name url" lines from bmf-steuerrechner.de, 65 s apart (robots.txt Crawl-Delay: 60)
LIST=$1; OUT=$2; mkdir -p $OUT
UA="Mozilla/5.0 (compatible; tax-model-test; non-commercial research)"
while read -r name url; do
  [ -z "$name" ] && continue
  if [ -s "$OUT/$name" ]; then continue; fi
  echo "$(date +%T) GET $url -> $name"
  curl -sSL -m 120 -A "$UA" -o "$OUT/$name" "$url"; echo "  status $? size $(stat -c %s $OUT/$name 2>/dev/null)"
  sleep 65
done < $LIST
echo DONE
