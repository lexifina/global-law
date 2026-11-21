import ESTax.Work

/-!
# One declaración (individual or conjunta): from rentas to cuota diferencial (LIRPF Títulos II-VII)

A `Member` is one person's income in cents. A `Ret` is one declaración: one member (tributación individual) or the
members of a unidad familiar (art. 82, tributación conjunta), with the mínimos and the household-level deductions
already worked out by `Household.lean`.
-/

namespace ESTax
open TaxKernel

structure Member where
  age : Nat := 40
  /-- rendimientos íntegros del trabajo from employment (art. 17.1), cents -/
  wages : Int := 0
  /-- pensions (art. 17.2 a) 1.º): rendimientos del trabajo, no contributions -/
  pension : Int := 0
  /-- rendimiento neto de actividades económicas (taken as net, after own RETA cuotas) -/
  selfEmp : Int := 0
  /-- rendimiento neto del capital inmobiliario, after any art. 23.2 reducción -/
  rental : Int := 0
  /-- renta del ahorro (art. 46): interest, dividends, gains on listed shares -/
  savings : Int := 0
  /-- aportaciones a planes de pensiones (art. 51.1) -/
  pensionContrib : Int := 0
  /-- donativos (Ley 49/2002 art. 17) -/
  charitable : Int := 0
  /-- ejercicio (round 5): selects the `YP` record -/
  year : Nat := 2025
  deriving Repr, Inhabited

def Member.yp (m : Member) : YP := ypFor m.year
def Member.ss (m : Member) : Int := ssEmployeeY m.yp m.wages
def Member.rit (m : Member) : Int := m.wages + m.pension
/-- Rendimiento neto for art. 20 (after art. 19.2 a)-e); here only a), the contributions). -/
def Member.rnt20 (m : Member) : Int := m.rit - m.ss
def Member.otros (m : Member) : Int := otrosGastosApplied m.rit m.ss
/-- Rendimiento neto del trabajo before the art. 20 reducción (art. 19.1). -/
def Member.rntPre (m : Member) : Int := m.rit - m.ss - m.otros
/-- Rentas distintas de las del trabajo (art. 20, DA 61.ª), net. -/
def Member.otras (m : Member) : Int := m.selfEmp + m.rental + m.savings
/-- Base imponible (general + ahorro) of the member alone, with the art. 20 reducción of a lone return
(used for the Madrid income limits, which are per contribuyente). -/
def Member.biAlone (m : Member) : Int :=
  m.rntPre - min (red20Y m.yp m.rnt20 m.otras) (pos m.rntPre) + m.selfEmp + m.rental + pos m.savings

structure Ret where
  members : List Member
  /-- art. 84.2 3.º / 4.º reducción (0 for an individual return) -/
  redJoint : Int := 0
  /-- mínimo personal y familiar, state and Madrid (arts. 56-61; Madrid arts. 2-2 quater) -/
  minEst : Int
  minMad : Int
  /-- Madrid art. 4 deducción por nacimiento (already within its art. 18.1 limits) -/
  madNac : Int := 0
  /-- Madrid art. 14 applies (two or more descendants, family bases ≤ 24.744 €) -/
  madFam2 : Bool := false
  /-- refundable: art. 81 maternidad + art. 81 bis, for this return -/
  maternidad : Int := 0
  famNum : Int := 0
  /-- ejercicio (round 5) -/
  year : Nat := 2025
  deriving Repr, Inhabited

structure Liq where
  big : Int        -- base imponible general (after the joint reducción)
  bia : Int        -- base imponible del ahorro (after the joint reducción's remainder)
  red20 : Int
  redPP : Int      -- art. 51 reducción
  blg : Int
  bla : Int
  cie : Int        -- cuota íntegra estatal (general + ahorro)
  cia : Int        -- cuota íntegra autonómica
  donEst : Int
  donAut : Int
  madNac : Int
  madFam2 : Int
  cle : Int        -- cuota líquida estatal (art. 67)
  cla : Int        -- cuota líquida autonómica (art. 77)
  smi : Int        -- DA 61.ª deduction applied
  maternidad : Int
  famNum : Int
  /-- incomeTax (state) and localIncomeTax (Madrid), after all deductions; refundables on the state line -/
  stateTax : Int
  madridTax : Int
  deriving Repr, Inhabited

/-- Ley 49/2002 art. 19.1 on a base already limited by LIRPF art. 69.1. -/
def donativosDed (base : Int) : Int :=
  bpOf donR1 (min base donTramo) + bpOf donR2 (pos (base - donTramo))

def liquidate (r : Ret) : Liq :=
  let yp := ypFor r.year
  let ms := r.members
  -- Trabajo (arts. 17-20). The art. 20 reducción is one amount per declaración, on the sum of the members'
  -- rendimientos (art. 84.2: "Los importes y límites cuantitativos ... se aplicarán en idéntica cuantía").
  let rnt20 := sumL (ms.map Member.rnt20)
  let otras := sumL (ms.map Member.otras)
  let rntPre := sumL (ms.map Member.rntPre)
  let red := min (red20Y yp rnt20 otras) (pos rntPre)
  -- Bases imponibles (arts. 45-49).
  let big0 := rntPre - red + sumL (ms.map (·.selfEmp)) + sumL (ms.map (·.rental))
  let bia0 := pos (sumL (ms.map (·.savings)))
  -- art. 84.2 3.º/4.º: "se aplicará, en primer lugar, a la base imponible general sin que pueda resultar negativa ...
  -- El remanente, si lo hubiera, minorará la base imponible del ahorro".
  let rg := min r.redJoint (pos big0)
  let big := big0 - rg
  let bia := pos (bia0 - (r.redJoint - rg))
  -- art. 51-52 (per partícipe, art. 84.2 1.º); art. 50.1: base liquidable general not negative.
  let ppLim := ms.map fun m => min (pos m.pensionContrib) (min ppLimite (bpOf ppLimitePct (pos (m.rntPre + m.selfEmp))))
  let redPP := min (sumL ppLim) (pos big)
  let blg := pos (big - redPP)
  let bla := bia
  -- art. 56.2: the mínimo fills the general base first, the rest goes to the ahorro base.
  let mgE := min r.minEst blg
  let maE := min (pos (r.minEst - blg)) bla
  let mgM := min r.minMad blg
  let maM := min (pos (r.minMad - blg)) bla
  let cie := cuotaMinusMin escalaEstatal blg mgE + cuotaMinusMin yp.escalaAhorro bla maE
  let cia := cuotaMinusMin yp.escalaMadrid blg mgM + cuotaMinusMin yp.escalaAhorro bla maM
  -- donativos: art. 69.1 limit 10 % of base liquidable, 50 % on each cuota (arts. 67.1 b), 77.1 a)).
  let donBase := min (sumL (ms.map fun m => pos m.charitable)) (bpOf 1000 (blg + bla))
  let don := donativosDed donBase
  let donE := don / 2
  let donA := don - donE
  let cle := pos (cie - donE)
  -- Madrid deductions on the cuota íntegra autonómica (art. 77.1 b)); art. 14 last.
  let nac := min r.madNac (pos (cia - donA))
  let base14 := pos (cia - donA - nac)
  let f2 := if r.madFam2 then bpOf madFam2Pct base14 else 0
  let cla := pos (cia - donA - nac - f2)
  -- DA 61.ª: limited to the share of (cuota íntegra estatal + autonómica) of the net work income in the bases;
  -- subtracted from the cuota líquida total (after art. 80).
  let wages := sumL (ms.map (·.wages))
  let otrasSmi := otras + sumL (ms.map (·.pension))
  let smi0 := smiAmountY yp wages otrasSmi
  let workNet := pos (rntPre - red)
  let bases := pos big0 + bia0
  let smiCap := if bases ≤ 0 then 0 else mulDiv (cie + cia) (min workNet bases) bases
  let smi := min (min smi0 smiCap) (cle + cla)
  let smiE := min smi cle
  let smiA := smi - smiE
  { big, bia, red20 := red, redPP, blg, bla, cie, cia, donEst := donE, donAut := donA, madNac := nac,
    madFam2 := f2, cle, cla, smi, maternidad := r.maternidad, famNum := r.famNum,
    stateTax := cle - smiE - r.maternidad - r.famNum, madridTax := cla - smiA }

def Liq.total (l : Liq) : Int := l.stateTax + l.madridTax

end ESTax
