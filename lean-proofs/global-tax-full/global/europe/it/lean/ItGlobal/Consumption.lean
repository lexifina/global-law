import ItGlobal.Pit
import TaxKernel.Global2

/-!
# IT 2025: Imposta sul valore aggiunto (5111); excises not modelled in this pass

Source: DPR 26 ottobre 1972 n. 633, Normattiva (official) multivigente text "!vig=2025-07-01" (`it/law/dpr633_art16.html`); sha256 in `law/SHA256SUMS`.
* art. 16: "L'aliquota dell'imposta è stabilita nella misura del ventidue per cento"
* "L'aliquota è ridotta al quattro, al cinque e al dieci per cento per le operazioni che hanno per oggetto i beni e i servizi elencati, rispettivamente, nella parte II, nella parte II-bis e nella parte III dell'allegata tabella A"

## Accise (5121), pass 2
Sources: D.Lgs. 26 ottobre 1995 n. 504 (TUA), normattiva Akoma Ntoso export `vigente al 2025-07-01`
(`it/law/tua504_akn20250701.xml`), and the Decreto MEF 14 maggio 2025 (G.U. 14/5/2025 n. 110, 25A02968,
`it/law/dm20250514_accise.html`); sha256 in `law/SHA256SUMS`.
* **DM 14 maggio 2025**, premise: "l'aliquota di accisa sulla benzina e' pari a euro 728,40 per mille litri e quella
  dell'aliquota di accisa sul gasolio impiegato come carburante e' pari a euro 617,40"; art. 1: from the day after
  publication (15.5.2025) petrol "ridotta di 1,50 centesimi di euro per litro", diesel "aumentata di 1,50 centesimi";
  art. 2 c. 1 (TUA All. I, AGGIORNAMENTO (130)): "a) benzina: euro 713,40 per mille litri; b) gasolio usato come
  carburante: euro 632,40 per mille litri".
* **TUA art. 39-octies c. 3**: cigarettes "a) un importo specifico fisso ... a decorrere dall'anno 2025, in 29,50 euro
  per 1.000 sigarette; b) ... l'aliquota di base, di cui alla voce "Tabacchi lavorati", lettera c), dell'allegato I, al
  prezzo di vendita al pubblico"; All. I "c) sigarette 49,50 per cento"; **c. 10** "non puo' essere inferiore a euro
  90 per mille sigarette".
* **Birra**: L. 30 dicembre 2021 n. 234 art. 1 c. 986 (as amended by D.L. 198/2022), All. I AGGIORNAMENTO (114):
  "a decorrere dal 1° gennaio 2024, in euro 2,99 per ettolitro e per grado-Plato". **Vino**: All. I "Vino: lire zero".
* Not modelled: alcole etilico. All. I prints 765,44 EUR per hl anidro; D.L. 104/2013 art. 25 c. 3 b) set 1019,21
  from 2015; the rate actually applied since 2015 comes from an ADM determinazione that is not in normattiva (not read).

## FT review (2026-11-21, third pass): heating oil
Same normattiva AKN text (vigente 2025-07-01). All. I prints "Oli da gas o gasolio: ... usato come combustibile per
riscaldamento: lire 747.470 per mille litri" with no update note; the D.L. 201/2011 art. 15 c. 1 (normattiva, read)
re-sets only benzina, gasolio carburante, GPL and metano carburante. The euro rate applied in 2025 comes from acts not
in the consolidated Allegato (as for alcole etilico above): not read. Heating oil is listed as grade C, not booked at 0.


## 5121 Accisa sull'alcole etilico (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), IT excise records for the situation on 1 July 2025 (alcohol 4095; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `it/law/tedb_*.json`).
* TEDB IT ethyl alcohol (1.7.2025): 1035.52 EUR per hl of pure alcohol
-/

namespace ItGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Imposta sul valore aggiunto", standard := 2200, reduced := 1000, reduced2 := 500, superReduced := 400, threshold := 0,
    classOf := fun gd => match gd with
      | .food | .water | .medicines | .hotels | .restaurants | .transport | .electricity => .reduced
      | .books | .newspapers => .superReduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "DPR 633/1972 art. 16 (22 %; 4, 5, 10 % per tabella A parti II, II-bis, III); art. 10 (esenzioni)"

def excise : Excise :=
  { rates := [
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 6472, perUnitDen := 625, onPureAlcohol := true, statute := "TEDB IT ethyl alcohol (1.7.2025): 1035.52 EUR per hl of pure alcohol" }] }

/-- TUA All. I, benzina, before the DM 14 maggio 2025 (its premise: 728,40 EUR per 1 000 l). -/
def petrolTo : ExciseRule := { good := .petrol, name := "Accisa sulla benzina", perUnitNum := 72840, perUnitDen := 100000, validTo := "2025-05-15", statute := "D.Lgs. 504/1995 All. I (benzina 728,40 EUR / 1 000 l, DM 14.5.2025 premessa), to 14.5.2025" }
def petrolFrom : ExciseRule := { good := .petrol, name := "Accisa sulla benzina", perUnitNum := 71340, perUnitDen := 100000, validFrom := "2025-05-15", statute := "D.Lgs. 504/1995 All. I; DM 14.5.2025 art. 2 c. 1 a) (713,40 EUR / 1 000 l from 15.5.2025)" }
def dieselTo : ExciseRule := { good := .diesel, name := "Accisa sul gasolio usato come carburante", perUnitNum := 61740, perUnitDen := 100000, validTo := "2025-05-15", statute := "D.Lgs. 504/1995 All. I (gasolio 617,40 EUR / 1 000 l, DM 14.5.2025 premessa), to 14.5.2025" }
def dieselFrom : ExciseRule := { good := .diesel, name := "Accisa sul gasolio usato come carburante", perUnitNum := 63240, perUnitDen := 100000, validFrom := "2025-05-15", statute := "D.Lgs. 504/1995 All. I; DM 14.5.2025 art. 2 c. 1 b) (632,40 EUR / 1 000 l from 15.5.2025)" }
def cigarettes : ExciseRule := { good := .cigarettes, name := "Accisa sui tabacchi lavorati (sigarette)", perUnitNum := 2950, perUnitDen := 100000, adValoremBp := 4950, minNum := 90, minDen := 1000, statute := "D.Lgs. 504/1995 art. 39-octies c. 3 (29,50 EUR / 1 000 + 49,50 % of the retail price, All. I c)), c. 10 (at least 90 EUR / 1 000)" }
def beer : ExciseRule := { good := .beer, name := "Accisa sulla birra", perPlatoNum := 299, perPlatoDen := 10000, statute := "D.Lgs. 504/1995 All. I; L. 234/2021 art. 1 c. 986 (2,99 EUR per hl and degree Plato from 2024)" }
def rules : List ExciseRule := [petrolTo, petrolFrom, dieselTo, dieselFrom, cigarettes, beer]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 IVA, 5121 accise", covers := [.vat, .excise, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges rules g }]

def absent : List Absent :=
  []

def notes : List String := ["IT 5111: Normattiva vigente al 2025-07-01", "IT 5121: TUA vigente 2025-07-01 (normattiva AKN), DM 14.5.2025; vino lire zero (All. I)", "IT 5121 gap pass: Accisa sull'alcole etilico (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["food at 10 % (tabella A parte III); bread, milk, fresh produce and other parte II items are 4 %: tabella A not read item by item"] else [])
  ++ (if g.entity == .company then ["no VAT registration threshold (the regime forfettario is an income-tax regime, not modelled)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits) then ["accisa sull'alcole etilico not modelled: the rate applied in 2025 is set by an ADM determinazione not in normattiva (All. I prints 765,44; D.L. 104/2013 art. 25 c. 3 b) 1019,21 from 2015)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["accisa sulla birra by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears none"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes) then ["cigarettes: onere fiscale minimo (art. 39-octies c. 6-8, 98,80 % of excise + VAT at the PMP-sigarette) not applied; the retail price is the line's amount"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then ["fuel: undated lines are split 134/365 at the rate before and 231/365 after 15.5.2025; regional surcharges and the 2026 riallineamento (D.Lgs. 43/2025) not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .heatingOil) then ["5121 heating oil (gasolio per riscaldamento): not modelled (grade C: All. I prints lire 747.470 / 1 000 l; the 2025 euro rate is set outside the consolidated Allegato, not read)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 IT: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12200 } == 2200
#guard vat.embedded { good := .food, amount := 11000 } == 1000
#guard vat.embedded { good := .books, amount := 10400 } == 400
#guard petrolTo.dutyOn { good := .petrol, amount := 1800, quantity := 1000000 } {} == 728
#guard petrolFrom.dutyOn { good := .petrol, amount := 1800, quantity := 1000000 } {} == 713
#guard dieselTo.dutyOn { good := .diesel, amount := 1700, quantity := 1000000 } {} == 617
#guard dieselFrom.dutyOn { good := .diesel, amount := 1700, quantity := 1000000 } {} == 632
-- 1 000 cigarettes at 400 EUR: 29,50 + 198,00 (rounded down); at 100 EUR: 29,50 + 49,50 = 79 < 90 (c. 10 binds)
#guard cigarettes.dutyOn { good := .cigarettes, amount := 400, quantity := 1000000 } {} == 227
#guard cigarettes.dutyOn { good := .cigarettes, amount := 100, quantity := 1000000 } {} == 90
#guard beer.dutyOn { good := .beer, amount := 300, quantity := 100000 } { platoBp := 1200 } == 35
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 414

end ItGlobal.Consumption
