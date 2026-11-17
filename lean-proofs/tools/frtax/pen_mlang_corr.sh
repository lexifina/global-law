#!/bin/bash
# Penalty study: run one IRJ file (with #ENTREES-RAPPELS) through the Mlang interpreter in correctif mode.
# Usage: harness/pen_mlang_corr.sh YEAR FILE.irj
Y=$1; F=$(readlink -f $2)
cd ~/fr/mlang; eval $(opam env --switch=. --set-switch) 2>/dev/null
SRC=$(make -s -n test_file YEAR=$Y MODE=corr TEST_FILE=X 2>/dev/null | grep -- '--run_test=X' | sed 's/.*--run_test=X //')
exec ./_build/install/default/bin/mlang -A iliad --precision double --income-year=$Y --comparison_error_margin=0.000001 \
  --mpp_function=enchainement_primitif_interpreteur --run_test=$F $SRC
