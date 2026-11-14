import LegalProofs.CaseLaw2.Exec.Verdicts
import LegalProofs.CaseLaw2.Spec.Recognised
import LegalProofs.CaseLaw2.Certificate

/-!
# Known episodes, replayed (DESIGN D3)

Real decisions (dates and courts as decided; court ids are v1's where v1 has them), with the model's answers checked
by `#guard` on every build. Every authority rule and every status rule is exercised by at least one of them; the
episodes:

* *Betts v. Brady* (1 Jun 1942) / *Gideon v. Wainwright* (18 Mar 1963); *Bowers v. Hardwick* (30 Jun 1986) / *Lawrence
  v. Texas* (26 Jun 2003), and a district court citing *Bowers* in 2005;
* Kentucky 1976: a 1970 decision of the old Court of Appeals of Kentucky (then the court of last resort) binds the new
  Court of Appeals in 1990, which cannot overrule it; the Supreme Court of Kentucky (successor) can;
* *Bonner v. City of Prichard* (11th Cir. 1981): pre-split Fifth Circuit law binds the Eleventh Circuit; a 1982 Fifth
  Circuit decision does not; only the 11th Circuit en banc may overrule;
* *South Corp. v. United States* (Fed. Cir. 1982): CCPA law binds the Federal Circuit and, on patent law, every
  district court;
* *M.A.P. v. Ryan* (D.C. 1971): D.C. Circuit decisions before 1 Feb 1971 bind the D.C. courts on D.C. law; later ones
  do not. This is the cross-system adoption that the *Erie* theorem's "absent adoption" hypothesis excludes;
* a California Court of Appeal conflict (*Auto Equity*): the superior court must choose; under an own-unit rule it
  follows its own district;
* a partial overruling (Georgia): the overruled issue falls, the other stands;
* *Ledbetter v. Goodyear* (29 May 2007), superseded by the Lilly Ledbetter Fair Pay Act (enacted 29 Jan 2009,
  retroactive to 28 May 2007): two-date answers;
* *Erie* (1938) both ways, the 5th Cir. unpublished-opinion cut-off (1996), a *Sunburst* prospective overruling,
  revival when the overruling decision is vacated, an en banc grant under an unknown rule (status unknown), and the
  certificate checker on Gideon's own words, a procedural "point of error is overruled" and a dissent.
-/

namespace CaseLaw2.Examples
open CaseLaw2 CaseLaw2.Spec CaseLaw2.Exec

def scotus := 2906
def ca5 := 346
def ca11 := 241
def ndtex := 367
def ndga := 10005
def kyOld := 918
def kySup := 917
def caSup := 522
def caApp := 524
def caSuper := 10000
def gaSup := 10001
def gaApp := 10002
def dcCir := 514
def dcCA := 627
def dcSuper := 10003
def ccpa := 655
def fedCir := 520
def ndill := 10006

def ep (court from_ to_ system : Nat) (tier : Tier) (circuit : Nat := 0) (lr : LastResortFor := .notLast) :
    CourtEpoch :=
  { court, dateFrom := from_, dateTo := to_, system, tier, lastResortFor := lr, circuit, unit := none, firm := true }

def env : Env :=
  { epochs := [ep scotus 0 forever 0 .last 0 .all, ep ca5 0 forever 0 .appellate 5, ep ca11 19811001 forever 0 .appellate 11,
      ep ndtex 0 forever 0 .trial 5, ep ndga 0 forever 0 .trial 11, ep ndill 0 forever 0 .trial 7,
      ep kyOld 0 19751231 17 .last 0 .all, ep kyOld 19760101 forever 17 .appellate,
      ep kySup 19760101 forever 17 .last 0 .all, ep caSup 0 forever 5 .last 0 .all, ep caApp 19050101 forever 5 .appellate,
      ep caSuper 0 forever 5 .trial, ep gaSup 0 forever 11 .last 0 .all, ep gaApp 19070101 forever 11 .appellate,
      ep dcCir 0 forever 0 .appellate 12, ep dcCA 19710201 forever 51 .last 0 .all, ep dcCA 0 19710131 51 .appellate,
      ep dcSuper 0 forever 51 .trial, ep ccpa 0 19820930 0 .appellate 13, ep fedCir 19821001 forever 0 .appellate 13]
    successions := [{ old := kyOld, new := kySup, date := 19760101, kind := .replace, firm := true }]
    adoptions := [{ adopter := ca11, source := ca5, upTo := 19810930, filter := .all, force := .binding, firm := true },
      { adopter := ca11, source := ca5, upTo := forever, filter := .unitB, force := .binding, firm := true },
      { adopter := fedCir, source := ccpa, upTo := 19820930, filter := .all, force := .binding, firm := true },
      { adopter := dcCA, source := dcCir, upTo := 19710131, filter := .all, force := .binding, firm := true }]
    rules := [⟨0, "horizontal", "strong", 0, forever, true⟩, ⟨5, "horizontal", "none", 0, forever, true⟩,
      ⟨5, "trialScope", "statewideChooseOnConflict", 0, forever, true⟩, ⟨17, "horizontal", "strong", 0, forever, true⟩,
      ⟨11, "horizontal", "strong", 0, forever, true⟩, ⟨51, "horizontal", "strong", 0, forever, true⟩,
      ⟨-(ca5 : Int), "unpubForce", "binding", 0, 19951231, true⟩,
      ⟨-(ca5 : Int), "unpubForce", "persuasive", 19960101, forever, true⟩,
      ⟨-(ca11 : Int), "firstInTimeControls", "1", 0, forever, true⟩,
      -- M.A.P. v. Ryan: the D.C. Court of Appeals sits in divisions, bound by the court's decisions (hunt H6)
      ⟨-(dcCA : Int), "horizontal", "strong", 19710201, forever, true⟩] }

def L : Lookups := (ExecEnv.build env).lookups

def d (id court date : Nat) (unit : Option Nat := none) (bench : Bench := .panel) (pub : Publication := .published) :
    Decision :=
  { id, court, date, unit, bench := some bench, pub := some pub, form := some .full }

def betts := d 0 scotus 19420601 (bench := .wholeCourt)
def gideon := d 1 scotus 19630318 (bench := .wholeCourt)
def bowers := d 2 scotus 19860630 (bench := .wholeCourt)
def lawrence := d 3 scotus 20030626 (bench := .wholeCourt)
def ky1970 := d 4 kyOld 19700115 (bench := .wholeCourt)
def ky1990 := d 5 kyOld 19900601
def kySup1995 := d 20 kySup 19950601 (bench := .wholeCourt)
def ca5in1975 := d 6 ca5 19750301
def ca11in1990 := d 7 ca11 19900301
def ca11enBanc := d 21 ca11 19920301 (bench := .enBanc)
def ca5in1982 := d 22 ca5 19820301
def caApp1 := d 8 caApp 20010101 (unit := some 1)
def caApp2 := d 9 caApp 20050101 (unit := some 2)
def caSuper2010 := d 10 caSuper 20100101 (unit := some 2)
def ledbetter := d 11 scotus 20070529 (bench := .wholeCourt)
def ndtex2010 := d 12 ndtex 20100601
def gaSup1980 := d 13 gaSup 19800101 (bench := .wholeCourt)
def gaSup1995 := d 14 gaSup 19950101 (bench := .wholeCourt)
def ca5unpub1999 := d 15 ca5 19990301 (pub := .unpublished)
def ca5unpub1994 := d 23 ca5 19940301 (pub := .unpublished)
def ndtex2001 := d 16 ndtex 20010101
def ndtex2005 := d 17 ndtex 20050101
def gaApp1996 := d 18 gaApp 19960101
def ccpa1980 := d 24 ccpa 19800101
def fedCir1990 := d 25 fedCir 19900101
def ndill1990 := d 26 ndill 19900101
def dcCir1965 := d 27 dcCir 19650101
def dcCir1975 := d 28 dcCir 19750101
def dcSuper1990 := d 29 dcSuper 19900101
def gaSup1930 := d 30 gaSup 19300101 (bench := .wholeCourt)
def ndga1935 := d 31 ndga 19350101
def ndga1950 := d 32 ndga 19500101
def dcCA1980 := d 33 dcCA 19800101
def dcCA1990 := d 34 dcCA 19900101
def dcCAenBanc := d 35 dcCA 19950101 (bench := .enBanc)
def ca5enBanc1983 := d 36 ca5 19830301 (bench := .enBanc)
def ndga1990 := d 37 ndga 19900101
def ca5in1990 := d 38 ca5 19900101
def ca5in1970 := d 39 ca5 19700301
def ca5enBanc1980 := d 40 ca5 19800301 (bench := .enBanc)
def dcCirEnBanc1980 := d 41 dcCir 19800101 (bench := .enBanc)

def decs : List Decision :=
  [betts, gideon, bowers, lawrence, ky1970, ky1990, kySup1995, ca5in1975, ca11in1990, ca11enBanc, ca5in1982, caApp1,
   caApp2, caSuper2010, ledbetter, ndtex2010, gaSup1980, gaSup1995, ca5unpub1999, ca5unpub1994, ndtex2001, ndtex2005,
   gaApp1996, ccpa1980, fedCir1990, ndill1990, dcCir1965, dcCir1975, dcSuper1990, gaSup1930, ndga1935, ndga1950,
   dcCA1980, dcCA1990, dcCAenBanc, ca5enBanc1983, ndga1990, ca5in1990, ca5in1970, ca5enBanc1980, dcCirEnBanc1980]

def dec (n : Nat) : Option Decision := decs.find? (·.id == n)

/-- Issues: 1 venue, 2 notice (Georgia); 3 Title VII charge period; 4 the California clause; 5 D.C. law. -/
def anon (x : Decision) : Holding := Holding.anon x
def hold (x : Decision) (issue : Nat) (dom : Domain) (ans : Option Answer := none) : Holding :=
  { id := x.id * 10 + issue, node := x.id, issue, domain := some dom, role := some .majority, answer := ans }

def tr (id by_ target date : Nat) (scope : Scope := .all) (temporal : Temporal := .retroactive) : TEvent :=
  { id, by_, target, date, kind := .overruled, scope, temporal, explicit := true }

def record : Record :=
  { dec
    hist := []
    treat := [tr 1 1 0 19630318, tr 2 3 2 20030626, tr 3 14 13 19950101 (.issues [2]),
      -- hunt H4: the Fifth Circuit en banc (1983) overrules a pre-split decision; the Eleventh en banc (1992) another
      tr 4 36 6 19830301, tr 5 21 39 19920301,
      -- round 2: the D.C. Circuit en banc (1980) overrules one of its pre-1971 decisions (*M.A.P.* line)
      tr 6 41 27 19800101]
    supers := [{ id := 1, target := 11, scope := .issues [3], enacted := 20090129, effective := 20090129,
                 retroactiveTo := some 20070528, explicit := true }] }

def E : EventLookups := (ExecRecord.build record).lookups
def effs (x : Nat) : List Effect := effectsOf L E dec x
def st (x k t u : Nat) : Status := status (effs x) k t u
def fo (x : Decision) (h : Holding) (c : Decision) : Option Force := (forceOn L E x h c).map (·.1)
def path (x : Decision) (h : Holding) (c : Decision) : List RuleId := ((forceOn L E x h c).map (·.2)).getD []
def pw (b x : Decision) (dom : Option Domain := none) : Option Bool := (canChangeStatus L b x dom).map (·.1)

-- Betts / Gideon, Bowers / Lawrence (F1, H1self, lastResortSelf, status by date)
#guard st 0 0 19630317 19630317 == .good
#guard st 0 0 19630318 19630318 == .neg .overruled
#guard st 2 0 20030625 20030625 == .good
#guard st 2 0 20030626 20030626 == .neg .overruled
#guard pw gideon betts == some true
#guard fo bowers (anon bowers) ndtex2005 == some .binding
#guard path bowers (anon bowers) ndtex2005 == [.assumeHomeDomain, .F1]
#guard fo bowers (anon bowers) lawrence == some .persuasiveStrong   -- SCOTUS is not bound by itself (H1)
#guard citesOverruled (citeFacts L E dec (effs 2) bowers (anon bowers) ndtex2005 (some 20050101) false) == true
#guard citesOverruled (citeFacts L E dec (effs 2) bowers (anon bowers) ndtex2001 (some 20010101) false) == false
-- the Georgia Supreme Court has no power over a SCOTUS decision on federal law
#guard pw gaSup1995 bowers == some false

-- Kentucky 1976 (epochs, H1, succession, power)
#guard fo ky1970 (anon ky1970) ky1990 == some .binding
#guard path ky1970 (anon ky1970) ky1990 == [.assumeHomeDomain, .H1]
#guard fo ky1970 (anon ky1970) kySup1995 == some .persuasiveStrong
#guard pw ky1990 ky1970 == some false
#guard pw kySup1995 ky1970 == some true
#guard (canChangeStatus L kySup1995 ky1970 none).map (·.2) == some .lastResortSelf

-- Bonner (F10): pre-split Fifth Circuit law binds the Eleventh; post-split does not; only en banc overrules
#guard fo ca5in1975 (anon ca5in1975) ca11in1990 == some .binding
#guard (path ca5in1975 (anon ca5in1975) ca11in1990).contains .adopted
#guard fo ca5in1982 (anon ca5in1982) ca11in1990 == some .persuasive
#guard pw ca11in1990 ca5in1975 == some false
#guard pw ca11enBanc ca5in1975 == some true
-- the Fifth Circuit keeps its own pre-split law (F7 horizontal)
#guard fo ca5in1975 (anon ca5in1975) ca5in1982 == some .binding
#guard pw ca5in1982 ca5in1975 == some false   -- no_panel_overrules_panel_in_strong

-- Hunt H4 (United States v. Salinas, 654 F.2d 319 (5th Cir. Aug 1981), overruled by United States v. Adamson, 700
-- F.2d 953 (5th Cir. 1983) (en banc), and still cited by the Eleventh Circuit): status after the Bonner cut-off is
-- per heir. The Fifth's overruling reaches the original line, not the Eleventh's
#guard (effs 6).map (·.reach) == [.lines true [] [ca11]]
#guard statusFor (inLine L ca11in1990) (effs 6) 0 19900301 19900301 == .good
#guard statusFor (inLine L ndga1990) (effs 6) 0 19900101 19900101 == .good
#guard statusFor (inLine L ca5in1990) (effs 6) 0 19900101 19900101 == .neg .overruled
#guard statusFor (inLine L ndtex2005) (effs 6) 0 20050101 20050101 == .neg .overruled
#guard statusFor (inLine L ndill1990) (effs 6) 0 19900101 19900101 == .neg .overruled
#guard citesOverruled (citeFacts L E dec (effs 6) ca5in1975 (anon ca5in1975) ca11in1990 none false) == false
#guard citesOverruled (citeFacts L E dec (effs 6) ca5in1975 (anon ca5in1975) ndtex2005 none false) == true
-- and the Eleventh's en banc overruling of an old Fifth Circuit decision stays in the Eleventh's line
#guard (effs 39).map (·.reach) == [.lines false [ca11] []]
#guard statusFor (inLine L (d 91 ca11 19950101)) (effs 39) 0 19950101 19950101 == .neg .overruled
#guard statusFor (inLine L (d 92 ndga 19950101)) (effs 39) 0 19950101 19950101 == .neg .overruled
#guard statusFor (inLine L (d 93 ca5 19950101)) (effs 39) 0 19950101 19950101 == .good
-- an overruling before the cut-off was adopted as overruled; SCOTUS reaches every line; no heir, no lines
#guard reachOf L ca5enBanc1980 ca5in1975 == .all
#guard reachOf L lawrence ca5in1975 == .all
#guard reachOf L ca5enBanc1983 ca5in1982 == .all
-- the union (court-independent) status, as status.tsv reports it, is unchanged
#guard st 6 0 19900101 19900101 == .neg .overruled

-- Round 2 (DEVIATIONS 74–78): status per line of authority, everywhere.
-- Per-line status rows (`status_lines.tsv`): Salinas is overruled in the original line, good in the Eleventh's
#guard linesOf (effs 6) == [.orig, .heir ca11]
#guard lineStatus .orig (effs 6) 0 19900101 19900101 == .neg .overruled
#guard lineStatus (.heir ca11) (effs 6) 0 19900101 19900101 == .good
#guard lineStatus (.heir ca11) (effs 6) 0 19900301 19900301 ==
  statusFor (inLine L ca11in1990) (effs 6) 0 19900301 19900301
#guard lineStatus (.heir ca11) (effs 6) 0 19900101 19900101 == statusFor (inLine L ndga1990) (effs 6) 0 19900101 19900101
#guard lineStatus .orig (effs 6) 0 19900101 19900101 == statusFor (inLine L ndill1990) (effs 6) 0 19900101 19900101
-- the Eleventh's own en banc overruling: the reverse
#guard lineStatus .orig (effs 39) 0 19950101 19950101 == .good
#guard lineStatus (.heir ca11) (effs 39) 0 19950101 19950101 == .neg .overruled
-- no heir, no per-line rows; any line reads the union status (Betts after Gideon)
#guard linesOf (effs 0) == []
#guard lineStatus (.heir ca11) (effs 0) 0 19700101 19700101 == st 0 0 19700101 19700101
-- M.A.P. v. Ryan: a pre-1971 D.C. Circuit decision the D.C. Circuit later overruled en banc still binds the D.C.
-- courts (the D.C. Court of Appeals holds it as its own), and is overruled for the D.C. Circuit's own line
#guard (effs 27).map (·.reach) == [.lines true [] [dcCA]]
#guard lineStatus (.heir dcCA) (effs 27) 0 19900101 19900101 == .good
#guard lineStatus .orig (effs 27) 0 19900101 19900101 == .neg .overruled
#guard statusFor (inLine L dcSuper1990) (effs 27) 0 19900101 19900101 == .good
#guard statusFor (inLine L dcCA1990) (effs 27) 0 19900101 19900101 == .good
#guard statusFor (inLine L (d 90 dcCir 19900101)) (effs 27) 0 19900101 19900101 == .neg .overruled
-- the original court is gone: the Federal Circuit en banc speaks for the CCPA's line too (every line is reached);
-- a decision dated outside its court's epoch has no line-limited effect
#guard reachOf L (d 42 fedCir 19900101 (bench := .enBanc)) ccpa1980 == .all
#guard reachOf L (d 42 fedCir 19900101 (bench := .enBanc)) (d 44 ccpa 19900101) == .all
#guard reachOf L ca5enBanc1983 (d 43 ca11 19700101) == .all
-- Splits and conflicts: the holdings that count at a court are those good law in its line
def ca11q := d 95 ca11 19950101
def ca5q := d 96 ca5 19950101
def heldSalinas : List (Held Nat) :=
  [{ item := 6, issue := 0, effs := effs 6 }, { item := 39, issue := 0, effs := effs 39 },
   { item := 22, issue := 0, effs := effs 22 }]
#guard heldVia (effectsFor L ca11q) 19950101 heldSalinas == [6, 22]
#guard heldVia (effectsFor L (d 97 ndga 19950101)) 19950101 heldSalinas == [6, 22]
#guard heldVia (effectsFor L ca5q) 19950101 heldSalinas == [39, 22]
#guard heldVia (effectsFor L (d 98 ndtex 19950101)) 19950101 heldSalinas == [39, 22]
#guard heldIn (inLine L ca11q) 19950101 heldSalinas == heldVia (effectsFor L ca11q) 19950101 heldSalinas
#guard heldUnion 19950101 heldSalinas == [22]
-- a court with no epoch on the date (the Eleventh Circuit in 1980) has no known line: the union
#guard heldVia (effectsFor L (d 99 ca11 19800101)) 19950101 heldSalinas == [22]
-- a conflict in the Eleventh Circuit between Salinas (yes) and a later Eleventh Circuit panel (no); none in the
-- Fifth, where Salinas is overruled
def candOf (hid : Nat) (a : Answer) (date : Nat) : Cand :=
  { holding := hid, answer := a, force := .binding, prec := 2, date, ownUnit := false }
def heldConflict : List (Held Cand) :=
  [{ item := candOf 6 .yes 19750301, issue := 0, effs := effs 6 },
   { item := candOf 7 .no 19900301, issue := 0, effs := effs 7 }]
#guard (resolve false none (heldVia (effectsFor L ca11q) 19950101 heldConflict)).map (·.holding) == [6, 7]
#guard (resolve false none (heldVia (effectsFor L ca5q) 19950101 heldConflict)).map (·.holding) == [7]
-- Horty: two precedents that conflict under the reason model; the base is inconsistent in the Eleventh Circuit's
-- line and consistent in the Fifth's, where one of them is overruled
def fcPi : Horty.FCase := ⟨[⟨1, .pi⟩, ⟨2, .delta⟩], [⟨1, .pi⟩], .pi⟩
def fcDelta : Horty.FCase := ⟨[⟨1, .pi⟩, ⟨2, .delta⟩], [⟨2, .delta⟩], .delta⟩
def heldHorty : List (Held Horty.FCase) :=
  [{ item := fcPi, issue := 0, effs := effs 6 }, { item := fcDelta, issue := 0, effs := effs 7 }]
#guard Horty.conflict fcPi fcDelta
#guard lineBase (inLine L ca11q) 19950101 heldHorty == [fcPi, fcDelta]
#guard !Horty.consistent (lineBase (inLine L ca11q) 19950101 heldHorty)
#guard lineBase (inLine L ca5q) 19950101 heldHorty == [fcDelta]
#guard Horty.consistent (lineBase (inLine L ca5q) 19950101 heldHorty)
#guard heldUnion 19950101 heldHorty == [fcDelta]
#guard liveSomewhere (effs 6) 0 19950101 && !goodLaw (effs 6) 0 19950101 19950101

-- Hunt H6 (M.A.P. v. Ryan, 285 A.2d 310 (D.C. 1971)): a division of the D.C. Court of Appeals is bound by the
-- court's decisions and cannot overrule them; the court en banc is not bound and can
#guard fo dcCA1980 (hold dcCA1980 5 (.stateLaw 51)) dcCA1990 == some .binding
#guard ((queryFor L dcCA1990).bind fun q => force L dcCA1980 (hold dcCA1980 5 (.stateLaw 51)) false q).map (·.1)
  == some .persuasiveStrong
#guard pw dcCA1990 dcCA1980 == some false
#guard (canChangeStatus L dcCA1990 dcCA1980 none).map (·.2) == some .strongNeedsEnBanc
#guard pw dcCAenBanc dcCA1980 == some true
-- a court of last resort with no court-level row overrules itself at any bench (H1)
#guard (canChangeStatus L kySup1995 { kySup1995 with id := 94, date := 19900101 } none) == some (true, .lastResortSelf)

-- South Corp (F11): CCPA law binds the Federal Circuit, and district courts on patent law
#guard fo ccpa1980 (anon ccpa1980) fedCir1990 == some .binding
#guard fo ccpa1980 (hold ccpa1980 6 .federalPatent) ndill1990 == some .binding
#guard fo ccpa1980 (hold ccpa1980 7 .federalGeneral) ndill1990 == some .persuasive

-- M.A.P. v. Ryan: cross-system adoption (the Erie theorem's "absent adoption" case)
#guard fo dcCir1965 (hold dcCir1965 5 (.stateLaw 51)) dcSuper1990 == some .binding
#guard fo dcCir1975 (hold dcCir1975 5 (.stateLaw 51)) dcSuper1990 == some .persuasive

-- Erie (E1), both ways and both sides of 25 Apr 1938
#guard fo gaSup1930 (anon gaSup1930) ndga1950 == some .binding
#guard fo gaSup1930 (anon gaSup1930) ndga1935 == some .persuasive
#guard fo ca5in1975 (hold ca5in1975 8 (.stateLaw 11)) gaApp1996 == some .persuasive
#guard fo gaSup1995 (hold gaSup1995 9 .federalGeneral) ndtex2005 == some .persuasive

-- California conflict (S-CA, Auto Equity): both districts bind absent conflict; the superior court chooses
def caCands : List Cand :=
  [caApp1, caApp2].filterMap fun x =>
    candFor L E x (hold x 4 (.stateLaw 5) (some (if x.id == 8 then .yes else .no))) caSuper2010
#guard caCands.map (·.force) == [.bindingAbsentConflict, .bindingAbsentConflict]
#guard (resolve false (some .chooseOnConflict) caCands).map (·.answer) == [.yes, .no]
#guard split (resolve false none [caCands[0]!]) (resolve false none [caCands[1]!]) false == true
-- under an own-unit rule (IL, NY, FL), the superior court in district 2 follows district 2
#guard (resolve false (some .ownUnitThenAny) caCands).map (·.answer) == [.no]
-- and a binding SCOTUS holding ends the conflict
def scotusCand : Cand :=
  { holding := 99, answer := .yes, force := .binding, prec := scotusPrec, date := 20090101, ownUnit := false }
#guard (resolve false none (scotusCand :: caCands)).map (·.answer) == [.yes]

-- partial overruling (Georgia): notice falls, venue stands
#guard st 13 2 20000101 20000101 == .neg .overruled
#guard st 13 1 20000101 20000101 == .good
#guard st 13 0 20000101 20000101 == .unknown .partialScope

-- Ledbetter: supersession is prospective (two dates)
#guard st 11 3 20100101 20060101 == .good
#guard st 11 3 20100101 20080101 == .neg .superseded
#guard st 11 3 20080601 20080101 == .good
#guard appliesSupersededHolding
  (citeFacts L E dec (effs 11) ledbetter (hold ledbetter 3 .federalGeneral) ndtex2010 (some 20080101) false) == true
#guard appliesSupersededHolding
  (citeFacts L E dec (effs 11) ledbetter (hold ledbetter 3 .federalGeneral) ndtex2010 (some 20060101) false) == false
-- H2: with no conduct date the finding is not made; the low-confidence family is, and only on a holding-level match
#guard appliesSupersededHolding
  (citeFacts L E dec (effs 11) ledbetter (hold ledbetter 3 .federalGeneral) ndtex2010 none false) == false
#guard supersededConductUnknown
  (citeFacts L E dec (effs 11) ledbetter (hold ledbetter 3 .federalGeneral) ndtex2010 none false) == true
#guard supersededConductUnknown
  (citeFacts L E dec (effs 11) ledbetter (hold ledbetter 3 .federalGeneral) ndtex2010 none false false) == false
#guard appliesSupersededHolding
  (citeFacts L E dec (effs 11) ledbetter (hold ledbetter 3 .federalGeneral) ndtex2010 (some 20080101) false false) == false

-- unpublished 5th Cir. opinions: precedent before 1996, not after (F9)
#guard fo ca5unpub1999 (anon ca5unpub1999) ndtex2001 == some .persuasive
#guard fo ca5unpub1994 (anon ca5unpub1994) ndtex2001 == some .binding
#guard citesUnpublishedAsBinding
  (citeFacts L E dec [] ca5unpub1999 (anon ca5unpub1999) ndtex2001 (some 20010101) true) == true

-- trial courts bind no one (F13)
#guard fo ndtex2001 (anon ndtex2001) ndtex2005 == some .persuasive

-- Sunburst: a prospective overruling leaves earlier conduct under the old rule
def sunburst : List Effect :=
  (treatEffect [] (tr 9 14 13 19950101 .all (.prospectiveFrom 19950101))).toList
#guard status sunburst 0 20000101 19940101 == .good
#guard status sunburst 0 20000101 19960101 == .neg .overruled

-- revival (T3): the overruling decision is vacated in 1999, so the target is good law again
def revival : List Effect :=
  (treatEffect [{ id := 5, target := 14, by_ := none, date := 19990101, kind := .vacated, scope := .all }]
    (tr 9 14 13 19950101)).toList
#guard status revival 0 19970101 19970101 == .neg .overruled
#guard status revival 0 20000101 20000101 == .good

-- an en banc grant in a circuit whose rule is not in the tables: status unknown (D5), not silently good
#guard (histEffect L (L.epochAt ca5 19900101) []
  { id := 1, target := 6, by_ := none, date := 19900101, kind := .rehearingEnBancGranted, scope := .all }).map (·.eff)
  == some (.unknown .enBancRuleUnknown)

-- certificates
def gideonText := "Gideon v. Wainwright. We accept the contention. Betts v. Brady, 316 U.S. 455, should be overruled. Reversed."
def certIn (q : String) (start : Nat) (ev part : String) (auth : Option Bool := some true) : Cert.Input :=
  { kind := .treat .overruled, textSha := "g", start, stop := start + q.length, quote := q, evidence := ev, part,
    shas := ["g"], windows := [{ start0 := 0, stop0 := gideonText.length, text := gideonText }], ordered := true, authority := auth }
#guard Cert.check (certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:316 U.S. 455" "majority") == .ok
#guard Cert.check (certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 47 "cite:316 U.S. 455" "majority")
  == .fail .quoteMismatch
#guard Cert.check (certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:316 U.S. 455" "dissent")
  == .fail .partNotMajority
#guard Cert.check (certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:372 U.S. 335" "majority")
  == .fail .targetUnresolved
#guard Cert.check (certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:316 U.S. 455" "majority"
  (some false)) == .fail .noAuthority
def ptText := "Appellant's first point of error is overruled. Smith v. Jones."
#guard Cert.check { certIn "Appellant's first point of error is overruled" 0 "name:Smith Jones" "majority" with
  windows := [{ start0 := 0, stop0 := ptText.length, text := ptText }] } == .fail .disqualified
def rptText := "Smith v. Jones, 245 Ga. 1 (1980), overruled by Doe v. Roe, 265 Ga. 2 (1995)."
#guard Cert.check { certIn "Smith v. Jones, 245 Ga. 1 (1980), overruled by Doe v. Roe" 0 "cite:245 Ga. 1" "majority" with
  windows := [{ start0 := 0, stop0 := rptText.length, text := rptText }] } == .fail .disqualified

-- window hashes (TRUST.md): the checker recomputes the window's SHA-1 and compares it with the audit copy's
def gideonSha := "b8319fc7c01d2d25f7c28baecd637d719190b8c4"
def gideonWin (h : Option String) : Cert.Window :=
  { start0 := 0, stop0 := gideonText.length, text := gideonText, hash := h }
def certGideonH (h : Option String) : Cert.Input :=
  { certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:316 U.S. 455" "majority" with
    windows := [gideonWin h], hashRequired := true }
#guard Cert.check (certGideonH (some gideonSha)) == .ok
#guard Cert.check (certGideonH (some "0000000000000000000000000000000000000000")) == .fail .windowHash
#guard Cert.check (certGideonH none) == .fail .windowHash
-- a tampered window text no longer matches its recorded hash
#guard Cert.check { certGideonH (some gideonSha) with
  windows := [{ start0 := 0, stop0 := gideonText.length, text := gideonText.replace "Gideon" "Gidеon",
                hash := some gideonSha }] } == .fail .windowHash

-- the citation index: `cite:` evidence must resolve to the row's target node
def idx (k : String) (n : Nat) : Std.HashMap String Nat := ({} : Std.HashMap String Nat).insert k n
def certGideonI (m : Std.HashMap String Nat) : Cert.Input :=
  { certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:316 U.S. 455" "majority" with
    target := betts.id, citeIndex := some m }
#guard Cert.check (certGideonI (idx "316us455" betts.id)) == .ok
#guard Cert.check (certGideonI (idx "316us455" (betts.id + 1))) == .fail .targetUnresolved
#guard Cert.check (certGideonI {}) == .fail .targetUnresolved
-- FB-L2: an empty quote at an empty span is not a certificate
#guard Cert.check (certIn "" 48 "cite:316 U.S. 455" "majority") == .fail .quoteMismatch
-- FB-L3: any usable window may carry the quote; a bad window listed first does not shadow a good one
#guard Cert.check { certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:316 U.S. 455" "majority" with
  windows := [{ start0 := 0, stop0 := gideonText.length, text := gideonText.replace "Betts" "Bxtts" },
              { start0 := 0, stop0 := gideonText.length, text := gideonText }] } == .ok
-- name evidence keeps its rule (no name index)
#guard Cert.check { certGideonI {} with evidence := "name:Betts Brady" } == .ok

/-! ## Witness rows (round 4): an implicit overruling stated by a later court -/

def witText := "As we said, the overruling of Fleet Corporation v. Lustgarten, 280 U. S. 320, by Brady v. Roosevelt S. S. Co., 317 U. S. 575, settles it."
def witQuote := "the overruling of Fleet Corporation v. Lustgarten, 280 U. S. 320, by Brady v. Roosevelt S. S. Co., 317 U. S. 575"
/-- X = *Fleet Corp. v. Lustgarten*, Y = *Brady v. Roosevelt S.S. Co.*; the text is the later decision W's. -/
def witIn : Cert.Input :=
  { kind := .treat .overruled, textSha := "w", start := 12, stop := 12 + witQuote.length, quote := witQuote,
    evidence := "cite:280 U.S. 320", part := "majority", shas := ["w"],
    windows := [{ start0 := 0, stop0 := witText.length, text := witText }], ordered := true, authority := some true }
def witRow : Cert.Witness :=
  { known := true, explicit := false, changes := true, byEvidence := "cite:317 U.S. 575", by_ := 0,
    witnessOrdered := true, standing := true }
#guard Cert.checkWitness witIn witRow == .ok
#guard Cert.checkWitness witIn { witRow with explicit := true } == .witnessBadRow
#guard Cert.checkWitness witIn { witRow with changes := false } == .witnessBadRow
#guard Cert.checkWitness witIn { witRow with known := false } == .witnessBadRow
#guard Cert.checkWitness { witIn with part := "dissent" } witRow == .fail .partNotMajority
#guard Cert.checkWitness witIn { witRow with byEvidence := "cite:999 U.S. 1" } == .byUnresolved
#guard Cert.checkWitness witIn { witRow with byEvidence := "name:Brady Roosevelt" } == .ok
#guard Cert.checkWitness { witIn with ordered := false } witRow == .fail .targetLater
#guard Cert.checkWitness witIn { witRow with witnessOrdered := false } == .witnessEarlier
#guard Cert.checkWitness witIn { witRow with standing := false } == .witnessNoStanding
#guard Cert.checkWitness { witIn with authority := some false } witRow == .fail .noAuthority
#guard Cert.checkWitness { witIn with authority := none } witRow == .okUnverifiedBy

/-- **A witness row never changes status**: the event built from an admitted witness row (it carries the row's
`explicit` flag) has no status effect. The row only yields an `atRisk` finding naming the by-decision. -/
theorem witness_row_no_effect (c : Cert.Input) (w : Cert.Witness) (h : (Cert.checkWitness c w).admitted = true)
    (byHist : List HEvent) (tr : TEvent) (he : tr.explicit = w.explicit) : treatEffect byHist tr = none :=
  inferred_treatment_no_effect byHist tr (he.trans (Cert.checkWitness_inferred c w h))

/-! ## Round 5: recognised overrulings and operative words (DESIGN5.md)

*Brown v. Board of Education* (17 May 1954) never says it overrules *Plessy v. Ferguson* (1896). A later decision W
of the same court does. The sentences below are test sentences, not quotations (except Brown's own). -/

def recText := "We have since held otherwise. See Plessy v. Ferguson, 163 U. S. 537, overruled by Brown v. Board of Education, 347 U. S. 483, and the cases that followed."
def recQuote := "Plessy v. Ferguson, 163 U. S. 537, overruled by Brown v. Board of Education, 347 U. S. 483"
def recStart : Nat := ((recText.splitOn recQuote).headD "").length
/-- X = *Plessy*, Y = *Brown*; the text is the later decision W's. -/
def recIn : Cert.Input :=
  { kind := .treat .overruled, textSha := "w", start := recStart, stop := recStart + recQuote.length, quote := recQuote,
    evidence := "cite:163 U.S. 537", part := "majority", shas := ["w"],
    windows := [{ start0 := 0, stop0 := recText.length, text := recText }], ordered := true, authority := some true }
def recRow : Cert.Witness :=
  { known := true, explicit := false, changes := true, byEvidence := "cite:347 U.S. 483", by_ := 0,
    witnessOrdered := true, standing := true, claim := true, power := true, datesKnown := true }
-- recognised: W has power, both names are in the quote, the cue is a recognition cue
#guard Cert.checkRecognised recIn recRow == .recognised false
-- "overruled by" is a round-4 disqualifier: without recognition the row asserts nothing
#guard Cert.checkWitness recIn recRow == .fail .disqualified
#guard Cert.checkRecognised recIn { recRow with claim := false } == .witness (.fail .disqualified)
-- W with mere standing (a panel of the same court under a strong rule): never recognised
#guard Cert.checkRecognised recIn { recRow with power := false } == .witness (.fail .disqualified)
#guard Cert.checkRecognised recIn { recRow with datesKnown := false } == .witness (.fail .disqualified)
-- Y's power over X unknown: recognised, unverified (the effect is `unknown powerUnknown`)
#guard Cert.checkRecognised { recIn with authority := none } recRow == .recognised true
#guard !(Cert.checkRecognised { recIn with authority := some false } recRow).isRecognised
#guard !(Cert.checkRecognised { recIn with part := "dissent" } recRow).isRecognised
#guard !(Cert.checkRecognised { recIn with ordered := false } recRow).isRecognised
#guard !(Cert.checkRecognised recIn { recRow with witnessOrdered := false }).isRecognised
#guard !(Cert.checkRecognised recIn { recRow with standing := false }).isRecognised
#guard !(Cert.checkRecognised recIn { recRow with explicit := true }).isRecognised
-- the same evidence for X and Y
#guard !(Cert.checkRecognised recIn { recRow with byEvidence := "cite:163 U.S. 537" }).isRecognised
-- a negated statement
def recNotText := "Plessy v. Ferguson, 163 U. S. 537, was not overruled by Brown v. Board of Education, 347 U. S. 483."
#guard !(Cert.checkRecognised { recIn with
    quote := recNotText, start := 0, stop := recNotText.length,
    windows := [{ start0 := 0, stop0 := recNotText.length, text := recNotText }] } recRow).isRecognised
-- the round-4 witness example: Y is named in the quote, so with W's power it is recognised; without, it stays
-- an "at risk" witness row
#guard Cert.checkRecognised witIn { witRow with claim := true, power := true, datesKnown := true } == .recognised false
#guard Cert.checkRecognised witIn { witRow with claim := true, power := false, datesKnown := true } == .witness .ok
-- Y named only in the window, not in the quote: the round-4 check passes, recognition does not
def witShortQuote := "the overruling of Fleet Corporation v. Lustgarten, 280 U. S. 320"
def witShortIn : Cert.Input := { witIn with quote := witShortQuote, stop := 12 + witShortQuote.length }
def witClaim : Cert.Witness := { witRow with claim := true, power := true, datesKnown := true }
#guard Cert.checkRecognised witShortIn witClaim == .witness .ok

/-- *Plessy* (node 1), *Brown* (node 2, 17 May 1954) and a later decision W (node 3, dated 29 June 1992 here) of
the same court that says *Plessy* was overruled by *Brown*. -/
def plessyRow : TEvent :=
  { id := 1, by_ := 2, target := 1, date := 19540517, kind := .overruled, scope := .all, temporal := .unknown,
    explicit := false, recog := some { witness := 3, date := 19920629, power := true } }
-- the recognition is the one the checker's verdict gives
#guard Cert.recogOf (Cert.checkRecognised recIn recRow) 3 19920629 == plessyRow.recog
#guard Cert.recogOf (Cert.checkRecognised recIn { recRow with power := false }) 3 19920629 == none
def plessyEffs : List Effect := recogEffects [] [] plessyRow
#guard plessyEffs.length == 2
#guard plessyEffs.all (·.rule == .recognised) && plessyEffs.all (·.actor == some 2)
-- at risk only: no effect
#guard (recogEffects [] [] { plessyRow with recog := none }).isEmpty
-- W vacated: the negative lapses, the unknown stays (Y stands); Y vacated: both lapse
def wVacated : List HEvent := [{ id := 9, target := 3, by_ := none, date := 19950101, kind := .vacated, scope := .all }]
#guard status (recogEffects [] wVacated plessyRow) 0 19940101 19940101 == .neg .overruled
#guard status (recogEffects [] wVacated plessyRow) 0 19960101 19960101 == .unknown .recognisedLater
#guard status (recogEffects wVacated [] plessyRow) 0 19960101 19960101 == .good
-- Y's power unknown: never negative
#guard status (recogEffects [] [] { plessyRow with powerKnown := false }) 0 20000101 20000101 == .unknown .powerUnknown
-- a partial recognition ("overruled in part by"): partly negative on the whole decision, never negative
#guard status (recogEffects [] [] { plessyRow with scope := .someIssue }) 0 20000101 20000101 == .unknown .partialScope

/-- **The Plessy timeline** (round 5): good law until the day before *Brown*; `unknown recognisedLater` from
*Brown* (17 May 1954) until the day before the later court says so; overruled from that day. -/
theorem plessy_timeline :
    status plessyEffs 0 19540516 19540516 = .good ∧
    status plessyEffs 0 19540517 19540517 = .unknown .recognisedLater ∧
    status plessyEffs 0 19920628 19920628 = .unknown .recognisedLater ∧
    status plessyEffs 0 19920629 19920629 = .neg .overruled := by decide

/-- Brown's own sentence (347 U.S. 483, 494-95). -/
def brownText := "Whatever may have been the extent of psychological knowledge at the time of Plessy v. Ferguson, this finding is amply supported by modern authority. Any language in Plessy v. Ferguson contrary to this finding is rejected. We conclude that in the field of public education the doctrine of \"separate but equal\" has no place."
def brownQuote := "Any language in Plessy v. Ferguson contrary to this finding is rejected."
def brownStart : Nat := ((brownText.splitOn brownQuote).headD "").length
def brownIn : Cert.Input :=
  { kind := .treat .disapproved, textSha := "b", start := brownStart, stop := brownStart + brownQuote.length,
    quote := brownQuote, evidence := "name:Plessy Ferguson", part := "majority", shas := ["b"],
    windows := [{ start0 := 0, stop0 := brownText.length, text := brownText }], ordered := true, authority := some true }
-- operative words: admitted with the claim; the round-4 check has no such cue for `disapproved`
#guard Cert.checkOperative brownIn true == .ok
#guard Cert.check brownIn == .fail .noCue
-- not the whole case: the scope is demoted
#guard Cert.wholeCase brownQuote == false
#guard Cert.wholeCase "Plessy v. Ferguson is no longer good law." == true
-- a limiting phrase undoes a whole-case phrase
#guard Cert.wholeCase "Race Horse is repudiated to the extent it held that treaty rights can be impliedly extinguished." == false
#guard Cert.checkOperative { brownIn with kind := .treat .overruled } true == .fail .operativeBadRow
#guard Cert.checkOperative brownIn false == .fail .operativeBadRow
#guard Cert.checkOperative { brownIn with part := "dissent" } true == .fail .partNotMajority
-- courts reject arguments constantly: an argument is not a case
def brownArgText := "We reject the argument that Plessy v. Ferguson controls this case."
def brownArgIn : Cert.Input :=
  { brownIn with
    quote := brownArgText, start := 0, stop := brownArgText.length,
    windows := [{ start0 := 0, stop0 := brownArgText.length, text := brownArgText }] }
#guard Cert.checkOperative brownArgIn true == .fail .disqualified
-- the target must be named in the quote itself, not only in the window
def brownTail := "contrary to this finding is rejected."
#guard Cert.checkOperative { brownIn with
    quote := brownTail,
    start := brownStart + (brownQuote.length - brownTail.length), stop := brownStart + brownQuote.length } true
  == .fail .targetUnresolved
-- classes
#guard Cert.classOf true false brownQuote == .operativeWords
#guard Cert.classOf true false "Betts v. Brady is overruled." == .selfAnnounced
#guard Cert.classOf false true recQuote == .recognised
#guard Cert.classOf false false witQuote == .atRiskWitness

/-- Brown's operative words on Plessy: an explicit `disapproved` row whose scope is demoted (not the whole case). -/
def brownEv : TEvent :=
  { id := 2, by_ := 2, target := 1, date := 19540517, kind := .disapproved, scope := demote .all, temporal := .unknown,
    explicit := true }
#guard status (treatEffects [] brownEv) 0 19540516 19540516 == .good
#guard status (treatEffects [] brownEv) 0 19600101 19600101 == .unknown .partialScope
#guard status (treatEffects [] { brownEv with scope := .all }) 0 19600101 19600101 == .neg .overruled
-- both rows together: the timeline the model now gives for Plessy
#guard status (treatEffects [] brownEv ++ plessyEffs) 0 19540516 19540516 == .good
#guard status (treatEffects [] brownEv ++ plessyEffs) 0 19540517 19540517 == .unknown .recognisedLater
#guard status (treatEffects [] brownEv ++ plessyEffs) 0 19920629 19920629 == .neg .overruled

/-- **No recognised effect without the checker's verdict and W's power**: the runner sets an event's recognition
with `Cert.recogOf` from the recognised check; when W lacks power over X the check never recognises the row
(`Cert.checkRecognised_needs_power`), the event carries no recognition and has no recognised effect. With
`witness_row_no_effect`, such a row has no status effect at all. -/
theorem recognised_effect_needs_power (c : Cert.Input) (w : Cert.Witness) (hp : w.power = false)
    (wn : Nat) (d : Date) (byHist wHist : List HEvent) (tr : TEvent)
    (hr : tr.recog = Cert.recogOf (Cert.checkRecognised c w) wn d) : recogEffects byHist wHist tr = [] := by
  apply witness_without_claim_no_effect
  rw [hr]
  simp [Cert.recogOf, Cert.checkRecognised_needs_power c w hp]

/-- **A recognised row is never an explicit row**: the recognised check passes only on `explicit = 0`, so the
event's `treatEffect` is none: its only effects are the two recognised ones. -/
theorem recognised_row_only_recog_effects (c : Cert.Input) (w : Cert.Witness)
    (h : (Cert.checkRecognised c w).isRecognised = true) (byHist : List HEvent) (tr : TEvent)
    (he : tr.explicit = w.explicit) : treatEffect byHist tr = none :=
  inferred_treatment_no_effect byHist tr (he.trans (Cert.checkRecognised_sound c w h).2.2.2.2.2.1)

/-! ## Round 6: anchored history rows (`round6/history/DESIGN6.md` §4)

A reviewing court's opinion: the head matter names the decision below; the judgment line is at the end. The two
quotes sit in different windows of the same text. -/

def ancHead := "Certiorari to the United States Court of Appeals for the Fifth Circuit. Reported below: 100 F. 2d 1. On the former appeal the Court of Appeals reversed, 90 F. 2d 5. "
def ancTail := "Mr. Justice X delivered the opinion of the Court. The judgment of the Court of Appeals is reversed. It is so ordered."
def ancText := ancHead ++ ancTail
def ancDisp := "The judgment of the Court of Appeals is reversed."
/-- The character offset of the first occurrence of `pat` in `s`. -/
def offOf (s pat : String) : Nat := ((s.splitOn pat).headD "").length
/-- One window for the head matter, one for the rest (with the digests the audit copy recorded, if any). -/
def ancWins (hh ht : Option String := none) : List Cert.Window :=
  [{ start0 := 0, stop0 := ancHead.length, text := ancHead, hash := hh },
   { start0 := ancHead.length, stop0 := ancText.length, text := ancTail, hash := ht }]
/-- The disposition certificate of the row "decision 7 (100 F.2d 1) reversed by this decision". -/
def ancIn : Cert.Input :=
  { kind := .hist .reversed, textSha := "a", start := offOf ancText ancDisp,
    stop := offOf ancText ancDisp + ancDisp.length, quote := ancDisp, evidence := "cite:100 F.2d 1",
    part := "majority", shas := ["a"], windows := ancWins, ordered := true, authority := some true, target := 7,
    citeIndex := some (idx "100f2d1" 7) }
def anc (q : String) (part : String := "headmatter") : Cert.Anchor :=
  { start := offOf ancText q, stop := offOf ancText q + q.length, quote := q, part }
def ancOk := anc "Reported below: 100 F. 2d 1."
def ancNoCue := anc "below: 100 F. 2d 1."
def ancNoCite := anc "Certiorari to the United States Court of Appeals for the Fifth Circuit."
def ancFormer := anc "On the former appeal the Court of Appeals reversed, 90 F. 2d 5."
def ancFormerIn : Cert.Input := { ancIn with evidence := "cite:90 F.2d 5", citeIndex := none }
-- the citation is not within the disposition quote's window: the one-quote certificate fails; with the anchor it passes
#guard Cert.check ancIn == .fail .targetUnresolved
#guard Cert.checkAnchored ancIn ancOk == .ok
#guard Cert.checkHistory ancIn none == .fail .targetUnresolved
#guard Cert.checkHistory ancIn (some ancOk) == .ok
-- check 1: the anchor quote at its offset, not empty
#guard Cert.checkAnchored ancIn { ancOk with start := ancOk.start + 1, stop := ancOk.stop + 1 } == .fail .anchorMismatch
#guard Cert.checkAnchored ancIn { ancOk with quote := "", stop := ancOk.start } == .fail .anchorMismatch
-- check 2: an anchor cue
#guard Cert.checkAnchored ancIn ancNoCue == .fail .anchorNoCue
-- check 3: an earlier proceeding is not the decision under review
#guard Cert.checkAnchored ancFormerIn ancFormer == .fail .anchorDisqualified
-- check 4: the evidence in the anchor quote itself (it is in the anchor's window here), and through the index
#guard Cert.checkAnchored ancIn ancNoCite == .fail .anchorUnresolved
#guard Cert.checkAnchored { ancIn with target := 8 } ancOk == .fail .anchorUnresolved
#guard Cert.checkAnchored { ancIn with citeIndex := none, target := 8 } ancOk == .ok
#guard Cert.checkAnchored { ancIn with evidence := "name:Fifth Circuit" } ancNoCite == .ok
#guard Cert.checkAnchored { ancIn with evidence := "name:Sixth Circuit" } ancNoCite == .fail .anchorUnresolved
#guard Cert.checkAnchored { ancIn with evidence := "100 F.2d 1" } ancOk == .fail .anchorUnresolved
-- check 5: the anchor's part
#guard Cert.checkAnchored ancIn (anc "Reported below: 100 F. 2d 1." "dissent") == .fail .anchorPart
#guard Cert.checkAnchored ancIn (anc "Reported below: 100 F. 2d 1." "majority") == .ok
-- check 6: the disposition quote keeps every check of `check` but the target evidence
#guard Cert.checkAnchored { ancIn with part := "dissent" } ancOk == .fail .partNotMajority
#guard Cert.checkAnchored { ancIn with part := "headmatter" } ancOk == .fail .partNotMajority
#guard Cert.checkAnchored { ancIn with kind := .hist .vacated } ancOk == .fail .noCue
#guard Cert.checkAnchored { ancIn with start := ancIn.start + 1, stop := ancIn.stop + 1 } ancOk == .fail .quoteMismatch
#guard Cert.checkAnchored { ancIn with shas := ["b"] } ancOk == .fail .shaUnknown
#guard Cert.checkAnchored { ancIn with ordered := false } ancOk == .fail .targetLater
#guard Cert.checkAnchored { ancIn with authority := some false } ancOk == .fail .noAuthority
#guard Cert.checkAnchored { ancIn with authority := none } ancOk == .okUnverifiedBy
def ancWould := "The dissent would reverse; the judgment is reversed."
def ancWouldIn : Cert.Input :=
  { ancIn with
    quote := ancWould, start := ancHead.length, stop := ancHead.length + ancWould.length,
    windows := [{ start0 := 0, stop0 := ancHead.length, text := ancHead },
                { start0 := ancHead.length, stop0 := ancHead.length + ancWould.length, text := ancWould }] }
#guard Cert.checkAnchored ancWouldIn ancOk == .fail .disqualified
-- window hashes: each quote's own window must match its recorded digest
def ancInH (hh ht : Option String) : Cert.Input := { ancIn with hashRequired := true, windows := ancWins hh ht }
def ancBadSha := "0000000000000000000000000000000000000000"
#guard Cert.checkAnchored (ancInH (some (Sha1.hex ancHead)) (some (Sha1.hex ancTail))) ancOk == .ok
#guard Cert.checkAnchored (ancInH (some ancBadSha) (some (Sha1.hex ancTail))) ancOk == .fail .anchorMismatch
#guard Cert.checkAnchored (ancInH none (some (Sha1.hex ancTail))) ancOk == .fail .anchorMismatch
#guard Cert.checkAnchored (ancInH (some (Sha1.hex ancHead)) (some ancBadSha)) ancOk == .fail .windowHash
-- another text's window never carries the anchor: the anchor is read over the certificate's own windows
def ancOtherText := "Reported below: 100 F. 2d 1. Affirmed."
def ancOtherWins : List Cert.Window := [{ start0 := 0, stop0 := ancOtherText.length, text := ancOtherText }]
def ancForeign : Cert.Anchor := { start := 0, stop := 28, quote := "Reported below: 100 F. 2d 1.", part := "headmatter" }
#guard Cert.checkAnchored ancIn ancForeign == .fail .anchorMismatch
#guard Cert.checkAnchored { ancIn with windows := ancOtherWins } ancForeign == .fail .noWindow

/-! ## Round 7: joined certificates, doctrine rows, history claims (`round7/DESIGN7.md` §2–3)

Test sentences, not quotations (except Brown's). An overruling stated across two sentences: the cases are named in
one sentence, the act ("Those cases are overruled.") is in a later one. -/

def jFar := "In Brown v. White, 200 U. S. 2, the Court sustained a tax on the mails."
def jFill := String.join (List.replicate 12 "The question has come back to us in many forms. ")
def jDis := "As the dissent notes, Smith v. Jones, 100 U. S. 1, and Brown v. White, 200 U. S. 2, were never questioned."
def jNear := "In Smith v. Jones, 100 U. S. 1, and Brown v. White, 200 U. S. 2, this Court held that a State may tax the mails."
def jMid := "We now hold otherwise."
def jMain := "Those cases are overruled."
def jNoAna := "The rule of the mails is overruled."
def jText := jFar ++ " " ++ jFill ++ jDis ++ " " ++ jNear ++ " " ++ jMid ++ " " ++ jMain ++ " " ++ jNoAna
/-- A joined line quoting `q` of text `txt`. -/
def jl (txt q : String) (rel : Cert.JRel := .antecedent) (part : String := "majority") (label : String := "") :
    Cert.Joined :=
  { rel, start := offOf txt q, stop := offOf txt q + q.length, quote := q, part, label }
/-- The row "this decision overrules Brown v. White (200 U.S. 2)", main quote `q` (one window: the whole text). -/
def jIn (q : String := jMain) : Cert.Input :=
  { kind := .treat .overruled, textSha := "j", start := offOf jText q, stop := offOf jText q + q.length, quote := q,
    evidence := "cite:200 U.S. 2", part := "majority", shas := ["j"],
    windows := [{ start0 := 0, stop0 := jText.length, text := jText }], ordered := true, authority := some true }
def jNearL := jl jText jNear
def jFarL := jl jText jFar
def jDisL := jl jText jDis
def jWinL := jl jText "this Court held that a State may tax the mails."
/-- The same row with two windows: the cases' sentence, and the act's (which names no case). -/
def jSplitIn : Cert.Input :=
  { jIn with windows := [{ start0 := 0, stop0 := offOf jText jMid, text := (jText.take (offOf jText jMid)).toString },
                         { start0 := offOf jText jMid, stop0 := jText.length,
                           text := (jText.drop (offOf jText jMid)).toString }] }
-- the act names no case: the one-quote certificate fails; with the antecedent sentence it passes
#guard Cert.checkTreatment jSplitIn true .plain [] == .fail .targetUnresolved
#guard Cert.checkTreatment jSplitIn true .plain [jNearL] == .ok
#guard Cert.checkTreatment jIn true .plain [jNearL] == .ok
#guard Cert.checkTreatment (jIn) true .plain [] == Cert.check (jIn)
-- check 1: the joined quote at its offset in the row's own text; one or two lines
#guard Cert.checkTreatment jIn true .plain [{ jNearL with start := jNearL.start + 1, stop := jNearL.stop + 1 }]
  == .fail .joinedMismatch
#guard Cert.checkTreatment jIn true .plain [{ jNearL with quote := "", stop := jNearL.start }] == .fail .joinedMismatch
#guard Cert.checkTreatment jIn true .plain [jNearL, jWinL] == .ok
#guard Cert.checkTreatment jIn true .plain [jNearL, jNearL, jNearL] == .fail .joinedMismatch
#guard Cert.checkJoined jIn true .plain [] == .fail .joinedMismatch
-- check 2: the opinion of the court only
#guard Cert.checkTreatment jIn true .plain [{ jNearL with part := "dissent" }] == .fail .joinedPart
#guard Cert.checkTreatment jIn true .plain [{ jNearL with part := "headmatter" }] == .fail .joinedPart
#guard Cert.checkTreatment jIn true .plain [{ jNearL with part := "perCuriam" }] == .ok
-- check 3: a dissent's account of the cases
#guard Cert.checkTreatment jIn true .plain [jDisL] == .fail .joinedDisqualified
-- check 4: the relation. Too far before the act (the 300-character gap), after the act, no anaphor in the act, no
-- cue of the kind in the act, a doctrine tie on a row that is not a doctrine row
#guard Cert.checkTreatment jIn true .plain [jFarL] == .fail .joinedRelation
#guard Cert.checkTreatment jIn true .plain [jl jText jNoAna] == .fail .joinedRelation
#guard Cert.checkTreatment (jIn jNoAna) true .plain [jNearL] == .fail .joinedRelation
#guard Cert.checkTreatment { jIn with kind := .treat .abrogated } true .plain [jNearL] == .fail .joinedRelation
#guard Cert.checkTreatment jIn true .plain [{ jNearL with rel := .doctrineTie, label := "tax the mails" }]
  == .fail .joinedRelation
#guard Cert.joinedGapMax == 300
-- check 5: the evidence inside a joined quote (here it is in the window, not in the quote)
#guard Cert.checkTreatment jIn true .plain [jWinL] == .fail .joinedUnresolved
#guard Cert.checkTreatment jIn true .plain [jWinL, jWinL] == .fail .joinedUnresolved
#guard Cert.checkTreatment { jIn with citeIndex := some (idx "200us2" 7), target := 7 } true .plain [jNearL] == .ok
#guard Cert.checkTreatment { jIn with citeIndex := some (idx "200us2" 7), target := 8 } true .plain [jNearL]
  == .fail .joinedUnresolved
-- check 6: the row's own check on the act, in its mode
#guard Cert.checkTreatment { jIn with part := "dissent" } true .plain [jNearL] == .fail .partNotMajority
#guard Cert.checkTreatment { jIn with ordered := false } true .plain [jNearL] == .fail .targetLater
#guard Cert.checkTreatment { jIn with authority := some false } true .plain [jNearL] == .fail .noAuthority
#guard Cert.checkTreatment { jIn with authority := none } true .plain [jNearL] == .okUnverifiedBy
#guard Cert.checkTreatment jIn true .operative [jNearL] == .fail .operativeBadRow
-- window hashes: the joined quote's window must match its recorded digest
def jInH (h : Option String) : Cert.Input :=
  { jSplitIn with
    hashRequired := true,
    windows := [{ start0 := 0, stop0 := offOf jText jMid, text := (jText.take (offOf jText jMid)).toString, hash := h },
                { start0 := offOf jText jMid, stop0 := jText.length, text := (jText.drop (offOf jText jMid)).toString,
                  hash := some (Sha1.hex (jText.drop (offOf jText jMid)).toString) }] }
#guard Cert.checkTreatment (jInH (some (Sha1.hex (jText.take (offOf jText jMid)).toString))) true .plain [jNearL] == .ok
#guard Cert.checkTreatment (jInH (some ancBadSha)) true .plain [jNearL] == .fail .joinedMismatch
#guard Cert.checkTreatment (jInH none) true .plain [jNearL] == .fail .joinedMismatch
-- another text's window never carries a joined quote
def jForeignQ := jNear.replace "tax the mails" "tax the roads"
def jForeignWins : List Cert.Window :=
  [{ start0 := offOf jText jNear, stop0 := offOf jText jNear + jForeignQ.length, text := jForeignQ }]
def jForeignL : Cert.Joined := { jNearL with quote := jForeignQ }
#guard Cert.checkTreatment jIn true .plain [jForeignL] == .fail .joinedMismatch
#guard Cert.checkTreatment { jIn with windows := jIn.windows ++ jForeignWins } true .plain [jForeignL] == .ok

/-! Doctrine rows: Brown's own sentence rejects a doctrine; an earlier sentence of the same opinion ties the doctrine
to *Plessy*. -/

def dTie := "The doctrine of \"separate but equal\" did not make its appearance in this Court until 1896 in the case of Plessy v. Ferguson, 163 U. S. 537, involving not education but transportation."
def dNoTie := "Plessy v. Ferguson, 163 U. S. 537, upheld \"separate but equal\" railway cars."
def dNoLabel := "The rule of Plessy v. Ferguson, 163 U. S. 537, governed railway cars."
def dArg := "The argument that \"separate but equal\" has no place is rejected."
def dMain := "We conclude that in the field of public education the doctrine of \"separate but equal\" has no place."
def dText := dTie ++ " " ++ dNoTie ++ " " ++ dNoLabel ++ " " ++ dArg ++ " " ++ dMain
def dIn (q : String := dMain) : Cert.Input :=
  { kind := .treat .disapproved, textSha := "d", start := offOf dText q, stop := offOf dText q + q.length, quote := q,
    evidence := "cite:163 U.S. 537", part := "majority", shas := ["d"],
    windows := [{ start0 := 0, stop0 := dText.length, text := dText }], ordered := true, authority := some true }
def dl (q : String) (label : String := "separate but equal") : Cert.Joined := jl dText q .doctrineTie "majority" label
def dTieL := dl dTie
#guard Cert.checkTreatment (dIn) true .doctrine [dTieL] == .ok
-- the plain check has no cue for `disapproved` in "has no place"
#guard Cert.checkTreatment (dIn) true .plain [] == .fail .noCue
-- doctrineBadRow: no tie line, another kind, an implicit row, an antecedent line only
#guard Cert.checkTreatment (dIn) true .doctrine [] == .fail .doctrineBadRow
#guard Cert.checkTreatment { dIn with kind := .treat .overruled } true .doctrine [dTieL] == .fail .doctrineBadRow
#guard Cert.checkTreatment (dIn) false .doctrine [dTieL] == .fail .doctrineBadRow
#guard Cert.checkTreatment (dIn) true .doctrine [{ dTieL with rel := .antecedent }] == .fail .doctrineBadRow
-- the tie: a tie cue, the label in both quotes, a label of two words and eight characters
#guard Cert.checkTreatment (dIn) true .doctrine [dl dNoTie] == .fail .joinedRelation
#guard Cert.checkTreatment (dIn) true .doctrine [dl dNoLabel] == .fail .joinedRelation
#guard Cert.checkTreatment (dIn) true .doctrine [dl dTie "equal"] == .fail .joinedRelation
#guard Cert.checkTreatment (dIn) true .doctrine [dl dTie "public education"] == .fail .joinedRelation
#guard Cert.checkTreatment (dIn) true .plain [dTieL] == .fail .joinedRelation
-- the main quote in doctrine mode: the operative disqualifiers apply
#guard Cert.checkTreatment (dIn dArg) true .doctrine [dTieL] == .fail .disqualified
#guard Cert.checkTreatment { dIn with authority := none } true .doctrine [dTieL] == .okUnverifiedBy
-- uniqueness inside the table: one label tied to two targets fails on every row that carries it
#guard Cert.tieLabels [dTieL, jNearL] == ["separatebutequal"]
def uRows : List Cert.DoctrineRow :=
  [{ target := 1, labels := ["separatebutequal"], text := true }, { target := 2, labels := ["separatebutequal"], text := true },
   { target := 3, labels := ["clearandpresentdanger"], text := true },
   { target := 4, labels := ["clearandpresentdanger"], text := false }]
#guard Cert.doctrineFinal uRows (uRows.headD default) .ok == .fail .doctrineAmbiguous
#guard Cert.doctrineFinal uRows (uRows.getD 2 default) .ok == .ok
#guard Cert.doctrineFinal uRows (uRows.getD 1 default) (.fail .noCue) == .fail .noCue
#guard Cert.doctrineFinal (uRows.drop 1) (uRows.getD 1 default) .okUnverifiedBy == .okUnverifiedBy
#guard Cert.ambiguousLabel (uRows.filter (·.labels.contains "separatebutequal")) "separatebutequal" == true
-- the effect: always demoted; a doctrine row never makes Plessy overruled, the recognised row still does
def brownAllEv : TEvent := { brownEv with scope := .all }
#guard status (doctrineEffects [] brownAllEv) 0 19540516 19540516 == .good
#guard status (doctrineEffects [] brownAllEv) 0 19600101 19600101 == .unknown .partialScope
#guard status (treatEffects [] brownAllEv) 0 19600101 19600101 == .neg .overruled
#guard status (doctrineEffects [] brownAllEv ++ plessyEffs) 0 19920629 19920629 == .neg .overruled
#guard status (doctrineEffects [] { brownAllEv with scope := .issues [3] }) 3 19600101 19600101 == .unknown .partialScope
-- classes
#guard Cert.classOf7 true false true dMain == .doctrine
#guard Cert.classOf7 true false false dMain == .operativeWords
#guard Cert.classOf7 false false true dMain == .atRiskWitness
#guard Cert.OClass.doctrine.idx == 3 && Cert.OClass.atRiskWitness.idx == 4

/-! History claims: a Supreme Court order-list entry whose disposition is printed as head matter only, and "set
aside" as a vacatur. -/

def oText := "No. 12-345. Smith v. Jones. C. A. 5th Cir. Motion for leave to proceed denied. Certiorari denied. Judgment modified. Reported below: 500 F. 3d 1."
def oIn (q : String := "Certiorari denied.") (k : HKind := .certDenied) (part : String := "headmatter") : Cert.Input :=
  { kind := .hist k, textSha := "o", start := offOf oText q, stop := offOf oText q + q.length, quote := q,
    evidence := "cite:500 F.3d 1", part, shas := ["o"], windows := [{ start0 := 0, stop0 := oText.length, text := oText }],
    ordered := true, authority := some true }
def oClaim : Cert.HClaims := { orderHead := true, scotus := true, date := 20140106 }
#guard Cert.checkHistory7 (oIn) none oClaim == .ok
-- without the claim head matter fails as before; the claim does not admit a separate opinion
#guard Cert.checkHistory7 (oIn) none {} == .fail .partNotMajority
#guard Cert.checkHistory7 (oIn) none {} == Cert.checkHistory (oIn) none
#guard Cert.checkHistory7 (oIn (part := "dissent")) none oClaim == .fail .partNotMajority
#guard Cert.checkHistory7 (oIn (part := "majority")) none {} == .ok
-- the conditions: the Supreme Court, from 2013, a listed kind, an order-line cue, at most 400 characters
#guard Cert.checkHistory7 (oIn) none { oClaim with scotus := false } == .fail .orderHeadNotAllowed
#guard Cert.checkHistory7 (oIn) none { oClaim with date := 20121231 } == .fail .orderHeadNotAllowed
#guard Cert.checkHistory7 (oIn) none { oClaim with date := 20130101 } == .ok
#guard Cert.checkHistory7 (oIn) none { oClaim with date := 0 } == .fail .orderHeadNotAllowed
#guard Cert.checkHistory7 (oIn "Judgment modified." .modified) none oClaim == .fail .orderHeadNotAllowed
#guard Cert.checkHistory7 (oIn "Motion for leave to proceed denied.") none oClaim == .fail .orderHeadNotAllowed
def oLongText := "Certiorari denied, " ++ String.join (List.replicate 9 "the petition having been considered with care and at length, ") ++ "and leave is refused. Reported below: 500 F. 3d 1."
def oLongQ := (oLongText.take (offOf oLongText " Reported")).toString
def oLongIn : Cert.Input :=
  { oIn with
    start := 0, stop := oLongQ.length, quote := oLongQ,
    windows := [{ start0 := 0, stop0 := oLongText.length, text := oLongText }] }
#guard oLongQ.length > 400
#guard Cert.checkHistory7 oLongIn none oClaim == .fail .orderHeadNotAllowed
#guard Cert.checkHistory7 { oLongIn with part := "majority" } none {} == .ok
-- the order-list wording with the court's name inside ("a ... b": a, then b later; lead ruling D7-9)
def o2Text := "No. 13-1. Doe v. Roe. Motion denied; petition for writ of certiorari to the Court of Appeals pending. Petition for writ of certiorari to the United States Court of Appeals for the Fifth Circuit denied. Reported below: 500 F. 3d 1."
def o2In (q : String) : Cert.Input :=
  { oIn with
    start := offOf o2Text q, stop := offOf o2Text q + q.length, quote := q,
    windows := [{ start0 := 0, stop0 := o2Text.length, text := o2Text }] }
#guard Cert.checkHistory7 (o2In "Petition for writ of certiorari to the United States Court of Appeals for the Fifth Circuit denied.")
  none oClaim == .ok
#guard Cert.checkHistory7 (o2In "Motion denied; petition for writ of certiorari to the Court of Appeals pending.") none oClaim
  == .fail .orderHeadNotAllowed
#guard Cert.orderLineHit "a b c" "a ... c" && !Cert.orderLineHit "c b a" "a ... c" && Cert.orderLineHit "x a ... c" "a ... c"
-- an anchored row under the claim
def oAnc : Cert.Anchor :=
  { start := offOf oText "Reported below: 500 F. 3d 1.", stop := offOf oText "Reported below: 500 F. 3d 1." + 28,
    quote := "Reported below: 500 F. 3d 1.", part := "headmatter" }
#guard Cert.checkHistory7 (oIn) (some oAnc) oClaim == .ok
#guard Cert.checkHistory7 (oIn) (some oAnc) {} == .fail .partNotMajority
#guard Cert.checkHistory7 (oIn) (some oAnc) {} == Cert.checkAnchored (oIn) oAnc
def sText := "In Doe v. Roe, 300 F. 2d 3, the Court of Appeals held for the State. The judgment of the Court of Appeals is set aside."
def sIn (k : HKind := .vacated) : Cert.Input :=
  { kind := .hist k, textSha := "s", start := offOf sText "The judgment of the Court of Appeals is set aside.",
    stop := offOf sText "The judgment of the Court of Appeals is set aside." + 50,
    quote := "The judgment of the Court of Appeals is set aside.", evidence := "cite:300 F.2d 3", part := "majority",
    shas := ["s"], windows := [{ start0 := 0, stop0 := sText.length, text := sText }], ordered := true,
    authority := some true }
#guard Cert.checkHistory7 (sIn) none { setAside := true } == .ok
#guard Cert.checkHistory7 (sIn) none {} == .fail .noCue
#guard Cert.checkHistory7 (sIn .reversed) none { setAside := true } == .fail .noCue
#guard Cert.checkHistory7 (sIn) none { setAside := true, orderHead := true } == .ok

/-! Round 8 (`round8/DESIGN8.md` §4): bridge evidence. O (node 30) is a Supreme Court order that names only its own
docket; W (node 40, dated after O) cites X (node 5, 123 F. 3d 456) and then O (577 U. S. 1001). The index also has
577 U. S. 100 (node 31, a prefix of O's citation), 200 F. 3d 9 (node 6) and 576 U. S. 900 (node 32). -/

def bIdx : Std.HashMap String Nat :=
  ((((({} : Std.HashMap String Nat).insert "123f3d456" 5).insert "577us1001" 30).insert "577us100" 31).insert
    "200f3d9" 6).insert "576us900" 32
/-- the key lengths, longest first (LEAN8 L8-3) -/
def bLens : List Nat := [9, 8, 7]
def bOText := "No. 15-1052. Smith v. Jones. Certiorari denied."
/-- O's own disposition; its evidence (X's citation) is not in O's text. -/
def bIn : Cert.Input :=
  { kind := .hist .certDenied, textSha := "o8", start := offOf bOText "Certiorari denied.",
    stop := offOf bOText "Certiorari denied." + 18, quote := "Certiorari denied.", evidence := "cite:123 F.3d 456",
    part := "majority", shas := ["o8"], windows := [{ start0 := 0, stop0 := bOText.length, text := bOText }],
    ordered := true, authority := some true, target := 5, citeIndex := some bIdx }
/-- A bridge line whose quote `q` is in W's text `txt` (by default "See " ++ q ++ "."). -/
def bw (q : String) (txt : String := "See " ++ q ++ ".") : Cert.Bridge :=
  { w := 40, wSha := "w8", windows := [{ start0 := 0, stop0 := txt.length, text := txt }], start := offOf txt q,
    stop := offOf txt q + q.length, quote := q, wDate := 20170101, oDate := 20160111, actor := 30, lens := bLens }
def bGood := "Smith v. Jones, 123 F. 3d 456 (CA5 2015), cert. denied, 577 U. S. 1001 (2016)"
def bGoodB := bw bGood
#guard Cert.checkBridge bIn bGoodB {} == .ok
-- without the bridge line the row is round 7's (X's citation is not in O's text)
#guard Cert.checkHistory8 bIn none none {} == .fail .targetUnresolved
#guard Cert.checkHistory8 bIn none none {} == Cert.checkHistory7 bIn none {}
#guard Cert.checkHistory8 bIn none (some bGoodB) {} == .ok
-- the positions: X's citation at 16, its end at 29, the cue at 42, O's citation at 56
#guard Cert.bridgeP1 bIn bGoodB == some 16 && Cert.bridgeXEnd bIn bGoodB == some 29 &&
  Cert.bridgeP2 bIn bGoodB 16 == some 42 && Cert.bridgeActorCite bIn bGoodB 42 == some (56, 30)
-- step 1: the quote at its offset in W's text, at most 600 characters
#guard Cert.checkBridge bIn { bGoodB with start := bGoodB.start + 1, stop := bGoodB.stop + 1 } {} == .fail .bridgeMismatch
#guard Cert.checkBridge bIn { bGoodB with windows := [] } {} == .fail .bridgeMismatch
#guard Cert.checkBridge bIn { bGoodB with quote := "", stop := bGoodB.start } {} == .fail .bridgeMismatch
def bLong := "Smith v. Jones, 123 F. 3d 456 (CA5 2015) (" ++
  String.join (List.replicate 12 "the panel considering the matter with care and at length, ") ++
  "), cert. denied, 577 U. S. 1001 (2016)"
#guard bLong.length > 600
#guard Cert.checkBridge bIn (bw bLong) {} == .fail .bridgeMismatch
#guard Cert.checkBridge bIn { bGoodB with windows := [{ start0 := 0, stop0 := 4, text := "See " }] } {}
  == .fail .bridgeMismatch
-- the window's recorded hash must match when the hash file is supplied
def bInH : Cert.Input :=
  { bIn with hashRequired := true, windows := bIn.windows.map (fun w => { w with hash := some (Sha1.hex w.text) }) }
def bGoodH (h : Cert.Window → String) : Cert.Bridge :=
  { bGoodB with windows := bGoodB.windows.map (fun w => { w with hash := some (h w) }) }
#guard Cert.checkBridge bInH (bGoodH (fun _ => ancBadSha)) {} == .fail .bridgeMismatch
#guard Cert.checkBridge bInH (bGoodH (fun w => Sha1.hex w.text)) {} == .ok
#guard Cert.checkBridge bInH bGoodB {} == .fail .bridgeMismatch
-- step 2: W dated before O; an unknown date
#guard Cert.checkBridge bIn { bGoodB with wDate := 20150101 } {} == .fail .bridgeDate
#guard Cert.checkBridge bIn { bGoodB with oDate := 0 } {} == .fail .bridgeDate
#guard Cert.checkBridge bIn { bGoodB with wDate := 20160111 } {} == .ok
-- step 3: one clause
def bSemi := "Smith v. Jones, 123 F. 3d 456 (CA5 2015), cert. denied, 577 U. S. 1001 (2016); Doe v. Roe"
#guard Cert.checkBridge bIn (bw bSemi) {} == .fail .bridgeClause
-- step 4: X's citation through the index; no index
#guard Cert.checkBridge { bIn with target := 6 } bGoodB {} == .fail .bridgeTarget
#guard Cert.checkBridge { bIn with citeIndex := none } bGoodB {} == .fail .bridgeTarget
-- step 5: a cue of the kind after X's citation
#guard Cert.checkBridge { bIn with kind := .hist .vacated } bGoodB {} == .fail .bridgeCue
#guard Cert.checkBridge { bIn with kind := .hist .modified } bGoodB {} == .fail .bridgeCue
def bAffd := "Smith v. Jones, 123 F. 3d 456 (CA5 2015), aff'd, 577 U. S. 1001 (2016)"
#guard Cert.checkBridge bIn (bw bAffd) {} == .fail .bridgeCue
-- as an `affirmed` row the bridge passes; step 7 then reads O's own words, which have no cue of that kind
#guard Cert.bridgeFail { bIn with kind := .hist .affirmed } (bw bAffd) == none
#guard Cert.checkBridge { bIn with kind := .hist .affirmed } (bw bAffd) {} == .fail .noCue
def bCueFirst := "Cert. denied, 577 U. S. 1001, in Smith v. Jones, 123 F. 3d 456 (CA5 2015)"
#guard Cert.checkBridge bIn (bw bCueFirst) {} == .fail .bridgeCue
-- step 5b (D8-9): no other citation between X's citation and the cue (O acted on Y, not on X)
def bChain := "Smith v. Jones, 123 F. 3d 456 (CA5 1998), aff'd, 200 F. 3d 9 (CA5 1999), cert. denied, 577 U. S. 1001 (2016)"
#guard Cert.checkBridge bIn (bw bChain) {} == .fail .bridgeChain
-- a parallel citation of X itself is a key too (lead ruling: literal)
def bParallel := "Smith v. Jones, 123 F. 3d 456, 123 F. 3d 456 (CA5 2015), cert. denied, 577 U. S. 1001 (2016)"
#guard Cert.checkBridge bIn (bw bParallel) {} == .fail .bridgeChain
-- step 6: the first citation after the cue is O's (the longest key: 577us1001, not 577us100)
def bOther := "Smith v. Jones, 123 F. 3d 456 (CA5 2015), cert. denied, 576 U. S. 900 (2015)"
#guard Cert.checkBridge bIn (bw bOther) {} == .fail .bridgeActor
#guard Cert.checkBridge bIn { bGoodB with lens := [8, 9, 7] } {} == .fail .bridgeActor
#guard Cert.checkBridge bIn { bGoodB with actor := 31 } {} == .fail .bridgeActor
def bOFirst := "Smith v. Jones, 577 U. S. 1001, and 123 F. 3d 456 (CA5 2015), cert. denied"
#guard Cert.checkBridge bIn (bw bOFirst) {} == .fail .bridgeActor
-- step 7: the row's own check, the target evidence taken as given
#guard Cert.checkBridge { bIn with part := "dissent" } bGoodB {} == .fail .partNotMajority
#guard Cert.checkBridge { bIn with authority := none } bGoodB {} == .okUnverifiedBy
#guard Cert.checkBridge { bIn with authority := some false } bGoodB {} == .fail .noAuthority
#guard Cert.checkBridge { bIn with part := "headmatter" } bGoodB {} == .fail .partNotMajority
#guard Cert.checkBridge { bIn with part := "headmatter" } bGoodB { orderHead := true, scotus := true, date := 20160111 }
  == .ok
#guard Cert.checkBridge { bIn with quote := "Judgment entered.", stop := bIn.start + 17 } bGoodB {} == .fail .quoteMismatch
-- a bridged row's anchor line is not used; the bridge steps do not read the power
#guard Cert.checkHistory8 bIn (some ancOk) (some bGoodB) {} == Cert.checkBridge bIn bGoodB {}
#guard Cert.bridgeFail { bIn with authority := none } bGoodB == Cert.bridgeFail bIn bGoodB
#guard Cert.bridgeMaxLen == 600

/-! Round 8 (§5): wide anchor cues under an `anchorWide` claim ("(CA2 2007)" names the court below). -/

def awText := "Iqbal v. Hasty, 490 F. 3d 143 (CA2 2007). The judgment of the Court of Appeals is reversed."
def awIn : Cert.Input :=
  { kind := .hist .reversed, textSha := "aw", start := offOf awText "The judgment",
    stop := offOf awText "The judgment" + 49, quote := "The judgment of the Court of Appeals is reversed.",
    evidence := "cite:490 F.3d 143", part := "majority", shas := ["aw"],
    windows := [{ start0 := 0, stop0 := awText.length, text := awText }], ordered := true, authority := some true,
    target := 9, citeIndex := some (idx "490f3d143" 9) }
def awAnc : Cert.Anchor :=
  { start := 0, stop := offOf awText " The judgment", quote := "Iqbal v. Hasty, 490 F. 3d 143 (CA2 2007).",
    part := "majority" }
#guard Cert.checkHistory8 awIn (some awAnc) none {} == .fail .anchorNoCue
#guard Cert.checkHistory8 awIn (some awAnc) none {} == Cert.checkHistory7 awIn (some awAnc) {}
#guard Cert.checkHistory8 awIn (some awAnc) none { anchorWide := true } == .ok
-- the other anchored checks are unchanged
#guard Cert.checkHistory8 awIn (some { awAnc with part := "dissent" }) none { anchorWide := true } == .fail .anchorPart
#guard Cert.checkHistory8 { awIn with citeIndex := some (idx "490f3d143" 8) } (some awAnc) none { anchorWide := true }
  == .fail .anchorUnresolved
-- without an anchor line the claim has no effect
#guard Cert.checkHistory8 awIn none none { anchorWide := true } == Cert.checkHistory7 awIn none {}
-- "(Cal." is not a wide cue (D8-5)
#guard !Cert.anchorWideCue { awAnc with quote := "People v. Doe, 9 Cal. 4th 1 (Cal. 1995)." }

/-! Round 8 (§6): old circuits. The Fifth Circuit in 1975 over the Northern District of Georgia (circuit 11 in the
court table): power only under an `oldCircuit` claim, and only before 1 Oct 1981. -/

#guard histPower L ca5in1975 ndga1950 == some false
#guard Exec.histPower8 L ca5in1975 ndga1950 false == some false
#guard Exec.histPower8 L ca5in1975 ndga1950 true == some true
#guard Exec.histPower8 L ca5in1982 ndga1950 true == some false
#guard Exec.histPower8 L { ca5in1975 with date := 0 } ndga1950 true == some false
#guard Exec.histPower8 L ca5in1975 ndill1990 true == some false
#guard Exec.histPower8 L ca11in1990 ndga1950 true == histPower L ca11in1990 ndga1950
#guard Exec.histPower8 L ca5in1975 ndtex2001 true == histPower L ca5in1975 ndtex2001
-- treatments rows keep `canChangeStatus` (the claim is a history claim)
#guard (canChangeStatus L ca5in1975 ndga1950 none).map (·.1) == some false

/-! ## Round 9: part zones (`round9/DESIGN9.md` §4). The Gideon test text: head matter `[0, 21)`, the opinion of the
Court `[21, 98)` (the quote is `[48, 97)`), a dissent `[98, 108)`. -/

def zn (a b : Nat) (p : String) : Cert.Zone := { start := a, stop := b, part := p }
def certGideonZ : Cert.Input := certIn "Betts v. Brady, 316 U.S. 455, should be overruled" 48 "cite:316 U.S. 455" "majority"
/-- the zones of the part map -/
def zGood : List Cert.Zone := [zn 0 21 "headmatter", zn 21 98 "majority", zn 98 108 "dissent"]
/-- a boundary inside the quote -/
def zStraddle : List Cert.Zone := [zn 0 60 "majority", zn 60 108 "dissent"]
/-- the quote inside a dissent -/
def zOther : List Cert.Zone := [zn 0 40 "majority", zn 40 108 "dissent"]
/-- two overlapping zones (the node keeps none) -/
def zOverlap : List Cert.Zone := [zn 0 60 "majority", zn 50 108 "dissent"]
/-- a part outside the seven (case-sensitive) -/
def zBadPart : List Cert.Zone := [zn 0 60 "majority", zn 60 108 "Dissent"]
#guard (certGideonZ.start, certGideonZ.stop, gideonText.length) == (48, 97, 108)
#guard Cert.check certGideonZ == .ok
#guard Cert.zoneThen zGood certGideonZ [] (Cert.check certGideonZ) == .ok
#guard Cert.zoneThen zStraddle certGideonZ [] (Cert.check certGideonZ) == .fail .partZone
#guard Cert.zoneThen zOther certGideonZ [] (Cert.check certGideonZ) == .fail .partZone
-- touching zones do not overlap; the quote may fill its zone exactly
#guard Cert.zonesValid [zn 0 48 "headmatter", zn 48 97 "majority", zn 97 108 "dissent"]
#guard Cert.zoneThen [zn 0 48 "headmatter", zn 48 97 "majority", zn 97 108 "dissent"] certGideonZ []
  (Cert.check certGideonZ) == .ok
#guard Cert.zoneThen [zn 0 48 "headmatter", zn 49 97 "majority"] certGideonZ [] (Cert.check certGideonZ) == .fail .partZone
-- a node with overlapping, identical, empty or unknown-part zones keeps none: its rows get the round-8 verdict
#guard !Cert.zonesValid zOverlap && !Cert.zonesValid zBadPart
#guard !Cert.zonesValid [zn 21 98 "majority", zn 21 98 "majority"]
#guard !Cert.zonesValid [zn 21 98 "majority", zn 98 98 "dissent"]
#guard Cert.nodeZones zOverlap == [] && Cert.nodeZones zBadPart == [] && Cert.nodeZones zGood == zGood
#guard Cert.zoneThen (Cert.nodeZones zOverlap) certGideonZ [] (Cert.check certGideonZ) == .ok
#guard Cert.zoneThen (Cert.nodeZones zBadPart) certGideonZ [] (Cert.check certGideonZ) == .ok
-- no zone, no change; a round-8 failure keeps its reason; an unverified power is zone-checked too
#guard Cert.zoneThen [] certGideonZ [] (Cert.check certGideonZ) == .ok
#guard Cert.zoneThen zStraddle { certGideonZ with part := "dissent" } [] (Cert.check { certGideonZ with part := "dissent" })
  == .fail .partNotMajority
#guard Cert.zoneThen zStraddle certGideonZ [] (Cert.check { certGideonZ with authority := some false }) == .fail .noAuthority
#guard Cert.zoneThen zStraddle certGideonZ [] (.fail .doctrineAmbiguous) == .fail .doctrineAmbiguous
#guard Cert.zoneThen zGood certGideonZ [] (Cert.check { certGideonZ with authority := none }) == .okUnverifiedBy
#guard Cert.zoneThen zOther certGideonZ [] (Cert.check { certGideonZ with authority := none }) == .fail .partZone
-- head matter under its own part: a head-matter row inside the head-matter zone
#guard Cert.zoneHas zGood 0 21 "headmatter" && !Cert.zoneHas zGood 0 22 "headmatter"
-- joined quotes: each inside a zone of its own `j_part`
def zJoined (p : String) : List Cert.Zone :=
  [zn 0 (offOf jText jNear + jNear.length) p, zn (offOf jText jNear + jNear.length) jText.length "majority"]
#guard Cert.checkTreatment9 [zn 0 jText.length "majority"] jIn true .plain [jNearL] == .ok
#guard Cert.checkTreatment9 (zJoined "majority") jIn true .plain [jNearL] == .ok
#guard Cert.checkTreatment9 (zJoined "dissent") jIn true .plain [jNearL] == .fail .partZone
#guard Cert.checkTreatment9 (zJoined "dissent") jIn true .plain [] == Cert.check jIn
-- witness rows: W's text
#guard Cert.checkRecognised9 [zn 0 witText.length "majority"] witIn witRow == .witness .ok
#guard Cert.checkRecognised9 [zn 0 witText.length "concurrence"] witIn witRow == .witness (.fail .partZone)
#guard Cert.checkRecognised9 [zn 0 witText.length "concurrence"] witIn
  { witRow with claim := true, power := true, datesKnown := true } == .witness (.fail .partZone)
#guard Cert.checkRecognised9 [] witIn witRow == Cert.checkRecognised witIn witRow
-- history rows: the anchor quote is not zone-checked (here it is in an `other` zone), the disposition is
#guard Cert.checkHistory9 [zn 0 (offOf awText "The judgment") "other", zn (offOf awText "The judgment") awText.length "majority"]
  awIn (some awAnc) none { anchorWide := true } == .ok
#guard Cert.checkHistory9 [zn 0 awText.length "other"] awIn (some awAnc) none { anchorWide := true } == .fail .partZone
#guard Cert.checkHistory9 [] awIn (some awAnc) none {} == Cert.checkHistory8 awIn (some awAnc) none {}


/-! ## Round 9, batch 2 (`round9/DESIGN9.md` §5, §7). Far antecedents: the cases are named in one sentence, the act
("Those cases are overruled.") comes some 480 characters later (beyond round 7's 300). -/

def fNear := "In Smith v. Jones, 100 U. S. 1, and Brown v. White, 200 U. S. 2, this Court held that a State may tax the mails."
def fFill := String.join (List.replicate 10 "The question has come back to us in many forms. ")
/-- the same filler with another decision's citation -/
def fFillKey := String.join (List.replicate 9 "The question has come back to us in many forms. ") ++
  "See Doe v. Roe, 300 U. S. 3, at 4. "
/-- a filler of 1,440 characters (beyond `joinedFarMax`) -/
def fFillLong := String.join (List.replicate 30 "The question has come back to us in many forms. ")
def fText (fill : String) (q : String := jMain) : String := fNear ++ " " ++ fill ++ q
/-- the index: 200 U.S. 2 (the target, node 7) and 300 U.S. 3 (node 9) -/
def fIdx : Std.HashMap String Nat := (idx "200us2" 7).insert "300us3" 9
def fIn (fill : String) (q : String := jMain) : Cert.Input :=
  { kind := .treat .overruled, textSha := "f", start := offOf (fText fill q) q,
    stop := offOf (fText fill q) q + q.length, quote := q, evidence := "cite:200 U.S. 2", part := "majority",
    shas := ["f"], windows := [{ start0 := 0, stop0 := (fText fill q).length, text := fText fill q }], ordered := true,
    authority := some true, target := 7, citeIndex := some fIdx }
def fL (fill : String) (q : String := jMain) : Cert.Joined := jl (fText fill q) fNear
#guard (fIn fFill).start - (fL fFill).stop == 481
#guard Cert.checkTreatment (fIn fFill) true .plain [fL fFill] == .fail .joinedRelation
#guard Cert.checkTreatmentF true [6] (fIn fFill) true .plain [fL fFill] == .ok
#guard Cert.checkTreatmentF false [6] (fIn fFill) true .plain [fL fFill] == .fail .joinedRelation
#guard Cert.checkTreatmentF true [6] (fIn fFillKey) true .plain [fL fFillKey] == .fail .joinedFarKey
#guard Cert.checkTreatmentF true [6] (fIn fFillLong) true .plain [fL fFillLong] == .fail .joinedFarGap
-- the main quote keeps round 7's anaphor test (after the far tests, ref9 Q9-12)
#guard Cert.checkTreatmentF true [6] (fIn fFill jNoAna) true .plain [fL fFill jNoAna] == .fail .joinedRelation
#guard Cert.checkTreatmentF true [6] (fIn fFillKey jNoAna) true .plain [fL fFillKey jNoAna] == .fail .joinedFarKey
-- the target's own citation in the gap is not "another key"; without an index there is no key
#guard Cert.checkTreatmentF true [6] { fIn fFillKey with citeIndex := some (idx "200us2" 7) } true .plain [fL fFillKey]
  == .ok
-- a key that starts in the gap and runs into the act counts; the act's own citations do not
#guard Cert.checkTreatmentF true [7, 6] { fIn fFill with citeIndex := some (fIdx.insert "thoseca" 9) } true .plain
  [fL fFill] == .ok
#guard Cert.checkTreatmentF true [8, 6] { fIn fFill with citeIndex := some (fIdx.insert "formstho" 9) } true .plain
  [fL fFill] == .fail .joinedFarKey
-- no window covers the gap (one window per quote)
def fSplit : Cert.Input :=
  { fIn fFill with windows := [{ start0 := 0, stop0 := fNear.length, text := fNear },
    { start0 := (fIn fFill).start, stop0 := (fText fFill).length,
      text := ((fText fFill).drop (fIn fFill).start).toString }] }
#guard Cert.checkTreatmentF true [6] fSplit true .plain [fL fFill] == .fail .joinedFarWindow
-- rows the round-7 check admits are unchanged
#guard Cert.checkTreatmentF true [6] jIn true .plain [jNearL] == Cert.checkTreatment jIn true .plain [jNearL]
-- round 7's far sentence (some 800 characters before the act): with an index, the citations of the cases in between
-- are other keys; without one, nothing marks them
#guard Cert.checkTreatment jIn true .plain [jFarL] == .fail .joinedRelation
#guard Cert.checkTreatmentF true [6] { jIn with citeIndex := some ((idx "200us2" 7).insert "100us1" 8), target := 7 }
  true .plain [jFarL] == .fail .joinedFarKey
#guard Cert.checkTreatmentF true [6] jIn true .plain [jFarL] == .ok
#guard Cert.joinedFarMax == 1200

/-! Implicit rejection: a soft row whose quote has no cue of its kind, only an implicit-rejection phrase. -/

def iText := "We are unpersuaded by the reasoning of Smith v. Jones, 100 U. S. 1, and we decline its rule here."
def iQuote := "We are unpersuaded by the reasoning of Smith v. Jones, 100 U. S. 1"
def iIn : Cert.Input :=
  { kind := .treat .declinedToFollow, textSha := "i", start := 0, stop := iQuote.length, quote := iQuote,
    evidence := "cite:100 U.S. 1", part := "majority", shas := ["i"],
    windows := [{ start0 := 0, stop0 := iText.length, text := iText }], ordered := true, authority := some true }
#guard Cert.check iIn == .fail .noCue
#guard Cert.checkTreatmentI true iIn true .plain [] == .ok
#guard Cert.checkTreatmentI false iIn true .plain [] == .fail .noCue
#guard Cert.checkTreatmentI true { iIn with kind := .treat .questioned } true .plain [] == .ok
#guard Cert.checkTreatmentI true { iIn with kind := .treat .overruled } true .plain [] == .fail .implicitBadKind
#guard Cert.checkTreatmentI true { iIn with kind := .treat .followed } true .plain [] == .fail .implicitBadKind
#guard Cert.checkTreatmentI true { iIn with part := "dissent" } true .plain [] == .fail .partNotMajority
#guard Cert.checkTreatmentI true { iIn with quote := "We are persuaded by Smith v. Jones, 100 U. S. 1" } true .plain []
  == .fail .quoteMismatch
#guard Cert.implicitRejectCues.length == 18

/-- Soft means `softNegative`. -/
theorem implicitSoft_softNegative (k : TKind) : Cert.implicitSoft (.treat k) = k.softNegative := by
  cases k <;> rfl

/-- **Implicit rejection never changes status** (§7): an admitted claimed row is of a soft kind, so its event has no
effect and every status is unchanged. -/
theorem implicitReject_never_neg (c : Cert.Input) (e : Bool) (js : List Cert.Joined) (k : TKind)
    (hk : c.kind = .treat k) (h : (Cert.checkImplicit c e js).admitted = true) (bh : List HEvent) (tr : TEvent)
    (htk : tr.kind = k) (l : List Effect) (n : Nat) (t u : Date) :
    treatEffect bh tr = none ∧ status ((treatEffect bh tr).toList ++ l) n t u = status l n t u := by
  have hs := Cert.implicitReject_soft c e js h
  rw [hk, implicitSoft_softNegative] at hs
  have hc : tr.kind.changesStatus = false := by
    rw [htk]
    cases k <;> simp_all [TKind.softNegative, TKind.changesStatus]
  have he := soft_treatment_no_effect bh tr hc
  exact ⟨he, by simp [he]⟩

/-! Round 9 §8 (D9-9): a judge-form anchor ("(Smith, District Judge)") counts only under an `anchorWide` claim. -/

def jgText := "Doe v. Roe, 490 F. 3d 143 (Smith, District Judge). The judgment of the Court of Appeals is reversed."
def jgIn : Cert.Input :=
  { kind := .hist .reversed, textSha := "jg", start := offOf jgText "The judgment",
    stop := offOf jgText "The judgment" + 49, quote := "The judgment of the Court of Appeals is reversed.",
    evidence := "cite:490 F.3d 143", part := "majority", shas := ["jg"],
    windows := [{ start0 := 0, stop0 := jgText.length, text := jgText }], ordered := true, authority := some true,
    target := 9, citeIndex := some (idx "490f3d143" 9) }
def jgAnc : Cert.Anchor :=
  { start := 0, stop := offOf jgText " The judgment", quote := "Doe v. Roe, 490 F. 3d 143 (Smith, District Judge).",
    part := "majority" }
#guard !Cert.anchorHasCue jgAnc && !Cert.anchorWideCue jgAnc && Cert.anchorWideCue9 jgAnc
#guard Cert.checkHistory8 jgIn (some jgAnc) none { anchorWide := true } == .fail .anchorNoCue
#guard Cert.checkHistory8J jgIn (some jgAnc) none { anchorWide := true } == .ok
#guard Cert.checkHistory8J jgIn (some jgAnc) none {} == .fail .anchorNoCue
#guard Cert.checkHistory8J awIn (some awAnc) none { anchorWide := true } == .ok
#guard Cert.checkHistory9J [] jgIn (some jgAnc) none { anchorWide := true } == .ok
#guard Cert.anchorWide9Cues == ["district judge", "magistrate judge", "trial judge"]

/-! ## Round 9 (`round9/DESIGN9.md` §6): New Jersey's successor courts of like jurisdiction (1947 Constitution, in
force 15 Sept 1948). The courts as `courts2.tsv` has them (system 30); the Law Division is a synthetic trial court
(id 10011). The round-9 data adds the adoption rows `1099 ← 1095` (Appellate Division ← old Supreme Court) and
`1222 ← 1206` (Chancery Division ← Court of Chancery); `1096 ← 1094` was already there. -/

def njEA := 1094
def njOldSup := 1095
def njSup := 1096
def njAppDiv := 1099
def njChan := 1206
def njChanDiv := 1222
def njLaw := 10011

def njAdopt (adopter source : Nat) : Adoption :=
  { adopter, source, upTo := 19480914, filter := .all, force := .binding, firm := true }

def njEnvWith (ads : List Adoption) : Env :=
  { epochs := [ep njEA 18210101 19480914 30 .last 0 .all, ep njOldSup 0 19480914 30 .appellate,
      ep njSup 19480915 forever 30 .last 0 .all, ep njAppDiv 19480915 forever 30 .appellate,
      ep njChan 18300101 19480914 30 .special, ep njChanDiv 19170101 forever 30 .special,
      ep njLaw 19480915 forever 30 .trial]
    successions := [{ old := njEA, new := njSup, date := 19480915, kind := .replace, firm := true },
      { old := njOldSup, new := njAppDiv, date := 19480915, kind := .replace, firm := true },
      { old := njChan, new := njChanDiv, date := 19480915, kind := .replace, firm := true }]
    adoptions := ads
    rules := [⟨30, "horizontal", "none", 0, forever, true⟩] }

/-- the round-9 tables -/
def njL : Lookups := (ExecEnv.build (njEnvWith [njAdopt njSup njEA, njAdopt njAppDiv njOldSup,
  njAdopt njChanDiv njChan])).lookups
/-- the round-8 tables (only `1096 ← 1094`) -/
def njL8 : Lookups := (ExecEnv.build (njEnvWith [njAdopt njSup njEA])).lookups
/-- the mutant fixture: also `1099 ← 1094` (an adoption across tiers) -/
def njLx : Lookups := (ExecEnv.build (njEnvWith [njAdopt njSup njEA, njAdopt njAppDiv njOldSup,
  njAdopt njChanDiv njChan, njAdopt njAppDiv njEA])).lookups
def njpw (L' : Lookups) (b x : Decision) : Option Bool := (canChangeStatus L' b x none).map (·.1)

def oldSup1924 := d 61 njOldSup 19240101
def oldSup1944 := d 57 njOldSup 19440101
def oldSup1948 := d 50 njOldSup 19480101
def ea1922 := d 59 njEA 19220101 (bench := .wholeCourt)
def ea1924 := d 53 njEA 19240101 (bench := .wholeCourt)
def chancery1937 := d 55 njChan 19370101
def appDiv1962 := d 51 njAppDiv 19620101
def appDiv1977 := d 52 njAppDiv 19770101
def chanDiv1949 := d 54 njChanDiv 19490101
def lawDiv1964 := d 56 njLaw 19640101
def sup1954 := d 60 njSup 19540101 (bench := .wholeCourt)
def sup1993 := d 58 njSup 19930101 (bench := .wholeCourt)

-- Clark v. Piccillo / In re Estate of Johnson: the Appellate Division over the old Supreme Court (comparable jurisdiction)
#guard njpw njL appDiv1962 oldSup1948 == some true
#guard (canChangeStatus njL appDiv1962 oldSup1948 none).map (·.2) == some .sameCourtSoft
-- Gruschow, Haber: bound by the Court of Errors and Appeals
#guard njpw njL appDiv1977 ea1924 == some false
-- Hagaman, Hogan: the Chancery Division over the Court of Chancery
#guard njpw njL chanDiv1949 chancery1937 == some true
-- a trial division changes no status of the old Supreme Court (F13; Weller)
#guard njpw njL lawDiv1964 oldSup1944 == some false
-- Bernard v. IMI Systems: the Supreme Court overrules the Court of Errors and Appeals
#guard njpw njL sup1993 ea1922 == some true
-- a higher court
#guard njpw njL sup1954 oldSup1924 == some true
-- without the two round-9 rows (round 8's tables): no power over the predecessors
#guard njpw njL8 appDiv1962 oldSup1948 == some false
#guard njpw njL8 chanDiv1949 chancery1937 == some false
#guard njpw njL8 sup1993 ea1922 == some true
-- an adoption across tiers gives no power over the higher court (the tier guard)
#guard njpw njLx appDiv1977 ea1924 == some false

/-! Round 10 (`round10/DESIGN10.md` §4, D10-5, D10-6): remand bridge evidence. The order O is node 30 (577 U. S. 1001,
dated 2016-01-11, as in the round-8 bridge example `bIn`); the target X (court 8, 2015-03-01) is the Fifth Circuit's
judgment in No. 14-50123; B (node 41, court 8, 2016-06-01) is its decision on remand, whose text names the docket and
says that the Supreme Court vacated and remanded. The order's text names the reason case (D10-7). -/

def rBText := "On remand from the Supreme Court of the United States. No. 14-50123. Before Smith, Circuit Judge. " ++
  "The Supreme Court vacated our judgment, 577 U. S. 1001 (2016), and remanded for further consideration in light " ++
  "of Doe v. Roe, 576 U. S. 900 (2015). We affirm."
def rTText := "United States Court of Appeals, Fifth Circuit. No. 14-50123. Smith v. Jones. Affirmed."
def rQ := "The Supreme Court vacated our judgment, 577 U. S. 1001 (2016), and remanded for further consideration in " ++
  "light of Doe v. Roe, 576 U. S. 900 (2015)."
def rOText := "Certiorari granted. Judgment vacated, and case remanded to the Court of Appeals for the Fifth Circuit " ++
  "for further consideration in light of Doe v. Roe, 576 U. S. 900 (2015)."
def rOSpan := "in light of Doe v. Roe, 576 U. S. 900 (2015)"
/-- A remand line: B's quote `q` in B's text `txtB` (by default `"See " ++ q`), the docket span `dkB` of B's text and
`dkT` of the target's text `txtT`. -/
def rm (q : String) (txtB : String := rBText) (txtT : String := rTText) (dk : String := "14-50123")
    (dkB : String := "No. 14-50123") (dkT : String := "No. 14-50123") (oSpan : String := rOSpan) : Cert.Remand :=
  { b := 41, bSha := "b10", bWindows := [{ start0 := 0, stop0 := txtB.length, text := txtB }], tSha := "t10",
    tWindows := [{ start0 := 0, stop0 := txtT.length, text := txtT }], start := offOf txtB q,
    stop := offOf txtB q + q.length, docket := dk, bdStart := offOf txtB dkB, bdStop := offOf txtB dkB + dkB.length,
    tStart := offOf txtT dkT, tStop := offOf txtT dkT + dkT.length, bCourt := some 8, tCourt := some 8,
    oDate := 20160111, bDate := 20160601, tDate := 20150301, order := some 30, lens := bLens,
    tie := "Doe v. Roe, 576 U. S. 900", oSha := "o10", oWindows := [{ start0 := 0, stop0 := rOText.length, text := rOText }],
    oStart := offOf rOText oSpan, oStop := offOf rOText oSpan + oSpan.length }
def rGood := rm rQ
/-- B's text with another quote in place of `rQ`. -/
def rmQ (q : String) : Cert.Remand := rm q (rBText.replace rQ q)
#guard Cert.remandQuote bIn rGood == some (rQ.toLower)
#guard Cert.reasonTie bIn rGood (rQ.toLower) && Cert.keyTie bIn rGood (rQ.toLower)
#guard Cert.remandFail bIn rGood == none
#guard Cert.remandThen (some rGood) bIn .ok == .ok
#guard Cert.remandThen (some rGood) bIn .okUnverifiedBy == .okUnverifiedBy
-- no line: the round-9 verdict
#guard Cert.remandThen none bIn .ok == .ok
#guard Cert.checkHistory10 none [] bIn none (some bGoodB) {} == Cert.checkHistory9J [] bIn none (some bGoodB) {}
-- the round-9 verdict first: the bridge admits the row, then the line checks it; a failing verdict keeps its reason
#guard Cert.checkHistory10 (some rGood) [] bIn none (some bGoodB) {} == .ok
#guard Cert.checkHistory10 (some { rGood with bCourt := some 9 }) [] bIn none (some bGoodB) {} == .fail .remandCourt
#guard Cert.checkHistory10 (some rGood) [] bIn none none {} == .fail .targetUnresolved
#guard Cert.checkHistory10 (some { rGood with bCourt := some 9 }) [] bIn none none {} == .fail .targetUnresolved
#guard Cert.remandThen (some { rGood with bCourt := some 9 }) bIn (.fail .noAuthority) == .fail .noAuthority
#guard Cert.remandThen (some { rGood with bCourt := some 9 }) bIn (.fail .partZone) == .fail .partZone
-- step 1: the court (another court; B or the target without a decisions2 row)
#guard Cert.remandFail bIn { rGood with bCourt := some 9 } == some .remandCourt
#guard Cert.remandFail bIn { rGood with bCourt := none } == some .remandCourt
#guard Cert.remandFail bIn { rGood with bCourt := none, tCourt := none } == some .remandCourt
-- step 1: the dates (B before the order; the target not before the order; unknown; not a calendar date; the bound)
#guard Cert.remandFail bIn { rGood with bDate := 20151201 } == some .remandDate
#guard Cert.remandFail bIn { rGood with bDate := 20160111 } == none
#guard Cert.remandFail bIn { rGood with tDate := 20160111 } == some .remandDate
#guard Cert.remandFail bIn { rGood with oDate := 0 } == some .remandDate
#guard Cert.remandFail bIn { rGood with tDate := 0 } == some .remandDate
#guard Cert.remandFail bIn { rGood with bDate := 20160231 } == some .remandDate
#guard Cert.remandFail bIn { rGood with bDate := 20210110 } == none
#guard Cert.remandFail bIn { rGood with bDate := 20210111 } == some .remandDate
#guard Cert.dayNum 20210110 == Cert.dayNum 20160111 + 1826
#guard Cert.dayNum 10101 == 1 && Cert.dayNum 10201 == 32 && Cert.dayNum 20010101 == 730486
#guard Cert.dayNum 20160301 == Cert.dayNum 20160229 + 1 && Cert.dayNum 20150301 == Cert.dayNum 20150228 + 1
#guard Cert.dayNum 20000301 == Cert.dayNum 20000229 + 1 && Cert.dayNum 19000301 == Cert.dayNum 19000228 + 1
#guard Cert.dayNum 20170101 == Cert.dayNum 20161231 + 1
#guard Cert.validDate 20160229 && Cert.validDate 20000229 && !Cert.validDate 20150229 && !Cert.validDate 19000229
#guard !Cert.validDate 20151301 && !Cert.validDate 20150100 && !Cert.validDate 20150431 && !Cert.validDate 1231
-- step 2: the docket token (too short; no digit; empty; in B's span only; a span over 200; no window of the target)
#guard Cert.remandFail bIn { rGood with docket := "14-5" } == some .remandDocket
#guard Cert.remandFail bIn { rGood with docket := "No. Smith" } == some .remandDocket
#guard Cert.remandFail bIn { rGood with docket := "" } == some .remandDocket
#guard Cert.remandFail bIn { rGood with docket := "No. 14-50123" } == none
def rTOther := "United States Court of Appeals, Fifth Circuit. No. 14-50999. Smith v. Jones. Affirmed."
def rBOnly := rm rQ rBText rTOther "14-50123" "No. 14-50123" "No. 14-50999"
#guard Cert.remandFail bIn rBOnly == some .remandDocket
#guard Cert.remandFail bIn { rGood with tStart := 0, tStop := 201 } == some .remandDocket
#guard Cert.remandFail bIn { rGood with tWindows := [] } == some .remandDocket
#guard Cert.remandFail bIn { rGood with tSha := "" } == some .remandDocket
#guard Cert.remandFail bIn { rGood with bdStop := rGood.bdStart } == some .remandDocket
-- the spans and the quote are read over hash-checked windows when the hash file is supplied
def rH (h : Cert.Window → String) : Cert.Remand :=
  { rGood with bWindows := rGood.bWindows.map (fun w => { w with hash := some (h w) }),
               tWindows := rGood.tWindows.map (fun w => { w with hash := some (Sha1.hex w.text) }) }
#guard Cert.remandFail bInH (rH (fun w => Sha1.hex w.text)) == none
#guard Cert.remandFail bInH (rH (fun _ => ancBadSha)) == some .remandDocket
#guard Cert.remandFail bInH rGood == some .remandDocket
-- step 3: the cue (no "supreme court"; no remand cue; over 600; no window of B)
#guard Cert.remandFail bIn (rmQ "The Court vacated our judgment, 577 U. S. 1001 (2016), and remanded.") ==
  some .remandCue
#guard Cert.remandFail bIn (rmQ "The Supreme Court denied rehearing, 577 U. S. 1001 (2016).") == some .remandCue
def rLong := "The Supreme Court vacated our judgment, 577 U. S. 1001 (2016), and remanded" ++
  String.join (List.replicate 12 ", the panel considering the matter with care and at length") ++ "."
#guard rLong.length > 600
#guard Cert.remandFail bIn (rmQ rLong) == some .remandCue
#guard Cert.remandFail bIn { rGood with start := rGood.stop } == some .remandCue
-- step 4: the tie (none; the docket; the two date forms; a key of another node; no index)
def rNoTie := "The Supreme Court vacated our judgment and remanded for further consideration in light of Doe v. Roe."
#guard Cert.remandFail bIn (rmQ rNoTie) == some .remandTie
-- D10-7: B's own docket is no tie
#guard Cert.remandFail bIn (rmQ "The Supreme Court vacated our judgment in No. 14-50123 and remanded.") ==
  some .remandTie
-- (c2) the reason case: in the order's span after "in light of" and in B's quote (at least 8 compact characters)
def rReason := "The Supreme Court vacated our judgment and remanded for further consideration in light of Doe v. Roe, " ++
  "576 U. S. 900 (2015)."
#guard Cert.remandFail bIn (rmQ rReason) == none
#guard Cert.reasonTie bIn (rmQ rReason) (rReason.toLower) && !Cert.keyTie bIn (rmQ rReason) (rReason.toLower)
#guard Cert.remandFail bIn { rmQ rReason with oStart := 0, oStop := 19 } == some .remandTie
#guard Cert.remandFail bIn { rmQ rReason with oStart := offOf rOText "Doe v. Roe", oStop := rOText.length } ==
  some .remandTie
#guard Cert.remandFail bIn { rmQ rReason with tie := "Doe v. Roe" } == some .remandTie
#guard Cert.remandFail bIn { rmQ rReason with tie := "Roe, 576 U. S. 900" } == none
#guard Cert.remandFail bIn { rmQ rReason with tie := "" } == some .remandTie
#guard Cert.remandFail bIn { rmQ rReason with tie := "Smith v. Jones, 123 F. 3d 456" } == some .remandTie
#guard Cert.remandFail bIn { rmQ rReason with oWindows := [] } == some .remandTie
#guard Cert.remandFail bIn { rmQ rReason with oStart := 0, oStop := 301 } == some .remandTie
#guard Cert.remandFail bIn (rmQ "On January 11, 2016, the Supreme Court vacated our judgment and remanded.") == none
#guard Cert.remandFail bIn (rmQ "On Jan. 11, 2016, the Supreme Court vacated our judgment and remanded.") == none
#guard Cert.remandFail bIn (rmQ "On Jan. 11, 2015, the Supreme Court vacated our judgment and remanded.") ==
  some .remandTie
#guard Cert.remandFail bIn (rmQ "On January 11 2016, the Supreme Court vacated our judgment and remanded.") ==
  some .remandTie
#guard Cert.remandFail bIn (rmQ "The Supreme Court vacated our judgment, 577 U. S. 100 (2016), and remanded.") ==
  some .remandTie
def rCiteOnly := "The Supreme Court vacated our judgment, 577 U. S. 1001 (2016), and remanded."
#guard Cert.remandFail bIn (rmQ rCiteOnly) == none
#guard Cert.remandFail { bIn with citeIndex := none } (rmQ rCiteOnly) == some .remandTie
#guard Cert.remandFail bIn { rmQ rCiteOnly with order := none } == some .remandTie
-- the reason case ties the line without the index
#guard Cert.remandFail { bIn with citeIndex := none } rGood == none
#guard Cert.dateForms 20150930 == ["september 30, 2015", "sept. 30, 2015", "sep. 30, 2015"]
#guard Cert.dateForms 20150505 == ["may 5, 2015"]
#guard Cert.dateForms 20160111 == ["january 11, 2016", "jan. 11, 2016"]
#guard Cert.dateForms 20151300 == [] && Cert.dateForms 20150000 == []

/-! Round 10 §6 (`round10/DESIGN10.md` §6, D10-8, D10-9): the trial-judgment bridge. D (a state court of last resort,
court 21, 2012-06-01) reverses the district court's judgment in Smith v. Jones; T (the intermediate court, court 20,
2010-03-01; 100 So. 2d 5, node 9) had affirmed it. -/

def tdAnc := "Smith v. Jones, 100 So. 2d 5 (Ct. App. 2010), decision below."
def tdQ := "The judgment of the district court is reversed."
/-- D's row: the anchor, then the main quote `q`, of kind `k`. -/
def tdIn (q : String := tdQ) (k : HKind := .reversed) : Cert.Input :=
  let txt := tdAnc ++ " " ++ q
  { kind := .hist k, textSha := "d10", start := offOf txt q, stop := offOf txt q + q.length, quote := q,
    evidence := "cite:100 So.2d 5", part := "majority", shas := ["d10"],
    windows := [{ start0 := 0, stop0 := txt.length, text := txt }], ordered := true, authority := some true,
    target := 9, citeIndex := some (idx "100so2d5" 9) }
def tdA : Cert.Anchor := { start := 0, stop := tdAnc.length, quote := tdAnc, part := "majority" }
def tText := "Smith v. Jones. Court of Appeal. The judgment of the trial court is affirmed. All concur."
/-- T's line: the quote `q` in T's text `txt`. -/
def tb (q : String := "The judgment of the trial court is affirmed.") (txt : String := tText) : Cert.TBridge :=
  { tSha := "t10b", tWindows := [{ start0 := 0, stop0 := txt.length, text := txt }],
    line := some (offOf txt q, offOf txt q + q.length), tDate := 20100301, dDate := 20120601, tCourt := some 20,
    dCourt := some 21 }
def tbGood := tb
def tbNeg := tb "The judgment is affirmed in part and reversed in part." ("Smith v. Jones. Court of Appeal. " ++
  "The judgment is affirmed in part and reversed in part.")
def tdInter := "The judgment of the court of appeals and of the district court is reversed."
def tdCoa := "The judgment of the Court of Appeals is reversed."
-- round 9 admits the anchored row (no claim); with the claim and T's line it is admitted too
#guard Cert.checkHistory8J (tdIn) (some tdA) none {} == .ok
#guard Cert.checkHistory8T (some tbGood) (tdIn) (some tdA) none {} == .ok
#guard Cert.checkHistory8T none (tdIn) (some tdA) none {} == .ok
#guard Cert.tbridgeQuote (tdIn) tbGood == some "the judgment of the trial court is affirmed."
-- trialBridgeD: an intermediate-court name; no trial-court name; no cue of the kind
#guard Cert.checkHistory8T (some tbGood) (tdIn tdInter) (some tdA) none {} == .fail .trialBridgeD
#guard Cert.checkHistory8T (some tbGood) (tdIn "The judgment is reversed.") (some tdA) none {} == .fail .trialBridgeD
#guard Cert.checkHistory8T (some tbGood) (tdIn "The judgment of the district court is affirmed.") (some tdA) none {}
  == .fail .trialBridgeD
#guard Cert.checkHistory8T (some tbGood) (tdIn tdCoa) (some tdA) none {} == .fail .trialBridgeD
-- without the claim the court-of-appeals row is round 9's
#guard Cert.checkHistory8T none (tdIn tdCoa) (some tdA) none {} == .ok
-- vacated rows; "set aside" under a setAside claim
#guard Cert.checkHistory8T (some tbGood) (tdIn "The judgment of the circuit court is vacated." .vacated) (some tdA)
  none {} == .ok
#guard Cert.checkHistory8T (some tbGood) (tdIn "The judgment of the circuit court is set aside." .vacated) (some tdA)
  none { setAside := true } == .ok
#guard Cert.checkHistory8T (some tbGood) (tdIn "The judgment of the circuit court is set aside." .vacated) (some tdA)
  none {} == .fail .trialBridgeD
-- trialBridgeT: T's quote reverses; no affirm cue; no line; no window of T's text; too long
#guard Cert.checkHistory8T (some tbNeg) (tdIn) (some tdA) none {} == .fail .trialBridgeT
#guard Cert.checkHistory8T (some (tb "Court of Appeal.")) (tdIn) (some tdA) none {} == .fail .trialBridgeT
#guard Cert.checkHistory8T (some { tbGood with line := none }) (tdIn) (some tdA) none {} == .fail .trialBridgeT
#guard Cert.checkHistory8T (some { tbGood with tWindows := [] }) (tdIn) (some tdA) none {} == .fail .trialBridgeT
#guard Cert.checkHistory8T (some { tbGood with line := some (0, 601) }) (tdIn) (some tdA) none {} == .fail .trialBridgeT
-- trialBridgeDate: T after D; the 1,826-day bound; the same court; an unknown court or date
#guard Cert.checkHistory8T (some { tbGood with tDate := 20130101 }) (tdIn) (some tdA) none {} == .fail .trialBridgeDate
#guard Cert.checkHistory8T (some { tbGood with dDate := 20150301 }) (tdIn) (some tdA) none {} == .ok
#guard Cert.checkHistory8T (some { tbGood with dDate := 20150302 }) (tdIn) (some tdA) none {} == .fail .trialBridgeDate
#guard Cert.checkHistory8T (some { tbGood with dCourt := some 20 }) (tdIn) (some tdA) none {} == .fail .trialBridgeDate
#guard Cert.checkHistory8T (some { tbGood with tCourt := none }) (tdIn) (some tdA) none {} == .fail .trialBridgeDate
#guard Cert.checkHistory8T (some { tbGood with tDate := 0 }) (tdIn) (some tdA) none {} == .fail .trialBridgeDate
-- order: the anchored checks first, then D, then T, then the dates; the round-9 tail after them
#guard Cert.checkHistory8T (some tbNeg) (tdIn tdInter) (some tdA) none {} == .fail .trialBridgeD
#guard Cert.checkHistory8T (some { tbNeg with tDate := 20130101 }) (tdIn) (some tdA) none {} == .fail .trialBridgeT
#guard Cert.checkHistory8T (some tbGood) (tdIn) (some { tdA with part := "dissent" }) none {} == .fail .anchorPart
#guard Cert.checkHistory8T (some tbGood) { tdIn with authority := some false } (some tdA) none {} == .fail .noAuthority
#guard Cert.checkHistory8T (some { tbGood with tDate := 20130101 }) { tdIn with ordered := false } (some tdA) none {} ==
  .fail .trialBridgeDate
#guard Cert.checkHistory8T (some tbGood) { tdIn with ordered := false } (some tdA) none {} == .fail .targetLater
-- the claim counts only on a reversed / vacated anchored row without a bridge line
#guard Cert.checkHistory8T (some tbNeg) (tdIn tdQ .certDenied) (some tdA) none {} ==
  Cert.checkHistory8J (tdIn tdQ .certDenied) (some tdA) none {}
#guard Cert.checkHistory8T (some tbNeg) (tdIn) none none {} == Cert.checkHistory8J (tdIn) none none {}
#guard Cert.checkHistory8T (some tbNeg) (tdIn) (some tdA) (some bGoodB) {} == Cert.checkHistory8J (tdIn) (some tdA) (some bGoodB) {}
-- the round-10 step: zones and the remand test after it; no claim = §4's step
#guard Cert.checkHistory10T none none [] (tdIn) (some tdA) none {} == Cert.checkHistory10 none [] (tdIn) (some tdA) none {}
#guard Cert.checkHistory10T (some tbNeg) none [] (tdIn) (some tdA) none {} == .fail .trialBridgeT

/-! Round 11 §5.1 (`round11/DESIGN11.md` §5.1, D11-4): the claim `anchorTribunal`. A Federal Circuit opinion names the
decision under review (123 F. Supp. 2d 456, node 9) by its tribunal. -/

/-- An anchor quote naming the decision under review with the tribunal `p` in parentheses. -/
def trA (p : String) : String := "Foo Corp. v. United States, 123 F. Supp. 2d 456 (" ++ p ++ ")."
/-- The row: the anchor quote `anc`, then the main quote `q`, of kind `k`. -/
def trIn (anc : String) (q : String := "The judgment is reversed.") (k : HKind := .reversed) : Cert.Input :=
  let txt := anc ++ " " ++ q
  { kind := .hist k, textSha := "tr11", start := offOf txt q, stop := offOf txt q + q.length, quote := q,
    evidence := "cite:123 F.Supp.2d 456", part := "majority", shas := ["tr11"],
    windows := [{ start0 := 0, stop0 := txt.length, text := txt }], ordered := true, authority := some true,
    target := 9, citeIndex := some (idx "123fsupp2d456" 9) }
def trAnc (anc : String) (part : String := "majority") : Cert.Anchor :=
  { start := 0, stop := anc.length, quote := anc, part }
def trCit := trA "Court of International Trade"
def trDc := trA "District Court"
def trNone := trA "2000"
def trTribunals : List String := ["Court of International Trade", "Customs Court", "Court of Federal Claims",
  "Claims Court", "Veterans Court", "Court of Veterans Appeals"]
/-- The round-11 step on the anchored row `anc` (no trial bridge, no bridge line) under the claims `h`. -/
def trStep (anc : String) (h : Cert.HClaims) : Cert.Result := Cert.checkHistory8A none (trIn anc) (some (trAnc anc)) none h
#guard Cert.anchorTribunalCues ==
  ["court of international trade", "customs court", "court of federal claims", "claims court", "veterans court",
   "court of veterans appeals"]
-- each tribunal name: ok with the claim (alone or with anchorWide); anchorNoCue without it or under anchorWide alone
#guard trTribunals.all fun p => trStep (trA p) { anchorTribunal := true } == .ok
#guard trTribunals.all fun p => trStep (trA p) { anchorWide := true, anchorTribunal := true } == .ok
#guard trTribunals.all fun p => trStep (trA p) {} == .fail .anchorNoCue
#guard trTribunals.all fun p => trStep (trA p) { anchorWide := true } == .fail .anchorNoCue
#guard trTribunals.all fun p => !Cert.anchorCueOk9 {} (trAnc (trA p)) && Cert.anchorTribunalCue (trAnc (trA p))
-- the union: anchor, anchor_wide and anchor_wide9 cues are accepted under the claim too
#guard trStep trDc { anchorTribunal := true } == .ok && trStep trDc {} == .ok
#guard trStep (trA "CAFC") { anchorTribunal := true } == .ok && trStep (trA "CAFC") {} == .fail .anchorNoCue
#guard trStep (trA "Smith, District Judge") { anchorTribunal := true } == .ok
#guard trStep (trA "Smith, District Judge") {} == .fail .anchorNoCue
-- no cue of any of the four lists: anchorNoCue under every claim
#guard trStep trNone { anchorTribunal := true } == .fail .anchorNoCue
#guard trStep trNone { anchorWide := true, anchorTribunal := true } == .fail .anchorNoCue
-- the other anchored checks still bite under the claim
#guard Cert.checkHistory8A none (trIn ("See also " ++ trCit)) (some (trAnc ("See also " ++ trCit))) none
  { anchorTribunal := true } == .fail .anchorDisqualified
#guard Cert.checkHistory8A none (trIn "Foo Corp. v. United States (Court of International Trade).")
  (some (trAnc "Foo Corp. v. United States (Court of International Trade).")) none { anchorTribunal := true } ==
  .fail .anchorUnresolved
#guard Cert.checkHistory8A none (trIn trCit) (some (trAnc trCit "dissent")) none { anchorTribunal := true } ==
  .fail .anchorPart
#guard Cert.checkHistory8A none (trIn trCit) (some { trAnc trCit with start := 1 }) none { anchorTribunal := true } ==
  .fail .anchorMismatch
#guard Cert.checkHistory8A none (trIn trCit "The judgment is noted.") (some (trAnc trCit)) none
  { anchorTribunal := true } == .fail .noCue
#guard Cert.checkHistory8A none { trIn trCit with authority := some false } (some (trAnc trCit)) none
  { anchorTribunal := true } == .fail .noAuthority
#guard Cert.checkHistory8A none { trIn trCit with ordered := false } (some (trAnc trCit)) none
  { anchorTribunal := true } == .fail .targetLater
-- a claimed row without an anchor line, or with a bridge line: round 10's verdict
#guard Cert.checkHistory8A none (trIn trCit) none none { anchorTribunal := true } ==
  Cert.checkHistory8T none (trIn trCit) none none {}
#guard Cert.checkHistory8A none (trIn trCit) (some (trAnc trCit)) (some bGoodB) { anchorTribunal := true } ==
  Cert.checkHistory8T none (trIn trCit) (some (trAnc trCit)) (some bGoodB) {}
-- without the claim the round-11 step is round 10's (round-10 examples replayed)
#guard Cert.checkHistory8A (some tbGood) (tdIn) (some tdA) none {} == Cert.checkHistory8T (some tbGood) (tdIn) (some tdA) none {}
#guard Cert.checkHistory8A (some tbNeg) (tdIn) (some tdA) none {} == .fail .trialBridgeT
#guard Cert.checkHistory8A none jgIn (some jgAnc) none { anchorWide := true } == .ok
#guard Cert.checkHistory8A none jgIn (some jgAnc) none {} == .fail .anchorNoCue
#guard Cert.checkHistory11 none none [] (tdIn) (some tdA) none {} == Cert.checkHistory10T none none [] (tdIn) (some tdA) none {}
-- a counted trialBridge claim with the tribunal cue: the union cue, then the trial check
#guard Cert.checkHistory8A (some tbGood) (trIn trCit "The judgment of the trial court is reversed.") (some (trAnc trCit))
  none { anchorTribunal := true } == .ok
#guard Cert.checkHistory8A (some tbGood) (trIn trCit "The judgment of the trial court is reversed.") (some (trAnc trCit))
  none {} == .fail .anchorNoCue
#guard Cert.checkHistory8A (some tbNeg) (trIn trCit "The judgment of the trial court is reversed.") (some (trAnc trCit))
  none { anchorTribunal := true } == .fail .trialBridgeT
-- the round-11 step with zones and the remand test
#guard Cert.checkHistory11 none none [] (trIn trCit) (some (trAnc trCit)) none { anchorTribunal := true } == .ok
#guard Cert.checkHistory11 none none [] (trIn trCit) (some (trAnc trCit)) none {} == .fail .anchorNoCue

/-! Round 11 §5.2 (`round11/DESIGN11.md` §5.2, D11-5): identity-tie evidence. D (the acting node) prints T's docket
number, citation and date; T's own text prints them too. Checked with the round-8 bridge example's input `bIn`. -/

def idD := "Smith v. Jones, No. 14-50123, decided September 30, 2015, 123 F. 3d 456. We reverse."
def idT := "United States Court of Appeals. No. 14-50123. Smith v. Jones. Decided Sept. 30, 2015. 123 F.3d 456."
/-- An identity line: the form, the token, D's span `dS` of `txtD` and T's span `tS` of `txtT`. -/
def idL (form token dS tS : String) (txtD : String := idD) (txtT : String := idT) (tDate : Nat := 20150930) :
    Cert.Identity :=
  { form, token, dSha := "id11d", dWindows := [{ start0 := 0, stop0 := txtD.length, text := txtD }],
    dStart := offOf txtD dS, dStop := offOf txtD dS + dS.length, tSha := "id11t",
    tWindows := [{ start0 := 0, stop0 := txtT.length, text := txtT }], tStart := offOf txtT tS,
    tStop := offOf txtT tS + tS.length, tDate }
def iDk := idL "docket" "14-50123" "No. 14-50123" "No. 14-50123"
def iCite := idL "cite" "123 F.3d 456" "123 F. 3d 456" "123 F.3d 456"
def iDate := idL "date" "20150930" "September 30, 2015" "Sept. 30, 2015"
def iDOnly := idL "docket" "14-50123" "No. 14-50123" "Smith v. Jones"
/-- D's span of 200 + `k` characters (`k` ≤ 1 here) holding the docket token. -/
def idLongD (k : Nat) : String := "No. 14-50123" ++ String.ofList (List.replicate (188 + k) 'x')
def iLong (k : Nat) : Cert.Identity := idL "docket" "14-50123" (idLongD k) "No. 14-50123" (idLongD k ++ " end")
#guard Cert.identitySpan bIn iDk.dSha iDk.dWindows iDk.dStart iDk.dStop == some "no. 14-50123"
#guard Cert.identityOk bIn iDk && Cert.identityOk bIn iCite && Cert.identityOk bIn iDate
#guard Cert.identityThen (some iDk) bIn .ok == .ok && Cert.identityThen (some iDate) bIn .okUnverifiedBy == .okUnverifiedBy
-- docket / cite: the token in one span only; too short; no digit; empty
#guard !Cert.identityOk bIn iDOnly
#guard !Cert.identityOk bIn (idL "docket" "14-50123" "We reverse." "No. 14-50123")
#guard !Cert.identityOk bIn (idL "docket" "14-5" "No. 14-50123" "No. 14-50123")
#guard !Cert.identityOk bIn (idL "docket" "Smith" "Smith v. Jones" "Smith v. Jones")
#guard !Cert.identityOk bIn (idL "docket" "" "No. 14-50123" "No. 14-50123")
#guard !Cert.identityOk bIn (idL "cite" "123 F.3d 457" "123 F. 3d 456" "123 F.3d 456")
-- date: the token is not date(T); date(T) unknown; not 8 digits; a span without a date form; both forms accepted
#guard !Cert.identityOk bIn (idL "date" "20150930" "September 30, 2015" "Sept. 30, 2015" (tDate := 20150101))
#guard !Cert.identityOk bIn (idL "date" "20150930" "September 30, 2015" "Sept. 30, 2015" (tDate := 0))
#guard !Cert.identityOk bIn (idL "date" "2015-9-30" "September 30, 2015" "Sept. 30, 2015")
#guard !Cert.identityOk bIn (idL "date" "2015093" "September 30, 2015" "Sept. 30, 2015" (tDate := 2015093))
#guard !Cert.identityOk bIn (idL "date" "20150930" "Smith v. Jones" "Sept. 30, 2015")
#guard !Cert.identityOk bIn (idL "date" "20150930" "September 30, 2015" "Smith v. Jones")
#guard Cert.identityOk bIn (idL "date" "20150930" "September 30, 2015" "September 30, 2015" (txtT := idD))
-- an unknown form; the span bound (200 ok, 201 not); an empty span; no window; no hash
#guard !Cert.identityOk bIn { iDk with form := "name" }
#guard Cert.identityOk bIn (iLong 0) && !Cert.identityOk bIn (iLong 1)
#guard !Cert.identityOk bIn { iDk with dStop := iDk.dStart }
#guard !Cert.identityOk bIn { iDk with tWindows := [] } && !Cert.identityOk bIn { iDk with dSha := "" }
-- a failing verdict keeps its reason; a failing line on an admitted verdict is identityTie
#guard Cert.identityThen (some iDOnly) bIn (.fail .noAuthority) == .fail .noAuthority
#guard Cert.identityThen (some iDOnly) bIn .ok == .fail .identityTie
#guard Cert.identityThen (some iDOnly) bIn .okUnverifiedBy == .fail .identityTie
-- the round-11 step: no line = §5.1's; the bridge admits the row, then the line checks it
#guard Cert.checkHistory11I none none none [] bIn none (some bGoodB) {} == Cert.checkHistory11 none none [] bIn none (some bGoodB) {}
#guard Cert.checkHistory11I (some iDk) none none [] bIn none (some bGoodB) {} == .ok
#guard Cert.checkHistory11I (some iDOnly) none none [] bIn none (some bGoodB) {} == .fail .identityTie
#guard Cert.checkHistory11I (some iDOnly) none none [] bIn none none {} == .fail .targetUnresolved
#guard Cert.identitySpanMax == 200

end CaseLaw2.Examples
