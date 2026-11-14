# Round 10: how to run a blind audit (for track agents)

Tools in `round10/audit/` (agent `infra10`; port of `round10/audit/`, same behaviour, self-test PASS). Run everything
from the `caselaw-lean-2` folder (Git Bash: `cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Rules first, commands after. What changed against round 9: paths and names (`*10.py`, `AUDITOR_BRIEF10.md`), the
base stage for base rows is `round9/stage/v9c`, the self-test uses `t10:` / `h10:` ids, more telling words in the
run-name guard (syllab, recut, bridge, named, bare, footnote, review; state and remand were already there); the decoy
pools are round 9's (= round 8's) plus the items of the round-9 audits `round9/audit/r9*/` whose answer is known
(every reader right with extent and high confidence, or every reader wrong as round 7's rule; `decoys10.py --no-r9`
rebuilds round 9's pools byte for byte): type A 944 -> 1,053 decoys, type B 1,902 -> 2,279.

## Rules (DESIGN10 sections 0 and 3)

1. **The sample is drawn by the script, never by hand.** `make_packs10.py` draws a seeded random sample from the
   whole certified class, stratified (federal / state x decade of the acting decision), and adds decoys (items whose
   answer is known from earlier audits, >= 10% of every pack). You never pick, drop, reorder or edit items, packs or
   answers. Select the class only by row fields (`--match`), a list of row ids that a rule script wrote (`--ids`, e.g.
   your `--replace` file or the ids of one sub-rule), or Lean admission (`--lean-certs`, `--lean-classes`).
   Never select by key cases: the sample comes from the whole certified class (corpus-wide).
2. **One fresh sample per decision.** Do not redraw (other `--seed`, `--force`, other `--n`) because you dislike a
   sample. A re-audit after a cut (rule changed, rows removed) is a new run with `--exclude` of **every** earlier
   sample of that class (`--exclude round10/audit/<run>/sample.tsv`, repeat the flag for each earlier run).
3. **Blind auditors.** Each auditor is a sub-agent with `model: "opus"` whose prompt is only the line in step 2
   below. Never tell an auditor anything about the rule, the class, the agent, why items were picked, what you expect,
   or that decoys exist. Never open `sample.tsv`, `strata.tsv` or `manifest.json` in front of an auditor or paste from
   them; the auditor reads only `BRIEF.md`, its pack and `more_text10.py` output.
4. **Neutral run names.** The run path (relative to `round10/audit/`) is printed in the packs and the brief, so
   `make_packs10.py` refuses a path carrying the class name or a telling word (round 9's list -- round 8's plus
   zone, part, gvr, jersey, succes, judgm, implic, pool, phrase, lean, line -- plus syllab, recut, bridge, named,
   bare, footnote, review). Use `round10/audit/r10<letter><nn>/` with your letter:

   | agent | letter | agent | letter |
   |---|---|---|---|
   | fjc10 | f | stlink10 | t |
   | scdb10 | b | lead | a |
   | syl10 | y | infra10 | x |
   | shadow10 | k | | |

   (e.g. `r10f01`, `r10f02`, ...; never `round10/audit/syllab01/`.)
5. **Installation bar:** >= 80 items (or the whole class when smaller), point estimate about >= 90% on the class's
   measure, Wilson 95% reported. Write the run name, the command, k/n and the interval into your NOTES.md.
6. No answer key is read by any of these tools (they read certified rows, the texts at git HEAD, graph node facts
   and earlier audit folders for decoys). Do not add a key file (or anything under `benchmarks/`) as `--cert`,
   `--ids` or `--pairs` input.

## 1. Build the packs

Certify first (`round10/certify10.py`, `round10/certify_recog10.py`, `round10/certify_opwords10.py`), then:

```
# treatments rows (item type A: did the acting court itself overrule / disapprove / ... X; extent)
python -X utf8 round10/audit/make_packs10.py --class <class> --cert round10/agents/<you>/<delta folder> \
       [--match FIELD=REGEX ...] [--ids FILE] [--lean-certs round10/out/<variant>/certs.tsv] \
       --n 80 --pack-size 30 --out round10/audit/r10<letter><nn>/

# history rows (item type B: same case? did the acting court itself dispose of the target? how? whole?)
#   a certify9 folder holds both tables: add --match table=history (or table=treatments for type A)
python -X utf8 round10/audit/make_packs10.py --class <class> --cert round10/agents/<you>/<delta folder> \
       --match table=history [--match kind=reversed|vacated ...] --n 80 --pack-size 30 --out round10/audit/r10<letter><nn>/

# pair form (item type C: two history rows of the same acting decision and target, e.g. a new row and the base
#   row it would replace; both quotes are shown unlabelled in text order; the auditor gets brief B and is asked
#   what the acting court itself did to the target). PAIRS = TSV, one line per pair: <row 1 id> TAB <row 2 id>
#   (row 1 = the row whose rightness decides; row 2 = the row it is compared with). Give every folder that holds
#   either row as --cert (the base stage round9/stage/v9c for base rows).
python -X utf8 round10/audit/make_packs10.py --class <class> --pairs round10/agents/<you>/pairs.tsv \
       --cert round10/agents/<you>/<delta folder> --cert round9/stage/v9c --n 40 --pack-size 30 \
       --out round10/audit/r10<letter><nn>/
```

- `--match FIELD=REGEX` (re.search, repeatable, all must match): FIELD in `id, src, kind, scope, claim, rel,
  evidence, part, witness, explicit, table`. For pairs it applies to row 1.
- `--dry-run` prints the population per stratum and the sample size, writes nothing. Use it first.
- `--n 80 --pack-size 30` gives 3 packs of about 27 rows + 4 decoys; `--pack-size 40` gives 2 packs of about 45.
  A class smaller than `--n` is read in full.
- Output in the run folder: `pack_<k>.md` (auditor), `BRIEF.md` (auditor), `answers/` (auditor writes here),
  `sample.tsv` = THE KEY, `strata.tsv`, `manifest.json`, `store/` (texts for `more_text10.py`). About 1-3 minutes.
- Warnings printed at the end (rows without text replaced from their stratum, decoy shortfall) are also in
  `manifest.json`; report them.

## 2. Spawn the blind auditors

Two independent auditors per pack (DESIGN10 section 3; the scorer takes the strict reading: an item is right only if
every reader's answer is right). Spawn them in parallel with the Agent tool, `model: "opus"`,
`subagent_type: "general-purpose"`, `run_in_background: true`, and the prompt exactly as below (fill in the run path,
k, and for the second reader the tag `b`), nothing else:

```
Read ~/Documents/us-caselaw-lean-work/caselaw-lean-2/round10/audit/<run>/BRIEF.md and the pack file
~/Documents/us-caselaw-lean-work/caselaw-lean-2/round10/audit/<run>/pack_<k>.md (k = <k>, no reader
tag), and write your answers to
~/Documents/us-caselaw-lean-work/caselaw-lean-2/round10/audit/<run>/answers/ans_<k>.jsonl as the brief
says.
```

Second reader: `(k = <k>, reader tag b)` and `answers/ans_<k>_b.jsonl`. Do not spawn a reader for a pack that
already has an answer file of that name. If an auditor dies mid-pack, delete its partial answer file and start a
fresh auditor with the same prompt (never finish a pack by hand).

## 3. Score

```
python -X utf8 round10/audit/score_audit10.py round10/audit/<run>        # writes score.md, score.json, errors.tsv
```

- Type A: `right` = speaks of X + the court's own words + act agrees with the row's effect class (report rows: and
  the other decision named is Y); `right + extent` adds extent `whole` for whole-scope rows; `link` = speaks of X.
- Type B: `link` = same case + acted on; `right` = link + disposition agrees with the kind; `link + effect` = link +
  the same status effect (reversed ~ vacated ~ withdrawn); `right + extent` adds whole for scope `all`.
- Type C: the type-B measures for row 1, `row 2 right` (etc.) for row 2, `only row 1 right`, `only row 2 right`;
  the 0.90 flag is on row 1's `right`. `quote_order` in the key says which quote comes first in the text.
- Every measure: k/n, Wilson 95%, per federal / state, decade, kind / effect, stratum, a corpus-weighted estimate;
  decoy accuracy per pack, per reader and per decoy family (a reader with poor decoy accuracy is a warning about that
  reader, report it). `errors.tsv` lists every wrong answer and missed decoy with the reader's words.
- Report class (population), run, n, the measure that the decision uses, k/n with the Wilson interval, decoy
  accuracy. A status-changing class below about 90% is not installed.
- Report rows (`report_*`): `errors.tsv` lists every `by` failure; if the automatic match of the reader's
  `other_decision` to Y is wrong, add `round10/audit/<run>/by_match_overrides.tsv` (item, answer file or `*`, yes|no)
  and say so in NOTES.

## Other tools

- `python -X utf8 round10/audit/more_text10.py <item> [chars|all] [--target]`: the auditors' text tool (you need not
  run it).
- `python -X utf8 round10/audit/decoys10.py`: rebuilds the decoy pools (round 9's sources + the round-9 audits;
  `--no-r9` gives round 9's pools byte for byte). Do not rerun during audits.
- `python -X utf8 round10/audit/selftest10.py`: tool self-test (writes only `round10/audit/selftest10/`).
- Agent `infra10` or the lead can run an audit for you: ask the lead.
