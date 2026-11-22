import IdGlobal.Pit

/-!
# Indonesia 2025: corporate income tax and art. 26 withholding (1200)

Source: UU 7/2021 (Harmonisasi Peraturan Perpajakan), `cmp20/world/B02-g20/id/law/uu_7_2021.txt`.
* **UU PPh Pasal 17 (1) b** as amended by UU 7/2021: "Wajib Pajak badan dalam negeri dan bentuk usaha tetap sebesar 22%
  (dua puluh dua persen) yang mulai berlaku pada tahun pajak 2022".
* **Pasal 26 (1)** (UU 36/2008, not amended on rates by UU 7/2021): 20 % on dividends, interest, royalties and services paid
  to non-residents; text of UU 36/2008 not on the build server (B).
-/

namespace IdGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Pajak Penghasilan badan (corporate income tax)",
    sched := Schedule.flat 2200 }

def citStatute : String := "UU PPh Pasal 17 (1) b (UU 7/2021)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 2000, statute := "UU PPh Pasal 26 (1) a" },
      { kind := .interest, rateBp := 2000, statute := "Pasal 26 (1) b" },
      { kind := .royalty, rateBp := 2000, statute := "Pasal 26 (1) c" },
      { kind := .services, rateBp := 2000, statute := "Pasal 26 (1) d" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["Pasal 31E 50 % rate cut (turnover ≤ 50 bn), listed-company 19 % (Pasal 17 (2b)), PP 55/2022 0.5 % final tax on small turnover and the branch-profits tax (Pasal 26 (4)) not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 220000
#guard wht.amount { kind := .dividend, amount := 1000 } == 200
#guard wht.amount { kind := .interest, amount := 1000 } == 200
#guard wht.amount { kind := .royalty, amount := 1000 } == 200
#guard wht.amount { kind := .services, amount := 1000 } == 200

end IdGlobal.Corporate
