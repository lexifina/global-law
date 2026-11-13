# caselaw-lean-2: fuzzing the glue (2026-11-12)

The harness is `lean-proofs/tools/caselaw2/fuzz/`:
- `fuzz.py`: generator, oracle, runs and checks;
- `Dump.lean`: what the Lean loaders parsed, re-serialised, plus the quote check per row;
- `RunBatch.lean`: the runner's own `CaseLaw2.Run.main` over many case dirs in one interpreter.

Open Lean-side bugs are in FUZZ_BUGS.md.

```
python -X utf8 fuzz.py all --n 5000 --seed 7 --dir <scratch>   # gen + run + check, report.json in <scratch>
python -X utf8 fuzz.py real                                      # real data/ quote-at-offset pass
```

## How a case is built

Each case starts from `fixtures/data`. It adds 1–4 synthetic decisions, each with one holding, one treatment and,
30% of the time, one history row, all certified on that decision's text.

**Decision texts** mix CRLF, lone CR, tab, LF, NBSP, curly quotes, combining marks (`é`), astral characters
(U+1F600, U+1D518, U+10348), BOM, zero-width space, soft hyphen, U+2028, VT/FF/FS/NEL, the Kelvin sign, U+0130,
Arabic and full-width digits, and CJK. Texts are written as `certify.py` does: offsets are in code points after
CRLF → LF; quotes and windows map tab and LF to a space.

**Spans** sit at offset 0, at end of text, at window edges, and inside windows clipped at the file end
(`end0 < end + 400`).

**Offset variants:**
- exact;
- UTF-8 byte offsets;
- UTF-16 code units;
- offsets counted before CRLF normalisation;
- ±1;
- empty span (`start = end`);
- swapped (`start > end`);
- a clipped window declared unclipped;
- a second, conflicting window for the same hash;
- CR also mapped to a space.

**Row mutations.** Each case then gets 0–8 byte-level mutations on any of the 14 SCHEMA files:
- CR at line end, CR CR LF, CRLF on every line;
- trailing tab, a dropped column, an extra column, an empty field;
- numbers: 0, 99991231, 40 nines, 2^64, `-5`, `+5`, ` 5`, `5 `, `1_000`, `٣`, NBSP 5, `0x1`, `5.0`, `05`, `-0`,
  empty, `１２`, `1e3`, `-`, `²`;
- a lone CR, tab or LF inside a field;
- NUL, 200,000-character fields, unicode inserted into fields;
- `#` lines, header lines, blank and whitespace-only lines;
- BOM, invalid UTF-8 (`FF`, `C3 28`, a surrogate `ED A0 80`, an overlong `C0 AF`, `F4 90 80 80`, a truncated
  sequence, a lone continuation byte), no final newline.

## Properties

The oracle reads SCHEMA literally:
- lines end at LF; trailing CRs and a line-1 BOM are not data; blank lines are skipped;
- a line must be valid UTF-8 and have exactly the schema's column count;
- integer columns are ASCII digits (with an optional `-` where a column may be negative);
- decimals are digits `.` digits.

| | Property | Lean side | Reference side |
|---|---|---|---|
| P1 | no crash | `Dump.lean` and `Run.main` finish, with no PANIC on stderr | `Data` + `Engine.admit` raise nothing |
| P2 | bad rows are rejected and counted, never mis-parsed | `problems.tsv` count = oracle bad (+ duplicate nodes); every kept row = the oracle's values, column by column | `BAD_ROWS` = oracle bad; table sizes = oracle |
| P3 | a row and its re-serialised form are equivalent | loading the dump again gives the same dump, `quotes.tsv` included | — |
| P4 | quote at offset = Python's own normalisation, counted in code points | `Cert.quoteOk` and the slice Lean compares equal Python's `norm(window)[start - start0 : end - start0]` for the same window | — |
| P5 | the runner and the reference agree | badRow verdicts and quote-stage pass/fail (`shaUnknown`, `noWindow`, `quoteMismatch` vs `noDecision`, `shaMismatch`, `offsets`, `quoteLength`, `noWindow`, `quoteMismatch`), then admission | same rows |

## Runs

| Run | Cases | Lean (dump, round trip, runner) | Reference | Result |
|---|---|---|---|---|
| A, seed 1 | 300 | yes | yes | P1–P4 clean apart from the tagged open bugs; P5 only the tagged open bugs |
| B, seed 7 | 5,000 | yes, under Linux Lean 4.35.0 in WSL (12 Nov, evening; twice: after the fuzz fixes, and again on the final code after the hunt fixes) | yes | **P1–P4: 0 failures. P5: only the 64-bit deviation (8 cases)** |
| real data | 31,841 treatments, 54,940 history rows, 260,054 holdings, 338,036 windows | compared with `out/certs.tsv` (18:39) | Python recomputation | 0 disagreements |

**Run A** (300 cases: 32,153 rows accepted, 408 rejected, 7,408 certificate rows):
- P1: 0 failures.
- P2: 0 failures, except FB-L1 (3 cases where a 10-field `decisions2` row was accepted).
- P3: 0 failures.
- P4 (Lean vs Python): 0 failures. 6,507 quotes were admitted at their offset, 533 of them with non-ASCII text, and
  every byte-offset, UTF-16-offset and pre-normalisation-offset variant with multi-byte text before the quote was
  rejected.
- Tagged differences, all open Lean bugs:
  - FB-L3 (window order): 95;
  - FB-L2 (empty quote): 89;
  - FB-L4 (holding `part`): 1.

**Run B** (5,000 cases, reference vs oracle: 534,000 rows accepted, 6,793 rejected):
- Mutations applied: 1,813 numeric, about 500–600 of each of the other 20 operations, and 1,018 cases with no
  mutation.
- Offset variants: 4,769 exact, about 700–800 of each of the 10 others.
- P1: 0 failures.
- P2: 0 failures, except 21 `decisions2` cases, all expected:
  - 8 use an id or date ≥ 2^63, which the reference rejects (`array('q')`) and Lean's `Nat` accepts. This is a
    documented deviation;
  - 13 repeat a node. The reference's `n_present` counts both rows, while the oracle keeps the last row, as both
    loaders do.
- **The Lean half of run B ran under WSL** (`wsl/verify.sh fuzz`: the 5,000 cases regenerated from seed 7 inside
  WSL, 12 parallel batches of the dumper, the round trip, the runner's `main` and the reference; about 6 minutes).
  533,780 rows accepted and 7,013 rejected by the oracle (after the FB-L5 change to it), 122,275 certificate rows
  compared, 108,171 quotes admitted at their offset (10,256 with non-ASCII text).
  - **P1** (no crash): 0. **P2** (Lean): 0. **P3** (round trip): 0. **P4** (quote at offset, Lean against the Python
    model): 0.
  - **P5:** 12 failure lines in 8 cases, all the documented deviation: a `court`, `date` or `unit` of 2^63 or more
    in `decisions2.tsv`, which the reference rejects (64-bit arrays) and Lean's `Nat` loads, so certificate rows
    naming that node differ (`P2.ref_bad.DEV-int64` 8, `P2.ref_rows.DEV-int64` 8, `P5.badRow.DEV-int64` 7,
    `P5.quote_stage.DEV-int64` 5). SCHEMA gives no upper bound; real data has no such value.
  - **Triggers generated** (`report.json` `trigger.*`): FB-L1 126 rows, FB-L2 1,581, FB-L3 1,542, FB-L4 9, FB-L5
    220; each with 0 tagged failures. FB-L6, FB-L7, FB-L8 and FB-R1 are not produced by the generator and were
    verified by direct test (FUZZ_BUGS.md).
  - **The first check of this run listed 10 classes** (8,446 `P4.lean_vs_python`, 1,542 `P4.window_order.FB-L3`,
    about 220 each of four P2 classes, 16 P5 rows). Nine were the fuzzer's own oracle and model still describing the
    pre-fix behaviour: an unparseable `confidence`/`score`/`explicit` read as 0 (FB-L5), a first-window quote model
    that allowed empty quotes (FB-L2, FB-L3), `targetLater`/`noAuthority` not counted as a passed text certificate,
    the reference's count of repeated nodes, and one mis-tagged FB-L1 row. `fuzz.py` was brought to the documented
    post-fix behaviour, keeping the tags so that a regression shows again. No new Lean or reference bug was found.

**Real data** (`fuzz.py real`):
- Every treatment, history and holding quote was recomputed in Python from `cert_text.tsv` plus
  `holdings_cert_text.tsv`. All 346,835 rows match at their stated code-point offsets, and Lean passed the quote stage
  for every row it has a verdict for: 0 disagreements.
- 2,287 history rows were written after the 18:39 runner output, so Lean has no verdict for them yet.
- 249,513 rows (72%) have non-ASCII characters (curly quotes, `§`, dashes) before or inside the quote, so a byte
  offset would differ from the code-point offset. On none of them would a byte-offset reading have found the quote.
- No real window holds an astral character, so UTF-16 offsets would have agreed with code points.
- 0 empty quotes, 0 malformed windows, 0 rows where window order matters, 0 CR bytes, 0 BOMs, 0 numeric fields
  outside the strict grammar, and every row has exactly the schema's column count. The stricter parser therefore
  loads the real data unchanged.

**Code points or bytes?** Lean's checker uses `String.length` and `toList.drop/take` (`Cert.slice`). Both count Unicode
scalar values, not `String.Pos` bytes, and so does Python's `str`. P4 and the real-data pass confirm that the two
sides agree.

## Bugs found and fixed

**Tsv.lean** (fuzz agent's file):
1. **Extra columns accepted.** `loadRows` took `≥ minFields` fields, so a tab inside a field silently shifted the
   columns. For example, an issues row with a tab in its label read the label's tail as the domain. Now it requires
   exactly the schema's count and logs `"n fields ≠ k"`.
2. **Non-SCHEMA numbers accepted.** `nat?`, `int?` and `natD` used `trimAscii` plus `String.toNat?`, so `1_000` read
   as 1000 and ` 12` as 12. `ppm?` read `.` as 0 and `1_0.5` as 10.5. Now they accept ASCII digits only (with a
   leading `-` for `int?`).
3. **BOM.** A UTF-8 BOM stayed in line 1's first field: a numeric first row was dropped, and a hash or id was
   silently altered. Now it is stripped.
4. **Extra CRs.** `chomp` dropped one CR only, so with `CR CR LF` the last field kept a `\r` (a tag `S\r` is not
   `S`). Now every trailing CR is dropped.
5. **Invalid UTF-8.** `getLine` decoded invalid UTF-8 lossily (U+FFFD) and the row was used. `foldLines` now reads
   bytes in 1 MiB chunks, splits on LF only (a lone CR stays data, as before) and validates each line; an invalid
   line is rejected and logged as `invalid UTF-8`.

**precedent_ref.py** (each change marked `# fuzz:`). With the original reference, run A gave 24 crashes, 380
row-count mismatches and 475 quote-stage disagreements.
1. **Crash on invalid UTF-8.** `open(encoding='utf-8')` raised on the first invalid byte and the whole run stopped.
   Lines are now read as bytes, and a bad line is rejected and counted.
2. **Lone CR split rows.** `open(newline='')` treated a lone CR as a line end and split the row. Now only LF ends a
   line.
3. **Silent mis-parsing of rows.** Short rows were padded with `''` and extra fields kept, so a 15-field treatment or
   a tab inside a quote was mis-read. Now `read_tsv` requires exactly the column count, checks the required integer
   columns, and counts rejected rows in `BAD_ROWS`.
4. **Data rows skipped.** `#` lines and header-looking lines were skipped, though Lean reads them. They are now data.
5. **Loose numbers.** `toint` and `tofloat` took ` 5`, `+5`, `1_000`, NBSP, other scripts' digits, `nan` and `1e5`.
   They are now strict, and `tofloat` keeps 6 decimals as Lean's ppm does.
6. **decisions2 loading.** Fixes:
   - 8 columns had been accepted; now exactly 9 are required;
   - `isdigit()` accepted `²`, and `int()` then crashed; ids are now ASCII digits;
   - negative courts had been accepted;
   - one huge node id grew the arrays without bound; ids at or above `CASELAW2_NODES` (default 2^27) are now
     rejected, as Lean rejects ids beyond its node count;
   - an id or date above 2^31 overflowed `array('i')`; the arrays are now `array('q')`.
7. **CRLF in quotes.** `norm_quote` collapsed CR LF into one space, shifting offsets. It is now one for one, as in
   SCHEMA and `Cert.norm`. The window is normalised before slicing, as Lean does.
8. **Unicode lowercasing.** `str.lower()` was used for cues, disqualifiers and evidence: the Kelvin sign became `k`
   and U+0130 became `i` plus U+0307. It now lowercases ASCII only, as Lean's `toLower`.
9. **NBSP in name evidence.** Name evidence was split with `split()`, which also splits on NBSP. It now splits on
   `' '`, as Lean does.
10. **Rows Lean calls badRow.** A treatment or history row naming an unknown kind or temporal value, or a node with no
    decisions2 row, is now `badRow`, as in Lean. It had been admitted when only the target's decision was missing,
    and an empty temporal read as `unknown`.

The fixtures' reference outputs are unchanged by all of this: `certs`, `status`, `findings`, `splits` and
`splits_asof` are byte-identical before and after.

## What is now tested, and what is not

**Tested:**
- `Tsv.lean` and the `Data.lean` row parsers: every SCHEMA file and every column class, against an independent
  SCHEMA oracle and the reference, on both sides: run A (300 cases, 32k rows) and run B (5,000 cases, 534k rows).
- Re-serialisation round trip of every table.
- `Cert.norm`, `Cert.slice`, `coveringWindow` and `quoteAt` at window edges, offset 0, end of text, clipped windows,
  and multi-byte, astral, combining, BOM, NBSP and CR text, against Python code-point slicing. The same check ran over
  every real certificate.
- The runner's `main` end to end on runs A and B (through the batched interpreter, the same `Run.main`). The
  compiled Linux runner ran the fixtures and the real data (DIFFTEST.md §8).

**Not tested:**
- Run.lean's output writers beyond `certs` and `summary`. They are exercised, but not compared value by value.
- `Run.lean`'s edge reader beyond the direct test of FB-L7 (the fuzzer always uses the fixtures' edges).
- `run_lean.sh`'s node count (FB-L8) end to end with a huge id; the awk line was tested alone.
- The reader's `clean()` (FB-R1) inside the reader; it was tested by a direct call.
- A range check on `court`, `date` and `unit` (the 64-bit deviation): neither side validates that a date is a date.

**Build and audit:** `lake build LegalProofs.CaseLaw2` (including `Run`) was green after the Tsv.lean change. The
other agent's concurrent edits briefly broke `Holdings.lean`, then `Run.lean`; both were green again before the
block. `audit/audit.py check` could not be re-run on Windows once the Lean binaries were blocked; under WSL it reports 114 theorems, 0 statement changes, 0 problems (12 Nov 21:18). Tsv.lean has no theorems or
locked statements, so the lock is unaffected.
