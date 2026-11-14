import sys
sys.path.insert(0, "~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog/ans_prescreen/tmp")
from r5_write import build, F, T
from r5_parse import parse
P = "~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog/packs/pack_T1f_030.md"
O = "~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog/ans_prescreen/ans_pack_T1f_030.jsonl"
W = {k: v["window"] for k, v in parse(P).items()}
def SPAN(i, start, end):
    w = W[i]
    a = w.index(start)
    b = w.index(end, a) + len(end)
    return w[a:b]
rows = [
 F("s01582","cannotTell"),
 F("s02201","notOverruling"),
 F("s01700","otherDecision"),
 F("s01707","notOverruling"),
 F("s02603","notOverruling"),
 F("s02429","otherDecision"),
 F("s01701","otherDecision"),
 T("s01776","overruled","otherGrounds",
   SPAN("s01776","Cicenia v. Lagay, 357 U. S. 504, 507-508","overruled on other grounds, Miranda v. Arizona, 384 U. S. 436, 479 n. 48 (1966)"), 0.9),
 F("s01606","notOverruling"),
 F("s02205","notOverruling"),
 F("s01993","would"),
 F("s01690","notOverruling"),
 F("s01814","cannotTell", 0.4),
 F("s01761","negation"),
 F("s01927","negation"),
 F("s02460","notOverruling"),
 F("s01979","otherDecision"),
 F("s02477","quotation"),
 F("s02552","otherDecision"),
 F("s01727","notOverruling"),
 F("s01728","notOverruling"),
 F("s02527","notOverruling"),
 F("s02516","notOverruling"),
 F("s02305","otherDecision"),
 F("s01680","negation"),
 F("s01622","otherDecision"),
 F("s01743","otherDecision"),
 F("s01764","notOverruling"),
 F("s02259","otherDecision"),
 F("s02260","notOverruling"),
 F("s02353","otherDecision"),
 F("s03222","otherDecision"),
 F("s02226","argument"),
 F("s01777","ownAct"),
 T("s01792","overruled","otherGrounds",
   SPAN("s01792","Cohen v. Hurley, in other respects, has been overruled.","Spevack v. Klein, 385 U. S. 511 (1967)"), 0.8),
 T("s01793","overruled","otherGrounds",
   SPAN("s01793","Cohen v. Hurley, 366 U.S. 117, 124","Spevack v. Klein, 385 U.S. 511, 87 S.Ct. 625, 17 L.Ed.2d 574 (1967)"), 0.9),
 F("s02288","otherDecision"),
 F("s02382","otherDecision"),
 F("s02571","notOverruling"),
 F("s01648","wrongDirection"),
 F("s01703","otherDecision"),
 F("s01778","notOverruling"),
 F("s01865","notOverruling"),
 F("s01960","otherDecision"),
 F("s02191","wrongDirection"),
 F("s02627","notOverruling"),
 F("s02725","notOverruling"),
 F("s01709","notOverruling"),
 F("s01935","otherDecision"),
 F("s02227","otherDecision"),
]
build(P, O, rows)
