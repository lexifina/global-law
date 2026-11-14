# -*- coding: utf-8 -*-
import json, os, re

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\audit\recog1"
PACK = os.path.join(BASE, "packs", "audit_05.md")
OUT = os.path.join(BASE, "answers", "ans_05.jsonl")

# id, stated, x_ok, y_ok, extent, words, note
A = [
 ("mtwqh9f", "yes", True, True, "otherGrounds", "overruled on other grounds by Garnes v. Fleming Landfill, Inc., 186 W.Va. 656", "court's own citation history for Wells"),
 ("d2tzcev", "yes", True, True, "whole", "abrogated by Granzer v. State, 2008 WY 118, 193 P.3d 266 (Wyo.2008)", "court's own citation parenthetical after Reilly"),
 ("9q7fs76", "yes", True, True, "part", "we approve Whitehurst and disapprove Gevertz to the extent it is inconsistent with this opinion", "per curiam disapproves the conflict case itself; Gevertz = Gevertz v. Gevertz, 608 So.2d 129 (wider text)"),
 ("dsefnv6", "yes", True, True, "otherGrounds", "overruled on other grounds in O’Kelley v. State, 284 Ga. 758 (3)", ""),
 ("yedbd43", "yes", True, True, "otherGrounds", "overruled on other grounds by Cooper Tire & Rubber Co. v. McGill", ""),
 ("a5k5uyy", "yes", True, True, "otherGrounds", "abrogated in part on other grounds by Abdul-Wadood v. Duckworth, 860 F.2d 280, 285", "in part and on other grounds"),
 ("cvhgy5d", "yes", True, True, "whole", "this Court expressly overruled Trujillo in Champlin Petroleum Co.", "passage names Y 'Champlin Petroleum Co. v. Lyman' but citation 103 N.M. 407, 708 P.2d 319 (1985) matches the claim's Y"),
 ("7wyt9sa", "yes", True, True, "whole", "abrogated by Buck v. Cam’s Broadloom Rugs, Inc., 328 Md. 51, 56", ""),
 ("ft5py9n", "yes", True, True, "part", "overruled in part by Valdez v. People 966 P.2d 587, 591 (Colo.1998)", ""),
 ("6y6wcsb", "yes", True, True, "part", "overruled in part, Walters v. City of St. Louis, 364 Mo. 56, 259 S.W.2d 377, 382 (banc 1953)", "footnote of the majority opinion"),
 ("gqjxtrq", "yes", True, True, "otherGrounds", "overruled on other grounds in People v. Perez, 62 Cal.2d 769, 776", ""),
 ("fcmgvwv", "yes", True, True, "part", "We reconsider that opinion and overrule its holding that amortization provisions are per se unconstitutional.", "speaking court overrules one holding of Ailes itself"),
 ("zatur4u", "yes", True, True, "otherGrounds", "abrogated, on other grounds by Fleshner v. Pepose Vision Inst., Inc., 304 S.W.3d 81", ""),
 ("mca6cj8", "yes", True, True, "otherGrounds", "disapproved on other grounds by Wood v. State, 111 Nev. 428, 430", "footnote of the opinion of the court"),
 ("utkba2c", "yes", True, True, "otherGrounds", "overruled on other grounds by Cross v. City of Memphis, 20 S.W.3d 642 (Tenn.2000)", ""),
 ("vrqc7d5", "yes", True, True, "otherGrounds", "overruled in part on other grounds by Rosas v. State, 122 Nev. 1258", "in part and on other grounds; majority footnote"),
 ("t6gb8hd", "yes", True, True, "whole", "Whitney v. California, supra, since overruled by Brandenburg v. Ohio, 395 U. S. 444 (1969)", "stated by the Court as fact"),
 ("bhnmzjw", "yes", True, True, "part", "Insofar as it deals with that point, the Howard case is overruled.", "Howard = 66 Minn. (cited at 66 Minn. 315); overruled by the speaking court on one point"),
 ("9w8hf7h", "yes", True, True, "part", "overruled in part in State v. Adkins, 170 W.Va. 46, 289 S.E.2d 720 (1982)", ""),
 ("95g2r8m", "yes", True, True, "part", "The decision in the case of The People v. Hood, on this point, was made without due consideration, and should be overruled.", "court's own voice in its opinion; phrased 'should be overruled', on one point"),
 ("5b5zz63", "yes", True, True, "part", "overruled in part by Olson v. State, 698 P.2d 107 (Wyo.1985)", "first Olson reference, attached to Chastain"),
 ("ejtuyva", "yes", True, True, "part", "(overruling in part Rolston v. Missouri Fund Comm’rs, 120 U. S. 390 (1887))", "majority's list of overruling decisions (footnote lies within the majority part)"),
 ("wfwt3v4", "yes", True, True, "otherGrounds", "overruled on other grounds by Unah By and Through Unah v. Martin, 1984 OK 2, 676 P.2d 1366", "footnote of the majority opinion"),
 ("tka52h5", "yes", True, True, "otherGrounds", "disapproved on another ground in People v. Hammon (1997) 15 Cal.4th 1117, 1123, 1128", ""),
 ("bwkfc55", "yes", True, True, "whole", "disapproved by People v. Lucente (1987), 116 Ill. 2d 133, 144-46", "no qualification stated"),
 ("hnn6u4w", "yes", True, True, "whole", "the holding in those cases has been overruled in the case of Armstrong v. Letty, 85 Okla. 205", "X given as 49 Okla. 161 with a different Pac. cite (148 Pac. 138); name and Okla. cite fit"),
 ("seypnpu", "yes", True, True, "whole", "abrogated by Manuel v. City of Joliet", "court's own citation history while describing the district court's ruling"),
 ("qwkjte3", "yes", True, True, "part", "interest judgment overruled by Komatsu Mfg. Co. v. United States, 131 F.Supp. 949", "only the interest judgment"),
 ("gta2cx2", "yes", True, True, "otherGrounds", "abrogated on other grounds by RTP LLC v. ORIX Real Estate Capital, 827 F.3d 689", ""),
 ("yb8yy3w", "yes", True, True, "otherGrounds", "abrogated on other grounds by Hart v. Schering-Plough Corp., 253 F.3d 272, 274", ""),
 ("27k7u5p", "yes", True, True, "part", "is in conflict with today’s decision, Goss is expressly overruled", "to the extent of conflict; by the speaking decision"),
 ("9zk5w5p", "unclear", True, True, "unclear", "which had been overruled in part by Morelli v. Manpower, Inc., 226 Conn. 831", "the clause sits inside the court's report of the trial court's reasons ('The trial court determined that ...'); cannot tell whether it is the court's own gloss or the trial court's view; not repeated elsewhere in the opinion"),
 ("eak6dq9", "yes", True, True, "otherGrounds", "overruled in part, on other grounds, in Barretto v. Akau, 51 Haw. 383", "in part and on other grounds"),
 ("r484m48", "yes", True, True, "part", "disapproved by Safety National, supra, 62 Cal.4th 703", "limited: 'regarding application of section 977'"),
 ("ft8xyg7", "yes", True, True, "whole", "which was itself overruled in Oklahoma Tax Comm’n v. Texas Co., 336 U. S. 342 (1949)", "majority footnote (before the partial dissent)"),
 ("9jpba35", "yes", True, True, "part", "except the didmm in Fleming v. Page, (practically overruled in Gross v. Harrison,)", "court's own voice; hedged 'practically overruled', and of the dictum in Fleming; 'Gross' is an OCR form of Cross v. Harrison"),
 ("tw8dkcj", "yes", True, True, "otherGrounds", "disapproved on other grounds by Jolly , 301 Kan. at 322-23, 342 P.3d 935", "majority; Jolly short form with 301 Kan. / 342 P.3d 935"),
 ("bka9a45", "yes", True, True, "otherGrounds", "overruled on other grounds by Lawley v. Dep’t of Higher Educ., 36 P.3d 1239 (Colo.2001)", ""),
 ("vwgr75u", "yes", True, True, "otherGrounds", "overruled in part on other grounds by State v. Harris , 330 Conn. 91, 131, 191 A.3d 119 [2018]", "in part and on other grounds"),
]

pack = open(PACK, encoding="utf-8").read()
parts = re.split(r"^## ITEM (\S+)\s*$", pack, flags=re.M)
order = parts[1::2]
bodies = dict(zip(order, parts[2::2]))

ids = [a[0] for a in A]
assert ids == order, (len(ids), len(order), [i for i in order if i not in ids], [i for i in ids if i not in order])
for a in A:
    if a[5] and a[5] not in bodies[a[0]]:
        print("WORDS NOT IN PASSAGE:", a[0], a[5])

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for i, st, x, y, ext, w, n in A:
        f.write(json.dumps({"id": i, "stated": st, "x_ok": x, "y_ok": y, "extent": ext, "words": w, "note": n}, ensure_ascii=False) + "\n")

from collections import Counter
rows = [json.loads(l) for l in open(OUT, encoding="utf-8")]
print(len(rows), Counter(r["stated"] for r in rows))
print(b"\r" in open(OUT, "rb").read())
