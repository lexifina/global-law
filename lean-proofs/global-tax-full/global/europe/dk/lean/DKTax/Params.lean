import TaxKernel

/-!
# Danish personal income tax: the parameters of one income year (indkomståret)

Every amount is either printed in a statute or derived from a statute's 2010-level grundbeløb by
personskatteloven (PSL) § 20 (`reg`). Sources (full list with URLs: `refs/PARAMS.md`):

* PSL = LBK nr. 1284 af 14/06/2021 (retsinformation.dk/eli/lta/2021/1284) as amended by lov nr. 252/2022,
  610/2023, 1564/2023, 108/2024, 482/2024, 1691/2024 (all read from retsinformation.dk XML, `refs/web/`).
  NB the Global law record of PSL stops at LBK 1284/2021 and holds none of these amending acts (finding F1).
* LL = ligningsloven, LBK nr. 42 af 13/01/2023 as amended by lov nr. 482 af 22/05/2024 § 2 (§ 9 J).
* AMBL = arbejdsmarkedsbidragsloven (Global law denmark/national/acts/lov/2009/471, § 1: "Bidraget udgør 8 pct.").
* Lov om en børne- og ungeydelse, LBK nr. 724 af 25/05/2022 (§ 1 a taper); amounts: Skatteministeriet,
  "Børne- og ungeydelse – en historisk oversigt", Tabel 1 (svmn.dk, 12-01-2026).
* Lov om skattefri kompensation for forhøjede energi- og miljøafgifter (grøn check), LBK nr. 1306 af 22/09/2022.
* Reguleringstal (PSL § 20): Skatteministeriet, "Reguleringstallet i PSL § 20 – en historisk oversigt":
  2023 121,8; 2024 126,1; 2025 131,0 (bekendtgørelse nr. 983 af 20. august 2024).
* Municipal and church tax rates: Danmarks Statistik, table PSKAT (api.statbank.dk), København 2025: 23,50 % and
  0,80 %; whole country 25,07 % (rounded).

Units: money in whole kroner (`Int`); rates in basis points (1201 = 12,01 %), except the municipal and church
rates, which are in units of 10⁻⁷ (`rate7`, 2 350 000 = 23,50 %) so that the OECD's unrounded average municipal
rate (25,06798 %) can be reproduced.
-/

namespace DKTax
open TaxKernel

/-- PSL § 20, stk. 2: "Ved regulering ... forhøjes eller nedsættes beløbene med samme procent som den, hvormed
årets reguleringstal afviger fra 100. De således regulerede beløb afrundes opad til nærmeste kronebeløb, der kan
deles med 100." `rt` is the reguleringstal in tenths (131,0 → 1310). -/
def reg (rt base2010 : Int) : Int := ceilDiv (base2010 * rt) 100000 * 100

/-- One income year's parameters. -/
structure Params where
  year : Nat
  /-- PSL § 20 reguleringstal, tenths. -/
  rt : Int
  /-- PSL § 6, stk. 2: bundskat percentage (bp). -/
  bundRate : Int
  /-- PSL § 7, stk. 1: "15 pct." (topskat, until 2025). -/
  topRate : Int := 1500
  /-- PSL § 7, stk. 2: bundfradrag 467.000 kr. (2010-niveau), regulated. (From 2026 § 7 is "mellemskat".) -/
  topThreshold : Int
  /-- From 2026 (lov 482/2024): PSL § 7 a topskat and § 8 toptopskat on personal income, (threshold, rate bp). -/
  extraBands : List (Int × Int) := []
  /-- PSL § 7, stk. 1: grundbeløb for positive nettokapitalindkomst, 40.000 kr. (2010-niveau), regulated. -/
  kapGrund : Int
  /-- PSL § 19, stk. 1: skatteloft for personal income (bp). -/
  skatteloft : Int
  /-- PSL § 19, stk. 2: skatteloft for positive nettokapitalindkomst, "42,0 pct." -/
  kapLoft : Int := 4200
  /-- PSL § 10, stk. 1: personfradrag, 39.350 kr. (2010-niveau), regulated. -/
  pf : Int
  /-- PSL § 8 a, stk. 1-2: grundbeløb for aktieindkomst (progressionsgrænse), regulated. -/
  aktieLimit : Int
  aktieLow : Int := 2700
  aktieHigh : Int := 4200
  /-- PSL § 11: nedslag 8 pct. of negative nettokapitalindkomst up to 50.000 kr. (not regulated). -/
  negKapRate : Int := 800
  negKapLimit : Int := 50000
  /-- AMBL § 1: "Bidraget udgør 8 pct. af grundlaget." -/
  amRate : Int := 800
  /-- LL § 9 J, stk. 2: beskæftigelsesfradrag percentage and maximum. -/
  bfRate : Int
  bfCap : Int
  /-- LL § 9 J, stk. 4: extra beskæftigelsesfradrag for enlige forsørgere. -/
  enligRate : Int
  enligCap : Int
  /-- LL § 9 K: jobfradrag 4,5 pct. of the § 9 J base above 171.300 kr. (2010), at most 2.200 kr. (2010). -/
  jobRate : Int := 450
  jobStart : Int
  jobCap : Int
  /-- LL § 9 L: ekstra pensionsfradrag 12 pct. (32 pct. from the 15th year before folkepensionsalderen) of at
  most 63.900 kr. (2010) of pension contributions. -/
  pensRateLow : Int := 1200
  pensRateHigh : Int := 3200
  pensCap : Int
  /-- PBL § 16, stk. 2: at most 50.000 kr. (2010) a year to ratepension (and ophørende livrente). -/
  ratepenCap : Int
  /-- LL § 13, stk. 1: union fees deductible up to this amount. -/
  unionCap : Int
  /-- LL § 8 A, stk. 1: gifts to approved charities deductible up to 14.500 kr. (2010), regulated. -/
  giftCap : Int
  /-- Børne- og ungeydelse per year by age band 0-2, 3-6, 7-14, 15-17 (lov § 2 amounts, Skatteministeriet table). -/
  buy02 : Int
  buy36 : Int
  buy714 : Int
  buy1517 : Int
  /-- Lov om en børne- og ungeydelse § 1 a: reduced by 2 pct. of the topskat base above 700.000 kr. (2010). -/
  buyTaperStart : Int
  buyTaperRate : Int := 200
  /-- Grøn check (LBK 1306/2022) § 1, stk. 2: 120 kr. per child, at most 240 kr.; § 2: withdrawn by 7,5 pct. of
  the topskat base above 362.800 kr. (2010-niveau). -/
  gcChild : Int := 120
  gcStart : Int
  gcRate : Int := 750
  /-- LBK 1306/2022 § 1, stk. 1: the adult (18+, not a pensioner) grøn check, "for indkomståret 2022 med et beløb,
  der udgør 263 kr."; 0 from 2023 (Skatteministeriet, "Grøn check – en historisk oversigt"). -/
  gcAdult : Int := 0
  /-- Børnetilskudsloven §§ 2-3: ordinært (per child) and ekstra (per family) børnetilskud, per year. -/
  ordBT : Int
  ekstraBT : Int
  /-- ATP employee and employer contributions per year, full-time (A-sats). -/
  atpOwn : Int
  atpEmployer : Int
  /-- Default municipality: København, kommuneskat and kirkeskat (rate7). -/
  munRate7 : Int
  churchRate7 : Int
  deriving Repr

/-- Indkomståret 2025. -/
def p2025 : Params where
  year := 2025
  rt := 1310
  -- lov nr. 108 af 31/01/2024 § 1: "For indkomståret 2024 og efterfølgende indkomstår udgør procenten 12,01."
  bundRate := 1201
  topThreshold := reg 1310 467000          -- 611.800
  kapGrund := reg 1310 40000               -- 52.400
  -- PSL § 19, stk. 1 (LBK 1284/2021): "For indkomståret 2022 og efterfølgende indkomstår udgør procenten 52,07."
  -- (lov 482/2024 § 1 nr. 15 sets 44,57 pct. with effect from 2026, § 10, stk. 4.)
  skatteloft := 5207
  -- lov nr. 1564 af 12/12/2023 § 1 nr. 2: "personfradragets grundbeløb 39.350 kr. (2010-niveau)" (all ages).
  pf := reg 1310 39350                     -- 51.600
  -- lov nr. 1691 af 30/12/2024 § 4: "et grundbeløb på 51.500 kr. (2010-niveau) for indkomståret 2025".
  aktieLimit := reg 1310 51500             -- 67.500
  -- lov nr. 482 af 22/05/2024 § 2 nr. 1: "For indkomståret 2025 udgør procenten 12,3, og grundbeløbet 42.400 kr."
  bfRate := 1230
  bfCap := reg 1310 42400                  -- 55.600
  -- lov nr. 482/2024 § 2 nr. 3: "For indkomståret 2025 og efterfølgende indkomstår udgør procenten 11,5, og
  -- grundbeløbet 36.800 kr. (2010-niveau)."
  enligRate := 1150
  enligCap := reg 1310 36800               -- 48.300
  jobStart := reg 1310 171300              -- 224.500
  jobCap := reg 1310 2200                  -- 2.900
  pensCap := reg 1310 63900                -- 83.800
  ratepenCap := reg 1310 50000             -- 65.500
  -- LL § 13: 7.000 kr. (Skatteministeriet tables: 7.000 kr. in 2024 and in 2026; not regulated).
  unionCap := 7000
  giftCap := reg 1310 14500                -- 19.000
  -- Skatteministeriet, "Børne- og ungeydelse – en historisk oversigt", Tabel 1, 2025: 21.168 / 16.764 / 13.188 kr.
  buy02 := 21168
  buy36 := 16764
  buy714 := 13188
  buy1517 := 13188
  buyTaperStart := reg 1310 700000         -- 917.000
  gcStart := reg 1310 362800               -- 475.300
  -- Official (round 2, 2026-11-19): Beskæftigelsesministeriet, "Vejledning om regulering pr. 1. januar 2025 af
  -- satser på Beskæftigelsesministeriets område" (VEJ nr 10154 af 19/12/2024, refs/web/vej_2024_10154.xml), table
  -- for lov om børnetilskud: "1. Ordinært børnetilskud (§ 2) 6.664 [kr. årligt] 1.666 [kr. kvartal]",
  -- "2. Ekstra børnetilskud (§ 3) 6.792 1.698". Same values as the earlier OECD-derived inference, now sourced.
  ordBT := 6664
  ekstraBT := 6792
  -- Round 15: statute BEK nr 1621 af 12/12/2023 § 2, stk. 1 (A-sats 3.564 kr., still in force in 2025) and
  -- ATP-loven § 15, stk. 6 (member 1/3): 1.188 kr. Earlier inference, kept as a check:
  -- OECD Taxing Wages 2025 rows: DSSCIT − 8 % × GEBT = 1.188,00 kr. for every 2025 single (99 kr. a month);
  -- the employer pays twice the employee's share (Skatteministeriet worked examples: "Eget og arbejdsgiver
  -- ATP-indbetaling 3*[2]").
  atpOwn := 1188
  atpEmployer := 2376
  munRate7 := 2350000                      -- København 2025: 23,50 % (PSKAT)
  churchRate7 := 80000                     -- København 2025: 0,80 % (PSKAT)

/-- Indkomståret 2024 (for the OECD 2024 rows). -/
def p2024 : Params where
  year := 2024
  rt := 1261
  bundRate := 1201                         -- lov nr. 108/2024
  topThreshold := reg 1261 467000          -- 588.900
  kapGrund := reg 1261 40000               -- 50.500
  skatteloft := 5207
  pf := reg 1261 39350                     -- 49.700
  aktieLimit := reg 1261 48300             -- 61.000 (PSL § 8 a as in LBK 1284/2021: 48.300 kr.)
  -- lov 482/2024 § 2 nr. 1: "For indkomståret 2024 udgør procenten 10,65 og grundbeløbet 35.700 kr."
  bfRate := 1065
  bfCap := reg 1261 35700                  -- 45.100
  enligRate := 625                         -- "For indkomståret 2024 udgør procenten 6,25, og grundbeløbet 20.000 kr."
  enligCap := reg 1261 20000               -- 25.300
  jobStart := reg 1261 171300              -- 216.100
  jobCap := reg 1261 2200                  -- 2.800
  pensCap := reg 1261 63900                -- 80.600
  ratepenCap := reg 1261 50000             -- 63.100
  unionCap := 7000
  giftCap := reg 1261 14500
  buy02 := 20496
  buy36 := 16224
  buy714 := 12768
  buy1517 := 12768
  buyTaperStart := reg 1261 700000         -- 882.700
  gcStart := reg 1261 362800               -- 457.500
  -- Børnetilskudsloven § 2 (ordinært, per child) and § 3 (ekstra, per sole provider), 2024 regulated amounts:
  -- "Ordinært, § 2 6.432" / "Ekstra, § 3 6.556" kr./år (SEGES/Landbrugsinfo, "Aktuelle satser familie- og
  -- socialjura", januar 2024, table "Børnetilskud mv. kr./år"; round 1, 2026-11-19).
  ordBT := 6432
  ekstraBT := 6556
  -- Round 15 (statute): BEK nr 1621 af 12/12/2023 (ATP), § 2, stk. 1: "Det almindelige årsbidrag udgør 3.564 kr.
  -- (A-satsen)"; Bilag 1, månedslønnede "Mindst 117 (fuldtid) 99 198 297"; § 13: "træder i kraft den 1. januar
  -- 2024"; ATP-loven § 15, stk. 6: "Arbejdsgiveren betaler 2/3 af bidraget og medlemmet 1/3" (refs/web/
  -- atp_bek_2023_1621.xml). Was 1.136 / 2.272 (94,65 kr. a month, taken from the OECD's 2024 rows, referee-derived).
  atpOwn := 1188
  atpEmployer := 2376
  munRate7 := 2360000                      -- København 2024: 23,60 %
  churchRate7 := 80000

/-- Indkomståret 2022 (round 2, 2026-11-19). Sources: Skatteministeriet, "Centrale beløbsgrænser i
skattelovgivningen 2018-2024" (refs/web/centrale_2018_2024.html; 2022 column) and "Centrale skattesatser i
skattelovgivningen 2018-2024" (refs/web/satser_2018_2024.html; 2022 column); Danmarks Statistik PSKAT
(København 2022: kommunal udskrivningsprocent 23,80, kirkeskatteprocent 0,80); LBK 1306/2022 (grøn check). -/
def p2022 : Params where
  year := 2022
  rt := 1183                               -- "Reguleringspristal / reguleringstal ... 118,3" (2022)
  bundRate := 1209                         -- "Bundskat ... 12,09" (2022)
  topThreshold := reg 1183 467000          -- 552.500 ("Beløbsgrænse ved topskat")
  kapGrund := reg 1183 40000               -- 47.400
  skatteloft := 5207                       -- "Skatteloft, personlig indkomst ... 52,07"
  pf := reg 1183 39350                     -- 46.600 ("Almindeligt personfradrag")
  aktieLimit := reg 1183 48300             -- 57.200
  bfRate := 1065                           -- "Beskæftigelsesfradrag ... 10,65"
  bfCap := 43500                           -- "Maks. beskæftigelsesfradrag ... 43.500"
  enligRate := 625                         -- "Ekstra beskæftigelsesfradrag til enlige forsørgere ... 6,25"
  enligCap := reg 1183 20000               -- 23.700
  jobStart := reg 1183 171300              -- 202.700 ("Bundgrænse for grundlaget for beregning af jobfradrag")
  jobCap := reg 1183 2200                  -- 2.700 ("Maks. jobfradrag")
  pensCap := reg 1183 63900                -- 75.600
  ratepenCap := reg 1183 50000
  unionCap := 6000                         -- "Loft over fradrag for fagforeningskontingent ... 6.000"
  giftCap := reg 1183 14500
  buy02 := 18612                           -- børne- og ungeydelse 2022: 18.612 / 14.724 / 11.592 / 11.592
  buy36 := 14724
  buy714 := 11592
  buy1517 := 11592
  buyTaperStart := reg 1183 700000         -- 828.100 ("Aftrapningsgrænse for børne- og ungeydelse")
  gcChild := 90                            -- LBK 1306/2022 § 1, stk. 2: "For indkomståret 2022 udgør beløbet 90 kr. pr. barn, dog maksimalt 180 kr."
  gcStart := reg 1183 362800
  gcAdult := 263                           -- LBK 1306/2022 § 1, stk. 1: "for indkomståret 2022 ... 263 kr."
  ordBT := 0                               -- børnetilskud 2022: no dated table found (not modelled; SP67 2022 benefits low)
  ekstraBT := 0
  -- BEK nr 1385 af 25/11/2015 (ATP; in force until 14/12/2023), § 3: "Det almindelige årsbidrag ... udgør 3.408 kr.";
  -- Bilag 1 "Mindst 117 (fuldtid) 94,65 189,35 284,00" kr. a month: 1.135,80 a year, rounded (refs/web/
  -- atp_bek_2015_1385.xml; round 15).
  atpOwn := 1136
  atpEmployer := 2272
  munRate7 := 2380000                      -- København 2022: 23,80 % (PSKAT)
  churchRate7 := 80000

/-- Indkomståret 2023 (Skatteministeriet's worked examples). -/
def p2023 : Params where
  year := 2023
  rt := 1218
  bundRate := 1206                         -- lov nr. 610/2023: "udgør procenten 12,06"
  topThreshold := reg 1218 467000          -- 568.900
  kapGrund := reg 1218 40000               -- 48.800
  skatteloft := 5207
  pf := reg 1218 39350                     -- 48.000
  aktieLimit := reg 1218 48300             -- 58.900
  bfRate := 1065                           -- LL § 9 J, stk. 2 (LBK 42/2023): 2023 "10,65 ... 37.400 kr."
  bfCap := reg 1218 37400                  -- 45.600
  enligRate := 625
  enligCap := reg 1218 20000               -- 24.400
  jobStart := reg 1218 171300              -- 208.700
  jobCap := reg 1218 2200                  -- 2.700
  pensCap := reg 1218 63900                -- 77.900
  ratepenCap := reg 1218 50000             -- 60.900
  unionCap := 6000                         -- LL § 13 (LBK 42/2023): "kan ikke overstige et beløb på 6.000 kr."
  giftCap := reg 1218 14500
  buy02 := 19644                           -- incl. the one-off 660 kr. of 1st quarter 2023
  buy36 := 15684
  buy714 := 12480
  buy1517 := 12480
  buyTaperStart := reg 1218 700000         -- 852.600
  gcStart := reg 1218 362800               -- 441.900
  ordBT := 0
  ekstraBT := 0
  atpOwn := 1136                           -- BEK 1385/2015 § 3 and Bilag 1, as 2022 (round 15)
  atpEmployer := 2272
  munRate7 := 2350000
  churchRate7 := 80000

/-- Indkomståret 2026 (only for the timing comparison across the reform, FINDINGS): lov nr. 482 af 22/05/2024
§ 1 (mellemskat 7,5 % above 467.000 kr. (2010), topskat 7,5 % above 566.500 kr. (2010), toptopskat 5 % above
1.888.300 kr. (2010); skatteloft 44,57 %), § 2 (beskæftigelsesfradrag 12,75 %, 46.100 kr. (2010)); lov 1691/2024
(aktieindkomst 57.800 kr. (2010)); reguleringstal 137,3. Amounts as printed by Skatteministeriet for 2026
(theorem `skm2026_table_eq_formula`). Not modelled for 2026: the senior beskæftigelsesfradrag (§ 9 J, stk. 5-6),
AM-bidrag 0 % for under-18s (lov 96/2025). ATP assumed unchanged. -/
def p2026 : Params where
  year := 2026
  rt := 1373
  bundRate := 1201
  topRate := 750
  topThreshold := reg 1373 467000          -- 641.200
  extraBands := [(reg 1373 566500, 750), (reg 1373 1888300, 500)]   -- 777.900, 2.592.700
  kapGrund := reg 1373 40000               -- 55.000
  skatteloft := 4457
  pf := reg 1373 39350                     -- 54.100
  aktieLimit := reg 1373 57800             -- 79.400
  bfRate := 1275
  bfCap := reg 1373 46100                  -- 63.300
  enligRate := 1150
  enligCap := reg 1373 36800               -- 50.600
  jobStart := reg 1373 171300              -- 235.200
  jobCap := reg 1373 2200                  -- 3.100
  pensCap := reg 1373 63900                -- 87.800
  ratepenCap := reg 1373 50000             -- 68.700
  unionCap := 7000
  giftCap := reg 1373 14500                -- 20.000
  buy02 := 21480
  buy36 := 16992
  buy714 := 13368
  buy1517 := 13368
  buyTaperStart := reg 1373 700000         -- 961.100
  gcStart := reg 1373 362800               -- 498.200
  ordBT := 6964                            -- borger.dk 2026: 1.741 kr. pr. kvartal
  ekstraBT := 7096                         -- borger.dk 2026: 1.774 kr. pr. kvartal
  atpOwn := 1188
  atpEmployer := 2376
  munRate7 := 2339000                      -- København 2026: 23,39 % (PSKAT)
  churchRate7 := 80000

def paramsFor (y : Nat) : Params :=
  if y = 2022 then p2022 else if y = 2023 then p2023 else if y = 2024 then p2024 else if y = 2026 then p2026
  else p2025

end DKTax
