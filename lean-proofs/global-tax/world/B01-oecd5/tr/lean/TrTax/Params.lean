import TaxKernel.World

/-!
# Türkiye 2025: parameters, each with its dated source (amounts in kuruş unless said otherwise)

Sources (Global law, corpus `turkey/national/acts`, publisher Mevzuat Bilgi Sistemi; files saved in `../src/`):
* GVK = Gelir Vergisi Kanunu, Kanun 193 (31/12/1960). The Mevzuat consolidation is current-only (2026-10-28);
  each provision used here carries its amendment notes ("Değişik: date-law"), and every amendment cited is dated
  before 1/1/2025 unless stated, so the wording was in force throughout 2025.
* Tebliğ 41166 = Gelir Vergisi Genel Tebliği (Seri No: 329), in force 1/1/2025 (`teblig/2024/41166`): the 2025
  amounts of GVK art. 103 and the other revalued amounts (GVK mükerrer 123, yeniden değerleme oranı 43,93 %).
* SSK = 5510 sayılı Sosyal Sigortalar ve Genel Sağlık Sigortası Kanunu; İSK = 4447 sayılı İşsizlik Sigortası
  Kanunu; DVK = 488 sayılı Damga Vergisi Kanunu.
-/

namespace TrTax
open TaxKernel

/-- Kuruş per lira. -/
def KR : Int := 100

/-! ## GVK art. 103 as revalued for 2025 (Tebliğ 41166 madde 3 (3)) -/

/-- Tebliğ 41166 m. 3 (3), non-wage tariff: "158.000 TL'ye kadar % 15; 330.000 TL'nin 158.000 TL'si için 23.700 TL,
fazlası % 20; 800.000 TL'nin 330.000 TL'si için 58.100 TL ..., fazlası % 27; 4.300.000 TL'nin 800.000 TL'si için
185.000 TL ..., fazlası % 35; 4.300.000 TL'den fazlasının ... 1.410.000 TL ..., fazlası % 40" (thresholds in TL). -/
def tariffTL : Schedule := Schedule.ofList [(0, 1500), (158000, 2000), (330000, 2700), (800000, 3500), (4300000, 4000)]

/-- Same, wage tariff: "(ücret gelirlerinde 1.200.000 TL'nin 330.000 TL'si için 58.100 TL), fazlası % 27;
(ücret gelirlerinde 4.300.000 TL'nin 1.200.000 TL'si için 293.000 TL), fazlası % 35; (ücret gelirlerinde
4.300.000 TL'den fazlasının 4.300.000 TL'si için 1.378.000 TL), fazlası % 40". -/
def wageTariffTL : Schedule := Schedule.ofList [(0, 1500), (158000, 2000), (330000, 2700), (1200000, 3500), (4300000, 4000)]

/-- The tariff as printed (lower limit, tax at the limit in TL, marginal rate): non-wage income. -/
def printedTL : List CumRow :=
  [⟨0, 0, 1500⟩, ⟨158000, 23700, 2000⟩, ⟨330000, 58100, 2700⟩, ⟨800000, 185000, 3500⟩, ⟨4300000, 1410000, 4000⟩]

/-- The tariff as printed: wages. -/
def printedWageTL : List CumRow :=
  [⟨0, 0, 1500⟩, ⟨158000, 23700, 2000⟩, ⟨330000, 58100, 2700⟩, ⟨1200000, 293000, 3500⟩, ⟨4300000, 1378000, 4000⟩]

/-- The tariffs in kuruş (the model computes in kuruş). -/
def tariff : Schedule := tariffTL.mapLo (· * KR)
def wageTariff : Schedule := wageTariffTL.mapLo (· * KR)

/-! ## Minimum wage, social insurance, stamp duty -/

/-- Gross monthly minimum wage 2025, 26.005,50 TL. Official secondary: Gelir Vergisi Genel Tebliği (Seri No: 331)
(`teblig/2025/42582` m. 3, Örnek 1: "Brüt asgari ücretin 40 katı (26.005,50 x 40)", for September 2025) and the same
tebliğ's note "(*) ... 2025 yılı sigorta prim tavanı 195.041,40 TL". The Asgari Ücret Tespit Komisyonu decision itself
is not in the record; no other 2025 minimum wage was found in it (searched "asgari ücret", 2025). -/
def minWage : Int := 2600550

/-- SSK art. 81 (a) (2025 wording, before Kanun 7566 art. 23 from 1/1/2026): "Malûllük, yaşlılık ve ölüm sigortaları
prim oranı, sigortalının prime esas kazancının %20'sidir. Bunun %9'u sigortalı hissesi" (dipnot 141 gives the
pre-2026 wording). -/
def rateMYO : Int := 900
/-- SSK art. 81 (f): "Genel sağlık sigortası primi ... prime esas kazancın %12,5'idir. Bu primin %5'i sigortalı". -/
def rateGSS : Int := 500
/-- İSK art. 49: "İşsizlik sigortası primi, sigortalının ... prime esas aylık brüt kazançlarından % 1 sigortalı". -/
def rateIS : Int := 100
/-- Employee total, 15 %. -/
def rateEmployee : Int := rateMYO + rateGSS + rateIS

/-- SSK art. 82: upper limit of daily earnings "16 yaşından büyük sigortalıların günlük kazanç alt sınırının 7,5 katı"
(dipnot 155: 7,5 from 1/1/2017; dipnot 156 and the yürürlük list: "9" by Kanun 7566 only from 1/1/2026); lower limit
"asgarî ücretin otuzda biri". Monthly ceiling = 7,5 × the minimum wage. -/
def ssCeilingNum : Int := 15   -- 7,5 = 15/2
def ssCeiling : Int := minWage * ssCeilingNum / 2

/-- DVK (1) sayılı tablo IV-1 (b): wage receipts "(Binde 7,59)". In tenths of a basis point: 7,59 ‰ = 759/100000. -/
def stampNum : Int := 759
def stampDen : Int := 100000

/-! ## Other 2025 amounts (Tebliğ 41166 m. 3 (2)) -/

/-- GVK art. 21 as revalued: "mesken kira gelirleri için uygulanan istisna tutarı 47.000 TL" (TL). -/
def rentExemptTL : Int := 47000
/-- GVK art. 21 second paragraph: no exemption when gross income exceeds "103 üncü maddede yazılı tarifenin üçüncü
diliminde ücret gelirleri için yer alan tutarı" = 1.200.000 TL in 2025 (Tebliğ 41166 m. 3 (3)). -/
def rentExemptLimitTL : Int := 1200000
/-- GVK art. 74 last paragraph: "hasılatlarından % 15'ini götürü olarak indirebilirler". -/
def rentLumpRate : Int := 1500
/-- GVK art. 86 (1) (b): single-employer wages are not declared up to "tarifenin dördüncü gelir diliminde yer alan
tutarı" = 4.300.000 TL in 2025. -/
def wageDeclLimitTL : Int := 4300000

end TrTax
