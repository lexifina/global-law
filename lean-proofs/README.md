# Formal proofs of the vulnerabilities (Lean 4)

A first attempt at stating the mistakes in [../vulnerabilities/](../vulnerabilities/) as theorems and checking them with
[Lean 4](https://lean-lang.org). This folder is self-contained: it has its own toolchain pin and build file, uses only
Lean's core library (no Mathlib), and nothing else in the repository depends on it.

```sh
cd lean-proofs
lake build                  # checks every proof
lake env lean Axioms.lean   # lists the axioms each headline theorem uses
```

## What is modelled

[LegalProofs/Basic.lean](LegalProofs/Basic.lean) has the whole model:

- A **date** is a number written `YYYYMMDD`; numeric order is calendar order for real dates.
- A **provision** is its text as a function of the date, with `none` when it does not exist: not yet enacted, repealed
  (a "(weggefallen)" or "Repealed" placeholder), or never enacted.
- Three legal rules, each written as a definition so every theorem shows which one it rests on:
  1. **A blanket rule needs what it points at.** A fine or charge defined by reference ("contrary to § 12(2)") applies
     on a date only if the provision it names is in force that day. There is no analogy against the person concerned.
  2. **No binding rule before publication.** A rule binds from the later of its stated commencement and its
     publication.
  3. **A time-limited rule binds only within its period.** An extension binds from its own commencement unless it is
     made retroactive.

Each rule comes with a general theorem, proved once for every case:

| Schema | Statement |
|---|---|
| `dead_reference` | If what a blanket rule points at is repealed from date *r*, the rule cannot apply on any date from *r*. |
| `phantom_reference` | If what it points at was never enacted, the rule can never apply. |
| `prepublication_window` | Between stated commencement and publication, a rule does not bind. |
| `empty_period` | Between the old end date and the extension's commencement, a time-limited rule does not bind. |

## The cases

| File | Headline theorem | In words |
|---|---|---|
| [AWaffV.lean](LegalProofs/Cases/AWaffV.lean) | `banned_but_unfineable` | From 1 Sep 2020, using a shut-down shooting range is banned (WaffG § 27a) and the only fine for it cannot apply. |
| [GwG50c.lean](LegalProofs/Cases/GwG50c.lean) | `transfer_never_valid` | On no date can a tax-data transfer under AO § 31b(3a) rest on a defined recipient. |
| [CLT413.lean](LegalProofs/Cases/CLT413.lean) | `no_notice_fine` | From 11 Nov 2017, no legal route is left to fine a failure to report minors' overtime. |
| [LwG154.lean](LegalProofs/Cases/LwG154.lean) | `charge_dead` | From 1 Jan 2025, the pest-control cost charge has no duty to attach to. |
| [NLFines.lean](LegalProofs/Cases/NLFines.lean) | `first_four_days` | On 1–4 Jan 2022, the decree claims a €900,000 maximum but €870,000 binds. |
| [GMOGap.lean](LegalProofs/Cases/GMOGap.lean) | `gap` | From 1 Jan to 31 Jul 2026, the GMO moratorium did not bind (an empty period, not a drafting mistake). |

Each case also proves sanity checks: the rule worked before the change, and the law and the claim agree again
afterwards. Where the vulnerability depends on a contested premise, the counterargument is proved too:

- `AWaffV.analogy_would_rescue`: if courts could read the stale reference as pointing to WaffG § 27a, the fine would
  apply again.
- `GMOGap.retroactive_closes_gap`: had the extension been made retroactive, there would be no gap.

## Checking every flag, not just five

[LegalProofs/History.lean](LegalProofs/History.lean) builds provisions from their corpus record (each dated change,
newest first) and defines a **certificate** for a reference flag: the target's record ends with it gone, and the citing
provision is still in force today. `RefFlag.certified_sound` proves, once for all flags, that a certified reference
cannot apply on any date from the target's removal.

[tools/gen_facts.py](tools/gen_facts.py) writes those records straight from the corpora for every reference flag in
[../vulnerabilities/data/](../vulnerabilities/data/) (references to repealed placeholders, references to deleted
provisions, dead fines) into [LegalProofs/Generated/](LegalProofs/Generated/). Each generated file ends with a theorem
saying which of its flags are certified, and Lean evaluates every certificate itself when it builds.

| | Flags |
|---|---|
| Reference flags checked | 6,741 |
| Certified by Lean | 6,530 |
| Citing provision rewritten after the target had gone (`RefFlag.reenacted`) | 308 |
| Of those, never reviewed by a model: the next leads | 259 |

A certificate is about the corpus record, not the law: where a corpus records a repeal wrongly, the certificate is
wrong too. That is why the strongest leads are the re-enacted ones, where the legislature rewrote the citing provision
after its target had gone and kept the reference.

## Tools

```sh
python tools/gen_facts.py                 # regenerate LegalProofs/Generated/ from the corpora (needs LE_HOME, below)
lake build                                # Lean checks every proof and every certificate (about 10 seconds)
python tools/check.py germany/bund/acts awaffv/0034.md   # one provision: writes and checks its theorems
python tools/report.py                    # tools/out/report.html: what was certified, and the leads
```

`gen_facts.py` reads the corpus index and read-only mirrors built by [../vulnerabilities/scripts/](../vulnerabilities/scripts/)
(`ingest/sync.py`, `ingest/extract.py`); set `LE_HOME` to that workspace. Output goes only to `LegalProofs/Generated/`
and `tools/out/` (git-ignored).

Example:

```
$ python tools/check.py germany/bund/acts awaffv/0034.md
germany/bund/acts awaffv/0034.md: 1 flagged reference(s), all theorems checked by Lean
  PROVED  points at awaffv/0012.md, gone since 2020-09-01: cannot apply on any date from then on, yet still in force on 2026-11-09
```

## More of the model

- [LegalProofs/Calendar.lean](LegalProofs/Calendar.lean): real calendar dates. `no_date_between_years` shows that no
  real date falls between 31 December and the next 1 January, and `retroactive_jan1_closes_gap` proves the gap closure
  that fails for raw `YYYYMMDD` numbers.
- [LegalProofs/Structure.lean](LegalProofs/Structure.lean): sections with numbered paragraphs (`missing_paragraph`) and
  regulations that must rest on a power in force on the day they are made (`void_without_power`).

## What a proof here does and does not show

Lean checks that each conclusion follows from the dated facts and the rule as defined. It does not check the facts or
the rules themselves:

- **The facts** (texts and dates) are copied by hand from the official sources cited in each file. A wrong date in a
  file gives a wrong theorem.
- **The rules** are simplified. Real courts can correct an obvious editorial slip, read a reference as "static", or
  apply a principle from outside the text. Those are exactly the objections rated in
  [../vulnerabilities/EXAMPLES.md](../vulnerabilities/EXAMPLES.md). Here they appear either as a different definition
  (which would make some proofs fail) or as an explicit counterfactual theorem.

So the guarantee is: if these facts are right and this is the rule, the vulnerability follows. A proof is no stronger
than its model.

## Next steps

- Feed the 259 re-enacted, unreviewed leads into the model review and official-source checks.
- Generate paragraph-level records from the corpora, to certify the missing-paragraph flags.
- Generate regulation records (date made, power cited) from gazette preambles, to certify enabling-power flags.
