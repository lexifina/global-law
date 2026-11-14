# Behavioural test (round 5 Test 4) — folded results

Scorer `round5/tests/behaviour.py`, docs `round5/tests/TESTS.md` ("Test 4: behavioural test, no labels"). Re-runnable
by design (not sealed), so re-run on round4 and round6. Dataset `behaviour`, split `all`, tests `overruling`, court
`mixed`, `blind: true` (no list of overrulings is used; the `bound` series is label-free).

**Metrics are not k/n proportions.** Each `did_<class>_k<5|10>[_clean]` is
`{value, lo, hi, n, kind: "did_ratio", index_did, index_lo, index_hi, share_of_explicit, share_lo, share_hi}`:
DiD = (post/pre bound-citation rate of event decisions) / (same for matched controls), bootstrap 95% over event
decisions (1,000 draws, seed 5), n = event decisions used; 1 = no drop. `_clean` = boundClean series. Primary
`did_explicit_k10` (self-announced whole-decision overrulings, TESTS.md's calibration row); each class has a
`did_placebo_*` (should be ~1). Because the entries carry no `k`/`p`, `benchmarks/graph/make_graph.py` draws no dot
for this row (checked: it runs, 9 rows, on `--bench benchmarks/existing`).

## Commands (run by `../run_existing.py --only behaviour`)

```
python benchmarks/existing/_r5tests/behaviour.py --status <OUT>/status.tsv --label <label> --data <DATA> --classes <R>/round5/classes_r5.tsv --out <R>/benchmarks/existing/behaviour/runs/<label>
```

`_r5tests/behaviour.py` is byte-identical to the original (981198e6a741fb67889f63b016dd77a435f40b17); only the
imported `common.py` copy differs (cache dir, see `../holdout_notes/RUN.md`). `--classes round5/classes_r5.tsv`
(sha1 1df407cb2d93b646508d7a54d3e7ba11c90f4fb0) is the class file `round5/score_all.sh` used; on round 4 its
round-5 rules match nothing, so the classes are the defaults.

| file | round4 | round6 |
|---|---|---|
| out/status.tsv | ece2365efc536dfcb39425e8c95efe842c57e3a6 | 96888c8b4381d3230e83d90c5d6f2fa45dfeeb8e |
| out/findings.tsv | 67a8b8a8e4a8358bca347c70ac65bad1907f3b95 | f007ad4c0c499fc248caf44fc19552027f29ca9f |
| data/decisions2.tsv | fd54596734f12a9fd3a739c55a82102f3c49213c | same file |
| graph/edges.bin | d96c93045ff9fc25294657d6f8cdae72b5de164c | same |
| gold/reports_typed.tsv | f2a49e55811ecb03e2584b5390dc4f6fdbf67ddf | same |

**Agreement with earlier logs.** round4: `behaviour_round4.tsv` equals `round5/tests/results/behaviour_baseline-round4.tsv`
in every column except the label.

## Headline, k = 10, bound (DiD, 95%; n = decisions used)

| class | round4 | round6 | round7 |
|---|---|---|---|
| explicit | 0.609 (0.544–0.685), n 1,676 | 0.655 (0.584–0.734), n 1,482 | 0.611 (0.541–0.694), n 1,526 |
| placebo explicit | 0.968 (0.880–1.063) | 1.042 (0.917–1.198) | 0.989 (0.869–1.156) |
| partly | 0.587 (0.472–0.687), n 6,087 | 0.637 (0.605–0.671), n 5,501 | 0.640 (0.611–0.670), n 5,668 |
| implicit | 0.894 (0.641–1.300), n 88 | 1.101 (0.660–1.646), n 47 | 1.012 (0.596–1.645), n 47 |
| recognised (round 5) | – | 0.775 (0.495–0.907), n 205 | 0.763 (0.485–0.901), n 209 |
| partlyRecognised | – | 0.841 (0.757–0.935), n 952 | 0.808 (0.735–0.878), n 1,050 |
| placebo partlyRecognised | – | 1.148 (1.039–1.275) | 1.026 (0.936–1.127) |
| operativeWords | – | 0.609 (0.358–0.875), n 181 | 0.582 (0.331–0.848), n 181 |
| partlyOperative | – | 0.783 (0.663–0.918), n 450 | 0.812 (0.719–0.903), n 744 |

round7 inputs: out/status.tsv 25972da2762435840f6ed51dbf83ec7c286984ce, out/findings.tsv
e168e894ca7bf46edbf5aa590208eacaa86f603b, data/decisions2.tsv fd54596734f12a9fd3a739c55a82102f3c49213c (same file),
edges/notes as above (`runs/round7/inputs.json`). Same-case history statuses (round 6's main addition) have no class
in this test and are left out (listed in the run's `.txt`).

## Round-6 placebo for partlyRecognised (1.148, 1.039–1.275): checked 2026-11-14, not a scorer bug

Verdict: sampling noise in a single-pick, citation-weighted placebo; not a bug, and not an effect of recognised
overrulings. The scorer copy is unchanged (byte-identical to the original); round4/round6 runs re-run and identical.

- The placebo uses no citations of the event decisions after the event: pseudo event = one control, against the
  other controls of the same event decision, all on the event decision's date, same court and +-2 years. So
  "recognised because heavily cited" cannot enter it. Class coverage is fine (round7: 3,152 partlyRecognised events).
- Which control is the pseudo event decides the value (round 6, k 10, bound, same data): nearest (as coded) 1.148;
  farthest 0.934; a random pick averaged over 200 draws 1.005 (2.5–97.5% of draws 0.911–1.116). Round 7 with the
  same nearest rule: 1.026 (0.936–1.127). Nearest vs random over six classes is mixed (round 7: explicit 0.989 vs
  1.001, partly 0.966 vs 1.003, partlyRecognised 1.026 vs 0.994), so the nearest rule is not systematically biased.
- Concentration: on round 6 the top 5 of 861 pseudo units hold 14.0% of post-event citations but 3.6% of pre-event
  (e.g. a control going 83 -> 361 bound citations, another 15 -> 104). Dropping the top 1/3/5/10 gives 1.133 /
  1.081 / 1.069 / 1.015. The bounded index DiD of the same placebo is -0.004 (-0.040 to 0.032).
- Tried and rejected (both left the scorer as it was): (a) picking the pseudo event by a hash instead of nearest:
  round6 1.043 (0.931–1.161) but round7 1.115 (1.008–1.238), round7 placebo recognised 0.820 (0.716–0.945) -- only
  moves which class lands in the tail; main rows unchanged. (b) a caliper on the 5-year bound count too: round6
  placebo partlyRecognised 1.095 (0.974–1.232), explicit placebo 1.067; main partlyRecognised 0.785 (0.697–0.877),
  explicit 0.646 (0.567–0.739) -- the class's drop does not depend on it.
- Reading: a placebo interval of a pooled, heavily-weighted ratio excludes 1 now and then across ~7 classes x 3
  builds; read partlyRecognised against its index DiD and the round7 placebo, not the round6 pooled placebo alone.
