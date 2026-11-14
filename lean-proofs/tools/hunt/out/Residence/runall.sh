cd ~/Documents/global-law-lean/lean-proofs
run(){ python -I tools/hunt/out/Residence/gen.py $1 && (timeout 240 lake env lean tools/hunt/out/Residence/$1.lean > tools/hunt/out/Residence/$1.txt 2>&1; echo "$1 exit $?"); }
for batch in "$@"; do
  for k in $(echo $batch | tr ',' ' '); do ( run $k ) & done
  wait
done
