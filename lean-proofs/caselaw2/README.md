# US case law in Lean, version 2: precedent at the level of holdings

The second formalisation of the doctrine of precedent over the US case law of global-law (6,892,454 decisions in 152
case-law repositories). Version 1 ([../LegalProofs/USCaseLaw/](../LegalProofs/USCaseLaw), data in
[../data/caselaw/](../data/caselaw)) modelled the court hierarchy and whole-decision overruling. Version 2
([../LegalProofs/CaseLaw2/](../LegalProofs/CaseLaw2), Lean namespace `CaseLaw2`) works on holdings:

- **authority**: which decision binds which court on which day, from dated court epochs, successions, adoptions and
  per-system rules, each row with its source;
- **treatments and same-case history**: overruled, overruled in part, abrogated, disapproved, receded from, superseded by
  an enactment, reversed, vacated, read from the treating court's own words;
- **certificates**: a treatment is admitted only if Lean's checker finds the quoted words at the stated offset in the
  decision text, of the stated kind, naming the target, in a majority part, from a court with the power to do it;
- **status**: good law per holding, per date, per line of courts; **splits** between circuits; a Horty-style
  consistency check of factor-based holdings; and **findings** (a decision that relies on negated law, a panel that
  departs from its circuit without sitting en banc, and so on).

Write-up (forthcoming): <https://lexifina.com/blog/formalizing-all-us-case-law-in-lean>. The built report with every
table and figure is [report/caselaw-lean-2.html](report/caselaw-lean-2.html).

## Results

After four rounds (12 November 2026; [ROUND2.md](ROUND2.md), [ROUND3.md](ROUND3.md), [ROUND4.md](ROUND4.md)); the
scores are in [../data/caselaw2/eval/score_final.txt](../data/caselaw2/eval/score_final.txt).

| Measure | Result |
|---|---|
| Treatment rows read / admitted by a passing certificate | 35,365 / 25,035 |
| Same-case history rows | 54,940 |
| Holdings | 260,349 |
| Status rows / certificates checked | 495,891 / 350,654 |
| Supreme Court Database, decisions flagged as altering precedent: found | 141 of 278 (50.7%) |
| Supreme Court on Supreme Court overrulings admitted that the database flags | 141 of 152 (92.8%) |
| Constitution Annotated table of overruled decisions, current edition: found | 162 of 292 resolved pairs (55.5%) |
| Constitution Annotated 2016, express overrulings: found | 135 of 243 (55.6%) |
| Later courts' notes that name an overruling decision: Lean agrees | 5,401 of 15,768 (34.3%) |
| Admitted "overruled" rows confirmed, among those a later court noted | 4,158 of 5,099 (81.5%) |
| Circuit splits later resolved by the Supreme Court (statutory): found at section level | 171 of 714 (23.9%) |
| Findings: decisions at risk / citing an overruled decision / panel departs without en banc | 86,228 / 50,742 / 573 |
| Theorems, each statement locked | 141 (4 use no axioms; the rest only `propext`, `Classical.choice`, `Quot.sound`) |
| Mutants killed by the properties | 27 of 27 |
| Lean runner against the independent Python reference, real data | 0 disagreements (status 398,482 rows, findings 168,276, certificates 350,651) |
| The same, 500 generated universes and 118 regression universes | 0 disagreements |

Recall is the weak side and precision the strong one: the reader keeps only what a court says in its own
present-tense words, and about half of the known Supreme Court overrulings are stated that way in a text the corpus
holds. [report/sections/why_recall.html](report/sections/why_recall.html) and [LIMITS.md](LIMITS.md) say where the
rest goes.

## Rounds 5 to 13 (13–14 November 2026)

Each round adds rules to the model and the reader, under one protocol (`benchmarks/CONTRACT.md`):
- rules are built on the development half of every answer key only;
- a rule enters the certified tier only after a blind audit at 0.90 or better;
- each build is frozen (file hashes in the round's `FREEZE.md`) before the sealed halves are scored, once
  (`SEALED_LOG.md`).

Every round's notes, scripts, audits, agent briefs and scores are in `round5/` to `round13/`. Each round's
`ROUNDn.md` is its summary (round 6's is `round6/shepardized/SHEPARDIZED.md`).

| Round | What it added |
|---|---|
| 5 | Overrulings recognised by a later court with power (`Spec/Recognised.lean`), operative words, the first fresh held-out lists |
| 6 | Same-case history, the Shepardized Courts of Appeals key |
| 7 | Joined certificates, a stronger reader, queued reading, scope, dates |
| 8 | The own-act queue, links through later citations, rehearing, multi-case acts, state courts, new keys |
| 9 | Shadow Docket remand links, FJC anchors, part zones in Lean, state joins, two fresh held-out keys |
| 10 | A state-court review linker, the remand and trial-judgment bridges in Lean, the Federal Circuit key |
| 11 | Supreme Court order lists as staged data, state review of uncited decisions below, a Federal Circuit tribunal linker |
| 12 | Shadow Docket order nodes, en banc, Federal Circuit district targets, a third Brace & Hall tie |
| 13 | The Shadow Docket leftover rules, and three held classes installed below the audit bar (marked as such) |

The frozen round-13 build is `v13a`. It has 305 theorems with locked statements (`audit/statements.lock`) and 89
deliberately broken versions, each caught by the properties. It shows 0 disagreements with the Python reference in
every table (status 532,639 rows, findings 329,990, certificates 498,507). Its outputs are in
[../data/caselaw2/out_v13a/](../data/caselaw2/out_v13a/).

**Recall and precision on the sealed half of each blind answer key, v13a:**

| Answer key | Recall | Precision |
|---|---|---|
| Supreme Court Database: reversed or vacated below | 76.5% | 97.2% |
| Shadow Docket Database: vacated or summarily reversed | 68.3% | 94.6% |
| FJC Integrated Database, unpublished appeals | 64.1% | 94.8% |
| FJC Integrated Database, district decisions reversed or vacated | 57.0% | 89.4% |
| Brace & Hall, state supreme courts | 56.8% | 93.6% |
| Federal Circuit Dataset Project | 56.0% | 90.3% |
| Beim, Hirsch & Kastellec, en banc rehearings | 52.9% | – |
| Shepardized Courts of Appeals | 52.0% (131 of 252) | 92.9% |
| Songer Courts of Appeals | 44.3% | 97.1% |
| Unopened overruling lists | 60.6% | 75% |
| Overruling notes from courts without power (held out) | 37.8% | 93.5% |
| Pre-1930 tables of overruled state cases | 7.7% | – |

Each key's source, licence, linking and scorer are in `benchmarks/<key>/` (`SOURCE.md`, `MAPPING.md`,
`DISAGREEMENTS.md`). The scores of every build are in `benchmarks/graph/rows.tsv`, and the figure is
`benchmarks/graph/benchmarks.png`. The keys' own rows are not copied here: download them from the sources named in
each `SOURCE.md`. Only our linking summaries, errors we found in the sources, and the scores are published. For the
Supreme Court Database (CC BY-NC) and the Songer data, only identifiers, aggregates and scores are included, and the
SCDB coding columns are blank. Lindquist's state supreme court data sits behind a click-through agreement and was not
used. Audit packets quote court opinions, which are public domain. The opinion texts given to the readers are not
kept here: they are rebuilt from the corpus.

## What the proofs do and do not show

[TRUST.md](TRUST.md) is the full inventory: what is proved by the kernel, what is computed by compiled code, what is
certified row by row, what is only tested, and what is assumed. In short: the theorems are about the model; the
doctrine tables and the reader's rows are data; every departure from the doctrine notes is listed in
[DEVIATIONS.md](DEVIATIONS.md); no `sorry`, `axiom` or `native_decide` anywhere.

## Build and run

Lean 4.35.0, core library only (the toolchain is pinned in `../lean-toolchain`).

```sh
cd lean-proofs
lake build LegalProofs.CaseLaw2 LegalProofs.USCaseLaw   # model, proofs, 223 #guard checks, mutation matrix, statement lock
python3 caselaw2/audit/audit.py check                    # 305 theorems (round 13); 0 statement changes; 0 problems
cd caselaw2
bash run_lean.sh 2 fixtures/data fixtures/edges /tmp/fx  # the runner on the fixtures (compare with fixtures/out; summary.tsv also carries timings)
python3 ../tools/caselaw2/ref/precedent_ref.py run --data fixtures/data --edges fixtures/edges --out /tmp/fxref
python3 ../tools/caselaw2/ref/diff.py /tmp/fx /tmp/fxref --info   # Lean against the Python reference
```

`LegalProofs.CaseLaw2` is its own build target; the default `lake build` does not include it.

**Windows.** Where Windows Application Control blocks `lean.exe`, `lake.exe` or the compiled runner, build and run
under Linux Lean in WSL: install elan in the distribution
(`curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.35.0`),
copy `lean-proofs/` into the Linux file system and run the commands above there. Every result here was produced that
way. `run_lean_wsl.sh` and `wsl/` are the helpers used during the work; they are kept as run and expect the working
layout of the time (a `us-caselaw-lean-work/caselaw-lean-2` folder beside the clone), so read them as a record.

## Where things are

| Path (from `lean-proofs/`) | Contents |
|---|---|
| `LegalProofs/CaseLaw2.lean`, `LegalProofs/CaseLaw2/` | the Lean: types, `Spec/` (authority, status, splits, lines, Horty, findings), certificates, the executable refinement (`Exec/`), runner (`Run`), examples, mutants, `Hunt`, and the generated `Registry`, `Audit`, `CueTable`. Module map in [LEAN.md](LEAN.md) |
| `LegalProofs/USCaseLaw/` | version 1, the statute text model and the statute uses |
| `caselaw2/` (here) | [DESIGN.md](DESIGN.md), [SCHEMA.md](SCHEMA.md) (the tables the runner reads), [LEAN.md](LEAN.md), [TRUST.md](TRUST.md), [DEVIATIONS.md](DEVIATIONS.md), [DIFFTEST.md](DIFFTEST.md), [FUZZ.md](FUZZ.md), [FUZZ_BUGS.md](FUZZ_BUGS.md), [LIMITS.md](LIMITS.md), the round logs, [STATEMENTS.log](STATEMENTS.log) |
| `caselaw2/research/` | the doctrine notes the model was written from, prior art, other formalisms, the data audit |
| `caselaw2/audit/` | `audit.py` (statement lock and axiom check), `statements.lock` |
| `caselaw2/runner/` | the lake package that compiles the runner natively; `run_lean.sh` drives it in shards |
| `caselaw2/fixtures/` | a small universe with expected Lean and reference outputs; `regress.tar.gz` holds the 118 regression universes (`tar -xzf`) |
| `caselaw2/difftest/` | summaries of the differential runs (the full outputs are not kept) |
| `caselaw2/report/` | `make_report.py`, the heatmaps (PNG and SVG) with their series, the v1/v2 declaration map, and the built report |
| `tools/caselaw2/` | `scan.py`, `reader/` (treatments and history), `holdings/` (holdings, issues, splits), `factors/`, `statutes/` (law changes and supersessions), courts and decisions builders, `ref/` (the Python reference, generator and differ), `fuzz/`, `eval/` (gold and scoring), `hunt/` |
| `tools/CaseLawAnatomy.lean`, `tools/LawAnatomy.lean`, `tools/caselaw/` | declaration maps; the version 1 tools |
| `data/caselaw2/` | the tables, Lean outputs, scores, gold, hunt results and audits: see its [README](../data/caselaw2/README.md) |
| `video/caselaw2_film*.html`, `video/render_caselaw2.py`, `video/caselaw2_data.json` | the film sources (no rendered video) |

## What is not in the repository

The bulk inputs are too large for git and are rebuilt from the per-court case-law repositories of global-law
(`united-states/…` case-law submodules; decisions from the Caselaw Access Project and CourtListener, public domain):

| Not here | Size | Rebuilt by |
|---|---|---|
| `decisions2.tsv` (one row per decision) | 915 MB | `tools/caselaw/extract.py`, `graph.py` (version 1 graph), then `tools/caselaw2/decisions_build.py` |
| citation edges (`edges-*.tsv`), node list | 48 million edges | `tools/caselaw/graph.py`, `encode.py` |
| `cert_text.tsv`, `holdings_cert_text.tsv`, `window_sha.tsv` (the quoted windows and their hashes) | 83 MB, 278 MB, 34 MB | `tools/caselaw2/reader/`, `holdings/`, `window_sha.py` |
| candidate scans, model inputs and outputs, caches, snapshots | several GB | `tools/caselaw2/scan.py`, `reader/`, `holdings/`, `hunt/` |
| rendered films | | `python video/render_caselaw2.py` |

The first 200 rows of the three large tables and their row counts are in `data/caselaw2/tables/`. The model-reading
steps call an Azure OpenAI deployment; the endpoint and key are read from the environment only
(`AGENTIC_AZURE_OPENAI_ENDPOINT`, `AGENTIC_AZURE_OPENAI_API_KEY`). Many scripts address the working folder as
`~/Documents/us-caselaw-lean-work/`; set that up, or change the constant at the top of the script.

Third-party material is not copied where its licence does not allow it: see
[../data/caselaw2/gold/README.md](../data/caselaw2/gold/README.md) (Supreme Court Database, CC BY-NC; law-review
appendices).
