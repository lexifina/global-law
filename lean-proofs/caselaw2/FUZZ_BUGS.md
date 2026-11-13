# caselaw-lean-2: bugs found by fuzzing (2026-11-12): all fixed, verification status per bug

These are bugs in files the fuzz agent does not own: `Data.lean`, `Run.lean`, `Certificate.lean`, `Events.lean`,
`run_lean.sh` and the reader. They are found by `lean-proofs/tools/caselaw2/fuzz/fuzz.py`; see FUZZ.md. Each fuzz
failure carries the tag in its property name (for example `P5.quote_stage.FB-L2`), so a fix can be checked by
running `fuzz.py check` again.

Bugs fixed in `Tsv.lean` and `precedent_ref.py` are listed in FUZZ.md.

**Verification (12 Nov, evening).** Windows Application Control blocks the Windows Lean toolchain, so the fixes were
compiled and run under Linux Lean 4.35.0 in WSL Ubuntu (`run_lean_wsl.sh`; LEAN.md "Running under WSL"). The 5,000
cases of seed 7 were regenerated inside WSL and run through the Lean dumper (two passes), the runner's `main` and
the reference: P1–P4 have 0 failures, and P5 has only the documented 64-bit deviation (8 cases; FUZZ.md run B).
No new Lean or reference bug was found. One unrelated compile error surfaced: `Run.lean` read `factor_cases.tsv` as
10 columns; the file has 11 (fixed).

## FB-L1: `Data.loadDecisions` accepts extra columns (Data.lean)

**Status:** Fixed (12 Nov): `loadDecisions` rejects any row without exactly 9 fields ("N fields ≠ 9"). **Verified** (12 Nov, Linux Lean 4.35.0 in WSL, 5,000 cases, seed 7): 126 `decisions2` rows with more than 9 fields generated, all rejected; 0 tagged failures.

`loadDecisions` rejects a row only when `f.size < 9`. A `decisions2.tsv` row with 10 or more fields is loaded, and
the extra fields are ignored. A tab inside `text_sha` or `src` therefore goes unnoticed. `Tsv.loadRows` now requires
the exact count for every other file. All 6,892,454 real rows have exactly 9 fields.

Reproducer (`decisions2.tsv`, fixtures universe):
```
7	241	19900301	0	panel	published	full	5a03a688…	src	EXTRA
```
Lean loads node 7. SCHEMA, the oracle and the reference reject the row.

Fix: `if f.size != 9 then …` (message `"{f.size} fields ≠ 9"`).

## FB-L2: an empty quote passes `quoteAt`, and a holding with an empty certificate is admitted (Certificate.lean, Run.lean)

**Status:** Fixed (12 Nov): `quoteAt` requires `start < stop` and a non-empty quote. New registered theorem `Cert.checkCert_quote_nonempty` (admitted → `quote ≠ ""` ∧ `start < stop`); `checkCert_sound` unchanged. `#guard` in Examples. **Verified** (WSL run, 5,000 cases): 1,581 certificate rows with an empty quote at an empty span over a covering window, none admitted; 0 tagged failures. `checkCert_quote_nonempty` is compiled, registered and locked (STATEMENTS.log 20:38).

`quoteAt` requires only `c.start ≤ c.stop`. With `start = stop` and quote `""`, the slice is `""`, which equals
`norm ""`. Treatments then fail at `noCue`. Holdings are admitted, because `holdingCert` checks only the hash, the
quote and the role. The reference rejects the row as `offsets`.

Reproducer (holdings.tsv, with a covering window for the hash in cert_text.tsv):
```
hX	1	ga.venue	P	yes	majority	b8319fc7…	10	10		name:x	majority	r	0.9
```
`certs.tsv` shows `holding hX ok ok`.

Fix: in `quoteAt`, require `c.start < c.stop` (or a nonempty `norm c.quote`). The statement text of `checkCert_sound`
does not change. Real data has 0 empty quotes.

## FB-L3: only the first usable window is checked (Certificate.lean `coveringWindow` / `quoteOk`)

**Status:** Fixed (12 Nov): `coveringWindow` is the first usable window *in which the quote is found* (`usable c w && quoteAt c w`), so any matching usable window admits the row, whatever the order; `windowHash` now means no usable window at all. `#guard` in Examples (a bad window listed first). **Verified** (WSL run, 5,000 cases): 1,542 rows where the first-window and any-window verdicts differ; Lean, the Python model and the reference agree on all; 0 tagged failures.

`quoteOk` checks the quote only against `windows.find? usable`. Run.lean builds that list newest first, so the last
covering row in cert_text, then holdings_cert_text, wins. When two windows of the same hash cover the span and
disagree, the verdict depends on row order. A good window can be shadowed by a bad one. The reference accepts any
covering window that matches.

Reproducer: two `cert_text.tsv` rows with the same `sha start0 end0`, where the second differs inside the quoted span
(`o` → `0`). Lean returns `quoteMismatch`; the reference returns `ok`.

Fix: either `quoteOk c := c.windows.any (fun w => usable c w && quoteAt c w)` (the soundness proof then picks that
witness), or reject a hash whose covering windows disagree. Real data: 0 rows where the order matters. With
`window_sha.tsv` present, `hashOk` already rules out a window that disagrees with the corpus.

## FB-L4: a holding's CERT `part` is never checked (Run.lean `holdingCert`)

**Status:** Fixed (12 Nov): `holdingCert` checks `Cert.partOk` (reason `partNotMajority`) before the role. **Verified** (WSL run, 5,000 cases): 9 holdings stopped only by the certificate's `part`; 0 tagged failures.

`holdingCert` checks the hash, the quote and `role`, but not the certificate's own `part` column. A holding whose
sentence is certified as `part = dissent` (or garbage such as `m\rajority`), with role `majority`, is admitted. The
reference requires `part ∈ {majority, plurality, perCuriam}`.

Reproducer: fixtures holding `h8` with column 12 set to `dissent`. Lean returns `ok`; the reference returns `part`.

Fix: add `Cert.partOk` to `holdingCert`.

## FB-L5: unparseable optional numbers become 0 silently (Data.lean)

**Status:** Fixed (12 Nov): `explicit` must be `0` or `1` (`flag01?`), `confidence` and `score` must parse (`← ppm?`); otherwise the row is a bad row. Reference matched (`read_tsv` `dec=`/`flag=`, `# fuzz FB-L5`). **Verified**, Lean and reference (WSL run, 5,000 cases): 220 rows with an unparseable `confidence`, `score` or `explicit`, all rejected and counted on both sides; 0 tagged failures. (The fuzzer's oracle still read them as 0; it now rejects them.)

These columns default to 0 instead of rejecting the row:
- `treatments.explicit` (`natD f[7] == 1`), `treatments.confidence` and `holdings.confidence` (`(ppm? …).getD 0`);
- `supersessions.score` and `supersessions.explicit`.

So `explicit = "yes"` reads as 0 and `confidence = "0,9"` reads as 0. The reference does the same, so they agree, but
the row is mis-read without being logged. Real data: 0 such values.

Fix: use `← ppm? f[15]!`, and `explicit` from `nat?` with a 0/1 check.

## FB-L6: `Temporal.ofString?` accepts `prospectiveFrom:1_000` (Events.lean)

**Status:** Fixed (12 Nov): `Temporal.ofString?` takes `prospectiveFrom:` followed by digits only. **Verified by direct test** (the generator makes no such input): `prospectiveFrom:1_000` is a bad row in Lean and in the reference; `prospectiveFrom:19990101` is admitted by both.

It uses `String.toNat?`, which accepts `_` separators. Low impact.

Fix: use `Tsv.nat?`, or an all-digits check.

## FB-L7: bad edge lines are dropped without a count (Run.lean, citation pass)

**Status:** Fixed (12 Nov): edge fields parse with `Tsv.nat?` (digits only); bad lines are counted and written as `bad_edges` in `summary.tsv`. **Verified by direct test** (the fuzzer always uses the fixtures' edges): appending `1_0\t2`, `x`, `3\t4\t5`, `+1\t2` and a non-ASCII digit line to `edges-00.tsv` gives `edges 16`, `bad_edges 5`, exit 0 (baseline `edges 11`, `bad_edges 0`). The 48,318,876 real edge lines give `bad_edges 0`.

`edges-NN.tsv` lines that do not split into two `toNat?` fields are skipped and not reported in `bad_rows`.
`toNat?` also takes `1_0`. Low impact: edges are generated, not hand-written.

## FB-L8: `run_lean.sh` node count for small universes (not verified at scale)

**Status:** Fixed (12 Nov): the awk counts only digit ids of at most 8 digits and prints with `%d`; larger ids are left to the loader, which reports them out of range. **Verified for the awk line only**: fed ids `5`, `1e+40`, 40 nines, `1000000000`, `1e3`, `12`, it prints `13`. `run_lean.sh` itself ran end to end on the fixtures, the real data and (through the same node count) every generated universe; no run with a huge id went through the script.

For `decisions2.tsv` files under 100k lines, NODES is `awk '$1+1>m{m=$1+1}'`. A huge node id prints as `1e+40`, and
`String.toNat!` then panics in `main`, so nodes becomes 0. A large id such as 10^9 makes `loadDecisions` allocate
10^9-entry arrays. Fix: count only ids made of digits that are below a cap, or count lines.

## FB-R1: reader `clean()` leaves a lone CR in windows (tools/caselaw2/reader/certify.py)

**Status:** Fixed (12 Nov): `clean()` maps `\r` to a space as well. **Verified by direct test**: `certify.clean('a\tb\nc\rd\r')` returns `'a b c d '`. The fuzzer models `clean()` (in its pre-fix form, so lone-CR windows are still generated); it does not call it.

`clean()` maps tab and LF to a space but leaves CR. A lone CR (one left after CRLF → LF) that is the last character
of a window is stripped as a line ending by both readers. The window length then no longer equals `end0 - start0`,
so the certificate fails `noWindow`. Real data has 0 CR bytes in every shipped file, so this is latent.

Fix: `clean()` should also map `\r` to a space (SCHEMA: tabs and newlines replaced by spaces).
