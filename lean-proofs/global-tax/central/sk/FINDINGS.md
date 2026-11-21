# Slovakia (SK), tax year 2025: findings

Amounts in euros. Lean names refer to `lean/SkTax/*.lean` (all proved, no `sorry`). Statute copies: `refs/slovlex/`
(Slov-Lex consolidated versions of zákon 595/2003 of 1. 1. 2024, 1. 1., 15. 3., 1. 4., 1. 7., 1. 12. 2025 and 1. 1. 2026;
461/2003, 580/2004, 600/2003, 601/2003 and opatrenie 149/2024 of 1. 1. 2025). Finančná správa pages: `refs/fs/`.
"Not found in N sources" counts the sources read for the question (the three Finančná správa bonus pages, the
podnikajte.sk 2025 bonus examples, podnikajte.sk "Ako vyberať peniaze z s.r.o.", epravo.sk "Porovnanie sro vs. živnosť
2025") plus one web search of the advisory literature; the budget allowed no wider search.

### F1 OECD vs statute: contributions rounded monthly per insurance (explained, 0,21–0,30 €)
- Kind: model-fix (explains every OECD difference; a convention, not an error)
- Households: OECD S67, S100, S167 (and every type built from them).
- Amounts: statute 1 758,62 / 2 624,89 / 4 383,65 € of employee contributions vs OECD 1 758,83 / 2 625,12 / 4 383,95 € (the
  OECD takes 13,4 % of the annual wage once and keeps unrounded fractions: GEBT 19 590,427201, BTA 5 027,341093).
- Provisions: ZSP § 129 ods. 2 ("Jednotlivé sumy poistného ... sa zaokrúhľujú na najbližší eurocent nadol"), the month
  being the rozhodujúce obdobie; ZZP § 19 ods. 3 (annual health, down to the cent); ZDP § 47 (tax, halves up).
- Lean: `Tests.lean` section D (OECD-style contributions reproduce the OECD's CGTC, CGITLETC, BTA, HFTA to the cent; the
  statutory ones differ by the amounts above).
- Status: explained. OECD check: 56/56 lines exact (within 1 €) with `~/cmp20/central/oecd/check.py SK` and with
  `~/cmp20/harness/oecd_check20.py SK`; take-home pay 8/8.

### F2 Employer side not compared (note)
- Kind: model-fix (note only; not counted)
- The OECD's employer rate for SVK is 32,2 % (2024–2025) and 29,7 % (2023); the statute's employer total is 35,2 % (ZSP
  §§ 130 b), 131 ods. 1 b), 132 b), 133, 135, 136 b) 1., 136a, 137 a) = 25,2 %; ZZP § 12 ods. 1 písm. d) 10 %). The OECD
  excludes funded second-pillar contributions, which explains 2023 (35,2 − 5,5) but not the 3,0 points of 2025. Outside the
  household contract. Open item.

### F3 § 33 ods. 8 and 11 as published for 1. 1. 2025: the bonus withdrawal could be escaped by pooling (closed 15. 3. 2025)
- Kind: statute-fault (closed by the legislature, retroactively for the whole year)
- Household: two children under 15; the claimant's own base 3 000 €, the other parent's 40 000 €.
- Amounts: under the 1. 1. 2025 text 2 400 € (ods. 8 lets the claimant add the other parent's base "na účely výpočtu výšky
  nároku na daňový bonus podľa odsekov 1 a 6", the cap, while ods. 11 reduced the bonus on "základ dane ... alebo ich
  úhrn", the claimant's own); under the text in force from 15. 3. 2025, 1 080 € (ods. 8 now says "odsekov 1, 6 a 11" and
  ods. 11 adds "alebo navýšený základ dane (čiastkový základ dane) podľa odseku 8"). Difference 1 320 €; in general the
  whole bonus of a couple with one high and one very low earner.
- Provisions: ZDP § 33 ods. 5, 8, 11 (diff of versions 20250101 → 20250315 in `refs/slovlex/`); § 52zzzd ("Ustanovenia
  § 33 ods. 5, 8 a 11 v znení účinnom od 15. marca 2025 sa prvýkrát použijú pri podaní daňového priznania za zdaňovacie
  obdobie 2025"). Finančná správa (podpora 790897, 272586) computes with the "navýšený základ".
- Lean: `Findings.f3_gap`; the 1. 1. 2025 reading is `sktax --statute-taper`.
- Status: fault in the 1. 1. 2025 text, closed 2½ months later; the model follows the amended text by default.

### F4 Stale transitional provisions on the bonus: § 52zzp ods. 6 and the § 33 ods. 1 cross-reference
- Kind: statute-fault
- Households: children aged 18–25 in education (nezaopatrené).
- Amounts: § 52zzp ods. 6 (still in the 2025 and 2026 texts): "Nárok na daňový bonus podľa § 33 ods. 1 v znení účinnom od
  1. januára 2023 si daňovník môže uplatniť prvýkrát za kalendárny mesiac január 2025." That text of § 33 ods. 1
  (`zdp595_20240101`) gives "50 eur mesačne, ak vyživované dieťa dovŕšilo 15 rokov veku" with no upper age (600 € a year
  for a student of 18–25); § 52zzzb ods. 6 (zákon 278/2024) applies the 2025 text (50 € only until the month of the 18th
  birthday) from the same month. Two transitional provisions name January 2025 for two different texts. § 33 ods. 1 also
  still opens "Ak § 52zzp ods. 3 až 5 neustanovuje inak", provisions that apply only "od 1. januára 2023 do 31. decembra
  2024".
- Provisions: ZDP § 33 ods. 1; § 52zzp ods. 3–6; § 52zzzb ods. 6 (1. 1. 2025, 1. 12. 2025 and 1. 1. 2026 versions).
- Lean: not a computation; the model applies § 52zzzb ods. 6 as Finančná správa does ("Zmeny platné od 1.1.2025", otázka 2:
  a student born 15. 4. 2007 gets the bonus "naposledy za mesiac apríl 2025"; `Tests.lean` C).
- Status: open; lex posterior settles it in practice, but the stale text should be repealed. Not found discussed in the
  6 sources read.

### F5 The 2025 bonus withdrawal is avoided by letting the lower earner claim
- Kind: loophole-new (not found stated as a way around § 33 ods. 11 in the 6 sources read; it follows directly from § 33
  ods. 4 "môže si daňový bonus uplatniť len jeden z nich" and ods. 11 being per claimant, so advisers may well use it)
- Household: married couple, gross wages 60 000 € and 12 000 € (§ 5 bases 51 960 € and 10 392 €), children 5 and 9.
- Amounts: claimed by the higher earner the bonus is 0 € (each child's 1 200 € is cut by (51 960 − 25 740)/10); claimed by
  the lower earner 2 400 € (`sktax`: incomeTax 10 636 € vs 8 236 €). A claimant whose own base is ≤ 25 740 € loses nothing
  to ods. 11 whatever the household's income; the cap needs only 1 200 n / pct(n) € of own base (4 138 € for one child,
  6 667 € for two). The withdrawal therefore reaches single parents, one-earner couples and couples where both bases exceed
  25 740 €, not high-income two-earner households as such.
- Provisions: ZDP § 33 ods. 4, 6, 11.
- Lean: `Findings.f5_claimant`, `Findings.f5_no_taper_below`; the model picks the better claimant unless `skBonusBy`.
- Status: confirmed on the statute; Finančná správa's examples compute per claimant (790897 otázka 5).

### F6 Marginal effective tax rate above 100 % with eight children under 15 (55 % with two)
- Kind: loophole-new (a stacking defect; not found in the 6 sources read)
- Households: a sole earner with n children under 15, gross 29 723–43 580 € (base 25 740–37 740 €).
- Amounts: the § 11 ods. 2 withdrawal (a quarter of the base) makes 19 % act as 23,75 %; § 33 ods. 11 adds 10 % per child;
  after 13,4 % contributions the METR on gross is 13,4 + 86,6 × (23,75 + 10 n) %: 51,3 % for n = 2 (scanner: 51,2 %
  average, 55,0 % peak, against a top statutory rate of 27,55 %), 94,6 % for n = 7, **103,3 % for n = 8** (`sktax`: +1 000 €
  gross from 34 000 € gives +899 € tax and +134 € contributions).
- Provisions: ZDP § 11 ods. 2 písm. b), § 33 ods. 11; ZSP §§ 130–136; ZZP § 12.
- Lean: `Theorems.ncz_band_marginal` (5 cents of taxable base per 4 cents of base), `Theorems.bonus_taper_step` (n cents of
  bonus per 10 cents of base, any n), `Findings.f6_eight_children`.
- Status: confirmed; scanners `results/search/metr.md`, `phaseouts.md` (8 bands above the top rate, no cliffs).

### F7 Timing: bunching income across the end of the bonus withdrawal saves up to 2 384 € over two years
- Kind: loophole-new (not found in the 6 sources read)
- Households: single parent with two children; one-earner couple with two children.
- Amounts: 43 647 € gross in each of two years vs 57 596 € and 29 699 €: 2 384 € less tax (12,2 % of AW); 2 403 € for the
  couple; 22–24 % of the scanned points gain more than 0,1 % of AW. The marginal rate is 51–55 % inside the withdrawal and
  38,5 % after it (base 37 740 €), so net income is not concave there. Routes: an SZČO's invoicing and expenses, an
  employee's bonus month (ZDP § 4 ods. 3: wages paid by 31 January count for the previous year).
- Provisions: ZDP § 33 ods. 11, § 11 ods. 2, § 4 ods. 3.
- Lean: `Theorems.bonus_taper_step`, `Theorems.bonus_gone` (the rate drop at the band's end).
- Status: confirmed by `~/cmp20/harness/search/timing.py` (`results/search/timing.md`).

### F8 The 100 000 € notches: 15 % PIT on business income and 10 % CIT
- Kind: loophole-known (threshold management; the notch follows from the text)
- Households: an SZČO with paušálne výdavky; an s.r.o. owner paid by dividends.
- Amounts: SZČO, receipts 100 000 € → 100 001 €: tax 8 193 € → 10 748 € (+2 555 € for 1 € more); s.r.o. with profit =
  revenue: owner's net 83 208 € → 73 234 € (−9 974 €; CIT 10 % → 21 % on the whole profit). The § 6 tax jumps by 4 % of the
  base (up to 1 937,77 €) at the threshold.
- Provisions: ZDP § 15 písm. a) bod 2, 3; § 15 písm. b) bod 1a, 1b.
- Lean: `Findings.f8_notch`; `results/owner_sk.md`.
- Status: confirmed.

### F9 The 8 580 € SZČO social-insurance threshold
- Kind: loophole-known (epravo.sk 2025: "hranica pre povinné sociálne odvody")
- Household: an SZČO with actual expenses, receipts 8 580 € vs 8 581 € (steady state).
- Amounts: social contributions 0 € → 2 844,24 € (12 × 237,02 €); net loss 2 600 € for 1 € more receipts.
- Provisions: ZSP § 21 ods. 1 (12 × the § 138 ods. 9 minimum base of 715 €), §§ 130, 131, 132, 137.
- Lean: `Findings.f9_notch`.
- Status: confirmed (insurance starts on 1 July of the next year; steady state as modelled).

### F10 Owner-manager: dividends instead of salary; self-employment with paušálne výdavky instead of employment
- Kind: loophole-known (podnikajte.sk "Ako vyberať peniaze z s.r.o."; epravo.sk 2025)
- Household: a single owner, pre-tax profit P, all paid out (`tools/owner_sk.py`, company side cited there).
- Amounts at P = 50 000 €: all salary 26 722 € net (53,4 %); all dividends 40 649 € (81,3 %, after 1 201,20 € of health as
  a self-payer); a few hundred euros of salary + dividends 41 604 € (83,2 %); SZČO with actual expenses 29 552 € (59,1 %);
  SZČO with paušálne výdavky and no real costs 38 272 € (76,5 %). Dividends over salary: 14 882 € (P = 20 000 €: 5 171 €;
  P = 100 000 €: 32 262 €).
- Provisions: ZDP § 15 písm. b), § 43 ods. 1 písm. a), § 52zzzb ods. 5; ZZP § 10b ods. 1 písm. e) (no health levy on
  dividends from taxed profits); ZDP § 6 ods. 10; ZSP employer rates.
- Lean: the personal side through `sktax` (`dividends` with `skDivProfitYear`, `skReceipts`); company side in Python.
- Status: recreated; also found blind by the generic scanners (income type: dividends +24 % vs wages; owner scan).

### F11 Two tax bases, two 19 % bands
- Kind: loophole-new (structure; not found described as a planning point in the 6 sources read)
- Household: a person with § 5 income and § 6 ods. 1, 2 income (receipts above 100 000 €), each base ≥ 48 441,43 €.
- Amounts: § 4 ods. 1 makes two bases and § 15 písm. a) bod 1 and bod 3 give each its own 176,8 × ŽM threshold: never
  dearer than one base, and up to 6 % × 48 441,43 = 2 906,49 € a year cheaper. (Below 100 000 € of receipts the business
  base is at 15 % anyway.)
- Provisions: ZDP § 4 ods. 1 písm. a), b); § 15 písm. a) bod 1, 3; § 11 ods. 12.
- Lean: `Theorems.two_bases_le_one` (kernel `separate_le_joint`), `Theorems.two_bases_saving`.
- Status: confirmed.

### F12 § 32a zamestnanecká prémia is dead law
- Kind: statute-fault
- Households: every employee.
- Amounts: the premium is 19 % of (21 × ŽM − the § 5 ods. 8 base of 12 minimum wages or more); with contributions of at
  most 13,4 % that base is ≥ 86,6 % × 12 × MW, above 5 753,79 € for any monthly minimum wage ≥ 554 €. The 2025 minimum
  wage is 816 €: the premium is 0 for everyone, yet § 32a (8 subsections, employer duties in ods. 5 and 7) stays in force.
- Provisions: ZDP § 32a ods. 1 písm. a) bod 7 ("suma vypočítaná podľa odseku 3 je kladné číslo"), ods. 3; § 11 ods. 2.
- Lean: `Theorems.premia_dead` (all incomes, all MW ≥ 554 €), `Theorems.premia_2025`.
- Status: confirmed; the year it died (a rough check with 2014/2015 parameters suggests 2015) is not verified.

### F13 Finančná správa's bonus arithmetic: proration of the withdrawal and rounding (reading, not an error)
- Kind: gov-error (classification: reading and convention; not an error; not counted in gov_errors)
- Households: Finančná správa 790897 otázky 4 and 6.
- Amounts: otázka 6 reduces a newborn's 200 € by 426 × 2/12 = 71 € (bonus 129 €); § 33 ods. 11 itself has no proration
  ("nárok na daňový bonus na každé jedno vyživované dieťa sa znižuje o 1/10 rozdielu"), which would leave 0 €; the
  15. 3. 2025 change to ods. 5 (the monthly bonus "podľa odsekov 1, 6 a 11") supports the monthly reading. Otázka 4 rounds
  the monthly cap first (78,54 × 10 = 785,40 €) where § 33 ods. 10 with § 47 on the period gives 785,42 €.
- Provisions: ZDP § 33 ods. 5, 10, 11; § 47.
- Lean: the model follows Finančná správa (`Kid.reduction`, `capMonth`); `Tests.lean` A reproduces both answers.
- Status: reading (129 €) and convention (2 cents); no correction proposed.

### F14 A token salary avoids the self-payer health minimum of a dividend-only owner (lead)
- Kind: loophole-new (lead; not found in the 6 sources read)
- Household: an s.r.o. owner with no other insured activity.
- Amounts: with no salary the owner pays health as a self-payer, 14 % of 715 € = 100,10 € a month (1 201,20 € a year); any
  employment removes the minimum (ZZP § 13 ods. 11 písm. a)) at a contribution cost of 48,6 % of that small wage: about
  950 € a year better at P ≥ 10 000 € (`results/owner_sk.md`, best mix).
- Provisions: ZZP § 11 ods. 2, § 12 ods. 1 písm. e), § 13 ods. 9–11.
- Lean: not in Lean (company side in `tools/owner_sk.py`).
- Status: lead; check the health insurers' practice before relying on it.
