import BoGlobal.Pit

/-!
# Bolivia 2025: Impuesto a las Grandes Fortunas (4200); TGB on inheritances grade C

Source: **Ley 1357 de 28 de diciembre de 2020** (Lexivox text, `bo/law/ley_1357_2020_lexivox.html`, ARCHIVE_INDEX.tsv).
Grade A.
* Art. 2: on the fortune of natural persons (real and movable property, financial assets, rights, money), from 2020;
  art. 3: residents on their fortune in Bolivia and abroad; art. 6: companies and other legal persons excluded.
* Art. 5: due when the net fortune at 31 December "sea mayor a los Bs30.000.000".
* Art. 7: base = net value of the fortune (less the deductions of the law and its regulation); spouses under community
  of property: each spouse's own fortune plus 50 % of the community fortune.
* Art. 9 scale on the whole base, with a deduction: Bs 30,000,001-40,000,000: 1.4 % less Bs 150,000; 40,000,001-
  50,000,000: 1.9 % less Bs 350,000; from 50,000,001: 2.4 % less Bs 600,000.
* Art. 10: the property taxes paid on real estate and registered movables are credited (not modelled: the municipal
  taxes are not modelled).
Model: each person's assets (by `person`) at their statutory value less their debts (art. 8 valuation rules are set by
the regulation, not read).
-/

namespace BoGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon BoGlobal

def netFortune (as : List Asset) : Int := pos (isum (as.map (·.statutoryValue)) - isum (as.map (·.debt)))

def igf (as : List Asset) : Int :=
  let b := netFortune as
  if b ≤ 30000000 then 0
  else if b ≤ 40000000 then divR .down (140 * b) BP - 150000
  else if b ≤ 50000000 then divR .down (190 * b) BP - 350000
  else divR .down (240 * b) BP - 600000

def wealthF : Family :=
  { name := "4200 impuesto a las grandes fortunas", covers := [.wealth],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.assets.map (·.person)).eraseDups.map fun p =>
        let as := g.assets.filter (·.person == p)
        charge .wealth "Impuesto a las Grandes Fortunas" (netFortune as) id (fun _ => igf as)
          (event := s!"person {p + 1}, 31 December 2025")
          (statute := "Ley 1357 de 2020 arts. 5, 7, 9: over Bs 30.000.000, 1.4 % - 150.000 / 1.9 % - 350.000 / 2.4 % - 600.000") }

def families : List Family := [wealthF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (!g.assets.isEmpty && g.entity != .company) "IGF per person at statutory values less debts (regulation's valuation rules not read; spouses' community property 50/50 split not applied beyond the asset's `person`); property taxes paid not credited (art. 10)"
  ++ when (!g.transfers.isEmpty) "TGB on inheritances and gifts (Ley 843 Título VI) not modelled"

#guard igf [{ kind := .realEstate, value := 30000000 }] == 0
#guard igf [{ kind := .realEstate, value := 40000000 }] == 410000
#guard igf [{ kind := .deposits, value := 50000000 }] == 600000
#guard igf [{ kind := .deposits, value := 60000000 }] == 840000

end BoGlobal.Property
