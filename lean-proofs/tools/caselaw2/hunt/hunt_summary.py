"""Collect every count, recall and audit figure of the hunt into caselaw-lean-2/hunt/summary.json.

    python hunt_summary.py     -> hunt/summary.json, data/p5_horty.tsv, data/p3_known_callouts.tsv, data/p2_pub_labels.tsv

All model reads are labelled by reader: "azure gpt-5.4-mini" (the first pass, kept from before the hand-over) or
"claude-subagent" (everything read after it, and every audit).
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict
import hcommon as C

csv.field_size_limit(10 ** 9)
H = C.HUNT


def L(name):
    p = os.path.join(C.HWORK, name)
    return [json.loads(l) for l in open(p, encoding="utf-8")] if os.path.exists(p) else []


def tsv(path):
    return list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))


def aud(p):
    f = os.path.join(H, "audit", p, "audit.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}


def audrows(p, group=None, verdict="confirmed"):
    f = os.path.join(H, "audit", p, "audit.tsv")
    if not os.path.exists(f):
        return []
    return [r for r in tsv(f) if (group is None or r["group"] in group) and (verdict is None or r["verdict"] == verdict)]


def inst(r):
    return dict(citing="%s, %s (%s, %s)" % (r["citing_name"], r["citing_cite"], r["citing_court"], r["citing_date"][:4]),
                cited="%s, %s" % (r["cited_name"], r["cited_cite"]), why=r["explanation"], citing_node=int(r["citing"]),
                cited_node=int(r["cited"]))


def W(k, n):
    p, lo, hi = C.wilson(k, n)
    return dict(k=k, n=n, p=round(p, 3), ci95=[round(lo, 3), round(hi, 3)])


def findings_counts():
    c = Counter()
    for r in C.read_tsv(os.path.join(C.OUT, "findings.tsv")):
        c[r[0]] += 1
    return c


def p1(F):
    ins = {r["hkey"]: r for r in L("p1_llm_in.jsonl")}
    strata = Counter()
    for l in open(os.path.join(C.HWORK, "p1_passages.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["hits"] <= 0:
            strata["not_located"] += 1
            continue
        ack = bool(r["ack_word"] or r["ack_actor"] or r["actor_any"])
        strata[("O-" if r["kind"] == "citesOverruled" else "V-") + ("ack" if ack else "silent")] += 1
    wsum, zsum, n1 = Counter(), Counter(), Counter()
    for o in L("p1_llm_out.jsonl"):
        a = o["ans"]
        if "error" in a or o["key"] not in ins:
            continue
        r = ins[o["key"]]
        n1[r["stratum"]] += 1
        wsum[r["stratum"]] += r["weight"]
        zsum[r["stratum"]] += r["weight"] * bool(a["zombie"])
    rate1 = {s: zsum[s] / wsum[s] for s in wsum}
    grp = json.load(open(os.path.join(C.HWORK, "claude", "zombie2", "groups.json"), encoding="utf-8"))
    sec = Counter()
    for o in L("p1_second_out.jsonl"):
        sec[(grp[o["key"]], bool(o["ans"].get("zombie")))] += 1
    r2 = {"O-silent": sec[("random_O", True)] / max(1, sec[("random_O", True)] + sec[("random_O", False)]),
          "V-silent": sec[("random_V", True)] / max(1, sec[("random_V", True)] + sec[("random_V", False)])}
    a1, a2 = aud("p1"), aud("p1b")
    prec2 = a2["flagged"]["precision"]
    est = {s: strata[s] * rate1[s] * r2[s] * prec2 for s in ("O-silent", "V-silent")}
    est1 = {"O-silent": strata["O-silent"] * rate1["O-silent"] * a1["flagged"]["precision"],
            "V-silent": strata["V-silent"] * rate1["V-silent"] * a1["flagged_vacated"]["precision"]}
    known = tsv(os.path.join(H, "data", "known_overrulings.tsv"))
    kneg = sum(r["our_status"].startswith("neg:") for r in known)
    kpart = sum(r["our_status"].startswith("partialScope") for r in known)
    kres = sum(r["target_node"] != "-" for r in known)
    kov = sum(r["overruler_node"] not in ("-", "") for r in known)
    call = tsv(os.path.join(H, "data", "p1_known_callouts.tsv"))
    kz = [r for r in call if r["known_zombie"] == "1"]
    kc = L("p1_known_zombie_out.jsonl")
    top = [inst(r) for r in audrows("p1", ("top",))] + [inst(r) for r in audrows("p1b", ("flagged",))] \
        + [inst(r) for r in audrows("p1", ("flagged", "flagged_vacated"))]
    return dict(
        predicate="citing decision relies on X for proposition p; statusOf X (for p) at the citing date is negative "
                  "(overruled, abrogated, disapproved, receded from, reversed, vacated); no acknowledgement; not the same case",
        lean="Hunt.zombie",
        corpus=dict(findings_citesOverruled=F["citesOverruled"], findings_citesVacated=F["citesVacated"],
                    candidate_rows=sum(strata.values()), located_by_stratum=dict(strata),
                    first_read=dict(reader="azure gpt-5.4-mini", rows=sum(n1.values()), by_stratum=dict(n1),
                                    weighted_zombie_rate={k: round(v, 3) for k, v in rate1.items()}),
                    second_read=dict(reader="claude-subagent", rows=sum(sec.values()),
                                     counts={"%s|%s" % k: v for k, v in sorted(sec.items())},
                                     confirm_rate={k: round(v, 3) for k, v in r2.items()}),
                    estimated_true_instances=dict(two_stage={k: round(v) for k, v in est.items()},
                                                  two_stage_total=round(sum(est.values())),
                                                  first_read_times_audit={k: round(v) for k, v in est1.items()},
                                                  note="two_stage counts only rows both readers accept (the second reader "
                                                       "rejected 6 of the 11 instances the full-text audit confirmed), so it "
                                                       "is a lower estimate; first_read_times_audit is the upper one")),
        known=dict(literature_overrulings=len(known), target_resolved=kres, overruler_in_corpus=kov,
                   status_negative=kneg, status_partial=kpart, recall_status=W(kneg, len(known)),
                   recall_status_incl_partial=W(kneg + kpart, len(known)),
                   later_citers_flagged="every later citer of the %d negative targets is a citesOverruled finding" % kneg,
                   callout_rows=len(call), callout_known_zombies=len(kz),
                   callout_known_zombies_in_findings=sum(r["in_findings"] == "1" for r in kz),
                   recall_callouts=W(sum(r["in_findings"] == "1" for r in kz), len(kz)),
                   classifier_on_known=dict(reader="azure gpt-5.4-mini", n=len(kc),
                                            zombie=sum(bool(o["ans"].get("zombie")) for o in kc))),
        audit=dict(reader="claude-subagent (full text, blind, decoys mixed in)",
                   first_read_overruled=a1.get("flagged"), first_read_vacated=a1.get("flagged_vacated"),
                   two_stage=a2.get("flagged"), decoys=[a1.get("decoy"), a2.get("decoy")], top_candidates=a1.get("top")),
        precision=a2["flagged"]["precision"], precision_ci95=a2["flagged"]["ci95"], precision_basis="two-stage (both readers)",
        top=top[:14])


def pub_labels():
    """decisions2.pub against the citation: a decision whose only reporter is the Federal Appendix is unpublished; one
    printed in F.2d/F.3d/U.S./a regional or official state reporter is published whatever decisions2 says."""
    con = C.db()
    rx_app = re.compile(r"F\. ?App")
    c = Counter()
    for pub, cite in con.execute("select d.pub, n.cite from dec d join nodes n on n.id=d.node where d.pub in "
                                 "('unpublished','table','summaryOrder','memorandum')"):
        cites = [x for x in (cite or "").split("|") if x]
        if not cites:
            c[(pub, "no citation")] += 1
        elif all(rx_app.search(x) for x in cites):
            c[(pub, "Federal Appendix only")] += 1
        elif any(re.search(r"\bWL\b|LEXIS", x) for x in cites) and len(cites) == 1:
            c[(pub, "database cite only")] += 1
        else:
            c[(pub, "printed reporter")] += 1
    rows = [[k[0], k[1], v] for k, v in sorted(c.items(), key=lambda kv: -kv[1])]
    C.write_tsv(os.path.join(H, "data", "p2_pub_labels.tsv"), rows, ["decisions2_pub", "citation_class", "decisions"])
    return c


def p2(F):
    ins = {r["hkey"]: r for r in L("p2_in.jsonl")}
    outs = L("p2_out.jsonl")
    rd = Counter(o.get("model", "").startswith("gpt") and "azure gpt-5.4-mini" or "claude-subagent" for o in outs)
    viol = sum(bool(o["ans"].get("violation")) for o in outs if "error" not in o["ans"])
    o2 = L("p2b_out.jsonl")
    c = pub_labels()
    tot = sum(c.values())
    printed = sum(v for k, v in c.items() if k[1] == "printed reporter")
    a1, a2 = aud("p2"), aud("p2b")
    ar = audrows("p2", None, None)
    notunpub = sum(1 for r in ar if r["group"] != "decoy" and not json.loads(r["checks"]).get("cited_is_unpublished"))
    nfl = sum(1 for r in ar if r["group"] != "decoy")
    return dict(
        predicate="citing court treats as binding a decision that is unpublished / non-precedential under the issuing "
                  "court's rule at its date (force below bindingAbsentConflict), not in the same case",
        lean="Hunt.unpublishedAsBinding",
        corpus=dict(findings_citesNotCitable=F["citesNotCitable"],
                    same_system_later_citations_of_nonpublished=sum(1 for _ in open(os.path.join(C.HWORK, "p2_edges.tsv"), encoding="utf-8")) - 1,
                    same_court_nonbinding_passages=sum(1 for _ in open(os.path.join(C.HWORK, "p2_passages.jsonl"), encoding="utf-8")),
                    binding_cue_passages=len(ins), first_read=dict(rows=len(outs), readers=dict(rd), violations=viol),
                    federal_appendix_binding_cue=len(o2),
                    second_read=dict(reader="claude-subagent", rows=len(o2),
                                     violations=sum(bool(o["ans"].get("violation")) for o in o2),
                                     same_case_binding=sum(bool(o["ans"].get("treats_as_binding") and o["ans"].get("same_case")) for o in o2)),
                    confirmed_instances=a2.get("flagged", {}).get("confirmed", 0)),
        known=dict(note="Anastasoff v. United States, 223 F.3d 898 (8th Cir. 2000) (unpublished Christie treated as binding) "
                        "is the textbook instance; Christie is not in the corpus, so it cannot be recreated. The pattern was "
                        "validated instead on the 5th Cir. pre-1996 window (49 unpublished decisions the rule makes binding: "
                        "none is reported, as it should be) and on same-case uses (law of the case: excluded).",
                   recall=None),
        data_error=dict(what="decisions2.pub marks reporter-published opinions as unpublished when their text mentions an "
                             "unpublished order (an attached opinion, a Rule 23 order under review)",
                        nonpublished_labels=tot, printed_reporter=printed, share=round(printed / max(1, tot), 3),
                        audit_cited_not_unpublished=W(notunpub, nfl),
                        affects="citesNotCitable (%d findings) and every unpublished-opinion cap" % F["citesNotCitable"]),
        audit=dict(reader="claude-subagent", first_pattern=a1.get("flagged"), first_top=a1.get("top"),
                   refined=a2.get("flagged"), decoys=[a1.get("decoy"), a2.get("decoy")]),
        precision=a1.get("flagged", {}).get("precision"), precision_ci95=a1.get("flagged", {}).get("ci95"),
        precision_basis="first pattern (decisions2.pub); the refined pattern has 2 instances, 1 confirmed",
        top=[inst(r) for r in audrows("p2b", ("flagged",))])


def p3_known(findset):
    """Later courts' own call-outs: a note that says a panel could not overrule (prior-panel rule) about a named pair."""
    rx = re.compile(r"(?:panel|division)[^.]{0,160}(?:cannot|could not|can not|may not|lacked|lacks|without)[^.]{0,80}"
                    r"overrul|one panel[^.]{0,80}overrul|prior[- ]panel rule|overrul[^.]{0,120}(?:without|absent)[^.]{0,40}en banc|"
                    r"only (?:the )?(?:court )?(?:sitting )?en banc[^.]{0,60}overrul", re.I)
    rows = []
    with open(os.path.join(C.GOLD, "reports_typed.tsv"), encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        h = next(r)
        for p in r:
            d = dict(zip(h, p))
            if d["kind"] in ("overruled", "disapproved", "recededFrom", "abrogated") and rx.search(d["snippet"]):
                by, t = int(d["by_node"]), int(d["target_node"])
                if by > 0 and t > 0:
                    rows.append([d["note_node"], by, t, d["kind"], int((by, t) in findset), d["snippet"][:300]])
    seen, out = set(), []
    for x in rows:
        if (x[1], x[2]) not in seen:
            seen.add((x[1], x[2]))
            out.append(x)
    C.write_tsv(os.path.join(H, "data", "p3_known_callouts.tsv"), out,
                ["note_node", "by_node", "target_node", "kind", "in_findings", "snippet"])
    return out


def p3(F):
    findset = set()
    for r in C.read_tsv(os.path.join(C.OUT, "findings.tsv")):
        if r[0] == "panelDepartsWithoutEnBanc":
            findset.add((int(r[1]), int(r[2])))
    rows = tsv(os.path.join(H, "data", "p3_panel.tsv"))
    o2 = L("p3b_out.jsonl")
    ins2 = {r["hkey"]: r for r in L("p3b_in.jsonl")}
    v2 = [o for o in o2 if o["ans"].get("violation")]
    known = p3_known(findset)
    a1, a2 = aud("p3"), aud("p3b")
    est_lo = len(v2) * a2["flagged"]["precision"]
    est_hi = est_lo + (len(o2) - len(v2)) * a2["decoy"]["precision"]
    return dict(
        predicate="status-changing treatment by b of x, same court (and unit), strong horizontal rule, bench of b is a "
                  "panel, no recognised exception (intervening higher authority, statute, full-court circulation, earlier "
                  "conflicting precedent), the court had an en banc procedure",
        lean="Hunt.panelOverrulesPanel",
        corpus=dict(findings_panelDepartsWithoutEnBanc=F["panelDepartsWithoutEnBanc"], pairs=len(findset),
                    first_read=dict(reader="azure gpt-5.4-mini", rows=len(rows),
                                    violations=sum(r["violation"] == "1" for r in rows),
                                    after_whole_court_filter=sum(r["violation_final"] == "1" for r in rows)),
                    second_read=dict(reader="claude-subagent", rows=len(o2), violations=len(v2),
                                     by_court=Counter(ins2[o["key"]]["court_name"] for o in v2).most_common(12),
                                     rejected_because=Counter("%s/%s" % (o["ans"]["bench"], o["ans"]["justification"])
                                                              for o in o2 if not o["ans"].get("violation")).most_common(8)),
                    estimated_true_instances=dict(low=round(est_lo), high=round(est_hi),
                                                  note="low = second-read violations x audit precision; high adds the "
                                                       "second-read rejections x the decoy confirmation rate (2 of 6)")),
        known=dict(note="no usable set of later-court call-outs exists for this pattern: the %d notes in reports_typed.tsv "
                        "that mention the prior-panel rule next to an overruling (data/p3_known_callouts.tsv) recite the rule "
                        "and do not accuse a panel. Validation is by mechanism instead: the known lawful routes (D.C. Cir. "
                        "Irons footnote, 2d Cir. and 1st Cir. circulation, Fed. Cir. en banc footnote, 9th Cir. Miller v. "
                        "Gammie, 7th Cir. Rule 40(e)) are all rejected by the second read, and the second read is scored "
                        "against the instances the full-text audit confirmed" % len(known),
                   rule_reciting_notes=len(known), in_findings=sum(x[4] for x in known),
                   second_read_recall_on_audit_confirmed=W(0, 2), recall=round(0 / max(1, 2), 3)),
        audit=dict(reader="claude-subagent", first_read=a1.get("flagged"), first_top=a1.get("top"),
                   two_stage=a2.get("flagged"), decoys=[a1.get("decoy"), a2.get("decoy")]),
        precision=a2["flagged"]["precision"], precision_ci95=a2["flagged"]["ci95"], precision_basis="two-stage (both readers)",
        top=[inst(r) for r in audrows("p3b", ("flagged",))] + [inst(r) for r in audrows("p3", ("flagged",))])


def p4(F):
    rows = tsv(os.path.join(H, "data", "p4_superseded.tsv"))
    over = list(C.read_tsv(os.path.join(C.GOLD, "congress_overrides.tsv")))
    npass = sum(1 for _ in open(os.path.join(C.HWORK, "p4_passages.jsonl"), encoding="utf-8"))
    nin = sum(1 for _ in open(os.path.join(C.HWORK, "p4_in.jsonl"), encoding="utf-8"))
    mult = json.load(open(os.path.join(C.HWORK, "claude", "super", "sample.json"), encoding="utf-8"))
    ins = {r["hkey"]: r for r in L("p4_in.jsonl")}
    west = 0.0
    wcand = 0.0
    for o in L("p4_out.jsonl"):
        a = o["ans"]
        r = ins[o["key"]]
        w = r["weight"] * mult.get(o["key"], 1.0)
        if a.get("error") is True:
            west += w
        if a.get("applies_old_rule") and not a.get("notes_statute") and a.get("conduct_after_effective") != "no":
            wcand += w
    ack = [r for r in rows if r["stratum"] == "ack"]
    a = aud("p4")
    conf = audrows("p4")
    return dict(
        predicate="citing court applies holding h of X to conduct u, where a statute superseded h for conduct from d "
                  "and u >= d (status at conduct = superseded), without accounting for the statute",
        lean="Hunt.twoDateError",
        corpus=dict(findings_appliesSupersededHolding=F["appliesSupersededHolding"], override_targets=len(over),
                    citations_after_effective_date=npass, located_sampled_pool=nin,
                    read=dict(reader="claude-subagent", rows=len(rows), errors=sum(r["error"] == "1" for r in rows),
                              applies_old_rule=sum(r["applies_old_rule"] == "1" for r in rows),
                              applies_old_rule_before_effective=sum(r["applies_old_rule"] == "1" and r["conduct_after_effective"] == "no" for r in rows),
                              weighted_error_estimate=round(west), weighted_candidate_estimate=round(wcand)),
                    confirmed_instances=len(conf)),
        known=dict(runner_findings=F["appliesSupersededHolding"],
                   runner_findings_audited=a.get("flagged_runner"),
                   note="the runner's own 26 findings (every later citation of the 11th Cir. Ledbetter under the charge-"
                        "timing issue) are the known set: none of the 20 audited applies the superseded holding. The "
                        "passage reader was validated on the acknowledged stratum (statute noted)",
                   ack_stratum=W(sum(r["notes_statute"] == "1" for r in ack), len(ack)), recall=None),
        audit=dict(reader="claude-subagent", flagged=a.get("flagged"), runner=a.get("flagged_runner"),
                   candidates_needing_full_text=a.get("top"), decoys=a.get("decoy")),
        precision=a.get("flagged_runner", {}).get("precision"), precision_ci95=a.get("flagged_runner", {}).get("ci95"),
        precision_basis="the runner's appliesSupersededHolding findings; the passage reader's 2 flags: 1 confirmed; "
                        "24 unsettled candidates: 2 confirmed",
        top=[inst(r) for r in conf])


def horty():
    """Pair-form Horty consistency (Spec.Horty.conflict) of the factor case base, per question family."""
    facts, reason = defaultdict(set), defaultdict(set)
    for p in C.read_tsv(os.path.join(C.DATA, "factors.tsv"), header=False):
        facts[p[0]].add((p[1], p[2]))
        if p[3] == "1":
            reason[p[0]].add((p[1], p[2]))
    fam = defaultdict(list)
    meta = {}
    for p in C.read_tsv(os.path.join(C.DATA, "factor_cases.tsv"), header=False):
        fam[p[2]].append(p[0])
        meta[p[0]] = (int(p[1]), "pi" if p[4] == "yes" else "delta", p[5])
    rows, per = [], {}
    for f, hs in fam.items():
        n = 0
        for i in range(len(hs)):
            for j in range(i + 1, len(hs)):
                a, b = hs[i], hs[j]
                if meta[a][1] != meta[b][1] and reason[b] <= facts[a] and reason[a] <= facts[b] and reason[a] and reason[b]:
                    n += 1
                    rows.append([f, a, meta[a][0], meta[a][1], meta[a][2], b, meta[b][0], meta[b][1], meta[b][2]])
        per[f] = dict(cases=len(hs), conflicting_pairs=n)
    nodes = C.nodes({r[2] for r in rows} | {r[6] for r in rows})
    for r in rows:
        r += [nodes.get(r[2], {}).get("name", "")[:60], nodes.get(r[6], {}).get("name", "")[:60]]
    C.write_tsv(os.path.join(H, "data", "p5_horty.tsv"), rows,
                ["family", "holding1", "node1", "outcome1", "date1", "holding2", "node2", "outcome2", "date2", "name1", "name2"])
    return per, rows


def p5(F):
    rows = tsv(os.path.join(H, "data", "p5_losing_side.tsv"))
    sp = Counter(r[0] for r in C.read_tsv(os.path.join(C.OUT, "splits.tsv")))
    gold = list(C.read_tsv(os.path.join(C.GOLD, "splits_resolved.tsv")))
    side = L("p5_side_out.jsonl")
    sides = Counter(s["side"] for o in side for s in o["ans"].get("sides", []))
    ins = {r["hkey"]: r for r in L("p5_in.jsonl")}
    mult = json.load(open(os.path.join(C.HWORK, "claude", "split", "sample.json"), encoding="utf-8"))
    west = sum(ins[o["key"]]["weight"] * mult.get(o["key"], 1.0) for o in L("p5_out.jsonl") if o["ans"].get("zombie"))
    # known: is the losing side noted as abrogated/overruled/reversed by that SCOTUS decision in later courts' notes?
    pairs = set()
    for p in C.read_tsv(os.path.join(C.GOLD, "reports_typed_pairs.tsv")):
        if p[3].lstrip("-").isdigit():
            pairs.add((int(p[0]), int(p[3])))
    losing = {(r["cited"], r["scotus"]) for r in ins.values()}
    noted = sum(1 for x in losing if x in pairs)
    per, hrows = horty()
    a = aud("p5")
    npass = sum(1 for _ in open(os.path.join(C.HWORK, "p5_passages.jsonl"), encoding="utf-8"))
    return dict(
        predicate="(a) Horty: two cases of one binding base with opposite outcomes, each reason present in the other's "
                  "facts; (b) split: two good-law opposite answers by courts neither of which binds the other; (c) after "
                  "SCOTUS resolves the split, a court relies on the losing side for the resolved question without noting it",
        lean="Hunt.inconsistentBase, Hunt.persistingSplit, Hunt.losingSideAfterResolution",
        corpus=dict(splits_persisting=sp.get("split", 0), conflicts_within_one_bound_court=sp.get("conflict", 0),
                    horty=dict(families=len(per), cases=sum(v["cases"] for v in per.values()),
                               conflicting_pairs=len(hrows),
                               by_family={k: v for k, v in per.items() if v["conflicting_pairs"]}),
                    scotus_resolutions_gold=len(gold), with_conflict_decisions_read=len(side),
                    conflict_decisions_by_side=dict(sides, reader="azure gpt-5.4-mini"),
                    losing_side_decisions_cited_later=len({r["cited"] for r in ins.values()}),
                    later_citations_of_losing_side=npass, silent_located_pool=len(ins),
                    read=dict(reader="claude-subagent", rows=len(rows), zombies=sum(r["zombie"] == "1" for r in rows),
                              weighted_estimate_in_pool=round(west),
                              weighted_estimate_after_audit=round(west * a["flagged"]["precision"]))),
        known=dict(note="losing-side decisions that later courts themselves marked as overruled / abrogated / reversed by "
                        "the resolving Supreme Court decision (reports_typed_pairs.tsv)",
                   losing_side_pairs=len(losing), noted_by_later_courts=noted, recall=W(noted, len(losing))),
        audit=dict(reader="claude-subagent", flagged=a.get("flagged"), top=a.get("top"), decoys=a.get("decoy")),
        precision=a["flagged"]["precision"], precision_ci95=a["flagged"]["ci95"], precision_basis="one read (claude-subagent) + audit",
        top=[inst(r) for r in audrows("p5", ("top", "flagged"))])


def p6():
    d = lambda n: tsv(os.path.join(H, "data", n))
    A, B, Cc, Dd, E = d("p6a_adoption_relativity.tsv"), d("p6b_successor_gaps.tsv"), d("p6c_dual_high_courts.tsv"), \
        d("p6d_unpublished_windows.tsv"), d("p6e_forum_choice.tsv")
    Fp, G, Hh = d("p6f_named_probes.tsv"), d("p6g_commission.tsv"), d("p6h_rule_values.tsv")
    seenA = set()
    Au = []
    for r in A:
        k = (r["target"], r["by"], r["other_heir"])
        if k not in seenA:
            seenA.add(k)
            Au.append(r)
    byheir = defaultdict(lambda: [0, 0, 0])
    for r in Au:
        k = "%s overrules; still binding on %s" % (r["by_court"], r["other_heir"])
        byheir[k][0] += 1
        byheir[k][1] += int(r["other_heir_citations_after"])
        byheir[k][2] += int(r["flagged_citesOverruled"])
    gaps = [r for r in B if r["gap"] == "1" and "selfNotBound" not in r["force_on_new"]]
    win = [(r["window"], int(r["decisions"])) for r in Dd]
    return dict(
        predicate="search of the rule tables with the reference engine: a pair (decision, forum) whose force differs "
                  "from the force of the same decision in a sibling forum, or changes across a cut-off date, or survives "
                  "a negation the source court made",
        lean="Hunt.forumDependent, Hunt.adoptionCarriesOverruled, Hunt.dualHighCourtConflict, Hunt.cutoffWindow",
        adoption_chains=dict(treatments=len(Au), with_power=sum(r["power"].startswith("yes") for r in Au),
                             other_heir_citations_after=sum(int(r["other_heir_citations_after"]) for r in Au),
                             of_which_runner_flags_citesOverruled=sum(int(r["flagged_citesOverruled"]) for r in Au),
                             by_heir={k: dict(treatments=v[0], later_citations=v[1], flagged=v[2]) for k, v in byheir.items()}),
        successor_gaps=dict(successions=len(B), without_binding_on_any_court=len(gaps),
                            orphaned_decisions=sum(int(r["old_decisions"]) for r in gaps),
                            later_citations=sum(int(r["later_citations_in_new_structure"]) for r in gaps),
                            rows=[dict(old=r["old_name"], new=r["new_name"], date=r["date"], decisions=int(r["old_decisions"]),
                                       force=r["force_on_new"], later_citations=int(r["later_citations_in_new_structure"]))
                                  for r in gaps],
                            named_probes=[dict(r) for r in Fp if r["probe_node"] != "-"]),
        dual_high_courts=dict(cross_treatments=len(Cc),
                              rows=[dict(by=r["by_name"], by_court=r["by_court"], target=r["target_name"],
                                         target_court=r["target_court"], kind=r["kind"], power=r["power"],
                                         both_bind_intermediate=(r["force_of_by_on_intermediate"].startswith("binding")
                                                                 and r["force_of_target_on_intermediate"].startswith("binding")))
                                    for r in Cc]),
        unpublished_windows=dict(rows=len(win), top=win[:12]),
        forum_choice=dict(cross_system_departures=len(E),
                          by_direction=Counter(r["direction"] for r in E).most_common(),
                          rule_values=[dict(r) for r in Hh if r["rule"] in ("trialScope", "horizontal", "stateFollowsCircuit", "firstInTimeControls")]),
        commission=dict(rows=[dict(r) for r in G[:12]],
                        texas_commission_decisions=int(next((r["source_published_decisions_before"] for r in Fp
                                                             if r["case"].startswith("Texas Commission")), 0)),
                        texas_commission_with_notation=sum(int(r["decisions"]) for r in G if r["court"] == "Texas Commission of Appeals")))


def main():
    F = findings_counts()
    S = dict(generated="2026-11-12", corpus=dict(findings=dict(F)),
             readers=dict(first_pass="azure gpt-5.4-mini (kept from before the hand-over; labelled in every *_out.jsonl)",
                          later="claude-subagent (pattern 2 remainder, patterns 4 and 5, all second reads, all audits)"),
             patterns=dict(p1_zombie=p1(F), p2_unpublished=p2(F), p3_panel=p3(F), p4_superseded=p4(F), p5_splits=p5(F),
                           p6_rules=p6()))
    with open(os.path.join(H, "summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(S, f, indent=1, ensure_ascii=False)
    for k, v in S["patterns"].items():
        if "precision" in v:
            print(k, "precision", v["precision"], v["precision_ci95"], "|", v["precision_basis"])
            print("   known", json.dumps(v["known"])[:600])
            print("   corpus", json.dumps(v["corpus"])[:1500])
    print(json.dumps(S["patterns"]["p6_rules"])[:3000])


if __name__ == "__main__":
    main()
