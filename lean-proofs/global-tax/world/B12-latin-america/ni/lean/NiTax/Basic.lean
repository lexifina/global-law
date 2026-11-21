import TaxKernel.World

/-!
# Nicaragua 2025: IR de rentas del trabajo (Ley 822, Ley de Concertacion Tributaria)

Sources (DGI Nicaragua documents, Internet Archive copies: dgi.gob.ni answers "Request Rejected" to scripts and the
Asamblea's Normaweb has no index reachable; not bypassed):
* Ley 822, La Gaceta No. 241 of 17-12-2012 (`dgi.gob.ni/documentos/GACETA_241_Ley_822_Ley_de_Concert._Tributaria.pdf`,
  capture 2013-01-23, sha256 c00a85dfa4136...): art. 21 (deductions: social-security contributions, pension-fund
  contributions, 25 % of education/health/professional expenses capped at C$ 20.000 from 2017), art. 23 (tarifa
  progresiva: 0.01-100.000 0 %; 100.000,01-200.000 15 %; 200.000,01-350.000 C$ 15.000 + 20 %; 350.000,01-500.000
  C$ 45.000 + 25 %; 500.000,01 a mas C$ 82.500 + 30 %, "sobre exceso de").
* Ley 891, La Gaceta No. 240 of 18-12-2014 (capture 2015-04-20, sha256 d5fb156a4233...), Articulo quinto: "Se derogan
  ... a. Ultimo parrafo del articulo 23" (the clause that would have lowered the tariff one point a year from 2016).
Later reforms (Ley 987 of 2019 and after) were not reached: access B.
* Art. 19 (Exenciones objetivas) num. 2 (same Gaceta, src/ley822_g241.txt sha256 017bb80b…): "El décimo tercer mes, o
  aguinaldo, hasta por la suma que no exceda lo dispuesto por el Código del Trabajo" is exempt (W5 review pass 2). The
  contract's annual wage does not say whether it includes the décimo tercer mes: input `niThirteenthMonth` (default
  false: no aguinaldo in `wages`); true = `wages` is thirteen equal monthly salaries, the thirteenth exempt (one month's
  salary, the Código del Trabajo amount, is taken as wages / 13; the Código's text itself was not read).
-/

namespace NiTax
open TaxKernel

/-- Ley 822 art. 23 (Gaceta 241/2012): impuesto base + porcentaje sobre exceso de. -/
def art23 : List CumRow :=
  [⟨0, 0, 0⟩, ⟨100000, 0, 1500⟩, ⟨200000, 15000, 2000⟩, ⟨350000, 45000, 2500⟩, ⟨500000, 82500, 3000⟩]
def art23Bands : Schedule := Schedule.ofList [(0, 0), (100000, 1500), (200000, 2000), (350000, 2500), (500000, 3000)]
/-- Art. 21 num. 1: 25 % of education, health and professional-service expenses, "hasta alcanzar un monto de veinte
mil cordobas (C$20,000.00) en el ano 2017". -/
def expenseRate : Int := 2500
def expenseCap : Int := 20000

structure Person where
  base : Int
  tax : Int
  deriving Repr

def person (wage inss expenses : Int) : Person :=
  let ded := pos inss + min (divR .down (pos expenses * expenseRate) BP) expenseCap
  let base := pos (pos wage - ded)
  { base, tax := divR .halfUp (cumTicks art23 base) BP }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let inss := (c.int? "niInss").getD 0
  let exps := (c.int? "niExpenses").getD 0
  let thirteen := (c.bool? "niThirteenthMonth").getD false
  let taxableWage (w : Int) : Int := if thirteen then w - divR .down (pos w) 13 else w
  /- W5 review pass 2: art. 21 num. 2 deducts each person's own contributions from that person's rentas del trabajo; the
  household total `niInss` is allotted in proportion to wages (the first adult takes the remainder), not halved (a
  halved total gave a one-earner couple half its deduction). -/
  let wsum := sumInts (c.adults.map fun a => pos a.wages)
  let inssShares : List Int :=
    if n != 2 then [inss] else if wsum = 0 then sh inss else
      let w1 := pos ((c.adults.getD 1 default).wages)
      let s2 := divR .down (inss * w1) wsum
      [inss - s2, s2]
  let ps := ((c.adults.zip inssShares).zip (sh exps)).map fun ((a, s), e) => person (taxableWage a.wages) s e
  let unsup :=
    ["INSS employee contribution (Ley de Seguridad Social and its regulation, not reached): pass niInss (annual household total, allotted by wages; deductible, art. 21 num. 2) or the base is overstated; employeeSocial = niInss",
     "Ley 822 as of Ley 891 (2014); later reforms (Ley 987/2019 and after) not reached",
     "art. 21 num. 1 expenses need niExpenses; taken as 0",
     "art. 19 num. 2 décimo tercer mes exempt only with niThirteenthMonth (wages = 13 equal salaries); default: none in wages"] ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: IR de actividades economicas not modelled; ignored"] else []) ++
    (if c.interest != 0 || c.dividends != 0 || c.rentalIncome != 0 || c.capitalGains != 0 then ["capital income (rentas de capital y ganancias de capital, arts. 80-89) not modelled; ignored"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pensions: not modelled"] else [])
  Out.make c "NI" "NIO" (sumInts (ps.map (·.tax))) (employeeSocial := pos inss)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.base)))])
    (unsupported := unsup)

def country : Country :=
  { code := "NI", name := "Nicaragua (IR rentas del trabajo, Ley 822)", currency := "NIO", year := "2025",
    compute := out }

#guard (person 100000 0 0).tax == 0
#guard (person 200000 0 0).tax == 15000

end NiTax

/- W5 review pass 2: 13 salaries of 10,000 (wages 130,000), no INSS: the thirteenth is exempt (art. 19 num. 2), base
120,000, tax 15 % x 20,000 = 3,000; without the input the base is 130,000 and the tax 4,500. -/
#guard (NiTax.person (130000 - 130000 / 13) 0 0).tax = 3000 ∧ (NiTax.person 130000 0 0).tax = 4500

