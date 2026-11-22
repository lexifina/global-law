import TaxKernel.World

/-!
# Oman 2025: no personal income tax yet (the 2025 law applies from 2028); Social Protection Law contributions

Sources (qanoon.om transcriptions of the Official Gazette, read 2026-11-20; `om/law/`):
* Royal Decree No. 56/2025 promulgating the Individuals' Income Tax Law (`qanoon_rd2025056.txt`), art. 4 of the
  decree: "ينشر هذا المرسوم في الجريدة الرسمية، ويعمل به من الأول من يناير ٢٠٢٨ م" (dated 22 June 2025): no personal
  income tax applies in 2025. The Income Tax Law (RD 28/2009, Global law `oman/national/acts/rd/2009/28`) taxes
  companies and establishments.
* Royal Decree No. 52/2023 promulgating the Social Protection Law, amended text (`qanoon_l2023052.txt`; the decree's
  art. 6 as amended by RD 60/2025): in force 1 January 2024.
  - art. 1(15) wage: "إجمالي الراتب أو الأجر الأساسي مضافا إليه جميع البدلات والعلاوات"; art. 1(16) contribution wage:
    the wage up to each branch's ceiling;
  - art. 52: ceiling for old age, disability and death "(٣٠٠٠) ثلاثة آلاف ريال عماني شهريا"; job security
    contributions are computed "بناء على الأجر" (no ceiling);
  - art. 70(2): insured's share "(٧٫٥٪) سبعة ونصف في المائة من الأجر الشهري ... وفقا لحكم المادة (٥٢)";
  - art. 115-116(2): job security, compulsory for all Omanis working in Oman: insured's share "(٠٫٥٪)";
  - art. 139(1): savings scheme for non-Omanis, 9 % of the basic wage (financing of the scheme: start date set by
    the Fund's board; not an employee deduction); the other branches are employer-financed (art. 120 ff., 128).
* Not modelled: a Ministry of Finance subsidy of part of the insured's share (art. 71 last paragraph: by decision,
  not read). Default `"nationality": "national"` (an Omani employee); non-Omanis: 0.
-/

namespace OmTax
open TaxKernel

def nationality (c : Canon) : String := (c.str? "nationality").getD "national"

def ceiling : Int := 3000 * 12
def oldAge : Contribution := Contribution.flatCapped "oldAgeDisabilityDeath" 750 ceiling   -- art. 70(2), 52
def jobSecurity : Contribution := { name := "jobSecurity", sched := Schedule.flat 50 }      -- art. 116(2)

def out (c : Canon) : Out :=
  let nat := nationality c
  let ws := if nat = "national" then c.adults.map (·.wages) else []
  let oa := sumInts (ws.map oldAge.amount)
  let js := sumInts (ws.map jobSecurity.amount)
  let uns := if nat = "gcc" then ["GCC national: contributions follow the home state's law, not modelled"] else []
  Out.make c "OM" "OMR" 0 (employeeSocial := oa + js)
    (detail := [Out.d "oldAgeDisabilityDeath" oa, Out.d "jobSecurity" js, Out.dStr "nationality" nat,
      Out.dStr "note" "no personal income tax in 2025: RD 56/2025 applies from 1 January 2028; Social Protection Law (RD 52/2023) art. 52, 70, 116"])
    (unsupported := uns)

def country : Country :=
  { code := "OM", name := "Oman (Omani employee)", currency := "OMR", year := "2025", compute := out }

end OmTax
