import PlTax.Params

/-!
# The scale, PIT art. 27 ust. 1, and splitting, art. 6 ust. 2 and 4d

`scaleTax g` is the tax on a base of `g` grosze (in use a whole number of złoty, or half of one for splitting), in
grosze: the kernel schedule 12 % / 32 % less the kwota zmniejszająca podatek 3600 zł, never below nil.
-/

namespace PlTax

/-- art. 27 ust. 1 on a base in grosze, result in grosze. -/
def scaleTax (g : Int) : Int := pos (rhu (schedRaw plScale g) 10000 - kwotaZmniejszajaca)

/-- The statute's own two-row form: "12% minus kwota zmniejszająca podatek 3600 zł" up to 120 000 zł, "10 800 zł + 32%
nadwyżki ponad 120 000 zł" above (base in grosze, `0 ≤ g`). -/
def scaleStatute (g : Int) : Int :=
  if g ≤ 12000000 then pos (rhu (g * 1200) 10000 - 360000)
  else 1080000 + rhu ((g - 12000000) * 3200) 10000

/-- Splitting, art. 6 ust. 2 (spouses) and ust. 4d (single parent): "podatek określa się ... w podwójnej wysokości
podatku obliczonego od połowy łącznych dochodów", on a base in whole złoty: half the base is `50 × base` grosze. -/
def splitTax (baseZl : Int) : Int := 2 * scaleTax (50 * baseZl)

/-- Separate assessment of two bases in whole złoty. -/
def sepTax (aZl bZl : Int) : Int := scaleTax (100 * aZl) + scaleTax (100 * bZl)

/-- Joint assessment of two spouses' bases. -/
def jointTax (aZl bZl : Int) : Int := splitTax (aZl + bZl)


/-! ## Tax year 2022 (tests round 4): the art. 26 refund of Dz.U. 2022 poz. 1265

Ustawa z 9 czerwca 2022 r. (Dz.U. 2022 poz. 1265, `refs/years/DU_2022_1265.txt`): the 12 % / 3 600 zł scale (art. 27
ust. 1 as amended) applies "do dochodów (przychodów) uzyskanych od dnia 1 stycznia 2022 r."; art. 26 ust. 1: "W przypadku
gdy podatek należny za 2022 r. … jest wyższy od hipotetycznego podatku należnego za 2022 r., właściwy naczelnik urzędu
skarbowego zwraca podatnikowi kwotę tej różnicy"; ust. 2: for taxpayers whose employment and business revenue (art. 26
ust. 4a's A) is "od 68 412 zł do 133 692 zł", spouses filing jointly per art. 26 ust. 4c (half of their combined A); ust. 3:
the hypothetical tax is the new law's computation with the ulga dla pracowników (art. 26 ust. 1 pkt 2aa) and the art. 27
ust. 1 scale "w brzmieniu z dnia 30 czerwca 2022 r."; ust. 4–5: the same comparison for the refundable part of the art. 27f
relief. Polski Ład text (Dz.U. 2021 poz. 2105, `refs/DU_2021_2105.txt`): art. 27 ust. 1 "17% minus kwota zmniejszająca
podatek 5100 zł … 120 000 … 15 300 zł + 32% nadwyżki ponad 120 000 zł"; art. 26 ust. 4a "(A × 6,68% – 4566 zł) ÷ 0,17, dla A
wynoszącego co najmniej 68 412 zł i nieprzekraczającego kwoty 102 588 zł", "(A × (-7,35%) + 9829 zł) ÷ 0,17, dla A wyższego
od 102 588 zł i nieprzekraczającego kwoty 133 692 zł"; ust. 4c: spouses filing jointly "od połowy sumy łącznych przychodów".
Since the relief's used and refunded parts make the net tax a monotone function of the tax, taking the smaller of the two
taxes before the art. 27f relief gives the art. 26 ust. 1, 4 and 5 result. -/

/-- art. 27 ust. 1 as of 30 June 2022, base in grosze. -/
def scaleTaxOld (g : Int) : Int :=
  if g ≤ 12000000 then pos (rhu (g * 1700) 10000 - 510000) else 1530000 + rhu ((g - 12000000) * 3200) 10000

/-- art. 26 ust. 4a (version of 30 June 2022): the ulga dla pracowników for revenue `a` złoty, in grosze. -/
def ulgaKS (a : Int) : Int :=
  if 68412 ≤ a ∧ a ≤ 102588 then pos ((a * 668 - 45660000) / 17)
  else if 102588 < a ∧ a ≤ 133692 then pos ((98290000 - a * 735) / 17)
  else 0

def refund2022Eligible (a : Int) : Bool := decide (68412 ≤ a ∧ a ≤ 133692)

/-- The hypothetical base (whole złoty) of a base `bZl` after deducting the ulga computed on revenue `a`. -/
def hypBase (bZl a : Int) : Int := zl (pos (100 * bZl - ulgaKS a))

theorem ulgaKS_values : ulgaKS 68411 = 0 ∧ ulgaKS 102588 = 1345222 ∧ ulgaKS 133692 = 1551 ∧ ulgaKS 133693 = 0 := by decide

end PlTax
