import TaxCode.Individual.Form1040

/-!
# The loophole hunt's entry point to the model

`form1040F f h` is `TaxCode.Individual.form1040` with group B's facts passed through (W-2 wages and UBIA of the
business for §199A(b)(2)(B), SSTB status, §63(c)(6)(A) spouse itemizes, the §63(e) election). With no election the
return is computed both ways and the cheaper kept, exactly as `form1040` does. Nothing in the model is changed.
-/

namespace UsLoop
open TaxCode.Individual

def form1040F (f : B.Facts) (h : Household) : Line :=
  match f.electItemize with
  | some _ => form1040With f h
  | none =>
    let d := form1040With f h
    let o := form1040With { f with electItemize := some (d.itemized ≤ d.standardDeduction) } h
    if o.net < d.net then o else d

end UsLoop
