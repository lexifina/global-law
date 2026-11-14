# usage: mk.sh name 'scenario expr'   (run from lean-proofs/)
D=tools/hunt/out/Instruments
cat $D/core.lean $D/scen.lean > $D/run_$1.lean
echo "#eval search (top := ${3:-5}) ($2)" >> $D/run_$1.lean
echo "end Legal.USTax.Hunt.Instruments" >> $D/run_$1.lean
timeout 400 lake env lean $D/run_$1.lean > $D/out_$1.txt 2>&1
