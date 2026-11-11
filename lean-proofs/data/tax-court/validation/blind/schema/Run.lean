import LegalProofs.USTax.TaxCourt.Case

/-!
# Batch runner for encoded Tax Court cases

    lake build LegalProofs.USTax.TaxCourt.Case
    lake env lean --run LegalProofs/USTax/TaxCourt/Run.lean cases.json outcomes.json

`cases.json` is one `Case` object or an array of them; any field may be left out (defaults are filled in). Dates are
"YYYY-MM-DD"; filing statuses "single" | "mfj" | "mfs" | "hoh" | "qss"; relationships as in `Relationship`.
`outcomes.json` gets one `Outcome` per case. The console shows one line per case: citation, deficiency, and whether
every `expected` figure agreed; disagreements are listed. Exit code 0 if all agree, 1 if any check failed, 2 on bad
input.
-/

open Legal.USTax.TaxCourt Lean

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, out] =>
    let j ← match Json.parse (← IO.FS.readFile inp) with
      | .ok j => pure j
      | .error e => IO.eprintln s!"bad JSON: {e}"; return 2
    let cases ← match j with
      | .arr _ => match fromJson? (α := Array Case) j with
        | .ok cs => pure cs
        | .error e => IO.eprintln s!"bad case: {e}"; return 2
      | _ => match fromJson? (α := Case) j with
        | .ok c => pure #[c]
        | .error e => IO.eprintln s!"bad case: {e}"; return 2
    let outs := cases.map decideCase
    IO.FS.writeFile out ((toJson outs).pretty)
    let mut bad := 0
    for o in outs do
      let d := match o.deficiency with | some d => s!"deficiency {d}" | none => "no deficiency computed"
      IO.println s!"{if o.agrees then "ok  " else "DIFF"} {o.taxYear} {o.citation}: {d}"
      for e in o.errors do IO.println s!"       error: {e}"
      for c in o.checks do
        if !c.ok then IO.println s!"       {c.item}: opinion {c.expected}, computed {c.computed}"
      if !o.agrees then bad := bad + 1
    IO.println s!"{outs.size} cases, {bad} with differences"
    return (if bad == 0 then 0 else 1)
  | _ => IO.eprintln "usage: Run.lean <cases.json> <outcomes.json>"; return 2
