"""Round 8 (agent infra): write the h0 halves of the four new benchmark keys, by script, for the h0 shadow scorers.

    python -B -X utf8 round8/bench_h0/build_keys.py

Reads benchmarks/<key>/key*.tsv (read only; never prints, copies or summarises a row of the other half) and writes
round8/bench_h0/<key>/<file> with the header and exactly the rows the scorer needs to give its full h0 result:

  fjc_idb_appeals         key_nodes.tsv: units with half = h0 (the scorer splits units by their own `half`);
                          key.tsv: items with key_item = 1 and half = h0 (link_rate splits items by their own `half`).
  shadow_docket           key.tsv, rows with class in NEG/PART/CLEAN: the scorer's unit is the linked lower node; its
                          half is split_half(dataset, smallest sc_docket of the node's linked items) and its class is
                          pooled over ALL its linked items. Kept: every item with half = h0 (link_rate counts items by
                          their own half) and every linked item of a node whose node half is h0 (pooling). An item of
                          half h1 is kept only when its node is an h0 unit. For a node whose unit half is h1 but
                          which has a linked h0 item, one synthetic stub item (no key content, half h1, docket
                          "!h1unit-<n>" sorting first and hashing to h1) makes the scorer give that node half h1.
  scdb_disposition        key.tsv: rows with half = h0 (unit = SCDB case row; every count is split by the row's half).
  state_overruled_tables  key.tsv: the unit is the overruled decision x_node, whose half is the half of its FIRST
                          linked row in file order; its listed overrulers / tables / partial pool over all its linked
                          rows. Kept: every row with half = h0 (link counts) and every linked row of an x_node whose
                          unit half is h0. A linked h0 row of an h1 unit would open a false h0 unit: counted and the
                          build refuses if there is any (so far none).
Row order is the key's own (pooling and tie order depend on it). Lines are copied byte for byte.
Writes round8/bench_h0/KEYS.json: counts per file and the sha1 of each source and output file. Nothing is printed
but counts.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(C2, "benchmarks")


def split_half(dataset, key):
    """= benchmarks/common/benchlib.split_half."""
    v = int(hashlib.sha1(("bench:%s:%s" % (dataset, key)).encode("utf-8")).hexdigest(), 16)
    return ("h0", "h1")[v % 2]


def sha1(p):
    with open(p, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()


def read(ds, name):
    """(header line bytes, [(line bytes, dict)]) split on LF exactly as the scorers do (rstrip of the newline)."""
    p = os.path.join(SRC, ds, name)
    with open(p, "rb") as f:
        raw = f.read()
    lines = raw.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    hdr = lines[0].decode("utf-8").split("\t")
    out = []
    for l in lines[1:]:
        out.append((l, dict(zip(hdr, l.decode("utf-8").split("\t")))))
    return lines[0], out, p


def write(ds, name, hdr, keep):
    d = os.path.join(HERE, ds)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p + ".tmp", "wb") as f:
        f.write(hdr + b"\n")
        for l in keep:
            f.write(l + b"\n")
    os.replace(p + ".tmp", p)
    return p


def main():
    rep = {}

    def note(ds, name, src, n_in, out, n_out, **extra):
        rep.setdefault(ds, {})[name] = dict({"source_rows": n_in, "rows_written": n_out, "source_sha1": sha1(src),
                                             "out_sha1": sha1(out)}, **extra)

    # ---- FJC IDB appeals
    ds = "fjc_idb_appeals"
    h, rows, src = read(ds, "key_nodes.tsv")
    keep = [l for l, r in rows if r["half"] == "h0"]
    note(ds, "key_nodes.tsv", src, len(rows), write(ds, "key_nodes.tsv", h, keep), len(keep))
    h, rows, src = read(ds, "key.tsv")
    keep = [l for l, r in rows if r["key_item"] == "1" and r["half"] == "h0"]
    note(ds, "key.tsv", src, len(rows), write(ds, "key.tsv", h, keep), len(keep))

    # ---- Shadow Docket
    ds = "shadow_docket"
    h, rows, src = read(ds, "key.tsv")
    score = [(l, r) for l, r in rows if r["class"] in ("NEG", "PART", "CLEAN")]
    bynode = {}
    for l, r in score:
        if r["link"] == "linked":
            bynode.setdefault(r["node"], []).append(r)
    h0nodes = set()
    for node, its in bynode.items():
        its = sorted(its, key=lambda x: x["sc_docket"])
        if split_half(ds, its[0]["sc_docket"]) == "h0":
            h0nodes.add(node)
    keep = [l for l, r in score if r["half"] == "h0" or (r["link"] == "linked" and r["node"] in h0nodes)]
    n_h1_items_of_h0_units = sum(1 for l, r in score if r["half"] != "h0" and r["link"] == "linked"
                                 and r["node"] in h0nodes)
    # An h0 item linked to a node whose unit half is h1 counts in the h0 link_rate, but alone it would make the
    # scorer open that node as a unit and compute its half from the h0 items only (possibly h0: a false h0 unit).
    # For each such node one SYNTHETIC stub item is added (no key content: sc_docket "!h1unit-<n>", which sorts before
    # every real docket and hashes to h1; half h1, so it counts in no h0 figure; class CLEAN, other fields "-"), so
    # the scorer computes that node's half as h1 and leaves it out of every h0 figure and of the h0 cases table.
    hdr = h.decode("utf-8").split("\t")
    other = sorted({r["node"] for l, r in score if r["half"] == "h0" and r["link"] == "linked"
                    and r["node"] not in h0nodes}, key=lambda x: (len(x), x))
    stubs = []
    j = 0
    for node in other:
        while True:
            s = "!h1unit-%d" % j
            j += 1
            if split_half(ds, s) == "h1":
                break
        assert all(s < r["sc_docket"] for r in bynode[node]), node
        f = {c: "-" for c in hdr}
        f.update({"sc_docket": s, "half": "h1", "class": "CLEAN", "link": "linked", "node": node,
                  "order_date": "0", "sc_in_corpus": "no"})
        stubs.append("\t".join(f[c] for c in hdr).encode("utf-8"))
    n_h0_items_of_h1_units = sum(1 for l, r in score if r["half"] == "h0" and r["link"] == "linked"
                                 and r["node"] not in h0nodes)
    note(ds, "key.tsv", src, len(rows), write(ds, "key.tsv", h, keep + stubs), len(keep) + len(stubs),
         h0_units=len(h0nodes), h1_half_items_kept_as_part_of_h0_units=n_h1_items_of_h0_units,
         h0_half_items_linked_to_h1_units=n_h0_items_of_h1_units, synthetic_h1_stub_items=len(stubs))

    # ---- SCDB disposition
    ds = "scdb_disposition"
    h, rows, src = read(ds, "key.tsv")
    keep = [l for l, r in rows if r["half"] == "h0"]
    note(ds, "key.tsv", src, len(rows), write(ds, "key.tsv", h, keep), len(keep))

    # ---- state overruled tables
    ds = "state_overruled_tables"
    h, rows, src = read(ds, "key.tsv")
    unit_half = {}
    for l, r in rows:
        if r["pair_status"] == "linked" and r["x_node"] not in unit_half:
            unit_half[r["x_node"]] = r["half"]
    h0x = {x for x, hv in unit_half.items() if hv == "h0"}
    bad = sum(1 for l, r in rows if r["pair_status"] == "linked" and r["half"] == "h0" and r["x_node"] not in h0x)
    if bad:
        sys.exit("state_overruled_tables: %d linked h0 rows belong to a unit whose half is not h0; refusing" % bad)
    keep = [l for l, r in rows if r["half"] == "h0" or (r["pair_status"] == "linked" and r["x_node"] in h0x)]
    n_other = sum(1 for l, r in rows if r["half"] != "h0" and r["pair_status"] == "linked" and r["x_node"] in h0x)
    note(ds, "key.tsv", src, len(rows), write(ds, "key.tsv", h, keep), len(keep), h0_units=len(h0x),
         other_half_rows_kept_as_part_of_h0_units=n_other)

    with open(os.path.join(HERE, "KEYS.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, indent=1, sort_keys=True)
        f.write("\n")
    for ds, v in rep.items():
        for name, c in v.items():
            print(ds, name, "rows %d -> %d" % (c["source_rows"], c["rows_written"]),
                  " ".join("%s=%s" % (k, c[k]) for k in sorted(c) if k not in
                           ("source_rows", "rows_written", "source_sha1", "out_sha1")))


if __name__ == "__main__":
    main()
