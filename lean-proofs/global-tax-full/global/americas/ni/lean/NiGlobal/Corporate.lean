import NiGlobal.Pit

/-!
# Nicaragua 2025: IR de actividades económicas (1200)

Source: Ley 822 (La Gaceta 241, 2012; `world/.../ni/src/raw822.txt`), Ley 987 (2019) not read: grade B.
* **art. 52**: "La alícuota del IR a pagar sobre la renta neta gravable … treinta por ciento (30%)".
* The pago mínimo definitivo (art. 61) and the non-resident withholdings (art. 89) were not read.

**Pass 8 (2026-11-21), withholding on payments abroad:** Ley de Concertación Tributaria (Ley 822): art. 89 capital income bears a final withholding; art. 87 num. 2 as reformed by Ley 987 (2019): 15 % on rentas de capital (interest, royalties, dividends: art. 15) of residents and non-residents (10 % before 2019); art. 53 num. 3 as reformed by Ley 987: 20 % on non-residents' other economic activities (15 % in the Ley 891 text). Ley 987 was read in a copy of La Gaceta 41 on leybook.com, and the 2024 reform (Ley 1212) was not checked: grade B.
-/

namespace NiGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon NiGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la Renta (actividades económicas)", sched := Schedule.flat 3000 }

def citStatute : String := "Ley 822 art. 52 (30 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1500, statute := "Ley 822 art. 87 num. 2 as reformed by Ley 987 (La Gaceta 41, 28 Feb 2019): rentas de capital, residentes y no residentes 15 %" }, { kind := .interest, rateBp := 1500, statute := "Ley 822 art. 87 num. 2 as reformed by Ley 987 (La Gaceta 41, 28 Feb 2019): rentas de capital, residentes y no residentes 15 %" }, { kind := .royalty, rateBp := 1500, statute := "Ley 822 art. 87 num. 2 as reformed by Ley 987 (La Gaceta 41, 28 Feb 2019): rentas de capital, residentes y no residentes 15 %" }, { kind := .services, rateBp := 2000, statute := "Ley 822 art. 53 num. 3 as reformed by Ley 987: restantes actividades económicas de no residentes 20 %" }] }

def citF : Family := corpFamily "1200 Impuesto sobre la Renta (actividades económicas)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "pago mínimo definitivo (Ley 822 art. 61, % of gross income) not modelled: the regular tax only"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "Ley 822 art. 87 num. 1 (10 % on financing from investment-grade international banks), art. 87 num. 3 and art. 49 (30 % for tax havens), and the 1.5 %/3 % rates of art. 53 num. 1-2 not modelled; Ley 1212 (La Gaceta 155, 22 Aug 2024) not checked"

#guard regime.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 150000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 200000

end NiGlobal.Corporate
