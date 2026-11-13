#!/bin/sh
# Re-run every demo of the watch (from uses/watch). Takes a few seconds each.
W="$(cd "$(dirname "$0")/../.." && pwd)/usc_watch.py"
python $W --doc demo_opinion/texas-v-united-states-809-F3d-134.md --today 2026-11-12 --json demo_opinion/watch.json --html demo_opinion/watch.html --title "What has changed under Texas v. United States, 809 F.3d 134 (5th Cir. 2015)" > demo_opinion/watch.txt
python $W --list lists/firearms_sentencing.txt --since 2015-01-01 --today 2026-11-12 --json demo_practice/firearms.json --html demo_practice/firearms.html --title "Firearms and drug sentencing watch list, since 2015" > demo_practice/firearms.txt
python $W --list lists/bankruptcy.txt --since 2015-01-01 --today 2026-11-12 --json demo_practice/bankruptcy.json --html demo_practice/bankruptcy.html --title "Bankruptcy watch list, since 2015" > demo_practice/bankruptcy.txt
python $W --list lists/top25.txt --digest 2025-11-04 2026-11-03 --json demo_top25/digest.json --html demo_top25/digest.html --title "The 25 sections courts cite most: every law change, 2025-11-04 to 2026-11-03" > demo_top25/digest.txt
python $W --list lists/top100.txt --digest 2025-11-04 2026-11-03 --json demo_top25/digest_top100.json --html demo_top25/digest_top100.html --title "The 100 sections courts cite most: every law change, 2025-11-04 to 2026-11-03" > demo_top25/digest_top100.txt
