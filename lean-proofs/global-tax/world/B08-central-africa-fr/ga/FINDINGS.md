# Gabon (GA) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Marriage can cost tax: an unmarried parent's first child counts a full part, so a cohabiting couple with children has more parts than a married one
- kind: loophole-known
- art. 170: married = 2 parts + 1/2 per child; 'célibataire ou divorcé ayant un enfant à charge' = 2 parts. A couple earning 14 M + 6 M with two children: married, one return with 3 parts: IRPP 1 549 998; unmarried, the parent with the children has 2.5 parts and the other 1 part: 1 306 800 (exe). Marriage costs 243 198 a year; the scan finds a marriage penalty at 27 % of the couples tested and a bonus at 52 % (one-earner couples).
- provisions: CGI arts. 75, 77, 170
- Lean: GaTax.halfParts, GaTax.out
- status: modelled; scan reproduces

### F2 The quotient has no ceiling: the value of a half-part grows with income
- kind: loophole-known
- Unlike France's plafonnement, art. 168/170 divide the income by the parts with no cap on the advantage (only the six-children limit). At the 35 % top rate each half-part removes 35 % of up to 11 M of income per part from the tariff's top band.
- provisions: CGI arts. 168, 170, 174
- Lean: GaTax.irpp (Unit.quotient)
- status: modelled

### F3 The TCS exempts bonuses up to 4 M a year: pay as performance bonus rather than salary
- kind: loophole-known
- art. 347: the TCS (5 % above 150 000 a month) exempts 'primes de performance ... treizième mois ... bonus' within an annual 4 000 000. Moving 4 M of salary into such bonuses saves 200 000 of TCS; the IRPP is unchanged. The model has no bonus field (the TCS is computed on the whole wage).
- provisions: CGI arts. 346-349
- Lean: GaTax.person
- status: catalogued; not modelled

### F4 The printed 'rate x Q - subtraction' tariff is exactly the band tariff
- kind: model-fix
- kernel subAgrees on 17 probes including every threshold and its successor: no rounding slip in art. 174 (unlike the column tariffs found elsewhere).
- provisions: CGI art. 174
- Lean: GaTax.rows, #guard subAgrees
- status: proved by #guard

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Stay unmarried with children (single-parent full part) | recreated: filing-unit scanner, F1 | CGI art. 170 |
| K2 | Bonuses exempt from the TCS up to 4 M | not modelled: F3 | CGI art. 347 |
| K3 | Housing indemnity taxable only within 40 % of gross and 250 000 a month; benefits in kind at flat % (logement 15 %, domesticité 5 %, nourriture 25 %) | not modelled | CGI art. 93 |
| K4 | Family allowances up to 20 000 a month per child exempt | not modelled | CGI art. 91 1° |
| K5 | Housing-loan repayments deducted from the base up to 500 000 a month for five years | not modelled | CGI art. 92 |
| K6 | Children 18-28 in studies keep counting as half-parts | not modelled: children under 18 only | CGI art. 172 |
| K7 | Capital income at a final 20 % (15 % bons de caisse, 10 % long bonds) vs up to 35 % on wages | recreated: income-type scanner | CGI arts. 109, 110 |
| K8 | Late declaration loses the 20 % frais (penalty-like rule) | not modelled: a cost, not a saving | CGI art. 94 |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 5.16 M, art. 174 band)
- married vs cohabiting couples with the exe
- printed tariff vs bands (subAgrees)

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (CM CG CD MG among the covered countries)
- IMF Article IV and technical-assistance reports on the CEMAC members, DRC, Madagascar, Burundi, Djibouti, Comoros
- CEMAC directives on the harmonisation of direct taxation (IRPP/IS) and the CIMA/CIPRES social-security rules
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- droit-afrique.com and juriafrique compilations (droit-afrique answered 403 to scripts and the laptop; not bypassed)
- Academic work on family quotients in francophone Africa and on informal-sector minimum taxes

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5R sweep P2-6: household-total employee-contribution input allotted by wages (W5 review pass 2, 2026-11-20)
- kind: model-fix (cross-country sweep from NI W5R-1)
- The optional household-total employee-contribution input was halved between two adults, so a one-earner couple
  deducted half of the earner's own contributions. The deduction provision this model already cites deducts each
  employee's own contributions from that employee's income; the total is now allotted in proportion to wages (halves
  only when nobody has wages). Checked on 400 random households: outputs change only for two adults with the input and
  unequal wages. Script: world/w5/review2/sweep_alloc.py. Rescanned (scan_world.py).
- status: model changed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/GaTax/Verify.lean` (imported by the `GaTax` library and built; each guard evaluates `GaTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/GA.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Marriage penalty from the quotient: an unmarried parent's first child gives 2 parts, so a couple with 14 M + 6 M and two children pays 243,198 more married (3 parts on one return) than unmarried (2.5 + 1). G: f1_marriage_penalty_children. S: law/cgi2025.raw.txt:2583-2584 (art. 170: 'marié sans enfant à charge, célibataire ou divorcé ayant un enfant à charge : 2'). |
| F2 | explained | Quotient without a ceiling: design (value of a half-part rises with income). |
| F3 | lead | TCS exemption of bonuses up to 4 M: not modelled (no bonus field). |
| F4 | explained | Formula tariff = bands (#guard subAgrees). |
| W5R P2-6 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: marriage penalty up to 245,000 (27.3 % of points with a penalty) = F1; bonus 1,341,200 = one-earner quotient. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: An unmarried parent's first child gives 2 parts: marriage costs a two-earner family | household-unit effect | **new**: PwC Gabon prints the parts table ('Married person without dependent child or unmarried or divorced person having a dependent child 2'), from which the penalty can be computed, but does not state it; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Gabon quotient familial célibataire enfant à charge deux parts mariage'; 'Gabon personal income tax family quotient marriage penalty' (1 hits, titles checked); OpenAlex broad 'Gabon personal income tax', 'Gabon income tax wages', 'Gabon tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (gabon, 5 individual pages): 9 passages with the item's terms; Crossref IMF prefix 10.5089 'Gabon tax policy' (8257 records, titles only). Record: world/loopholes/africa_mena/search/GA-F1.json |

<!-- L1-VERIFICATION END -->
