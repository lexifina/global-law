#!/bin/bash
# usage: probe.sh YEAR "1AJ=30000,0AC=1" [VARS...]   -> prints M and Lean values
Y=$1; B=$2; shift 2; VARS=${@:-NBPT RNG RNI IDRS2 IDEC ITRED CITOT IRN REVKIRE}
D=$(mktemp -d); { echo "#NOM"; echo PROBE; echo "#ENTREES-PRIMITIF"; echo "REGCO/1"; echo "ANREV/$Y"; echo "$B" | tr ',' '\n' | sed 's#=#/#'; printf "#CONTROLES-PRIMITIF\n#RESULTATS-PRIMITIF\n#ENTREES-CORRECTIF\n#CONTROLES-CORRECTIF\n#RESULTATS-CORRECTIF\n##\n"; } > $D/p.irj
mkdir $D/o; ~/fr/bin/cal$Y -completion -m p -a $Y -dst $D/o $D/p.irj | grep "KO" ; 
echo -n "M   : "; for v in $VARS; do printf "%s=%s " $v "$(grep -m1 "^$v/" $D/o/p.irj 2>/dev/null | cut -d/ -f2 | sed 's/\.00*$//')"; done; echo
echo -n "Lean: "; echo "p;$Y;$B" | ~/fr/lean/.lake/build/bin/frtax | cut -d';' -f2- ; rm -rf $D
