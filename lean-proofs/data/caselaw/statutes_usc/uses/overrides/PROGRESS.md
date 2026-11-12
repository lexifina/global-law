# uses/overrides: congressional overrides of judicial decisions, found automatically

Goal: from the statute check (every US Code citation in decisions since 1995 against the Code's history), find the
decisions Congress answered by rewriting exactly the words the court read; score evidence; validate against published
override lists; Lean module `LegalProofs/USCaseLaw/Overrides.lean`. Status: DONE (2026-11-12). Draft text: BLOG.md.

## Results (results.json, recall.json, per_congress.tsv, confirmed.tsv)
- 1,931,153 citations; cited words rewritten since: 596,692; first rewrite by a law: 421,897 (edition: 174,795);
  first law within 10 years: 365,853 citations.
- Candidates (Lean, window 10 years, evidence): 6,069 decision-law pairs / 12,687 citations. By evidence: law names it
  30, committee report names it 279, quoted words struck (+ the law speaks of courts/decisions) 5,760. By court:
  Supreme Court 101, courts of appeals 2,392, district/specialised 3,201, state/territorial 375.
- Audit (agents, blind to stratum, audit/INSTRUCTIONS.md): law-named census 11/30 overrides (10 express; 6 codify;
  4 named a different case); report-named sample 8/40; quoted-words sample 5/45 (4/25 appeals+SC, 1/20 others);
  top 10 7/10, top 20 11/20, top 30 15/30; non-candidate baseline 0/20. Estimated overrides among candidates ~609
  (215-1,730 from Wilson intervals).
- Auditor calibration: 15 of 20 known (gold) overrides recognised; 2 of the 5 misses were packets showing the wrong
  cited block (make_audit shows the pair's first citation, not the one the law changed).
- Recall on gold (Christiansen & Eskridge 2014 + Hasen 2013; 36 overrides of 1995-2011 Supreme Court decisions by laws
  of 2011 or earlier): 20/36 found; 24 reachable by the record, 20/24. Misses: 3 no Code citation read (Schlup,
  Thompson v. Keohane, Jefferson Lines); 4 law changed none of the cited sections (Rasul: DTA credited to 109-163, not
  109-148; Graham County; Barnett Bank; Heintz); 5 not the first rewrite of the cited block (Santos, Nationsbank,
  Brockamp, Quackenbush, Buckhannon); 4 no evidence (Till, Murphy, Koon, Muscarello).
- Confirmed overrides: 34 (17 Supreme Court, 17 other); 15 on the gold list; 19 new: 15 lower-court, 2 after 2011
  (Nagarwala 2018 -> Pub. L. 116-309; US v. Wright 2011 -> Pub. L. 115-299, implicit), 2 Supreme Court not on the lists
  (Lorillard v. Reilly, implicit; Ashcroft v. Free Speech Coalition, constitutional).
- Figure: overrides.svg (arcs decision -> law for the 34 confirmed).

## Lean
- `LegalProofs/USCaseLaw/Overrides.lean`: firstRewrite, firstRewritingLaw, overrideCandidate (window in years on
  yyyymmdd days, evidence flag). Theorems: firstRewrite_spec, firstRewritingLaw_spec, candidate_law,
  candidate_amendedSince, candidate_rewrites, candidate_window_mono, candidate_evidence, firstRewritingLaw_unique,
  firstRewrite_first; #guard examples. No sorry.
- `LegalProofs/USCaseLaw/RunOverrides.lean`: runner. Not in the project build: the Overrides olean is compiled into
  `lean/olean/` (with copies of the 4 USCaseLaw dependency oleans) and run with that dir first on LEAN_PATH:
  `LEAN_PATH="<lean/olean>;$(lake env printenv LEAN_PATH)" lean --run LegalProofs/USCaseLaw/RunOverrides.lean lean/in.tsv 10 lean/out.tsv`
- Run: lean/run.log. Lean and candidates.py agree on the first rewriting law for all 421,897 citations.
- Not committed (per brief).

## Pipeline (scripts/)
1. `candidates.py` -> `cand_rows.tsv` (first rewrite of each cited block; law-made ones kept).
2. `fetch_plaw.py` (+ `_rev`) -> `cache/plaw/` (1,324 of 1,334 laws; 10 are pre-104th, no PLAW text).
3. `fetch_crpt.py` -> `cache/crpt/` (1,159 reports, 719 laws; govinfo answers missing pages with a 200 "Page Not
   Found", detected; multi-part reports: part 1 only, at pkg/<id>/html/<id>-pt1.htm).
4. `features.py` -> `feat/out_*.tsv` (decision-text evidence; S+A within 15 years, F+T within 10).
5. `score.py` -> `pairs.tsv`, `law_names.tsv`, `lean/in.tsv`, `score_summary.json`.
6. Lean run -> `lean/out.tsv`.
7. `recall.py` -> `recall.tsv`, `recall.json`.
8. `make_audit.py N|rest|G` -> `audit/in_*.json`, `audit/key_*.json`; verdicts `audit/out_*.json`.
9. `results.py` -> `results.json`, `per_congress.tsv`, `confirmed.tsv`, `overrides.tsv` (Lean's candidates, ranked,
   with evidence columns and audit labels).
10. `figure.py` -> `overrides.svg`.

## overrides.tsv columns
nid, decided, tier (S Supreme Court / A appeals / F district, bankruptcy, tax, claims / T state, territorial, tribal),
name, cite, law, law_day, title, gap (months), sections (cited blocks the law first rewrote), kind (evidence), score,
law_match / report_match (cite, name2 both parties, name1 one party), report (CRPT id), near_strong (override language
within 600 chars of the name in the law), law_strong (count of override phrases in the law), mentions, interp
(interpretive cues near the citations), qin / qstruck (quoted phrases found in the old words / gone from the new),
struck_hits (struck 5-word runs found in the decision), quote, repo, path, law_snip, report_snip, rids,
on_gold_list, audit_label, audit_why.

## Known weaknesses
- Block granularity: overrides that add a definition in another subsection or a new section are missed.
- Reports only from the law's own legislative-history note (no companion bills); part 1 only.
- Name matching: one-party matches (`name1`) are noisy; 4/30 law-named pairs were a different case.
- Quoted-words evidence is weak (~11%); "law speaks of courts" is law-wide, so omnibus laws always pass it.
- Audit by agents, small samples; packets show one citation per pair.
