# Formalizing the US tax code: progress

Resumable tracker. Data (not in git): `C:\Users\alany\Documents\tax-formalization-data` (OLRC release point 119-138,
all titles; `out/t26.json`, `out/ids.tsv`). Run heavy steps at below-normal priority (`cmd //c "start "" /belownormal /b /wait ..."`);
keep C: above 50 GB free (resources-used session).

## Layer 1: drafting checks over all of Title 26 (no AI)

- [x] Download release point 119-138 (Title 26 + all titles)
- [x] `tools/taxcode/parse_uslm.py` → `t26.json` (58,929 provisions; 35,864 references: hyperlinks, words, section citations), `ids.tsv` (781,852 identifiers, all titles)
- [x] Checker runs via `lake env lean --run TaxCode/Main.lean` (the compiled exe is blocked by Windows Application Control): 389 findings in 9 classes, 39 s
- [x] Triage: 3 rounds of 40-item samples; dangling word refs ~55–65% precise; duplicate designations, wrong level words, broken links, unbalanced parentheses high. Recall vs OLRC footnotes: parentheses 13/13, References in Text 35/79 (misses mostly refs whose target exists but changed meaning). `tools/taxcode/report.py` → findings.csv, summary.json
- [ ] Certificates: kernel-checked restatement of each confirmed finding (TaxCode/Certs)
- [ ] Baseline + diff: a release point before Pub. L. 119-21 (OLRC prior release points page not found; probing got a 403 — stopped; asked resources-used for a local copy)

## Layer 2: the individual income tax, tax year 2025 (copy / test / prove / check)

Interface: `TaxCode/Individual/Household.lean`. One file per provision group.

| Group | Provisions | Status |
|---|---|---|
| A income & AGI | §§61, 86, 62, 219, 221, 223, 164(f), 1401–1402, 3101(b)(2), 1411 | todo |
| B deductions | §§63, 151(f), 164(b)(6)–(7), 163(h), 170, 213, 199A, 224, 225, 163(h)(4) | todo |
| C tax | §1(j) schedules, §1(h) capital gains, §55–59 AMT | todo |
| D credits | §§21, 24, 25A, 25B, 32, 36B | todo |
| E assemble | Form 1040 order; IRS worked examples | todo |

## Layer 3 (after completion): differential testing

- PolicyEngine-US, Tax-Calculator (PSL), NBER TAXSIM; plus IRS tax tables, EIC table, publication examples.
