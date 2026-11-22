import GrGlobal.Pit
import TaxKernel.Global2

/-!
# GR 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Φόρος μεταβίβασης ακινήτων (ν. 1587/1950, 3 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (ΕΝΦΙΑ (ν. 4223/2013)): pass 15: the floor area is an input since kernel 2.4, but the band of the zone price and the coefficients are not, and the band table was not reached (grade C; zone-value field requested from the kernel); would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Φόρος μεταβίβασης ακινήτων (ΦΜΑ) (pass 6)
Source: PwC Worldwide Tax Summaries, Greece, Corporate - Other taxes, accessed 2025-06-23 (Wayback capture; `law/pwc_corpother_wb2025.txt`).
* ΦΜΑ 3 % of the objective value (transfers outside VAT) + municipal surcharge 3 % of the tax = 3,09 %

* **4100 Recurrent property tax (pass 6 note, grade C)**: ΕΝΦΙΑ (ν. 4223/2013): ENFIA (ν. 4223/2013) is national but per m2 with location and use coefficients (EUR 2-16,20 per m2 for buildings): area inputs are not in the model (pass 6 note (PwC WWTS 2025 captures on disk))


## 4100 ΕΝ.Φ.Ι.Α. of natural persons (pass 17, kernel 2.7.0 ZoneTax, grade B)
Sources: ν. 4916/2022 (ΦΕΚ Α' 65/28.03.2022) άρθ. 40 (άρθ. 1 παρ. 3: principal tax plus the Ε surcharge for natural persons), 43 (άρθ. 4 Α παρ. 2 α table; new Ενότητες Γ, Δ, Ε), 44 (supplementary tax of natural persons abolished), 46 (άρθ. 7 παρ. 2Α); ν. 4223/2013 άρθ. 4 Α παρ. 1-3 in the 2013 wording for the coefficients.
* Β.Φ. by zone price (€/m²): 0-750 2,00; 751-1 500 2,80; 1 501-2 500 3,70; 2 501-3 000 4,50; 3 001-3 500 7,60; 3 501-4 000 9,20; 4 001-4 500 11,10; 4 501-5 000 13,40; 5 001+ 16,20
* Σ.Π.Κ. by age (tax year less the newest permit's year): up to 4 1,25; 5-9 1,20; 10-14 1,15; 15-19 1,10; 20-25 1,05; 26+ 1,00; built before 1930 0,80; over 100 years 0,60. Σ.Ο.: basement 0,98; ground and 1st 1,00; 2nd-3rd 1,01; 4th-5th 1,02; 6th+ 1,03. Σ.Π.: no frontage 1,00, one 1,01, two or more 1,02
* Γ: where the owner's total value exceeds 300 000, each right's value is taxed by bands: to 400 000 0 %; 0,20 / 0,30 / 0,40 / 0,50 / 0,60 / 0,70 % per further 100 000 to 1 000 000; 0,90 % to 2 000 000; 1,00 % above
* Ε: the natural person's ΕΝ.Φ.Ι.Α. is raised by 5 % (total to 650 000), 10 % (to 800 000), 15 % (to 1 000 000), 20 % (above), only above 500 000; άρθ. 7 παρ. 2Α: reduced by 30 % (to 100 000), 25 % (150 000), 20 % (250 000), 15 % (300 000), 10 % (400 000)
* Kernel: `ZoneTax` with `.perArea` bands and the age, floor and frontage coefficients per building (one rounding each), then (Σ Α + Σ Γ) x (1 + Ε) x (1 - 2Α) rounded half up; the objective value is read from the asset's `"objectiveValue"`
* Hand check (case gr-enfia-flat): 100 m², zone 1 800 (3,70), built 2005 (20 years: 1,05), 3rd floor (1,01), one frontage (1,01): 100 x 3,70 x 1,05 x 1,01 x 1,01 = 396,31 -> 396; objective value 160 000: reduction 20 %: 316,8 -> **317**
* Hand check (case gr-enfia-large): 150 m², zone 5 200 (16,20), built 2019 (6 years: 1,20), 6th floor (1,03), two frontages (1,02): 150 x 16,20 x 1,20 x 1,03 x 1,02 = 3 063,55 -> 3 063; objective value 900 000: Γ = 200 + 300 + 400 + 500 + 600 = 2 000; (3 063 + 2 000) x 1,15 = 5 822,45 -> **5 822**
-/

namespace GrGlobal.Property
open TaxKernel TaxKernel.Global

/-- ν. 1587/1950 ΦΜΑ 3 % + municipal surcharge 3 % of it = 3,09 % -/
def p6fma : TransferDuty := { name := "Φόρος μεταβίβασης ακινήτων (ΦΜΑ)", sched := Schedule.flat 309, kinds := [.home, .realEstate, .land] }

/-- ν. 4223/2013 άρθ. 4 Α παρ. 2 α (πίνακας ν. 4916/2022 άρθ. 43 παρ. 1, from ΕΝ.Φ.Ι.Α. 2022), β (Σ.Π.Κ.; before 1930 0,80,
over 100 years 0,60), δ (Σ.Ο.), στ (Σ.Π.), παρ. 3 α: area x Β.Φ. of the zone-price band x Σ.Π.Κ. x Σ.Ο. x Σ.Π. -/
def p17grEnfiaA : ZoneTax :=
  { name := "ΕΝ.Φ.Ι.Α. κύριος φόρος κτισμάτων (άρθ. 4 Α)", kinds := [.home, .realEstate],   base := .perArea [(0, QtyTable.perUnit 200 100), (751, QtyTable.perUnit 280 100), (1501, QtyTable.perUnit 370 100),     (2501, QtyTable.perUnit 450 100), (3001, QtyTable.perUnit 760 100), (3501, QtyTable.perUnit 920 100),     (4001, QtyTable.perUnit 1110 100), (4501, QtyTable.perUnit 1340 100), (5001, QtyTable.perUnit 1620 100)],   coefs := [{ fact := .age, bands := [(0, 12500), (5, 12000), (10, 11500), (15, 11000), (20, 10500), (26, 10000), (96, 8000), (101, 6000)] },             { fact := .floor, bands := [(-1000, 9800), (0, 10000), (2, 10100), (4, 10200), (6, 10300)] },             { fact := .frontages, bands := [(0, 10000), (1, 10100), (2, 10200)] }],   statute := "ν. 4223/2013 άρθ. 4 Α παρ. 2 α (πίνακας ν. 4916/2022 άρθ. 43 παρ. 1), β, δ, στ, παρ. 3 α" }
def p17grIsRe (a : Asset) : Bool := a.kind == .home || a.kind == .realEstate || a.kind == .land
/-- the objective values ("objectiveValue", ν. 3842/2010 άρθ. 32) of the household's real estate; none if one is missing -/
def p17grOvs (g : CanonGlobal) : Option (List Int) :=
  let xs := (g.assets.zipIdx.filter fun (a, _) => p17grIsRe a).map fun (_, i) => assetFact? g i (.field "objectiveValue")
  if xs.all (·.isSome) then some (xs.map (·.getD 0)) else none
/-- άρθ. 4 Γ (ν. 4916/2022 άρθ. 43 παρ. 4): tax on the total value per right, by bands, where the owner's total exceeds 300 000 -/
def p17grGamma : Schedule := Schedule.ofList [(0, 0), (400000, 20), (500000, 30), (600000, 40), (700000, 50), (800000, 60), (900000, 70), (1000000, 90), (2000000, 100)]
/-- άρθ. 4 Ε: surcharge on a natural person's ΕΝ.Φ.Ι.Α. above a total value of 500 000 -/
def p17grSurBp (v : Int) : Int :=
  if v ≤ 500000 then 0 else if v ≤ 650000 then 500 else if v ≤ 800000 then 1000 else if v ≤ 1000000 then 1500 else 2000
/-- άρθ. 7 παρ. 2Α (ν. 4916/2022 άρθ. 46 παρ. 3): reduction by the total value up to 400 000 -/
def p17grRedBp (v : Int) : Int :=
  if v ≤ 100000 then 3000 else if v ≤ 150000 then 2500 else if v ≤ 250000 then 2000 else if v ≤ 300000 then 1500
  else if v ≤ 400000 then 1000 else 0
/-- computed only for a household whose buildings give every fact and whose real estate gives its objective value, without plots -/
def p17grReady (g : CanonGlobal) : Bool :=
  g.entity == .household && !g.assets.any (·.kind == .land) && (p17grOvs g).isSome && (p17grEnfiaA.unknown g).isEmpty
    && g.assets.any (fun a => a.kind == .home || a.kind == .realEstate)
/-- (total objective value, ΕΝ.Φ.Ι.Α.): (Σ Α + Σ Γ) x (1 + Ε) x (1 - 2Α), rounded once to the euro -/
def p17grEnfiaDue (g : CanonGlobal) : Int × Int :=
  let ovs := (p17grOvs g).getD []
  let v := isum ovs
  let a := isum ((p17grEnfiaA.charges g).map (·.due))
  let c := if 300000 < v then isum (ovs.map fun x => p17grGamma.tax {} x) else 0
  (v, divR .halfUp ((a + c) * (10000 + p17grSurBp v) * (10000 - p17grRedBp v)) (10000 * 10000))
def p17grEnfiaCharges (g : CanonGlobal) : List Charge :=
  if !p17grReady g then [] else
  let r := p17grEnfiaDue g
  [charge .propertyRecurrent "ΕΝ.Φ.Ι.Α. φυσικών προσώπων (κύριος φόρος άρθ. 4 Α, Γ; προσαύξηση Ε; μείωση άρθ. 7 παρ. 2Α)" r.1
    (fun _ => r.1) (fun _ => r.2) (event := "year") (level := .central)
    (statute := "ν. 4223/2013 άρθ. 1 παρ. 3 α, 4 Α, Γ, Δ, Ε, 7 παρ. 2Α (ν. 4916/2022 άρθ. 40, 43, 46)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Φόρος μεταβίβασης ακινήτων (ΦΜΑ)", covers := [.transactions],
     run := fun args g prev =>
       p6fma.charges g.purchases "ν. 1587/1950 ΦΜΑ 3 % + municipal surcharge 3 % of it = 3,09 %" },
   { name := "4100 ΕΝ.Φ.Ι.Α. φυσικών προσώπων (pass 17, kernel 2.7.0 ZoneTax)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       p17grEnfiaCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["GR 4400 Φόρος μεταβίβασης ακινήτων (ΦΜΑ): PwC WWTS Corporate - Other taxes, 2025-06-23 (Wayback capture) (grade B)", "GR 4100 ΕΝ.Φ.Ι.Α. pass 17 (kernel 2.7.0 ZoneTax): band table of ν. 4916/2022 άρθ. 43 (ΦΕΚ Α' 65/2022), coefficients of άρθ. 4 Α παρ. 2 β, δ, στ; Ενότητες Γ, Ε and άρθ. 7 παρ. 2Α on the objective value (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["4400 the base is the objective value where higher (the price stands in); new buildings under VAT not separated"] else [])
  ++ (if g.assets.any p17grIsRe && !p17grReady g then ["4100 ΕΝ.Φ.Ι.Α.: not computed (grade C): every building needs its area, zone value, building year, floor and frontages, and all real estate its objective value (ν. 3842/2010 άρθ. 32, \"objectiveValue\"), which sets Ενότητες Γ and Ε and the άρθ. 7 παρ. 2Α reduction; plots and land (Ενότητα Β) and legal persons (άρθ. 5) are not modelled"] else [])
  ++ (if p17grReady g then ["4100 ΕΝ.Φ.Ι.Α.: each building is taken as a finished main-use apartment space in full ownership (Σ.Μ. 1,02 for a detached house, Σ.Β.Χ., Σ.Η.Κ. and special buildings are not inputs) and its building year as the year of the newest permit; not applied: the insurance discount of ν. 5162/2024 (from 2025) and the άρθ. 7 παρ. 1-2 exemption and 50 % reduction (2024 family income, not an input)"] else [])

#guard p6fma.amount { kind := .home, price := 200000 } == 6180
#guard p6fma.amount { kind := .home, price := 2000000 } == 61800
#guard p6fma.amount { kind := .vehicle, price := 100000 } == 0
#guard p17grSurBp 600000 == 500 && p17grSurBp 500000 == 0 && p17grSurBp 1000001 == 2000
#guard p17grRedBp 160000 == 2000 && p17grRedBp 100000 == 3000 && p17grRedBp 400001 == 0
#guard p17grGamma.tax {} 450000 == 100 && p17grGamma.tax {} 400000 == 0

end GrGlobal.Property
