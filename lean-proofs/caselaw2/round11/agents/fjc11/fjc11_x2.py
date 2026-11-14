"""fjc11 rule X2 over the N linker's rows (corpus-wide; no key, no list of cases).

    python -X utf8 fjc11_x2.py rows_n2.jsonl work/feat_n2.tsv rows_x2.jsonl [--drop-ids FILE]

X2 keeps a form x / s row (district decision J, appeal D) when
  identity    the caption tie H (each side of J's caption shares a distinctive word with D's head-matter caption)
              AND at least one of docket K / district judge U / date T (the linker's ties);
  ruling      J is the ruling under review: no other district decision of the same court and docket key dated after J
              and on or before D (the latest decision of that docket before the appeal), and D does not name a later
              ruling below (no date > J + 30 days in an "appeal(ed) from ..." / "judgment|order ... entered|dated ..."
              phrase of D);
  scope       the linker's rules P (partial hint), D (partial disposition sentence), C (consolidated appeal: a mixed
              end zone drops, a whole reversal / vacatur is scope unknown) are already applied.
--no-k (rule X2b): no docket tie K (a row with K drops), and at least one of U / T besides H.
The rule label becomes below:fjc11_x2 (note keeps the ties and flags).
"""
import collections, csv, json, sys

NL = chr(10)
NO_K = False


def main():
    src, feat, out = sys.argv[1], sys.argv[2], sys.argv[3]
    drop = set()
    if "--drop-ids" in sys.argv:
        drop = {l.strip() for l in open(sys.argv[sys.argv.index("--drop-ids") + 1], encoding="utf-8") if l.strip()}
    global NO_K
    NO_K = "--no-k" in sys.argv
    F = {(int(r["by"]), int(r["target"])): r for r in csv.DictReader(open(feat, encoding="utf-8"), delimiter="\t")}
    st = collections.Counter()
    keep = []
    for l in open(src, encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l)
        f = F[(r["by"], r["target"])]
        form, ties = f["form"], f["ties"]
        if form == "h":
            st["skip:form_h"] += 1
            continue
        if "H" not in ties:
            st["drop:no_caption_tie"] += 1
            continue
        if not set(ties) & set("KUT"):
            st["drop:no_second_tie"] += 1
            continue
        if NO_K and "K" in ties:
            # X2b: J's own docket number printed in D marks J as one ruling of the docket among several (D names
            # it to tell it from the ruling under review); reading r11 work/read: H+K* 18/30 right
            st["drop:docket_printed"] += 1
            continue
        if NO_K and not set(ties) & set("UT"):
            st["drop:no_judge_or_date_tie"] += 1
            continue
        if f["latest"] == "0":
            st["drop:later_sibling_of_docket"] += 1
            continue
        if f["named"] == "later":
            st["drop:names_later_ruling"] += 1
            continue
        r = dict(r, rule="below:fjc11_x2")
        keep.append(r)
        st["rows"] += 1
        st["rows:%s:%s" % (ties, r["kind"])] += 1
        st["kind:%s:%s" % (r["kind"], r["scope"])] += 1
    with open(out, "w", encoding="utf-8", newline=NL) as fo:
        for r in keep:
            fo.write(json.dumps(r, ensure_ascii=False) + NL)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
