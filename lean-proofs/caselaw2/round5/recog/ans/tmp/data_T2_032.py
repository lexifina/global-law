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
    F("r190050", "otherDecision", 0.95),
    T("r119554", OV, P, "Belford v. New Haven, 170 Conn. 46", "184 Conn. 51"),
    T("r137110", OV, O, "State v. Oge, 227 Iowa 1094", "State v. Walton, 195 N.W.2d 100"),
    T("r155238", DI, P, "SID No. 57 v. City of Elkhorn, 248 Neb. 486", "676 N.W.2d 710"),
    F("r155205", "otherDecision", 0.9),
    T("r113677", OV, P, "People v. Ausbie (2004) 123 Cal.App.4th 855", "People v. Santana (2013) 56 Cal.4th 999"),
    T("r155639", OV, P, "Mitchell v. State, 114 Nev. 1417", "Sharma v. State, 118 Nev. 648"),
    T("r147925", DI, P, "People v Foster, 175 Mich App 311", "People v Fields, 450 Mich 94"),
    T("r3711", OV, O, "Bob v. State, 29 Ala. 20", "State 33 Ala. 389", 0.85),
    T("r121960", OV, P, "Holliday v. Principi, 14 Vet.App. 280", "Dyment v. Principi, 287 F.3d 1377"),
    T("r121976", OV, P, "Holliday v. Principi 14 Vet.App. 280", "Dyment v. Principi 287 F.3d 1377"),
    T("r115516", DI, P, "Circus Circus Hotels, Inc. v. Superior Court (1981) 120 Cal.App.3d 546", "(1996) 14 Cal.4th 434"),
    T("r155282", DI, P, "State v. Allen , 252 Neb. 187", "State v. Myers , 258 Neb. 300"),
    F("r119726", "notOverruling", 0.85),
    T("r116448", OV, P, "Hilberg v. F.W. Woolworth Co., 761 P.2d 236", "Casebolt v. Cowan, 829 P.2d 352"),
    T("r115724", OV, P, "People v. Wheeler (1978) 22 Cal.3d 258", "Johnson v. California (2005) 545 U.S. 162"),
    T("r115731", OV, P, "People v. Wheeler (1978) 22 Cal.3d 258", "Johnson v. California (2005) 545 U.S. 162"),
    T("r115769", OV, P, "People v. Wheeler (1978) 22 Cal.3d 258", "Johnson v. California (2005) 545 U.S. 162"),
    T("r118403", OV, P, "Carr v. Woolwich, 7 Conn. App. 684", "Zoning Board of Appeals, 225 Conn. 432"),
    T("r116650", OV, P, "People v. Stiles, 692 P.2d 1124", "King v. People, 785 P.2d 596"),
    T("r191268", OV, P, "Arnold v. United Cos. Lending Corp., [204 W.Va. 229,]", "Nelson, 230 W.Va. 281", 0.8),
    F("r114217", "notOverruling", 0.75),
    T("r131030", OV, P, "Kent v. Brown, 238 Ga. App. 607", "Styles v. State, 245 Ga. App. 90"),
    T("r128204", DI, P, "State v. Osborne, 781 So.2d 1137", "State v. Goode, 830 So.2d 817", 0.85),
    T("r131262", DI, P, "Allen v. State, 268 Ga. App. 519", "Harris v. State, 322 Ga. App. 87"),
    F("r168794", "cannotTell", 0.6),
    F("r169400", "cannotTell", 0.6),
    T("r139652", OV, P, "Board of Ed. of Ashland School Dist. v. Chattin, Ky., 376 S.W.2d 693", "415 S.W.2d 607"),
    T("r139859", OV, P, "957 S.W.2d 195 (1997), overruled", "Yanero v. Davis, Ky., 65 S.W.3d 510", 0.85),
    T("r127902", RE, P, "State v. Gibson, 452 So.2d 553", "State v. Enmund, 476 So.2d 165"),
    T("r127911", RE, P, "State v. Gibson, 452 So.2d 553", "State v. Enmund, 476 So.2d 165", 0.75),
    T("r154537", OV, P, "State v. Reesman, 2000 MT 243", "333 Mont. 220"),
    T("r154700", OV, P, "State v. Reesman, 2000 MT 243", "333 Mont. 220"),
    T("r154883", OV, P, "State v. Reesman , 2000 MT 243", "333 Mont. 220"),
    T("r136299", OV, P, "Mitchell v. State, 619 N.E.2d 961", "Patterson v. State, 659 N.E.2d 220"),
    T("r161636", OV, P, "State v. Manus, 93 N.M. 95", "Sells v. State, 98 N.M. 786"),
    T("r174042", DI, P, "Engberg v. Ford Motor Company, 87 S.D. 196", "Smith v. Smith, 278 N.W.2d 155"),
    T("r127931", DI, P, "Senior v. State, 502 So.2d 1360", "Goene v. State, 577 So.2d 1306"),
    F("r128401", "notOverruling", 0.85),
    T("r7394", AB, P, "State v. Richmond, 114 Ariz. 186", "State v. Salazar, 173 Ariz. 399"),
    T("r136743", OV, P, "Miller v. State, 8 Ind. 325", "State v. Walker, 26 Ind. 346", 0.85),
    T("r153990", OV, P, "Kelley v. Cable Co., 7 Mont. 70", "18 Mont. 493", 0.85, "on this point"),
    T("r154308", OV, P, "State v. Armstrong (1976), 170 Mont. 256", "State v. Johnson (1986), 221 Mont. 503"),
    T("r5905", OV, P, "Stevenson v. Celaya, 10 Ariz.App. 203", "McHazlett v. Otis Eng. Corp., 133 Ariz. 530"),
    T("r154589", OV, P, "State v. Graves, 191 Mont. 81", "336 Mont. 6", 0.8),
    T("r190672", OV, P, "Jenkins v. J.C. Penney Casualty Ins. Co., 167 W.Va. 597", "Madden, 192 W.Va. 155"),
    T("r190719", OV, P, "Jenkins v. J.C. Penney Cas. Ins. Co., 167 W.Va. 597", "Madden, 192 W.Va. 155"),
    T("r190777", OV, P, "Jenkins v. J.C. Penney Cas. Ins. Co., 167 W.Va. 597", "Madden, 192 W.Va. 155"),
    T("r155281", DI, P, "Dawes v. Wittrock Sandblasting & Painting , 266 Neb. 526", "Kimminau v. Uribe"),
    T("r78361", OV, O, "Holmes v. United States Board of Parole, 541 F.2d 1243", "Solomon v. Benson, 563 F.2d 339", 0.85),
]
