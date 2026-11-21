# Sweden (Stockholm), inkomstår 2025: findings

Model: `lean/SETax` (statute provision by provision, on TaxKernel), exe `setax`. Validation: OECD Taxing Wages 2025
for SWE 56/56 lines exact (`harness/oecd_check.py`, `runs/oecd_check.json`); 22 worked examples of Skatteverket's
*Teknisk beskrivning SKV 433, 2025* as theorems (`SETax/Tests.lean`, all pass); Skatteverket's withholding tables
2025 (open data, 26 936 monthly cells, tables 29-42, columns 1/2/3/6) all equal to the statute model applied to the
band (`harness/table_check.py`, `runs/table_check.json`). Theorems: `SETax/Theorems.lean`, `SETax/Loopholes.lean`
(no `sorry`; `#print axioms` shows at most propext, Classical.choice, Quot.sound). Scans: `harness/scan.py`,
`harness/loop.py`, `harness/gov_check.py` (`runs/`), and the kernel's generic scanners
(`results/search/SUMMARY.md`). Amounts in kronor, Stockholm (30,60 % + begravningsavgift 0,07 %), adults 40 unless
stated; "70" means a person who had turned 66 at 1 January 2025.

Kinds: loophole-known | loophole-new | gov-error | statute-fault | model-fix. Known-ness: "known" cites where;
"not found in N sources searched" lists them.

### F1 Pensionsavgift floor: one more krona of pay at 24 899 kr costs 1 700 kr
- kind: loophole-known (notch)
- households: single, wages 24 899 vs 24 900 (any family type; the generic METR scanner found it blind: "1,699 at
  24,899", `results/search/SUMMARY.md`)
- amounts: total burden 0 -> 1 700 kr. Below 42,3 % of pbb (24 872,40 kr) no fee is due; the income is first
  rounded down to hundreds, so the fee starts at 24 900 kr on the whole income (7 % = 1 743 -> 1 700) while the
  income tax is still 0 (grundavdrag 24 900), so the fee's credit has nothing to reduce. A self-employed person
  meets the same notch at about 32 200 kr of profit (egenavgifter first).
- provisions: lag (1994:1744) 3 § ("avrundas till närmast lägre hundratal"), 4 § ("understiger 42,3 procent"), IL
  67 kap. 4 §; kernel `Contribution.floor_notch`
- Lean: `SETax.f1_fee_notch`, `SETax.fee_floor_notch`, `SETax.fee_floor_value`
- status: certain. Known: Skatteverket publishes the threshold ("Skattefri årsinkomst ... 24 873 kronor", *Belopp
  och procentsatser 2025*) and SKV 433 §3 notes higher withholding "i de lägsta inkomstskikten" because of the fee.
  Advice: a person with only a small job should keep the year's pay at or below 24 800 kr or well above it.

### F2 Working pensioners up to 213 000 kr pay the 7 % pensionsavgift in full: its credit only displaces jobbskatteavdrag
- kind: loophole-new (a trap: a hidden 7 % charge, with 100-kr notches)
- households: one person aged 66+ at 1 January 2025 with wages; and under 66 with wages
- amounts: the fee credit (67 kap. 4 §) comes before the jobbskatteavdrag in the 67 kap. 2 § order and both are
  limited by the tax; when the jobbskatteavdrag alone would wipe out the municipal tax, the fee credit just takes its
  place and the fee is a net cost. Age 70, pay 200 000 kr: municipal tax 27 509 kr, fee 14 000 kr (credited),
  jobbskatteavdrag 29 493 kr of which 13 509 kr used; income tax paid 0, yet the person pays the whole 14 000 kr fee
  (+ public service 899 + begravningsavgift 62). A 66+ wage earner pays no income tax after credits up to
  340 000 kr of pay, but pays the fee from 24 900 kr. Range where the fee is entirely uncompensated: 25 000-213 000 kr
  for 66+, 25 000-53 000 kr for under 66; some credit is wasted up to 341 000 kr (66+) and 86 000 kr (<66)
  (`runs/loop.json` "wasted_credits_age70/40"). Inside these ranges each 100-kr step of the rounded fee is a notch:
  one more krona of pay costs 100 kr (`runs/scan_metr.json`: 82 such steps for 66+ up to 309 300 kr, 42 for <66
  up to 85 100 kr).
- provisions: IL 67 kap. 2 § (order; "5-9 d ... och 46-48 §§ ... endast mot kommunal inkomstskatt"), 4 §, 8 §;
  63 kap. 3 a §; lag (1994:1744) 2-3 §§
- Lean: `SETax.f2_old_worker_fee_is_a_cost`, `SETax.f2_young_low_earner`
- status: certain (model = statute; the order is the statute's). Known-ness: the under-66 low band is acknowledged
  by SKV 433 §3; for working pensioners the general statements say the opposite ("de allra flesta får
  skattereduktion för hela beloppet", Skatteverket *Skattereduktioner* page; "Skattereduktion medges med hela den
  allmänna pensionsavgiften", FAR *Fakta och siffror*); not found in 4 sources searched (those two, SKV 433 2025,
  the Pensionsmyndigheten *Pension och skatt* reports listed by a search). The fee still earns inkomstpension
  rights, so it is not a pure loss; the point is that the tax-financed compensation every other earner gets does
  not reach these people.
- for the government: if the intent is that the allmän pensionsavgift is fully tax-compensated, the credit would
  have to be allowed to exceed what the jobbskatteavdrag leaves of the municipal tax, or the 66+
  jobbskatteavdrag would have to be designed net of the fee.

### F3 IL 67 kap. 2 § does not say which tax a two-tax credit consumes first (up to 3 520 kr at stake)
- kind: statute-fault (reading; gap)
- households: single, wages 55 000, interest 20 000 (390 of 1 736 grid points differ, `runs/loop.json`
  "credit_order")
- amounts: the pensionsavgift credit may be set against municipal or state income tax (the 30 % capital tax is
  state tax, 65 kap. 7 §); the jobbskatteavdrag only against municipal tax. Taken first against municipal tax (the
  reading Skatteverket's tables use, SKV 433 7.5 example 2, where there is no state tax) the fee credit blocks the
  jobbskatteavdrag: total 10 122 kr; taken first against the capital tax: 6 602 kr. 3 520 kr apart.
- provisions: IL 67 kap. 2 § (2025 wording, Lag 2022:445; unchanged on this point by SFS 2025:539/1370), 4 §, 7 §;
  65 kap. 7 §
- Lean: `SETax.f3_credit_order`; the model computes both (`setax --state-first`)
- status: open. Skatteverket's public page states the order of the credits and that their sum may not exceed the
  taxes, but not the order of the taxes (fetched: skatteverket.se/privat/skatter/arbeteochinkomst/skattereduktioner).
- draft question to Skatteverket (not sent): "Vid beräkning av slutlig skatt för inkomstår 2025: när en
  skattereduktion som enligt 67 kap. 2 § andra stycket IL får räknas av mot både kommunal och statlig inkomstskatt
  (t.ex. skattereduktion för allmän pensionsavgift) inte ryms helt, mot vilken skatt räknas den av först? För en
  person med 55 000 kr i lön och 20 000 kr i ränteinkomst skiljer det 3 520 kr, eftersom jobbskatteavdraget bara
  får räknas av mot kommunal inkomstskatt. Var finns ordningen beskriven?"

### F4 The 2025 formulas jump at their joints; one gives a negative marginal rate for pensioners
- kind: statute-fault (minor)
- households: 70, pension 115 500 vs 115 600 kr (total 11 812 -> 11 748: 100 kr more pension, 64 kr less tax);
  wage earner at 475 100 vs 475 200 kr (jobbskatteavdrag 44 656 -> 44 654)
- amounts: the coefficients are rounded to 3-4 decimals, so adjacent lines do not meet. 63 kap. 3 § jumps up by
  0,001 pbb at 2,72 pbb (hidden by the rounding up to 100, and for 66+ cancelled exactly by a -0,001 pbb jump of
  3 a §); 67 kap. 7 § jumps up by 0,000358 pbb at 3,24 pbb and down by 0,00016 pbb at 8,08 pbb; 63 kap. 3 a § (SFS
  2024:1131) jumps at 0,91 (+0,016 pbb, invisible: the deduction exceeds the income there), 1,11 (+0,00027),
  1,965 (+0,003973 pbb = 233,64 kr), 3,24, 7,88, 8,08, 10,94 and 12,47 pbb (+0,00008 to +0,000484). The 2026
  wording (SFS 2025:1376) keeps the 1,965 jump and adds a -0,00084 pbb drop of the jobbskatteavdrag at 8,08 pbb.
- provisions: IL 63 kap. 3 §, 3 a §; 67 kap. 7 §
- Lean: `SETax.ga_jump_272`, `SETax.jsa_jump_324`, `SETax.jsa_drop_808`, `SETax.f4_extra_jump`,
  `SETax.f4_negative_marginal`
- status: certain, small. Not found in 1 targeted search and SKV 433 2025 (which tabulates the lines without
  remarking on the joints). Same kind as the German § 32a finding (DE S1).

### F5 Stockholm employees are over-withheld about 3 300 kr a year by the tables
- kind: gov-error -> convention (not an error)
- households: Stockholm, outside Svenska kyrkan, column 1, monthly pay 2 000-120 000 kr (`runs/gov_check.json`)
- amounts: at the average wage (46 500 kr/month) table 31 withholds 124 188 kr, the final tax is 120 927 kr:
  3 261 kr too much; 97 % of the grid over-withheld, up to 12 884 kr (118 500 kr/month), under-withheld at most
  792 kr. Causes: the table number is the total rate in whole percent (30,67 -> 31); the table assumes 1,16 pp of
  begravnings-/trossamfundsavgift (Stockholm non-member: 0,07), so the jobbskatteavdrag is computed at 29,84 %
  instead of 30,60 %; the band's top amount is used.
- provisions: SKV 433 2025 §§ 7.1, 7.3, 7.5.2 (SKVFS 2024:19); SFL (2011:1244) on tables and the final tax
- Lean: `SETax.tableMonthly` (table = statute with T - 1,16 % and 1,16 %)
- status: convention by design (whole-percent tables), documented by Skatteverket; the effect is an interest-free
  loan of about 0,6 % of pay, refunded with the final tax.

### F6 The withholding tables are exactly the statute applied to the top of each band
- kind: gov-error -> none found (verification)
- households: all 6 734 monthly rows x columns 1, 2, 3, 6 of tables 29-42
- amounts: 26 936 of 26 936 cells equal; the percent rows above 80 000 kr/month: 360 919 of 360 928 200-kr steps
  equal the half-up rounded percentage of the tabled tax; the 9 others are exact ties (x,5 %) that Skatteverket
  keeps in the lower percent (undocumented tie rule; e.g. table 38 column 2 at 1 042 800 kr: 56,5 % -> 56)
- provisions: SKV 433 2025 §§ 5, 7, 8
- Lean: `SETax.table34_20200`, `SETax.table34_80000`; `harness/table_check.py`, `harness/pct_scan.py`
- status: certain. Columns 5 and 6 are identical in every row and in the one-off tables of SKV 433 §10 (looked
  like a copy error; it is not: the fee of column 5 is fully credited wherever there is tax).

### F7 The OECD's Swedish figures: exact, with three conventions to know
- kind: gov-error -> convention
- households: the eight Taxing Wages types at AW 557 053 kr
- amounts: every line equal (56/56). Conventions: (1) the national average municipal rate 32,41 % (Stockholm:
  30,60 %); (2) the public service-avgift (1 249 kr per adult at AW in 2025, a compulsory 1 % levy on taxable
  earned income collected with the income tax, 2019-2025) and the begravningsavgift (national average 0,266 %,
  about 1 400 kr at AW) are left out of the tax wedge; (3) every credit is booked against central-government tax
  (CGITFP = -87 795 at AW), although in law the jobbskatteavdrag and the förvärvsinkomst credit may only reduce
  municipal tax (67 kap. 2 §): the OECD's split follows who bears the cost, not the statute's allocation.
- provisions: IL 65 kap. 3 §, 67 kap. 2 §; lag 2018:1893; begravningslagen 9 kap.
- Lean: `SETax.oecd_s100`, `SETax.oecd_s167`; `harness/oecd_check.py`
- status: certain; conventions, not errors.

### F8 An amending act had to be amended before it entered into force (67 kap. 1-2 §§)
- kind: statute-fault (repaired before commencement)
- amounts: none for 2025. SFS 2025:539 (May 2025, in force 2026-01-01, removing the reduction for mikroproduktion)
  rewrote 67 kap. 1 § to "bestämmelser om skattereduktion för fysiska personer" only; SFS 2025:1361 (Nov 2025)
  then gave legal persons a gift reduction (67 kap. 24 a, 25 a, 26 a §§), which that wording no longer covered;
  SFS 2025:1370 amended "lagen (2025:539) om ändring i inkomstskattelagen" so that 1 § again names legal persons and
  2 § says they set it only against state tax. A consistency fault caught in time, visible only in the amending
  history.
- provisions: IL 67 kap. 1-2 §§ (Lag 2022:445 -> SFS 2025:539 -> SFS 2025:1370)
- Lean: none (no 2025 effect); sources `refs/raw/SFS2025-539.txt`, `SFS2025-1370.txt`, `SFS2025-1361.txt`
- status: certain; repaired.

### F9 The year's amounts follow their indexation rules
- kind: gov-error -> none found (verification)
- amounts: skiktgräns 2025: 598 500 x (KPI jun 2024 415,86 / KPI jun 2023 405,49 + 0,02) = 625 776,04 -> 625 800
  (65 kap. 5 §, rounded up to 100) as published; 2026: 625 800 x (418,94/415,86 + 0,02) = 642 950,89 -> 643 000.
  Prisbasbelopp 2025: 36 396 x 415,86 / 257,40 = 58 802,02 -> 58 800 (SFB 2 kap. 7 §, nearest 100); 2026:
  59 237,53 -> 59 200. KPI: SCB PR0101 KPItotM (fastställda tal).
- status: certain, no error.

### F10 Individual taxation: splitting earnings between spouses saves up to 178 832 kr
- kind: loophole-known
- households: couple, wages 1 300 000 on one return vs 650 000 + 650 000: 479 878 vs 301 046 kr (600 000: 28 914)
- provisions: individual taxation (IL 1 kap. 5 §: each person's own förvärvsinkomst; no joint assessment); limits:
  60 kap. (medhjälpande make), 56-57 kap. (närstående in fåmansföretag)
- Lean: `SETax.f10_spouse_split`; generic scanner `unit.py` found it blind (178 885 at 3,95 AW)
- status: known (separate taxation of spouses).

### F11 Bunching: 800 000 kr in one year vs 400 000 + 400 000 costs 72 458 kr more
- kind: loophole-known
- households: single, two years at 2025 rules (`runs/loop.json` "timing")
- provisions: IL 65 kap. 5 § (skiktgräns), 63 kap. 3 § (grundavdrag falls with income); tools: periodiseringsfond
  (30 kap.), expansionsfond (34 kap.) for sole traders
- status: known. The generic timing scanner reports only small gains (1 842 kr) because it moves income
  symmetrically around each point; large gains come from straddling the skiktgräns.

### F12 Interest deductions: who takes them matters (30 % up to 100 000 kr per person, then 21 %; non-refundable)
- kind: loophole-known
- households: couples (`runs/loop.json` "interest_allocation"): 500 000 + 500 000 pay, 500 000 kr interest: all on
  one return 139 724 kr, split 83 276 kr (56 448 kr); 600 000 + 50 000 pay, 300 000 kr interest: all on the earner
  65 576 kr, all on the low earner 137 576 kr (72 000 kr)
- provisions: IL 67 kap. 10 §, 2 §; 42 kap. 1 §
- Lean: `SETax.f12_interest_split`
- status: known (the 100 000 kr threshold and the 30/21 % split are per person; spouses with a joint loan choose who
  pays the interest).

### F13 Gifts: 1 krona more unlocks 500 kr; the 3 000 kr cap is per person
- kind: loophole-known
- amounts: 1 999 kr of gifts -> 0, 2 000 kr -> 500 kr; a couple giving 24 000 kr gets 3 000 kr on one return,
  6 000 kr if each gives 12 000 kr
- provisions: IL 67 kap. 21, 22, 26 §§ (26 § Lag 2021:1160: "högst 3 000 kronor")
- Lean: `SETax.f13_gifts`
- status: known (statute design).

### F14 Owner-manager (3:12, 2025): above 475 100 kr of salary, dividends taxed as salary beat salary
- kind: loophole-known (with a model nuance)
- households: one owner, company profit before salary P = 1 000 000-3 000 000 kr, gränsbelopp by the
  förenklingsregel 209 550 kr (`runs/loop.json` "owner_manager_312")
- amounts: best salary 475 000 kr for P >= 1 000 000 (all-salary loses 54 557 kr at P = 1 000 000, 103 055 kr at
  3 000 000). At the margin, 131 420 kr of profit gives the owner 100 000 kr of salary (31,42 % arbetsgivaravgifter)
  or 104 346 kr of dividend above the gränsbelopp (20,6 % bolagsskatt), taxed in tjänst but with no
  jobbskatteavdrag and no fee: 448 929 vs 451 958 kr net. Below 8,08 pbb salary wins because each krona still raises
  the jobbskatteavdrag; above it the 20,6 % < 31,42 % difference decides.
- provisions: IL 57 kap. 20 § ("Utdelning upp till gränsbeloppet ska tas upp till två tredjedelar i inkomstslaget
  kapital"), 20 a § (90 ibb cap), 65 kap. 10 §, 67 kap. 6-7 §§; socialavgiftslagen (2000:980)
- Lean: `SETax.f14_owner_dividend_beats_salary`
- status: known in its parts ("Några socialavgifter ska dock inte betalas på tjänstebeskattad utdelning", FAR
  Resultat 2015 nr 9; the salary-vs-dividend guides of Företagarna and Spiris advise salary up to the brytpunkt).
  Nuance: ignoring the social-insurance value of salary (pension rights up to 8,07 ibb, sickness pay) and the
  lönebaserat utrymme of the huvudregel (not modelled), the optimum is 8,08 pbb, not the brytpunkt.

### F15 Löneväxling pays above the brytpunkt
- kind: loophole-known
- amounts: 10 000 kr less pay saves 3 067 kr below 643 100 kr and 5 067 kr above; the employer can pay
  10 576 kr of premium for the same cost (särskild löneskatt 24,26 % vs arbetsgivaravgifter 31,42 %); at 66+ a
  pension of 250 000 kr pays 2 513 kr on the extra 10 576 kr
- provisions: IL 65 kap. 5 §; lag (1991:687) om särskild löneskatt på pensionskostnader; Belopp och procentsatser 2025
- Lean: `SETax.f15_salary_sacrifice`
- status: known (standard advice: above the brytpunkt and 8,07 ibb).

### F16 ISK: 0,888 % of capital above 150 000 kr per person instead of 30 % of the return
- kind: loophole-known
- amounts: 1 000 000 kr: 7 548 kr a year (direct holding at a 7 % return: 21 000 kr); break-even return 2,96 %;
  a couple with 500 000 kr each pays 1 332 kr less than one person with 1 000 000 kr; two children's accounts at
  150 000 kr each save 2 664 kr a year
- provisions: IL 42 kap. 35-37 §§, 45-48 §§ (SFS 2024:1131, the 150 000 kr from 2025), statslåneränta 30 Nov 2024
  1,96 %
- Lean: none (ISK is outside the contract household; computed in `harness/loop.py` from the cited rules)
- status: known (the purpose of ISK).

### F17 Pensioners pay about 50 % between 643 300 and 733 200 kr although the state tax has not started
- kind: loophole-known (design)
- amounts: the förhöjt grundavdrag is withdrawn at 62 % of income between 10,94 and 12,47 pbb, so the marginal
  rate is 1,62 x 30,67 % = 49,7 % up to the pensioners' brytpunkt 733 200 kr (Belopp och procentsatser 2025)
- provisions: IL 63 kap. 3 a § (SFS 2024:1131)
- status: known (the design aligns the pensioners' brytpunkt; Skatteverket publishes "Den som fyllt 66 vid årets
  ingång 733 200 kronor").

### F18 The gift reduction cap in 2025 is 3 000 kr, not 1 500 kr
- kind: model-fix
- the first parameter draft used 1 500 kr (the SFS 2019:454 wording); the amending history shows 67 kap. 26 § was
  raised to 3 000 kr by SFS 2021:1160 for gifts after 2021-12-31, so 3 000 kr applies in 2025 (and again in the
  2026 wording of SFS 2025:1361). Fixed before any run.

### F19 The dual-income wedge: capital income pays 30 %, labour up to 50,67 %
- kind: loophole-known
- amounts: the generic income-type scanner: the same amount as interest, dividends or gains instead of wages costs
  up to 15,55 % of the income less at 5 AW, and up to 18 % more at 0,25 AW (no grundavdrag or credits on capital)
- provisions: IL 65 kap. 5, 7 §§; 57 kap. (the 3:12 rules that police the wedge for owner-managers)
- status: known (the 1991 dual income tax).

## Notes on the generic scanners (`results/search/SUMMARY.md`)
- "Bands above the top rate" (max 54,7 %, average 50,7 %, above 1,16 AW) are the 100-kr rounding of the fastställd
  förvärvsinkomst seen at 0,002 AW steps; the true marginal rate there is 50,67 % (30,60 + 0,07 + 20).
- The edges scanner's "largest rounding-scale fall 99 at 77 899" is the same rounding (1 kr more pay crosses a
  hundred).
- Not found blind by the generic scanners (Sweden-specific searches needed): F2 (needs age 66+), F3 (needs capital
  income with low pay and the --state-first reading), F4's negative step (pension at 66+), F12-F14 (per-person
  capital, gifts, company side: `company.json` has no SE entry; proposed entry in PROGRESS.md).
