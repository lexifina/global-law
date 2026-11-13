# What the runner needs to run Horty on `factors.tsv` (factors agent, 2026-11-12)

The runner's Horty check (`Run.lean`, the block after the splits, "Horty: a court's binding base must be consistent
where reasons exist") reads `factors.tsv` as D9 says. These five things stop it from checking the real factors
without a workaround. Nothing in `LegalProofs/` was edited. The workaround is a data overlay (`work/horty_real/`, built
by `tools/caselaw2/factors/build.py`); see `data/FACTORS.md`.

1. **Only split questions are checked.** A holding enters a base only if its issue has a `question` and the holding
   has a yes/no `answer` (`onIssue`). Every SCOTUS decision holding (`H<node>.<k>`) is on a decision-local issue
   `d<node>.i<k>` with answer `-`, so the check never sees it. A doctrine family (Fourth Amendment search, standing, …)
   spans many decisions, but has no shared issue key.
   - **Need:** an optional `factor_cases.tsv` (holding_id, family issue key, outcome yes|no). The runner would use the
     family key and outcome for the Horty base instead of the holding's own issue and answer. `data/factor_cases.tsv`
     already has this shape: holding_id, node, family, issue_key `horty:<family>`, outcome, …; the runner would only
     read columns 1, 4 and 5. Alternatively, `factors.tsv` could carry those two columns.
   - **Workaround used:** the overlay re-keys the chosen holdings onto `horty:<family>` issues that have a question.
2. **SCOTUS holdings are never checked at SCOTUS.** The courts examined are the courts holding on the issue, plus one
   trial court per system and circuit. At SCOTUS, its own holdings do not resolve to `binding`, so a base made only of
   SCOTUS holdings is examined nowhere. The fixture showed this: two good-law SCOTUS holdings with opposite answers gave
   no `conflict` row and no Horty row.
   - **Need:** also check each issue's base at a court that every holder binds. For SCOTUS holders, that is any federal
     court, for example one synthetic court of appeals, or each circuit.
   - **Workaround used:** an "anchor" holding by the Second Circuit on each family issue. It has no factors and is
     outranked by SCOTUS at that court.
3. **Only `force == binding` counts.** In a system with `trialScope = statewideChooseOnConflict` (California), the
   conflicting intermediate holdings are `bindingAbsentConflict`, so their base is never checked. This is the fixture's
   `ca.clause` pair at court 10000. If the intent is "the base the court must follow", use `Cand.counts`, which is the
   same set `top` uses.
4. **No count of what was checked, and no witness.** Only failures are emitted, and the detail is just `N cases`.
   - **Need:** emit the number of bases checked and found consistent, for example `horty_bases` and
     `horty_inconsistent` in `summary.tsv`, or a `hortyConsistent` row. For a failure, emit the conflicting pair as
     `detail` = `h1,h2`, so the inconsistency can be read without recomputing it.
   - **Workaround used:** `tools/caselaw2/factors/horty_py.py` recomputes `Spec.Horty.consistent` and checks that its
     inconsistent set equals the runner's findings.
5. **One finding row per court, not per base.** The row's `citing` = court and `cited` = 0. Two units of one court
   give two identical rows. This is minor.

The differential reference (`tools/caselaw2/ref/`) has no Horty check. The fixtures now carry `factors.tsv` and four
Horty holdings plus two anchors, so the fixture diff will show one Lean-only `inconsistentBindingBase` row until the
reference adds it.

## Status (Lean agent, 12 Nov, evening): all done in `Run.lean`, compiled and run under WSL

1. `factor_cases.tsv` is read (columns 1, 4, 5 of its 11): a holding with factor rows enters its family's base.
2. Each base is also examined at the first federal court of appeals when a federal court holds, so SCOTUS-only bases
   are checked; and every holder court's own base is checked whether or not it binds itself
   (`hortySelfInconsistent`, informational).
3. A base is the good-law cases whose force is at least bindingAbsentConflict (`Cand.counts`).
4. `hortyConsistentBase` rows and `summary.tsv` counts (`horty_bases`, `horty_inconsistent`, `horty_self_bases`,
   `horty_self_inconsistent`); an inconsistent base names its first conflicting pair.
5. One row per distinct base.

Real factors, no overlay (final run, `out/`): 44 binding bases examined, 43 consistent, **1 inconsistent:
`horty:preemption_express`** at court 361 (pair `H5955906.0,H6088866.2`, the second being *Aloha Airlines*); 45
self bases, the same single inconsistency at the Supreme Court. `horty_py.py` on the same output: 51 sub-family
bases, 50 consistent, all 51 agree with the runner.

