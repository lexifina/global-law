import json, os, re
from collections import Counter

OUT = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\audit\recog1\answers\ans_02.jsonl"
PACK = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\audit\recog1\packs\audit_02.md"
Y, N = "yes", "no"
rows = [
 ("6jdxhzx", Y, True, True, "otherGrounds", "overruled on other grounds by Miller v. City of Red Lodge, 2003 MT 44", "court's own citation history"),
 ("r2ns9mf", Y, True, True, "whole", "Hendrix v. United States, 219 U. S. 79, both overruled in Funk v. United States, supra", "court's own statement"),
 ("q6wgpkm", Y, True, True, "whole", "which has since been overruled by this court in State v. Lewis, 109 Ariz. 466", "court's own description while stating the State's cross-appeal"),
 ("9twydhs", Y, True, True, "whole", "Carter State Bank v. Ross, 52 Okla. 642, 152 Pac. 1113, which was overruled in Egan v. First National Bank of Tulsa", ""),
 ("v6huqaj", Y, True, True, "otherGrounds", "overruled in part on other grounds by Farmers Ins. Co. v. Mowry, 350 Or 686", "in part and on other grounds"),
 ("7y237qh", Y, True, True, "part", "overruled in part, Falcone v. DeFuria, 103 N.J. 219", ""),
 ("pgb7s22", Y, True, True, "otherGrounds", "disapproved of on other grounds by Ledford v. State, 289 Ga. 70", ""),
 ("sz3xz55", Y, True, True, "part", "Besse v. Besse, 1 Kan. App. 2d 217, relied on by the trial court, was disapproved in part in Brady v. Brady", "appellate court's own note after the quoted trial-court text"),
 ("j2fqg4r", Y, True, True, "whole", "overruled by State v. Haanio", ""),
 ("gd2gwuf", Y, True, True, "part", "in so far as they are in conflict with the ruling here announced, must be deemed overruled", "speaking decision overrules Camenzind (89 Or. 158, cited earlier in the opinion) to the extent of conflict"),
 ("rp6f4jx", Y, True, True, "whole", "overruled in People v. Lee (1987) 43 Cal.3d 666, 676", "court's own citation history inside its account of defendant's argument"),
 ("2mg52vv", Y, True, True, "otherGrounds", "overruled in part on other grounds by Ramapo River Reserve Homeowners", "in part and on other grounds"),
 ("vw9rtdb", Y, True, True, "whole", "McCarver and Riceland Foods decisions that they should be overruled", "speaking court announces it overrules both; later text: 'our authority and responsibility to overrule those cases'"),
 ("2v8cn8a", Y, True, True, "otherGrounds", "disapproved on other grounds by State v. Gunby, 282 Kan. 39", ""),
 ("wwdvhjx", Y, True, True, "otherGrounds", "disapproved on other grounds in Gruenberg v. Aetna Ins. Co. (1973) 9 Cal.3d 566", ""),
 ("a5mfzm5", Y, True, True, "otherGrounds", "abrogated on other grounds by Onvoy, Inc. v. SHAL, LLC, 669 N.W.2d 344", "court's own citation history inside a parenthetical"),
 ("yaapzxh", Y, True, True, "part", "it must be regarded as retaining no vitality since the Michelin decision", "court says Hooven I (324 U.S. 652) was not expressly overruled in Michelin but has had no vitality since it; the court then also overrules it itself 'to the extent it espouses that doctrine'"),
 ("87nk9x2", Y, True, True, "whole", "United States v. Rabinowitz, 339 U. S. 56 (1950), which was overruled in turn by Chimel v. California", "footnote of the opinion of the court"),
 ("2j9k7d5", Y, True, True, "part", "To the extent Black stands for the proposition cited in Amador-Gonzalez but disavowed in Causey, it is overruled.", "Black is Black v. State, 739 S.W.2d 240 (cited earlier). Stands in Part I of Judge Davis's opinion, which three judges declined to join as dicta (one more concurred in judgment only, one dissented): lead opinion, possibly not a majority on this part"),
 ("p7h7yxt", Y, True, True, "otherGrounds", "State v. Gaskins, 284 S.C. 105, 326 S.E.2d 132 (1985) overruled on other grounds by State v. Torrence", ""),
 ("7hszecd", Y, True, True, "whole", "Collector v. Day, 11 Wall. 113, and New York ex rel. Rogers v. Graves, 299 U. S. 401, overruled in Graves v. N. Y. ex rel.", ""),
 ("5tmbbn6", Y, True, True, "part", "abrogated in other part by Black v. TIC Inv. Corp., 900 F.2d 112", "abrogated on a part other than the one relied on"),
 ("686guf8", Y, True, True, "whole", "Mark v. Mark, 697 P.2d 799 (Colo. overruled by Robbins v. A.B. Goldberg, 185 P.3d 794", "subsequent history added by the speaking court to a case the court of appeals had cited; text is garbled at the court/year"),
 ("by9ys4p", Y, True, True, "otherGrounds", "overruled in part on other grounds by Malachinski v. CIR, 268 F.3d 497", "in part and on other grounds"),
 ("u4uwae7", N, True, True, "unclear", "overruled in other regards by State v. Zimmerman, 261 Md. 11", "the court uses the word 'overruled', but the wider text shows State v. Zimmerman is the Court of Appeals' review of the same case ('The Court of Appeals, in reversing that decision'): reversal on appeal in the same litigation, not an overruling by a later decision. If the bare wording governs, this would be yes / otherGrounds"),
 ("y7hvyct", Y, True, True, "part", "the language of Brinkerhoff J. in Stevens v. Allmen, 19 Ohio St. 485, indicating a contrary rule, has been disapproved in McLain v. Simington", "a statement in X is disapproved, not X as a whole"),
 ("6cassc2", Y, True, True, "part", "was, insofar as pertinent, overruled in Milwaukee County v. White Co., 296 U. S. 268", ""),
 ("2hqxh6x", Y, True, True, "part", "receded from in part, State v. Enmund, 476 So.2d 165", ""),
 ("vrpxx48", Y, True, True, "whole", "disapproved of by Great Am. Ins. Co. v. N. Austin Mun. Util. Dist. No. 1", "court's own citation history for a case a party cited"),
 ("fahskxh", Y, True, True, "whole", "We subsequently overruled Linkletter in Griffith v. Kentucky, 479 U. S. 314 (1987)", ""),
 ("b44d45f", Y, True, True, "otherGrounds", "disapproved of on other grounds in Cross v. Pacific Gas & Elec. Co. (1964) 60 Cal.2d 690", ""),
 ("6j8wnff", Y, True, True, "part", "Anything held to the contrary in People v. Loria (supra) should be regarded as overruled.", "Loria is 10 N Y 2d 368 (cited earlier); majority opinion (Van Voorhis), overruled by this decision to the extent contrary"),
 ("gft67s6", Y, True, True, "otherGrounds", "overruled on other grounds by State v. Steinzig, 1999-NMCA-107", ""),
 ("q4q4jgn", Y, True, True, "whole", "United States v. Welton, 583 F.3d 494 (7th Cir.2009), which has been overruled by our holding in United States v. Corner", ""),
 ("rxxqn8p", Y, True, True, "whole", "Although overruled in Louisville, C., & C. R. Co. v. Letson, 2 How. 497 (1844), Deveaux was resurrected", "footnote of the opinion of the court; Deveaux is Bank of United States v. Deveaux, 5 Cranch 61; the court adds that it was later revived by Marshall"),
 ("efawfzr", Y, True, True, "whole", "State v. Robertson, 932 P.2d 1219 (Utah 1997), overruled by State v. Reyes, 2005 UT 33", "also: 'In Reyes, this court abandoned the Robertson test'"),
 ("dnrw48d", Y, True, True, "part", "overruled in part by G.M., supra, 198 N.J. at 405, 968 A.2d 698", "G.M. short form; reporter citations match Y"),
 ("5j42y48", Y, True, True, "whole", "both of which were subsequently overruled in Tomlin v. Alford, Mo.Sup., 351 S.W.2d 705", ""),
 ("avdyarp", Y, True, True, "part", "The Malloy decision overruled the long-settled doctrine of Twining v. New Jersey, 211 U. S. 78", "doctrine of Twining overruled; Malloy is Malloy v. Hogan, 378 U.S. 1 (cited earlier); footnote of the opinion of the court"),
 ("r65qfbu", Y, True, True, "whole", "Fairfield v. County of Gallatin, 100 U. S. 47, that decision was overruled", ""),
]
assert len(rows) == 40 and len({r[0] for r in rows}) == 40

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for i, s, x, y, e, w, n in rows:
        f.write(json.dumps({"id": i, "stated": s, "x_ok": x, "y_ok": y, "extent": e, "words": w, "note": n}, ensure_ascii=False) + "\n")

pack = open(PACK, encoding="utf-8").read()
ids = re.findall(r"^## ITEM (\S+)", pack, flags=re.M)
got = [json.loads(l)["id"] for l in open(OUT, encoding="utf-8")]
print(len(ids), len(got), ids == got)
print(Counter(json.loads(l)["stated"] for l in open(OUT, encoding="utf-8")))
for i, s, x, y, e, w, n in rows:
    if w and w not in pack:
        print("words not verbatim:", i, w)
