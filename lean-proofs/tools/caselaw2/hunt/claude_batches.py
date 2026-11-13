"""Passage classification by Claude subagents (replaces llm_run.py; no external LLM is called from here).

    python claude_batches.py make <task> <in.jsonl> <out.jsonl> [--pick p2|p4|p5|all] [--per-agent 60] [--per-file 12]
        -> hunt/work/claude/<task>/aNNN/{INSTRUCTIONS.md, b1.txt.., manifest.json}; prints the agent dirs
    python claude_batches.py merge <task> <out.jsonl>
        -> appends each agent's answers.jsonl to <out.jsonl> as {"key", "model": "claude-subagent", "ans"}

The rows already in <out.jsonl> (read earlier by Azure gpt-5.4-mini; their "model" field says so) are kept and skipped.
Sampling of the remainder is recorded in hunt/work/claude/<task>/sample.json (key -> weight multiplier) for the scorers.
"""
import json, os, random, sys
from collections import defaultdict
import hcommon as C
import tasks as T

ROOT = os.path.join(C.HWORK, "claude")

# superseded holdings the predecessor's table lacked (compiler's reading of the override lists; scope notes for the reader)
HOLDING_MORE = {
    6154858: "a habeas petitioner passes the actual-innocence gateway by showing it is more likely than not that no reasonable juror would have convicted. AEDPA 28 U.S.C. 2244(b)(2)(B) replaced this ONLY for second or successive petitions (clear and convincing evidence + due diligence); Schlup still governs first petitions and procedural default, so an error exists only where the Schlup standard is applied to a claim in a second or successive petition filed after 24 Apr 1996",
    6160238: "state-court 'in custody' (Miranda) rulings are reviewed independently, without deference, on federal habeas. AEDPA 28 U.S.C. 2254(d)(1) now requires deference to state-court merits adjudications; the two-part 'in custody' test itself is unaffected, so an error exists only where a habeas court reviews a state court's custody ruling de novo for a petition filed after 24 Apr 1996",
    6164051: "(Hasen list) reading of 28 U.S.C. 1447(c) 'defect in removal procedure'; the 1996 Act reworded 1447(c) to 'any defect other than lack of subject matter jurisdiction'. The Burford-abstention and appealability holdings are unaffected",
    6156529: "the FDCPA applies to lawyers who regularly collect consumer debts through litigation. The 1996 amendment only exempts formal pleadings from the 15 U.S.C. 1692e(11) disclosure requirement; the main holding is unaffected, so an error exists only where a court requires the 1692e(11) disclosure in a formal pleading after 30 Sep 1996",
    6178109: "'carries a firearm' in 18 U.S.C. 924(c) includes conveying it in a vehicle. The 1998 Act added 'possesses in furtherance'; the 'carry' holding is essentially unaffected",
    6192938: "the FDA has no jurisdiction to regulate tobacco products. The 2009 Tobacco Control Act gave it; the interpretive (major-questions) reasoning is unaffected, so an error exists only where a court holds after 22 Jun 2009 that the FDA cannot regulate tobacco products",
    6157455: "ADEA back pay and liquidated damages are not excludable under I.R.C. 104(a)(2) (damages must be on account of personal injuries). The 1996 amendment requires 'physical' injuries or sickness for amounts received after 20 Aug 1996",
    6156524: "a state may impose its sales tax on the full price of an interstate bus ticket sold in the state. ICC Termination Act 49 U.S.C. 14505 forbids such taxes from 1 Jan 1996; the Commerce Clause (Complete Auto) analysis is unaffected",
    6154856: "national banks may sell annuities as incidental to banking (deference to the Comptroller). Gramm-Leach-Bliley 1999 regulates this by statute; the Chevron reasoning is unaffected",
    6201157: "habeas jurisdiction under 28 U.S.C. 2241 survives for aliens' legal challenges to removal orders. The REAL ID Act (11 May 2005) eliminated district-court habeas review of removal orders (petition for review only); the separate holding that 212(c) relief remains available for pre-IIRIRA guilty pleas is unaffected",
    6164031: "federal law pre-empts state law that prevents or significantly interferes with a national bank's power to sell insurance. Gramm-Leach-Bliley 104 codified and adjusted this for insurance sales",
    6169048: "no equitable tolling of the I.R.C. 6511 refund limitation periods. The 1998 Act added 6511(h): tolling during financial disability, for periods after 22 Jul 1998; equitable tolling otherwise still unavailable",
    6156538: "a person who paid another's tax under protest to remove a lien may sue for refund under 28 U.S.C. 1346(a)(1). The 1998 Act created the I.R.C. 6325(b)(4)/7426(a)(4) remedy",
    6226396: "28 U.S.C. 2241 habeas jurisdiction reaches Guantanamo detainees. Detainee Treatment Act 2005 withdrew it (then Boumediene 2008 held the withdrawal unconstitutional)",
    6239496: "the DTA did not strip jurisdiction over pending Guantanamo habeas cases; military commissions lacked authority. Military Commissions Act 2006 overrode both (then Boumediene 2008)",
    6225353: "Chapter 13 cramdown interest uses the prime-plus formula. BAPCPA 2005 changed secured-claim valuation (11 U.S.C. 506(a)(2), 1325(a) hanging paragraph); the interest formula itself is essentially unaffected",
    6199024: "discharge-of-indebtedness income excluded under I.R.C. 108 passes through to S-corporation shareholders and increases basis. Overridden for discharges after 11 Oct 2001 (108(d)(7)(A))",
    6162278: "the Tax Court look-back period is 2 years where no return was filed before the notice of deficiency. The 1997 Act makes it 3 years for tax years ending after 5 Aug 1997",
    6156543: "18 U.S.C. 1001 does not reach false statements made to courts (judicial branch). The 1996 Act extends 1001 to the judicial branch, except statements by parties or counsel to a judge in the proceeding",
    6218078: "retrogression under Voting Rights Act section 5 is judged on the totality, including influence districts. The 2006 amendment restores 'ability to elect preferred candidates of choice'",
    6191268: "section 5 does not bar a change with a discriminatory but non-retrogressive purpose. The 2006 amendment defines 'purpose' as any discriminatory purpose",
    6176339: "all members of a federal credit union must share one common bond. The 1998 Act permits multiple common-bond credit unions",
    6199932: "a fee award as 'prevailing party' requires a judgment or court-ordered consent decree (catalyst theory rejected). The OPEN Government Act 2007 overrode this ONLY for FOIA fee awards (5 U.S.C. 552(a)(4)(E)); for every other fee statute Buckhannon is still law, so an error exists only in a FOIA fee case decided on a claim after 31 Dec 2007",
    6157819: "'use' of a firearm under 18 U.S.C. 924(c) requires active employment. The 1998 Act added 'possesses in furtherance of'; the definition of 'use' itself is still law, so an error exists only where post-13-Nov-1998 conduct charged as possession in furtherance is judged by the active-employment test",
    6164595: "sentencing departures are reviewed for abuse of discretion. The PROTECT Act (30 Apr 2003) required de novo review of departures; United States v. Booker (12 Jan 2005) excised that provision and restored abuse-of-discretion review, so an error exists only for appeals decided between those dates",
}
LOW_YIELD = {6164051, 6178109, 6157455, 6164031, 6156538, 6226396, 6225353, 6239496}

EXTRA = {
    "unpub": "",
    "unpub2": "\nSecond read. The CITED DECISION here is one printed only in the Federal Appendix (F. App'x), i.e. a "
              "non-precedential disposition of a federal court of appeals (after 2001). Be strict on treats_as_binding: "
              "it needs words showing the citing court regards itself as bound or the question as foreclosed/controlled "
              "by the unpublished decision itself (not by a published case cited alongside it, and not a mere 'see' or "
              "'as we held in' used as an example). If a published precedent is cited for the same point in the same "
              "sentence, answer false.",
    "panel2": "\nSecond read. An earlier reader marked each item a violation; the blind audit found most were not, for "
              "these reasons - check each: (a) the later decision was in fact by the court en banc / in banc / the whole "
              "court (count the judges in the JUDGES line and BENCH PASSAGES: more than three judges of an intermediate "
              "court, or 'en banc', means bench = en_banc; a court that had only three judges, or that sits as a whole, "
              "is also not a panel: answer bench = en_banc); (b) a footnote says the opinion was circulated to or approved "
              "by all active judges / the full court (justification = circulated_to_full_court); (c) the departure rests "
              "on intervening or earlier binding higher-court authority, or a statute or rule change; (d) the decision "
              "departed from is of a different court or district, or is a different case sharing the page citation; "
              "(e) only dicta or imprecise language was disapproved; (f) the court had no en banc procedure at the time "
              "(e.g. Florida district courts of appeal before 1980) - then justification = other and violation = false. "
              "violation = true only if none of these applies.",
    "super": "\nYou may use your own knowledge of the statute's scope and effective dates when judging whether the "
             "superseded holding (as opposed to an unaffected holding of the same decision) is being applied, and the "
             "SCOPE NOTE in each item. Facts about the citing opinion (what it holds, the conduct dates) must come from "
             "the text given. error = true only when you are confident on all three limbs.",
    "split": "\nYou may use your own knowledge of the Supreme Court decision to judge which side the court of appeals "
             "decision was on. Facts about the citing opinion must come from the text given.",
}


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")] if os.path.exists(path) else []


def trim(r, cut=950, n=2):
    ws = []
    for w in (r.get("windows") or [])[:n]:
        if len(w) > 2 * cut:
            mid = len(w) // 2
            w = w[mid - cut:mid + cut]
        ws.append(w)
    r = dict(r)
    r["windows"] = ws
    return r


def pick_rows(task, rows, done, mode, rnd):
    todo = [r for r in rows if T.TASKS[task]["key"](r) not in done]
    mult = {}
    if mode == "p2":
        k = min(600, len(todo))
        sel = rnd.sample(todo, k)
        for r in sel:
            mult[r["hkey"]] = len(todo) / k
    elif mode == "p4":
        by = defaultdict(list)
        ack = []
        for r in todo:
            (ack if r["stratum"] == "ack" else by[r["cited"]]).append(r)
        sel = []
        for t, v in by.items():
            k = min(12 if t in LOW_YIELD else 30, len(v))
            for r in rnd.sample(v, k):
                mult[r["hkey"]] = len(v) / k
                sel.append(r)
        k = min(60, len(ack))
        for r in rnd.sample(ack, k):
            mult[r["hkey"]] = len(ack) / k
            sel.append(r)
        for r in sel:
            if r["cited"] in HOLDING_MORE:
                r["holding"] = HOLDING_MORE[r["cited"]]
    elif mode == "p5":
        by = defaultdict(list)
        for r in todo:
            by[r["cited"]].append(r)
        sel = []
        for t, v in by.items():
            k = min(3, len(v))
            for r in rnd.sample(v, k):
                mult[r["hkey"]] = len(v) / k
                sel.append(r)
    else:
        sel = todo
        for r in sel:
            mult[T.TASKS[task]["key"](r)] = 1.0
    rnd.shuffle(sel)
    return sel, mult


def make(task, inp, out, mode, per_agent, per_file, dirname=None):
    rnd = random.Random(20261112)
    rows = load(inp)
    done = {o["key"] for o in load(out)}
    sel, mult = pick_rows(task, rows, done, mode, rnd)
    d0 = os.path.join(ROOT, dirname or task)
    os.makedirs(d0, exist_ok=True)
    json.dump(mult, open(os.path.join(d0, "sample.json"), "w", encoding="utf-8", newline="\n"))
    t = T.TASKS[task]
    props = t["schema"]["properties"]
    fields = ", ".join('"%s": %s' % (k, "true|false" if v["type"] == "boolean" else
                                      ("|".join('"%s"' % e for e in v["enum"]) if "enum" in v else
                                       ("<integer>" if v["type"] == "integer" else '"<text; %s>"' % v.get("description", ""))))
                       for k, v in props.items())
    dirs = []
    for ai in range(0, len(sel), per_agent):
        part = sel[ai:ai + per_agent]
        d = os.path.join(d0, "a%03d" % (ai // per_agent))
        os.makedirs(d, exist_ok=True)
        man = {}
        files = []
        for fi in range(0, len(part), per_file):
            fn = "b%d.txt" % (fi // per_file + 1)
            with open(os.path.join(d, fn), "w", encoding="utf-8", newline="\n") as f:
                for j, r in enumerate(part[fi:fi + per_file]):
                    rid = "R%03d" % (fi + j)
                    man[rid] = t["key"](r)
                    f.write("=" * 30 + " ITEM %s " % rid + "=" * 30 + "\n" + (r.get("_text") or t["user"](trim(r))) + "\n\n")
            files.append(fn)
        json.dump(man, open(os.path.join(d, "manifest.json"), "w", encoding="utf-8", newline="\n"))
        with open(os.path.join(d, "INSTRUCTIONS.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# Task\n\n" + t["system"] + EXTRA.get(dirname or task, "") + "\n\n# What to do\n\n"
                    "Read every batch file in this directory (%s). Each holds items headed `ITEM Rnnn`. Classify every "
                    "item independently. Do not search the web or other files. Then write ONE file `answers.jsonl` in "
                    "this directory (Write tool, LF line endings): one JSON object per line, one line per item, with "
                    "exactly these fields:\n\n    {\"id\": \"Rnnn\", %s}\n\n"
                    "There are %d items; answers.jsonl must have %d lines. Reply only with the number of lines written "
                    "and the count where the last boolean field (%s) is true.\n"
                    % (", ".join(files), fields, len(part), len(part), list(props)[[i for i, k in enumerate(props)
                                                                                      if props[k]["type"] == "boolean"][-1]]))
        dirs.append(d)
    print(len(sel), "rows in", len(dirs), "agent dirs under", d0)


def merge(task, out, dirname=None):
    d0 = os.path.join(ROOT, dirname or task)
    done = {o["key"] for o in load(out)}
    props = T.TASKS[task]["schema"]["properties"]
    n = bad = 0
    with open(out, "a", encoding="utf-8", newline="\n") as f:
        for a in sorted(os.listdir(d0)):
            p = os.path.join(d0, a, "answers.jsonl")
            if not os.path.exists(p):
                continue
            man = json.load(open(os.path.join(d0, a, "manifest.json"), encoding="utf-8"))
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                try:
                    j = json.loads(line)
                    key = man[j.pop("id")]
                    assert all(k in j for k in props)
                except Exception:
                    bad += 1
                    continue
                if key in done:
                    continue
                done.add(key)
                f.write(json.dumps({"key": key, "model": "claude-subagent", "ans": {k: j[k] for k in props}}) + "\n")
                n += 1
    missing = [a for a in sorted(os.listdir(d0)) if os.path.isdir(os.path.join(d0, a))
               and not os.path.exists(os.path.join(d0, a, "answers.jsonl"))]
    print("merged", n, "bad lines", bad, "agent dirs without answers", missing)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    if a[0] == "make":
        make(a[1], a[2], a[3], opt("--pick", "all"), int(opt("--per-agent", 60)), int(opt("--per-file", 12)),
             opt("--dir", None))
    else:
        merge(a[1], a[2], opt("--dir", None))
