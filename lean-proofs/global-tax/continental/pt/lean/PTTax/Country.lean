import PTTax.Household

/-! # The contract: canonical household in, one output line out -/

namespace PTTax
open TaxKernel Lean

def toPersons (c : Canon) : List Person :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 2 then (if i = 0 then half1 x else half2 x) else x
  c.adults.zipIdx.map fun (a, i) =>
    { wages := (c.int? (if i = 0 then "pt_wagesCents1" else "pt_wagesCents2")).getD (eur a.wages), selfEmp := eur a.selfEmployment, pension := eur a.pension, age := a.age,
      jovemYear := (c.int? (if i = 0 then "pt_jovemYear1" else "pt_jovemYear2")).getD 0,
      interest := share (eur c.interest) i, dividends := share (eur c.dividends) i,
      gains := share (eur c.capitalGains) i, rent := share (eur c.rentalIncome) i }

/-- The cheapest of the household's legal choices (units × englobamento options), first one on ties. -/
def bestOf (l : List HouseCalc) : HouseCalc :=
  l.foldl (fun b h => if h.irs < b.irs then h else b) (l.headD default)

def units (c : Canon) (args : List String) : List String :=
  let forced := (c.str? "pt_unit").orElse fun _ =>
    if args.contains "--joint" then some "joint" else if args.contains "--separate" then some "separate" else none
  if c.isCouple && c.married then (match forced with | some u => [u] | none => ["joint", "separate"])
  else if c.isCouple then ["unmarried"] else ["single"]

def englobFrom (args : List String) : List Englob :=
  if args.contains "--no-englobamento" then [{}] else englobOptions

def out (args : List String) (c : Canon) : Out :=
  -- `--start-of-year` (Eurostat earn_net ESMS 3.4): the tax parameters in force on 1 January; for 2025 the art. 68
  -- table before Lei 55-A/2025 (the only mid-year change to a 2025 tax or contribution parameter in this model)
  let y := if args.contains "--start-of-year" && c.year = 2025 then y2025start else ypFor c.year
  let persons := toPersons c
  let ages := c.children.map (·.age)
  -- `--taxben-despesas-gerais` (convention, round 2): TaxBEN assumes every taxpayer has enough e-fatura general
  -- expenses for the full art. 78-B n.º 1 deduction (35 % up to 250 € each; 45 % up to 335 € single parents); the
  -- statute grants it only on invoices, so the default is none unless `pt_despesasGerais` is given.
  -- `--despesas-gerais-max` (EUROMOD convention, round 14): every taxpayer (each adult of an unmarried couple too) is
  -- given the full art. 78-B deduction, as EUROMOD's tin00_pt does with no expense condition ("Other expenses (despesas
  -- gerais)": $tintcox_amt1 250 per partner / single, $tintcox_amt2 335 per lone parent; EUROMOD policy parameters
  -- J2.0+.xlsx, sheet PT, "Tax credit: household general expenses").
  let gMax := args.contains "--despesas-gerais-max"
  let despGer := eur ((c.int? "pt_despesasGerais").getD
    (if gMax then 1000000 else if args.contains "--taxben-despesas-gerais" then 2000 else 0))
  let despGer2 := if gMax then eur 1000000 else 0
  let cands := (units c args).flatMap fun u => (englobFrom args).map fun e =>
    houseCalc persons ages despGer u e (args.contains "--bandsum") y despGer2
  let h := bestOf cands
  let bestOfUnit (u : String) : Option HouseCalc :=
    let l := cands.filter (·.unit == u); if l.isEmpty then none else some (bestOf l)
  let mono := persons.length == 1 && !ages.isEmpty
  let income := eur c.gross + (persons.map (·.wages)).foldl (· + ·) 0 - eur ((c.adults.map (·.wages)).foldl (· + ·) 0)
  let (ab, esc) := if y.abono then abono income ages mono (args.contains "--abono-annual") y else (0, 0)
  let d0 := h.decls.headD default
  let sumD (f : DeclCalc → Int) := (h.decls.map f).foldl (· + ·) 0
  let detail : List (String × Json) :=
    [Out.dStr "unit" h.unit,
     Out.dBool "englobCapital" h.englob.capital, Out.dBool "englobGains" h.englob.gains,
     Out.dBool "englobRent" h.englob.rent,
     Out.d "rendimentoColetavel_cents" (sumD (·.coletavel)),
     Out.d "minimoExistenciaAbate_cents" (sumD (·.meAbate)),
     Out.d "coletaArt68_cents" (sumD (·.coleta68)),
     Out.d "deducoesColeta_cents" (sumD (·.deductions)),
     Out.d "autonomousTax_cents" (sumD (·.autonomous)),
     Out.d "irsJovemExempt_cents" ((h.ps.map (·.exempt)).foldl (· + ·) 0),
     Out.d "dependentsDeduction_cents" (dependentsDeduction ages y),
     Out.d "taxYear" (y.year : Int), Out.dBool "abonoModelled" y.abono,
     Out.d "abonoEscalao" esc,
     Out.d "firstDeclColetavel_cents" d0.coletavel]
    ++ (match bestOfUnit "joint", bestOfUnit "separate" with
        | some j, some s => [Out.d "irsJoint_cents" j.irs, Out.d "irsSeparate_cents" s.irs]
        | _, _ => [])
  Out.make c "PT" "EUR" (h.irs - h.solidarity) (surtaxes := [("taxaAdicionalSolidariedade", h.solidarity)])
    (employeeSocial := h.ss) (benefits := ab) (detail := detail)
    (unsupported := ["deduções à coleta that need invoices (saúde, educação, habitação, lares, IVA) and despesas "
      ++ "gerais unless pt_despesasGerais is given", "PPR and other EBF benefits (pensionContributions, charitable)",
      "municipal IRS participation (RFALEI art. 26: 0-5 % returned by the município)",
      "Azores/Madeira regional rates", "categoria B other than art. 151 professional services; organised accounts",
      "abono: garantia para a infância complement, bonificação por deficiência"]
      ++ (if yearSupported c.year then [] else [s!"tax year {c.year} not implemented: 2025 rules applied"])
      ++ (if y.abono then [] else ["abono de família amounts for this year not modelled (benefits 0)"])
      ++ (if y.jovem || persons.all (·.jovemYear == 0) then [] else ["IRS Jovem before 2025 not modelled"]))

def country : Country :=
  { code := "PT", name := "Portugal (mainland)", currency := "EUR", year := "2022-2025",
    compute := out [], computeWith := out }

end PTTax
