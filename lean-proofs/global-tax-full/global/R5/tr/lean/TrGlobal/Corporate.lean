import TaxKernel.Global
import R5Common

/-!
# Türkiye 2025: Kurumlar Vergisi (1200) and withholding on non-residents

Source: Kurumlar Vergisi Kanunu No. 5520, mevzuat.gov.tr consolidated PDF (`law/tr_5520.pdf`; current text whose
change notes date every amendment; the provisions used carry no change in force after 2025 except 32/C(2)(d), added
21/5/2026 and not used):
* art. 32(1) (7394/25, 2022): "Kurumlar vergisi, kurum kazancı üzerinden %25 oranında alınır" (banks, insurers and other
  financial institutions 30 %: flag `financial`).
* art. 32/C(1) (7524/36, 28/7/2024; domestic minimum corporate tax, first applied to 2025 earnings): the tax "indirim ve
  istisnalar düşülmeden önceki kurum kazancının %10'undan az olamaz" (the deductions of 32/C(2) are not modelled).
* art. 9(1)(a): losses of the previous five years deducted in full.
* art. 5(1)(a): dividends from a full-taxpayer resident company exempt (any stake).
* art. 30(1), (3): non-residents: "% 15 oranında kurumlar vergisi kesintisi" on the listed income (services, royalties,
  interest, rents) and on dividends; the President may vary the rates (decisions, e.g. CK 9707 on dividends, not
  read): grade B for the withholding.
-/

namespace TrGlobal
open TaxKernel TaxKernel.Global R5Common

def ktRate (co : Company) : Int := if co.flags.contains "financial" then 3000 else 2500

def kv (co : Company) : CorpRegime :=
  { name := "Kurumlar Vergisi", sched := Schedule.flat (ktRate co), participationBp := 10000 }

/-- art. 32/C: the higher of the regular tax and 10 % of profit before exemptions and deductions. -/
def kvDue (co : Company) : Int := max ((kv co).citTax co) (divR .down (1000 * pos (co.profit + co.addBacks)) BP)

def whtNonResident : Wht :=
  { name := "Kurumlar vergisi kesintisi (dar mükellef)",
    rules := [.dividend, .interest, .royalty, .rent, .services].map fun k =>
      { kind := k, rateBp := 1500, statute := "KVK art. 30(1), (3) (15 %; Presidential decisions not read)" } }

def corporate : Family :=
  { name := "1200 kurumlar vergisi", covers := [.cit, .incomeOther],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      [charge .cit "Kurumlar Vergisi" ((kv co).beforeLosses co) (fun _ => (kv co).taxableProfit co) (fun _ => kvDue co)
        (statute := s!"KVK art. 32(1) ({ktRate co / 100} %), art. 32/C (10 % minimum), art. 9 (losses), art. 5(1)(a)")]
      ++ whtNonResident.charges co }

def corporateUnsupported (g : CanonGlobal) : List String :=
  corpInputsUnread g false true false false
  ++ (if g.entity == .company then ["KVK 32/C(2) exclusions from the minimum-tax base not modelled; art. 30 rates as printed (15 %), Presidential decisions not read"] else [])

#guard kvDue { profit := 1000000 } == 250000
-- losses wipe the regular tax; the 10 % minimum on profit before deductions remains
#guard kvDue { profit := 1000000, lossesForward := 900000 } == 100000
#guard kvDue { profit := 1000000, dividendsReceived := 400000, participationBp := 100 } == 150000

end TrGlobal
