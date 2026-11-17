#!/bin/bash
# usc_at.sh SECTION DATE : print 26 U.S.C. SECTION as in force on DATE (usc-history; commit dated by effective/enactment date)
cd ${USC_HISTORY:-$HOME/united-states-law}
c=$(git log -1 --format=%h --before="$2T23:59:59Z" -- title-26/$1.md)
echo "# commit $c $(git log -1 --format='%ad %s' --date=short $c | cut -c1-120)"
git show $c:title-26/$1.md
