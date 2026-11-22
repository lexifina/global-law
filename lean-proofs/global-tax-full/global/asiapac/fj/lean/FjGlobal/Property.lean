import FjGlobal.Pit

/-!
# Fiji 2025: no stamp duty on property transfers (4400, cited absence)

Source: Stamp Duties (Repeal) Act 2020 (laws.gov.fj `/api/get_act_by_id/3102`, sections via `/api/retrieve_html/<LegalId>`;
`fj/law/fj_stamp_duties_repeal_act_2020.json`): s. 1 (2) in force 1 August 2020; s. 2 "The Stamp Duties Act 1920 and any
subsidiary legislation made thereunder are repealed"; s. 3 savings for instruments executed before 1 August 2020. The
official list of acts in force (`/api/get_all_acts`, read 2026-11-21) contains no later stamp duty act. Municipal rates
(4100) are not modelled.
-/

namespace FjGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .transactions, why := "No stamp duty on property transfers in 2025: the Stamp Duties Act 1920 (Cap. 205) and its subsidiary legislation were repealed by the Stamp Duties (Repeal) Act 2020 s. 2, in force 1 August 2020 (s. 1 (2)); s. 3 keeps duty only on instruments executed before that date. laws.gov.fj (official, act 3102) lists no stamp duty act in force (act list read 2026-11-21)" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end FjGlobal.Property
