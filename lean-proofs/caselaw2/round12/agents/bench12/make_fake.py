"""Synthetic build for the fjc_idb_unpub scorer self-test (never a real build). python -I make_fake.py <key_nodes.tsv> <fake dir>"""
import csv, hashlib, os, sys
kn, F = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(F, "out"), exist_ok=True)
os.makedirs(os.path.join(F, "data"), exist_ok=True)
CL = ["NEG_HIST", "UNK_HIST", "NEG_OTHER", "UNK_OTHER", "GOOD", "GOODROW"]
def h(s): return int(hashlib.md5(s.encode()).hexdigest(), 16)
st = open(os.path.join(F, "out", "status.tsv"), "w", encoding="utf-8", newline="\n")
st.write("node\tissue\tholding\tfrom\tto\tstatus\tx6\tx7\twitness\tactor\tpath\n")
hi = open(os.path.join(F, "data", "history.tsv"), "w", encoding="utf-8", newline="\n")
ce = open(os.path.join(F, "out", "certs.tsv"), "w", encoding="utf-8", newline="\n")
ex = open(os.path.join(F, "expected.tsv"), "w", encoding="utf-8", newline="\n")
def row(n, iss, frm, to, status, path, wit="w", act="a"):
    st.write("\t".join([n, iss, "-", str(frm), str(to), status, "-", "-", wit, act, path]) + "\n")
for i, u in enumerate(csv.DictReader(open(kn, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)):
    n = u["dist_node"]; c = CL[h(n) % 6]
    ex.write("%s\t%s\n" % (n, "GOOD" if c == "GOODROW" else c))
    if c == "NEG_HIST": row(n, "-", 19000101, 20261112, "neg:reversed", "history")
    elif c == "UNK_HIST": row(n, "-", 19000101, 20261112, "unknown:partial", "history")
    elif c == "NEG_OTHER": row(n, "-", 19000101, 20261112, "neg:overruled", "treatment")
    elif c == "UNK_OTHER": row(n, "-", 19000101, 20261112, "unknown:questioned", "treatment")
    elif c == "GOODROW": row(n, "-", 19000101, 20261112, "good", "-")
    # decoys that must be ignored
    if i % 3 == 0: row(n, "-", 19000101, 19991231, "neg:vacated", "history")      # expired
    if i % 4 == 0: row(n, "I1", 19000101, 20261112, "neg:reversed", "history")    # issue-level
    if i % 5 == 0: row(n, "-", 20270101, 20991231, "neg:reversed", "history")     # starts after as-of
    hi.write("h%d\t%s\t%d\t20100101\treversed\twhole\n" % (i, n, 9000000 + i))
    if i % 2: ce.write("history\th%d\tok\n" % i)
for j in range(50):  # node ids unknown to the key (staged Supreme Court order nodes)
    row(str(9000000 + j), "-", 19000101, 20261112, "neg:vacated", "history")
st.close(); hi.close(); ce.close(); ex.close()
