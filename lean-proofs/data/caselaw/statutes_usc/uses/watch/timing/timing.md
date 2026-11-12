# Timing (2026-11-12, this machine, 24 logical CPUs; one Python process and one Lean process per watch)

Watch list: the 100 sections courts cite most (lists/top100.txt, whole sections), since 2015-01-01, read 2026-11-12.
169 versions in the window (106 by law, 63 by edition); 55 items alert.

| run | load versions.tsv | read + encode | Lean (one `lake env lean --run`, incl. start-up) | diffs + report | total |
|---|---|---|---|---|---|
| 1 | 0.58 s | 0.59 s | 1.68 s | 3.29 s | 6.14 s |
| 2 | 0.54 s | 0.49 s | 1.02 s | 1.63 s | 3.69 s |
| 3 | 0.30 s | 0.47 s | 0.92 s | 1.59 s | 3.29 s |

- The same list over the last 12 months of the record (since 2025-11-03): 1.54 s in all, Lean 0.88 s.
- The 1,000 sections courts cite most, since 2015-01-01: 16.7 s in all, Lean 0.88 s; 529 alerts, 1,122 alerting law
  versions from 214 laws.
- Before two fixes the same 100-section watch took 50-69 s (timing/old_worddiff/): the word diff ran on whole
  sections (now lines first, then words), and usc_encode.norm's str.translate was slow on long sections (now
  str.replace, same output, checked on 42 U.S.C. 1396a).
- Check of the "no alert" theorem on real data: in every run (1,000 sections, 100 sections, the three demos) no item
  has no alert, no edition notice, and different words. Every history Lean saw was in date order.
