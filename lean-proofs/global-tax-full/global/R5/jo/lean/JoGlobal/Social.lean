import TaxKernel.Global
import TaxKernel.Global2
import R5Common

/-!
# Jordan 2025: employer social security contributions (2200) (pass 3r: re-cited to the SSC 2025 edition)

Social Security Law No. 1 of 2014 as amended to Law 11 of 2023, SSC consolidated edition (Jan 2024,
`law/ssl2014.pdf`; art. 59 page read as an image, the others from the OCR, where the rates are spelt in words):
* art. 59(أ)(1) old age, disability and death: "تؤديها المنشأة بنسبة (11٪) من أجور المؤمن عليهم" (p. 54);
* art. 26(أ) work injuries: "(اثنين بالمائة)";
* art. 43(أ)(1) maternity: "ثلاثة أرباع الواحد بالمائة";
* art. 48(أ) unemployment: "(نصف بالمائة)".
Total 14.25 %. Wage ceiling (art. 20(ب), indexed): 3,668 JOD a month for 2025 (SSC statement on the 2026 ceiling,
`law/jo_ssc_ceiling2026.html`: "كان العام الماضي (3668) ديناراً"), as in the 1.x model.

**2025 (pass 3r).** The SSC's English edition `law-26.1.2025-compressed.pdf` (PDF of 28/01/2025, uploaded 2025/02,
Wayback 27/04/2025; `law/jo_ssl_en_2025.pdf`, `.txt`) is "According to the latest amendments until April 16, 2023" and
gives the same rates: firm 2 % work injury, 0.75 % maternity, 0.5 % unemployment, 11 % old age (art. 59(a)(1)); art.
59(c)(1): private firms may reduce the old-age contribution by a Bylaw, at most 50 %. That Bylaw is **Regulation 45 of
2024** (SSC copy, PDF of 03/12/2024, Wayback 19/01/2025; `law/jo_reg45_2024.pdf`, `.txt`), in force 1/8/2024: on the
firm's request the old-age contribution the firm pays is reduced by **40 % in a small firm (25 workers or fewer)** and
**20 % in a medium firm (26-50)** (art. 3) for an insured who is Jordanian, had no earlier mandatory coverage, has not
completed 30 and is not the owner (art. 4(b)). Applied when the adult's `"sscReduction": true` (the firm applied and the
art. 4(b) conditions hold), `age` < 30 and `"employerEmployees"` ≤ 50; otherwise listed. **Grade A.**
Not applied: art. 20(ج) older ceilings of members insured before 2009.
-/

namespace JoGlobal
open TaxKernel TaxKernel.Global R5Common

def joCap : Int := 12 * 3668

/-- Regulation 45/2024 art. 3: reduction of the 11 % (bp of the 11 %): 40 % small, 20 % medium, else none -/
def joReductionBp (employees : Int) : Int :=
  if employees < 0 then 0 else if employees ≤ 25 then 4000 else if employees ≤ 50 then 2000 else 0

def joAsked (g : CanonGlobal) (i : Nat) : Bool :=
  match (adultJson g i).getObjValAs? Bool "sscReduction" with
  | .ok b => b
  | .error _ => false

/-- employer rate (bp) for adult `i`: 14.25 %, or 3.25 % + 11 % less the Regulation 45/2024 reduction -/
def joRate (g : CanonGlobal) (a : Adult) (i : Nat) : Int :=
  if joAsked g i && a.age < 30 then 325 + divR .down (1100 * (10000 - joReductionBp (employerOf g i).employees)) 10000
  else 1425

def social : Family :=
  { name := "2200 social security (employer)", covers := [.sscEmployer],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.household.adults.zipIdx.filter fun (a, _) => a.wages > 0).map fun (a, i) =>
        charge .sscEmployer "اشتراكات الضمان الاجتماعي (المنشأة)" a.wages (fun w => min (pos w) joCap)
          (fun b => divR .down (joRate g a i * b) BP)
          (event := s!"adult {i + 1}") (level := .social) (bearer := .employer)
          (statute := if joRate g a i == 1425 then
              "SSL 1/2014 (to Law 11/2023; SSC edition of 26/1/2025) art. 59(a)(1) 11 %, 26(a) 2 %, 43(a)(1) 0.75 %, 48(a) 0.5 %; ceiling 3,668 a month (2025)"
            else "SSL 1/2014 art. 59(a)(1), 59(c); Regulation 45/2024 art. 3-4 (old-age 11 % reduced 40 % small / 20 % medium firm, insured under 30); 26(a), 43(a)(1), 48(a); ceiling 3,668 a month") }

def socialUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company || !(g.household.adults.any (·.wages > 0)) then [] else
  ["employer social security: art. 20(c) ceilings of members insured before 2009 not applied"]
  ++ (if (g.household.adults.zipIdx.any fun (a, i) => a.wages > 0 && a.age < 30 && !joAsked g i) then
    ["Regulation 45/2024: a small/medium private firm may reduce the 11 % old-age share by 40 %/20 % for a first-insured Jordanian under 30 on request: not applied without the adult's sscReduction and employerEmployees"] else [])
  ++ (if (g.household.adults.zipIdx.any fun (a, i) => a.wages > 0 && a.age < 30 && joAsked g i && (employerOf g i).employees < 0) then
    ["Regulation 45/2024: sscReduction given without employerEmployees: no reduction applied"] else [])

#guard joCap == 44016
#guard divR .down (1425 * joCap) BP == 6272
#guard joReductionBp 10 == 4000
#guard joReductionBp 40 == 2000
#guard joReductionBp 51 == 0
#guard 325 + divR .down (1100 * (10000 - 4000)) 10000 == 985

end JoGlobal
