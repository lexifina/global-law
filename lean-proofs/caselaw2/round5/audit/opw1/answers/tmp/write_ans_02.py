# -*- coding: utf-8 -*-
import json, re, io, os
from collections import Counter

base = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\audit\opw1"
pack = io.open(os.path.join(base, "packs", "audit_02.md"), encoding="utf-8").read()
ids = re.findall(r"^## ITEM (\S+)", pack, flags=re.M)
Y, N = "yes", "no"
A = [
("m997xmz", Y, True, True, "part", "the dictum contained in Gittings v. Baltimore, 95 Md. 419 at page 424, 52 A. 937, we decline to follow it", "own court's dictum, insofar as inconsistent with this opinion; wording is 'decline to follow', taken as a partial disapproval (borderline)"),
("v2czqg7", Y, True, True, "part", "To the extent that Norton and Zahner could be read to suggest ... they are no longer good law", "court's own footnote; declared here, with the Marketable Title Act as a supporting reason"),
("8v8dy9g", N, True, False, "unclear", "The enactment of Code § 37.2-905.1 altered the applicable standard. Consequently, Shelton is no longer good law.", "displaced by a statutory amendment, not by a decision"),
("pukcyn2", Y, True, True, "part", "We reject the holding in Hovland that reasonableness is a secondary issue to the legal duty to attend an IME.", "supreme court rejects a holding of the state court of appeals"),
("vkuuq5k", Y, True, True, "part", "the Dowell case cited by appellant, which must be deemed overruled so far as it is inconsistent with the later cases", "court resolves the conflict here and deems Dowell overruled in part; arguably the overruling is attributed to the later cases"),
("p36vu4n", Y, True, True, "part", "To this extent we cannot follow the contrary implications of the prior cases, including Hoyt v. Florida.", "with 'it is no longer tenable to hold'"),
("ua883tc", Y, True, True, "part", "State v. Graves, supra, are in conflict with this view, they are expressly rejected", "expressions rejected insofar as in conflict"),
("v3e38jh", Y, True, True, "part", "we reject the dicta in Tobia that placed drug abusers in the same category as the elderly or mentally ill", "dicta of own earlier decision rejected"),
("bqmfznk", Y, True, True, "whole", "Citing Henning v. Insurance Co., 47 Mo. 425, which, as above shown, is no longer the law in Missouri.", "wider text: Henning not expressly overruled in Baile, not followed since; the express declaration is made here, though it rests on the earlier Baile line (y_ok arguable)"),
("t2qmbjc", Y, True, True, "whole", "Crooker v. California, 357 U. S. 433 (1958) and Cicenia v. Lagay, 357 U. S. 504 (1958) are not to be followed", "'In accordance with our holdings today and in Escobedo'; footnote of the opinion of the court"),
("hm42ubs", N, True, False, "unclear", "Orr, however, is no longer authoritative on that issue. As changed in 1980, Iowa Rule of Civil Procedure 237(c) allows", "displaced by a rule amendment, not by a decision"),
("5kmam6j", Y, True, False, "part", "overruled by Demain v. Bruce McLaughlin Logging, 132 Idaho 782, 785, 979 P.2d 655, 658 (1999)", "court reports that the earlier Demain decision overruled Bowman ('To the extent Bowman is inconsistent'); not done by this decision"),
("5v2haqg", Y, True, True, "part", "Lesser controls and the quoted language in Shellabarger is rejected.", "quoted language of Hilliard v. Shellabarger rejected"),
("4dunv4s", Y, True, True, "part", "Any other opinions that similarly applied the Moore test are also overruled to the extent they did the same", "Branch is in the list of located cases that applied the Moore test; 'also' shows the listed cases are overruled to that extent (footnote)"),
("pzbjpzw", Y, True, False, "whole", "In light of the Supreme Court's more recent discussion, Glover is no longer good law", "loss of authority attributed to the U.S. Supreme Court's Daimler decision, recognised here; if the court's own first declaration counts as 'this decision', y_ok would be true"),
("w54r2tx", N, True, False, "unclear", "we noted that this section overruled our Kintzinger holding", "displaced by statute (Iowa Code section 633.449), not by a decision"),
("x268u74", Y, True, True, "part", "the sweeping language of J. M. Davis Company can no longer be considered good authority outside the area of “public” contracts", "declared here on the strength of later cases that had only limited it"),
("unxppza", N, True, False, "unclear", "Under our interpretation of legislative action, Romp and Stroh are no longer good law.", "superseded by the 2007 and 2012 statutory amendments ('now superseded precedent'), not by a decision"),
("g6fhjzt", Y, True, True, "part", "(and any dicta in Framingham) suggest that a lack of affirmative support inevitably constitutes a violation of § 7 (b), they rest on an error of law, and we do not follow them", "own dicta said to rest on an error of law"),
("5pum2kk", Y, True, True, "part", "We reconsider that opinion and overrule its holding that amortization provisions are per se unconstitutional.", "overrules the named holding of Ailes"),
("fvsbyj8", Y, True, True, "whole", "Crooker v. California, 357 U. S. 433 (1958) and Cicenia v. Lagay, 357 U. S. 504 (1958) are not to be followed", "'In accordance with our holdings today and in Escobedo'; footnote of the opinion of the court"),
("pyahnw4", Y, True, True, "part", "We accordingly disavow the dicta in paragraph 17 of Paries and the dicta in Tindley that cites it.", "dicta disavowed (footnote of the opinion)"),
("sstfh2d", Y, True, True, "part", "To the extent that we have equated the summary judgment and directed verdict standards ... we disavow those misleading statements", "Cameron cited as an example of the disavowed statements"),
("rt3bhkr", Y, True, True, "part", "Any contrary intimations contained in the cases of Spellacy v. Young, 44 Cal. App. 174 [186 Pac. 368] ... should not be followed", "supreme court disapproves contrary intimations of a Court of Appeal decision"),
("87eupq4", Y, True, True, "part", "if it is so understood as to prevent this interpretation of § 18, to that extent it should not be followed", "low confidence: conditional on a reading and coupled with a distinguishing reason ('was not considering a situation such as is now in hand'); could be seen as mere limiting"),
("qn8rht5", Y, True, True, "part", "is read as inconsistent with this holding, we expressly reject it", "en banc court rejects its own panel decision insofar as inconsistent"),
("yh3jdkz", Y, True, True, "whole", "We therefore reject the Ninth District’s reasoning in Fair Hous.", "supreme court disagrees with and rejects the reasoning of a state court of appeals decision"),
("39gq229", N, True, False, "unclear", "Under our interpretation of legislative action, Romp and Stroh are no longer good law.", "superseded by the 2007 and 2012 statutory amendments ('now superseded precedent'), not by a decision"),
("jj5svkc", Y, True, True, "part", "to the extent that Jones may be at odds with the conclusion reached here, it is expressly overruled", ""),
("yk2q44e", N, True, False, "unclear", "declare a rule contrary to our existing statute we feel compelled to hold that these decisions are no longer controlling upon us", "close: the majority holds the old Supreme Court decisions no longer controlling because later statutes (lien statute of 1813 and re-enactments) displaced their rule; 'squarely overrules' is only the dissent's description"),
("3ujardk", Y, True, False, "whole", "Holder is no longer the law in Idaho", "wider text: 'Holder was recently overruled. Humpherys, 134 Idaho at 659' - done by the earlier Humpherys decision, not by this one"),
("zd34qj8", Y, True, True, "part", "is obiter dictum. To that extent such cases are disapproved.", "Richland School Tp. v. Overmyer is one of 'these cases'"),
("8gdrdjv", Y, True, True, "part", "We disavow any contrary meaning in the dicta Lane quotes from Burcina.", "disavowal of a possible meaning of own dicta; court otherwise treats Burcina as consistent (borderline)"),
("tryhc97", Y, True, True, "part", "To the extent that the Miller case may be construed as declaring unlawful the picketing of a business by non-employees, it is no longer authoritative.", "declared in the court's own voice here; appellants attributed it to the earlier Blanford and Deena Artware cases (y_ok arguable)"),
("tz6v57d", Y, True, True, "part", "State v. Ford, 240 N.J.Super. 44, 48-49, 572 A.2d 640 (App.Div.1990), we reject that notion", "supreme court rejects a notion intimated by Appellate Division decisions"),
]
assert [a[0] for a in A] == ids, (len(A), len(ids))
for a in A:
    for frag in a[5].split(" ... "):
        if frag and frag not in pack:
            print("WORDS NOT IN PACK:", a[0], "|", frag)
out = os.path.join(base, "answers", "ans_02.jsonl")
with io.open(out, "w", encoding="utf-8", newline="\n") as f:
    for i, s, x, y, e, w, n in A:
        f.write(json.dumps({"id": i, "stated": s, "x_ok": x, "y_ok": y, "extent": e, "words": w, "note": n}, ensure_ascii=False) + "\n")
rows = [json.loads(l) for l in io.open(out, encoding="utf-8")]
print(len(rows), Counter(r["stated"] for r in rows))
