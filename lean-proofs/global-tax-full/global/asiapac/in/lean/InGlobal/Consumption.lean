import InGlobal.Pit
import TaxKernel.Global2

/-!
# India 2025: GST in two periods (5111); central excise on fuel (5121, session 9)

Sources (A, session 4): Notification 1/2017-Central Tax (Rate) as amended (to 21 September 2025) and Notification 9/2025-Central Tax (Rate)
of 17 September 2025 (G.S.R. 641(E); 10/2025 exemptions), in force 22 September 2025, giving effect to the 56th GST Council
meeting. Official e-Gazette texts read: G.S.R. 641(E) (9/2025-CT(Rate), ID 266209), G.S.R. 660(E) (10/2025-CT(Rate), ID 266210),
G.S.R. 663(E) (15/2025-CT(Rate), amending 11/2017: serial 7 (i) hotel accommodation 2.5 % CGST, serial 35 beauty 2.5 %, serial
34 betting 20 %) and G.S.R. 666(E) (16/2025-CT(Rate), amending 12/2017: S. Nos. 36C, 36D individual life and health insurance
nil), all of 17 September 2025, in force 22 September (ID 266220). Period-1 figures appear as the replaced entries ("for the
figure 6, the figure 9"). Summary first read from the Directorate of Commercial Taxes, West Bengal, "Major Recommendations of the 56th Meeting of the GST Council, Part
B" (Wayback 2026-05-17, `in/law/wb_56gstcm_partB.pdf`): apparel ≤ Rs 2,500 5 %; other non-alcoholic beverages 18 → 40 %;
aerated drinks 28 → 40 %; all other drugs and medicines 12 → 5 %; hotel units ≤ Rs 7,500 12 → 5 %; individual life and health
insurance 18 % → nil; soap, toothpaste 18 → 5 %; cigarettes stay at 28 % + cess until the cess ends (notified separately).
CGST + SGST together. The kernel's four rate slots hold: standard 18 %, reduced 5 %, reduced2 12 % (40 % from 22 September),
superReduced 28 %. Outside GST: alcohol for human consumption, petrol, diesel, electricity (Constitution arts. 279A, 366 (12A)).
Food: unbranded staples (nil) taken for the basket; registration threshold Rs 40 lakh (goods).
-/

namespace InGlobal.Consumption
open TaxKernel TaxKernel.Global

def gst1 : Vat :=
  { name := "GST (to 21 September 2025)", standard := 1800, reduced := 500, reduced2 := 1200, superReduced := 2800, threshold := 4000000,
    classOf := fun gd => match gd with
      | .food | .beer | .wine | .spirits | .rent | .water | .electricity | .petrol | .diesel | .heatingOil | .health | .books | .newspapers | .education => .exempt
      | .clothing | .gas | .transport | .restaurants => .reduced
      | .medicines | .hotels => .reduced2
      | .cigarettes | .tobaccoOther => .superReduced
      | _ => .standard }

def gst2 : Vat :=
  { name := "GST (from 22 September 2025)", standard := 1800, reduced := 500, reduced2 := 4000, superReduced := 2800, threshold := 4000000,
    classOf := fun gd => match gd with
      | .food | .beer | .wine | .spirits | .rent | .water | .electricity | .petrol | .diesel | .heatingOil | .health | .books | .newspapers | .education | .insurance => .exempt
      | .clothing | .gas | .transport | .restaurants | .medicines | .hotels => .reduced
      | .nonAlcoholic => .reduced2
      | .cigarettes | .tobaccoOther => .superReduced
      | _ => .standard }

def st1 : String := "CGST/SGST Acts 2017 s. 9; Notification 1/2017-CT(Rate) as amended (to 21 September 2025)"
def st2 : String := "CGST/SGST Acts 2017 s. 9; Notification 9/2025-CT(Rate), G.S.R. 641(E) of 17 Sep 2025 (Schedules I 2.5 %, II 9 %, III 20 %, VII 14 % CGST), 10/2025-CT(Rate) (G.S.R. 660(E)); services 11/2017 and 12/2017-CT(Rate) as amended by 15/2025 (G.S.R. 663(E)) and 16/2025-CT(Rate) (G.S.R. 666(E)) (from 22 September 2025)"

def inGst : DatedVat := { periods := [{ vat := gst1, statute := st1 }, { start := "2025-09-22", vat := gst2, statute := st2 }] }

/-! ## R3 session 9: central excise on fuel (5121), grade B
Per litre, charged on removal from the refinery and passed into the retail price: Basic Excise Duty (Central Excise Act 1944
s. 3, Fourth Schedule, effective rate by notification), Special Additional Excise Duty (Finance Act 2002 s. 147,
Notification 05/2019-Central Excise as amended), Agriculture Infrastructure and Development Cess and the additional duty
of excise (Road and Infrastructure Cess). **8 April 2025**: Notification **02/2025-Central Excise** of 7 April 2025
(G.S.R. 220(E), e-Gazette `egazette.gov.in/WriteReadData/2025/262327.pdf`, read): in Notification 05/2019-CE, Sl. No. 1
(petrol) "Rs. 13 per litre", Sl. No. 2 (diesel) "Rs. 10 per litre", in force 8 April 2025. The other components and
the earlier SAED are from the official PPAC table "Central Excise and Customs Tariff Table on Major Petroleum Products"
(Wayback 20250214145448 and 20250513131653; 20251119043735 unchanged): petrol BED 1.40 (branded 2.60), SAED 11.00 ->
13.00, AIDC 2.50, RIC 5.00; HSD BED 1.80 (branded 4.20), SAED 8.00 -> 10.00, AIDC 4.00, RIC 2.00 (rupees per litre).
Branded fuel: consumption line `"sub": "branded"`. -/

def inFuelRule (g : Good) (sub nm st : String) (paise : Int) (fr to : String) : ExciseRule :=
  { good := g, sub := sub, name := nm, perUnitNum := paise, perUnitDen := 100, validFrom := fr, validTo := to,
    statute := "Central Excise Act 1944 s. 3 (BED); Finance Act 2002 s. 147 and Notification 05/2019-CE as amended (SAED); AIDC; Road and Infrastructure Cess: " ++ st }

def inFuel (fr to : String) (pB pU dB dU : Int) (st : String) : List ExciseRule :=
  [inFuelRule .petrol "branded" "Central excise on petrol (branded)" st pB fr to,
   inFuelRule .petrol "" "Central excise on petrol" st pU fr to,
   inFuelRule .diesel "branded" "Central excise on high speed diesel (branded)" st dB fr to,
   inFuelRule .diesel "" "Central excise on high speed diesel" st dU fr to]

def inExcisePeriods : List (List ExciseRule) :=
  [inFuel "" "2025-04-08" 2110 1990 1820 1580 "to 7 April 2025: petrol 1.40 (branded 2.60) + SAED 11.00 + AIDC 2.50 + RIC 5.00; HSD 1.80 (branded 4.20) + SAED 8.00 + AIDC 4.00 + RIC 2.00 Rs per litre (PPAC table, Wayback 20250214145448)",
   inFuel "2025-04-08" "" 2310 2190 2020 1780 "from 8 April 2025: SAED 13.00 petrol, 10.00 HSD (Notification 02/2025-Central Excise, G.S.R. 220(E) of 7 April 2025); petrol 21.90 (branded 23.10), HSD 17.80 (branded 20.20) Rs per litre"]

def inExciseCharges (g : CanonGlobal) : List Charge :=
  inExcisePeriods.flatMap fun rs => exciseRuleCharges rs g (firstOnly := true)

def families : List Family := [inGst.family "GST (two periods)",
  { name := "5121 central excise on petrol and diesel", covers := [.excise], run := fun _ g _ => inExciseCharges g }]

def absent : List Absent := []

def notes : List String := ["IN 5111: GST in two periods (kernel 2.1 DatedVat); from 22 Sep 2025: G.S.R. 641(E), 660(E), 663(E), 666(E) (e-Gazette, A)", "IN 5121: central excise on petrol and diesel per litre (BED + SAED + AIDC + RIC), SAED raised 8 Apr 2025 by Notification 02/2025-CE (G.S.R. 220(E)); other components from the PPAC table (B)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food || s.good == .clothing || s.good == .nonAlcoholic) then ["GST rates by HSN within a good (packaged food 5 %/12 %, apparel above Rs 1,000/2,500, fruit drinks) taken at one rate per good"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) then ["compensation cess and excise on tobacco, state excise on alcohol and state VAT on fuel (Maharashtra, Mumbai: petrol 25 % + Rs 5.12 a litre, HSD 21 %, PPAC table 2025, base not read) not modelled; central excise on fuel computed (session 9)"] else [])

#guard (inGst.vatOn 2025 "2025-10-01").map (·.reduced2) == some 4000
#guard gst1.embedded { good := .medicines, amount := 11200 } == 1200
#guard gst2.embedded { good := .medicines, amount := 10500 } == 500
#guard gst2.embedded { good := .insurance, amount := 10000 } == 0
#guard inExcisePeriods.length == 2
#guard ((inExcisePeriods.getD 0 []).find? (fun e => e.good == .petrol && e.sub == "")).map (fun e => e.dutyOn { good := .petrol, amount := 10000, quantity := 100000 } {}) == some 1990
#guard ((inExcisePeriods.getD 1 []).find? (fun e => e.good == .diesel && e.sub == "")).map (fun e => e.dutyOn { good := .diesel, amount := 9000, quantity := 100000 } {}) == some 1780
#guard ((inExcisePeriods.getD 1 []).find? (fun e => e.good == .petrol && e.sub == "branded")).map (fun e => e.dutyOn { good := .petrol, amount := 10000, quantity := 100000 } {}) == some 2310

end InGlobal.Consumption
