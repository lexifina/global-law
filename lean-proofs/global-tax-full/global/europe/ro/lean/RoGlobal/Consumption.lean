import RoGlobal.Pit
import TaxKernel.Global2

/-!
# Romania 2025: taxa pe valoarea adăugată (5111) in two rate periods; excises not reached (5121)

Sources: Codul fiscal (Legea nr. 227/2015), legislatie.just.ro `Public/DetaliiDocument/171282`, the consolidated
text as captured by the Internet Archive on 2025-05-02 (`ro/law/cf_wb20250502.html`, in force before 1 August 2025)
and on 2025-11-25 (`ro/law/cf_wb20251125.html`, art. 291 marked "(la 01-08-2025" as amended by Legea nr. 141 din
25 iulie 2025, art. II pct. 42, MO nr. 699 din 25 iulie 2025); sha256 in `law/SHA256SUMS`.
* **Art. 291 (1)** to 31 July 2025: "b) 19% începând cu data de 1 ianuarie 2017"; **(2)** "Cota redusă de 9%":
  c) "livrarea de medicamente de uz uman și veterinar"; e) "alimente, inclusiv băuturi, destinate consumului uman ...
  cu excepția: 1. băuturilor alcoolice; 2. băuturilor nealcoolice care se încadrează la codul NC 2202; 3. alimentelor
  cu zahăr adăugat ..." (wording of Legea 254/2024 from 1.1.2025); i) "serviciile de alimentare cu apă și de
  canalizare"; j) "cazarea în cadrul sectorului hotelier"; k) "serviciile de restaurant și de catering, cu excepția
  băuturilor alcoolice ..."; **(3)** "Cota redusă de 5%": a) "livrarea de manuale școlare, cărți, ziare și reviste".
* **Art. 291 (1)** from 1 August 2025 (Legea 141/2025): "nivelul acesteia este 21%"; **(2)** "Cota redusă de 11%":
  a) medicines for human use, b) food (same exceptions, plus food supplements), c) water and sewerage, g) "manuale
  școlare, cărți, ziare și reviste", h) access to museums and monuments, m) hotel accommodation, n) restaurant and
  catering services; the 5 % rate of (3) is repealed (Legea 141/2025 art. II pct. 43).
* Kernel 2.1 `DatedVat`: a dated line goes to its period; an undated basket is split 212/365 (19 %) and 153/365 (21 %).
-/

namespace RoGlobal.Consumption
open TaxKernel TaxKernel.Global

/-- Codul fiscal art. 291 to 31 July 2025: 19 %, 9 % (2), 5 % (3). -/
def vat1 : Vat :=
  { name := "Taxa pe valoarea adăugată", standard := 1900, reduced := 900, reduced2 := 500,
    classOf := fun gd => match gd with
      | .food | .water | .medicines | .hotels | .restaurants => .reduced
      | .books | .newspapers => .reduced2
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

/-- Codul fiscal art. 291 from 1 August 2025 (Legea 141/2025 art. II pct. 42): 21 %, 11 %. -/
def vat2 : Vat :=
  { name := "Taxa pe valoarea adăugată", standard := 2100, reduced := 1100,
    classOf := fun gd => match gd with
      | .food | .water | .medicines | .hotels | .restaurants | .books | .newspapers => .reduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def roVat : DatedVat :=
  { periods := [{ vat := vat1, statute := "Codul fiscal art. 291 (1) b) 19 %, (2) 9 %, (3) 5 % (to 31.7.2025)" },
                { start := "2025-08-01", vat := vat2, statute := "Codul fiscal art. 291 (1) 21 %, (2) 11 % (Legea 141/2025, from 1.8.2025)" }],
    undatedSupplies := .split }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 TVA (two rate periods)", covers := [.vat],
     run := fun args g prev =>
       roVat.charges g }]

def absent : List Absent :=
  []

def notes : List String := ["RO 5111: art. 291 19/9/5 % to 31 July 2025, 21/11 % from 1 August 2025 (kernel 2.1 DatedVat)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["small-business exemption (art. 310: 88 500 euro equivalent, 395 000 lei from 1.9.2025) not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .nonAlcoholic) then ["non-alcoholic drinks taken at the standard rate (NC 2202 drinks are excluded from the reduced rate; other drinks are 9 % / 11 %)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["food with added sugar of at least 10 g/100 g is excluded from the reduced rate: food taken wholly at 9 % / 11 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .recreation) then ["access to museums and monuments (9 % / 5 % / 11 %) not separated from recreation (standard)"] else [])
  ++ (if !g.consumption.isEmpty then ["undated basket lines split by days between the 19 % and 21 % periods"] else [])
  ++ (if !g.consumption.isEmpty || g.entity == .company then ["5121 Excise duties: not modelled (grade C: not reached in the P1 pass)"] else [])

#guard vat1.embedded { good := .clothing, amount := 119 } == 19
#guard vat1.embedded { good := .food, amount := 109 } == 9
#guard vat1.embedded { good := .books, amount := 105 } == 5
#guard vat2.embedded { good := .clothing, amount := 121 } == 21
#guard vat2.embedded { good := .restaurants, amount := 111 } == 11
#guard vat2.embedded { good := .books, amount := 111 } == 11
#guard vat2.embedded { good := .health, amount := 100 } == 0

end RoGlobal.Consumption
