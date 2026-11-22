import TaxKernel.World

/-!
# Holy See / Vatican City State: no tax on income, 2025

Access tier B (rescue pass 2). Official texts on vatican.va (saved in `va/law/rescue2/`):
* Patti Lateranensi, Trattato (11 February 1929), art. 17: "Le retribuzioni, di qualsiasi natura, dovute dalla Santa
  Sede, dagli altri enti centrali della Chiesa Cattolica e dagli enti gestiti direttamente dalla Santa Sede anche fuori
  di Roma, a dignitari, impiegati e salariati, anche non stabili, saranno nel territorio italiano esenti, a decorrere
  dal 1° gennaio 1929, da qualsiasi tributo tanto verso lo Stato quanto verso ogni altro ente." (exemption from Italian
  taxes; `patti.html`).
* No Vatican text levies a tax on income: the Legge fondamentale and the Legge sulle fonti del diritto (Global law
  `vatican-city/national/acts`) hold no "imposta" or "tribut*"; the vaticanstate.va legislation index (read in the
  build and rescue passes) lists no tax law. This is an absence, written down as such: no statute says "there is no
  income tax".
* Pension contributions: Regolamento per le Pensioni (AAS 84 (1992) pp. 1033-1052, art. 8): a contribution of 20 % of
  the ordinary pay "comprensivo della quota a carico del dipendente", with "la corrispondente ritenuta del 5% a carico
  di ciascun dipendente"; art. 8(5): rates may be varied by the Secretary of State. Replaced from 1 January 2004 by the
  Regolamento Generale del Fondo Pensioni (AAS 96 (2004), April issue), art. 15(2): "La misura del contributo
  percentuale ... e della quota a carico del dipendente è stabilita, tempo per tempo, dal Cardinale Segretario di
  Stato." The only later rate decision found in the AAS (1993-2026, scanned) is the Rescriptum of 6 April 2009 raising
  the Administrations' share of the ordinary account from 25 % to 26 % (and the Gendarmeria's from 31.25 % to 33 %)
  from 1 January 2010; the employee's share in force in 2025 is not published there. Contributions: unsupported.
Model: income tax 0 for every household; employee contributions unsupported.
-/

namespace VaTax
open TaxKernel

def out (c : Canon) : Out :=
  Out.make c "VA" "EUR" 0 (employeeSocial := 0)
    (detail := [Out.dStr "note" "No tax on income: no Vatican text levies one (Legge fondamentale, Legge sulle fonti, vaticanstate.va index); Holy See remuneration exempt from Italian taxes (Lateran Treaty art. 17)"])
    (unsupported := ["Fondo Pensioni employee contribution: rate set 'tempo per tempo' by the Secretary of State (Regolamento Generale 2004 art. 15(2)); the 2025 rate is not published (last published: 5 %, Regolamento 1992 art. 8(2)); employeeSocial = 0"])

def country : Country := { code := "VA", name := "Holy See (Vatican City State)", currency := "EUR", year := "2025", compute := out }

#guard (out { id := "g", adults := [{ wages := 60000 }] }).incomeTax = 0

end VaTax
