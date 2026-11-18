# Five tax systems in Lean: the shared contract

Goal (set on 2026-11-18): compare the US, French, UK, German and Japanese tax systems head to head through Lean
formalisms, to understand the pros and cons of each system and why and how tax systems are written. Blog post:
"Comparing 5 tax systems formally with Lean". Common tax year: **2025** (US TY2025; France income 2025; UK 2025-26;
Germany VZ 2025; Japan 令和7年分). Earlier years only if cheap and useful.

## Layout
- `uk` (the model is [`../../official-checks/uk-model`](../../official-checks/uk-model)), `de`, `jp`: one country
  each. `lean/` is its own Lake project (Lean 4.35, core only, no Mathlib). Lib names `UkTax`, `DeTax`, `JpTax`; exe
  names `uktax`, `detax`, `jptax`. Each has a `FINDINGS.md`.
- `compare`: the comparison and its harness, with the US and French adapters.
- Existing models: US [`../../TaxCode/Individual`](../../TaxCode/Individual) (TY2025, `Household.lean`, `Run.lean`);
  France [`../../FrTax`](../../FrTax) (exe `frtax`, `id;year;BOX=val,...`), reports in `../../FrTax/reports`.
- Style: the French model (`FrTax/*.lean`, `FrTax/reports/FINDINGS.md`, `FrTax/reports/RESULTS.md`) and the US brief
  [`../../TaxCode/Individual/BRIEF.md`](../../TaxCode/Individual/BRIEF.md): copy the statute provision by provision, each definition
  citing its section and quoting a short phrase; whole currency units (Int) and basis points; the statute's own
  rounding; test against official worked examples and an independent referee; prove properties for all inputs; record
  every disagreement and who is right, with the authority.

## The canonical household (input), one JSON object per line (JSONL), amounts in whole units of local currency
{"id": "h1", "year": 2025,
 "adults": [{"age": 40, "wages": 50000, "selfEmployment": 0, "pension": 0}, ...],   // 1 or 2 adults
 "married": true,                       // the two adults are married / civil partners (filing jointly where allowed)
 "children": [{"age": 7}, ...],         // dependent children living with the household
 "interest": 0, "dividends": 0, "capitalGains": 0,   // household totals, domestic, long-held listed shares
 "rentalIncome": 0, "charitable": 0, "pensionContributions": 0}
Each country decides how these map to its own law (e.g. which spouse holds investment income: split equally).
Missing a feature is fine; say so in `"unsupported"`.

## Output (one JSON object per line, same order)
{"id": "h1", "country": "UK", "currency": "GBP",
 "incomeTax": 0,          // central-government income tax after reliefs and credits (refundable credits negative)
 "surtaxes": {},          // named add-ons to income tax: Soli, 復興特別所得税, CEHR/CDHR, NIIT, Additional Medicare...
 "localIncomeTax": 0,     // income tax to regions/municipalities (Japan 住民税; 0 where none or not modelled)
 "employeeSocial": 0,     // employee social contributions on earnings (NI, FICA, SV, 社会保険, CSG/CRDS...)
 "benefits": 0,           // universal cash child benefits paid (Kindergeld, UK Child Benefit net of HICBC...)
 "detail": {...},         // country-specific lines (taxable income, allowances, rates)
 "unsupported": []}
Net income = gross − incomeTax − sum(surtaxes) − localIncomeTax − employeeSocial + benefits.
Employee social contributions may be modelled at statutory rates and ceilings for an ordinary employee (state the
simplifications); the income tax must be the full statute.

## Rules the models follow
- Primary sources: the statute and official guidance (legislation.gov.uk API, gesetze-im-internet.de, e-Gov 法令API
  laws.e-gov.go.jp, HMRC/BMF/NTA pages and PDFs). Do not bypass bot protection or logins. Official calculators may be
  queried politely: sequential, >= 1 s apart.
- Never invent a worked example or a figure; cite page/section for each test value.
- Only Lean 4.35 core. Each model builds with `lake build` inside its own project.
