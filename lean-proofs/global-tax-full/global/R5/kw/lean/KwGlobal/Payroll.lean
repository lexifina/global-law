import TaxKernel.Global

/-! # Kuwait 2025: per-worker fees on employers (OECD 3000), grade C (pass 3p)

Fee decisions of the Public Authority for Manpower read (PAM website, Internet Archive captures 2022-07-23 and
2024-05-24; `law/kw_pam_*`; Arabic OCR, figures checked on the page images):
* Ministerial Decision 38-A of 2016 (from 1/6/2016): no fee for the work authorisation; KWD 50 for a first work
  permit, KWD 50 for a transfer, KWD 10 for a renewal.
* Ministerial Decision 57-A of 2016: additional fees on transfers of work permits (private and oil sectors).
* Ministerial Decision 18 of 2017: KWD 250 more for each work permit above 25 % (up to 50 %) of the workforce
  authorised to employers of the second category (Administrative Decision 647/2017).
* Ministerial Decision of 2017 on employers on the distinguished lists: KWD 150 more for each new permit for workers
  recruited from abroad beyond the number allotted.
* Ministerial Decision of 31/12/2020 (Minister of Commerce): permits of GCC nationals and of illegal residents, and
  certificates.
No later fee decision was found among PAM's archived documents (2023-2025).
Every amount is charged per permit issued, transferred or renewed; none is fixed per worker per year, and the
decisions set no permit term. Under the pass-3l rule a one-off permit charge is a note, and the renewal fee cannot be
put on a yearly basis without the term; the number of permits issued or renewed in a year is not an input. Grade C.
-/

namespace KwGlobal
open TaxKernel TaxKernel.Global

def payrollNote : String := "3000 per-worker fees: PAM fee decisions read (MD 38-A/2016 from 1/6/2016: first work permit KWD 50, transfer KWD 50, renewal KWD 10; MD 57-A/2016 transfer add-ons; MD 18/2017 KWD 250 per permit above 25 % of a second-category employer's authorised workforce; MD 2017 KWD 150 per extra new permit of distinguished-list companies; MD 31/12/2020 GCC nationals and illegal residents). All are charges per permit issued, transferred or renewed, with no permit term in the decisions: no yearly per-worker amount can be booked and permit counts are not inputs (pass-3l rule: one-off permit charges are notes). Grade C (pass 3p)."

def payrollUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then [payrollNote] else []

end KwGlobal
