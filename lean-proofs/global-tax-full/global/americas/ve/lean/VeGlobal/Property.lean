import VeGlobal.Pit

/-!
# Venezuela 2025: Impuesto a los Grandes Patrimonios (4200); inheritance grade C

Source: **Ley Constitucional que crea el Impuesto a los Grandes Patrimonios**, G.O. 41.667 of 3 Jul 2019 (gazette copy,
`ve/law/go41667_ley_igp_2019.pdf`, ARCHIVE_INDEX.tsv). Grade A.
* Art. 1: on the net patrimony of the "sujetos pasivos especiales" whose patrimony is at least 36.000.000 U.T. (natural
  persons) or 100.000.000 U.T. (legal persons), "por la porción del patrimonio que supere los montos indicados";
  art. 4: residents on their worldwide patrimony.
* Art. 13: exempt, among others, no. 4 "La vivienda registrada como principal ... hasta por un valor de sesenta y cuatro
  millones de Unidades Tributarias (64.000.000 U.T.)", no. 5 the household goods, no. 6 social benefits (prestaciones).
* Art. 23: rate between 0.25 % and 1.50 % fixed by the Executive; Disposición Transitoria Segunda: "será del cero
  veinticinco por ciento (0,25%)" until another rate is set (none found).
U.T.: the period is annual (the tax arises on the last day of the period, art. 11), so the U.T. in force at the close
of 2025 applies (Código Orgánico Tributario art. 3, G.O. 6.507 Ext.): Bs. 43 (G.O. 43.140): thresholds Bs.
1,548,000,000 (natural persons), home exemption up to Bs. 2,752,000,000.
Model: each person (by `person`) is taken to be a designated sujeto pasivo especial (SENIAT designation is not an
input: upper bound for anyone not designated); assets at their statutory value less debts; the main home exempt up
to the limit; pension funds out (prestaciones). Companies (100.000.000 U.T. on net patrimony) not modelled.
-/

namespace VeGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon VeGlobal

def ut : Int := 43
def threshold : Int := 36000000 * ut
def homeCap : Int := 64000000 * ut

def counted (a : Asset) : Int :=
  if a.kind == .pensionFund then 0
  else if a.kind == .home then pos (a.statutoryValue - homeCap)
  else pos a.statutoryValue

def net (as : List Asset) : Int := pos (isum (as.map counted) - isum (as.map (·.debt)))
def igp (as : List Asset) : Int := if net as < threshold then 0 else divR .down (25 * (net as - threshold)) BP

def wealthF : Family :=
  { name := "4200 impuesto a los grandes patrimonios", covers := [.wealth],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.assets.map (·.person)).eraseDups.map fun p =>
        let as := g.assets.filter (·.person == p)
        charge .wealth "Impuesto a los Grandes Patrimonios" (net as) (fun b => pos (b - threshold)) (fun _ => igp as)
          (event := s!"person {p + 1}, 31 December 2025")
          (statute := "Ley Constitucional del IGP (G.O. 41.667, 2019) arts. 1, 13 no. 4, 23, Disp. Trans. 2a: 0.25 % above 36.000.000 U.T. (U.T. Bs. 43)") }

def families : List Family := [wealthF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (!g.assets.isEmpty && g.entity != .company) "IGP: every person taken as a designated sujeto pasivo especial (upper bound); statutory values less debts; household goods not in the canon"
  ++ when (g.entity == .company) "IGP on legal persons (100.000.000 U.T.) not modelled"
  ++ when (!g.transfers.isEmpty) "inheritance and gift tax (Ley de Impuesto sobre Sucesiones) not modelled"

#guard threshold == 1548000000
#guard igp [{ kind := .deposits, value := 1548000000 }] == 0
#guard igp [{ kind := .deposits, value := 2548000000 }] == 2500000
#guard igp [{ kind := .home, value := 2752000000 }] == 0

end VeGlobal.Property
