import UyGlobal.Pit

/-!
# Uruguay 2025: employer special social security contributions (2200)

Source: BPS, "Tributación y recaudación de Contribuciones Especiales de Seguridad Social", edición 2026 (bps.gub.uy file
24270, fetched 2026-11-21): "Tasas de aporte jubilatorio para Industria y Comercio: Aporte personal 15 % | Aporte
patronal 7,5 %"; Fonasa "Los aportes patronales se componen de un aporte básico del 5 % y el complemento de cuota mutual
... El aguinaldo se encuentra exonerado del aporte patronal (5 %)"; Fondo de Reconversión Laboral "Desde el 1 de enero
de 2019 ... Aporte patronal 0,10 %"; Fondo de Garantía de Créditos Laborales "una tasa de 0,025 % de carácter
patronal" (ley 19.690). Grade B (official guide, 2026 edition; the rates date from 2019 or earlier). Not applied: the
tope de cotización of the jubilatorio contribution ($ 288.836 a month at 2/2026; 2025 value not reached, as in the 1.x
model), the aguinaldo exoneration from the Fonasa 5 %, and the complemento de cuota mutual.

**Pass 9 (2026-11-21):** Ley 16.713 (IMPO text, archived `uy/law/impo_ley16713.*`) art. 14 A): the régimen de solidaridad intergeneracional receives "Los aportes patronales jubilatorios sobre el total de asignaciones computables hasta $ 15.000 (quince mil pesos uruguayos) mensuales" (May 1995 values, adjusted under art. 12): the employer jubilatorio is capped; its 2025 value was not found (BPS pages, Wayback, one search), so the cap is still not applied (upper bound for wages above it).
-/

namespace UyGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon UyGlobal

def jub : Contribution := { name := "Aporte jubilatorio patronal", sched := Schedule.flat 750 }
def fonasa : Contribution := { name := "Fonasa aporte patronal básico", sched := Schedule.flat 500 }
def frl : Contribution := { name := "Fondo de Reconversión Laboral (patronal)", sched := Schedule.flat 10 }
def fam1 : Family := employerFamily "2200 BPS employer contributions" [jub, fonasa, frl] "BPS guide 2026: jubilatorio patronal 7.5 %; Fonasa 5 %; FRL 0.10 %" (inBp := 10000) (oecd := .sscEmployer) (level := .social)
def fgcl : Contribution := { name := "Fondo de Garantía de Créditos Laborales", sched := Schedule.flat 2 }
def fam2 : Family := employerFamily "2200 Fondo de Garantía de Créditos Laborales" [fgcl] "Ley 19.690 (BPS guide 2026): 0.025 %" (inBp := 10000) (oecd := .sscEmployer) (level := .social)

def families : List Family := [fam1, fam2]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.household.adults.any (·.wages > 0) || g.entity == .company) "BPS employer 7.5 % + 5 % + 0.1 % + 0.025 % without the jubilatorio cap (Ley 16.713 art. 14 A): employer jubilatorio on asignaciones up to $ 15,000 of May 1995, indexed (art. 12); 2025 value not reached: upper bound above it); aguinaldo exoneration from Fonasa and the complemento de cuota mutual not applied; FGCL 0.025 % charged at 0.02 % (basis-point resolution)"

#guard jub.amount 1000000 == 75000
#guard fonasa.amount 1000000 == 50000
#guard frl.amount 1000000 == 1000
#guard fgcl.amount 1000000 == 200

end UyGlobal.Social
