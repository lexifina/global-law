import CnhkGlobal.Pit

/-!
# Hong Kong 2025/26: profits tax on corporations and the royalty charge on non-residents (1200)

Inland Revenue Ordinance (Cap. 112): text not fetched (elegislation.gov.hk is script-driven); rates from IRD tables (B).
* **s. 14, Sch. 8 Part 1**: two-tiered rates for corporations, 8.25 % on the first HK$2 m of assessable profits, 16.5 %
  above (from 2018/19; one entity per connected group).
* **s. 15 (1) (a)-(b), s. 21A**: royalties to non-residents deemed 30 % profit, so 4.95 % of the gross. No withholding
  on dividends or interest.
-/

namespace CnhkGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Profits tax (corporations)",
    sched := Schedule.ofList [(0, 825), (2000000, 1650)] }

def citStatute : String := "IRO (Cap. 112) s. 14 (1), (3) (b); Sch. 8B s. 2 (a): 8.25 % on assessable profits up to $2,000,000, 16.5 % above"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 0, statute := "IRO (Cap. 112) s. 26 (a): a dividend from a corporation chargeable to profits tax is not included in any other person's profits; no other charge on dividends" },
      { kind := .interest, rateBp := 0, statute := "IRO s. 14 (1) (profits tax only on persons carrying on business in Hong Kong), s. 15 (1) (f), (g), (i) (interest deemed a receipt only for persons carrying on business in Hong Kong): none on a non-resident lender" },
      { kind := .services, rateBp := 0, statute := "IRO s. 14 (1): profits tax only on profits arising in or derived from Hong Kong from a business carried on in Hong Kong; s. 20B (1) (b) covers only entertainers and sportsmen performing in Hong Kong" }] }


/-- IRO (Cap. 112, HKLII version of 25 Jul 2025) s. 15 (1) (b), s. 20B (charged in the payer's name, deducted from the
payment), s. 21A (1) (assessable profits 30 % of the sum; 100 % from an associate), Sch. 8A s. 2 (persons other than
corporations: 7.5 % to $2,000,000, 15 % above), Sch. 8B s. 2 (a) (corporations: 8.25 % / 16.5 %). -/
def sch8A : Schedule := Schedule.ofList [(0, 750), (2000000, 1500)]
def sch8B : Schedule := Schedule.ofList [(0, 825), (2000000, 1650)]
def royaltyProfit (p : Payment) : Int := if p.stakeBp > 5000 then pos p.amount else pos p.amount * 3 / 10
def royaltyTax (p : Payment) : Int := (if p.toCompany then sch8B else sch8A).tax {} (royaltyProfit p)

def royaltyCharges (co : Company) : List Charge :=
  co.paymentsAbroad.zipIdx.filterMap fun (p, i) =>
    if p.kind == .royalty then
      some (charge (if p.toCompany then .cit else .pit) "Profits tax on royalties of non-residents (charged in the payer's name)" p.amount
        (fun _ => royaltyProfit p) (fun b => (if p.toCompany then sch8B else sch8A).tax {} b)
        (event := s!"payment {i + 1} ({p.kind.name})") (bearer := .withheld)
        (statute := "IRO (Cap. 112) s. 15 (1) (b), s. 20B, s. 21A (1) (30 %; 100 % from an associate), Sch. 8A / 8B two-tiered rates"))
    else none


def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company
       ++ royaltyCharges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["global minimum tax (Cap. 112 Part 4AA, from 2025) not modelled"] else [])

#guard cit.citTax { profit := 3000000 } == 330000
#guard royaltyTax { kind := .royalty, amount := 1000000 } == 24750
#guard royaltyTax { kind := .royalty, amount := 1000000, toCompany := false } == 22500
#guard royaltyTax { kind := .royalty, amount := 10000000 } == 330000
#guard wht.amount { kind := .dividend, amount := 1000 } == 0

end CnhkGlobal.Corporate
