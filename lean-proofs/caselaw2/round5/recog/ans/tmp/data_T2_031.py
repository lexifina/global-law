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
    T("r138717", DI, P, "Stratmann v. Stratmann, 204 Kan. 658", "Classen v. Federal Land Bank of Wichita, 228 Kan. 426"),
    T("r5094", OV, P, "Greater Anchorage Area Borough v. City of Anchorage, 504 P.2d 1027", "Thibodeau, 595 P.2d 626"),
    T("r192647", OV, P, "Pickens v. State, 96 Wis. 2d 549", "State v. Klessig, 211 Wis. 2d 194", 0.85),
    T("r187339", OV, P, "State v. Lairby, 699 P.2d 1187", "State v. Ossana, 739 P.2d 628"),
    F("r127965", "notOverruling", 0.6),
    T("r150086", OV, P, "Hendrickson v. Minnesota Power & Light Co., 258 Minn. 368", "overruled in part, 255 N.W.2d 362", 0.85),
    T("r150150", OV, P, "Hendrickson v. Minnesota Power & Light Co., 258 Minn. 368", "Tolbert v. Gerber Indus., Inc., 255 N.W.2d 362"),
    T("r150432", OV, P, "Hendrickson v. Minn. Power & Light Co. , 258 Minn. 368", "255 N.W.2d 362"),
    T("r136569", OV, P, "Edgerton v. Huff, 26 Ind. 35", "Water Works Co. v. Burkhart, 41 Ind. 364", 0.9,
      "as to the construction of certain statutes"),
    T("r127884", RE, P, "Floridians Against Casino Takeover v. Let", "Fine v. Firestone, 448 So.2d 984", 0.8),
    F("r139651", "ownAct", 0.95),
    F("r5280", "otherDecision", 0.9),
    T("r159682", OV, P, "State v. Brown, 138 N.J. 481", "State v. Cooper, 151 N.J. 326"),
    T("r111378", DI, P, "State Farm Fire & Casualty Co. v. Superior Court (1996) 45 Cal.App.4th 1093", "(1999) 20 Cal.4th 163", 0.9,
      "as to actions between business competitors"),
    T("r154606", OV, P, "Bruce, however, has been overruled", "State v. Ariegwe, 2007 MT 204", 0.9, "on this point"),
    T("r128153", DI, P, "State Dep’t of Transp. v. Byrd, 254 So.2d 836", "Broward County v. Patel, 641 So.2d 40"),
    T("r173626", OV, P, "Cochran v. City of Sumter, 242 S.C. 382", "McCall v. Batson, 285 S.C. 243", 0.9,
      "to the extent that it holds an action may not be maintained against the State without its consent"),
    T("r154539", OV, P, "Major v. North Valley Hosp., 233 Mont. 25", "Clinic, 286 Mont. 60"),
    T("r155622", OV, P, "Garner v. State, 116 Nev. 770, 780", "Sharma v. State, 118 Nev. 648"),
    T("r134188", AB, P, "People v. Cole (1990), 193 Ill. App. 3d 990", "People v. Schott (1991), 145 Ill. 2d 188"),
    T("r131452", OV, P, "Woodworth v. Woodworth, 7 Haw. App. 11", "Myers v. Myers, 70 Haw. 143"),
    T("r131453", OV, P, "Woodworth v. Woodworth, 7 Haw. App. 11", "Myers v. Myers, 70 Haw. 143"),
    T("r131456", OV, P, "Woodworth v. Woodworth, 7 Haw. App. 11", "Myers v. Myers, 70 Haw. 143"),
    T("r5063", OV, P, "Nazareno v. Urie, 638 P.2d 671", "Elbow Room, Inc., 711 P.2d 521"),
    T("r79750", AB, O, "Reiherzer v. Shannon, 581 F.2d 1266", "Black v. TIC Inv. Corp., 900 F.2d 112", 0.85),
    F("r138811", "otherDecision", 0.9),
    T("r147264", OV, P, "Lovitt v Concord School Dist, 58 Mich App 593", "overruled in part 398 Mich 527", 0.85),
    T("r175557", AB, P, "King v. Governor of New Jersey, 767 F. 3d 216", "Becerra, 585 U. S. 755", 0.9),
    T("r186361", OV, P, "Ex parte Paprskar, 573 S.W.2d 525", "Weiner v. Dial, 653 S.W.2d 786", 0.9),
    T("r186485", OV, P, "Jackson v. State, 718 S.W.2d 724", "Studer, 799 S.W.2d 263"),
    T("r154792", OV, P, "State v. Ereth, 1998 MT 197", "344 Mont 468", 0.85),
    F("r79996", "notOverruling", 0.9),
    T("r154242", OV, P, "Sztaba v. Great Northern Ry. Co. (1966), 147 Mont. 185", "Kyriss v. State (1985), 218 Mont. 162"),
    T("r137204", OV, P, "Addy v. Addy, 240 Iowa 255", "Brown v. Brown, 269 N.W.2d 819"),
    T("r108917", DI, P, "People v. Mullen (1941) 45 Cal.App.2d 297", "People v. Hood (1962) 199 Cal.App.2d 44"),
    T("r192553", OV, P, "Rineck v. Johnson, 155 Wis. 2d 659", "182 Wis. 2d 549"),
    T("r192595", OV, P, "Rineck v. Johnson, 155 Wis. 2d 659", "182 Wis.2d 549"),
    T("r139785", OV, P, "Stark v. Commonwealth, Ky., 828 S.W.2d 603", "Thomas v. Commonwealth, Ky., 931 S.W.2d 446"),
    T("r154426", OV, P, "State v. Moorman (1997), 279 Mont. 330", "323 Mont. 347"),
    T("r132534", OV, P, "State v. Pizzuto, 119 Idaho 742", "State v. Card, 121 Idaho 425"),
    T("r152925", OV, P, "Bain v. Dir. of Revenue, 69 S.W.3d 117", "Dir. of Revenue, 119 S.W.3d 543"),
    T("r6814", AB, P, "State v. Box, 205 Ariz. 492", "Driscoll, 238 Ariz. 432"),
    T("r188072", OV, P, "State v. Couture, 146 Vt. 268", "State v. Holcomb, 156 Vt. 251"),
    T("r152672", OV, P, "Misener v. Dir. of Revenue, 13 S.W.3d 666", "Dir. of Revenue, 119 S.W.3d 543"),
    T("r152776", OV, P, "Misener v. Director of Revenue, 13 S.W.3d 666", "Verdoorn v. Director of Revenue, 119 S.W.3d 543"),
    T("r109300", DI, O, "Gehman v. Superior Court (1979) 96 Cal.App.3d 257", "(1980) 26 Cal.3d 744", 0.85),
    T("r154181", OV, P, "State v. Siegal (1997), 281 Mont. 250", "State v. Kuneff, 1998 MT 287, [291 Mont. 474]"),
    T("r154213", OV, P, "State v. Siegal (1997), 281 Mont. 250", "State v. Kuneff (1998), 291 Mont. 474"),
    T("r154221", OV, P, "State v. Siegal (1997), 281 Mont. 250", "State v. Kuneff, 1998 MT 287, 291 Mont. 474"),
    T("r135545", OV, P, "Ewing v. State (1974), 160 Ind.App. 138", "Hoffa v. State (1977), 267 Ind. 133"),
]
