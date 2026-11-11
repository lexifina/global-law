import LegalProofs.USTax.TaxCourt.Extra.Foreign
import LegalProofs.USTax.TaxCourt.Extra.Estimated
import LegalProofs.USTax.TaxCourt.Extra.Alimony
import LegalProofs.USTax.TaxCourt.Extra.Lapse
import LegalProofs.USTax.TaxCourt.Extra.Additions

/-!
# Tax Court library: further rules (tax years 2012–2024)

Pure functions over court findings, each module self-contained on `TaxCourt.Basic`:

* `Extra.Foreign` — §911 foreign earned income and housing exclusions; the §911(f) stacking rule.
* `Extra.Estimated` — §6654 required annual payment, installments and the addition, with the quarterly §6621
  underpayment rates 2012–2025 Q2.
* `Extra.Alimony` — §§71/215 for pre-2019 instruments; TCJA §11051 cut-off.
* `Extra.Lapse` — §72(e) lapse or surrender of a life insurance contract with a policy loan.
* `Extra.Additions` — whether §6651(a)(1)–(3), §6651(c)(1) and §6654 applied.
-/
