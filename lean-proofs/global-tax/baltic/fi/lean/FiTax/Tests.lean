import FiTax.Theorems

/-!
# Official and independent worked figures, checked by `decide` (cents)

Referees (all recomputed in full by `harness/referees.py` and `b38.py oecd`; a sample is fixed here as theorems):
* OECD Taxing Wages 2025, FIN (`~/cmp20/baltic/oecd/tw_cou_baltic.json`), at the OECD's average municipal rate 7,54 %;
* Kela, "Kokonaiseläkkeen ja nettoeläkkeen määrät 2025" (refs/kela_elaketulo_verotaulukko.txt);
* Verohallinto, "Verohallinto laskee nämä vähennykset automaattisesti" (refs/vero_automaattiset_vahennykset.txt);
* the government proposals HE 108/2024 and HE 98/2025 (two of their thresholds are wrong: `Loopholes.lean`).
-/

namespace FiTax
open TaxKernel

def avgRates : Rates := { municipal := averageMunicipalRate }

/-- OECD S100 (wage 55 462,10): CGTC 49 953,45; CGITLETC 10 218,85; BTC 2 400,36; SLT 3 766,49; EECSSC_PTI 529,51;
EECSSC_PGE 4 758,65; the YLE tax 160 inside CGITFP 7 978,49 (= 10 218,85 − 2 400,36 + 160). -/
theorem oecd_s100 :
    let s := stage avgRates { wages := 5546210 }
    s.taxable = 4995345 ∧ s.stateBefore = 1021885 ∧ s.workCredit = 240036 ∧ s.afterWork.municipal = 376649 ∧
    s.afterWork.medical = 52951 ∧ s.contributions = 475865 ∧ s.afterWork.state + s.yle = 797849 := by decide

/-- OECD S67 (wage 37 159,61): CGITLETC 5 157,38; BTC 2 955,06; SLT 2 504,89; CGITFP 2 362,32. (CGTC: ours
33 221,32, the OECD 33 221,31: a cent of rounding in the contributions.) -/
theorem oecd_s67 :
    let s := stage avgRates { wages := 3715961 }
    s.stateBefore = 515738 ∧ s.workCredit = 295506 ∧ s.afterWork.municipal = 250489 ∧
    s.afterWork.state + s.yle = 236232 := by decide

/-- OECD SP67: the sole parent of two gets the doubled child increase, 4 × 50 € (BTC 3 155,06; CGITFP 2 162,32). -/
theorem oecd_sp67 :
    let s := stage avgRates { wages := 3715961, kids := 2, sole := true }
    s.workCredit = 315506 ∧ s.afterWork.state + s.yle = 216232 := by decide

/-- OECD CTGG 2025: two children 2 396,64 €/year (couple), 4 155,84 (single parent). -/
theorem oecd_ctgg : 12 * childBenefitMonth [11, 6] false = 239664 ∧ 12 * childBenefitMonth [11, 6] true = 415584 := by
  decide

/-- Kela 2025, single pensioner, työeläke 1 750 €/month: tax 244,87 €/month at 7,54 % (×12 = 2 938,44; ours
2 938,43 for the year: Kela rounds the month). And 986,30 €/month of pensions (the guarantee-pension level): 0. -/
theorem kela_1750 : (finishAlone (stage avgRates { age := 70, pension := 2100000 }) { age := 70, pension := 2100000 } 0
    |> fun x => x.stateTotal + x.st.yle + x.local + x.employee) = 293843 := by decide
theorem kela_guarantee : (finishAlone (stage avgRates { age := 70, pension := 1183560 }) { age := 70, pension := 1183560 } 0
    |> fun x => x.stateTotal + x.st.yle + x.local + x.employee) = 0 := by decide

/-- Vero 2025: "Eläketulovähennys on enintään 11 030 euroa"; "Saat eläketulovähennyksen vuonna 2025, jos puhtaat
ansiotulosi ovat enintään 48 930 euroa"; "Perusvähennystä ei voi saada osittaisenakaan, jos puhdas ansiotulo ... yli
26 976 euroa"; "ennen vuoden 2025 alkua täyttänyt 65 vuotta, työtulovähennys on enintään 4 425 euroa". -/
theorem vero_pension_full : pensionDeductionFull = eur 11030 := by decide
theorem vero_pension_end : 0 < pensionDed { age := 70, pension := 4893000 } ∧ pensionDed { age := 70, pension := 4893100 } = 0 := by
  decide
theorem vero_basic_end : 0 < basicDed 2697600 ∧ basicDed 2697700 = 0 := by decide
theorem vero_workcredit_65 : workCreditMaxOf { age := 66 } = eur 4425 := by decide

end FiTax
