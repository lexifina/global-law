import UyGlobal.Pit

/-!
# Uruguay 2025: Impuesto al Patrimonio of individuals (4200); inheritance grade C

Sources (`uy/law/`, ARCHIVE_INDEX.tsv):
* Texto Ordenado DGI 2023, **Título 14** (IMPO, `todgi_t14_2024.html`): **art. 53 A)** scale for personas físicas,
  núcleos familiares y sucesiones indivisas (0.70 % to 2.75 % by multiples of the mínimo), with the statutory cuts: from
  2016 "las tasas correspondientes a las escalas 1) a 7) se reducirán en un 0,10% anual. Dicha reducción no podrá
  determinar una tasa inferior al 0,10%" (all bands reach 0.10 % by 2025); **art. 57** tax on the excess over the
  mínimo no imponible; the casa-habitación "se le deducirá el 50% de su valor con un máximo equivalente al mínimo no
  imponible correspondiente".
* **Decreto 334/025** (IMPO, published 13 Jan 2026) **art. 2**: "Fíjase en $ 6:653.000 ... el mínimo no imponible del
  Impuesto al Patrimonio correspondiente al año 2025 para las personas físicas y sucesiones indivisas" (doubled for a
  núcleo familiar).
* DGI "Tasas del Impuesto al Patrimonio personas físicas 2025" (gub.uy, `dgi_tasas_ip_pf_2025.html`): from 6.653.000:
  0,10 % (residents); confirms the computation.
Grade A. Model: each person separately (the joint núcleo familiar option with a doubled mínimo gives the same result
when assets split evenly), assets at their statutory value (valor real for real estate), home less 50 % of its value
up to the mínimo, bonds treated as exempt (public debt is; others are not), pension funds out; debts not deducted
(only certain debts are admitted); the fictitious ajuar (10 % of assets, art. 49 G) not added; assets abroad are outside
the tax (the canon has no location: all taken as in Uruguay). Companies (1.5 %, abatement by IRAE) not modelled.
-/

namespace UyGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon UyGlobal

def mni : Int := 6653000

def counted (a : Asset) : Int :=
  if [AssetKind.bonds, .pensionFund].contains a.kind then 0
  else if a.kind == .home then pos a.statutoryValue - min (divR .down (pos a.statutoryValue) 2) mni
  else pos a.statutoryValue

def base (as : List Asset) : Int := pos (isum (as.map counted) - mni)
def ipTax (as : List Asset) : Int := divR .down (10 * base as) BP

def wealthF : Family :=
  { name := "4200 impuesto al patrimonio (personas físicas)", covers := [.wealth],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.assets.map (·.person)).eraseDups.map fun p =>
        let as := g.assets.filter (·.person == p)
        charge .wealth "Impuesto al Patrimonio" (isum (as.map counted)) (fun _ => base as) (fun _ => ipTax as)
          (event := s!"person {p + 1}, 31 December 2025")
          (statute := "T.O. 2023 Título 14 arts. 53 A) (0.10 % from the 2016-2025 cuts), 57; Decreto 334/025 art. 2: mínimo $ 6.653.000") }

def families : List Family := [wealthF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (!g.assets.isEmpty && g.entity != .company) "impuesto al patrimonio per person: bonds taken as exempt (only public debt is), debts not deducted, ajuar ficto not added, all assets taken as located in Uruguay"
  ++ when (g.entity == .company) "impuesto al patrimonio of companies (1.5 %, IRAE abatement) not modelled"
  ++ when (!g.transfers.isEmpty) "inheritance and gift: no text held (grade C)"

#guard ipTax [{ kind := .realEstate, value := 16653000 }] == 10000
#guard ipTax [{ kind := .home, value := 12000000 }] == 0
#guard ipTax [{ kind := .home, value := 20000000 }] == 6694

end UyGlobal.Property
