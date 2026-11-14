"""Pipeline test only: a synthetic order-list nodes folder (FORMAT.md shape) made from corpus GVR orders that round-10
C6 linked, written as an order list prints them (date heading, "docket SURNAME, GIVEN V. ..." caption line, the
disposition sentences). Output work/synth_nodes/. Never staged for scoring.
    python -X utf8 round11/agents/shadow11/mk_synth.py [N]
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import olink11 as X  # noqa: E402

R = X.R
NL = chr(10)


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    ref = []
    for line in open(os.path.join(X.S10W, "build10_cap_b_links.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[2] >= "20150101":
            ref.append(int(p[0]))
    ref = ref[:: max(1, len(ref) // k)][:k]
    out = os.path.join(HERE, "work", "synth_nodes")
    os.makedirs(os.path.join(out, "text"), exist_ok=True)
    rows = ["local_id\tdocket\tdate\tcaption\tdisposition\tlist_file\tline_span"]
    for i, on in enumerate(ref):
        o = R.orders()[on]
        cap = X.to_list_style(R.one_caption(o, True))
        dk = re.sub(r"[^\d\-]", "", (o["docket"] or "").replace("–", "-").split()[0]) or "-"
        d = datetime.date(o["date"] // 10000, o["date"] // 100 % 100, o["date"] % 100)
        head = d.strftime("%A, %B %d, %Y").upper()
        q0, q1 = o["disp"]
        disp = o["T"][q0 - o["off"]:].strip()
        disp = re.sub(r"\s+", " ", disp)[:600]
        lid = "synth%02d" % i
        txt = head + NL + "CERTIORARI -- SUMMARY DISPOSITIONS" + NL + dk + " " + cap + NL + \
            "The petition for a writ of certiorari is granted. " + disp + NL
        open(os.path.join(out, "text", lid + ".txt"), "w", encoding="utf-8", newline=NL).write(txt)
        rows.append("\t".join([lid, dk, str(o["date"]), cap, "GVR", "synthetic", "1-4"]))
        print(lid, on, dk, cap[:70])
    open(os.path.join(out, "nodes.tsv"), "w", encoding="utf-8", newline=NL).write(NL.join(rows) + NL)


if __name__ == "__main__":
    main()
