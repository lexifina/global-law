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

### The other flag kinds

[LegalProofs/Certificates.lean](LegalProofs/Certificates.lean) gives three more kinds of flag a certificate and a
soundness theorem, and [tools/gen_more.py](tools/gen_more.py) generates them from the facts in each flag:

| Kind | Certificate | Soundness theorem | Flags | Certified |
|---|---|---|---|---|
| Empty periods | the first real day after the old end date falls before the extension took effect | `GapFlag.certified_sound`: the rule did not bind that day | 1,760 | 1,760 |
| Pre-publication dates | stated in force before the instrument was made | `PrepubFlag.certified_sound`: it does not bind on its own start date, whenever it was published | 5,769 | 5,769 |
| Missing paragraphs | the cited section lacks the paragraph today | `ParaFlag.certified_sound`: a rule naming it cannot apply today | 630 | 630 |

In all, Lean checks **14,900 flags** and certifies **14,689**. For these three kinds every flag certifies, because the
detectors raise a flag exactly when its facts show the defect: here a certificate confirms that the facts imply the
defect under the formal rule, and gives each flag a precise statement. The reference certificates carry more weight,
because they rebuild each provision's history from the corpus instead of trusting the flag. 130 missing-paragraph flags
name paragraphs such as "1a" and are not modelled yet.

## A semantics of amending acts

[LegalProofs/Amendments.lean](LegalProofs/Amendments.lean) formalises how the corpora are built: a statute maps
provision keys to texts, an amendment is an instruction (insert, replace, repeal), and a day's consolidation applies the
day's instructions in order. Two vulnerability kinds then become theorems about that process rather than definitions:

| Theorem | Statement |
|---|---|
| `replace_missing_noop`, `repeal_missing_noop` | An instruction aimed at a provision that does not exist changes nothing: the statute after it is the statute before (the GwG § 50c case). |
| `commute` | Instructions on different provisions commute. |
| `consolidate_perm` | If no two of a day's instructions touch the same provision, every order of applying them gives the same statute (proved by induction over permutations). |
| `same_key_conflict` | Two different replacements of one existing provision give different statutes in the two orders. |

Together the last two say exactly when a day's amendments are ambiguous: the criterion behind the same-day-conflict
detector is now a theorem.

## Tools

```sh
python tools/gen_facts.py                 # reference flags, from the corpora (needs LE_HOME, below)
python tools/gen_more.py                  # empty periods, pre-publication dates, missing paragraphs
lake build                                # Lean checks every proof and every certificate (about 10 seconds)
python tools/check.py germany/bund/acts awaffv/0034.md   # one provision: writes and checks its theorems
python tools/report.py                    # tools/out/report.html: what was certified, and the leads
python tools/diff.py OLD.json NEW.json      # after the corpora move: new dead references, and flags no longer certified
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

## US federal income tax: cliffs and penalties

[LegalProofs/USTax/](LegalProofs/USTax) is an executable model of 2025 federal income tax for one household (FICA,
AGI, standard deduction, the §1 rate schedule, the EITC with the §32(i) investment-income limit, the Child Tax Credit,
and the Saver's Credit tiers of §25B), with figures from Rev. Proc. 2024-40 as amended by Pub. L. 119-21. The same
definitions are both proved about and run.

- [Schedule.lean](LegalProofs/USTax/Schedule.lean) proves `scheduleTax_step`: for every filing status and every income,
  one more dollar of taxable income never adds more than one dollar of tax. The rate schedule on its own has no cliffs.
- [Cliffs.lean](LegalProofs/USTax/Cliffs.lean) proves where the rest of the code does have them: $1 of interest costs a
  married family of five $8,045 (`investment_cliff_8045`); $1 of wages costs a saving couple $799
  (`savers_cliff_799`), and $1 more into an IRA wins back $800 (`ira_dollar_value`); marrying costs two single parents
  $3,511 a year (`marriage_penalty_3511`).
- [Search.lean](LegalProofs/USTax/Search.lean) runs the model over about 2 million households, one dollar at a time
  (`lake env lean LegalProofs/USTax/Search.lean`), and writes every point where earning more leaves a household with
  less to `tools/out/`. `python tools/gen_tax_certs.py` turns the 889 cliffs found into
  [Generated/](LegalProofs/USTax/Generated) files that Lean re-checks with `decide` on every build.
- `python tools/tax_writeup.py` writes the full write-up, [us-tax-cliffs.html](us-tax-cliffs.html), with charts and
  the limits of the model (no state tax, no benefits outside the tax code, statutory EITC formula rather than tables).

[video/tax_film.html](video/tax_film.html) is an 80-second film of this work: the bracket staircase under a 100%
ceiling it never reaches, the net-income landscape with the §32(i) cliff (a family's marble rolls off it at $11,951), the
search sweeping it, the Saver's Credit terraces and the marriage merge. `python video/render_tax.py` writes
`video/out/us-tax-film.mp4`.

## US retirement accounts: the Roth income limit, and the routes round it

[LegalProofs/USTax/Retirement/](LegalProofs/USTax/Retirement) writes the 2025 retirement-account rules as moves between
accounts, each from the provision that governs it: Roth contributions and their income limit (§408A(c)(2)–(3)),
traditional contributions and the deduction phase-out (§219, §408(o)), conversions taxed pro rata across all IRAs as one
contract (§408(d)(1)–(2), §72), rolling IRA money into a 401(k) (§408(d)(3)(A)(ii) and (H)), elective deferrals and
annual additions (§§402(g), 415(c)), and in-plan Roth rollovers (§402A(c)(4)). No planning technique is written in.

[Search.lean](LegalProofs/USTax/Retirement/Search.lean) explores every allowed sequence of moves (345,000 positions at
depth 6) for a single filer earning $250,000, whose Roth limit is $0, with $100,000 of pre-tax money in an old IRA. It
finds, unprompted, the routes practitioners call the backdoor Roth and the mega backdoor Roth, and that the backdoor only
works tax-free after the pre-tax IRA money has been moved into the 401(k).

[Theorems.lean](LegalProofs/USTax/Retirement/Theorems.lean) proves, for every sequence of moves of any length:

- `pretax_conservation`: pre-tax IRA money leaves the IRAs only by being taxed or by being rolled into the 401(k);
- `no_escape`: without that roll-in, every pre-tax dollar is taxed on its way out, whatever the order, size or number
  of contributions and conversions;
- `income_limit_void`: for every income above the limits and every starting position, a permitted sequence puts $7,000
  into the Roth with no tax;
- `roth_ceiling`: Roth gain less tax never exceeds $77,000 plus the after-tax money already held.

[Found.lean](LegalProofs/USTax/Retirement/Found.lean) re-checks the search's plan ($77,000 into Roth accounts, no tax)
and proves it optimal from `roth_ceiling`. [video/retire_film.html](video/retire_film.html) is a 72-second film of it, drawn from the real search tree
(`lake env lean LegalProofs/USTax/Retirement/Search.lean` writes it; `python video/render_retire.py` renders
`video/out/backdoor-roth-search.mp4`). The model's limits are listed at the top of
[Rules.lean](LegalProofs/USTax/Retirement/Rules.lean); the main one is that the pro-rata rule is applied at the time of
each conversion, where the Code uses the year-end value of all IRAs.

## Grantor trusts: two tests of who owns a trust

[LegalProofs/USTax/Trusts/](LegalProofs/USTax/Trusts) writes two tests separately, over a single trust power
described by what it does, who holds it, in what capacity and under what standard:
- the income-tax test of whether the grantor owns a trust (§§672–677);
- the estate-tax test of whether it is in the grantor's estate (§§2036–2038, 2042).

Neither test refers to the other. [Search.lean](LegalProofs/USTax/Trusts/Search.lean) classifies all 20,100 instruments
of one or two powers. Most fall where both tests agree, but 9,648 are "defective" (the grantor pays the income tax,
the property is out of the estate) and 333 are traps (in the estate, but not the grantor's for income tax). The search
then scores every plan on every instrument for a founder's $50 million stake over 20 years. The best it finds is the
technique practitioners use: sell the asset to a trust containing a nonfiduciary power to substitute property, then
swap it back for cash just before death so that it takes a stepped-up basis. On those assumptions the heirs receive
$259.5 million against $177.2 million for keeping the asset.

[Sale.lean](LegalProofs/USTax/Trusts/Sale.lean) proves, for every path of growth and yield:
- `defective_neutral`: the defective trust is income-tax neutral. The family is exactly as rich, after exactly the same
  income tax, as if the grantor had kept the asset.
- `estate_shrinks`: the estate is smaller by exactly what the trust holds net of the note.
- `swap_never_worse`: with the swap, the heirs never do worse than keeping the asset.
- `no_swap_cost`: without the swap, the gap is precisely the capital-gains tax on the carried-over basis.
- `trap_never_better`: selling to a trap trust is never better than keeping the asset.

[Found.lean](LegalProofs/USTax/Trusts/Found.lean) re-checks the search's results. The model's simplifications are at
the top of [Rules.lean](LegalProofs/USTax/Trusts/Rules.lean). In practice the swap power alone is not relied on, because
whether a power is held "in a nonfiduciary capacity" is a question of fact, and Rev. Rul. 2008-22 protects it only if
the trustee must confirm that the values are equal.

## The wash-sale rule's reach

[LegalProofs/USTax/WashSale/](LegalProofs/USTax/WashSale) executes trade sequences under §1091: a loss on stock or
securities is disallowed if a substantially identical acquisition falls within 30 days either side, and the loss is
added to the replacement's basis. [Theorems.lean](LegalProofs/USTax/WashSale/Theorems.lean) proves, for every sequence
of trades:
- `deferral_not_forgiveness`: once every position is closed, the gain recognised equals cash in minus cash out, so every
  disallowed loss has come back.
- `outside_scope`: assets that are not stock or securities never have a loss disallowed.
- `outside_window`: an acquisition 31 or more days from the sale never counts as a replacement.

[Search.lean](LegalProofs/USTax/WashSale/Search.lean) asks which trades recognise a loss without leaving the market,
and finds three answers ([Found.lean](LegalProofs/USTax/WashSale/Found.lean)):
- switch to a fund that tracks a different index of the same market;
- for a single stock, which has no substitute, double up 31 days before selling;
- for bitcoin, which is property and not a security (Notice 2014-21), sell and buy back the same day.

Whether two index funds are "substantially identical" has never been settled by the IRS, and is modelled as data.
Bills to extend §1091 to digital assets have been introduced since 2021; none is law as of November 2026.

## US case law: the doctrine of precedent

[LegalProofs/USCaseLaw/](LegalProofs/USCaseLaw) states the rules of precedent (which court binds which, who may
overrule whom, good law on a day) and runs them over every decision in the US case law of global-law (6,892,454
decisions); it also checks, over the whole US Code, whether the words a decision applied have changed since. Data and
pipeline: [data/caselaw/README.md](data/caselaw/README.md); tools: [tools/caselaw/](tools/caselaw).

[LegalProofs/CaseLaw2/](LegalProofs/CaseLaw2) is the second version, at the level of holdings: dated authority between
courts, treatments admitted only with a certificate that Lean checks against the decision's text, status per holding
and per line of courts, circuit splits, and 141 theorems with locked statements, tested against an independent
reference. Results, how to build and run it, the trust inventory and where everything lives:
[caselaw2/README.md](caselaw2/README.md).

    lake build LegalProofs.USCaseLaw LegalProofs.CaseLaw2

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

## Video

[video/film.html](video/film.html) is the film: a 72-second, GPU-rendered three.js piece (bloom, real data) in which
every one of the 14,900 flags is a star in a galaxy of jurisdictions, the shooting-range reference beam dies as § 12 is
deleted, the real dependency graph of `fine_dead` (exported from Lean by [tools/DepTree.lean](tools/DepTree.lean):
50 constants, 116 edges) assembles and is checked, amendments hit statutes in both orders, and a verification wave sweeps
the galaxy. `python tools/video_data.py` packages the data; `python video/render_film.py` writes
`video/out/lean-proofs-film.mp4`.

[video/anim.html](video/anim.html) is the earlier, simpler explainer (git history → facts → rule → theorem → objections → every
flag), drawn on a canvas and rendered frame by frame: `python video/render.py` writes `video/out/lean-proofs.mp4`
(needs `pip install playwright imageio-ffmpeg`; encodes on an NVIDIA GPU when one is present).

## Next steps

- Feed the 259 re-enacted, unreviewed leads into the model review and official-source checks.
- Generate paragraph-level records from the corpora, to certify the missing-paragraph flags.
- Generate regulation records (date made, power cited) from gazette preambles, to certify enabling-power flags.
