import TaxKernel.Global
import R5Common

/-!
# Cyprus 2025: Special Defence Contribution on passive income and Capital Gains Tax (1100)

The 1.x model (`cytax`) already charges SDC on the household's own dividends, interest and rents (its surtaxes
`SDC_dividends`, `SDC_interest`, `SDC_rent`): this family charges SDC only on the extra income items of a global line
(`incomes`), so nothing is counted twice (finding R5-CY-1: a first draft charged the household fields again).

* Special Defence Contribution Law 117(Ι)/2002, cylaw consolidation as of 2025-11-07
  (`law/sdc_117_2002_as_of_2025-11-07.txt`), s. 3(1): (α) dividends from a resident company "σε ποσοστό δεκαεπτά τοις
  εκατό (17%)"; (β) interest "σε ποσοστό δεκαεπτά τοις εκατόν (17%)"; (δ) rents "σε ποσοστό τρία τοις εκατόν (3%) επί
  του ποσού των ακαθαρίστων ενοικίων μειωμένων κατά ποσοστό εικοσιπέντε τοις εκατόν (25%)". Charged on persons
  resident and domiciled in Cyprus: none with the 1.x option `--non-dom`.
* Capital Gains Tax Law 52/1980, cylaw page as archived on 2025-04-19 (`law/cgt_2025-04-19.html`, ARCHIVE_INDEX.tsv;
  the registry's later copy carries Law 242(Ι)/2025, which raises the limits from 2026): s. 4 "φόρος κατά συντελεστήν
  είκοσι τοις εκατόν" on gains from disposals of immovable property in Cyprus; s. 5(1) no tax while an individual's
  total gains do not exceed "δέκα χιλιάδων λιρών" (lifetime; taken as unused); s. 5(2) a main residence used for at
  least five years: no tax on a gain up to "πενήντα χιλιάδων λιρών". Pounds are converted at the irrevocable euro rate
  CYP 0,585274 per euro (euro changeover; not read here: grade B for the two limits): 17 086 and 85 430 euros.
  Indexation of the cost (s. 6) is not applied.
-/

namespace CyGlobal
open TaxKernel TaxKernel.Global R5Common

def cypToEur (cyp : Int) : Int := divR .down (cyp * 1000000) 585274

def cgtGeneral : Int := cypToEur 10000
def cgtMainHome : Int := cypToEur 50000

#guard cgtGeneral == 17086
#guard cgtMainHome == 85430

def incomesOf (g : CanonGlobal) (k : IncomeKind) : Int := isum ((g.incomes.filter (·.kind == k)).map (·.amount))

/-- s. 3(1)(δ): 3 % of gross rents less 25 %. -/
def sdcRent (rent : Int) : Int := divR .down (300 * divR .down (7500 * pos rent) BP) BP

def cgtTaxable (d : Disposal) : Int :=
  let gain := d.proceeds - d.cost - d.costs
  if d.mainHome then pos (gain - cgtMainHome) else gain

def capital : Family :=
  { name := "1100 έκτακτη εισφορά για την άμυνα, φόρος κεφαλαιουχικών κερδών", covers := [],
    run := fun args g _ =>
      if g.entity == .company then [] else
      let h := g.household
      let dom := !args.contains "--non-dom"
      let _ := h
      let div := incomesOf g .dividend
      let int := incomesOf g .interest
      let rent := incomesOf g .rent
      let props := g.disposals.filter (·.kind.isRealEstate)
      (if dom && (div ≠ 0 || int ≠ 0 || rent ≠ 0) then
        [charge .pit "Έκτακτη εισφορά για την άμυνα (μερίσματα)" div pos (fun x => divR .down (1700 * x) BP) (event := "dividends")
           (statute := "SDC Law 117(Ι)/2002 s. 3(1)(α) (17 %)"),
         charge .pit "Έκτακτη εισφορά για την άμυνα (τόκοι)" int pos (fun x => divR .down (1700 * x) BP) (event := "interest")
           (statute := "SDC Law s. 3(1)(β) (17 %)"),
         charge .pit "Έκτακτη εισφορά για την άμυνα (ενοίκια)" rent (fun x => divR .down (7500 * pos x) BP) (fun x => divR .down (300 * x) BP)
           (event := "rents") (statute := "SDC Law s. 3(1)(δ) (3 % of rents less 25 %)")] else [])
      ++ (if props.isEmpty then [] else
        [charge .pit "Φόρος Κεφαλαιουχικών Κερδών" (isum (props.map fun d => d.proceeds - d.cost - d.costs))
           (fun _ => pos (isum (props.map cgtTaxable) - cgtGeneral)) (fun x => divR .down (2000 * x) BP) (event := "immovable property")
           (statute := "CGT Law 52/1980 s. 4 (20 %), s. 5(1) (CYP 10 000 lifetime), s. 5(2) (main home CYP 50 000)")]) }

def capitalUnsupported (g : CanonGlobal) : List String :=
  (if g.disposals.any (·.kind.isRealEstate) then ["CGT: the lifetime exemption is taken as unused; cost indexation (s. 6) not applied"] else [])
  ++ (if g.disposals.any (·.kind.isShares) then ["gains on shares are outside CGT unless the company holds Cypriot immovable property (s. 2): not computed"] else [])

#guard sdcRent 10000 == 225
#guard cgtTaxable { kind := .home, proceeds := 300000, cost := 200000, mainHome := true } == 100000 - 85430

end CyGlobal
