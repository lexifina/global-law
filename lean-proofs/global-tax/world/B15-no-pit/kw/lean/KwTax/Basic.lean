import TaxKernel.World

/-!
# Kuwait 2025: no personal income tax; employee social security for Kuwaiti nationals

Source: PIFSS "الدليل التشريعي، الكتاب الأول: قوانين التأمينات الاجتماعية والقوانين المعدلة له" (legislative guide,
book 1, dated 16-9-2021; pifss.gov.kw/LegislativeGuide/; `kw/law/pifss_book1_2021.pdf`, NFKC text
`pifss_book1_2021_nfkc.txt`). The guide prints each law as amended with its amending acts and their dates; it is
the PIFSS's own consolidation (official secondary for the law text). Amendments after September 2021 and
ministerial decisions after that date could not be checked (access tier B).

* Social Insurance Law (Amiri Decree-Law No. 61 of 1976), art. 2 (as amended by Law No. 9 of 2011, in force
  2011-05-01): "يكون الحد الأقصى للمرتب المنصوص عليه في هذا القانون (1500) دينار شهريا"; scope art. 2 of the
  issuing decree (book p. 429): "الكويتيين الذين يعملون لدى صاحب عمل ، ويكون التأمين عليهم إلزاميا";
  art. 11 (basic insurance): "االشتراكات الشهرية التي تقتطع من مرتبات المؤمن عليهم وذلك بواقع (5%)".
* Law No. 25 of 2001, art. 8 (fund for the increase of pensions) and its table: the insured's monthly share is
  2.5 % from the tenth year "العاشرة وما بعدها" (in force 2001-07-01, so 2025 is beyond the tenth year).
* Law No. 110 of 2014 (financial reward at the end of contribution), art. 3: salary "بحد أقصى (1500) دينار";
  art. 4(1): "االشتراكات الشهرية التي تقتطع من مرتبات المؤمن عليهم ... بواقع (2.5%)".
* Decree-Law No. 128 of 1992 (supplementary insurance), art. 1(3): the salary is the pay "بعد استبعاد المرتب
  المنصوص عليه في التأمين األساسي", i.e. "ما زيد على الحد األقصى للمرتب"; its maximum "(1250د.ك) شهريا" (raised from
  1,000 by decision 1/2005 from 2005-07-01; decision 6/2019 raised it to 1,500 only for optional contributors);
  art. 4(a): "االشتراكات الدورية التي تقتطع من مرتبات المؤمن عليهم بواقع (5%) شهريا".
* Decree-Law No. 101 of 2013 (unemployment insurance), art. 3: "االشتراكات الشهرية التي تقتطع من مرتبات المؤمن
  عليهم في التأمين األساسي والتأمين التكميلي بواقع (0.5%)".

Assumptions: the increase-fund contribution (Law 25/2001) is taken on the basic-insurance salary (capped 1,500);
the contract wage is the insurance salary; a private-sector Kuwaiti employee (no minimum wage floor applied).
No personal income tax: Kuwait's income tax decree (No. 3 of 1955, as amended by Law 2/2008) taxes corporate
bodies; it was not read (FINDINGS F1). Non-Kuwaitis are outside the Social Insurance Law: 0.
-/

namespace KwTax
open TaxKernel

def pct (rate base : Int) : Int := divR .down (rate * pos base) 10000
def nationality (c : Canon) : String := (c.str? "nationality").getD "national"

def basicCeiling : Int := 1500 * 12      -- SIL art. 2 (Law 9/2011)
def suppMax : Int := 1250 * 12           -- DL 128/1992 art. 1(3) (decision 1/2005)

def basic (w : Int) : Int := pct 500 (min w basicCeiling)                       -- SIL art. 11: 5 %
def increaseFund (w : Int) : Int := pct 250 (min w basicCeiling)                -- Law 25/2001 art. 8: 2.5 %
def reward (w : Int) : Int := pct 250 (min w basicCeiling)                      -- Law 110/2014 art. 3-4: 2.5 %
def suppSalary (w : Int) : Int := min (pos (w - basicCeiling)) suppMax
def supplementary (w : Int) : Int := pct 500 (suppSalary w)                      -- DL 128/1992 art. 4(a): 5 %
def unemployment (w : Int) : Int := pct 50 (min w basicCeiling + suppSalary w)   -- DL 101/2013 art. 3: 0.5 %

def person (w : Int) : Int := basic w + increaseFund w + reward w + supplementary w + unemployment w

def out (c : Canon) : Out :=
  let nat := nationality c
  let ws := if nat = "national" then c.adults.map (·.wages) else []
  let b := sumInts (ws.map basic); let i := sumInts (ws.map increaseFund); let r := sumInts (ws.map reward)
  let s := sumInts (ws.map supplementary); let u := sumInts (ws.map unemployment)
  let uns :=
    (if nat = "national" ∧ c.adults.any (fun a => a.wages > 0) then
      ["ceilings and rates from the PIFSS consolidation of September 2021: later ministerial decisions not checked"] else [])
    ++ (if nat = "gcc" then ["GCC national: contributions follow the home state's law, not modelled"] else [])
  Out.make c "KW" "KWD" 0 (employeeSocial := b + i + r + s + u)
    (detail := [Out.d "basicInsurance" b, Out.d "pensionIncreaseFund" i, Out.d "endOfContributionReward" r,
      Out.d "supplementaryInsurance" s, Out.d "unemploymentInsurance" u, Out.dStr "nationality" nat,
      Out.dStr "note" "no personal income tax on individuals; Kuwaiti employees: SIL 61/1976 art. 11, Law 25/2001, Law 110/2014, DL 128/1992, DL 101/2013"])
    (unsupported := uns)

def country : Country :=
  { code := "KW", name := "Kuwait (Kuwaiti private-sector employee)", currency := "KWD", year := "2025", compute := out }

end KwTax
