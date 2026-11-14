import json, os, re, sys

BASE = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\round5\recog"
BANNED = ["not overrul", "n't overrul", "never overrul", "not been overrul", "never been overrul", "not abrogat",
          "n't abrogat", "not been abrogat", "not disapprov", "whether", "without overruling", "rather than overrul",
          "declin", "refus", "would overrule", "should be overruled", "should overrule", "to overrule", "argu",
          "contend", "urge", "dissent", "question", "doubt"]
ALLOW_BANNED = {"r191445": "dissent", "r151169": "doubt"}


def T(i, s, e, kind, scope, conf, x, y, fl="", doc=""):
    return dict(id=i, t=True, s=s, e=e, kind=kind, scope=scope, conf=conf, x=x, y=y, fl=fl, doc=doc)


def F(i, reason, conf):
    return dict(id=i, t=False, reason=reason, conf=conf)


OV, AB, DI, RE = "overruled", "abrogated", "disapproved", "recededFrom"
ALL, OG, PU = "all", "otherGrounds", "partialUnknown"

PACKS = {
"pack_T2_019": [
 T("r192638", "Sch. Dist. of Spooner", "overruled by DeBaker, 194 Wis. 2d 104", OV, ALL, 0.95, "Spooner", "DeBaker"),
 F("r166843", "notOverruling", 0.95),
 F("r117508", "question", 0.95),
 T("r157110", "State v. Ramos, 203 N.J.Super. 197", "overruled by J.S., 222 N.J.Super. 247", OV, ALL, 0.95, "Ramos", "222 N.J.Super. 247"),
 T("r188090", "State v. Brillon, 2008 VT 35", "overruled by Vermont v. Brillon, 556 U.S. 81", OV, ALL, 0.85, "183 Vt. 475", "556 U.S. 81"),
 T("r167692", "Jennings v. State, Okl.Cr., 484 P.2d 885", "Conner v. State, Okl.Cr., 518 P.2d 1271", OV, ALL, 0.95, "Jennings", "Conner"),
 F("r108710", "argument", 0.9),
 F("r150962", "otherDecision", 0.9),
 T("r132079", "Nishi v. Hartwell, 52 Haw. 188", "i 475, 904 P.2d 489", OV, ALL, 0.95, "Nishi", "Carr"),
 F("r167851", "wrongDirection", 0.9),
 T("r138932", "State v. Valentine, 260 Kan. 431", "disapproved by State v. Brice, 276 Kan. 758", DI, PU, 0.6, "Valentine", "Brice"),
 T("r166091", "Jones v. Gwynne, 312 N.C. 393", "receded from by Hawkins v. Hawkins, 331 N.C. 743", RE, ALL, 0.95, "Gwynne", "Hawkins"),
 T("r190268", "Barlow v. Daniels, 25 W. Va. 512", "Richmond v. Henderson, 48 W. Va. 389", OV, ALL, 0.95, "Barlow", "Henderson"),
 T("r80057", "Kilaab Al Ghashiyah", "disapproved by Charles v. Verhagen, 348 F.3d 601", DI, ALL, 0.8, "Kilaab", "Verhagen"),
 F("r185326", "cannotTell", 0.55),
 F("r161640", "otherDecision", 0.95),
 T("r4248", "Ex parte Hicks, 727 So.2d 23", "overruled by Ex parte Henry, 770 So.2d 76", OV, ALL, 0.9, "Hicks", "Henry"),
 T("r4256", "Ex parte Hicks, 727 So.2d 23", "overruled by Ex parte Henry, 770 So.2d 76", OV, ALL, 0.9, "Hicks", "Henry"),
 T("r133371", "People v. Knowles (1979), 70 Ill. App. 3d 30", "People v. Cox (1980), 82 Ill. 2d 268", OV, PU, 0.9, "Knowles", "Cox"),
 T("r176448", "Medlin v. Allied Inv. Co.", "abrogated by Camper v. Minor, 915 S.W.2d 437", AB, ALL, 0.95, "Medlin", "Camper"),
 F("r110342", "quotation", 0.95),
 T("r191445", "513 S.E.2d 170", "abrogated by Aikens , 208 W.Va. 486", AB, ALL, 0.85, "513 S.E.2d 170", "Aikens"),
 T("r186079", "Johnson v. State, 509 S.W.2d 322", "Ex parte Charlesworth, 600 S.W.2d 316", DI, PU, 0.9, "509 S.W.2d 322", "Charlesworth"),
 T("r186094", "Johnson v. State, 509 S.W.2d 322", "worth, 600 S.W.2d 316", DI, PU, 0.65, "509 S.W.2d 322", "600 S.W.2d 316"),
 F("r133420", "argument", 0.9),
 T("r167090", "Cementech, Inc. v. Fairlawn, 160 Ohio App.3d 450", "overruled by Cementech, Inc. v. Fairlawn, 109 Ohio St.3d 475", OV, ALL, 0.9, "160 Ohio App.3d 450", "109 Ohio St.3d 475"),
 T("r115415", "Holloway, supra, 47 Cal.App.4th 1757", "People v. Fuhrman (1997) 16 Cal.4th 930", DI, OG, 0.95, "Holloway", "Fuhrman"),
 T("r3793", "Sullivan v. Sullivan, 215 Ala; 627", "overruled in Gabbert v. Gabbert, 217 Ala. 599", OV, ALL, 0.85, "Sullivan", "Gabbert"),
 T("r3800", "Sullivan v. Sullivan, 215 Ala. 627, 111 So. 911, overruled", "overruled in Gabbert v. Gabbert, 217 Ala. 599", OV, ALL, 0.7, "Sullivan", "Gabbert"),
 T("r3815", "Sullivan v. Sullivan, 215 Ala. 627, 111 So. 911, overruled", "overruled in Gabbert v. Gabbert, 217 Ala. 599", OV, ALL, 0.85, "Sullivan", "Gabbert"),
 T("r67734", "Jones v. Diamond, 636 F.2d 1364", "790 F.2d 1174", OV, ALL, 0.9, "Diamond", "790 F.2d 1174"),
 T("r67864", "Jones v. Diamond, 636 F.2d 1364", "790 F.2d 1174", OV, ALL, 0.9, "Diamond", "790 F.2d 1174"),
 F("r176339", "quotation", 0.65),
 T("r190539", "State v. Clawson, 165 W.Va. 588", "receded from by Wilt v. Buracker, 191 W.Va. 39", RE, ALL, 0.95, "Clawson", "Buracker"),
 F("r150978", "cannotTell", 0.8),
 F("r150986", "cannotTell", 0.8),
 T("r155733", "104 Nev. 51, 752 P.2d 225 (1988), overruled", "overruled by Hubbard v. State, 112 Nev. 946", OV, ALL, 0.9, "104 Nev. 51", "Hubbard"),
 T("r108316", "People v. North Beach Bonding Co. (1974)", "disapproved by Safety National, supra, 62 Cal.4th 703", DI, PU, 0.9, "North Beach Bonding", "Safety National", "regarding application of section 977"),
 T("r153595", "Hacker v. City of Potosi, (Mo. App.) 340 S.W.2d 166", "Hacker v. City of Potosi, 351 S.W.2d 760", OV, ALL, 0.95, "340 S.W.2d 166", "351 S.W.2d 760"),
 F("r167501", "otherDecision", 0.85),
 T("r111344", "People v. Adams (1986) 186 Cal.App.3d 75", "disapproved by People v. Gammage (1992) 2 Cal.4th 693", DI, ALL, 0.9, "Adams", "Gammage"),
 T("r132869", "Corwith v. Hyde Park, 14 Ill. App. 635", "Hyde Park v. Corwith, 122 Ill. 441", OV, PU, 0.6, "14 Ill. App. 635", "122 Ill. 441"),
 T("r154380", "Rouse v. Anaconda-Deer Lodge County (1991), 250 Mont. 1", "overruled by Stratemeyer v. Lincoln County (1996), 276 Mont. 67", OV, ALL, 0.9, "Rouse", "Stratemeyer"),
 T("r168202", "Special Indemnity Fund v. Maples, 1998 OK CIV APP 157", "Samman v. Multiple Injury Trust Fund, 2001 OK 71", OV, PU, 0.9, "Maples", "Samman"),
 T("r162513", "Peeples v State of New York, 179 Misc 272", "v State of New York, 42 NY2d 289", DI, PU, 0.85, "Peeples", "42 NY2d 289"),
 T("r6340", "Knight v. Mewszel, 3 Ariz.App. 295", "overruled by Walker v. Dallas, 146 Ariz. 440", OV, ALL, 0.95, "Mewszel", "Walker v. Dallas"),
 T("r166446", "260 N.W.2d 328, 332 (N.D.1977)", "767 N.W.2d 869", OV, PU, 0.9, "260 N.W.2d 328", "Zwicke"),
 T("r151215", "Marcum v. Mississippi Valley Gas Company and Mermelstein", "overruled in Whigham v. State, 611 So.2d 988", OV, ALL, 0.85, "587 So.2d 223", "Whigham"),
 T("r131602", "State v. Haanio, 94 Hawai", "314 P.3d 120", OV, ALL, 0.95, "Haanio", "Flores"),
],
"pack_T2_020": [
 F("r151235", "cannotTell", 0.55),
 T("r167417", "State ex rel. Flynn v. Cuyahoga Bd. of Elections", "State ex rel. Schenck v. Shattuck (1982), 1 Ohio St.3d 272", OV, ALL, 0.95, "Flynn", "Schenck"),
 F("r3816", "notOverruling", 0.97),
 T("r4332", "Sisters of the Visitation v. Cochran Plastering Co., 775 So.2d 759", "Citizens Bank v. Alafabco, Inc., 539 U.S. 52", AB, ALL, 0.8, "Sisters of the Visitation", "Alafabco"),
 T("r4356", "Sisters of the Visitation v. Cochran Plastering Co., 775 So.2d 759", "Citizens Bank v. Alafabco, Inc., 539 U.S. 52", OV, ALL, 0.95, "Sisters of the Visitation", "Alafabco"),
 T("r174018", "Vodopich v. Trojan Mining Co.", "Chittenden v. Jarvis, 68 S. D. 5", OV, ALL, 0.9, "Vodopich", "Chittenden"),
 F("r175454", "notOverruling", 0.97),
 T("r160329", "State v. Ulibarri, 96 N.M. 511", "overruled by State v. Hosteen, 122 N.M. 228", OV, ALL, 0.95, "Ulibarri", "Hosteen"),
 T("r174090", "G.H. Lindekugel", "447 N.W.2d 339", OV, ALL, 0.95, "Lindekugel", "Candee"),
 T("r132786", "State v. Woolery, 116 Idaho 368", "overruled by Wulff 157 Idaho 416", OV, ALL, 0.95, "Woolery", "Wulff"),
 T("r135648", "Lyles v. State, 576 N.E.2d 1344", "abrogated by Peterson v. State, 650 N.E.2d 339", AB, ALL, 0.9, "Lyles", "Peterson"),
 T("r173538", "State v. Gonzales, 360 S.C. 263", "overruled by State v. Gentry, 363 S.C. 93", OV, ALL, 0.95, "Gonzales", "Gentry"),
 T("r192567", "Radlein v. Industrial Fire", "Nicholson v. Home Insurance Co., 137 Wis. 2d 581", DI, PU, 0.85, "Radlein", "Nicholson"),
 F("r110083", "otherDecision", 0.95),
 T("r120344", "Hoskins v. State (Hoskins I), 14 A.3d 554", "overruled by Brooks v. State, 40 A.3d 346", OV, ALL, 0.95, "14 A.3d 554", "Brooks"),
 T("r120349", "Hoskins v. State, 14 A.3d 554", "overruled by Brooks v. State, 40 A.3d 346", OV, ALL, 0.95, "14 A.3d 554", "Brooks"),
 T("r173489", "Clark v. Ross, 284 S.C. 543", "abrogated by Sherer v. James, 290 S.C. 404", AB, ALL, 0.95, "Clark v. Ross", "Sherer"),
 T("r173524", "Clark v. Ross, 284 S.C. 543", "abrogated by Sherer v. James, 290 S.C. 404", AB, ALL, 0.95, "Clark v. Ross", "Sherer"),
 T("r153605", "State v. Jones, 12 Mo.App. 93", "State v. Dreher, 137 Mo. 11", OV, ALL, 0.95, "12 Mo.App. 93", "Dreher"),
 T("r161949", "State v. Torres, 1998-NMSC-052", "136 N.M. 309", OV, PU, 0.95, "Torres", "Alvarez-Lopez"),
 T("r176472", "Bone v. Saturn Corp., 148 S.W.3d 69", "Britt, 211 S.W.3d 706", OV, ALL, 0.95, "Bone v. Saturn", "Britt"),
 F("r135058", "negation", 0.97),
 T("r6986", "Anderson v. Coulter, 16 Ariz.App. 27", "Anderson v. Coulter, 108 Ariz. 388", OV, OG, 0.9, "16 Ariz.App. 27", "108 Ariz. 388"),
 T("r115127", "Magee v. Superior Court (1973) 34 Cal.App.3d 201", "People v. Norris (1985) 40 Cal.3d 51", DI, PU, 0.95, "Magee", "Norris"),
 T("r134058", "Dillon v. Nathan (1956), 10 Ill. App. 2d 289", "Hamm (1978), 58 Ill. App. 3d 177", OV, ALL, 0.9, "Dillon", "Hamm"),
 F("r149588", "argument", 0.95),
 F("r113370", "otherDecision", 0.95),
 T("r153558", "State ex rel. Tredway v. Lusk, 18 Mo. 333", "Thomas, 102 Mo. 85", OV, ALL, 0.95, "Tredway", "Thomas"),
 T("r132477", "Dunbar v. United Steelworkers, 100 Idaho 523", "Sterling v. Bloom, 111 Idaho 211", OV, ALL, 0.85, "Dunbar", "Sterling"),
 T("r135747", "Clark v. Estate of Slovens, 687 N.E.2d 246", "Richie, 707 N.E.2d 992", AB, ALL, 0.9, "687 N.E.2d 246", "Richie"),
 F("r154120", "otherDecision", 0.95),
 T("r4119", "Sloss-Sheffield Steel & Iron Co. v. Wilkes, 236 Ala. 173", "overruled by Henderson v. Wade Sand & Gravel Co., 388 So.2d 900", OV, ALL, 0.95, "236 Ala. 173", "Henderson"),
 F("r185158", "notOverruling", 0.97),
 T("r168029", "White v. Saling, 185 Okla. 46", "Johnson v. Whelan, 186 Okla. 511", OV, ALL, 0.85, "Saling", "Whelan"),
 T("r135819", "Vinson v. State, 735 N.E.2d 828", "disapproved of by Long, 743 N.E.2d 253", DI, ALL, 0.9, "Vinson", "743 N.E.2d 253"),
 F("r114214", "argument", 0.95),
 T("r7778", "Scott v. McCuen, 289 Ark. 41", "overruled by Stilley v. Priest, 341 Ark. 329", OV, ALL, 0.95, "Scott v. McCuen", "Priest"),
 F("r153776", "notOverruling", 0.97),
 T("r108329", "People v. Cervantes (2017) 9 Cal.App.5th 569", "4 Cal.5th 299", DI, ALL, 0.9, "Cervantes", "4 Cal.5th 299"),
 T("r154208", "State v. Frates (1972), 160 Mont. 431", "overruled by State v. Cameron (1992), 255 Mont. 14", OV, ALL, 0.95, "Frates", "Cameron"),
 T("r3779", "Stewart v. Court of County Commissioners of Hale County, 82 Ala. 209", "Elyton Land Co., 114 Ala. 70", OV, ALL, 0.9, "Stewart", "Elyton"),
 T("r159764", "Kruzdlo v. Kruzdlo, 251 N.J.Super. 70", "it was disapproved. Kay, supra, 405 N.J.Super", DI, PU, 0.6, "Kruzdlo", "Kay"),
 T("r192801", "State v. Santos, 136 Wis. 2d 528", "abrogated by Padilla, 559 U.S. 356", AB, ALL, 0.95, "Santos", "Padilla"),
 T("r187470", "State v. Tunzi, 2001 UT App 224", "overruled by State v. Tunzi, 2002 UT 119, 63 P.3d 70", OV, ALL, 0.95, "31 P.3d 588", "63 P.3d 70"),
 T("r190538", "State v. Casdorph, 159 W.Va. 909", "receded from by State v. Persinger, 169 W.Va. 121", RE, ALL, 0.95, "Casdorph", "Persinger"),
 F("r169709", "otherDecision", 0.9),
 F("r165123", "otherDecision", 0.9),
 T("r58608", "United States v. Chester, 628 F.3d 673", "by Bruen, 597 U.S. 1", AB, ALL, 0.95, "Chester", "Bruen"),
 F("r153446", "negation", 0.97),
],
"pack_T2_021": [
 T("r7850", "Philyaw v. State, 288 Ark. 237", "overruled by Oliver v. State, 323 Ark. 743", OV, PU, 0.95, "288 Ark. 237", "Oliver"),
 F("r192571", "argument", 0.95),
 T("r174098", "Egan v. Dotson, 36 S.D. 459", "Hackworth v. Larson, 83 S.D. 674", OV, PU, 0.9, "Egan", "Hackworth"),
 T("r174338", "State v. King, 383 N.W.2d 854", "abrogated by State v. Chant, 2014 S.D. 77", AB, ALL, 0.95, "State v. King", "Chant"),
 T("r135952", "Seidner v. Dill, 137 Ind.App. 177", "overruled by Puckett v. Miller, 178 Ind. App. 174", OV, ALL, 0.95, "Seidner", "Puckett"),
 T("r151741", "Harris v. State, 704 So.2d 1286", "abrogated by Jackson v. State, 732 So.2d 187", AB, ALL, 0.9, "704 So.2d 1286", "732 So.2d 187"),
 T("r136611", "Board, etc. v. State, ex rel., 147 Ind. 476, was overruled", "155 Ind. 604", OV, OG, 0.9, "147 Ind. 476", "155 Ind. 604"),
 T("r151169", "Johnson v. State, 186 Miss. 405", "Mahfouz v. State, 303 So.2d 461", OV, PU, 0.85, "186 Miss. 405", "Mahfouz", "", "ownership must be proven as averred"),
 T("r176601", "State v. Denton, 938 S.W.2d 373", "State v. Watkins, 362 S.W.3d 530", OV, ALL, 0.95, "Denton", "Watkins"),
 F("r186448", "notOverruling", 0.97),
 F("r172344", "wrongDirection", 0.9),
 T("r190949", "Soliva v. Shand", "177 W.Va. 734", OV, PU, 0.9, "Soliva", "McMahon"),
 T("r142149", "West Orleans Beach Corporation v. Martinez, 180 La. 31", "Reeves v. Globe Indemnity Co., 185 La. 42", OV, ALL, 0.95, "West Orleans", "Reeves"),
 T("r155508", "118 Nev. 488, 50 P.3d 546", "by Garvin, 118 Nev. 749", DI, PU, 0.9, "118 Nev. 488", "Garvin"),
 F("r166963", "quotation", 0.9),
 T("r142332", "Soulie, 29 La.Ann. 161, and Succession", "Succession of Farmer, 32 La. Ann. 1037", OV, ALL, 0.8, "Soulie", "Farmer"),
 T("r150062", "Hallada v. Great Northern Ry. Co., 244 Minn. 81", "262 N.W.2d 377", OV, ALL, 0.9, "Hallada", "262 N.W.2d 377"),
 T("r129781", "U. S. Security Warehouse v. Tasty Sandwich Co.", "Union Camp Corp., 230 Ga. 8", DI, ALL, 0.95, "Tasty Sandwich", "Union Camp"),
 T("r131239", "Payne v. State, 285 Ga. 137", "overruled by Reed v. State, 291 Ga. 10", OV, ALL, 0.95, "285 Ga. 137", "Reed"),
 T("r114880", "Carlos v. Superior Court (1983) 35 Cal.3d 131", "overruled by People v. Anderson (1987) 43 Cal.3d 1104", OV, ALL, 0.95, "Carlos", "43 Cal.3d 1104"),
 T("r114885", "Carlos v. Superior Court (1983) 35 Cal.3d 131", "overruled in People v. Anderson (1987) 43 Cal.3d 1104", OV, ALL, 0.95, "Carlos", "43 Cal.3d 1104"),
 T("r114919", "Carlos v. Superior Court (1983) 35 Cal.3d 131", "overruled by People v. Anderson (1987) 43 Cal.3d 1104", OV, ALL, 0.95, "Carlos", "43 Cal.3d 1104"),
 T("r124174", "Border Brokerage Co. Inc. v. United States, 60 Cust. Ct. 487", "Green Giant Co. v. United States, 61 CCPA 46", DI, PU, 0.9, "Border Brokerage", "Green Giant"),
 T("r151553", "King v. American RV Centers, Inc., 862 So.2d 558", "Wilner v. White, 929 So.2d 315", OV, ALL, 0.9, "American RV", "Wilner"),
 T("r136580", "Burns v. Anderson, 68 Ind. 202", "overruled in Shaw v. Rigby, 84 Ind. 375", OV, ALL, 0.9, "Burns v. Anderson", "Rigby"),
 T("r110211", "Bassett v. Johnson (1949) 94 Cal.App.2d 807", "disapproved in People v. Benford, supra, 53 Cal.2d 1", DI, ALL, 0.9, "Bassett", "Benford"),
 T("r151912", "Wirtz v. Switzer, 586 So.2d 775", "964 So.2d 1100", AB, ALL, 0.95, "Wirtz", "Upchurch"),
 T("r160526", "Corn v. New Mexico Educators Federal Credit Union, 119 N.M. 199", "overruled by Trujillo v. City of Albuquerque, 1998-NMSC-031", OV, PU, 0.9, "Corn v. New Mexico", "Trujillo"),
 T("r115901", "Catchpole v. Brannon (1995) 36 Cal.App.4th 237", "disapproved in People v. Freeman (2010) 47 Cal.4th 993", DI, ALL, 0.9, "Catchpole", "Freeman"),
 T("r145398", "Fairbairn v. Planning Bd. of Barnstable, 5 Mass. App. Ct. 171", "374 Mass. 343", DI, OG, 0.95, "Fairbairn", "Loring Hills"),
 T("r117385", "Pikes Peak Golf Club, Inc. v. Kuiper, 169 Colo. 309", "overruled by Giffen v. State, 690 P.2d 1244", OV, ALL, 0.95, "Pikes Peak", "Giffen"),
 F("r107700", "notMajority", 0.7),
 F("r107738", "notMajority", 0.7),
 T("r144053", "Hartlove v. Maryland School for the Blind, 111 Md.App. 310", "overruled by Kann, supra, 344 Md. at 709, 690 A.2d 509", OV, ALL, 0.9, "Hartlove", "Kann"),
 T("r115504", "People v. Lomeli (1993) 19 Cal.App.4th 649", "disapproved in People v. Hernandez (2004) 33 Cal.4th 1040", DI, ALL, 0.9, "Lomeli", "Hernandez"),
 T("r192736", "Sporleder v. Hermes, 162 Wis. 2d 1002", "v. Knott, 193 Wis. 2d 649", OV, PU, 0.85, "Sporleder", "193 Wis. 2d 649"),
 T("r128440", "In re Estate of Greenberg, 390 So.2d 40", "Zrillic, 563 So.2d 64", AB, ALL, 0.95, "Greenberg", "Zrillic"),
 T("r192451", "Blue Cross v. Fireman", "overruled by Schulte, 176 Wis. 2d 622", OV, ALL, 0.9, "140 Wis. 2d 544", "Schulte"),
 T("r80736", "Arnow v. NRC, 868 F.2d 223", "overruled by Builders Bank v. FDIC, 846 F.3d 272", OV, ALL, 0.95, "Arnow", "Builders Bank"),
 F("r3808", "otherDecision", 0.9),
 T("r172228", "Erie County v. Erie County Commissioners, 113 Pa. 368", "Sewickley v. Sholes, 118 Pa. 165", OV, ALL, 0.9, "113 Pa. 368", "Sholes"),
 F("r114409", "otherDecision", 0.95),
 T("r80693", "Smith v. Potter, 445 F.3d", "Hill v. Tangherlini, 724 F.3d 965", OV, OG, 0.9, "Smith v. Potter", "Tangherlini"),
 T("r80753", "Smith\xa0v.\xa0Potter,\xa0445\xa0F.3d", "Hill\xa0v.\xa0Tangherlini,\xa0724\xa0F.3d\xa0965", OV, OG, 0.9, "Potter", "Tangherlini"),
 T("r150224", "State v. Smith, 669 N.W.2d 19", "overruled by State v. Leake, 699 N.W.2d 312", OV, ALL, 0.95, "669 N.W.2d 19", "Leake"),
 T("r4441", "Foster v. Greer & Sons, Inc., 446 So.2d 605", "overruled by Ex parte Andrews, 520 So.2d 507", OV, PU, 0.95, "Foster v. Greer", "Andrews"),
 T("r187730", "Samms v. Eccles , 11 Utah 2d 289", "abrogated by Johnson v. Rogers , 763 P.2d 771", AB, ALL, 0.95, "Samms", "Rogers"),
 T("r192410", "Olsen v. Copeland, 90 Wis. 2d 483", "Sorensen v. Jarvis, 119 Wis. 2d 627", OV, ALL, 0.95, "Olsen", "Sorensen"),
 T("r108725", "People v. Gibbs, 12 Cal.App.3d 526", "People v. Timmons, 4 Cal.3d 411", DI, PU, 0.95, "Gibbs", "Timmons"),
],
}


def parse_pack(path):
    txt = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    items = []
    for block in re.split(r"(?m)^### ITEM ", txt)[1:]:
        iid = block.split("\n", 1)[0].strip()
        w = block.split("\nWINDOW:\n", 1)[1].split("\nNOTE AT:", 1)[0]
        items.append((iid, w))
    return items


ok = True
for pack, answers in PACKS.items():
    items = parse_pack(os.path.join(BASE, "packs", pack + ".md"))
    ids = [i for i, _ in items]
    if ids != [a["id"] for a in answers]:
        ok = False
        print(pack, "ORDER/ID MISMATCH", [x for x in ids if x not in [a["id"] for a in answers]],
              [a["id"] for a in answers if a["id"] not in ids])
        continue
    lines = []
    ntrue = 0
    for (iid, w), a in zip(items, answers):
        if not a["t"]:
            lines.append(dict(id=iid, states=False, reason=a["reason"], kind="", scope="", field_limit="",
                              doctrine="", quote="", confidence=a["conf"]))
            continue
        si = w.find(a["s"])
        ei = w.find(a["e"], si) if si >= 0 else -1
        if si < 0 or ei < 0:
            ok = False
            print(pack, iid, "ANCHOR NOT FOUND", si, ei)
            continue
        q = w[si:ei + len(a["e"])]
        probs = []
        if q not in w:
            probs.append("not substring")
        if len(q) > 400:
            probs.append("len %d" % len(q))
        if not re.search(r"overrul|abrogat|disapprov|reced", q):
            probs.append("no overruling word")
        if a["x"] not in q:
            probs.append("no X")
        if a["y"] not in q:
            probs.append("no Y")
        for b in BANNED:
            if b in q.lower() and ALLOW_BANNED.get(iid) != b:
                probs.append("banned:" + b)
        if a["fl"] and a["fl"] not in w:
            probs.append("field_limit not in window")
        if probs:
            ok = False
            print(pack, iid, probs, repr(q))
        ntrue += 1
        lines.append(dict(id=iid, states=True, kind=a["kind"], scope=a["scope"], field_limit=a["fl"],
                          doctrine=a["doc"], quote=q, confidence=a["conf"]))
    out = os.path.join(BASE, "ans", "ans_" + pack + ".jsonl")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for l in lines:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")
    # re-read and verify
    back = [json.loads(x) for x in open(out, encoding="utf-8").read().split("\n") if x]
    assert [b["id"] for b in back] == ids, pack
    wmap = dict(items)
    for b in back:
        if b["states"]:
            assert b["quote"] in wmap[b["id"]] and len(b["quote"]) <= 400, b["id"]
    print(pack, "items", len(back), "true", sum(1 for b in back if b["states"]), "maxlen",
          max([len(b["quote"]) for b in back]))
print("OK" if ok else "PROBLEMS")
