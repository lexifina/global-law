import TaxKernel.World

/-!
# North Macedonia 2025: parameters, each with its dated source (whole denars)

Sources. Global law corpus `north-macedonia/national/acts` (Службен весник) holds the Закон за данокот на личен доход
(SV 241/2018, `zakon/2018/sv241-43203`) as enacted and its amending laws 275/2019, 290/2020, 85/2021, 274/2022 as
separate acts (each read). The tax authority's page for the law (ujp.gov.mk/mk/regulativa/opis/425) says the text is
"Ажуриран со ... 274 од 20.12.2022", "Важи од: 01.01.2023": no later amendment. Contributions: Закон за придонеси од
задолжително социјално осигурување (SV 142/2008), член 25 as replaced by 247/2018 (član 7); 251/2022 and 3/2025 do
not touch the rates; 267/2025 changes the pensioners' health rate only from 2026-01-01 (član 3 of that law);
the UJP consolidated text of 07/2026 (`../src/zpzso_ujp_2026-07.txt`) was used only to locate articles.
-/

namespace MkTax
open TaxKernel

/-- ЗДЛД член 11 as replaced by 274/2022 (applies from 2023-01-01, its член 26): "(1) Данокот на личен доход се плаќа
по стапка од 10%." -/
def rate : Int := 1000
def schedule : Schedule := Schedule.flat rate

/-- Член 10 (2): "Даночното намалување при годишно пресметување на данокот на доход изнесува 96.000 денари", indexed
each year by 50 % of the growth of the average gross wage (член 10 (3)) and published by the Minister of Finance
before the year (член 10 (4)). The 2025 published amount was **not reached**; the model uses the act's printed amount
and says so in `unsupported`. -/
def taxReduction : Int := 96000

/-- Член 53 (1): rent "бруто-доходот намален за нормираните трошоци во висина од 10%". -/
def rentCosts : Int := 1000

/-- Член 12 (1) 37): "камати на депозити во износ до 15.000 денари на годишно ниво" are not taxed; член 116 as replaced
by 274/2022 член 23: the taxation of interest on term deposits applies only "од денот на пристапувањето на Република
Северна Македонија во Европската Унија". -/
def depositInterestTaxed : Bool := false

/-- Закон за придонеси член 25 (1) as replaced by 247/2018 član 7: "18,8% за задолжително пензиско и инвалидско
осигурување", "7,5% за задолжително здравствено осигурување", "0,5% стапка на дополнителен придонес за задолжително
здравствено осигурување ...", "1,2% за задолжителен придонес за осигурување во случај на невработеност". -/
def pension : Int := 1880
def health : Int := 750
def healthExtra : Int := 50
def unemployment : Int := 120

end MkTax
