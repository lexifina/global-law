# Urssaf modele-social vs the statute: taxable pay of a cadre

Checked: modele-social 11.1.0 (mon-entreprise `8b2affafb5ebf65c0904876675fdb1fda3a29a23`; `VERSIONS.txt`), run with
publicodes in Node (`engine/driver.mjs`), against a reference computed from the statute (`scripts/law.py`) and a Lean
adapter (`lean/Ours.lean`), on 8,685 salary cases for 2025.

One genuine error, already reported upstream as
[betagouv/mon-entreprise#4320](https://github.com/betagouv/mon-entreprise/issues/4320): the employer's compulsory
cadre insurance contribution (1.50 % of pay up to the social security ceiling) is added to taxable pay in full,
although [CGI art. 83, 1° quater](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051765287) makes it
deductible within limits that the default cover never reaches: €706.50 a year too much taxable pay for every cadre at
or above the ceiling.

`lean/01-prevoyance-cadres-net-imposable.lean` proves the exact case by `decide` and, for every pay, that the engine
exceeds the law by 1.50 % of pay up to the ceiling. `engine/repro_4320.mjs` reproduces it; `engine/patch_4320.mjs`
applies the fix in memory and matches the statute reference on 1,278 cases. The method and every other difference
(all on our side's documented simplifications) are in `../fr-report.md`; `results/` has every case.
