import PwGlobal.Pit

/-!
# Palau 2025: business profits tax (1200) and non-resident tax (withholding)

Source: RPPL 11-11 (Senate Bill 11-15, SD1; tax reform, commencement date 1 January 2023), text copied by the 1.x PW
builder (`cmp20/world/B14-pacific/pw/law/RPPL-11-11.txt`, sha256 in `pw/law/SOURCES.tsv`).
* **§ 1421**: every PGST-registered person "must pay business profits tax on the net income ... at the same rate as the
  highest rate of tax on wages and salary established in Section 1101"; **§ 1101**: 6 % to $8,000, 10 % to $40,000,
  "twelve percent (12%) upon the amount over the first forty thousand dollars": 12 %.
* **§ 1422**: non-resident tax on "the gross amount of interest, a royalty, technical fee, or insurance premium derived
  from sources in the Republic": (b) (1) insurance premium 5 %, (2) any other amount 10 %; withheld by the payer (§ 1465).
  Dividends are not in § 1422: explicit 0 % rule (cited).
-/

namespace PwGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Business profits tax",
    sched := Schedule.flat 1200 }

def citStatute : String := "RPPL 11-11 § 1421 (rate of § 1101 top band, 12 %)"

def wht : Wht :=
  { name := "Non-resident tax (RPPL 11-11 § 1422)", rules := [
      { kind := .interest, rateBp := 1000, statute := "RPPL 11-11 § 1422 (a), (b) (2) (10 %)" },
      { kind := .royalty, rateBp := 1000, statute := "RPPL 11-11 § 1422 (a), (b) (2) (10 %)" },
      { kind := .services, rateBp := 1000, statute := "RPPL 11-11 § 1422 (a), (b) (2): technical fees 10 %" },
      { kind := .dividend, rateBp := 0, statute := "RPPL 11-11 § 1422 (a): interest, royalties, technical fees and insurance premiums only" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard cit.citTax { profit := 1000000 } == 120000
#guard wht.amount { kind := .interest, amount := 1000 } == 100

end PwGlobal.Corporate
