# Estonia (EE) 2025: findings

Model: `lean/EeTax` (Lean 4.35 + TaxKernel), exe `eetax`. Amounts in euro (the model computes in cents, as EMTA
does). "Burden" = income tax + unemployment insurance (1.6 %) + II pillar (2 % default) + an FIE's social tax − family
benefits. Every Lean name builds with no `sorry` and no `native_decide` (`#print axioms`: the concrete findings use
no axioms; the general theorems propext, Classical.choice, Quot.sound). Statute: TuMS = Tulumaksuseadus, redaction
RT I 20.12.2024, 5 (https://www.riigiteataja.ee/akt/120122024005, in force 1.1–31.8.2025; the 1.9 and 1.10.2025
redactions change nothing modelled); SMS 127092024008, KoPS 103122024015, TKindlS 106072023111 + regulation
124092024004, PHS 112122024013/108042025002 (texts in `refs/`, fetched from the Riigi Teataja public API).

Sources searched for "is it known" (N = 9): EMTA *2025. aasta maksumuudatused*, *Maksuvaba tulu arvestamine*,
*Maksuvaba tulu vanaduspensionieas*, *Tulumaks ja maksuvaba tulu* (employer), *Dividendide ja omakapitali
väljamaksete maksustamine*, *Väärtpaberid ja investeerimiskonto* (all `refs/emta/`, fetched 2026-11-19); Sander,
Kantšukov & Buldas (2010) (`refs/lit/tpep892.txt`); the e-Residency tax guide (search snippet only); two web
searches (security-tax repeal; owner-manager dividends literature).

### F1 The OECD models the Estonian worker without the II-pillar contribution
- kind: gov-error (checked) — classification: **convention**
- households: all eight OECD Taxing Wages types (AW 25,603.16)
- amounts: OECD EECSSC = 1.6 % of gross exactly (S100: 409.65 = unemployment insurance only) and CGTC = gross − 1.6 %
  (S100 25,193.51), i.e. no 2 % II-pillar payment and no § 28^1(1) deduction of it. With the statutory default 2 %
  (KoPS § 9(1) "Makse määr on 2%"), take-home pay is 400 lower at S100 (512.06 paid, 112.65 less tax).
- provisions: KoPS § 7(3), § 9(1)-(2); TuMS § 28^1(1).
- model: `incomeTax`/`employeeSocial` keep the statutory 2 %; `detail.oecdNoPillar2_*` recompute with 0 % and
  `oecd_map.py` compares those: **48/48 mapped lines exact** (in cents within 0.01: `oecd_S100`, `oecd_S67`). Since
  2021 a member may stop paying (KoPS § 27^3), so the OECD worker is a legal case, but not the statutory default.
- Lean: `EeTax.oecd_S100`, `oecd_S67`. status: explained.

### F2 The OECD gives the single parent the single-parent child allowance, which the statute restricts
- kind: gov-error (checked) — classification: **reading** (favourable assumption)
- households: SP67 (single parent, two children): OECD CTGG 3,840 = 2 × 80 × 12 child allowance + 2 × 80 × 12
  üksikvanema lapse toetus.
- provisions: PHS § 19(1): only for a child "kelle sünniaktis või rahvastikuregistrisse kantud perekonnaseisuandmetes
  puuduvad andmed isa või teise vanema kohta või kelle vanem on … tunnistatud tagaotsitavaks"; the child of a
  divorced or separated parent does not qualify.
- model: paid only with the input flag `otherParentUnrecorded`; `detail.singleParentAllowanceIfEligible` (1,920 for
  SP67) is added by `oecd_map.py`. status: explained.

### F3 The tax hump: 37.99 % income tax (40.8 % with contributions) on 14,400–25,200 euro
- kind: loophole-known (the formula is published; the proved band rate and its non-stacking are the contribution)
- households: any resident below pension age with annual "tulu" of 14,400–25,200 (0.56–0.98 AW)
- amounts: 100 more euro of wages cost 37.20 income tax + 3.60 contributions (`hump_wages_100`, `hump_wages_social`):
  METR 40.8 % (employee), 55.7 % as a wedge on labour cost (33.8 % employer). Pure income tax on fully taxable income:
  22 % × 259/150 = 37.99 % for every 1.50-euro step in the band (`hump_marginal`, from the kernel's
  `Taper.taper_marginal`). The generic METR scanner finds exactly this band (14,389–25,245, avg 40.7 %) and nothing
  else above the 25 % top rate; family benefits (PHS) are not income-tested, so nothing stacks on it
  (`runs/notches.md` §1: same band for single, single parent, one-earner couple with 3 children; benefits constant).
- provisions: TuMS § 23(1)-(2) ("7848 – 7848 / 10 800 × (tulu summa – 14 400)"), § 4(1).
- Lean: `EeTax.hump_marginal`, `hump_gt_rate`, `exemption_bandEnd`, `exemption_zero_above`, `exemption_full_below`,
  `hump_wages_100`. status: confirmed; abolished from 1.1.2026 (F18).

### F4 Untaxed Estonian dividends switch off the basic exemption: up to 1,726.56 euro, 34.5 % on the profit
- kind: loophole-new (that dividends count is in § 23(3) and EMTA's list; the resulting rates, the routing gain and
  the interaction with owner-manager pay were not found in 9 sources searched)
- households: a person with wages/pension/interest of up to 25,200 who also receives Estonian dividends
- amounts: wages 14,400 + net dividend 10,800: the dividend bears no personal tax (§ 12(2)) and 3,046.15 of company
  CIT, yet the person's income tax rises by 1,726.56 because the whole 7,848 exemption is withdrawn (`dividend_hump`).
  Per euro of net dividend inside the band: 0.22 × 109/150 = 16.0 cents; on the gross profit 22 % + 0.78 × 16.0 % =
  **34.47 %** instead of 22 % (`runs/notches.md` §2). An owner who pays herself a fee up to the exemption and takes the
  rest as dividends loses the exemption on the fee as soon as fee + dividend > 14,400. Gains: route the dividend to a
  family shareholder with no other taxable income (no personal effect at all), bunch dividends into alternate years
  (F5), or (for 2025) into 2026 (F12).
- provisions: TuMS § 23(3) ("Tuluna lõike 2 tähenduses käsitatakse … ka … §-s 50 nimetatud, füüsilise isiku
  tasemel täiendavalt maksustamata tulu"), § 12(2), § 50(1), § 4(1^1). EMTA (*Maksuvaba tulu arvestamine*): "Eesti
  äriühingult saadud dividend … mis on äriühingu tasandil maksustatud tavamääraga 22/78" counts.
- Lean: `EeTax.dividend_hump`, `dividend_cit`. status: confirmed by model and statute.

### F5 Timing across the hump: 1,726.57 euro per pair of years
- kind: loophole-known in principle (annual test), recreated blind by the kernel timing scanner
- households: income that can be moved between years (bonus, FIE profit, capital gain, dividend, III-pillar payout)
- amounts: two years of 25,200 vs 36,000 + 14,400: 1,726.57 less income tax (`bunching_gain`); scanner's best case
  1,730 (6.8 % AW) for a single at 27,907 a year; `runs/notches.md` §3: 576 at a two-year total of 43,200, 1,726–1,728
  from 50,400 up; nothing at or below 36,000.
- provisions: TuMS § 23(2), § 36(1) (cash basis: "tulu … võetakse … arvesse sellel maksustamisperioodil, millal
  tulu laekus"). Lean: `EeTax.bunching_gain`. status: confirmed.

### F6 Owner-manager: all dividends, 22 % at every profit level, against 43.8 % through salary
- kind: loophole-known (Sander et al. 2010: replacement of labour income with dividends is "widespread")
- households: one-person OÜ, profit 0.5–10 AW, all paid out (kernel `owner.py`; company side 22 % CIT, 33.8 % employer)
- amounts: total tax 22.0 % with dividends at every level vs 30.3 % (0.5 AW) to 43.8 % (≥ 2 AW) with salary; gain
  4,613 at 1 AW, 55,822 at 10 AW (`results/search/owner.md`). As a management-board fee (no UI, TKindlS § 3(2) p3):
  902 / 4,304 / 10,511 at 0.5 / 1 / 2 AW (`runs/recreate.md` L01).
- provisions: SMS § 2(1) p4, § 7(1) (33 % on fees, none on dividends), TuMS § 50(1), § 12(2); KoPS § 7(1) (II pillar on
  fees only). Counter: EMTA may treat dividends paid for work as pay (e-Residency guide; no specific statutory rule
  found). status: confirmed.

### F7 Retained profit earns its return untaxed until distribution
- kind: loophole-known (the design: "maksab tulumaksu … jaotatud kasumilt nende väljamaksmisel", § 50(1))
- households: owner-manager who does not need the profit now (owner.py pays all out; this is `tools/retention.py`)
- amounts: per euro of pre-tax profit at 5 % for 20 years: retained 2.07, paid out to an investment account 1.79, to
  an ordinary account 1.68 (tax on the return 0 % / 22 % / 30.5 %); as a board fee 1.32. R ≥ I ≥ D for every r > 0,
  n ≥ 1 (cash-flow tax: 22 % of the final distribution = 22 % of the profit grown at the pre-tax return).
- provisions: TuMS § 50(1), § 4(1^1), § 17^2, § 15, § 17. status: confirmed (`runs/retention.md`).

### F8 OÜ instead of FIE
- kind: loophole-known. households: business profit 15,000 / 30,000 / 60,000. amounts: saving 1,352 / 5,736 / 12,315
  (FIE: 33 % social tax on profit/1.33 with a 9,840 minimum base, II pillar 2 %; OÜ: 22 % CIT on distribution).
- provisions: TuMS § 14(5^3)-(5^5), SMS § 2(1) p5, § 2(5), § 7(1). Lean: `EeTax.fie`. status: confirmed.

### F9 Monthly withholding against the annual return: refunds up to 1,726.57, bills up to 1,582.68
- kind: loophole-new (cash-flow trap; the mechanism is published by EMTA, the bounds and their frequency were not
  found in 9 sources searched)
- households: employees with uneven pay from the one payer holding the exemption application
- amounts: the monthly formula is exactly the annual one / 12 (`monthly_even_bounds`: 12 × monthly exemption within
  0–11 cents of the annual one), so an even salary settles to zero; 11 × 1,200 + a 12,000 December bonus leaves a
  **bill of 1,582.64** (`bonus_bill`; the maximum is 11 × 654 × 22 % = 1,582.68); six months of 2,100 then nothing a
  **refund of 1,726.57** (`halfyear_refund`; the maximum, the year's whole exemption at 22 %); starting work in July
  at 2,500 a month: refund 1,631. Of 3,060 patterns (k months at m + a bonus) 66 % settle by more than 1 euro. Two
  payers both applying the exemption (forbidden by § 42(2), warned against by EMTA): bill 3,262 at 2 × 1,000 a month
  (`runs/notches.md` §4).
- provisions: TuMS § 42(1) ("654 – 654 / 900 × (väljamakse – 1200)"), § 42(2), § 23(2), § 46.
- Lean: `EeTax.monthly_even_bounds`, `bonus_bill`, `halfyear_refund`; `EeTax.yearSettlement`. status: confirmed.

### F10 Reaching pension age: same wages, 1,849.06 less income tax (2,756 less burden at 25,200)
- kind: loophole-known (catalogue L12). households: an employee aged 64 vs 65 (pension age) with the same wages.
- amounts: at 25,200: income tax 5,344.42 → 3,495.36 (`pension_age_switch`), plus no UI (TKindlS § 3(2) p5) and (model
  assumption) no II pillar once payouts start; 2,891 at 30,000; 3,734 at 60,000 (`runs/notches.md` §5). The 9,312
  pension-age exemption is never withdrawn; the general one is gone above 25,200.
- provisions: TuMS § 23^5(1), § 23(1) last sentence. Lean: `EeTax.pension_age_switch`. status: confirmed.

### F11 The FIE entry notch: 3,247.20 of social tax from the first euro of profit
- kind: loophole-known (minimum published: EMTA "kuumäär 820 eurot ja sotsiaalmaks 270,60 eurot")
- households: a registered sole trader with small profit and no exception under SMS § 2(5)-(10)
- amounts: profit 1 euro → social tax 3,247.20 (`fie_entry`); net income negative until 3,247; the floor stops binding
  at 13,087 of profit. Escape routes: ELMS business account or an OÜ (catalogue L03, L14).
- provisions: SMS § 2(5), § 2^1, § 7(1). Lean: `EeTax.fie_entry`. status: confirmed.

### F12 Paying in January 2026 instead of December 2025: up to 1,727 euro
- kind: loophole-new (cross-year timing at the hump's abolition; not found in 9 sources searched)
- households: anyone whose 2025 income was in or near the band and who could move a payment by a few days
- amounts (two-year burden, `runs/cross2026.md`): salary 20,000 + bonus 5,000: 800; salary 16,000 + bonus 9,200: 1,470;
  wages 14,400 + an Estonian dividend 10,800: 1,727 (counted in 2025 it kills the 2025 exemption; in 2026 the 8,400
  exemption is flat); capital gain 10,000 on wages 15,000: 1,598. Nothing outside 14,400–25,200 + the payment.
- provisions: TuMS § 23 in redactions 120122024005 (2025) and 118122025017 (2026: "maksuvaba tulu 8400 eurot"),
  § 36(1). Lean: input `"year": 2026` (`Params.exemption2026`). status: confirmed (past for 2025; the same logic applies
  to any income-tested exemption that is announced to end).

### F13 § 13(3) p7: the tax-free birth benefit is "5/12 of the person's basic exemption (§ 23)", which the 2018 hump made income-dependent
- kind: statute-fault (amount reference not updated when the related provision changed); EMTA's reading is a
  **convention** in the taxpayer's favour
- households: an employee who receives an employer's birth benefit (lapse sünni toetus) and earns ≥ 25,200, or is of
  pension age
- amounts: "toetust, mis ei ületa 5/12 residendist füüsilise isiku maksustamisperioodi maksuvabast tulust (§ 23)"
  (RT I 11.07.2014, 5) was written for a flat exemption; since 2018 § 23 gives 0 above 25,200, so read literally the
  tax-free cap is 0 for such a parent and cannot be known when the benefit is paid (it depends on the year's income);
  a pension-age employee has no § 23 exemption at all (§ 23^5 instead). EMTA applies a fixed 3,270 (5 × 654) to
  everyone ("3270 eurot (5 × 654) kuni 31. detsembrini 2025"): 719.40 of income tax per benefit for a parent above
  the hump. Unchanged in the 2026 and 2027 redactions (where § 23 is flat again, so the gap closes from 2026).
- provisions: TuMS § 13(3) p7, § 23(1)-(2), § 23^5; EMTA *Tulumaks ja maksuvaba tulu* (`refs/emta/tulumaks-ja-maksuvaba-tulu.txt`).
- status: confirmed by text. Draft issue: "§ 13(3) p7 should name a fixed amount (5/12 of the § 23(1) amount) rather than
  the person's own exemption for the period".

### F14 § 4(1^1)'s exception "välja arvatud käesoleva paragrahvi lõikes 5 nimetatud juhul" has pointed at nothing since 2025
- kind: statute-fault (stale cross-reference, harmless)
- Until 2024 § 4(5) covered § 47^1 and § 50^1 (14 %, divisor 0,86) and the exception kept the 0,80 divisor off the
  14/86 dividends. From 1.1.2025 § 4(5) reads only "Paragrahvis 47^1 nimetatud juhul on tulumaksu määr 18%", and
  § 47^1 (credit institutions' advance payments on profit) is none of the § 1(2)-(4), (6)-(8) objects to which § 4(1^1)
  applies: the exception is vacuous. Still in the 2026 and 2027 redactions. status: confirmed.

### F15 Ranges and transitional rules that still name repealed provisions
- kind: statute-fault (cosmetic). § 57^1(6) "Lõigetes 1–5^3 nimetatud deklaratsioonid …" while § 57^1(1) is "Kehtetu"
  from 1.1.2025; § 61(24) refers to "§ 57^2 lõikes 1" (§ 57^2 repealed); § 61(37) to "§ 17 lõike 3 punktis 1"
  (repealed). `tools/xref.py` resolves every internal reference of the 2025 text: these are the only dangling ones apart
  from the deliberate references to the repealed § 50^1 in § 61(67^2), (68), (71) (`runs/xref_tums_2025.tsv`).
  Cross-act references SMS/KoPS/TKindlS/PHS → TuMS all resolve (`tools/xact.py`). status: confirmed.

### F16 The 2025–2028 unemployment-insurance regulation misquotes the title of the regulation it repeals
- kind: gov-error (cosmetic). Regulation RT I 24.09.2024, 4 § 2(1): "määrus nr 88 „Kindlustatu ja tööandaja
  töötuskindlustusmakse määrad aastatel 2024–2027” tunnistatakse kehtetuks"; the repealed regulation (RT I 03.10.2023,
  19) is titled "Kindlustatu ja tööandja …". No effect on the rates (1.6 % / 0.8 %). status: confirmed
  (`refs/reg_124092024004.xml`, `refs/reg_103102023019.xml`).

### F17 EMTA's description of the 2025 hump income quotes 2024 rates
- kind: gov-error (stale guidance, immaterial). EMTA *Maksuvaba tulu arvestamine*, "Maksuvaba tulu arvestamine 2025.
  aasta lõpuni", counts "täiendava kogumispensioni (III samba) väljamakse, mis on maksustatud maksumääraga 20%" and
  "dividend, millelt on kinnipeetud tulumaks 7%": for 2025 the rate is 22 % (§ 4(1)) and the 7 % withholding (§ 4(4)) and
  14/86 dividends (§ 50^1) were repealed from 1.1.2025. The amounts counted are unaffected. status: confirmed.

### F18 Versioned law 2023–2026: the hump's abolition postponed, a 24 % rate and a security tax enacted and never applied
- kind: statute history (checked; no fault)
- RT I 30.06.2023, 107 set 22 % and 22/78 from 1.1.2025 and the flat exemption; RT I 20.12.2024, 2 moved the § 23
  change to 1.1.2026 ("jõustumine muudetud"), so 2025 kept the hump (EMTA: "„Maksuküür“ jääb kehtima ka 2025. aastal").
  RT I 08.07.2025, 1 (adopted 18.6.2025) repealed the Security Tax Act and enacted 24 % / divisor 0,76 from 1.1.2026
  (§ 3); the redaction in force on 1.1.2026 (118122025017) still reads 22 % with the 2023 amendment mark, so § 3 was
  repealed before entry into force (the repealing act was not identified within the search budget). § 61(71) orders
  the Ministry of Finance to analyse in 2028 the effects of changing §§ 4 and 23 and repealing § 50^1. status: confirmed.

### F19 II- and III-pillar payments do not reduce the hump income
- kind: reading (trap). households: a contributor in the band. amounts: a 1,000 III-pillar payment saves 220 (22 %), not
  380: § 23(2) tests "tulu", income before the deductions of §§ 26-28^1. Evidence: the OECD's S67 line withdraws the
  exemption on gross wages (BTA 5,846.68 = 7,848 − 109/150 × (17,154.12 − 14,400)), not on wages less the 1.6 % UI it
  deducts, and EMTA's list names gross income types only. Lean: `EeTax.person`; `oecd_S67`. status: model reading,
  consistent with OECD and EMTA.

### F20 Model fixes during the work
- kind: model-fix. (a) An FIE's II-pillar payment is on the actual SMS § 2(1) p5 income, not the § 2(5) minimum base
  (KoPS § 11(2^1)); (b) social tax above the business income is carried forward (TuMS § 14(5^4), § 35), not set against
  wages. Both corrected before the final runs.
