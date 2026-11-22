import TaxKernel.Global
import R5Common

/-!
# United Arab Emirates 2025: employer pension contribution for Emirati employees (2200) (pass 3r: re-cited, grade B)

Two federal laws apply in 2025 (GPSSA news of 26/08/2024 as served on 15/04/2025, Wayback, `law/ae_gpssa_news57_2025.html`):
Federal Decree-Law No. 57 of 2023 covers Emiratis employed for the first time from 31/10/2023 (input
`"gpssaScheme": "57"`, top level or household); Emiratis insured before stay under **Federal Law No. 7 of 1999** and its
amendments (the default).
* GPSSA FAQ "ما توزيع نسب الاشتراكات المستحقة عن المؤمن عليه؟" (last updated 21/08/2024, served 10/02/2025, Wayback;
  `law/ae_gpssa_faq_rates_2025.html`): insured 5 %; government-sector employer 15 %; **private-sector employer 12.5 %**;
  the government bears 2.5 % of the 15 % due from a private employer; total 20 %.
* GPSSA FAQ on the contribution-account salary (last updated 04/03/2025, served 19/04/2025, Wayback;
  `law/ae_gpssa_faq_limits_2025.html`): private sector **maximum AED 50,000, minimum AED 1,000** a month.
* FDL 57/2023 art. 4(1)(b) (English text, 1.x `law/fdl57-2023_en.txt`): the employer pays 15 % and the government bears
  2.5 points of it only for Emiratis whose contribution-account salary is under AED 20,000: for a new-law insured at
  AED 20,000 a month or more the private employer pays 15 %. (GPSSA's Arabic copy of FDL 57/2023 captured 05/08/2025 is a
  firewall refusal page: the 2025 text of art. 4 was not read; the FAQ above does not mention the AED 20,000 test.)
Insured persons are Emiratis; the household's `nationality` field (1.x convention: `national` by default, `expatriate`,
`gcc`) selects them. Private-sector employer assumed. **Grade B** (official FAQ pages dated 2024-2025).
-/

namespace AeGlobal
open TaxKernel TaxKernel.Global R5Common

def isNational (g : CanonGlobal) : Bool :=
  match g.raw.getObjValAs? String "nationality" with
  | .ok s => s == "national"
  | .error _ => match (g.household.raw.getObjValAs? String "nationality") with
    | .ok s => s == "national"
    | .error _ => true

/-- "7" (default: insured under Federal Law 7/1999) or "57" (first employed from 31/10/2023: FDL 57/2023) -/
def gpssaScheme (g : CanonGlobal) : String := (g.str? "gpssaScheme").getD ((g.household.str? "gpssaScheme").getD "7")

def gpssaMax : Int := 50000 * 12
def gpssaMin : Int := 1000 * 12

/-- private employer's rate (bp): 12.5 %; 15 % under FDL 57/2023 from AED 20,000 a month -/
def gpssaRate (scheme : String) (wages : Int) : Int :=
  if scheme == "57" && wages ≥ 240000 then 1500 else 1250

def social : Family :=
  { name := "2200 GPSSA employer contribution", covers := [.sscEmployer],
    run := fun _ g _ =>
      if !isNational g then [] else
      let sch := gpssaScheme g
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
        charge .sscEmployer "GPSSA pension contribution (employer)" a.wages (fun w => max gpssaMin (min (pos w) gpssaMax))
          (fun b => divR .down (gpssaRate sch a.wages * b) BP)
          (event := s!"adult {i + 1}") (level := .social) (bearer := .employer)
          (statute := if sch == "57" then "FDL 57/2023 art. 4(1)(b) (15 %; 12.5 % net of the 2.5 % borne by the government below AED 20,000 a month); GPSSA FAQ 2025 (AED 1,000-50,000)"
            else "Federal Law 7/1999 as amended; GPSSA FAQ 2025: private employer 12.5 % (government 2.5 %), contribution salary AED 1,000-50,000 a month") }

def socialUnsupported (g : CanonGlobal) : List String :=
  if isNational g && g.household.adults.any (·.wages > 0) then
    ["GPSSA: private-sector employer assumed (government employers 15 %); Abu Dhabi pension fund not modelled"]
    ++ (if (g.str? "gpssaScheme").isNone && (g.household.str? "gpssaScheme").isNone then
      ["GPSSA: insured taken under Federal Law 7/1999; an Emirati first employed from 31/10/2023 needs gpssaScheme \"57\" (15 % from AED 20,000 a month)"] else [])
  else []

#guard gpssaRate "57" 300000 == 1500
#guard gpssaRate "7" 300000 == 1250
#guard gpssaRate "57" 200000 == 1250

end AeGlobal
