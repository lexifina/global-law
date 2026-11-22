import TaxKernel.World

/-!
# Monaco 2025: no personal income tax on residents' wages (French nationals excepted); employee contributions

Sources (read 2026-11-20; `mc/law/`). Access tier B: the rates and ceilings come from the Caisses Sociales de
Monaco's published tables (official secondary), in the Internet Archive copies of their page "Cotisations" for an
employer (captures 2025-04-21, 2025-09-10 and 2025-12-15, `csm_cotis_*.txt`); the ordonnances and arrêtés
ministériels that fix them were not read.
* C.A.R. (Caisse Autonome des Retraites), employee "Salarié 01/10/2024 6,15 % 0,70 % - 6,85 %"; ceiling "C.A.R.
  01/10/2024 6 028,00 €" a month, and "C.A.R. 01/10/2025 6 112,00 €" (the rate unchanged at 6,85 %).
* Assurance chômage: "Salarié 01/01/2025 2,40 %" (and from 01/05/2025, unchanged); ceiling "15 700,00 €" a month
  (from 01/01/2025 and 01/05/2025; four French social security ceilings).
* CMRC (complementary pensions): Tranche A ceiling "3.947 €" (from 1 October 2024) and "3 971 €" (from 1 October
  2025); rates TA "7,87 % d'acquisition des droits" + "2,15 % non générateur de droits", TB (between TA and 8 TA)
  "21,59 %" + "2,70 %"; "Répartition de la cotisation 60 % pour l'employeur et 40 % pour le salarié".
  Employee: TA 40 % × 10,02 % = 4,008 %; TB 40 % × 24,29 % = 9,716 %.
* C.C.S.S. (health and family): employer only ("Employeur 13,15 %").
2025 = 9 months (January-September) under the October 2024 ceilings + 3 months (October-December) under the
October 2025 ceilings; wages spread evenly over 12 months.

Income tax: none of the texts read levies a tax on residents' wages; by the Franco-Monegasque tax convention of
18 May 1963 French nationals resident in Monaco pay French income tax (not modelled: `"nationality": "french"` →
`unsupported`). The absence of a Monegasque personal income tax is not established from a text read (FINDINGS F1).
-/

namespace McTax
open TaxKernel

/-- Rates in parts per million. -/
def carRate : Int := 68500
def unempRate : Int := 24000
def cmrcA : Int := 40080      -- 40 % × (7,87 % + 2,15 %)
def cmrcB : Int := 97160      -- 40 % × (21,59 % + 2,70 %)

/-- Monthly ceilings for a period. -/
structure Period where
  months : Int
  car : Int
  unemp : Int
  ta : Int

def p1 : Period := { months := 9, car := 6028, unemp := 15700, ta := 3947 }   -- January-September 2025
def p2 : Period := { months := 3, car := 6112, unemp := 15700, ta := 3971 }   -- October-December 2025
def periods : List Period := [p1, p2]

/-- Annual wage `w` capped at a monthly ceiling `m` (annualised). -/
def capA (m w : Int) : Int := min (pos w) (12 * m)

/-- Each period's share of the year: months/12 of the annualised base × rate (ppm); ticks = € × ppm × months. -/
def carTicks (w : Int) : Int := sumInts (periods.map fun p => p.months * carRate * capA p.car w)
def unempTicks (w : Int) : Int := sumInts (periods.map fun p => p.months * unempRate * capA p.unemp w)
def cmrcTicks (w : Int) : Int :=
  sumInts (periods.map fun p => p.months * (cmrcA * capA p.ta w + cmrcB * (capA (8 * p.ta) w - capA p.ta w)))

def toEuros (t : Int) : Int := divR .down t (12 * 1000000)

def car (w : Int) : Int := toEuros (carTicks w)
def unemp (w : Int) : Int := toEuros (unempTicks w)
def cmrc (w : Int) : Int := toEuros (cmrcTicks w)

def out (c : Canon) : Out :=
  let ws := c.adults.map (·.wages)
  let a := sumInts (ws.map car); let u := sumInts (ws.map unemp); let m := sumInts (ws.map cmrc)
  let uns :=
    (if c.str? "nationality" = some "french" then
      ["French national resident in Monaco: French income tax under the 1963 Franco-Monegasque convention, not modelled"] else [])
    ++ (if c.adults.any (fun a => a.selfEmployment > 0) then ["self-employed (CAMTI/CARTI) contributions not modelled"] else [])
  Out.make c "MC" "EUR" 0 (employeeSocial := a + u + m)
    (detail := [Out.d "car" a, Out.d "unemploymentInsurance" u, Out.d "cmrc" m,
      Out.dStr "note" "no Monegasque tax on residents' wages; rates and ceilings: Caisses Sociales de Monaco tables (official secondary)"])
    (unsupported := uns)

def country : Country :=
  { code := "MC", name := "Monaco (private-sector employee)", currency := "EUR", year := "2025", compute := out }

end McTax
