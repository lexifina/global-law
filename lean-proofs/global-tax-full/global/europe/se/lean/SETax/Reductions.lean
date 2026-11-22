import SETax.Grundavdrag

/-!
# Skattereduktioner: IL 67 kap. (inkomstår 2025)

* 1 § (Lag 2022:445): "Skattereduktion ska anges i hela krontal så att öretal faller bort."
* 2 § (Lag 2022:445, the 2025 wording): "Skattereduktion ska göras för sjöinkomst, allmän pensionsavgift,
  arbetsinkomst (jobbskatteavdrag), sjukersättning och aktivitetsersättning, förvärvsinkomst, boende i vissa
  områden (regional skattereduktion), underskott av kapital, hushållsarbete, installation av grön teknik, gåva,
  mikroproduktion av förnybar el och avgift till arbetslöshetskassa i nu nämnd ordning." ... "Skattereduktion
  enligt 5-9 d, 34, 35 och 46-48 §§ ska dock räknas av endast mot kommunal inkomstskatt."
* 4 §: pensionsavgift credit "för allmän pensionsavgift ... som avser beskattningsåret" (100 % of the fee).
* 6 §: arbetsinkomster "avrundas nedåt till helt hundratal kronor".
* 7 § (SFS 2024:1131, 2025 wording), under 66 at 1 January:
  > överstiger inte 0,91 prisbasbelopp: skillnaden mellan arbetsinkomsterna och grundavdraget, multiplicerad med
  > skattesatsen för kommunal inkomstskatt
  > överstiger 0,91 men inte 3,24: skillnaden mellan å ena sidan summan av 0,91 prisbasbelopp och 38,74 procent av
  > arbetsinkomsterna mellan 0,91 och 3,24 prisbasbelopp och å andra sidan grundavdraget, multiplicerad med ...
  > överstiger 3,24 men inte 8,08: ... summan av 1,813 prisbasbelopp och 19,9 procent av arbetsinkomsterna mellan
  > 3,24 och 8,08 prisbasbelopp ... och grundavdraget, multiplicerad med ...
  > överstiger 8,08: skillnaden mellan 2,776 prisbasbelopp och grundavdraget, multiplicerad med ...
* 8 § (SFS 2024:1131), 66 or over: "22 procent av arbetsinkomsterna" up to 1,75 pbb; "summan av 0,2635
  prisbasbelopp och 7 procent av arbetsinkomsterna" up to 5,24 pbb; "0,6293 prisbasbelopp" above.
* 10 § (SFS 2024:1131): underskott av kapital, 30 % up to 100 000 kr, 21 % above.
* 26 § (Lag 2021:1160): gåva "25 procent av underlaget ... högst 3 000 kronor"; 22 § underlag below 2 000 kr gives
  nothing; 21 § each gift "minst 200 kronor".
* 46-47 §§ (Lag 2020:1166): förvärvsinkomst, if the beskattningsbar förvärvsinkomst "är högre än 40 000 kronor":
  "1 500 kronor", but between 40 000 and 240 000 kr "0,75 procent av skillnaden mellan den beskattningsbara
  förvärvsinkomsten och 40 000 kronor".
-/

namespace SETax
open TaxKernel

/-- 67 kap. 7 § (2025): the amount before "multiplicerad med skattesatsen", minus nothing yet; 10⁻⁷ kr. `ai` is the
arbetsinkomst rounded down to hundreds (6 §). -/
def jsaBaseN (pbb ai : Int) : Int :=
  let A := 1000 * ai
  if A ≤ 910 * pbb then 10000 * A
  else if A ≤ 3240 * pbb then kN 910 pbb + 3874 * (A - 910 * pbb)
  else if A ≤ 8080 * pbb then kN 1813 pbb + 1990 * (A - 3240 * pbb)
  else kN 2776 pbb

/-- 67 kap. 7 § as worded for 2026 by SFS 2025:1376 (comparison only): 25,1 % and 3,027 pbb. -/
def jsaBaseN2026 (pbb ai : Int) : Int :=
  let A := 1000 * ai
  if A ≤ 3240 * pbb then jsaBaseN pbb ai
  else if A ≤ 8080 * pbb then kN 1813 pbb + 2510 * (A - 3240 * pbb)
  else kN 3027 pbb

/-- 67 kap. 7 § with the year's third and fourth steps (`Params.jsaMidK`, `jsaRate`, `jsaTopK`; 2022-2024). -/
def jsaBaseNY (p : Params) (ai : Int) : Int :=
  let A := 1000 * ai
  if A ≤ 3240 * p.pbb then jsaBaseN p.pbb ai
  else if A ≤ 8080 * p.pbb then kN p.jsaMidK p.pbb + p.jsaRate * (A - 3240 * p.pbb)
  else kN p.jsaTopK p.pbb

/-- Jobbskatteavdrag under 66 (7 §): `(base − GA) × KI`, öretal dropped (1 §), never negative. -/
def jsaUnder66 (p : Params) (ai gaAmt : Int) : Int :=
  pos ((jsaBaseN p.pbb ai - gaAmt * N) * p.kommun / (N * BP))

/-- Jobbskatteavdrag 66 and over (8 §), exact in 10⁻⁷ kr then öretal dropped. -/
def jsa66 (p : Params) (ai : Int) : Int :=
  let A := 1000 * ai
  let n := if A ≤ 1750 * p.pbb then 2200 * A
    else if A ≤ 5240 * p.pbb then kN 2635 p.pbb / 10 + 700 * A
    else kN 6293 p.pbb / 10
  pos (n / N)

/-- Arbetsinkomst (6 §): rounded down to hundreds. -/
def arbetsinkomst (earned : Int) : Int := toMultiple .down 100 (pos earned)

/-- Jobbskatteavdrag (5-8 §§). `old` = turned 66 before the year began. -/
def jsa (p : Params) (old : Bool) (earned gaAmt : Int) : Int :=
  let ai := arbetsinkomst earned
  if ai = 0 then 0 else if old then jsa66 p ai
  else if p.year < 2025 then
    pos ((jsaBaseNY p ai - gaAmt * N) * p.kommun / (N * BP)
      - (if p.jsaPhaseOut then 3 * pos (100 * ai - 1354 * p.pbb) / 10000 else 0))
  else jsaUnder66 p ai gaAmt

/-- Skattereduktion för förvärvsinkomster (46-47 §§), from the beskattningsbar förvärvsinkomst. -/
def fiCredit (b : Int) : Int :=
  if b ≤ 40000 then 0 else if b < 240000 then 75 * (b - 40000) / BP else 1500

/-- Underskott av kapital (10 § första stycket): kernel deficit schedule, öretal dropped. -/
def deficitCredit (p : Params) (deficit : Int) : Int := (dual p).deficit.ticks (pos deficit) / BP

/-- Gåva (21-26 §§): `gifts` = gifts of at least 200 kr each to godkända gåvomottagare. -/
def giftCredit (gifts : Int) : Int := if gifts < 2000 then 0 else min 3000 (25 * gifts / 100)

/-- The three pots credits are set against (67 kap. 2 § andra stycket): municipal income tax, state income tax
(earned and capital, both "statlig inkomstskatt ... enligt 65 kap."). -/
structure Pots where
  municipal : Int
  state : Int
  deriving Repr, Inhabited

/-- Use a credit `v` that may be set against both taxes. 67 kap. 2 § does not say which tax a two-tax credit
consumes first; `stateFirst = false` takes the municipal tax first (Skatteverket's tables, SKV 433 7.5 example 2,
where there is no state tax). Returns (used, pots after). -/
def useBoth (stateFirst : Bool) (v : Int) (t : Pots) : Int × Pots :=
  let u := min (pos v) (pos t.municipal + pos t.state)
  if stateFirst then
    let us := min u (pos t.state)
    (u, { municipal := t.municipal - (u - us), state := t.state - us })
  else
    let um := min u (pos t.municipal)
    (u, { municipal := t.municipal - um, state := t.state - (u - um) })

/-- Use a municipal-only credit (7, 8, 46-47 §§). -/
def useMunicipal (v : Int) (t : Pots) : Int × Pots :=
  let u := min (pos v) (pos t.municipal)
  (u, { t with municipal := t.municipal - u })

/-- Credits in the 67 kap. 2 § order (those the model has): pensionsavgift, jobbskatteavdrag, förvärvsinkomst,
underskott av kapital, gåva. Returns the amounts used and the taxes left. -/
structure CreditsUsed where
  pension : Int
  jobb : Int
  forvarv : Int
  underskott : Int
  gava : Int
  left : Pots
  deriving Repr, Inhabited

/-- Lag (2021:930) om tillfällig skattereduktion för arbetsinkomster (beskattningsåren 2021 och 2022; round 4,
text `refs/raw/sfs-2021-930.txt` from data.riksdagen.se): 3 § arbetsinkomst "överstiger 60 000 kronor och understiger
500 000 kronor"; 4 § "1,25 procent av skillnaden mellan arbetsinkomsten och 60 000 kronor" (60 000-240 000), "2 250
kronor" (240 000-300 000), "2 250 kronor minskat med 1,125 procent av den del av arbetsinkomsten som överstiger
300 000 kronor" (300 000-500 000); 7 § "öretal faller bort"; `ai` = arbetsinkomst as in 67 kap. 6 § (2 §). -/
def tempCredit (y : Nat) (ai : Int) : Int :=
  if y = 2021 ∨ y = 2022 then
    if ai ≤ 60000 ∨ 500000 ≤ ai then 0
    else if ai < 240000 then 125 * (ai - 60000) / 10000
    else if ai ≤ 300000 then 2250
    else pos ((225000000 - 1125 * (ai - 300000)) / 100000)
  else 0

def applyReductions (stateFirst : Bool) (t : Pots) (pension jobb forvarv underskott gava : Int) : CreditsUsed :=
  let (u1, t1) := useBoth stateFirst pension t
  let (u2, t2) := useMunicipal jobb t1
  let (u3, t3) := useMunicipal forvarv t2
  let (u4, t4) := useBoth stateFirst underskott t3
  let (u5, t5) := useBoth stateFirst gava t4
  { pension := u1, jobb := u2, forvarv := u3, underskott := u4, gava := u5, left := t5 }

end SETax
