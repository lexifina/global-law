S = dict(cc="LK", family_name="5111 Value added tax",
doc=r'''# Sri Lanka 2025: value added tax (5111); SSCL and excise not modelled

Source: Value Added Tax Act, No. 14 of 2002, IRD consolidated text "incorporating amendments up to 2025" (26 Dec 2025;
each amendment with its Act and effective date), and the Value Added Tax (Amendment) Act, No. 4 of 2025 (certified
11 Apr 2025) itself (ird.gov.lk `publications/Value Added Tax_Acts/`; `lk/law/lk_vat_cons2025.pdf`,
`lk/law/lk_vat_04_2025.pdf`, sha256 in `SHA256SUMS`).
* **s. 2 (1) (ix)**: "for any taxable period commencing on or after January 1, 2024 at the rate of eighteen per centum
  (of which the tax fraction is 9/59)" (s. 2 (3) of Act 16 of 2024).
* **s. 10 (viii)**: registration where taxable supplies in the twelve months exceed sixty million rupees (or fifteen
  million in a taxable period): threshold 60 000 000.
* **First Schedule Part III** (taxable periods from 1 Jan 2024; Act 32 of 2023, as amended by Act 4 of 2025 s. 14):
  (a) (i) wheat and wheat flour, (iii) prescribed pharmaceuticals, (vi) kerosene; (b) (i) educational services,
  (ii) public passenger transport (not air, water, tourist or taxi), (iii) electricity, (viii) financial services
  (accounts, currency exchange, loans, securities; life insurance only), (ix) healthcare services other than hospital
  room charges, (x) Special Commodity Levy articles, (xii) locally made rice, rice flour and bread, (xiii) unprocessed
  local agricultural and fishing products, (xxv) liquid milk and yoghurt from local fresh milk.
* Residential letting is not in Part III (Part II item (xi) (e) already excluded lease or rent from 1 Jan 2023):
  standard-rated.''',
vat=dict(name="Value added tax", standard=1800, threshold=60000000, statute="VAT Act No. 14 of 2002 s. 2 (1) (ix) (18 %), s. 10 (viii) (Rs 60 million), First Schedule Part III",
  classes={"food":"exempt","medicines":"exempt","health":"exempt","education":"exempt","transport":"exempt","electricity":"exempt","financial":"exempt","heatingOil":"exempt"}),
notes=["LK 5111: VAT Act No. 14 of 2002, IRD consolidation to 2025 + Amendment Act No. 4 of 2025 (rate 18 % from 1 Jan 2024; First Schedule Part III)"],
unsupported=[[["food"],"food is modelled as exempt: rice, bread, wheat flour, unprocessed local produce and fish, local liquid milk and Special Commodity Levy articles are exempt (First Schedule Part III (a) (i), (b) (x), (xii), (xiii), (xxv)); processed food is taxable at 18 %"],
 [["medicines"],"only pharmaceuticals bought on a physician's prescription (and ayurvedic preparations) are exempt (Part III (a) (iii)-(iv)); applied to the whole class"],
 [["transport"],"public passenger transport other than air, water, tourist and taxi services is exempt (Part III (b) (ii)); applied to the whole class"],
 [["insurance"],"only life, Agrahara and crop/livestock insurance are exempt (Part III (b) (viii) (I)); insurance is modelled as taxable"],
 [["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise duty (Excise (Special Provisions) Act No. 13 of 1989 and gazetted rates) not modelled"],
 ["*","Social Security Contribution Levy (SSCL Act No. 25 of 2022, 2.5 % of turnover above Rs 120 million) not modelled"]],
extra_run=[],
guards=["vat.embedded { good := .clothing, amount := 1180 } == 180","vat.embedded { good := .rent, amount := 1180 } == 180","vat.embedded { good := .electricity, amount := 1180 } == 0","vat.net { turnover := 60000000, sales := [{ good := .other, net := 60000000 }] } == 0"],
taxes=[{"oecd":"5111","tax":"Value added tax (18 %)","statute":"Value Added Tax Act, No. 14 of 2002 s. 2 (1) (ix), s. 10 (viii), First Schedule Part III (as amended by Act No. 4 of 2025)","dated":"IRD consolidated text to 2025 (26 Dec 2025) with effective dates; rate from 1 Jan 2024, Part III for taxable periods from 1 Jan 2024; Act No. 4 of 2025 read","grade":"A","kernel_parts":["Vat"],"unsupported":["partial exemptions (food, prescription medicines, public transport, life insurance) applied by whole class"]},
 {"oecd":"5126","tax":"Social Security Contribution Levy (2.5 % of turnover)","statute":"Social Security Contribution Levy Act, No. 25 of 2022 as amended (Acts 15 of 2023, 15 of 2024, 24 of 2025)","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: the Acts are on ird.gov.lk (Acts_SSCL/), not read in this pass; would unlock: a turnover-levy charge on company turnover above Rs 120 million (liable turnover per s. 3 and the Schedule)"]},
 {"oecd":"5121","tax":"Excise duty","statute":"Excise (Special Provisions) Act No. 13 of 1989 and gazette rate notices","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: the build server law folders (1.x builder: PIT texts only); would unlock: the 2025 excise gazette notices (cigarettes per 1,000 sticks, liquor per litre of alcohol, petroleum)"]}])

# --- R3 gap-closing session (2026-11-21): SSCL from the Acts in lexifina/sri-lanka-law (C -> A, reclassified 5126 -> 5113) ---
S['doc'] = S['doc'].replace("# Sri Lanka 2025: value added tax (5111); SSCL and excise not modelled",
                            "# Sri Lanka 2025: value added tax (5111), Social Security Contribution Levy (5113); excise not modelled") + '''

**Social Security Contribution Levy** (gap-closing session): Act No. 25 of 2022 and its amending Acts No. 15 of 2023, No. 15
of 2024 and No. 24 of 2025, read in lexifina/sri-lanka-law `act/2022/025`, `act/2023/015`, `act/2024/015`, `act/2025/024`
(official source parliament.lk act details G6262, G6303, G6336, G6407).
* **s. 3 (1)**: 2.5 % of the liable turnover of every taxable person (s. 2: importers, manufacturers, service providers,
  wholesalers and retailers) for every quarter from 1 October 2022. **Second Schedule**: liable turnover = 100 % of
  imports, 85 % of a manufacturer's turnover, 100 % of services (financial services: value addition), 50 % of wholesale
  and retail turnover (25 % for a manufacturer's registered distributor). s. 3 (3): turnover excludes VAT.
* **s. 4 (1) (c)** (Act No. 15 of 2024 s. 2, periods from 1 January 2024): registration once the turnover of four
  consecutive quarters exceeds Rs 60 million; s. 5 (1) (c): cancellation at or below it. Modelled: a company with annual
  turnover above Rs 60 million pays 2.5 % of the share of its turnover set by `company.sector` (manufacturing 85 %,
  commercialTrading 50 %, telecom and tourism 100 %); other or absent sectors are listed (grade C), as are financial
  services (value addition basis) and the First Schedule exemptions (exports, fuel from 1 July 2025 by Act No. 24 of
  2025 s. 2 (2), electricity generation, and others).
* Classification: a multi-stage cumulative turnover tax: OECD 5113 (Interpretative Guide §63), not 5126.'''
S['extra_lean'] = (S.get('extra_lean') or '') + '''
/-- `company.sector` (string or array) and `flags`. -/
def sectorsOf (g : CanonGlobal) : List String :=
  (match (g.raw.getObjValD "company").getObjValD "sector" with
   | Lean.Json.str s => [s]
   | Lean.Json.arr a => a.toList.filterMap fun j => match j with | Lean.Json.str s => some s | _ => none
   | _ => []) ++ g.company.flags
/-- SSCL Act No. 25 of 2022 Second Schedule: liable share of turnover (bp) by sector; `none` when the sector is absent or its
share is not read from the company's facts (financial services, exempt or mixed activities). -/
def ssclShareBp (g : CanonGlobal) : Option Int :=
  let s := sectorsOf g
  if s.any (fun x => ["bank", "insurer", "petroleum", "utilities", "shipping", "agriculture", "mining"].contains x) then none
  else if s.contains "manufacturing" then some 8500
  else if s.contains "commercialTrading" then some 5000
  else if s.any (fun x => ["telecom", "tourism"].contains x) then some 10000
  else none
/-- s. 3 (1): 2.5 % of the liable turnover; s. 4 (1) (c), 5 (1) (c): above Rs 60 million a year (from 2024). -/
def ssclCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.turnover ≤ 60000000 then [] else
  match ssclShareBp g with
  | none => []
  | some sh =>
    [charge .salesTax "Social Security Contribution Levy (2.5 % of the liable turnover)" g.company.turnover
      (fun t => divR .down (t * sh) BP) (fun b => divR .down (250 * b) BP) (bearer := .entity)
      (statute := s!"Social Security Contribution Levy Act, No. 25 of 2022 s. 3 (1), Second Schedule (liable turnover {sh / 100} %), s. 4 (1) (c) as amended by Act No. 15 of 2024")]'''
S['extra_run'] = list(S.get('extra_run') or []) + ['ssclCharges g']
S['extra_covers'] = list(S.get('extra_covers') or []) + ['.salesTax']
S['unsupported'] = [u for u in S['unsupported'] if 'Social Security Contribution Levy' not in u[1]]
S['extra_unsupported'] = list(S.get('extra_unsupported') or []) + [
    '(if g.entity == .company && g.company.turnover > 60000000 && (ssclShareBp g).isNone then ["5113 SSCL: the liable share of turnover (Second Schedule) depends on the activity: company.sector absent or not one of manufacturing, commercialTrading, telecom, tourism (financial services: value addition basis): not booked (grade C)"] else [])',
    '(if g.entity == .company && g.company.turnover > 60000000 then ["5113 SSCL: First Schedule exemptions (exports, fuel from 1 July 2025, electricity generation, healthcare, education and others) and the 25 % share for registered distributors not applied; imports (100 %) not in the company facts"] else [])']
S['guards'] = list(S['guards']) + [
    '(ssclCharges { id := "t", household := { id := "t" }, entity := .company, company := { turnover := 100000000, flags := ["manufacturing"] } }).map (·.due) == [2125000]',
    '(ssclCharges { id := "t", household := { id := "t" }, entity := .company, company := { turnover := 100000000, flags := ["commercialTrading"] } }).map (·.due) == [1250000]',
    '(ssclCharges { id := "t", household := { id := "t" }, entity := .company, company := { turnover := 60000000, flags := ["manufacturing"] } }).length == 0',
    '(ssclCharges { id := "t", household := { id := "t" }, entity := .company, company := { turnover := 100000000 } }).length == 0']
for _i, _t in enumerate(S['taxes']):
    if _t['oecd'] == '5126' and _t['tax'].startswith('Social Security Contribution Levy'):
        S['taxes'][_i] = {"oecd": "5113", "tax": "Social Security Contribution Levy (2.5 % of the liable turnover)",
            "statute": "Social Security Contribution Levy Act, No. 25 of 2022 ss. 2, 3, 4 (1) (c), 5 (1) (c), First and Second Schedules, as amended by Acts No. 15 of 2023, No. 15 of 2024 and No. 24 of 2025",
            "dated": "2025: Act No. 25 of 2022 with Act No. 15 of 2024 (registration Rs 60 million from 2024) and Act No. 24 of 2025 (exemptions deemed from 18 Feb and 1 Jul 2025), read in lexifina/sri-lanka-law (official source parliament.lk); gap-closing session: C -> A; reclassified 5126 -> 5113 (OECD Interpretative Guide §63: multi-stage cumulative turnover tax)",
            "grade": "A", "kernel_parts": ["charge"],
            "unsupported": ["liable share by company.sector only (manufacturing 85 %, wholesale/retail 50 %, telecom/tourism 100 %); other sectors grade C", "First Schedule exemptions not applied", "imports by the company not in the facts"]}
