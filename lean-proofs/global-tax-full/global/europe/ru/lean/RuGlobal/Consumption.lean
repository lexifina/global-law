import RuGlobal.Pit

/-!
# RU 2025: Налог на добавленную стоимость (5111); excises not modelled in this pass

Source: PwC Worldwide Tax Summaries, Russian Federation, Corporate - Other taxes, accessed 2022-01-17 (Wayback capture; `ru/law/pwc_other_wb2025.html`; PwC no longer publishes the page), checked against Федеральный закон от 12.07.2024 № 176-ФЗ (kremlin.ru, the 1.x model's `fz176_2024_clean.txt`): its amendments to ст. 164 add п. 8 and change п. 4 only; sha256 in `law/SHA256SUMS`.
* VAT 20 % (18 % before 2019); 10 %: some basic foods, children's clothes, medicines, medical goods, printed matter (PwC page reviewed 12 February 2021)
* 176-ФЗ ст. 2 п. 5: "в статье 164: а) в пункте 4 слова \"пунктом 2 или 3\" заменить словами \"пунктом 2, 3 или 8\"; б) дополнить пунктом 8 ..." (5 % / 7 % for simplified-regime taxpayers): п. 2-3 unchanged for 2025
-/

namespace RuGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Налог на добавленную стоимость", standard := 2000, reduced := 1000, threshold := 0,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .medicines | .books | .newspapers => .reduced
      | _ => .standard }

def vatStatute : String := "Налоговый кодекс РФ ст. 164 п. 2 (10 %), п. 3 (20 %); п. 8 (5 % / 7 %, УСН, from 1.1.2025, 176-ФЗ)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Налог на добавленную стоимость", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["RU 5111: PwC 2021 review (rates of п. 2-3 unchanged in 2025 per 176-ФЗ)", "RU 5111 Налог на добавленную стоимость: back to A (pass 17, 2025 text read)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the EU-style structure the source describes (health, education, finance, insurance, residential rent), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["food at 10 % (some basic foods only: the 10 % list of п. 2 not read item by item)"] else [])
  ++ (if g.entity == .company then ["exemption of ст. 145 (revenue thresholds) and the 5 % / 7 % simplified-regime rates of п. 8 not modelled: every company line taxed at 20 %"] else [])
  ++ (if !g.consumption.isEmpty then ["ст. 164 itself not read (consultant.ru is script-built); rates from PwC"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Налоговый кодекс РФ гл. 22 (not read)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12000 } == 2000
#guard vat.embedded { good := .food, amount := 11000 } == 1000

end RuGlobal.Consumption
