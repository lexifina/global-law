import BsGlobal.Pit

/-!
# BS 2025: Corporate family

The Bahamas levies no corporate income tax: the Ministry of Finance's consultation paper on the Domestic Minimum Top-up Tax (Aug 2024, opm.gov.bs) says an income tax system would have to be developed "from the ground up" and that smaller businesses stay under the Business Licence Tax. Grade B (an official statement, not a statute). Payments abroad therefore bear no withholding: cited zeros on all four kinds (`Wht.zeroOn`). The DMTT (Pillar Two, in-scope MNE groups with at least EUR 750 million revenue) stays C: the enacted Act (Nov 2024) was not reached; the Bill was read.
-/

namespace BsGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon BsGlobal

def wht : Wht :=
  { name := "Withholding on payments abroad (none levied)",
    rules := Wht.zeroOn [.dividend, .interest, .royalty, .services] "no income tax is levied in The Bahamas (Ministry of Finance, Introduction of a Domestic Minimum Top-up Tax in The Bahamas, Aug 2024: an income tax would have to be built 'from the ground up'; smaller businesses pay the Business Licence Tax): none withheld" }

def families : List Family := [wht.family]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Domestic minimum top-up tax (in-scope MNE groups only): enacted Act not read (grade C): not computed"

#guard wht.amount { kind := .dividend, amount := 1000000 } == 0
#guard wht.amount { kind := .interest, amount := 1000000 } == 0
#guard wht.amount { kind := .royalty, amount := 1000000 } == 0
#guard wht.amount { kind := .services, amount := 1000000 } == 0

end BsGlobal.Corporate
