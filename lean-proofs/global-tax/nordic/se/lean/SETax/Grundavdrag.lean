import SETax.Params

/-!
# Grundavdrag: IL 63 kap. 3 §, 3 a §, 5 § and 1 kap. 5 § (inkomstår 2025)

Text for 2025. 63 kap. 3 § (Lag 2011:1256, unchanged since 2012):

> Fastställd förvärvsinkomst / Grundavdrag
> överstiger inte 0,99 prisbasbelopp: 0,423 prisbasbelopp
> överstiger 0,99 men inte 2,72 prisbasbelopp: 0,423 prisbasbelopp ökat med 20 procent av det belopp med vilket
> den fastställda förvärvsinkomsten överstiger 0,99 prisbasbelopp
> överstiger 2,72 men inte 3,11 prisbasbelopp: 0,77 prisbasbelopp
> överstiger 3,11 men inte 7,88 prisbasbelopp: 0,77 prisbasbelopp minskat med 10 procent av det belopp med vilket
> den fastställda förvärvsinkomsten överstiger 3,11 prisbasbelopp
> överstiger 7,88 prisbasbelopp: 0,293 prisbasbelopp

63 kap. 3 a § as worded by SFS 2024:1131 (in force 2025-01-01, "tillämpas första gången på beskattningsår som
börjar efter den 31 december 2024"): "För dem som vid beskattningsårets ingång har fyllt 66 år är grundavdraget
beloppet enligt 3 § med tillägg av följande särskilda belopp" (table below, `extraN`). SFS 2025:1376 replaced the
four top rows for 2026 (`extraN2026`).

63 kap. 2 § tredje stycket: "Avdraget ska avrundas uppåt till helt hundratal kronor." 63 kap. 5 §: "Grundavdraget
får inte överstiga den skattskyldiges sammanlagda överskott av aktiv näringsverksamhet och av tjänst, minskat med
hans allmänna avdrag." 1 kap. 5 §: the sum of tjänst and näringsverksamhet less allmänna avdrag "avrundas nedåt till
helt hundratal kronor och är den fastställda förvärvsinkomsten"; "Från den fastställda förvärvsinkomsten dras
grundavdrag ... Det återstående beloppet är den beskattningsbara förvärvsinkomsten."

Exact arithmetic: every coefficient is a multiple of 0,001 prisbasbelopp or of 0,01 %, so the statute's amounts are
exact in units of 10⁻⁷ kr (`N` per krona): `k/1000 × pbb` is `k·pbb·10⁴`; `r` basis points of an amount `F` in
milli-kronor (`F = 1000 × kr`) is `r·F`. One rounding, up to the hundred, at the end (`ga`).
-/

namespace SETax
open TaxKernel

/-- 10⁻⁷ kr per krona. -/
def N : Int := 10000000

/-- `k` thousandths of a prisbasbelopp, in 10⁻⁷ kr. -/
def kN (k pbb : Int) : Int := k * pbb * 10000

/-- 63 kap. 3 §, exact (10⁻⁷ kr), as a function of fastställd förvärvsinkomst `f` (kr). -/
def baseN (pbb f : Int) : Int :=
  let F := 1000 * f
  if F ≤ 990 * pbb then kN 423 pbb
  else if F ≤ 2720 * pbb then kN 423 pbb + 2000 * (F - 990 * pbb)
  else if F ≤ 3110 * pbb then kN 770 pbb
  else if F ≤ 7880 * pbb then kN 770 pbb - 1000 * (F - 3110 * pbb)
  else kN 293 pbb

/-- 63 kap. 3 a § (SFS 2024:1131), the "särskilt belopp" for those who had turned 66 at 1 January 2025, exact. -/
def extraN (pbb f : Int) : Int :=
  let F := 1000 * f
  if F ≤ 910 * pbb then kN 687 pbb                       -- "0,687 prisbasbelopp"
  else if F ≤ 1110 * pbb then kN 885 pbb - 2000 * F      -- "0,885 ... minskat med 20 procent av ... förvärvsinkomsten"
  else if F ≤ 1965 * pbb then kN 600 pbb + 570 * F       -- "0,600 ... ökat med 5,7 procent"
  else if F ≤ 2720 * pbb then kN 333 pbb + 1949 * F      -- "0,333 ... ökat med 19,49 procent"
  else if F ≤ 3110 * pbb then 3949 * F - kN 212 pbb      -- "39,49 procent ... minskat med 0,212"
  else if F ≤ 3240 * pbb then 4949 * F - kN 523 pbb      -- "49,49 procent ... minskat med 0,523"
  else if F ≤ 5000 * pbb then kN 96 pbb + 3040 * F       -- "0,096 ... ökat med 30,4 procent"
  else if F ≤ 7880 * pbb then kN 186 pbb + 2860 * F      -- "0,186 ... ökat med 28,6 procent"
  else if F ≤ 8080 * pbb then kN 872 pbb + 1990 * F      -- "0,872 ... ökat med 19,9 procent"
  else if F ≤ 10940 * pbb then kN 2480 pbb               -- "2,48 prisbasbelopp"
  else if F ≤ 12470 * pbb then kN 9263 pbb - 6200 * F    -- "9,263 ... minskat med 62 procent"
  else kN 1532 pbb                                       -- "1,532 prisbasbelopp"

/-- 63 kap. 3 a § as worded for 2026 by SFS 2025:1376 (comparison only; rows above 3,24 pbb changed). -/
def extraN2026 (pbb f : Int) : Int :=
  let F := 1000 * f
  if F ≤ 3240 * pbb then extraN pbb f
  else if F ≤ 5000 * pbb then 3560 * F - kN 73 pbb       -- "35,6 procent ... minskat med 0,073"
  else if F ≤ 7880 * pbb then kN 17 pbb + 3380 * F       -- "0,017 ... ökat med 33,8 procent"
  else if F ≤ 8080 * pbb then kN 703 pbb + 2510 * F      -- "0,703 ... ökat med 25,1 procent"
  else if F ≤ 11160 * pbb then kN 2732 pbb               -- "2,732 prisbasbelopp"
  else if F ≤ 12840 * pbb then kN 9651 pbb - 6200 * F    -- "9,651 ... minskat med 62 procent"
  else kN 1691 pbb                                       -- "1,691 prisbasbelopp"

/-- 63 kap. 2 § "avrundas uppåt till helt hundratal kronor", applied once to the sum (3 a §: "beloppet enligt 3 §
med tillägg av ... särskilda belopp"; SKV 433 avsnitt 6.2: "delvärdena ... inte ska avrundas innan summeringen"). -/
def roundUp100 (n : Int) : Int := ceilDiv n (100 * N) * 100

/-- Grundavdrag before the 63 kap. 5 § cap. `old` = turned 66 before the year began. -/
def gaRaw (p : Params) (old : Bool) (f : Int) : Int :=
  roundUp100 (baseN p.pbb f + (if old then extraN p.pbb f else 0))

/-- Grundavdrag (63 kap. 3, 3 a, 5 §§), capped by the fastställd förvärvsinkomst `f ≥ 0` (5 §: the overskott
less allmänna avdrag; `f` is that amount rounded down, so the cap on the taxable income is the same). -/
def ga (p : Params) (old : Bool) (f : Int) : Int := min (pos f) (gaRaw p old f)

/-- 1 kap. 5 §: fastställd förvärvsinkomst = (tjänst + näringsverksamhet − allmänna avdrag) rounded down to 100. -/
def ffi (earned : Int) : Int := toMultiple .down 100 (pos earned)

/-- 1 kap. 5 §: beskattningsbar förvärvsinkomst. -/
def bfi (p : Params) (old : Bool) (f : Int) : Int := pos (f - ga p old f)

end SETax
