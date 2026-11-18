# UK model: interface example (`uktax`)

Build and run (on lean1):

    cd ~/cmp/uk/lean && export PATH=$HOME/.elan/bin:$PATH && lake build
    ./.lake/build/bin/uktax households.jsonl > out.jsonl        # or: ... | ./.lake/build/bin/uktax
    ./.lake/build/bin/uktax --literal households.jsonl          # statute read literally (FINDINGS F1, F2)

Input: the canonical household of `~/cmp/shared/CONTRACT.md`, one JSON object per line. Output: one contract object
per line, same order. ~0.1 ms per household.

## Conventions (read before comparing)

| Field | UK meaning |
|---|---|
| `incomeTax` | Sum over adults of the ITA 2007 s. 23 liability (Steps 1-7, incl. marriage allowance, MCA, Gift Aid charge; **without** the HICBC) **less** the basic-rate relief at source on pension contributions (FA 2004 s. 192(1): 20 % of the gross contribution, paid into the pension by HMRC). Can be negative (a non-taxpayer contributing). The pure HMRC liability is `detail.liabilityITA2007s23`. |
| `surtaxes` | `{"capitalGainsTax": x}` when there are taxable gains. CGT is a separate tax in the UK (TCGA 1992 s. 1H-1K: £3,000 exempt, 18 % / 24 %). Add it to `incomeTax` to compare with countries that tax gains inside the income tax. Otherwise empty. |
| `localIncomeTax` | 0 (rUK rates; Wales's rates equal rUK's in 2025-26; Scotland not modelled). |
| `employeeSocial` | Class 1 primary NI (8 % / 2 %, annual earnings period: thresholds £12,570 / £50,270) + Class 4 (6 % / 2 %, same limits). Class 2 is nil (treated as paid above £6,845). None from age 66 (pensionable age). |
| `benefits` | Child Benefit (£26.05 eldest + £17.25 others a week, 52 weeks) **net of** the High Income Child Benefit Charge (ITEPA 2003 s. 681B-681H: 1 % per £200 of the higher partner's adjusted net income above £60,000). Gross CB and the charge are in `detail.childBenefit`, `detail.hicbc`. |
| money | pounds with pence (two decimals at most). |

Mapping of the household (see `lean/UkTax/Household.lean`):
- Adults are taxed separately. `interest`, `dividends`, `capitalGains`, `rentalIncome` split equally between two
  adults (first adult takes an odd pound). `age` is read as age on 6 April 2025.
- `charitable` = Gift Aid donations (amount paid), made by the adult with the larger income: bands extended and
  adjusted net income reduced by the grossed-up gift (x 1.25).
- `pensionContributions` = **gross** relief-at-source personal pension contributions (the amount credited to the
  pension; the member pays 80 %), shared in proportion to earnings; relief capped at max(£3,600, earnings).
- `rentalIncome`, `selfEmployment` are profits (no £1,000 property/trading allowance applied).
- Two adults are partners for the HICBC (married or not); only a married couple gets the marriage allowance, chosen
  in the direction that minimises the couple's tax. Married couple's allowance when an adult is 90 or over.
- Children under 20 count for Child Benefit (16-19 assumed in education).
- Optional extension: `"blind": true` on an adult (blind person's allowance, s. 38-39).
- Optional extension: `"region": "scotland"` on the household: the adults are Scottish taxpayers (Scottish rates
  and bands on non-savings income, ITA 2007 s. 11A); default England, Wales and Northern Ireland.
- Switches (statute readings, see FINDINGS.md): `--literal`, `--psa-literal`, `--ras-literal`, `--ras-unconditional`;
  `--pe` reproduces PolicyEngine-UK's conventions (for testing only).

## Example

Input line 1:

    {"id": "h1", "year": 2025, "adults": [{"age": 40, "wages": 50000, "selfEmployment": 0, "pension": 0}], "married": false, "children": [], "interest": 0, "dividends": 0, "capitalGains": 0, "rentalIncome": 0, "charitable": 0, "pensionContributions": 0}

Output (excerpt; the full line also has per-adult detail: allowances, bands, PSA, NI, CGT):

    {"id": "h1", "country": "UK", "currency": "GBP", "incomeTax": 7486, "surtaxes": {}, "localIncomeTax": 0, "employeeSocial": 2994.4, "benefits": 0, "unsupported": [], "detail (excerpt)": {"liabilityITA2007s23": 7486, "reliefAtSource": 0, "childBenefit": 0, "hicbc": 0, "hicbcPayer": null, "election": "none"}}

Input line 2:

    {"id": "h2", "year": 2025, "adults": [{"age": 40, "wages": 70000, "selfEmployment": 0, "pension": 0}, {"age": 38, "wages": 11500, "selfEmployment": 0, "pension": 0}], "married": true, "children": [{"age": 7}, {"age": 4}], "interest": 2000, "dividends": 3000, "capitalGains": 10000, "rentalIncome": 0, "charitable": 500, "pensionContributions": 4000}

Output (excerpt; the full line also has per-adult detail: allowances, bands, PSA, NI, CGT):

    {"id": "h2", "country": "UK", "currency": "GBP", "incomeTax": 14357.5, "surtaxes": {"capitalGainsTax": 840}, "localIncomeTax": 0, "employeeSocial": 3410.6, "benefits": 1306.6, "unsupported": [], "detail (excerpt)": {"liabilityITA2007s23": 15157.5, "reliefAtSource": 800, "childBenefit": 2251.6, "hicbc": 945, "hicbcPayer": 1, "election": "none"}}

Input line 3:

    {"id": "h3", "year": 2025, "adults": [{"age": 40, "wages": 30000, "selfEmployment": 0, "pension": 0}, {"age": 38, "wages": 11500, "selfEmployment": 0, "pension": 0}], "married": true, "children": [{"age": 3}], "interest": 0, "dividends": 0, "capitalGains": 0, "rentalIncome": 0, "charitable": 0, "pensionContributions": 0}

Output (excerpt; the full line also has per-adult detail: allowances, bands, PSA, NI, CGT):

    {"id": "h3", "country": "UK", "currency": "GBP", "incomeTax": 3272, "surtaxes": {}, "localIncomeTax": 0, "employeeSocial": 1394.4, "benefits": 1354.6, "unsupported": [], "detail (excerpt)": {"liabilityITA2007s23": 3272, "reliefAtSource": 0, "childBenefit": 1354.6, "hicbc": 0, "hicbcPayer": null, "election": "marriage allowance 2\u21921"}}

Hand check of line 2: adult 1 has wages £70,000, half the interest/dividends/gains (£1,000 / £1,500 / £5,000),
the Gift Aid (£500 paid, £625 gross) and £3,435 of the pension contribution (70,000/81,500 of £4,000). Adjusted net
income 72,500 - 625 - 3,435 = £68,440; basic rate limit 37,700 + 625 + 3,435 = £41,760; tax 41,760 x 20 % +
15,670 x 40 % + 500 x 40 % (savings above the £500 allowance) + 1,000 x 33.75 % (dividends above £500) =
£15,157.50; CGT (5,000 - 3,000) x 24 % = £480; Class 1 (50,270 - 12,570) x 8 % + (70,000 - 50,270) x 2 % = £3,410.60.
HICBC on adult 1: floor((68,440 - 60,000)/200) = 42 %, of £2,251 (two children, 52 x £43.30 rounded down) = £945.
