import CuGlobal.Pit

/-!
# Cuba 2025: Impuesto sobre Utilidades (1200)

Sources: Ley 113 (as modified to 2021) and Ley 174 (2025 budget, GOC-2024-O127).
* **Ley 174 art. 69**: "Para el cálculo del Impuesto sobre Utilidades se aplica con carácter general el tipo
  impositivo del treinta y cinco por ciento (35 %)" (exceptions in Ley 113, Ley 118 and the Mariel regulations).

**Pass 7 (2026-11-21), withholding on payments abroad:** Ley 113/2012 del Sistema Tributario: art. 73 párr. 2: the taxable profit of a foreign legal person without a permanent establishment is its gross income; art. 98: 4 %; art. 99: whoever pays it withholds. Individuals not permanently resident: art. 27 15 % of the total income generated in Cuba; art. 33 párr. 2: a final 15 % withholding. Grade A.
-/

namespace CuGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon CuGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre Utilidades", sched := Schedule.flat 3500 }

def citStatute : String := "Ley 174 (2025) art. 69; Ley 113 art. 97"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 400, toCompany := some true, statute := "Ley 113/2012 arts. 73 párr. 2, 98, 99: personas jurídicas extranjeras sin establecimiento permanente 4 % of gross income, retenido por el pagador" }, { kind := .interest, rateBp := 400, toCompany := some true, statute := "Ley 113/2012 arts. 73 párr. 2, 98, 99: personas jurídicas extranjeras sin establecimiento permanente 4 % of gross income, retenido por el pagador" }, { kind := .royalty, rateBp := 400, toCompany := some true, statute := "Ley 113/2012 arts. 73 párr. 2, 98, 99: personas jurídicas extranjeras sin establecimiento permanente 4 % of gross income, retenido por el pagador" }, { kind := .services, rateBp := 400, toCompany := some true, statute := "Ley 113/2012 arts. 73 párr. 2, 98, 99: personas jurídicas extranjeras sin establecimiento permanente 4 % of gross income, retenido por el pagador" }, { kind := .dividend, rateBp := 1500, toCompany := some false, statute := "Ley 113/2012 arts. 27, 33 párr. 2: personas naturales no residentes permanentes 15 % of the total income, retención definitiva" }, { kind := .interest, rateBp := 1500, toCompany := some false, statute := "Ley 113/2012 arts. 27, 33 párr. 2: personas naturales no residentes permanentes 15 % of the total income, retención definitiva" }, { kind := .royalty, rateBp := 1500, toCompany := some false, statute := "Ley 113/2012 arts. 27, 33 párr. 2: personas naturales no residentes permanentes 15 % of the total income, retención definitiva" }, { kind := .services, rateBp := 1500, toCompany := some false, statute := "Ley 113/2012 arts. 27, 33 párr. 2: personas naturales no residentes permanentes 15 % of the total income, retención definitiva" }] }

def citF : Family := corpFamily "1200 Impuesto sobre Utilidades" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "foreign-investment (Ley 118, 15 %) and Mariel (12 %) rates, cooperative minimum (art. 71) not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "dividend exemptions for foreign investment (Ley 118) and Mariel not modelled"

#guard regime.citTax { profit := 1000000 } == 350000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 40000
#guard wht.amount { kind := .interest, amount := 1000000 } == 40000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 40000
#guard wht.amount { kind := .services, amount := 1000000 } == 40000
#guard wht.amount { kind := .dividend, amount := 1000000, toCompany := false } == 150000
#guard wht.amount { kind := .interest, amount := 1000000, toCompany := false } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000, toCompany := false } == 150000
#guard wht.amount { kind := .services, amount := 1000000, toCompany := false } == 150000

end CuGlobal.Corporate
