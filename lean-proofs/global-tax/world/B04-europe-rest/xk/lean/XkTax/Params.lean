import TaxKernel.World

/-!
# Kosovo 2025: parameters, each with its dated source (whole euros)

Sources (Global law, corpus `kosovo/national/acts`, as enacted, Official Gazette gzk.rks-gov.net; copies in `../src/`):
* Ligji Nr. 05/L-028 për tatimin në të ardhurat personale (in force 2015-09-01). The corpus file names are offset
  from the article numbers; cites below use the "Neni" heading printed in the text.
* Ligji Nr. 08/L-142 (published 23.08.2024, in force on publication, neni 7), neni 5: replaces neni 6 of 05/L-028
  (the rate table). The Gazette's page for 05/L-028 (https://gzk.rks-gov.net/ActDetail.aspx?ActID=11014) lists
  08/L-142 as its only amending act.
* Ligji Nr. 04/L-101 për fondet pensionale të Kosovës, neni 6.2; Ligji Nr. 05/L-116 (amending it), neni 37.2.
-/

namespace XkTax
open TaxKernel

/-- 05/L-028 neni 6 as replaced by 08/L-142 neni 5: "deri në tremijë euro (3.000 €) ... zero për qind (0%)"; "mbi
tremijë euro (3.000 €), deri në pesëmijë e katërqind (5.400 €) ... tetë për qind (8%)"; "mbi pesëmijë e katërqind
(5,400 €), njëqind nëntëdhjetë e dy euro (192 €) plus dhjetë për qind (10%)" (annual taxable income). -/
def schedule : Schedule := Schedule.ofList [(0, 0), (3000, 800), (5400, 1000)]

/-- The rate table as printed: lower limit, tax at the limit, marginal rate (08/L-142 neni 5). -/
def printed : List CumRow := [⟨0, 0, 0⟩, ⟨3000, 0, 800⟩, ⟨5400, 192, 1000⟩]

/-- The table replaced by 08/L-142 (05/L-028 neni 6 as enacted, in force until 22.08.2024): 0 % to 960, 4 % to 3 000,
8 % to 5 400 ("81.6 €"), 10 % above ("273.6 €"); amounts in cents for the printed 81.6 and 273.6. Used only for the
2024 comparison (FINDINGS F2). -/
def schedule2015 : Schedule := Schedule.ofList [(0, 0), (960, 400), (3000, 800), (5400, 1000)]

/-- 04/L-101 neni 6.2 (b): "çdo punonjës paguan një shumë që është baras me pesë përqind (5%) të rrogës së tërësishme
të tij". -/
def pensionEmployee : Int := 500

/-- 05/L-116 neni 37.2: "Kontributet e dhëna nga punonjësi në FKPK ... nuk janë subjekt i tatimit mbi të ardhurat
personale"; 05/L-028 neni 15 (2): pension contributions are deductible. -/
def pensionDeductible : Bool := true

/-- 05/L-028 neni 27: rent without records: "një zbritje ... dhjetë për qind (10%) të qirave të pranuara". -/
def rentLumpRate : Int := 1000

end XkTax
