import ClGlobal.Pit

/-!
# Chile 2025: 1200 primera categoría and impuesto adicional (pilot, unchanged)

* **LIR** (DL 824, idNorma 6368, version 2025-07-01; last amendment note D.O. 14.02.2025):
  - art. 20 inc. 1 (Ley 21.210): "un impuesto de 25% … para los contribuyentes que se acojan al Régimen Pro Pyme
    contenido en la letra D) del artículo 14, la tasa será de 25%. En el caso de los contribuyentes sujetos al
    régimen del artículo 14 letra A, el impuesto será de 27%".
  - art. 14 D N° 1 (b): Pro Pyme if the 3-year average of gross income ≤ 75.000 UF (one year seen: that year's
    turnover, with the `proPyme` flag, the regime being an option of the company).
  - art. 58 N° 2: impuesto adicional "con tasa del 35%" on dividends to non-residents; art. 63: credit = the
    first-category rate on the amounts in the base, and the non-treaty restitution "una cantidad equivalente al 35%
    del monto del referido crédito"; art. 59: royalties 30 % (inc. 1), interest 35 % (inc. 4); pass 7: services N° 2 15 % (engineering, technical and
    professional services, "sea que se presten en Chile o el exterior"; other services abroad 35 %).
-/

namespace ClGlobal.Corporate
open TaxKernel TaxKernel.Global ClGlobal

def isProPyme (co : Company) : Bool := co.flags.contains "proPyme" && decide (co.turnover ≤ ufToPesos 75000)
def idpcRate (co : Company) : Int := if isProPyme co then 2500 else 2700

def idpc (co : Company) : CorpRegime := { name := "Impuesto de primera categoría", sched := Schedule.flat (idpcRate co) }

/-- art. 58 N° 2 + art. 63: impuesto adicional on a dividend paid to a non-resident out of profits taxed at `t`. -/
def adicionalDividend (t div : Int) : Int :=
  let base := divR .down (pos div * BP) (BP - t)
  let credit := divR .down (t * base) BP
  pos (divR .down (3500 * base) BP - credit + divR .down (3500 * credit) BP)

#guard adicionalDividend 2700 7300 == 1745

def whtOther : Wht :=
  { name := "Impuesto adicional (retención)",
    rules := [{ kind := .royalty, rateBp := 3000, statute := "LIR art. 59 inc. 1 (30 %)" },
              { kind := .interest, rateBp := 3500, statute := "LIR art. 59 inc. 4 (35 %)" },
              { kind := .services, rateBp := 1500, statute := "LIR art. 59 inc. 4 N° 2: trabajos de ingeniería o técnicos y servicios profesionales o técnicos, en Chile o el exterior (15 %)" }] }

def corporate : Family :=
  { name := "1200 primera categoría, impuesto adicional", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := { g.company with lossesForward := 0 }
      let r := idpc co
      [r.citCharge co s!"LIR art. 20 inc. 1: {if isProPyme co then "Pro Pyme (art. 14 D) 25 %" else "art. 14 A 27 %"}"]
      ++ ((co.paymentsAbroad.zipIdx.filter fun (p, _) => p.kind == .dividend).map fun (p, i) =>
            charge (if p.toCompany then .cit else .pit) "Impuesto adicional (dividendos)" p.amount id
              (fun x => adicionalDividend (idpcRate co) x) (event := s!"payment {i + 1} (dividend)") (bearer := .withheld)
              (statute := "LIR art. 58 N° 2, art. 63 (credit and 35 % restitution)"))
      ++ whtOther.charges { co with paymentsAbroad := co.paymentsAbroad.filter (·.kind != .dividend) } }

def families : List Family := [corporate]
def absent : List Absent := []
def notes : List String := ["Chile 2025 (pilot integrated in R2): LIR, DL 825 and Ley 16.271 as in force on 2025-07-01"]
def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.company.lossesForward ≠ 0 then ["losses brought forward: LIR art. 31 N° 3 not read in this pilot; not offset"] else [])
  ++ (if g.company.debt ≠ 0 then ["thin capitalisation (LIR art. 41 F, 35 % on excess interest) not modelled"] else [])
  ++ (if g.company.paymentsAbroad.any (·.kind == .services) then ["services abroad taken as technical or professional (LIR art. 59 N° 2, 15 %): other services 35 % and the art. 59 N° 2 exemptions (freight, commissions on exports ...) not distinguished"] else [])

#guard (idpc { profit := 100000000 }).citTax { profit := 100000000 } == 27000000
#guard (idpc { profit := 100000000, flags := ["proPyme"], turnover := 500000000 }).citTax { profit := 100000000 } == 25000000

#guard whtOther.amount { kind := .services, amount := 1000000 } == 150000

end ClGlobal.Corporate
