# Official calculators checked against the statute

Open-source government code that computes tax, checked against independent models of the statute written in Lean.
Every difference was traced to the text of the law; where the code is wrong, it was reported to its maintainers.

| Folder | Code checked | Law | Finding |
|---|---|---|---|
| [`gov-uk-child-benefit`](gov-uk-child-benefit) | GOV.UK's Child Benefit tax calculator ([alphagov/smart-answers](https://github.com/alphagov/smart-answers)) | [ITEPA 2003 s. 681C](https://www.legislation.gov.uk/ukpga/2003/1/section/681C) | two rounding differences: 28 % instead of 29 % at £65,800 (floating point); the total not rounded down to whole pounds first |
| [`hmrc-tax-kalculator`](hmrc-tax-kalculator) | HMRC's take-home pay engine ([hmrc/tax-kalculator](https://github.com/hmrc/tax-kalculator)) | [ITA 2007 s. 35](https://www.legislation.gov.uk/ukpga/2007/3/section/35), HMRC's PAYE specification | T and K codes miss the £9 that L codes get; the £100,000 taper not applied to the 2020 default code |
| [`urssaf-modele-social`](urssaf-modele-social) | Urssaf's payroll rules ([modele-social](https://github.com/betagouv/mon-entreprise)) | [CGI art. 83, 1° quater](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051765287) | the employer's cadre insurance contribution added to taxable pay in full (€706.50 a year at or above the ceiling); upstream issue #4320 |

[`uk-model`](uk-model) is the Lean model of the UK income tax and National Insurance (2025-26) the UK checks use.
The method, every difference and its classification are in [`uk-report.md`](uk-report.md) and
[`fr-report.md`](fr-report.md).

Each folder has:

- `lean/`: the finding as a standalone Lean 4 file (core only, `lean-toolchain` v4.35.0). `lean <file>` checks it:
  the exact cases by `decide`, the general statements by proof, no `sorry`.
- `scripts/`: how the official code was run and compared. The scripts were run on our build machine, where the checkouts and tools sat under `~/cmp`; the paths at the top of each script say where they expect them.
- `results/`: the summaries and every compared case (`.jsonl.gz`).
- `refs/` or `VERSIONS.txt`: the text of the law and the versions of the code that were checked.
- `figures/`: the calculation at one case, statute beside code.
