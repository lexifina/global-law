import AuTax.Basic

/-!
# PAYG withholding: Schedule 1, statement of formulas (Taxation Administration (Withholding Schedules)
Instrument 2024, F2024L00664, made under TAA 1953 Sch 1 s. 15-25; unchanged in F2025L00647 and F2025L01016)

"The formulas comprise linear equations of the form y = ax − b, where: y is the weekly withholding amount
expressed in dollars; x is the number of whole dollars in the weekly earnings plus 99 cents"; "Withholding amounts
... are rounded to the nearest dollar. Values ending in 50 cents are rounded to the next higher dollar. Do this
rounding directly". Coefficients `a`, `b` are held in ten-thousandths (as printed, 4 decimals).
-/

namespace AuTax

/-- A scale: (weekly earnings less than, a, b); the last row is "& over" (bound 0 = none). -/
abbrev Scale := List (Int × Int × Int)

def scale1 : Scale := [(150, 1600, 1600), (371, 2117, 77550), (515, 1890, -6702), (932, 3227, 682367),
  (2246, 3200, 657202), (3303, 3900, 2229510), (0, 4700, 4872587)]
def scale2 : Scale := [(361, 0, 0), (500, 1600, 578462), (625, 2600, 1078462), (721, 1800, 578462),
  (865, 1890, 643365), (1282, 3227, 1800385), (2596, 3200, 1765769), (3653, 3900, 3583077), (0, 4700, 6506154)]
def scale3 : Scale := [(2596, 3000, 3000), (3653, 3700, 1817308), (0, 4500, 4740385)]
def scale5 : Scale := [(361, 0, 0), (721, 1600, 578462), (865, 1690, 643365), (1282, 3027, 1800385),
  (2596, 3000, 1765769), (3653, 3700, 3583077), (0, 4500, 6506154)]
def scale6 : Scale := [(361, 0, 0), (721, 1600, 578462), (843, 1690, 643365), (865, 2190, 1064962),
  (1053, 3527, 2221981), (1282, 3127, 1800385), (2596, 3100, 1765769), (3653, 3800, 3583077), (0, 4600, 6506154)]

def coeffs : Scale → Int → Int × Int
  | [], _ => (0, 0)
  | [(_, a, b)], _ => (a, b)
  | (lt, a, b) :: rest, x => if x < lt then (a, b) else coeffs rest x

/-- Weekly withholding in whole dollars for weekly earnings `x` whole dollars (x + 0.99 in the formula). -/
def withhold (s : Scale) (x : Int) : Int :=
  let (a, b) := coeffs s x
  let xc := 100 * x + 99                       -- cents
  let y := a * xc - 100 * b                    -- millionths of a dollar
  if y ≤ 0 then 0 else (y + 500000) / 1000000  -- nearest dollar, 50 cents up

/-- Medicare levy adjustment (scale 2), weekly, whole dollars; WFT and SOP per the schedule: WFT = (43,846 +
4,027 x children) / 52 to the cent; SOP = WFT x 0.1 / 0.08, cents ignored. Parameters as printed (2023-24 levels). -/
def wla2 (x : Int) (children : Int) (spouseOrKids : Bool) : Int :=
  let xc := 100 * x + 99
  if !spouseOrKids || xc < 50000 then 0 else
  let wftNum := 100 * (43846 + 4027 * children)          -- cents x 52
  let wft := (2 * wftNum + 52) / 104                     -- cents, nearest
  let sop := (wft * 1000 / 800) / 100 * 100              -- cents, whole dollars
  if xc ≥ sop then 0 else
  -- in ten-thousandths of a cent (cents x bp)
  let v := if xc < 62500 then (xc - 50000) * 1000
           else if xc < wft then xc * 200
           else wft * 200 - (xc - wft) * 800
  if v ≤ 0 then 0 else (v + 500000) / 1000000            -- to dollars, 50 cents up

end AuTax
