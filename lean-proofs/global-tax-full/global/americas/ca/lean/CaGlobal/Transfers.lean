import CaGlobal.Pit

/-!
# Canada 2025 (Toronto): Ontario Land Transfer Tax and Toronto Municipal Land Transfer Tax (4400); Toronto property
tax (4100)

* **Ontario LTT** (pass 1, unchanged): Land Transfer Tax Act, R.S.O. 1990 c. L.6 (e-Laws consolidation from 2026-04-24;
  `ca/law/on_90l06.txt`), s. 2 (1): 0.5 % to $55,000, 1 % to $250,000, 1.5 % to $400,000, 2 % above; (b) above
  $2,000,000 for land with one or two single family residences, an additional 0.5 %. Grade B.
* **Toronto MLTT**: Toronto Municipal Code ch. 760 (toronto.ca PDF, consolidated to 2023-09-06; `ca/law/toronto_mc_760.pdf`),
  **§ 760-9.2** "Amount on or after January 1, 2024" (By-law 824-2023): A. land with one or two single-family residences:
  0.5 % to $55,000; 1 % to $250,000; 1.5 % to $400,000; 2 % to $2,000,000; 2.5 % to $3,000,000; 3.5 % to $4,000,000;
  4.5 % to $5,000,000; 5.5 % to $10,000,000; 6.5 % to $20,000,000; "7.5 percent of the value of the consideration
  which exceeds $20,000,000"; B. other land: 0.5 / 1 / 1.5 / 2 % (to $55,000 / $250,000 / $400,000 / above). First-time
  purchaser rebate: "the maximum amount of tax subject to rebate ... on or after March 1, 2017 ... is $4,475". Grade A.
* **Toronto property tax 2025**: City of Toronto, "Property Tax Rates and Fees" (toronto.ca, Wayback capture 2025-07-16;
  `ca/law/toronto_tax_rates_2025.html`): "2025 Property Tax Rates ... Residential 0.592653% [City] 0.153000% [Education]
  0.008434% [City Building Fund] 0.754087% [Total]" on the MPAC assessed value. Official secondary for the 2025 rate
  by-law and the Ontario education-rate regulation: grade B. Residential class read for homes, other real estate and
  land (flagged).

FT review (2026-11-21), Ontario LTT re-read in `ca/law/on_90l06.txt` (e-Laws consolidation from 2026-04-24, whose
"Section Amendments with date in force" lists, for s. 2, no change after "2017, c. 17, Sched. 1, s. 2 - 01/06/2017"
(subs. (2.1), the NRST) and for s. 9.2 none after "2017, c. 8, Sched. 16, s. 4 (1-3) - 17/05/2017": the 2025 wording):
* **s. 2 (1) (b)**: "if the value of the consideration for the conveyance exceeds $2,000,000 and the conveyance is a
  conveyance of land that contains at least one and not more than two single family residences, an additional tax of
  one-half of 1 per cent": homes only (the model applied it to every kind before).
* **s. 9.2 (2)**: "The Minister may refund ... tax payable under this Act by a purchaser in respect of the acquisition
  by the purchaser of a qualifying home to be used by the purchaser as his or her principal residence"; **(2.1) (b)**:
  "$4,000 if the conveyance or disposition of the home occurs on or after January 1, 2017". Applied to a home flagged
  `firstHome` (the purchaser conditions of s. 9.2 (1), citizenship or permanent residence, not checked).
Toronto MLTT rates checked against the City's "MLTT and MNRST Rates" page (Wayback 2025-08-02,
`ca/law/toronto_mltt_rates_wb20250802.html`): "Effective September 6, 2023 ... Over $2,000,000.00 2.5% Over $3,000,000
and up to $4,000,000 3.5% ... Over $20,000,000 7.5%": unchanged in 2025. The MNRST (10 % for foreign buyers from
1 January 2025, item 2024.EX11.1) and the Ontario NRST (s. 2 (2.1)) are not modelled.

FT review 5 (2026-11-21), Dataset round 3 R3-1. Toronto Municipal Code ch. 760 (`ca/law/toronto_mc_760.txt`), § 760-1
"FIRST TIME PURCHASER" B: "If the conveyance or disposition of the eligible home occurs on or after March 1, 2017, an
individual who is at least 18 years of age, is a Canadian citizen or permanent resident of Canada and who has never
owned an eligible home"; § 760-60 A rebates "tax payable under this chapter by a first time purchaser"; G: a
non-citizen becomes eligible only "if he or she becomes a Canadian citizen or permanent resident of Canada within 18
months". Ontario LTTA s. 9.2 (1) "purchaser" (c) ("who is a Canadian citizen or permanent resident of Canada") and
(2.0.1) (`ca/law/on_90l06.txt`), the same. A purchase flagged `nonResident` is read as a purchaser who is not a Canadian
citizen or permanent resident on the date of the conveyance (the reading of the AU model's s. 104J foreign person, and
the City calculator's MNRST purchaser type, which carries no rebate): no rebate or refund (a later grant under § 760-60 G
/ s. 9.2 (2.0.1) is not modelled).
-/

namespace CaGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon CaGlobal

/-- LTTA s. 2 (1) (a) and (b): land with one or two single family residences (+ 0.5 % above $2,000,000). -/
def lttHome : TransferDuty :=
  { name := "Land Transfer Tax (Ontario)", kinds := [.home],
    sched := Schedule.ofList [(0, 50), (55000, 100), (250000, 150), (400000, 200), (2000000, 250)] }
/-- s. 2 (1) (a) only: other land. -/
def lttOther : TransferDuty :=
  { name := "Land Transfer Tax (Ontario)", kinds := [.realEstate, .land],
    sched := Schedule.ofList [(0, 50), (55000, 100), (250000, 150), (400000, 200)] }
/-- s. 9.2 (2), (2.1) (b): refund to a first-time purchaser of a qualifying home, at most $4,000. -/
def ltt (p : Purchase) : Int :=
  let t := lttHome.amount p + lttOther.amount p
  t - (if p.firstHome && !p.nonResident && p.kind == .home then min 4000 t else 0)
def lttF : Family :=
  { name := "4400 Ontario land transfer tax", covers := [.transactions],
    run := fun _ g _ => (g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).map fun (p, i) =>
      charge .transactions "Land Transfer Tax (Ontario)" p.price id (fun _ => ltt p) (event := s!"purchase {i + 1}")
        (level := .state) (statute := "Land Transfer Tax Act (Ont.) s. 2 (1) (a), (b) (one or two single family residences); s. 9.2 (2), (2.1) (b) first-time purchaser refund max $4,000") }

/-- Toronto MLTT § 760-9.2 A (one or two single-family residences). -/
def mlttRes : TransferDuty :=
  { name := "Municipal Land Transfer Tax (Toronto)", kinds := [.home],
    sched := Schedule.ofList [(0, 50), (55000, 100), (250000, 150), (400000, 200), (2000000, 250), (3000000, 350),
      (4000000, 450), (5000000, 550), (10000000, 650), (20000000, 750)] }
/-- § 760-9.2 B (other land). -/
def mlttOther : TransferDuty :=
  { name := "Municipal Land Transfer Tax (Toronto)", kinds := [.realEstate, .land],
    sched := Schedule.ofList [(0, 50), (55000, 100), (250000, 150), (400000, 200)] }

/-- MLTT after the first-time purchaser rebate (at most $4,475). -/
def mltt (p : Purchase) : Int :=
  let t := mlttRes.amount p + mlttOther.amount p
  t - (if p.firstHome && !p.nonResident && p.kind == .home then min 4475 t else 0)

def mlttF : Family :=
  { name := "4400 Toronto Municipal Land Transfer Tax", covers := [.transactions],
    run := fun _ g _ => (g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).map fun (p, i) =>
      charge .transactions "Municipal Land Transfer Tax (Toronto)" p.price id (fun _ => mltt p) (event := s!"purchase {i + 1}")
        (level := .local) (statute := "Toronto Municipal Code ch. 760 § 760-9.2 (from 1 Jan 2024); first-time purchaser rebate max $4,475") }

/-- 2025 residential rates, per 100,000,000 of assessed value: City 0.592653 % + City Building Fund 0.008434 %;
education 0.153 %. -/
def cityTax (v : Int) : Int := divR .down (pos v * 601087) 100000000
def eduTax (v : Int) : Int := divR .down (pos v * 153000) 100000000

def propF : Family :=
  { name := "4100 Toronto property tax (residential)", covers := [.propertyRecurrent],
    run := fun _ g _ => (g.assets.zipIdx.filter fun (a, _) => a.kind.isRealEstate).flatMap fun (a, i) =>
      [charge .propertyRecurrent "Property tax, municipal (Toronto)" a.statutoryValue id cityTax (event := s!"asset {i + 1}") (level := .local)
         (statute := "City of Toronto 2025 residential rate 0.592653 % + City Building Fund 0.008434 % (toronto.ca rate table)"),
       charge .propertyRecurrent "Property tax, education (Ontario)" a.statutoryValue id eduTax (event := s!"asset {i + 1}") (level := .state)
         (statute := "Ontario 2025 residential education rate 0.153 % (toronto.ca rate table)")] }

def families : List Family := [lttF, mlttF, propF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := when (!g.purchases.isEmpty) "Ontario LTT: a home read as land with one or two single family residences, the s. 9.2 refund applied when flagged firstHome and not nonResident (age and earlier ownership not checked), NRST (s. 2 (2.1)) and Toronto MNRST not modelled; MLTT: a home read as land with one or two single-family residences, the first-time rebate applied when the purchase is flagged firstHome and not nonResident (a nonResident purchaser read as not a citizen or permanent resident; age and earlier ownership not checked)"
  ++ when (g.assets.any fun a => a.kind.isRealEstate) "Toronto property tax at the 2025 residential rates on the asset's assessed (MPAC) value; other real estate and land read as residential; vacant home tax and municipal surcharges not modelled"

#guard ltt { kind := .home, price := 500000 } == 275 + 1950 + 2250 + 2000
#guard ltt { kind := .home, price := 3000000 } == 275 + 1950 + 2250 + 32000 + 25000
#guard mltt { kind := .home, price := 1000000 } == 275 + 1950 + 2250 + 12000
#guard mltt { kind := .home, price := 1000000, firstHome := true } == 275 + 1950 + 2250 + 12000 - 4475
#guard mltt { kind := .home, price := 25000000 } == 275 + 1950 + 2250 + 32000 + 25000 + 35000 + 45000 + 275000 + 650000 + 375000
#guard mltt { kind := .realEstate, price := 3000000 } == 275 + 1950 + 2250 + 52000
#guard cityTax 1000000 + eduTax 1000000 == 7540
-- LTTA s. 2 (1) (b): the 0.5 % above $2,000,000 only for one or two single family residences
#guard ltt { kind := .realEstate, price := 3000000 } == 275 + 1950 + 2250 + 52000
#guard ltt { kind := .land, price := 2000001 } == 275 + 1950 + 2250 + 32000
#guard ltt { kind := .home, price := 2000100 } == 275 + 1950 + 2250 + 32002 + 0
-- s. 9.2 (2.1) (b): refund at most $4,000
#guard ltt { kind := .home, price := 368000, firstHome := true } == 0
#guard ltt { kind := .home, price := 500000, firstHome := true } == 275 + 1950 + 2250 + 2000 - 4000
-- ch. 760 § 760-1 FIRST TIME PURCHASER B, LTTA s. 9.2 (1) (c): citizen or permanent resident only
#guard mltt { kind := .home, price := 586575, firstHome := true, nonResident := true } == 275 + 1950 + 2250 + 3731
#guard mltt { kind := .home, price := 586575, firstHome := true } == 275 + 1950 + 2250 + 3731 - 4475
#guard ltt { kind := .home, price := 500000, firstHome := true, nonResident := true } == 275 + 1950 + 2250 + 2000

end CaGlobal.Transfers
