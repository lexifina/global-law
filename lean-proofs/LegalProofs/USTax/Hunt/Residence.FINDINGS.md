# Residence: individuals crossing borders — findings

File: `LegalProofs/USTax/Hunt/Residence.lean` (runs in ~30 s). Recorded outputs: `tools/hunt/out/Residence/*.txt`
(`main_run.txt` is the file's own output; the lettered files are the other scenarios, produced from the same rules by
`gen.py` / `runall.sh`).

Position searched: one individual, salary $300,000 a year that follows the person, one asset with a $1,000,000
long-term built-in gain (basis $500,000), dividend $30,000 a year. Flat rates: ordinary 35% (illustrative), gain 20%
(§1(h)), §1411 3.8%, nonresident 30%. Baseline (in the US every day, sell): **$238,000** on the gain.
Figures: §877A(a)(3) exclusion $890,000 and §911 exclusion $130,000 (2025); §2503(b) $19,000 (2025).

## Provisions encoded (text read with `sec.py`)

| Provision | What the model takes from it |
|---|---|
| §7701(b)(1)(A), (3)(A) | resident if green card at any time in the year, or 31 days and days + ⅓ + ⅙ ≥ 183 |
| §7701(b)(3)(B) | closer-connection exception: under 183 days, foreign tax home all year |
| §7701(b)(3)(D), (5) | exempt-individual (student) days are not days "for purposes of this subsection" |
| §7701(b)(2)(A), (B) | first-year start date; last-year end date (needs closer connection and no residence next year) |
| §7701(b)(6) | ceasing to be a lawful permanent resident |
| §7701(b)(10) + §877(b), (d)(1) | return within 3 calendar years after ≥3 years' residence: interval taxed under §877(b) if more than §871 |
| §871(a)(1)(A), (a)(2), (b) | 30% on US dividends; 30% on US-source gains if present 183 days in the taxable year; ECI salary |
| §865(a), (g)(1), (g)(2) | gain sourced by tax home; citizens/residents foreign-source only if 10% foreign tax paid |
| §897(a) | nonresident's US realty gain taxed as ECI |
| §1411(a), (e)(1) | 3.8% on residents' and citizens' investment income; not on nonresident aliens |
| §877A(a), (g); §877(a)(2), (e)(2) | covered expatriate mark to market, exclusion, basis adjustment; long-term resident = 8 of 15 years; certification test |
| §911(a), (b)(2), (d)(1)(B), (d)(3) | earned income exclusion, 330 days, tax home |
| §901(b), §904(a) | credit for foreign tax, limited to US tax on the foreign income |
| §2501(a)(1)–(2), §2511(a), §2505, §2503(b), §1015 | gifts: residents use the unified credit; nonresident aliens taxed only on US-situs non-intangibles; carryover basis |
| §2801(a), (c), (e) | 40% on a US donee of a covered expatriate |

Read but not modelled: §871(h), (i) (interest), §864, §§931, 933, 937 (possessions; the 10-year rule for pre-move gain is
in regulations), §§2101–2107 and §1014 (death is not a move), §684, §7701(b)(4) first-year election, §7701(b)(2)(C)
10 nominal days, §6013(g)/(h), treaties, states. §4475 (2025 Act remittance tax) read: see traps.

## Search size

Exhaustive depth-first with deduplication. Moves: present / absent for a segment, relocate tax home, sell,
renounce (certify or not), abandon green card (certify or not), gift to US person, gift to nonresident alien.
23 scenario runs (20 lettered files plus three only in `main_run.txt`), 2.63 million positions, 340,000 finished plans in all. Largest: green-card holder with foreign
stock over 3 years, 720,901 positions; fine 5-segment grid over 2 years, 330,000–373,000 positions each.
Grids: fine `[30,90,62,1,182]`, coarse `[30,152,183]`, arrival `[183,182]`, whole years `[365]`.

## Plans that beat the baseline

| # | Plan (as the search printed it) | Gain tax vs $238,000 | US days | Provisions combined | Class |
|---|---|---|---|---|---|
| 1 | Long-term green-card holder (or citizen) gives up the status as a covered expatriate **and stays** in the US as a resident under the day count; sells later | **$26,180** (saves $211,820) | 730/730 | §877A(a)(1)–(3), (g)(2)(B), (g)(1)(C); §7701(b)(3) | CANDIDATE |
| 2 | Same person *below* the wealth and tax tests declines the §877(a)(2)(C) certification, so becomes covered on purpose; US realty then sold as a nonresident | **$26,180** vs $200,000 if certified | any | §877(a)(2)(C), §877A(a), §897 | CANDIDATE |
| 3 | Visa holder (no green card) sells on 1–30 January **while still living in the US**, leaves by day 30 | **$0** | 395/730 | §7701(b)(3)(A)(i) (31 days), §871(a)(2) (183 days), §865(g) | CANDIDATE (weak: consequence of known rules) |
| 4 | Visa holder, **foreign-corporation stock**: one calendar year as a nonresident (closer connection, up to 182 US days), sells, resident again the next year | **$0** | 912/1095 | §7701(b)(3)(B), (b)(10); §877(b), (d)(1)(B) | VARIANT |
| 5 | Visa holder, domestic stock: leaves, sells, returns within 3 years | **$198,505–$200,000** (20%, no §1411) | 912/1095 | §7701(b)(10), §877(b), §1411(e)(1) | VARIANT |
| 6 | Visa holder, domestic stock: out one year, back one year, out one year and sell, back | **$0** | 1460/2190 (3 straight years out: 1095) | §7701(b)(10)(A): 3 consecutive years | VARIANT |
| 7 | Sell after the residency end date in the year of departure | $0 | 548/730 | §7701(b)(2)(B), §865(a)(2) | KNOWN (sell after you leave) |
| 8 | Newcomer present only the last 182 days of the arrival year sells that year | $0 | 547/730 | §7701(b)(3)(A)(ii), §871(a)(2) | KNOWN (arrive after 2 July / pre-immigration sale) |
| 9 | Closer-connection year, sale that year, no return within the window | $0 | 547/730 | §7701(b)(3)(B) | KNOWN (Form 8840) |
| 10 | Green card under 8 years: abandon, leave, sell | $0 | 547/730 | §877(e)(2) | KNOWN (leave before year 8) |
| 11 | Citizen or long-term resident below the tests: certify, leave, sell | $0 | 547/730 | §877A(g)(1) | KNOWN (non-covered expatriation) |
| 12 | Citizen abroad paying 15% foreign tax on the gain | $88,000 | 547/730 | §865(g)(2), §901, §904 | KNOWN (resourcing + credit) |
| 13 | Gift to a nonresident alien who sells | $0, uses $1,481,000 of unified credit | 730/730 | §2501, §1015, §865(a)(2) | KNOWN |
| 14 | US realty sold as a nonresident | $200,000 | 547/730 | §897, §1411(e)(1) | KNOWN |
| 15 | F-1 student: sells in a year with under 183 days of presence | $0 (vs $300,000) | 547/730 | §871(a)(2) | KNOWN |

### Judging 1 and 2 (expatriate and stay; covered on purpose)

Text: §877A(a)(1) deems all property sold the day before; (a)(3) removes $890,000 of the gain; (a)(2) last sentence
adjusts later gain for the deemed gain "determined without regard to paragraph (3)", so basis rises by the excluded
amount too. An "expatriate" is a long-term resident who "ceases to be a lawful permanent resident" (§877A(g)(2)(B));
nothing requires ceasing to be a resident, and (g)(1)(C) expressly contemplates a covered expatriate who is "subject to
tax as a citizen or resident" afterwards (and then switches off §2801 and the withholding rules). Covered status
needs only a failure to certify (§877(a)(2)(C)). Not a model artifact; the model omits the costs below.

What could defeat or spoil it:
* immigration law, not tax: the person needs a new status to stay (a citizen needs a visa; INA §212(a)(10)(E) bars
  re-entry of those who renounced for tax reasons, rarely applied); an abandonment followed at once by a new green card
  invites a sham / substance-over-form argument;
* §877A(e): IRAs, HSAs, 529s are treated as fully distributed; (d)(2) non-eligible deferred compensation is
  accelerated; all other property is marked too (gain above $890,000 is taxed now);
* Notice 2009-85 (not read here): exclusion allocated pro rata across assets and, as I recall, not renewed on a second
  expatriation; §121 does not apply to the deemed sale;
* §2801 applies to gifts and bequests to US persons once the person is no longer taxed as a resident;
* §6039G penalty if Form 8854 is not filed (file it and answer the certification "no");
* §7701(o) is aimed at transactions, not status changes; I found no statutory anti-abuse rule.

Sources checked (2 searches): practitioner pages describe the exclusion and the step-up; none describes staying
resident after the expatriating act or choosing covered status. Not found is not proof of novelty.

### Judging 3 (January window)

In year 2 the person has 30 or fewer days, so is not a resident "with respect to" that calendar year at all
(§7701(b)(3)(A)(i)); year 1 residence ends 31 December. A January sale with a US tax home is US-source (§865(g)(1)(A)(i)(II))
but §871(a)(2) needs 183 days in the year. One day earlier (31 December) the same sale costs $238,000.
Difference from the known "sell after you leave": the sale happens before the person is resident anywhere else, so the
destination country's tax on the gain is avoided too. Defeated by: holding a green card (resident if a permanent
resident at any time in the year); returning within 3 calendar years (§7701(b)(10): 20% on domestic stock); state
residence rules; a regulation I could not read locally. 2 searches found no write-up of it.

### Judging 4–6 (§7701(b)(10))

Known rule (Hodgen, "Leave the USA, cash in, and come back? Here's a gotcha"): the return within 3 years taxes
gain on US stock. The search adds three consequences of the text: (4) §877(b) gross income is §872(a) as modified by
§877(d), and (d)(1)(B) reaches only stock "issued by a domestic corporation", so foreign-corporation stock sold with a
foreign tax home is outside it; (5) the charge is "as provided in section 1 or 55", and §1411 does not apply to a
nonresident alien, so even the caught case costs 20% and not 23.8%; (6) the rule needs a residency period of 3
consecutive calendar years, and a one-year return starts a new period of one year, so the second absence is not caught
(Reg. §301.7701(b)-5, seen in a search snippet: also requires 183 days of residence in each of the three years, and
measures from the termination date of the initial period). Defeats: (4) PFIC stock (Prop. Reg. §1.1291-3(b)(2)
treats becoming a nonresident as a disposition), CFC stock (§877(d)(1)(C)), an exchange of US for foreign property
during the interval (§877(d)(2)); the closer-connection year with 182 US days and a US home before and after is a
weak fact pattern; a full year away is safer. (6) each leg is a real move of a year.

## Traps the search hit

* **§871(a)(2) counts every physical day of the taxable year**, including exempt-individual days (§7701(b)(3)(D)
  is "for purposes of this subsection") and the resident part of a split year. A student in the US all year, or
  anyone who sells as a nonresident with a US tax home in a year with 183 days, pays 30% = **$300,000**, more than a
  resident (23.8%), with no loss carryover.
* 31 December vs 1 January sale: $238,000 (plan 3).
* Returning in the 3rd calendar year instead of the 4th: $198,505 (plan 5).
* Green-card holder: resident for any year in which the card is held on any day, so plans 3 and 9 are closed unless
  the card is given up first; from the 8th year that triggers §877A.
* Covered expatriate who certifies nothing and leaves with domestic stock: pays $26,180 where a non-covered
  leaver pays $0.
* A nonresident alien's gift of US realty: 40% from the first dollar above $19,000 (no §2505 credit); a covered
  expatriate's gift of stock to a US person: §2801 at 40%.
* §4475 remittance tax: 1%, but only where the sender hands over cash, a money order or a cashier's check; a
  transfer from a US bank account or US-issued card is outside it ((c), (d)). No plan here is touched.

## Drafting gaps noticed

* §877A(g)(2)(B): "expatriate" does not require ceasing to be a resident; §877(a)(2)(C) lets anyone opt into covered
  status. The exclusion was written as relief from a penalty and works as an elective $890,000 step-up.
* §2501(a)(3) and (a)(5), §2107, §877(e)(1) still key on "a donor/decedent to whom section 877(b) applies", but
  §877(h) switches §877 off for expatriations after 16 June 2008: dead letters for new expatriates. §7701(b)(10)
  still borrows §877(b) and is the only living use.
* §7701(b)(10) borrows the 1966-era §877(d) source list: domestic stock and US-situs property only.
* §7701(b)(10) says "section 1 or 55"; chapter 2A (§1411) is not mentioned.
* §871(a)(2) has its own undefined "present ... 183 days", not tied to §7701(b)(7) or (b)(3)(D).
* Tax home: §7701(b)(3)(B) and §937 use §911(d)(3) "without regard to the second sentence"; §865(g) uses it with
  the second sentence. The same person can have a foreign tax home for one and not the other.
* §4475(d) exempts what (c) already excludes; "sender" is borrowed from the Electronic Fund Transfer Act and does not
  turn on citizenship or residence.
* §1014(b)(1) is not conditioned on estate-tax inclusion: a nonresident decedent's foreign assets get a new basis.

## Model limits

Tax home and closer connection are one fact; domicile for gift tax is the same fact. Flat rates. No growth. The
year after the horizon is assumed spent abroad, which favours selling in the last year (plans 7, 9). Day grids are
whole segments. Regulations and Notice 2009-85 were not available locally.
