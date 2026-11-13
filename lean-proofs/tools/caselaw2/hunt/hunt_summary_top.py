"""Second step of the summary: add the per-pattern top-level fields the report generator reads (precision, recall,
their 95% intervals, counts) and the Lean status to hunt/summary.json.

    python hunt_summary.py && python hunt_summary_top.py
"""
import json, os
import hunt_summary as HS

PATH = os.path.join(HS.H, "summary.json")


def main():
    S = json.load(open(PATH, encoding="utf-8"))
    P = S["patterns"]
    n = lambda p: len(HS.audrows(p))

    def top_level(k, recall, basis, counts):
        P[k]["recall"] = recall["p"] if recall else None
        P[k]["recall_ci95"] = recall["ci95"] if recall else None
        P[k]["recall_basis"] = basis
        P[k]["counts"] = counts

    c = P["p1_zombie"]["corpus"]
    top_level("p1_zombie", P["p1_zombie"]["known"]["recall_status"],
              "status layer: literature overrulings (CRS table, casebooks) our data mark negative; 0 of 3 later-court "
              "call-outs are in the findings",
              dict(candidates=c["candidate_rows"],
                   reported_two_stage_in_sample=sum(v for kk, v in c["second_read"]["counts"].items() if kk.endswith("True")),
                   estimated_true_low=c["estimated_true_instances"]["two_stage_total"],
                   estimated_true_high=sum(c["estimated_true_instances"]["first_read_times_audit"].values()),
                   confirmed_by_audit=n("p1") + n("p1b")))
    c = P["p2_unpublished"]["corpus"]
    top_level("p2_unpublished", None, "the known instance (Anastasoff) cites a decision outside the corpus",
              dict(candidates=c["binding_cue_passages"], reported_first_pattern=c["first_read"]["violations"],
                   reported_refined=c["second_read"]["violations"], confirmed_by_audit=c["confirmed_instances"],
                   mislabelled_decisions=7342))  # courts_validation.md §6: 7,342 of the 77,575 reporter-printed labels were wrong
    c = P["p3_panel"]["corpus"]
    top_level("p3_panel", P["p3_panel"]["known"]["second_read_recall_on_audit_confirmed"],
              "second read against the instances the full-text audit confirmed in the first-read sample",
              dict(candidates=c["pairs"], reported_first_read=c["first_read"]["after_whole_court_filter"],
                   reported_two_stage=c["second_read"]["violations"],
                   estimated_true_low=c["estimated_true_instances"]["low"],
                   estimated_true_high=c["estimated_true_instances"]["high"], confirmed_by_audit=n("p3") + n("p3b")))
    c = P["p4_superseded"]["corpus"]
    top_level("p4_superseded", None, "the runner's 26 findings are not instances (0 of 20 audited), so nothing known to recall",
              dict(candidates=c["citations_after_effective_date"], read=c["read"]["rows"], reported=c["read"]["errors"],
                   runner_findings=c["findings_appliesSupersededHolding"], confirmed_by_audit=c["confirmed_instances"]))
    c = P["p5_splits"]["corpus"]
    top_level("p5_splits", P["p5_splits"]["known"]["recall"],
              "losing-side labels that later courts' own notes confirm (overruled / abrogated / reversed by the resolving decision)",
              dict(persisting_splits=c["splits_persisting"], conflicts=c["conflicts_within_one_bound_court"],
                   horty_conflicting_pairs=c["horty"]["conflicting_pairs"], candidates=c["later_citations_of_losing_side"],
                   read=c["read"]["rows"], reported=c["read"]["zombies"],
                   estimated_true_in_pool=c["read"]["weighted_estimate_after_audit"], confirmed_by_audit=n("p5")))
    r = P["p6_rules"]
    g = r["successor_gaps"]
    seen = {}
    for row in g["rows"]:          # one old court can have two successors: count it once
        seen.setdefault(row["old"], row)
    g["old_courts_without_binding_successor"] = len(seen)
    g["orphaned_decisions"] = sum(x["decisions"] for x in seen.values())
    g["later_citations"] = sum(x["later_citations"] for x in seen.values())
    r["precision"] = None
    r["recall"] = None
    two = {kk: v for kk, v in r["adoption_chains"]["by_heir"].items() if v["later_citations"]}
    r["counts"] = dict(adoption_two_heir_treatments=sum(v["treatments"] for v in two.values()),
                       adoption_other_heir_citations=sum(v["later_citations"] for v in two.values()),
                       adoption_flagged_by_runner=sum(v["flagged"] for v in two.values()),
                       successor_gaps=len(seen),
                       orphaned_decisions=r["successor_gaps"]["orphaned_decisions"],
                       dual_high_court_cross_treatments=r["dual_high_courts"]["cross_treatments"],
                       unpublished_windows=r["unpublished_windows"]["rows"],
                       cross_system_departures=r["forum_choice"]["cross_system_departures"])
    S["lean"] = dict(module="LegalProofs/CaseLaw2/Hunt.lean", guards=44, theorems=14,
                     compiled="yes: WSL Ubuntu, Lean 4.35.0, lake env lean LegalProofs/CaseLaw2/Hunt.lean, exit 0, no messages (2026-11-12)",
                     command="wsl.exe -d Ubuntu -- bash /mnt/c/Users/<you>/Documents/global-law-lean/lean-proofs/tools/caselaw2/hunt/hunt_lean.sh")
    S["strongest"] = [
        "In re Odyssey Healthcare, 310 S.W.3d 419 (Tex. 2010) applies National League of Cities v. Usery, overruled by Garcia in 1985",
        "United States v. Helsey, 463 F. Supp. 1111 (D. Mont. 1979) strikes down a federal statute on Hammer v. Dagenhart, overruled in 1941",
        "decisions2.pub mislabelled 7,342 reporter-printed decisions as not published (77,575 such labels, most of them right); every audited 'unpublished treated as binding' report was this error",
        "United States v. Armstrong, 550 F.3d 382 (5th Cir. 2008) requires an overt act for a 1956(h) conspiracy three years after Whitfield v. United States",
        "one day decides it: a Fifth Circuit decision of 30 Sep 1981 binds the Eleventh Circuit, even after the Fifth Circuit en banc overrules it (37 such overrulings, 63 later Eleventh Circuit citations, 10 of them reported by our own runner as citing overruled law)",
    ]
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(S, f, indent=1, ensure_ascii=False)
    for k, v in P.items():
        print(k, v.get("precision"), v.get("precision_ci95"), v.get("recall"), v.get("recall_ci95"), json.dumps(v.get("counts")))


if __name__ == "__main__":
    main()
