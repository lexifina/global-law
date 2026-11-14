# Formalizing the US tax code: progress

Resumable tracker. Data (not in git): `~\Documents\tax-formalization-data` (OLRC release point 119-138,
all titles; `out/t26.json`, `out/ids.tsv`). Run heavy steps at below-normal priority (`cmd //c "start "" /belownormal /b /wait ..."`);
keep C: above 50 GB free (resources-used session).

## Layer 1: drafting checks over all of Title 26 (no AI)

- [x] Download release point 119-138 (Title 26 + all titles)
- [x] `tools/taxcode/parse_uslm.py` → `t26.json` (58,929 provisions; 35,864 references: hyperlinks, words, section citations), `ids.tsv` (781,852 identifiers, all titles)
- [x] Checker runs via `lake env lean --run TaxCode/Main.lean` (the compiled exe is blocked by Windows Application Control): 389 findings in 9 classes, 39 s
- [x] Triage: 3 rounds of 40-item samples; dangling word refs ~55–65% precise; duplicate designations, wrong level words, broken links, unbalanced parentheses high. Recall vs OLRC footnotes: parentheses 13/13, References in Text 35/79 (misses mostly refs whose target exists but changed meaning). `tools/taxcode/report.py` → findings.csv, summary.json
- [ ] Certificates: kernel-checked restatement of each confirmed finding (TaxCode/Certs)
- [ ] Baseline + diff: a release point before Pub. L. 119-21 (OLRC prior release points page not found; probing got a 403 — stopped; asked resources-used for a local copy)

## Layer 2: the individual income tax, tax year 2025 (copy / test / prove / check) — done

Interface: `TaxCode/Individual/Household.lean`. Assembly: `Form1040.lean` (§63(e) election computed both ways);
batch runner `Run.lean` (`lake env lean --run TaxCode/Individual/Run.lean households.json results.json`).

| Group | Provisions | Theorems | Status |
|---|---|---|---|
| A income & AGI | §§61, 86, 62, 219, 221, 223, 164(f), 1401–1402, 3101(b)(2), 1411 | 104 | done, reviewed |
| B deductions | §§63, 151(d)(5)(C), 164(b)(6)–(7), 163(h), 170, 213, 199A, 224, 225 | 133 | done, reviewed |
| C tax | §1(j) schedules, §3 Table, §1(h), §§55–56 AMT | 59 | done, reviewed (AMT gain band fixed) |
| D credits | §§21, 24, 25A, 25B, 32, 36B | 74 | done, reviewed (§36B(c)(1)(C)/(D) fixed) |

Findings: `Individual/{A,B,C,D}/FINDINGS.md` (each with the independent review appended).

## Layer 3: differential testing — done

`tools/taxcode/diff/` (results in `RESULTS.md`): 2,000 common + 3,000 hard households against PolicyEngine-US 2.116.9,
Tax-Calculator 6.8.5 (exact calculations) and UsTaxes 49cd0f2 (runner `run_ustaxes.ts`, built under
`tax-formalization-data/ustaxes-runner`). Lean vs PolicyEngine: 7 disagreements in 5,000, all the EIC table. TC: MFS
EITC/CDCC lived-apart rule, one MFS AMT case, itemizing ties. UsTaxes: 14 bugs with file:line.
TAXSIM-35 stops at 2023; OpenTaxSolver 2025 download refuses automation (not bypassed).

## Write-up — done

`~/Documents/html-reports/formalizing-the-us-tax-code.html`.

## Open

- Layer 1 certificates (kernel-checked restatements of confirmed findings) — optional.
- Layer 1 baseline from a pre-119-21 release point (OLRC prior release points refused automated access).
- Nothing pushed: global-law is public; ask before pushing.
