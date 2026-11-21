import TaxKernel.World

/-!
# Andorra 2025: parameters, each with its dated source (whole euros)

Sources (Global law corpus `andorra/national/acts`: the laws of the Consell General as enacted, BOPA; amendments are
separate laws, each read for the articles used here; copies in `../src/`):
* Llei 5/2014 de l'impost sobre la renda de les persones físiques (IRPF), in force 2014-05-21. Amending laws found by
  searching the corpus for every law that modifies it: 42/2014, 8/2015 (DF 5a), 17/2017, 6/2018 (DF 1a), 18/2019
  (DF 8a: art. 13.2 a, 35.2-35.3), 42/2022 (art. 5), 5/2023 (arts. 4, 5, 14, 21, 24, 27 bis, 29 bis, 38, 39, 45, 47-52),
  11/2023 (art. 16), 4/2025 and 5/2025 (arts. 21, 27 bis, 38, 48 bis). None changes arts. 13.2 b, 35.1, 41 or 46.
* Llei 17/2008 de la seguretat social, arts. 100 and 103 as replaced by Llei 18/2014 (arts. 26 and 29).
-/

namespace AdTax
open TaxKernel

/-- Llei 5/2014 art. 41: "El tipus de gravamen de l'impost és el 10 per cent." -/
def rate : Int := 1000
/-- Art. 35.1: "reducció per mínim personal exempt, en un import de 24.000 euros"; "s'incrementa a 40.000 euros quan
el cònjuge ... no percebi cap tipus de renda". -/
def personalMin : Int := 24000
def couplePersonalMin : Int := 40000
/-- Art. 35.2 a) (Llei 18/2019 DF 8a): "750 euros per cada descendent que sigui menor de 25 anys". -/
def childReduction : Int := 750
def childAge : Nat := 25
/-- Art. 13.2 b): other expenses "un 3 per cent dels rendiments íntegres del treball ... fins a un màxim de 2.500
euros". -/
def otherExpRate : Int := 300
def otherExpCap : Int := 2500
/-- Art. 46: "bonificació del 50 per cent de la quantitat que resulti d'aplicar el tipus de gravamen ... sobre l'import
de la base de tributació general ..., minorada en la quantitat de 24.000 euros"; "no pot excedir la quantitat de 800
euros". -/
def bonusShare : Int := 5000
def bonusCap : Int := 800
/-- Art. 39 (savings base): "La base de tributació de l'estalvi es redueix en un import de 3.000 euros". -/
def savingsMin : Int := 3000

/-- Llei 17/2008 art. 100.1, general branch, as replaced by Llei 2/2016, del 10 de març, del pressupost per a l'exercici
del 2016, disposició final sisena §1 (BOPA 20/2016 of 2016-03-30, in force 2016-03-31; it rewrites art. 100 of the
consolidated text of 16 September 2015): "Part empresarial | 7%", "Part assalariada | 3%" (W5 review pass 4,
2026-11-20; Global law `andorra/national/acts/lleis/2016-002`, copy in `ad/law/w5/`). Llei 18/2014 art. 26 had set
6 % / 2 % ("Part assalariada | 2%"); its art. 100.3 lets the budget law change the rate. No later text in the corpus
replaces art. 100 (searched to the 2026 budget law). Art. 103.2 (Llei 18/2014 art. 29): retirement branch, "Part
assalariada 3,5%". The input `adCassGeneral2014: true` applies the Llei 18/2014 rate (the model's pre-W5 output). -/
def cassGeneral : Int := 300
def cassGeneral2014 : Int := 200
def cassRetirement : Int := 350
#guard cassGeneral + cassRetirement = 650 ∧ cassGeneral2014 + cassRetirement = 550

end AdTax
