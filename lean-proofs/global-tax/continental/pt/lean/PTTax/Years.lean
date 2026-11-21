import PTTax.Minimo

/-!
# Tax years 2022-2025 (round 2, improve-continental)

Each year's parameters with the dated text they come from. Earlier wordings of the CIRS are the Autoridade
Tributária's "Redações anteriores" pages (info.portaldasfinancas.gov.pt/.../cirs_rep/ra/Pages/<art>ra_<YYYYMM>.aspx,
"em vigor até" YYYY-MM), saved in `../law/hist/` (fetched 2026-11-19):
* art. 68: `irs68ra_202212` (Lei n.º 12/2022, de 27 de junho: income 2022), `irs68ra_202312` (Lei n.º 24-D/2022,
  de 30 de dezembro: income 2023), `irs68ra_202412` + `CIRS_68_Lei332024.png` (Lei n.º 33/2024, de 7 de agosto:
  income 2024; it replaced the Lei 82/2023 table of `irs68ra_202408` for the whole of 2024);
* art. 70: `irs70ra_202212` (Lei n.º 114/2017 wording: n.º 1 "rendimento líquido de imposto inferior a 1,5 x 14 x
  (valor do IAS)", n.º 2 the family exemptions, n.º 4 "não pode, por titular, ser inferior ao valor anual da
  retribuição mínima mensal"); `irs70ra_202312`: the Lei 24-D/2022 abatimento model, marked by the AT "produz efeitos
  a partir de 1 de janeiro de 2024", so income 2023 is still under the Lei 114/2017 wording (reading stated in
  IMPROVE.md); `irs70ra_202412`: income 2024, VR "maior valor entre 11 480 e 1,5 x 14 x IAS" (Lei 82/2023),
  b) factor 2,60 and L with 3,60 (Lei 82/2023), c) factor 1,35 (Lei 34/2024);
* art. 25: `irs25ra_202312` (income 2022 and 2023: n.º 1 a) "(euro) 4 104"), `irs25ra_202412` (income 2024:
  4 104 and n.º 7 "O valor referido na alínea a) do n.º 1 é atualizado anualmente à taxa de atualização do IAS"
  (Lei n.º 32/2024, de 7 de agosto); the IAS rose 6 % for 2024: 4 104 x 1,06 = 4 350,24);
* art. 78-A: `irs78ara_202212` (income 2022, Lei 12/2022: n.º 3 a) + 300 for the second and later dependents up to
  three years, b) + 150 for those over three and up to six; n.º 4 not cumulative with n.º 2), current wording (Lei
  24-D/2022, from 2023: + 300 for the second and later dependents up to six years).
* IAS: 443,20 € (2022, Portaria n.º 294/2021, de 13 de dezembro), 480,43 € (2023, Portaria n.º 298/2022, de 16 de
  dezembro), 509,26 € (2024, Portaria n.º 421/2023, de 11 de dezembro).
* Retribuição mínima mensal garantida: 705 € (2022, Decreto-Lei n.º 109-A/2021, de 7 de dezembro), 760 € (2023,
  Decreto-Lei n.º 85-A/2022, de 22 de dezembro).
* Unchanged 2022-2025: art. 68-A (2,5 % / 5 %), art. 69, art. 78-B n.º 1 (250 € per taxpayer), the 11 % employee
  contribution (Código Contributivo art. 53).
* Abono de família 2024: Portaria n.º 422/2023 (below). Not modelled for 2022-2023: the abono amounts (Portaria
  n.º 34/2023 and the 2022 Portarias, with the 2022-2023 garantia para a infância complements), IRS Jovem (art. 12-B had other percentages and caps before Lei 45-A/2024).
-/

namespace PTTax
open TaxKernel

/-- One tax year's parameters (money in cents, rates as in `Params`). -/
structure YP where
  year : Nat
  rows : List (Int × Int × Int)
  firstRate : Int          -- column A of the 1st escalão, pcm
  lim1 : Int               -- limit of the 1st escalão, cents
  bands : Schedule
  ias : Int
  dedEsp : Int
  meNew : Bool             -- the abatimento model of art. 70 (from income 2024) or the Lei 114/2017 floor
  meRef : Int              -- VR (new) / the floor of n.º 1 and n.º 4 (old), cents
  meBnum : Int             -- b) factor x 100
  meLdiv : Int             -- the divisor of L x 100
  meCnum : Int             -- c) factor x 100
  famEx34 : Int            -- old n.º 2 a): coletável up to which 3-4 dependents pay no art. 68 tax (0 = none)
  famEx5 : Int             -- old n.º 2 b): 5 or more dependents
  depSecUnder3 : Int       -- art. 78-A n.º 3: second and later dependents up to three years
  depSec4to6 : Int         -- art. 78-A n.º 3: second and later dependents over three, up to six
  abono : Bool             -- abono amounts modelled for this year
  jovem : Bool             -- IRS Jovem (Lei 45-A/2024 wording) applies
  abonoM : List (Int × Int × Int) := abonoMonthly   -- monthly amounts by escalão (≤ 36, 36-72, > 72 months)
  abonoMaj2 : List Int := abonoMajTwo
  abonoMajN : List Int := abonoMajMore

def y2025 : YP :=
  { year := 2025, rows := art68Rows, firstRate := art68FirstRate, lim1 := lim1, bands := art68Bands, ias := ias,
    dedEsp := dedEspecifica, meNew := true, meRef := meRef, meBnum := 260, meLdiv := 360, meCnum := 135,
    famEx34 := 0, famEx5 := 0, depSecUnder3 := dedSecondUnder6, depSec4to6 := dedSecondUnder6, abono := true,
    jovem := true }

def y2024 : YP :=
  { year := 2024,
    rows := [(7703, 16500, 13000), (11623, 22000, 14180), (16472, 25000, 16482), (21321, 32000, 18419),
             (27146, 35500, 21334), (39791, 43500, 25835), (43000, 45000, 27154), (80000, 48000, 35408)],
    firstRate := 13000, lim1 := eur 7703,
    bands := Schedule.ofList [(0, 1300), (770300, 1650), (1162300, 2200), (1647200, 2500), (2132100, 3200),
      (2714600, 3550), (3979100, 4350), (4300000, 4500), (8000000, 4800)],
    ias := 50926, dedEsp := 435024,
    meNew := true, meRef := max (eur 11480) (15 * 14 * 50926 / 10), meBnum := 260, meLdiv := 360, meCnum := 135,
    famEx34 := 0, famEx5 := 0, depSecUnder3 := eur 300, depSec4to6 := eur 300, abono := true, jovem := false,
    -- Portaria n.º 422/2023, de 11 de dezembro (effects from 1 January 2024), art. 2 n.º 1: 1.º escalão € 183,03 /
    -- € 72,00; 2.º € 154,92 / € 72,00; 3.º € 126,57 / € 56,86 / € 52,09; 4.º € 84,75 / € 42,91; art. 3 a)
    -- € 62,25 / 55,24 / 52,09 / 37,64, b) € 102,51 / 88,47 / 82,18 / 53,38; art. 4 n.º 1 monoparental + 50 %
    -- (law/hist/Portaria_422_2023.pdf). Escalão limits: DL 176/2003 art. 14 (x 14 x IAS 2024).
    abonoM := [(18303, 7200, 7200), (15492, 7200, 7200), (12657, 5686, 5209), (8475, 4291, 0)],
    abonoMaj2 := [6225, 5524, 5209, 3764], abonoMajN := [10251, 8847, 8218, 5338] }

def y2023 : YP :=
  { year := 2023,
    rows := [(7479, 21000, 14500), (11284, 26500, 16692), (15992, 28500, 19579), (20700, 35000, 21608),
             (26355, 37000, 24482), (38632, 43500, 28460), (50483, 45000, 31991), (78834, 48000, 36669)],
    firstRate := 14500, lim1 := eur 7479,
    bands := Schedule.ofList [(0, 1450), (747900, 2100), (1128400, 2650), (1599200, 2850), (2070000, 3500),
      (2635500, 3700), (3863200, 4350), (5048300, 4500), (7883400, 4800)],
    ias := 48043, dedEsp := eur 4104,
    meNew := false, meRef := max (15 * 14 * 48043 / 10) (14 * eur 760), meBnum := 0, meLdiv := 100, meCnum := 0,
    famEx34 := eur 11320, famEx5 := eur 15560, depSecUnder3 := eur 300, depSec4to6 := eur 300, abono := false,
    jovem := false }

def y2022 : YP :=
  { year := 2022,
    rows := [(7116, 23000, 14500), (10736, 26500, 17366), (15216, 28500, 20055), (19696, 35000, 21976),
             (25076, 37000, 24770), (36757, 43500, 28657), (48033, 45000, 32141), (75009, 48000, 36766)],
    firstRate := 14500, lim1 := eur 7116,
    bands := Schedule.ofList [(0, 1450), (711600, 2300), (1073600, 2650), (1521600, 2850), (1969600, 3500),
      (2507600, 3700), (3675700, 4350), (4803300, 4500), (7500900, 4800)],
    ias := 44320, dedEsp := eur 4104,
    meNew := false, meRef := max (15 * 14 * 44320 / 10) (14 * eur 705), meBnum := 0, meLdiv := 100, meCnum := 0,
    famEx34 := eur 11320, famEx5 := eur 15560, depSecUnder3 := eur 300, depSec4to6 := eur 150, abono := false,
    jovem := false }

/-- Round 10: the art. 68 table **in force at the start of 2025** (AT "Redações anteriores", wording in force until July
2025, `../law/hist/irs68_ra202507.html`): limits "(Redação da Lei n.º 45-A/2024, de 31 de dezembro)" 8 059 ... 83 696 and
rates A and B "(Redação da Lei n.º 33/2024, de 7 de agosto)": 13,00 / 13,000; 16,50 / 14,180; 22,00 / 16,482;
25,00 / 18,419; 32,00 / 21,334; 35,50 / 25,835; 43,50 / 27,154; 45,00 / 35,408; 48,00. Lei n.º 55-A/2025 replaced it in
July 2025 for the whole year (the statute-mode table). Used only under `--start-of-year`, the convention of Eurostat's
earn_net ESMS section 3.4: "Income tax and social security contributions parameters refer to the beginning of the
fiscal year, i.e. changes occurring later during the year are ignored." -/
def y2025start : YP :=
  { y2025 with
    rows := [(8059, 16500, 13000), (12160, 22000, 14180), (17233, 25000, 16482), (22306, 32000, 18419),
             (28400, 35500, 21334), (41629, 43500, 25835), (44987, 45000, 27154), (83696, 48000, 35408)]
    firstRate := 13000
    bands := art68BandsOE2025 }

/-- The parameters of tax year `y` (2022-2025); other years fall back to 2025 (flagged in `unsupported`). -/
def ypFor : Nat → YP
  | 2022 => y2022 | 2023 => y2023 | 2024 => y2024 | _ => y2025

def yearSupported (y : Nat) : Bool := 2022 ≤ y && y ≤ 2025

/-! ## Art. 68 / 69 for a year -/

def art68ScaledY (p : YP) (n x : Int) : Int :=
  p.rows.foldl
    (fun acc (r : Int × Int × Int) =>
      let lim := n * eur r.1
      if lim ≤ x then lim * r.2.2 + (x - lim) * r.2.1 else acc)
    (x * p.firstRate)

def art68ScaledByY (p : YP) (bands : Bool) (n x : Int) : Int :=
  if bands then 10 * (p.bands.mapLo (n * ·)).ticks (pos x) else art68ScaledY p n (pos x)

/-! ## Art. 70 abatimento (the model in force from income 2024) for a year -/

/-- Limite despesas gerais / Taxa 1.º escalão, in cents, rounded half up to the cent (the statute names no
rounding; 2025: exactly 2 000 €; 2024: 250 / 13 % = 1 923,08 €). -/
def meGY (p : YP) : Int := divR .halfUp (limDespesasGerais * 100000) p.firstRate

/-- S x L in cents, S = the divisor x 100: S·VR + 100·(Lim1 − G). -/
def meLS (p : YP) : Int := p.meLdiv * p.meRef + 100 * (p.lim1 - meGY p)

def meRawY (p : YP) (rb de : Int) : Int :=
  let g := meGY p
  if rb ≤ p.meRef then pos (p.meRef - de - g)
  else if p.meLdiv * rb ≤ meLS p then
    divR .halfUp (pos (100 * p.meRef - p.meBnum * (rb - p.meRef) - 100 * de - 100 * g)) 100
  else divR .halfUp (pos ((100 + p.meCnum) * meLS p - 100 * p.meLdiv * p.lim1 - p.meCnum * p.meLdiv * rb
      - 100 * p.meLdiv * de)) (100 * p.meLdiv)

def meAbateY (p : YP) (rb de : Int) : Int := if p.meNew then min (meRawY p rb de) (pos (rb - de)) else 0

/-! ## Checks: the year functions reproduce the 2025 ones, and the earlier years' tables -/

#guard [0, 500000, 805900, 1216000, 1500000, 2840000, 4498700, 9000000].all fun x =>
  art68ScaledY y2025 1 x == art68Scaled 1 x && art68ScaledY y2025 2 x == art68Scaled 2 x
#guard [0, 1000000, 1218000, 1300000, 1386305, 1400000, 1600000, 2000000].all fun rb =>
  meAbateY y2025 rb 446215 == meAbate rb 446215
-- OECD 2022 S67: rendimento coletável 9 120,84 € -> 1 492,93 € (art. 68 n.º 2: 7 116 x 14,5 % + excess x 23 %)
#guard divR .halfUp (art68ScaledY y2022 1 912084) 100000 = 149293
-- 2023: 10 301,74 € -> 7 479 x 14,5 % + 2 822,74 x 21 % = 1 677,23 €
#guard divR .halfUp (art68ScaledY y2023 1 1030174) 100000 = 167723

end PTTax
