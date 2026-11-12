import LegalProofs.USCaseLaw.Courts
import LegalProofs.USCaseLaw.Precedent
import LegalProofs.USCaseLaw.Examples
import LegalProofs.USCaseLaw.Statute
import LegalProofs.USCaseLaw.StatuteText
import LegalProofs.USCaseLaw.AmendmentCheck
import LegalProofs.USCaseLaw.CrossRefs
import LegalProofs.USCaseLaw.Recodification
import LegalProofs.USCaseLaw.Overrides
import LegalProofs.USCaseLaw.Watch

/-!
# US case law: the doctrine of precedent in Lean

Every decision in the US case law of global-law (6,892,454 decisions), checked against the rules of precedent.

* `Courts` — systems, tiers, circuits; `binds` (who is bound by whom) and `mayOverrule` (who may overrule whom), with
  proofs that only the Supreme Court overrules the Supreme Court, that no court overrules a decision of a court that
  binds it, and that no court overrules across systems.
* `Precedent` — decisions, overruling events, `Record.valid`, `overruledOn` (good law on a day) with proofs that once
  overruled a decision stays overruled and that citation chains run backwards in time; `findings` per decision.
* `Statute` — the version of a US Code section a decision applied, and whether it has changed since.
* `StatuteText` — over the whole US Code: amended since by a law, and whether the words of the section and of the
  subsection a decision cited still read the same, with proofs that words differ only if something changed.
* `Examples` — Gideon/Betts, Lawrence/Bowers and invalid overrulings, checked by `#guard`.
* `Run` (not imported) — the runner over all decisions: `lake env lean --run LegalProofs/USCaseLaw/Run.lean`.

No `sorry`, no `native_decide`.

    lake build LegalProofs.USCaseLaw
-/
