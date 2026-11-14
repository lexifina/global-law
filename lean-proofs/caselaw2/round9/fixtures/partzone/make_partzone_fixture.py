"""Round 9 fixture: part zones (DESIGN9 section 4, D9-4).

    python make_partzone_fixture.py        writes j/ and b/ here

Two stages built from the earlier fixtures (synthetic decisions only; no corpus text, no answer key), each with a
part_zone.tsv over the acting nodes (the text owners) of its rows:

j/  round7/fixtures/joined (treatments with joined lines, doctrine rows, a witness row; history rows with claims and
    an anchor): inside (ok kept), a joined quote in a dissent zone, an unverified-power row in a concurrence zone, a
    quote across two touching majority zones, a doctrine row in its zones, a round-8 failure kept (targetUnresolved,
    partNotMajority, doctrineAmbiguous), head matter in a head-matter zone and in a majority zone, an overlapping node,
    a node with an empty zone, a node with an unknown part (all three dropped), three bad lines (not poisoning node 10),
    an unknown node, rows with no zone.
b/  round8/fixtures/bridge (history rows with bridge and anchor lines): a bridged row whose W text is all dissent (the
    bridge quote is not zone-checked), a bridged row across a zone boundary, a head-matter row, an anchored row whose
    anchor lies in a dissent zone (not zone-checked), a row with no zone.

Each stage has data/ (with part_zone.tsv), data_nozone/ (without: the earlier fixture's output exactly) and
data_emptyzone/ (an empty part_zone.tsv: the same), edges/, expected_certs.tsv, expected_zone_summary.tsv and
expected_summary_changes.tsv (the earlier counters that the zone refusals change, with their new values).
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

SETS = {
    "j": {
        "src": os.path.join(ROOT, "round7", "fixtures", "joined"),
        "zones": [
            # t7:10 ok (main [626,649), joined [523,602)): one majority zone; a bad line for node 10 does not poison it
            (10, 0, 1000, "majority"),
            # t7:11 targetUnresolved: a boundary inside the quote, the round-8 reason is kept
            (11, 0, 630, "majority"), (11, 630, 1000, "dissent"),
            # t7:20 ok: its joined quote [561,605) in a dissent zone -> partZone
            (20, 0, 561, "majority"), (20, 561, 606, "dissent"), (20, 606, 1000, "majority"),
            # t7:22 okUnverifiedBy: the quote in a concurrence -> partZone
            (22, 0, 1000, "concurrence"),
            # t7:23 ok (main [561,620)): two touching majority zones meeting at 580 -> partZone (inside one zone)
            (23, 0, 580, "majority"), (23, 580, 1000, "majority"),
            # t7:30 doctrine ok (main [657,757), tie [0,183)): both inside majority zones -> ok
            (30, 0, 191, "majority"), (30, 191, 657, "other"), (30, 657, 800, "majority"),
            # t7:36 doctrineAmbiguous: in a dissent zone, the round-8 reason is kept
            (36, 0, 1000, "dissent"),
            # h7:50 ok (head matter [38,56) under orderHead): a head-matter zone -> ok
            (50, 0, 60, "headmatter"), (50, 60, 85, "majority"),
            # h7:51 ok (head matter [23,122)): a majority zone -> partZone
            (51, 0, 200, "majority"),
            # h7:57 ok: two overlapping zones -> the node keeps none -> ok
            (57, 0, 600, "majority"), (57, 500, 700, "dissent"),
            # h7:58 partNotMajority: kept
            (58, 0, 85, "dissent"),
            # h7:60 ok: an empty zone poisons the node -> ok
            (60, 0, 50, "headmatter"), (60, 50, 50, "majority"),
            # h7:62 noCue: an unknown part (case-sensitive) poisons the node
            (62, 0, 127, "Majority"),
            # a node no row acts from
            (99999, 0, 10, "majority"),
        ],
        "bad_lines": ["x1\t0\t5\tmajority\tr9:fixture-bad-node", "10\tabc\t5\tmajority\tr9:fixture-bad-offset",
                      "12\t0\t5\tmajority"],
        "refused": ["t7:20:0:606", "t7:22:0:584", "t7:23:0:561", "h7:51:5:certDenied"],
        "zone_summary": [("zone_nodes", 11), ("zone_lines", 18), ("zone_bad_nodes", 3), ("zone_bad_rows", 3),
                         ("zone_checked_rows", 7), ("zone_failed_rows", 4), ("zone_missing_rows", 3)],
        # t7:20, t7:22, t7:23 carry joined lines; t7:23 an operativeWords claim; h7:51 an orderHead claim
        "changes": [("joined_admitted", 2), ("joined_rejected", 20), ("operative_rows", 0), ("hclaim_admitted", 4),
                    ("hclaim_rejected", 8)],
        "bad_rows": 3,
    },
    "b": {
        "src": os.path.join(ROOT, "round8", "fixtures", "bridge"),
        "zones": [
            # h8:101 ok (bridged; main [26,44)): majority -> ok; its W (201) is all dissent: the bridge quote is not checked
            (101, 0, 26, "headmatter"), (101, 26, 200, "majority"), (201, 0, 500, "dissent"),
            # h8:112 ok (bridged; main [87,105)): a boundary at 100 -> partZone
            (112, 0, 100, "majority"), (112, 100, 300, "majority"),
            # h8:114 ok (head matter under orderHead): a head-matter zone -> ok
            (114, 0, 50, "headmatter"),
            # h8:300 ok (anchored; anchor [0,41), main [42,91)): the anchor in a dissent zone is not checked -> ok
            (300, 0, 42, "dissent"), (300, 42, 200, "majority"),
        ],
        "bad_lines": [],
        "refused": ["h8:112:5:certDenied"],
        "zone_summary": [("zone_nodes", 5), ("zone_lines", 8), ("zone_bad_nodes", 0), ("zone_bad_rows", 0),
                         ("zone_checked_rows", 4), ("zone_failed_rows", 1), ("zone_missing_rows", 1)],
        "changes": [("anchored_admitted", None), ("bridge_admitted", 2), ("bridge_rejected", 12)],
        "bad_rows": 0,
    },
}


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for l in lines:
            f.write(l + "\n")


def main():
    for name, s in SETS.items():
        out = os.path.join(HERE, name)
        if os.path.isdir(out):
            shutil.rmtree(out)
        os.makedirs(out)
        src_data = os.path.join(s["src"], "data")
        for d in ("data", "data_nozone", "data_emptyzone"):
            shutil.copytree(src_data, os.path.join(out, d))
        shutil.copytree(os.path.join(s["src"], "edges"), os.path.join(out, "edges"))
        zl = ["%d\t%d\t%d\t%s\tr9:fixture" % z for z in s["zones"]]
        write_lines(os.path.join(out, "data", "part_zone.tsv"), zl[:1] + s["bad_lines"] + zl[1:])
        write_lines(os.path.join(out, "data_emptyzone", "part_zone.tsv"), [])
        # expected certs: the earlier fixture's, with the refused rows turned partZone (both rule sets)
        with open(os.path.join(s["src"], "expected_certs.tsv"), encoding="utf-8") as f:
            rows = f.read().splitlines()
        exp = [rows[0]]
        seen = set()
        for r in rows[1:]:
            f = r.split("\t")
            if f[1] in s["refused"]:
                assert f[2].startswith("ok") and f[3].startswith("ok"), r
                f[2] = f[3] = "partZone"
                seen.add(f[1])
            exp.append("\t".join(f))
        assert seen == set(s["refused"]), seen
        write_lines(os.path.join(out, "expected_certs.tsv"), exp)
        shutil.copy(os.path.join(s["src"], "expected_certs.tsv"), os.path.join(out, "expected_certs_nozone.tsv"))
        zs = ["%s\t%d" % kv for kv in s["zone_summary"]]
        if s["bad_rows"]:
            zs.append("bad_rows\tpart_zone.tsv\t%d" % s["bad_rows"])
        write_lines(os.path.join(out, "expected_zone_summary.tsv"), zs)
        write_lines(os.path.join(out, "expected_summary_changes.tsv"),
                    ["%s\t%d" % (k, v) for k, v in s["changes"] if v is not None])
        print(name, "zones", len(zl), "bad lines", len(s["bad_lines"]), "refused", len(s["refused"]))


if __name__ == "__main__":
    main()
