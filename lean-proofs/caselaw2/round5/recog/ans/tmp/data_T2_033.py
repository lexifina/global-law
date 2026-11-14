# -*- coding: utf-8 -*-
P = "partialUnknown"
O = "otherGrounds"
OV = "overruled"
AB = "abrogated"
DI = "disapproved"
RE = "recededFrom"


def T(i, kind, scope, qs, qe, conf=0.9, fl="", doc=""):
    return (i, True, kind, scope, fl, doc, qs, qe, conf)


def F(i, reason, conf=0.9):
    return (i, False, reason, conf)


A = [
    T("r78430", OV, O, "Holmes v. United States Bd. of Parole, 541 F.2d 1243", "Solomon v. Benson, 563 F.2d 339", 0.85),
    T("r157526", OV, P, "Kleinke v. City of Ocean City, 163 N.J.Super. 424", "Sharra, supra, 199 N.J.Super. 535"),
    T("r158958", OV, P, "Kleinke v. City of Ocean City, 163 N.J.Super. 424", "Sharra v. City of Atlantic City, 199 N.J.Super. 535"),
    T("r7716", OV, P, "Jones, 274 Ark. 379", "George v. State, 306 Ark. 360", 0.85),
    T("r149482", OV, P, "People v. Gahan , 456 Mich. 264", "People v. McKinley , 496 Mich. 410", 0.85),
    T("r119258", OV, P, "State v. Jones, 180 Conn. 443", "State v. Powell, 186 Conn. 547"),
    T("r115493", OV, P, "People v. McDonald (1984) 37 Cal.3d 351", "People v. Mendoza (2000) 23 Cal.4th 896"),
    T("r136849", OV, O, "Johnson v. St. Vincent Hosp., 273 Ind. 374", "In re Stephens, 867 N.E.2d 148", 0.85),
    T("r110773", DI, O, "Rosner v. Peninsula Hospital District (1964) 224 Cal.App.2d 115", "King v. Meese (1987) 43 Cal.3d 1217", 0.85),
    T("r7343", OV, P, "Stone v. Ariz. Highway Comm", "Paroles, 115 Ariz. 260"),
    T("r7403", OV, P, "Stone v. Arizona Highway Commission, that", "Paroles, 115 Ariz. 260"),
    T("r113164", DI, P, "Clemente v. State of California (1980) 101 Cal.App.3d 374", "(1983) 34 Cal.3d 18"),
    T("r138328", DI, P, "Besse v. Besse, 1 Kan. App. 2d 217", "Brady v. Brady, 225 Kan. 485"),
    T("r153928", OV, O, "Adams ex rel. Adams v. Children", "376 S.W.3d 633", 0.85),
    F("r153443", "notOverruling", 0.9),
    T("r27571", OV, P, "Fla. ex rel. Att", "132 S.Ct. 2566", 0.85),
    T("r131042", OV, P, "Nelson v. State, 233 Ga. App. 385", "Curtis v. State, 275 Ga. 576"),
    T("r108365", OV, P, "Neuber v. Royal Realty Co. (1948) 86 Cal.App.2d 596", "(1957) 48 Cal.2d 846"),
    T("r161413", OV, P, "Ramirez v. Armstrong, 100 N.M. 538", "110 N.M. 457"),
    T("r155289", DI, P, "Wells v. Goodyear Tire & Rubber Co. , 14 Neb. App. 384", "272 Neb. 918"),
    T("r154197", OV, P, "Monroe v. Harper (1974), 164 Mont. 23", "286 Mont. 60"),
    T("r135567", OV, P, "Hiatt v. Yergin (1972), 152 Ind.App. 497", "overruled in part, 411 N.E.2d 653", 0.85),
    T("r154274", OV, P, "State v. DeVore, 1998 MT 340", "309 Mont. 113"),
    T("r156260", OV, P, "Williams v. State, 81 N.H. 341", "Dartmouth College, 89 N.H. 471"),
    F("r142689", "notOverruling", 0.9),
    T("r155635", OV, P, "Antonini v. Hanna Industries, 94 Nev. 12", "Harris v. Rio Hotel & Casino, 117 Nev. 482"),
    T("r186554", OV, P, "Helms v. State, 484 S.W.2d 925", "Young v. State, 8 S.W.3d 656"),
    T("r127799", OV, P, "Baker v. State, 30 Fla. 41", "Tipton v. State, 97 So.2d 277"),
    T("r127812", OV, P, "Baker v. State, 30 Fla. 41", "Tipton v. State, 97 So.2d 277"),
    T("r155126", OV, P, "Atokad Ag. & Racing v. Governors of Knts. of Ak-Sar-Ben, 237 Neb. 317", "Eccleston v. Chait, 241 Neb. 961"),
    T("r113092", DI, P, "Titan Enterprises, Inc. v. Armo Construction, Inc. (1973) 32 Cal.App.3d 828", "(1979) 23 Cal.3d 180"),
    T("r151207", OV, P, "Gadd v. Thompson, 517 So.2d 576", "Foster v. Harden, 536 So.2d 905"),
    T("r151548", OV, P, "Gadd v. Thompson, 517 So.2d 576", "Foster v. Harden, 536 So.2d 905"),
    T("r98068", OV, P, "Kuske v. McSheridan (In re McSheridan), 184 B.R. 91", "504 F.3d 978"),
    T("r5150", OV, P, "A.M. v. State, 891 P.2d 815", "In re S.A., 912 P.2d 1235", 0.85),
    T("r5159", OV, P, "AM v. State, 891 P.2d 815", "In re S.A., 912 P.2d 1235", 0.85),
    T("r154588", OV, P, "State v. Sorenson, 180 Mont. 269", "State v. Loh, 275 Mont. 460", 0.85),
    T("r155814", AB, P, "Johnson v. State, 97 Nev. 621", "Horton v. California, 496 U.S. 128"),
    T("r154629", OV, P, "State v. Beavers, 2000 MT 145", "343 Mont. 494"),
    T("r7559", OV, P, "Holloway v. State, 18 Ark. App. 136", "Doby v. State, 290 Ark. 408"),
    T("r130937", OV, P, "Alexander v. State, 247 Ga. 780", "Edge v. State, 261 Ga. 865", 0.85),
    T("r140103", OV, P, "Sanders v. Commonwealth, 89 S.W.3d 380", "Leonard v. Commonwealth, 279 S.W.3d 151"),
    T("r169655", OV, P, "Fox v. Ungar, 164 Or 226", "Ross v. Robinson, 174 Or 25", 0.85),
    T("r135554", OV, P, "Watkins v. State (1991), Ind.App., 571 N.E.2d 1262", "overruled in part, 575 N.E.2d 624", 0.75),
    T("r167331", OV, P, "State v. Thomas (1980), 61 Ohio St.2d 254", "State v. Crago (1990), 53 Ohio St.3d 243"),
    T("r4023", OV, P, "Waldon v. Hartford Insurance Group, 435 So.2d 1271", "Mfg. Co., 547 So.2d 90"),
    T("r80552", AB, P, "United States v. Bloom, 149 F.3d 649", "130 S.Ct. 2896"),
    T("r158028", OV, P, "Division of Youth & Family Servs. v. R.G., 397 N.J.Super. 439", "968 A.2d 698"),
    T("r186605", OV, P, "Smith v. State, 898 S.W.2d 838", "Tennard v. Dretke, 542 U.S. 274"),
    T("r6528", DI, P, "Hayden Business Center Condominiums Ass", "218 Ariz. 574"),
]
