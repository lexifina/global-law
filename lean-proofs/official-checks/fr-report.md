# modele-social (Urssaf) against the statute and our Lean adapter: employee contributions, CSG/CRDS, net pay, 2025

18 Nov 2026.

## Setup and versions (`VERSIONS.txt`)

- Engine: `modele-social` **11.1.0** (npm; gitHead 2e786977712ce1225fef95b3469f98fd0ef0fd5c, mon-entreprise commit of
  16 Jul 2026), `publicodes` **1.10.4**, pinned exactly in `engine/package.json`.
- Upstream: sparse clone `src/me`; `origin/master` 8b2affafb5ebf65c0904876675fdb1fda3a29a23 (18 Nov 2026) leaves the
  rule blocks of the one finding unchanged.
- Runtime: Node v26.13.1 (official tarball, SHA-256 checked) in `opt/node`; Pillow 13.0.0 in `opt/venv`.
- Our side: `~/cmp/compare/lean/Compare/Fr.lean` (`contrib`, `taxableSalary`) run unchanged from its existing build via
  `LEAN_PATH`; `lean/Ours.lean` only prints its lines.
- Statute reference: `scripts/law.py`, written from the texts (exact decimals), also covering what the adapter leaves
  out: APEC, compulsory cadre prévoyance (1,50 % T1), complementary health, CGI art. 83, 1° quater.

### Engine situation (every assumption; `engine/driver.mjs`)

`date: '01/06/2025'` (the published rules default to 01/07/2026; all 2025 rates are in the rules' date variations; the
12 months of 2025 and 31/12/2025 give identical figures); `salarié . contrat: 'CDI'`; `salaire brut: '<g> €/an'` or
`€/mois`; `statut cadre: oui|non`; `temps partiel: non` (151,67 h); `alsace moselle: non`. Everything else at engine
defaults (no overtime, bonuses, benefits in kind, meal vouchers, transport, apprenticeship, JEI, outre-mer). Variants:
- **neutral**: `prévoyances . santé . montant = 0 €/mois` and, for cadres, `prévoyances . employeur . cadres = 0`, to sit
  beside the adapter, which has neither;
- **default**: engine defaults (mutuelle 40 €/mois, 50 % employer; cadre prévoyance 1,50 % of T1).

Lines read (unrounded): vieillesse salarié plafonnée/déplafonnée, retraite complémentaire salarié (T1+T2), CEG, CET,
APEC, CSG déductible, CSG non déductible, CRDS, assiette abattue, assiette de base, prévoyances employeur (and cadres),
total cotisations salarié, net, net imposable, net à payer avant impôt (= net here: no benefits in kind, no meal vouchers).

## Coverage

- 3 900 annual pay points: 0-8 PASS by 100 €, 8-10 PASS by 1 000 €, plus SMIC (21 622 €), PASS 47 100, 4 PASS 188 400,
  8 PASS 376 800, each ± 0, 1, 2, 10, 100, 1 000 €; non-cadre and cadre.
- Monthly thresholds to the cent: SMIC 1 801,80, PSS 3 925, 4 PSS 15 700, 8 PSS 31 400, each ± 0,01 and ± 1 €.
- Every month of 2025 and 31/12/2025 at 2 000, 5 000, 20 000 €/mois.
- 8 685 engine cases, 231 675 line comparisons (`scripts/compare.py` -> `out/diffs.json`).

## Results

### Adapter vs engine (neutral, 7 800 cases)

Every line the adapter computes matches the engine **to the cent at all 3 900 points, both statuses**: vieillesse
plafonnée/déplafonnée, AGIRC-ARRCO T1+T2, CEG, CET (including its jump at the PASS: 0 at 47 100 €, 65,94 € at
47 101 €), the CSG/CRDS base with the 1,75 % abatement up to 4 PASS, CSG déductible and non déductible, CRDS, the
taxable salary (exact cents; and box 1AJ rounded to the euro within 1,50 €), contributions + CSG/CRDS in euros. Only
APEC differs (our documented omission).

### Engine vs statute reference (8 685 cases)

Identical (to 1e-6 €) on every contribution line, the CSG base (with employer health and cadre prévoyance), total
employee contributions and net. Two lines differ:

| # | Difference | Cases | Class |
|---|---|---|---|
| 1 | **Net imposable of every cadre**: the engine adds the employer's cadre prévoyance (1,50 % x min(brut, PSS)) to taxable pay; CGI art. 83, 1° quater makes it deductible (with the employee's prévoyance, within 5 % PASS + 2 % of pay, at most 2 % of 8 PASS). Gap exactly 1,50 % x min(brut, PSS) in all 441 cadre/default cases with pay > 0: 58,875 €/mois, **706,50 €/an** at or above the PASS. 5 000 €/mois: engine 4 158,55 €, law 4 099,68 €. | 441 | **(a)**, **already reported** upstream: open issue betagouv/mon-entreprise#4320 (17 Feb 2026), acknowledged by a maintainer; still in 11.1.0 and on master |
| 2 | Pay 0 with the default mutuelle: the engine floors the net at 0 (net 0 vs -263,28 €/an; net imposable 246,96 vs -16,32). | 2 | (c) degenerate case |

### Finding 1 in detail

- Rules: `règles/salarié/rémunération.publicodes` l. 117-123 (`net . imposable . sans déductions` sums
  `cotisations . prévoyances . employeur` = `santé . employeur` + `conventionnelle . employeur` + `cadres`);
  `règles/salarié/cotisations.publicodes` l. 881-929 (the 1° quater limit applied to the employee part only).
- Law: CGI art. 83, 1° quater, al. 1-4; same wording in the versions in force from 2 Jun 2024 and 19 Jun 2025 and today.
- Lean `lean/01-prevoyance-cadres-net-imposable.lean`: exact case by `decide` (no
  axioms) and, for every pay >= 0, `engine g - law g = 1,50 % x min(g, PSS)` with the limit never binding under the
  default cover (axioms `propext`, `Quot.sound` only; no `sorry`).
- Fix tested in memory (`engine/patch_4320.mjs`): patched engine = statute reference within 7e-12 € on 1 278 cases
  (cadres/non-cadres, 250-40 000 €/mois, mutuelle 0/40/100/400 €/mois, including binding limits; 2 negative-net cases
  left out).
- Related, not counted: #4668 (closed), employee health share in the net; outside our scope.

### Our side (adapter): no errors in what it computes; documented simplifications only

| Item | Effect | Class |
|---|---|---|
| APEC omitted (0,024 % employee, up to 4 PASS, cadres) | <= 45,22 €/an; 3 899 cadre cases differ by exactly that | (c) documented ("no APEC") |
| Employer cadre prévoyance (1,50 % T1, compulsory for cadres) and employer health not in the CSG/CRDS base | cadre at >= PASS: 9,7 % x 706,50 = 68,53 €/an more CSG/CRDS by law (6,8 points deductible) | (c) documented ("no employer-paid complementary health or provident cover ...") |
| Employer health share not added to taxable pay (art. 83, 1° quater, al. 3) | taxable pay low by that share (engine default 240 €/an) | (c) same |
| Per-line rounding to the euro on annual pay | within 1,50 € everywhere | (c) documented |

Corrected reading if the adapter is to cover cadres: APEC = `rnd (24 * min g (4*pass)) 1000` cents (0,024 % = 2,4 bp)
added to `ssc`; 1,50 % x T1 added to `csgBase` without abatement; taxable salary not increased by that 1,50 %
(art. 83, 1° quater). Nothing in the originals was modified.

## Counts

| Class | Count |
|---|---|
| (a) genuine error in modele-social | 1 (already reported upstream as #4320) |
| (b) error in our adapter | 0 |
| (c) scope / convention / documented simplification | 5 (engine at zero pay; adapter: APEC, prévoyance/health in CSG base, employer health in taxable pay, euro rounding) |
| (d) ambiguous | 0 |
