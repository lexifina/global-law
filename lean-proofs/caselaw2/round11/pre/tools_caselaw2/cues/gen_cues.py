"""One cue table for every checker (round 4, item 2).

Source of truth: cue_table.json (this folder). This script writes it into
  - LegalProofs/CaseLaw2/CueTable.lean   (Lean: Cert.treatCues, Cert.histCues, Cert.treatDisqualifiers, Cert.histDisqualifiers)
  - tools/caselaw2/ref/cue_table.py      (reference engine: VERBS, DISQUALIFY_TREAT, DISQUALIFY_HIST)
  - tools/caselaw2/reader/cue_table.py   (reader / certifier: the same module)
Usage: python gen_cues.py [--check] [--skip-ref]   (--check: exit 1 if a generated file differs from the table;
       --skip-ref: leave tools/caselaw2/ref/cue_table.py alone (round 8: ref/ has its own writer, agent ref8))
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
T = json.load(open(os.path.join(HERE, "cue_table.json"), encoding="utf-8"))


def lstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def llist(xs):
    return "[" + ", ".join(lstr(x) for x in xs) + "]"


# round 5: (Lean name, table key, doc)
R5 = [("selfAnnouncedCues", "self_announced", "Round 5: terms of art; an explicit row whose quote has one is class `selfAnnounced`."),
      ("recognisedCues", "recognised", "Round 5: cue phrases of a recognised overruling (a later court's statement)."),
      ("recognisedDisqualifiers", "disqualify_recognised",
       "Round 5: phrases that show a later court's sentence is not an accepted statement that X was overruled."),
      ("operativeCues", "operative", "Round 5: operative words other than the terms of art."),
      ("operativeWhole", "operative_whole", "Round 5: phrases that dispose of the case as a whole."),
      ("operativeLimit", "operative_limit",
       "Round 5: words that limit an act to part of a case; with one of them the quote is not a whole-case disposal."),
      ("operativeDisqualifiers", "disqualify_operative",
       "Round 5: objects other than a case (arguments, contentions ...) that the court rejects.")]
# round 6 (round6/history/DESIGN6.md section 4): the anchor quote of an anchored history row
R6 = [("anchorCues", "anchor",
       "Round 6: cue phrases of an anchor quote (the sentence identifying the decision acted on)."),
      ("anchorDisqualifiers", "disqualify_anchor",
       "Round 6: marks of an earlier proceeding; an anchor quote with one of them is not the decision under review.")]
# round 7 (round7/DESIGN7.md sections 2-3): joined certificates, doctrine rows, history claims
R7 = [("anaphorCues", "anaphor",
       "Round 7: anaphors; the main quote of an `antecedent` joined row refers back with one of them."),
      ("doctrineTieCues", "doctrine_tie",
       "Round 7: phrases that tie a doctrine to the case it comes from (`doctrineTie` joined quote)."),
      ("doctrineRejectCues", "doctrine_reject",
       "Round 7: cue phrases of a doctrine row's main quote (doctrine mode)."),
      ("joinedDisqualifiers", "disqualify_joined",
       "Round 7: phrases that show a joined quote is not the court's own statement."),
      ("setAsideCues", "set_aside",
       "Round 7: \"set aside\" as a vacatur cue (history rows with a `setAside` claim).")]
R7_NAT = [("joinedGapMax", "joined_gap_max",
           "Round 7: the most characters between an `antecedent` joined quote and the main quote."),
          ("orderHeadFrom", "order_head_from",
           "Round 7: the first date of Supreme Court orders printed as head matter only (`orderHead` claim)."),
          ("orderHeadMaxLen", "order_head_max_len",
           "Round 7: the longest quote an `orderHead` claim admits as head matter.")]
# round 8 (round8/DESIGN8.md sections 4-5): bridge evidence of history rows, wide anchor cues (appended)
R8 = [("anchorWideCues", "anchor_wide",
       "Round 8: further anchor cues, used only under an `anchorWide` claim (DESIGN8 section 5).")]
R8_NAT = [("bridgeMaxLen", "bridge_max_len",
           "Round 8: the longest bridge quote (DESIGN8 section 4, step 1).")]
# round 9 (round9/DESIGN9.md sections 5 and 7): far antecedents, implicit rejection (appended)
R9 = [("implicitRejectCues", "implicit_reject",
       "Round 9: cue phrases a soft row may use under an `implicitReject` claim (DESIGN9 section 7)."),
      ("anchorWide9Cues", "anchor_wide9",
       "Round 9: judge-form anchor cues, used with `anchor_wide` under an `anchorWide` claim (DESIGN9 section 8).")]
R9_NAT = [("joinedFarMax", "joined_far_max",
           "Round 9: the most characters between a far `antecedent` joined quote and the main quote under a "
           "`joinedFar` claim (DESIGN9 section 5).")]
# round 10 (round10/DESIGN10.md section 4, D10-5, D10-6): remand bridge evidence of history rows (appended)
R10 = [("remandCourtCues", "remand_court",
        "Round 10: the court phrase B's remand quote must hold (DESIGN10 section 4, check 3)."),
       ("remandCues", "remand_cue",
        "Round 10: the remand cues B's quote must hold with the court phrase (DESIGN10 section 4, check 3)."),
       ("remandMonths", "remand_months",
        "Round 10: the full month names of the printed order date (`<month> <d>, <yyyy>`; D10-6).")]
R10_NAT = [("remandQuoteMax", "remand_quote_max", "Round 10: the longest remand quote of B (DESIGN10 section 4)."),
           ("remandDocketSpanMax", "remand_docket_span_max",
            "Round 10: the longest docket span of B's or the target's text (D10-5)."),
           ("remandDaysMax", "remand_days_max", "Round 10: the most days from the order to the remand decision B.")]
# round 10, D10-7 (section 4 amendment 2): the reason-case tie
R10B = [("remandOrderCues", "remand_order_cue",
         "Round 10: the phrase that introduces the reason case in the order's span (D10-7, tie (c2)).")]
R10B_NAT = [("remandOrderSpanMax", "remand_order_span_max", "Round 10: the longest span of the order's text (D10-7)."),
            ("remandTieMin", "remand_tie_min", "Round 10: the fewest characters of a compact reason-case tie (D10-7).")]
# round 10 section 6 (D10-8, D10-9): the trial-judgment bridge
R10C = [("trialCourtNames", "trial_court_names",
         "Round 10: trial-court names; D's judgment line under a `trialBridge` claim holds one (DESIGN10 section 6)."),
        ("intermediateCourtNames", "intermediate_court_names",
         "Round 10: intermediate-court names; D's judgment line under a `trialBridge` claim holds none."),
        ("tbridgeCues", "tbridge_cue", "Round 10: the cue of T's own judgment line (it affirmed; `trialBridgeT`)."),
        ("tbridgeNegative", "tbridge_negative", "Round 10: phrases T's judgment line must not hold (`trialBridgeT`).")]
R10C_NAT = [("tbridgeQuoteMax", "tbridge_quote_max", "Round 10: the longest quote of T's text (`trialBridgeT`)."),
            ("tbridgeDaysMax", "tbridge_days_max", "Round 10: the most days from T to D (`trialBridgeDate`).")]


def lean():
    o = ["import LegalProofs.CaseLaw2.Events", "",
         "/-! GENERATED by tools/caselaw2/cues/gen_cues.py from cue_table.json. Do not edit: edit the table and",
         "re-run the generator. The same table is written to the reference engine and the reader",
         "(`tools/caselaw2/ref/cue_table.py`, `tools/caselaw2/reader/cue_table.py`). -/", "",
         "namespace CaseLaw2.Cert", "open CaseLaw2", "",
         "/-- Cue phrases of a treatment kind: a certificate quote must contain one. -/",
         "def treatCues : TKind → List String"]
    for k, v in T["treat"].items():
        o.append("  | .%s => %s" % (k, llist(v)))
    o += ["", "/-- Cue phrases of a same-case history kind. -/", "def histCues : HKind → List String"]
    for k, v in T["hist"].items():
        o.append("  | .%s => %s" % (k, llist(v)))
    o += ["", "/-- Phrases that show a quote is not the court's own status-changing act. -/",
          "def treatDisqualifiers : List String :=", "  " + llist(T["disqualify_treat"]), "",
          "/-- Phrases that show a history quote is a separate opinion's would-be disposition. -/",
          "def histDisqualifiers : List String :=", "  " + llist(T["disqualify_hist"]), ""]
    # round 5 (DESIGN5.md section 6)
    for name, key, doc in R5 + R6:
        o += ["/-- %s -/" % doc, "def %s : List String :=" % name, "  " + llist(T[key]), ""]
    # round 7 (round7/DESIGN7.md): appended, so every earlier line stays byte-identical
    for name, key, doc in R7:
        o += ["/-- %s -/" % doc, "def %s : List String :=" % name, "  " + llist(T[key]), ""]
    o += ["/-- Round 7: the order-list / judgment-line forms of a history kind (`orderHead` claim). -/",
          "def orderLineCues : HKind → List String"]
    for k, v in T["order_line"].items():
        o.append("  | .%s => %s" % (k, llist(v)))
    o += ["  | _ => []", ""]
    for name, key, doc in R7_NAT:
        o += ["/-- %s -/" % doc, "def %s : Nat := %d" % (name, int(T[key])), ""]
    # round 8: appended
    for name, key, doc in R8:
        o += ["/-- %s -/" % doc, "def %s : List String :=" % name, "  " + llist(T[key]), ""]
    o += ["/-- Round 8: the history cues of a bridge quote, after the target's citation (DESIGN8 section 4, step 5). -/",
          "def bridgeCues : HKind → List String"]
    for k, v in T["bridge_cue"].items():
        o.append("  | .%s => %s" % (k, llist(v)))
    o += ["  | _ => []", ""]
    for name, key, doc in R8_NAT:
        o += ["/-- %s -/" % doc, "def %s : Nat := %d" % (name, int(T[key])), ""]
    o += ["/-- Round 8: (acting circuit, target circuit, acting date before) of the old circuits (`oldCircuit` claim,",
          "DESIGN8 section 6). -/", "def oldCircuitRules : List (Nat × Nat × Nat) :=",
          "  [" + ", ".join("(%d, %d, %d)" % tuple(t) for t in T["old_circuit"]) + "]", ""]
    # round 9: appended
    for name, key, doc in R9:
        o += ["/-- %s -/" % doc, "def %s : List String :=" % name, "  " + llist(T[key]), ""]
    for name, key, doc in R9_NAT:
        o += ["/-- %s -/" % doc, "def %s : Nat := %d" % (name, int(T[key])), ""]
    # round 10: appended
    for name, key, doc in R10:
        o += ["/-- %s -/" % doc, "def %s : List String :=" % name, "  " + llist(T[key]), ""]
    o += ["/-- Round 10: the abbreviations of each month (January first) in the printed order date (`<abbr> <d>, <yyyy>`;",
          "D10-6). -/", "def remandMonthsAbbr : List (List String) :=",
          "  [" + ", ".join(llist(v) for v in T["remand_months_abbr"]) + "]", ""]
    for name, key, doc in R10_NAT:
        o += ["/-- %s -/" % doc, "def %s : Nat := %d" % (name, int(T[key])), ""]
    for name, key, doc in R10B:
        o += ["/-- %s -/" % doc, "def %s : List String :=" % name, "  " + llist(T[key]), ""]
    for name, key, doc in R10B_NAT:
        o += ["/-- %s -/" % doc, "def %s : Nat := %d" % (name, int(T[key])), ""]
    for name, key, doc in R10C:
        o += ["/-- %s -/" % doc, "def %s : List String :=" % name, "  " + llist(T[key]), ""]
    for name, key, doc in R10C_NAT:
        o += ["/-- %s -/" % doc, "def %s : Nat := %d" % (name, int(T[key])), ""]
    o += ["end CaseLaw2.Cert", ""]
    return "\n".join(o)


def py():
    o = ['"""GENERATED by tools/caselaw2/cues/gen_cues.py from cue_table.json. Do not edit."""',
         "VERBS = {"]
    for sec in ("treat", "hist"):
        for k, v in T[sec].items():
            if v:
                o.append("    %r: %r," % (k, tuple(v)))
    o += ["}", "TREAT_KINDS = %r" % (tuple(T["treat"]),), "DISQUALIFY_TREAT = %r" % (tuple(T["disqualify_treat"]),),
          "DISQUALIFY_HIST = %r" % (tuple(T["disqualify_hist"]),)]
    for _, key, _ in R5 + R6:
        o.append("%s = %r" % (key.upper(), tuple(T[key])))
    # round 7: appended
    for _, key, _ in R7:
        o.append("%s = %r" % (key.upper(), tuple(T[key])))
    o.append("ORDER_LINE = {")
    for k, v in T["order_line"].items():
        o.append("    %r: %r," % (k, tuple(v)))
    o.append("}")
    for _, key, _ in R7_NAT:
        o.append("%s = %d" % (key.upper(), int(T[key])))
    # round 8: appended
    for _, key, _ in R8:
        o.append("%s = %r" % (key.upper(), tuple(T[key])))
    o.append("BRIDGE_CUE = {")
    for k, v in T["bridge_cue"].items():
        o.append("    %r: %r," % (k, tuple(v)))
    o.append("}")
    for _, key, _ in R8_NAT:
        o.append("%s = %d" % (key.upper(), int(T[key])))
    o.append("OLD_CIRCUIT = %r" % (tuple(tuple(t) for t in T["old_circuit"]),))
    # round 9: appended
    for _, key, _ in R9:
        o.append("%s = %r" % (key.upper(), tuple(T[key])))
    for _, key, _ in R9_NAT:
        o.append("%s = %d" % (key.upper(), int(T[key])))
    # round 10: appended
    for _, key, _ in R10:
        o.append("%s = %r" % (key.upper(), tuple(T[key])))
    o.append("REMAND_MONTHS_ABBR = %r" % (tuple(tuple(v) for v in T["remand_months_abbr"]),))
    for _, key, _ in R10_NAT:
        o.append("%s = %d" % (key.upper(), int(T[key])))
    for _, key, _ in R10B:
        o.append("%s = %r" % (key.upper(), tuple(T[key])))
    for _, key, _ in R10B_NAT:
        o.append("%s = %d" % (key.upper(), int(T[key])))
    for _, key, _ in R10C:
        o.append("%s = %r" % (key.upper(), tuple(T[key])))
    for _, key, _ in R10C_NAT:
        o.append("%s = %d" % (key.upper(), int(T[key])))
    o.append("")
    return "\n".join(o)


OUT = {os.path.join(ROOT, "LegalProofs", "CaseLaw2", "CueTable.lean"): lean(),
       os.path.join(ROOT, "tools", "caselaw2", "ref", "cue_table.py"): py(),
       os.path.join(ROOT, "tools", "caselaw2", "reader", "cue_table.py"): py()}
bad = 0
for p, s in OUT.items():
    if "--skip-ref" in sys.argv and os.sep + "ref" + os.sep in p:
        continue
    if "--check" in sys.argv:
        cur = open(p, encoding="utf-8").read() if os.path.exists(p) else None
        if cur != s:
            bad += 1
            print("STALE", p)
    else:
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(s)
        print("wrote", p)
sys.exit(1 if bad else 0)
