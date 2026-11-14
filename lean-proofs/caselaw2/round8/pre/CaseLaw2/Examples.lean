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

end CaseLaw2.Examples
