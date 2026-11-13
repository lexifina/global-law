"""Second label fix for decisions2.tsv (hunt/HUNT.md "What to fix" 1 and 3): publication checked against the reporter
citation, and bench (en banc / circulated) re-read for the decisions that overrule, disapprove or recede.

    python -X utf8 labels_fix2.py scan [procs]     targeted re-read from git (<= 8 processes) ->
                                                   work/courts/pub2.tsv, work/courts/bench2.tsv
    python -X utf8 labels_fix2.py apply            decisions2.tsv -> decisions2.tsv.tmp -> rename

Composes after limits_fix.py: `apply` reads data/decisions2.tsv as limits_fix left it. It is idempotent (a changed row is
never a candidate again). When the input carries no `fix2` marker (a fresh limits_fix output) the input is kept as
data/decisions2.pre_pubfix.tsv (hard link) before the rename; a rerun on its own output leaves that backup alone.
`scan` writes only signals (evidence snippets of at most 140 characters), never opinion text.

PUBLICATION (src `p:reporter2:<reporter>+was:<old value>/<old evidence>`)
  Candidates: publication in {unpublished, table, summaryOrder, memorandum}, a citation in a reporter of published
  opinions (PUB_REP: official state reports, the regional reporters, F./F.2d/F.3d/F.4th, F. Supp., F.R.D., B.R., U.S.,
  T.C. and the other federal courts' reports), no F. App'x / T.C. Memo. / T.C. Summary Op. citation, and not a Florida
  PCA without opinion (those stay `table`). Reporters that also print memorandum or unpublished decisions do not count
  (N.Y.S., A.D., Misc., Cal. Rptr. alone, Ill. Dec., Mass. L. Rptr., Mass. App. Div., Pa. D. & C., Ohio Law Abs.,
  neutral and database citations).
  A candidate becomes `published` unless the decision itself says it is not (pub2.tsv signals):
    federal courts   always published, except a `table` row whose own heading is a table entry;
    state courts     kept when  (a) `ban`: its own banner or rule note (NOT FOR PUBLICATION, "Not to be published in
                     full" / abstract of decision, UNPUBLISHED OPINION / MEMORANDUM / Disposition, SUMMARY DISPOSITION
                     ORDER, decision without published opinion, Mo. Rule 84.16(b) / 30.25(b), Ind. App. R. 65(D), "shall
                     not be regarded as precedent", "no precedential value", Rule 1:28 heading) and no order publishing
                     it (`puborder`) or publishing it in part (`partial`);
                                (b) under 600 characters of opinion text (a disposition entry, not an opinion), unless
                     the old value is `table` from a "(table)" citation in the text.
BENCH (src `b:fix2:<evidence code>+was:<old value>`)
  Candidates (bench2.tsv): the treating decisions of treatments.tsv (overruled / disapproved / recededFrom) and the
  citing decisions of hunt/data/p3_panel.tsv, when bench is panel or unknown (never SCOTUS).
    enBanc      front-matter judges, the first or last 1,500 characters, or self-referring prose anywhere say en banc /
                in banc / in bank / before the full court (citations, rehearing petitions and denials rejected);
                "all the judges concur"; or the judges lines name at least 5 judges in a court that sits in panels of
                three (federal circuits, FL, TX, OH, PA, KY, NC, D.C.), at least 7 elsewhere (tiers A, B, D).
                9th Circuit from 1980: limitedEnBanc.
    circulated  federal circuits: the opinion (not a rehearing petition) was circulated to all (active) judges / the
                full court, the Irons footnote, 7th Cir. R. 40(e), "mini en banc", "approved by the full court".
"""
import collections, csv, os, re, shutil, subprocess, sys, threading
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan import parse_fm, SEC, judges_in, JSTOP, ev  # noqa: E402
from orders_scan import opinion_text  # noqa: E402

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
L2 = os.path.join(WORK, "caselaw-lean-2")
DATA = os.path.join(L2, "data")
WD = os.path.join(L2, "work", "courts")
SCOTUS = 2906
NONPUB = ("unpublished", "table", "summaryOrder", "memorandum")
STUB = 600

# ------------------------------------------------------------------------------------------------ reporters
_STATE = (r"Ala|Alaska|Ariz|Ark|Cal|Colo|Conn|Del|D\.C|Fla|Ga|Haw|Idaho|Ill|Ind|Iowa|Kan|Ky|La|Me|Md|Mass|Mich|Minn|Miss|"
          r"Mo|Mont|Neb|Nev|N\.H|N\.J|N\.M|N\.Y|N\.C|N\.D|Ohio|Okla|Or|Pa|R\.I|S\.C|S\.D|Tenn|Tex|Utah|Vt|Va|Wash|W\.Va|"
          r"Wis|Wyo|P\.R|V\.I|Guam")
PUB_REP = re.compile(
    r"^(?:F\.(?:2d|3d|4th)?|F\.Supp\.(?:2d|3d)?|F\.R\.D\.|B\.R\.|U\.S\.|S\.Ct\.|L\.Ed\.(?:2d)?|T\.C\.|B\.T\.A\.|Fed\.Cl\.|"
    r"Cl\.Ct\.|Ct\.Cl\.|M\.J\.|Vet\.App\.|C\.C\.P\.A\.|Ct\.Int'lTrade|Cust\.Ct\.|U\.S\.App\.D\.C\.|F\.Cas\.|"
    r"(?:A|N\.E|N\.W|P|S\.E|S\.W|So)\.(?:2d|3d)?|"
    r"(?:%s)\.?(?:St\.)?(?:App\.|Super\.|Commw\.|Crim\.|Civ\.App\.|Ch\.|Eq\.|Ann\.|Ct\.Cl\.)?(?:Ct\.)?(?:2d|3d|4th|5th)?)$"
    % _STATE)
NOT_PUB_REP = re.compile(r"App'x|Appx|T\.C\.Memo|T\.C\.Summary|Summary ?Op")


def reporter(c):
    m = re.match(r"\s*\d+\s+(.+?)\s+[\dA-Z-]+\s*$", c)
    return re.sub(r"\s+", "", m.group(1)) if m else ""


def pub_reporter(cites):
    """the first reporter of published opinions among the citations; '' when none, or with an unpublished-series cite"""
    if not cites or NOT_PUB_REP.search(cites.replace(" ", "")) or NOT_PUB_REP.search(cites):
        return ""
    for c in cites.split("|"):
        r = reporter(c)
        if r and PUB_REP.match(r):
            return r
    return ""


# ------------------------------------------------------------------------------------------------ publication signals
BAN = re.compile(
    r"[Nn]ot to be published|NOT TO BE (?:OFFICIALLY )?PUBLISHED|[Aa]bstract of (?:the )?[Dd]ecision|"
    r"UNPUBLISHED (?:MEMORANDUM|OPINION|ORDER|DISPOSITION|DECISION)(?! (?:OF|DATED|ISSUED|WITHDRAWN|ON)\b)|Unpublished (?:Memorandum|Opinion|Disposition|Order)"
    r"(?: Decision)?\b(?! (?:under|pursuant|of|in|is|are|was|may|filed|issued|dated|at)\b)|"
    r"SUMMARY DISPOSITION ORDER|[Dd]ecisions? [Ww]ithout [Pp]ublished [Oo]pinions?|[Ww]ithout [Rr]eported [Oo]pinions?|"
    r"NOT (?:DESIGNATED |RECOMMENDED )?FOR (?:FULL[- ]TEXT |OFFICIAL )?PUBLICATION|[Nn]ot [Ff]or (?:[Oo]fficial )?"
    r"[Pp]ublication|DO NOT PUBLISH|[Dd]o [Nn]ot [Pp]ublish|NON-?PRECEDENTIAL|NOT PRECEDENTIAL|"
    r"MEMORANDUM AND ORDER PURSUANT TO RULE|Rule 84\.16\(b\)|Rule 30\.25\(b\)|Appellate Rule 65\(D\)|"
    r"(?:shall|will|may|should) not be regarded as precedent|(?:have|has|be of|is of|of) no precedential value|"
    r"(?:this|the) (?:opinion|decision|disposition|order|memorandum)[^.]{0,40}? (?:is|will be|shall be) not (?:designated "
    r"|to be |appropriate |intended |recommended |selected )?(?:for )?(?:official )?publi(?:cation|shed)")
TABLE_SELF = re.compile(r"[Dd]ecisions? [Ww]ithout [Pp]ublished [Oo]pinions?|[Ww]ithout [Rr]eported [Oo]pinions?|"
                        r"Table of Decisions|Unpublished Disposition|^\s*TABLE\s*$", re.M)
PUBORDER = re.compile(
    r"(?:order(?:ed|s)?|direct(?:ed|s)?)[^.]{0,80}?\b(?:be |to be |is )?publi(?:shed|cation)|motion (?:to publish|for "
    r"publication)[^.]{0,120}?grant|grant[^.]{0,80}?(?:motion|request) (?:to publish|for publication)|(?:now|hereby) "
    r"(?:designated|ordered|certified|approved) for publication|redesignat|publication (?:is|was) (?:hereby )?(?:ordered|"
    r"granted)|status is changed from .UNPUBLISHED. to .PUBLISHED|ordered published|[Cc]ertified for (?:[Pp]artial )?"
    r"[Pp]ublication|CERTIFIED FOR (?:PARTIAL )?PUBLICATION", re.I)


PARTIAL = re.compile(r"(?:portions?|parts?|sections?|issues?|material|remainder|discussion|pages?)[^.]{0,80}?(?:is|are) not "
                     r"(?:to be |for )publi(?:shed|cation)|nonpublish(?:able|ed) (?:portion|part|material)|publi(?:shed|cation) "
                     r"in part|[Pp]artial(?:ly)? publi(?:shed|cation)")


def pub_signals(text):
    fm, body = parse_fm(text)
    op = opinion_text(text).strip()
    head, tail = body[:3000], body[-1500:]
    out = []
    for zone in (head, tail):
        for m in BAN.finditer(zone):
            pre = zone[max(0, m.start() - 2):m.start()]
            if re.search(r"[(\"“‘']\s?$", pre):  # "(unpublished opinion)", a quoted rule: a mention, not a banner
                continue
            out.append("ban=" + ev(zone[max(0, m.start() - 25):m.end() + 20]))
            break
        if out:
            break
    m = TABLE_SELF.search(body[:1500])
    if m:
        out.append("tableself=" + ev(body[max(0, m.start() - 20):m.end() + 20]))
    for z in (head, tail):
        hit = False
        for m in PUBORDER.finditer(z):
            if re.search(r"\bnot\b|unpublish|\bclass\b", z[max(0, m.start() - 15):m.end() + 15], re.I):
                continue  # "ordered not to be published"; "redesignated the class"
            out.append("puborder=" + ev(z[max(0, m.start() - 20):m.end() + 20]))
            hit = True
            break
        if hit:
            break
    m = PARTIAL.search(head) or PARTIAL.search(tail)
    if m:
        out.append("partial=" + ev(m.group(0)))
    return len(op), out


# ------------------------------------------------------------------------------------------------ bench signals
EBW = re.compile(r"\b(?:en|in)\s+banc\b|\bin\s+bank\b", re.I)
EB_REJECT = re.compile(
    r"denied|deny|denying|denial|petition|suggestion|motions? for|request|\bpoll|whether to|unless|absent|until|\bonly\b|"
    r"\bmay\b|\bcan\b|could|would|should|must|prior panel|\bsee\b|\bcf\.|supra|\bin [A-Z][A-Za-z.'’]+ v\.|decision in|"
    r"opinion in|affirmed by|reversed by|overruled by|\ban en banc|required?|without|\bnot\b|\bnor\b|\bno\b|cannot|"
    r"pending|vacated|\bif\b|absence|power|authority to|\(en banc\)|\(in banc\)|dissolv|declin|refus|reject|withdrawn|"
    r"elusive|rule for|Veterans Court|District Court|\bBoard\b|Commission|Tax Court|court below|lower court", re.I)
EB_OK = re.compile(
    r"sitting (?:en|in) ban[ck]|(?:court|Court|COURT|judges|Judges),? (?:en|in|EN|IN|En|In) (?:ban[ck]|BAN[CK]|Ban[ck])|"
    r"(?:argued|reargued|submitted|resubmitted|heard|reheard|considered|reconsidered|decided|re-?argued) (?:and (?:submitted|"
    r"decided) )?(?:en|in) ban[ck]|(?:rehearing|reargument|reconsideration|review|consideration|hearing|rehear|reconsider)"
    r"[^.]{0,30}(?:en|in) ban[ck][^.]{0,40}(?:granted|ordered|was had)|(?:granted|ordered|grants?|orders?)[^.]{0,60}"
    r"(?:rehearing|reargument|reconsideration|review|consideration|hearing|reheard|heard)[^.]{0,20}(?:en|in) ban[ck]|"
    r"(?:we|court|Court) (?:has |have |had )?(?:took|take|taken|heard|hear|reheard|rehear|sat|sit|voted to (?:re)?hear|"
    r"agreed to (?:re)?hear|decided to (?:re)?hear|convened|considered|consider|reconsidered)[^.]{0,60}(?:en|in) ban[ck]|"
    r"\b(?:on|upon) (?:rehearing|reargument|reconsideration|hearing|consideration) (?:en|in) ban[ck]|"
    r"^\W*(?:opinion |decision )?(?:on |upon )?(?:(?:motion for )?(?:rehearing|reconsideration|reargument|hearing) )?"
    r"(?:en|in) ban[ck]\W*(?:opinion)?\W*$|(?:en|in) ban[ck] (?:court|opinion|decision|panel)\b|(?:en|in) ban[ck],? we\b|"
    r"\b(?:en|in) ban[ck]\W*$", re.I | re.M)
EB_STRICT = re.compile(  # self-referring prose anywhere in the opinion
    r"[Ss]itting (?:en|in) banc,? we\b|[Ww]e,? sitting (?:en|in) banc|[Tt]his [Cc]ourt,? sitting (?:en|in) banc,? (?:now|"
    r"hereby|today|we|holds?|overrules?|recedes?|concludes?)|[Tt]he [Cc]ourt has (?:re)?heard this (?:matter|case|cause|"
    r"appeal) (?:en|in) banc|(?:rehearing|reargument|reconsideration|review|consideration|hearing) (?:en|in) banc (?:was|"
    r"has been|is) (?:hereby |then |subsequently |thereafter )?(?:granted|ordered)|[Ww]e (?:granted|ordered|took|heard|"
    r"reheard|voted to (?:re)?hear|agreed to (?:re)?hear|sua sponte (?:ordered|granted)|have (?:taken|heard|considered|"
    r"reheard)|decided to (?:re)?hear|convened|now sit)[^.]{0,80}?(?:en|in) banc|OPINION (?:UP)?ON (?:REHEARING|HEARING|"
    r"RECONSIDERATION|REARGUMENT) EN BANC|^\W*(?:UP)?ON (?:REHEARING|HEARING|RECONSIDERATION|REARGUMENT|MOTION FOR "
    r"REHEARING) EN BANC\W*$|[Tt]he (?:en|in) banc [Cc]ourt (?:now |today |hereby |also |therefore |unanimously )?(?:holds|"
    r"overrules|recedes|concludes|adopts|affirms|reverses|agrees|disapproves|finds|vacates|withdraws|is of the)|"
    r"[Ww]e (?:now |therefore |hereby |today )?(?:recede|overrule|disapprove|hold|conclude)[^.]{0,40}? (?:en|in) banc\b|"
    r"\b(?:en|in) banc,? (?:we|this [Cc]ourt) (?:now |hereby |today |therefore )?(?:recede|overrule|hold|conclude|"
    r"disapprove|adopt|affirm|reverse|granted|voted)|(?:argued|reargued|heard|reheard|submitted) before (?:this|the) "
    r"[Cc]ourt (?:sitting )?(?:en|in) banc|(?:case|appeal|cause|matter) (?:is|was|has been|comes?|came)[^.]{0,40}? before "
    r"(?:this|the) [Cc]ourt (?:sitting )?(?:en|in) banc|[Cc]ourt (?:sitting )?(?:en|in) banc (?:now |hereby |today )?"
    r"(?:holds|overrules|recedes|concludes|adopts|granted|ordered|voted|has (?:decided|determined|concluded|considered))|"
    r"(?:before|by) the (?:full|whole|entire) [Cc]ourt (?:sitting )?(?:en|in) banc|[Tt]his (?:en|in) banc (?:[Cc]ourt|"
    r"opinion|decision|proceeding|rehearing|hearing)|[Ww]e (?:have |now |therefore )?sua sponte (?:consider|considered|"
    r"ordered|granted|determined|elected|voted|take|took|hear|heard)[^.]{0,60}? (?:en|in) banc|(?:considered|heard|reheard|"
    r"decided)[^.]{0,30} (?:en|in) banc (?:on|upon) (?:the )?(?:court|Court)'?s own motion|"
    r"(?:certified|submitted|resubmitted|set|scheduled|listed|referred|assigned|transferred|taken|ordered)[^.]{0,80}? "
    r"(?:for|to) (?:the |this )?(?:[Cc]ourt )?(?:sitting )?(?:en|in) banc(?: (?:review|consideration|argument|reargument|"
    r"hearing|rehearing|certification|determination|decision|disposition))?|(?:to|by) (?:this|the) [Cc]ourt sitting "
    r"(?:en|in) banc|by an (?:en|in) banc court|(?:en|in) banc consideration by (?:the|this) [Cc]ourt|[Cc]ourt (?:en|in) "
    r"banc in order to", re.M)
FULL = re.compile(r"(?:considered|heard|reheard|decided|determined|approved|reviewed|reconsidered|concurred in|adopted|"
                  r"argued|reargued)[^.]{0,30}? (?:by|before) (?:the|a) (?:full|whole|entire) (?:[Cc]ourt|"
                  r"bench)|\b(?:the )?(?:full|whole|entire) [Cc]ourt (?:concurs?|sitting|has (?:considered|approved|"
                  r"concurred|decided|determined|voted))|^\W*(?:Before|BEFORE) the (?:full|whole|entire) [Cc]ourt|"
                  r"^\W*(?:FULL|WHOLE|Full|Whole) (?:COURT|Court)\W*$", re.M)
ALLJ = re.compile(r"\b[Aa]ll (?:the |of the )?(?:[Jj]udges|JUDGES|[Jj]ustices|JUSTICES|members of the [Cc]ourt)(?: of th(?:e|is)"
                  r" [Cc]ourt)? (?:concur|CONCUR)")
CIRC2 = re.compile(
    r"(?:opinion|decision|holding|ruling|part|section|footnote|portion|overruling|conclusion|paragraph|result|issue|"
    r"question|matter|case|draft)[^.]{0,160}?\b(?:been |was |were |is |being )?circulated\b[^.]{0,60}?(?:all|full|entire|"
    r"active|each|every|en banc|in banc|members|regular)|circulated (?:among|to|before|in advance)[^.]{0,120}?(?:judges|"
    r"members|[Cc]ourt)[^.]{0,250}?(?:no (?:active )?judge|none of|not one|a majority|majority of|all (?:of whom )?(?:approv|"
    r"concur|agree)|favored|voted|requested|objection|rehear|en banc|in banc)|circulated (?:this|the|our) (?:panel )?"
    r"(?:opinion|decision|holding|draft|portion|part|order|footnote|section)[^.]{0,60}? (?:to|among) (?:all|the|each|every)|Irons footnote|Irons v\. Diamond|"
    r"mini[- ]en[- ]banc|Circuit Rule 40\(e\)|Cir\. ?R\. 40\(e\)|Rule 40\(e\)|(?:considered|reviewed|approved|endorsed|"
    r"concurred in|agreed to)[^.]{0,80}? by (?:the )?(?:full|entire|en banc|in banc|whole) [Cc]ourt|by (?:all|each of) "
    r"(?:the )?(?:active |regular )?(?:judges|members) of (?:the|this) [Cc]ourt|all (?:the )?active (?:circuit )?judges"
    r"[^.]{0,80}(?:concur|agree|approv)|(?:approval|concurrence|consent|authorization) of (?:all|the full|the entire|"
    r"every|each)[^.]{0,30}(?:judges?|[Cc]ourt|members)", re.I)
CIRC_REJECT = re.compile(r"petition|suggestion|request for|motion for|application for", re.I)
NAME_CAPS = re.compile(r"\b(?:Mc|Mac|La|Le|De|Di|Du|Van|Von|St\.? ?|O['’])?[A-Z]{2,}(?:[-'’][A-Z]+)*\b")
NAME_ANY = re.compile(r"\b(?:Mc|Mac|O['’])?[A-Z][A-Za-z'’\-]{2,}\b")
JSTOP2 = JSTOP | set("""FILES FILED FILE WHICH JOIN JOINS JOINED JOINING AGREE AGREES AGREED VIEWS SUPPORT REMAND REVERSAL
AFFIRMANCE STATEMENT RESULT SPECIALLY SEPARATE CONCURS CONCURRING DISSENTS WRITTEN REASONS ASSIGNS ASSIGNING WOULD DENY
GRANT RECUSED PARTICIPATE PARTICIPATED PARTICIPATION CONSIDERATION DECISION TOOK SAT PRESIDENT VICE JUDGMENT ONLY ACTIVE
SERVICE EMERITUS VISITING SITTING ASSIGNMENT DESIGNATION TEMPORE JUSTICE JUSTICES CHIEF JUDGE JUDGES CIRCUIT COURT PART
WITH WITHOUT OPINION AND THE FOR NOT DID DOES FOLLOWING ORIGINAL SUBSTITUTED WITHDRAWN PRIOR SUBMISSION ARGUMENT ORAL
PANEL FULL ENTIRE WHOLE BANC TEXAS FLORIDA LOUISIANA OHIO PENNSYLVANIA KENTUCKY COMPOSED CONSISTING TERM SPECIAL MEMBERS
SESSION SUPERIOR COMMONWEALTH SUPREME APPEALS APPELLATE DISTRICT SENIOR RETIRED FORMER ASSOCIATE PRESIDING ACTING PRO TEM
JJ JR SR III II IV ALL NONE BOTH EACH ALSO THIS THAT THESE THOSE HIS HER THEIR WHO WHOM WHEN WHERE DISSENT DISSENTING
CONCUR CONCURRENCE MAJORITY PLURALITY PER CURIAM REHEARING DENIED GRANTED EN BEFORE PRESENT ABSENT EXCUSED VACANCY""".split())


VOTE_NOISE = re.compile(r"sitting by|assign|designat|retired|of the [A-Z][a-z]+ (?:County|District|Circuit|Appellate)|"
                        r"Court of Common Pleas|took no part|not participat|did not (?:sit|participate)|recus|"
                        r"disqualif|absent|deceased|petition|rehearing", re.I)


def judge_names(lines, author=""):
    """distinct judges named in the front-matter judges lines (one name per comma/and part), plus the author"""
    names = set()
    for ln in lines:
        before = bool(re.search(r"\b(?:Before|BEFORE|Present|PRESENT|composed of|COMPOSED OF)\b", ln))
        if not before and VOTE_NOISE.search(ln):
            continue
        ln = re.sub(r"\([^()]{0,40}\)|\[[^\[\]]{0,40}\]", " ", ln)
        caps = [t for t in NAME_CAPS.findall(ln) if t.upper() not in JSTOP2 and len(t) >= 3]
        rx = NAME_CAPS if len(caps) >= 2 else NAME_ANY
        prev_single = False
        for part in re.split(r",|;|\band\b|\bAND\b|&", ln):
            if prev_single and re.match(r"^\s*[A-Z][A-Za-z]+ [A-Z]\.?\s*$", part):  # "DOWNEY, JAMES C."
                prev_single = False
                continue
            toks = [t for t in rx.findall(part) if t.upper() not in JSTOP2 and len(t) >= 3]
            prev_single = len(toks) == 1
            if toks:
                names.add(re.sub(r"[^A-Z]", "", toks[-1].upper()))
    if author and names:
        toks = [t for t in NAME_ANY.findall(re.sub(r"\(.*?\)", " ", author.split(",")[0])) if t.upper() not in JSTOP2]
        if toks:
            names.add(re.sub(r"[^A-Z]", "", toks[-1].upper()))
    names.discard("")
    return names


def fm_judges(text):
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    for line in text[3:end].splitlines():
        if line.startswith("judges:"):
            v = line[7:].strip()
            parts = re.findall(r'"((?:[^"\\]|\\.)*)"', v)
            return parts or ([v] if v and v not in ("[]", "null") else [])
    return []


def eb_zone(zone, strict_lines=True):
    for m in EBW.finditer(zone):
        a, b = m.start(), m.end()
        ls = zone.rfind("\n", 0, a) + 1
        le = zone.find("\n", b)
        le = len(zone) if le < 0 else le
        ctx = zone[max(ls, a - 110):min(le, b + 70)]
        line = zone[ls:le].strip()
        if EB_REJECT.search(ctx):
            continue
        if re.search(r"\(\s*$", zone[max(0, a - 2):a]) and len(line) > 60:  # "(en banc)" after a citation
            continue
        if re.search(r"\d{4}\)\s*$|Cir\.\s*$|App\.\s*$", zone[max(0, a - 12):a]):
            continue
        if len(line) <= 90 and not re.search(r"\bv\.|\d{4}\)", line):
            return "eb_line", ctx
        if EB_OK.search(ctx):
            return "eb_prose", ctx
    return None


def bench_signals(text):
    fm, body = parse_fm(text)
    out = []
    jl = fm_judges(text)
    fmj = " ; ".join(jl)
    # the opinion's author, from the first opinion section title
    author = ""
    m = re.search(r"^## (?:Majority|Lead|Plurality|Combined)[^\n(]*\(([^)\n]{3,80})\)", body, re.M)
    if m:
        author = m.group(1)
    n = len(judge_names(jl, author))
    out.append("nj=%d" % n)
    if fmj and EBW.search(fmj):
        r = eb_zone(fmj.replace(" ; ", "\n"))
        if r:
            out.append("eb_fm=" + ev(r[1], 110))
    head, tail = body[:1500], body[-1500:]
    for nm, zone in (("h", head), ("t", tail)):
        r = eb_zone(zone)
        if r:
            out.append("%s_%s=%s" % (r[0], nm, ev(r[1], 110)))
            break
    m = EB_STRICT.search(body)
    if m:
        ctx = body[max(0, m.start() - 60):m.end() + 40]
        if not re.search(r"denied|deny|petition for|suggestion|[\"“][^\"”]{0,60}$", body[max(0, m.start() - 80):m.start()]) \
                and not re.search(r"dissolv|declin|refus|withdrawn|Veterans Court|District Court|\bBoard\b|Tax Court|"
                                  r"court below|lower court|Supreme Court", ctx):
            out.append("eb_strict=" + ev(ctx, 140))
    for zone in (fmj, head, tail):
        m = FULL.search(zone)
        if m and not re.search(r"\bnot\b|denied|petition|[\"“]", zone[max(0, m.start() - 60):m.end() + 30]):
            out.append("full=" + ev(zone[max(0, m.start() - 30):m.end() + 30]))
            break
    for zone in (fmj, head, tail):
        m = ALLJ.search(zone)
        if m:
            out.append("allj=" + ev(zone[max(0, m.start() - 20):m.end() + 20]))
            break
    for m in CIRC2.finditer(body):
        pre = body[max(0, m.start() - 160):m.start() + 40]
        if CIRC_REJECT.search(pre) or CIRC_REJECT.search(m.group(0)):
            continue
        out.append("circ=" + ev(body[max(0, m.start() - 10):m.end() + 40], 110))
        break
    return out


# ------------------------------------------------------------------------------------------------ scan (git re-read)
def one_repo(args):
    repo, items = args
    p = subprocess.Popen(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, creationflags=0x08000000 if os.name == "nt" else 0)

    def feed():
        for _, path, _ in items:
            p.stdin.write(("HEAD:%s\n" % path).encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    out = []
    for node, _, kinds in items:
        header = p.stdout.readline().split()
        if len(header) < 3 or header[1] == b"missing":
            out.append((node, kinds, None, None))
            continue
        data = p.stdout.read(int(header[2]))
        p.stdout.read(1)
        text = data.decode("utf-8", "replace").replace("\r\n", "\n")
        pub = pub_signals(text) if "p" in kinds else None
        ben = bench_signals(text) if "b" in kinds else None
        out.append((node, kinds, pub, ben))
    p.wait()
    return repo, out


def bench_candidates():
    want = set()
    with open(os.path.join(DATA, "treatments.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 6)
            if len(p) > 4 and p[4] in ("overruled", "disapproved", "recededFrom"):
                want.add(p[1])
    hp = os.path.join(L2, "hunt", "data", "p3_panel.tsv")
    if os.path.exists(hp):
        with open(hp, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                want.add(r["citing"])
    return want


def scan(procs=8):
    procs = min(8, int(procs))
    nonpub = {}
    with open(os.path.join(DATA, "decisions2.tsv"), encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            if r[5] in NONPUB and ";p:fl-pca-without-opinion;" not in r[8]:
                nonpub[r[0]] = 1
            elif ";p:reporter2:" in r[8]:  # already fixed by an earlier apply: still a candidate for the scan
                nonpub[r[0]] = 1
    bwant = bench_candidates()
    by = collections.defaultdict(list)
    reps = {}
    with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            k = ""
            if p[0] in nonpub:
                r = pub_reporter(p[5])
                if r:
                    k += "p"
                    reps[p[0]] = r
            if p[0] in bwant:
                k += "b"
            if k:
                by[p[1]].append((p[0], p[2], k))
    jobs = []
    for repo, items in by.items():
        for i in range(0, len(items), 4000):
            jobs.append((repo, items[i:i + 4000]))
    jobs.sort(key=lambda x: -len(x[1]))
    pp, bp = os.path.join(WD, "pub2.tsv"), os.path.join(WD, "bench2.tsv")
    np_, nb, miss = 0, 0, 0
    with open(pp + ".part", "w", encoding="utf-8", newline="\n") as fp, \
            open(bp + ".part", "w", encoding="utf-8", newline="\n") as fb, ProcessPoolExecutor(procs) as ex:
        for repo, rows in ex.map(one_repo, jobs):
            for node, kinds, pub, ben in rows:
                if pub is None and ben is None:
                    miss += 1
                    continue
                if pub is not None:
                    fp.write("%s\t%s\t%d\t%s\n" % (node, reps[node], pub[0], "|".join(pub[1]) or "-"))
                    np_ += 1
                if ben is not None:
                    fb.write("%s\t%s\n" % (node, "|".join(ben) or "-"))
                    nb += 1
    for a in (pp, bp):  # node order
        rows = sorted(open(a + ".part", encoding="utf-8"), key=lambda l: int(l.split("\t", 1)[0]))
        with open(a + ".part", "w", encoding="utf-8", newline="\n") as f:
            f.writelines(rows)
        os.replace(a + ".part", a)
    print("pub2 rows %d, bench2 rows %d, missing blobs %d" % (np_, nb, miss))


# ------------------------------------------------------------------------------------------------ apply
PANEL3 = re.compile(r"United States Court of Appeals for the|Florida District Court|Texas Courts? of (?:Civil )?Appeals|"
                    r"Courts? of (?:Civil )?Appeals of Texas|Superior Court of Pennsylvania|Commonwealth Court of "
                    r"Pennsylvania|Ohio Courts? of Appeals|Courts? of Appeals of Ohio|Kentucky Court of Appeals|North "
                    r"Carolina Court of Appeals|Court of Appeals (?:of|for) the District of Columbia|District of Columbia "
                    r"Court of Appeals")


def parse_codes(s):
    out = {}
    if s != "-":
        for part in s.split("|"):
            k, _, v = part.partition("=")
            out.setdefault(k, v)
    return out


def load_courts():
    ep = collections.defaultdict(list)
    for line in open(os.path.join(DATA, "courts2.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        ep[int(f[0])].append((int(f[1]), int(f[2]), f[3], int(f[4]), f[5], int(f[7])))
    return ep


def epoch_of(ep, cid, date):
    rows = ep.get(cid)
    if not rows:
        return (0, 0, "", -1, "?", 0)
    for r in rows:
        if r[0] <= date <= r[1]:
            return r
    return rows[-1] if date > rows[-1][1] else rows[0]


def decide_pub(old, oldev, system, oplen, sig):
    """-> True when the row becomes published"""
    if system == 0:
        return not (old == "table" and "tableself" in sig)
    if old == "table":
        return "tableself" not in sig
    if "partial" in sig:
        return True
    if "ban" in sig and "puborder" not in sig:
        return False
    if "puborder" in sig:
        return True
    return oplen >= STUB


def decide_bench(sig, name, system, tier, circuit, date):
    """-> (value, evidence code) or None"""
    nj = int(sig.get("nj", "0") or 0)
    ca9 = system == 0 and tier == "A" and circuit == 9 and date >= 19800101
    eb = None
    for k in ("eb_fm", "eb_line_h", "eb_line_t", "eb_prose_h", "eb_prose_t", "eb_strict"):
        if k in sig:
            eb = k
            break
    if tier == "L":
        if eb in ("eb_fm", "eb_line_h", "eb_line_t"):
            return "enBanc", eb
        return None
    if tier not in ("A", "B", "D"):
        return None
    fedcirc = system == 0 and tier == "A" and circuit > 0
    if "circ" in sig and fedcirc and eb not in ("eb_fm", "eb_line_h", "eb_line_t") and nj < 5:
        return "circulated", "circ"  # the circulation footnote names the en banc court; the panel decided
    if not eb:
        thr = 5 if PANEL3.search(name) else 7
        if nj >= thr:
            eb = "judges=%d" % nj
        elif "allj" in sig and system != 0:
            eb = "allj"
        elif "full" in sig:
            eb = "full"
    if eb:
        return ("limitedEnBanc" if ca9 else "enBanc"), eb + ("+ca9-limited" if ca9 else "")
    return None


def apply():
    ep = load_courts()
    pub2, bench2 = {}, {}
    for line in open(os.path.join(WD, "pub2.tsv"), encoding="utf-8"):
        n, rep, oplen, flags = line.rstrip("\n").split("\t")
        pub2[n] = (rep, int(oplen), parse_codes(flags))
    for line in open(os.path.join(WD, "bench2.tsv"), encoding="utf-8"):
        n, flags = line.rstrip("\n").split("\t")
        bench2[n] = parse_codes(flags)
    stats = collections.Counter()
    src_p = os.path.join(DATA, "decisions2.tsv")
    tmp = src_p + ".tmp"
    marked = 0
    with open(src_p, encoding="utf-8") as f, open(tmp, "w", encoding="utf-8", newline="\n") as fo:
        for line in f:
            r = line.rstrip("\n").split("\t")
            n, s = r[0], r[8]
            if ";p:reporter2:" in s or ";b:fix2:" in s:
                marked += 1
            if r[5] in NONPUB and n in pub2 and ";p:fl-pca-without-opinion;" not in s:
                rep, oplen, sig = pub2[n]
                e = epoch_of(ep, int(r[1]), int(r[2]))
                m = re.search(r";p:([^;]*);", s)
                if decide_pub(r[5], m.group(1) if m else "", e[3], oplen, sig):
                    s = s.replace(";p:%s;" % m.group(1), ";p:reporter2:%s+was:%s/%s;" % (rep, r[5], m.group(1)), 1)
                    stats["publication\t%s -> published" % r[5]] += 1
                    r[5] = "published"
                else:
                    stats["publication kept (reporter-cited)\t%s" % r[5]] += 1
            if r[4] in ("panel", "unknown") and n in bench2 and int(r[1]) != SCOTUS:
                e = epoch_of(ep, int(r[1]), int(r[2]))
                d = decide_bench(bench2[n], e[2], e[3], e[4], e[5], int(r[2]))
                if d:
                    m = re.search(r";b:([^;]*);", s)
                    s = s.replace(";b:%s;" % m.group(1), ";b:fix2:%s+was:%s;" % (d[1], r[4]), 1)
                    stats["bench\t%s -> %s" % (r[4], d[0])] += 1
                    stats["bench evidence\t%s" % re.sub(r"\d+", "N", d[1])] += 1
                    r[4] = d[0]
            r[8] = s
            stats["rows"] += 1
            fo.write("\t".join(r) + "\n")
    bak = os.path.join(DATA, "decisions2.pre_pubfix.tsv")
    if marked == 0:  # the input is limits_fix output: keep it
        if os.path.exists(bak):
            os.remove(bak)
        try:
            os.link(src_p, bak)
        except OSError:
            shutil.copy2(src_p, bak)
    os.replace(tmp, src_p)
    print("input rows already carrying a fix2 marker: %d" % marked)
    for k, v in sorted(stats.items()):
        print("%s\t%d" % (k, v))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        scan(*sys.argv[2:3])
    else:
        apply()
