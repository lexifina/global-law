import DoGlobal.Pit

/-!
# Dominican Republic 2025: employer SDSS contributions (2200)

Source: Tesorería de la Seguridad Social, FAQ no. 13 "¿Cuáles son los porcentajes de retención y aporte de trabajador y
empleadores?" (page held by the 1.x builder, `world/B13-caribbean/do/law/tss_faq.txt`): Empleador "Seguro Familiar de
Salud 7.09%", "Seguro de Vejez, Discapacidad y Sobrevivencia 7.10%", Seguro de Riesgo Laboral "1% cuota fija más un
porciento variante de 0.10-0.30 dependiendo el factor de riesgo" (applied at the lowest, 1.10 %). The employee rates of
the same table (3.04 %, 2.87 %) are the 1.x model's for 2025. FAQ no. 14 caps (4, 10 and 20 salarios mínimos
cotizables) are shown only with the 2026 amount (RD$ 23,223 from 1 Feb 2026): no cap is applied (upper bound for
wages above 10 SMN a month), as in the 1.x model without `doSmn`. Grade B (official table read on the 2026 page; Ley
87-01 not read). INFOTEP 1 % (Ley 116-80) not modelled.

**Pass 9 (2026-11-21):** SDSS caps from the TSS resolutions on the salario minimo nacional (Wayback copies of tss.gob.do/assets/reso01-2024.pdf and reso01-2025.pdf, archived `do/law/tss_reso01-*`): Res. 01-2024 (from 1 Feb 2024) SRL RD$ 77,410, SFS RD$ 193,525, SVDS RD$ 387,050 a month; Res. 01-2025 (11 Mar 2025, from 1 Apr 2025, SMN RD$ 21,674.80) SRL RD$ 86,699.20, SFS RD$ 216,748, SVDS RD$ 433,496. Annual caps = 3 months at the first + 9 at the second (whole pesos). INFOTEP: Ley 116-80 art. 24 a) 1 % of the payroll of fixed salaries (G.O. 9522, 20 Jan 1980; archived `do/law/ley116-80_go9522_siteal.*`), grade A; the worker's 0.5 % on bonuses (art. 24 b) is not modelled.
-/

namespace DoGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon DoGlobal

/-- Annual caps 2025 (whole pesos): Jan-Mar at TSS Res. 01-2024 (from 1 Feb 2024), Apr-Dec at TSS Res. 01-2025
    (from 1 Apr 2025): SVDS 3 x 387,050 + 9 x 433,496; SFS 3 x 193,525 + 9 x 216,748; SRL 3 x 77,410 + 9 x 86,699.20. -/
def topeSvds : Int := 5062614
def topeSfs : Int := 2531307
def topeSrl : Int := 1012522
def sfs : Contribution := Contribution.flatCapped "Seguro Familiar de Salud (empleador)" 709 topeSfs
def svds : Contribution := Contribution.flatCapped "Seguro de Vejez, Discapacidad y Sobrevivencia (empleador)" 710 topeSvds
def srl : Contribution := Contribution.flatCapped "Seguro de Riesgo Laboral (empleador, lowest class)" 110 topeSrl
def fam1 : Family := employerFamily "2200 SDSS employer contributions" [sfs, svds, srl] "TSS FAQ no. 13: employer SFS 7.09 %, SVDS 7.10 %, SRL 1 % + 0.10 % (lowest risk factor); caps 10/20/4 salarios minimos (Ley 87-01 arts. 143, 57; CNSS Res. 151-10) at TSS Res. 01-2024 and 01-2025" (inBp := 10000) (oecd := .sscEmployer) (level := .social)
def infotep : Contribution := { name := "INFOTEP (empleador, 1 %)", sched := Schedule.flat 100 }
def fam2 : Family := employerFamily "3000 INFOTEP" [infotep] "Ley 116-80 art. 24 a): 1 % of the monthly payroll of fixed salaries" (inBp := 10000) (oecd := .payroll) (level := .central)

def families : List Family := [fam1, fam2]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "SDSS employer 7.09 % + 7.10 % + 1.10 % up to the 2025 caps (annual sums of the monthly caps: even monthly pay assumed); SRL at the lowest risk factor; INFOTEP 1 % on the whole wage (the 0.5 % worker share on bonuses not split)"

#guard sfs.amount 1000000 == 70900
#guard svds.amount 1000000 == 71000
#guard srl.amount 1000000 == 11000
#guard svds.amount 9000000 == svds.amount topeSvds
#guard sfs.amount 9000000 == sfs.amount topeSfs
#guard srl.amount 9000000 == srl.amount topeSrl
#guard infotep.amount 1000000 == 10000

end DoGlobal.Social
