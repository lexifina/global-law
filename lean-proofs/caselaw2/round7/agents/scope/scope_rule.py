"""Round 7, track B2 (agent `scope`): the scope of an overruling, settled from the overruling sentence itself.

    python -X utf8 round7/agents/scope/scope_extract.py           # the sentences (sentences.jsonl.gz)
    python -X utf8 round7/agents/scope/scope_rule.py [--base round6/history/stage/final2]

DESIGN7 section 6 (B2). The rule reads the row's quote and the one sentence that holds it (git text, scope_extract.py)
and nothing else: no answer key, no note, no list of cases. Rows: treatments rows of kind overruled / abrogated /
disapproved / recededFrom.

P rows (explicit = 1, scope partialUnknown or unknown):
  (b) the sentence has a LIMITING phrase (LIMIT: "to the extent", "insofar", "in part", "on this point", "as to",
      "on other grounds", ...) or names a PART of the case as what is acted on (PART_OBJECT: "the language", "dictum",
      "statement", "holding", "rule", "reasoning", "portion", ...)            -> partial: partialUnknown stays;
                                                                                  unknown -> partialUnknown
  (a) otherwise, when the sentence is a present act of the court on the named case:
        - the row's target evidence (cite:/name:) resolves inside the sentence;
        - an act form (ACT: "X is overruled", "we overrule X", "we disapprove X", "we recede from X",
          "X ... is no longer good law", ...) is in the sentence, and the target's evidence lies in that act's
          object zone (the subject before a passive verb / the object after an active verb, in the same clause);
        - no report or hedge (HEDGE: "has been overruled", "overruled by", "decline to overrule", "whether",
          "would overrule", "not ... overrule", "impliedly", ...), and no anaphor as the thing acted on
          ("they are overruled" with the case named elsewhere is left alone);
                                                                               -> scope all
        - the sentence's bounds were found (scope_extract.sentence_span2; a sentence cut at the search limit is
          left alone);
        - the case is not only cited as authority for the act ("in light of X, we overrule Y": row X is left).
      A list the act verb introduces counts as its object ("are overruled, including X; Y", "are overruled: X",
      "[e.g., X]", "we overrule our contrary decisions, namely X").
      When one of these fails the row is left as it is (and an `unknown` row becomes partialUnknown only under (b)).
  (c) one verb on several cases ("A, B and C are overruled"): every row of the sentence is judged as above, each on
      its own evidence; a limiting phrase anywhere in the sentence keeps every row of it partial.
I rows (explicit = 1, scope issues:...): left alone, except a row with exactly one issue on a target with exactly one
  holding (holdings.tsv) whose sentence passes (a) -> all. Counted either way.
W rows (witness rows): never rewritten. Counted: "overruled in part by" / "on other grounds by" (partial) vs plain
  "overruled by" (as is).

Writes in this folder: replace.tsv (full 16-column treatments rows; only the scope column differs from the base),
decisions.tsv (every candidate: id, class, old scope, new scope, reason, sentence), counts.tsv, sample40.tsv (40 changed
rows, seed 7), control_partial40.tsv (40 P rows the rule keeps partial, seed 8: the audit's control on half (b)).
"""
import argparse
import gzip
import json
import os
import random
import re
import sys
from collections import Counter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round5", "recog"))
import recog_common as R  # noqa: E402
RC = R.RC

NEG4 = ("overruled", "abrogated", "disapproved", "recededFrom")


def rx(words):
    return re.compile(r"(?<![a-z0-9])(?:" + "|".join(words) + r")(?![a-z0-9])")


# ---------------------------------------------------------------------------------------------------- phrase lists
# (b) limiting phrases: the act reaches the case only so far, only on a point, only as to something, only where it
# conflicts
LIMIT = rx([
    r"(?:to|in) (?:the|that|this|any|whatever|what|such|some|a|which|an|so|its|their) (?:\w+ )?ex\w*nt", r"extent",
    r"(?:to|in) (?:the|that|this|any|whatever|such|what) ex ?te[a-z]{1,2}t?",
    r"no longer (?:the )?law(?: of [a-z ]{1,30})? that",
    r"(?:can|could|may|might|is to|are to) be (?:\w+ )?(?:construed|read|interpreted|understood|viewed|taken|"
    r"considered|deemed) (?:as|to)", r"stands? for the proposition", r"inasmuch",
    r"insofar", r"in so f[ao]r", r"so\W{0,2} ?far", r"so far as", r"as far as", r"so far", r"in part",
    r"(?:relevant|pertinent|material|some|one|certain|that|this) parts?", r"partly",
    r"if.{0,250}?(?:conflict|inconsisten|contrary|otherwise|construed|consider)",
    r"no longer (?:be )?(?:good |valid |binding |viable |controlling )?(?:law|precedent|authority|good law|"
    r"followed|relied (?:up)?on|valid|viable|binding|controlling|regarded|considered|accepted|reflective)\w* "
    r"(?!as (?:stating |expressing |declaring |an )?(?:the )?(?:present |correct )?(?:law|authority|authoritative|"
    r"controlling|good law|binding|precedent)(?: of (?:this|the) (?:state|jurisdiction|circuit|commonwealth))?"
    r"(?:[.,;]|$| to the contrary))(?:for|as|on|under|with|regarding|in (?!light|view))",
    r"partially", r"pro tanto",
    r"in (?:some|certain|several|many|these|those|this|that|one|any|such|other|all other|some other|its|their) "
    r"(?:respects?|regards?|particulars?|instances?)",
    r"in respect (?:of|to)", r"with (?:respect|regard|reference) to", r"in regard to", r"as regards", r"as respects",
    r"respecting", r"regarding", r"concerning", r"relating to", r"in relation to", r"as to",
    r"(?:on|upon|in|at) (?:this|that|the|these|those|such|said|its|their|one|a|any|which|the latter|the former|"
    r"the same|the first|the second|the last) (?:\w+ )?(?:points?|issues?|questions?|propositions?|grounds?|"
    r"subjects?|matters?|aspects?|branch|head|feature|score)",
    r"other grounds?", r"another ground", r"different grounds?", r"other points?", r"other issues?",
    r"in the (?:field|area|context|domain|sphere|realm) of", r"in cases (?:of|involving|where|in which|like)",
    r"for (?:the )?(?:type|types|purposes?|kind|sort|class) of", r"for (?:that|this|the) purpose",
    r"where(?:in|ever)? (?:it|they|the same|such|so|inconsistent|in conflict|contrary|conflicting|they conflict)",
    r"wherein", r"as (?:it|they) conflicts?", r"in so (?:far|much)", r"(?<=, )on [a-z]+ing",
    r"as applied", r"so much of", r"except", r"excepting", r"save as", r"save that", r"but only", r"only (?:as|in|on|"
    r"for|with|so|to|insofar|where|when|because)", r"solely", r"to (?:the|that|this|such|the same|a|some) degree",
    r"modif\w*", r"qualif\w*", r"limited(?! liability)", r"limit (?:it|them|that case|those cases|\w+) to",
    r"restrict\w*", r"clarif\w*", r"narrow\w*", r"confin\w*", r"in whole or in part", r"wholly or",
])
# (b) the thing acted on is a part of the case, not the case. ALWAYS_PART: quantifiers and parts that are partial
# wherever they stand. PART_NOUN: partial when attached to a case ("the language in X", "the rule of X", "X's
# holding", "its reasoning") or when it is itself what the act verb acts on ("the statement is disapproved",
# "we overrule the holding"); a noun that is this court's own ("our holding today", "the rule we adopt") is not.
ALWAYS_PART = rx([
    r"anything", r"whatever", r"aught", r"so much", r"portions?", r"parts? (?:[ivx0-9]+ )?of", r"that part",
    r"those parts", r"part [ivx0-9]+", r"divisions? (?:[ivx0-9]+|one|two|three|four|five|six)", r"(?:first|second|"
    r"third|fourth|fifth|sixth|seventh|eighth) division", r"dict(?:um|a)",
    r"intimations?", r"insinuations?", r"implications?", r"syllabus", r"syllabi", r"head-?notes?", r"footnotes?",
    r"paragraphs?", r"syl\.", r"¶", r"\d+,? \((?:\d{1,2}|[a-z])\)", r"supra,? \((?:\d{1,2}|[a-z])\)",
    r"such of (?:them|those|these|the)", r"what\W{1,3}(?:was|is|has been|we)\W+(?:said|stated|held|wrote)",
    r"(?:first|second|third|fourth|last|final|\w+) sentences? of", r"notes? \d+", r"\d+ n\. ?\d+", r"nn?\. \d+",
    r"remain\w* of", r"what little", r"omissions?", r"intent", r"premises?",
    r"(?:used|uses|employed|employs|contains?|containing) (?:\w+ ){0,2}(?:language|statements?|expressions?|dicta|"
    r"dictum|words?|phrases?)",
    r"any (?:\w+ )?(?:holdings?|statements?|language|expressions?|suggestions?|implications?|intimations?|dicta|"
    r"dictum|comments?|remarks?|observations?|pronouncements?|reasoning|rules?|views?|conclusions?|"
    r"interpretations?|constructions?|inferences?|indications?|references?|readings?|rulings?|findings?|intent|"
    r"premises?|distinctions?)",
    r"(?:its|their) (?:\w+ )?(?:holdings?|statements?|language|reasoning|rationale|analysis|rules?|tests?|"
    r"standards?|conclusions?|views?|interpretations?|constructions?|approach|dicta|dictum|discussion|rulings?)",
])
PART_NOUN = (r"(?:language|langauge|statements?|distinctions?|expressions?|suggestions?|observations?|remarks?|comments?|pronouncements?|"
             r"passages?|holdings?|rules?|rulings?|reasoning|rationale|analysis|tests?|standards?|doctrines?|"
             r"principles?|interpretations?|constructions?|views?|conclusions?|approach(?:es)?|formulations?|"
             r"requirements?|discussions?|concepts?|theory|theories|definitions?|points?|propositions?|ideas?|"
             r"notions?|characteri[sz]ations?|criteria|criterion|presumptions?|inferences?|indications?|"
             r"declarations?|words?|phrases?|phrasing|methodology|framework|exceptions?|determinations?|aspects?|"
             r"enunciations?|references?|readings?|findings?|writing|reliance|endorsement|adoption|recognition|"
             r"application|treatment|extension)(?![a-z])")
# a case reference after an attaching preposition (a citation, "v.", supra, ex parte, in re, "case", "decision")
CASE_MARK = re.compile(r"(?<![a-z])(?:v\.|vs\.|supra|ex parte|in re|matter of|case|cases|decision|decisions|opinion|"
                       r"opinions)(?![a-z])|\d+ [a-z][a-z.\s]{0,20}\d* \d+")
PART_ATTACH = re.compile(r"(?<![a-z])" + PART_NOUN + r"(?![a-z])[,\"']*(?: [a-z,\"'\-]+){0,7}? (?:in|of|from|contained in|"
                         r"expressed in|announced in|set forth in|stated in|made in|found in|appearing in|"
                         r"adopted in|laid down in|enunciated in|established in|declared in|articulated in|"
                         r"followed in|applied in|by)(?![a-z])")
PART_POSS = re.compile(r"(?:'s|s') (?:[a-z\-]+ ){0,2}" + PART_NOUN + r"(?![a-z])")
PART_ACTED = re.compile(r"(?:(?<![a-z])" + PART_NOUN + r"(?![a-z])(?:,? [a-z]+){0,3},? (?:is|are|be)(?:,? [a-z]+)"
                        r"{0,3},? (?:overruled|disapproved|abrogated|receded from|repudiated|disavowed|no longer)|"
                        r"(?:overrule|disapprove|disapprove of|recede from|abrogate|repudiate|disavow|overturn|"
                        r"reject)(?: (?:the|that|this|those|these|such|our|any|all|its|their|prior|earlier|former|"
                        r"previous|contrary|above|[a-z]+ed|[a-z\-]+)){0,3} " + PART_NOUN + r"(?![a-z]))")
# this court's own holding / rule / view in this case: not a part of the case acted on
_NOT_ATT = r"(?!(?: [a-z,\"'\-]+){0,7}? (?:in|of|from|contained in|expressed in|announced in|by) )"
OWN = re.compile(r"(?:our|this court's|the court's|today's|our present|the present) (?:\w+ )?" + PART_NOUN +
                 r" (?:today|here|herein|now|in this case|in this opinion|announced today|we announce|we adopt|"
                 r"we reach)" + _NOT_ATT +
                 r"|(?:our|this court's|today's) (?:\w+ )?" + PART_NOUN + r"(?=[,.;]| we | today)"
                 r"|" + PART_NOUN + r" (?:we|which we|that we) (?:now |today |here )?(?:announce|adopt|reach|apply|"
                 r"hold|state|set|establish|follow|make|express)\w*(?![a-z])" + _NOT_ATT +
                 r"|" + PART_NOUN + r" (?:here|herein|today|now|hereinbefore|heretofore|above|hereinabove)"
                 r"(?: [a-z]+)? (?:announced|stated|adopted|declared|set forth|expressed|laid down|reached|made)" +
                 _NOT_ATT +
                 r"|(?:this|the present|the foregoing|the above|today's|our present) (?:[a-z\-]+ )?" + PART_NOUN +
                 _NOT_ATT + r"|in (?:light|view) of|in support of|in accordance with|(?:by|in) so holding|"
                 r"in holding")
# "the opinion holding to the contrary in X": a participle, not the noun "holding"
PARTICIPLE = re.compile(r"(?<!the )(?<!its )(?<!their )(?<!any )(?<!our )(?<!this )(?<!that )(?<!such )(?<!'s )"
                        r"(?<!a )(?<!s' )(?<!prior )(?<!earlier )(?<!contrary )(?<!former )holding(?= (?:to the contrary|"
                        r"contrary|otherwise|that|the contrary|to a contrary|inconsistent|a contrary))")


# generic attachment: "the <words> of / in <the target>" where none of the words names a whole case
GEN_ATTACH = re.compile(r"(?<![a-z])(?:the|that|this|those|these|such|said|our|its|their|his|a|an)((?: [a-z\-/']+){1,4}?) "
                        r"(?:of|in|from)(?= )")
WHOLE_NOUNS = set("""case cases decision decisions opinion opinions judgment judgments line progeny precedent
    precedents authority authorities court courts caselaw case-law law appeals district circuit division's""".split())


def _x(m):
    return re.sub(r"[a-z]", "x", m.group(0))


def part_object(s, evpos):
    """The partial-object phrase of s, or None. This court's own holding / rule / view / conclusion (OWN) is masked
    first ('consistent with our holding today, we overrule X' acts on X itself); masking keeps word counts."""
    m = ALWAYS_PART.search(s)
    if m:
        return m.group(0)
    t = PARTICIPLE.sub("xxxxxxx", s)
    t = OWN.sub(_x, t)
    for m in PART_ATTACH.finditer(t):
        e = m.end()
        if any(e <= p < e + 250 for p in evpos) or CASE_MARK.search(t[e:e + 150]):
            return m.group(0)
    for m in PART_POSS.finditer(t):
        if any(m.start() - 80 <= p < m.start() for p in evpos):
            return m.group(0)
    m = PART_ACTED.search(t)
    if m:
        return m.group(0)
    for m in GEN_ATTACH.finditer(t):
        words = m.group(1).split()
        e = m.end()
        if not any(w.strip("'") in WHOLE_NOUNS for w in words) and any(e <= p < e + 120 for p in evpos):
            return "generic:" + m.group(0).strip()
    return None
# act forms: a present act of this court on a case (passive: the case is the subject; active: the case is the object)
VERB_P = r"(?:overruled|disapproved|abrogated|receded from|repudiated|disavowed|overturned|abandoned|discarded)"
VERB_A = r"(?:overrule|overrules|disapprove|disapproves|recede from|recedes from|abrogate|abrogates|repudiate|" \
         r"repudiates|disavow|disavows|overturn|overturns)"
PASSIVE = re.compile(r"(?<![a-z])(?:is|are|be|stands?|now stands?|being)(?:,? (?:[a-z]+(?:ly)?|[a-z]+,|and|it|they|"
                     r"is|are|be|hereby|now|therefore|accordingly|thus|also|herewith|necessarily|must|should|"
                     r"ought|to be|will|shall|deemed|considered|held|declared|regarded as|treated as|taken as)){0,5},? "
                     + VERB_P + r"(?![a-z])")
ACTIVE = re.compile(r"(?<![a-z])(?:we|court)(?:,? (?:[a-z]+ly|hereby|now|therefore|accordingly|thus|also|further|"
                    r"do|must|today|herewith|here|again|now|and|,|so|necessarily|likewise)){0,4},? " + VERB_A +
                    r"(?![a-z])")
WHOLE = re.compile(r"(?<![a-z])(?:is|are|should|must|will|shall|can)(?:,? (?:[a-z]+ly|thus|therefore|now|hence|"
                   r"accordingly|also),?)* (?:no longer (?:good )?law|no longer (?:be )?authorit\w*|no longer the law|"
                   r"no longer (?:to )?be followed|no longer be relied (?:up)?on|not to be followed|overthrown|"
                   r"no longer (?:be )?(?:regarded|considered|accepted) as (?:stating |expressing |an )?(?:the )?"
                   r"(?:present |correct )?(?:law|authority|authoritative|controlling|good law|binding)|"
                   r"wrongly decided and (?:is|are) overruled)(?![a-z])")
# after the verb, a list of the cases acted on: "are overruled, including X"; "are overruled: X; Y"; "[e.g., X]"
LIST_AFTER = re.compile(r"^(?:[ ,]*(?:hereby|expressly|specifically|therefore|now|accordingly))*\s*(?::|,? including|"
                        r",? inclusive of|,? namely|,? to wit|,? viz\.?|,? such as|,? e\. ?g\.,?|\[e\. ?g\.,?|"
                        r"\(e\. ?g\.,?|,? for example|,? among them)")
# reports, conditions, refusals, questions, other speakers: not this court's present act
HEDGE = rx([
    r"has been", r"have been", r"had been", r"was overruled", r"were overruled", r"was disapproved",
    r"were disapproved", r"was abrogated", r"were abrogated", r"was repudiated", r"were repudiated",
    r"overruled by", r"disapproved by", r"abrogated by", r"receded from by", r"repudiated by", r"overruled in",
    r"disapproved in", r"abrogated in", r"since overruled", r"later overruled", r"subsequently overruled",
    r"impliedly", r"implicitly", r"sub silentio", r"in effect", r"effectively", r"virtually", r"necessarily overruled",
    r"not", r"n't", r"never", r"no reason", r"no need", r"nor", r"neither", r"decline\w*", r"refus\w*",
    r"reluctan\w*", r"would", r"could", r"might", r"may(?! \d)", r"if", r"whether", r"unless", r"urg\w+", r"asks?",
    r"asked", r"argu\w*", r"contend\w*", r"invit\w*", r"request\w*", r"dissent\w*", r"concur\w*",
    r"appellants? (?:asks?|urges?|argues?|contends?)", r"counsel", r"should be (?:\w+ )?overruled(?!,? and)",
    r"seem\w*", r"appears?", r"perhaps", r"doubt\w*", r"question\w*", r"apparently", r"it is said",
    r"recommend\w*", r"suggest\w*",
])
# the thing acted on is a pronoun or a description ("they are overruled", "those cases"): the case is named elsewhere
ANAPHOR_SUBJ = re.compile(r"(?<![a-z])(?<!as )(?:it|they|them|those|these|such|same|that|said|both|each|"
                          r"former|latter|foregoing|cited)(?:,? (?:[a-z]+ly|are|is|hereby|be|must|should|and|now|"
                          r"therefore|cases?|decisions?|opinions?|authorities|holdings?)){0,3},? " + VERB_P +
                          r"(?![a-z])")
ANAPHOR_OBJ = re.compile(r"(?<![a-z])" + VERB_A + r",? (?:it|them|that|those|these|such|said|all|both|each|the "
                         r"(?:former|latter|above|foregoing|cited|earlier|prior)|any)(?![a-z])")


def norm(s):
    s = RC.dehyphen_norm(R.ascii_lower(s))
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[^\x00-\x7f¶§]", " ", s)
    s = re.sub(r"(?<=[a-z])-(?=(?:in|of) )", " ", s)
    return re.sub(r"\s+", " ", s)


def ev_positions(ev, s):
    """Character positions in the normalised sentence s where the row's evidence stands (empty: not there)."""
    if ev.startswith("cite:"):
        key = ev[5:]
        out = []
        # cite keys are matched on the compact form, then mapped back by a tolerant pattern
        want = R.alnum(key)
        parts = key.split(" ")
        if len(parts) != 3:
            return out
        vol, rep, page = parts
        pat = r"(?<!\d)" + re.escape(vol) + r"\s*" + r"[\s.,']*".join(re.escape(c) for c in rep) + r"[\s.,']*" + \
              re.escape(page) + r"(?!\d)"
        for m in re.finditer(pat, s):
            if R.alnum(m.group(0)) == want:
                out.append(m.start())
        return out
    if ev.startswith("name:"):
        toks = [R.alnum(x) for x in ev[5:].split(" ")]
        toks = [x for x in toks if len(x) >= 3]
        if not toks:
            return []
        pos = []
        for t in toks:
            ps = [m.start() for m in re.finditer(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", s)]
            if not ps:
                return []
            pos.append(ps)
        return sorted(set(pos[0]))
    return []


def clause_bounds(s, i):
    """The clause of s that holds position i: from the previous ';' / ':' (or the start) to the next one (or the
    end). Semicolons inside a citation list ("123 So.2d 45 (1987); Bonham v. ...") also cut, which only narrows."""
    a = max(s.rfind(";", 0, i), s.rfind(":", 0, i)) + 1
    b = [x for x in (s.find(";", i), s.find(":", i)) if x >= 0]
    return a, (min(b) if b else len(s))


def object_zone_hit(s, evpos):
    """Is some evidence position in the object zone of an act form of the sentence? Passive: between the clause
    start and the verb phrase, or in a list that the verb introduces ("are overruled, including X", "are
    overruled: X; Y"); active: from the verb to the clause end, or to the sentence end when the verb's object is a
    list ("we overrule the following cases: X; Y"). -> (hit, which act form)."""
    acts = []
    for m in PASSIVE.finditer(s):
        acts.append(("passive", m.start(), m.end()))
    for m in WHOLE.finditer(s):
        acts.append(("passive", m.start(), m.end()))
    for m in ACTIVE.finditer(s):
        acts.append(("active", m.start(), m.end()))
    if not acts:
        return False, "noAct"
    for kind, a, b in acts:
        for p in evpos:
            if kind == "passive":
                c0, _ = clause_bounds(s, a)
                if c0 <= p < a:
                    return True, kind
                if p >= b and LIST_AFTER.match(s[b:b + 40]):
                    return True, kind + "List"
            else:
                _, c1 = clause_bounds(s, b)
                if b <= p < c1:
                    return True, kind
                if p >= b and re.search(r"(?:following|these|those|all|any|our|other|prior) (?:\w+ ){0,3}"
                                        r"(?:cases?|decisions?|opinions?|authorit\w+|precedents?|case ?law)[^;]{0,80}"
                                        r"(?::|including|inclusive of|namely|e\. ?g\.)", s[b:c1 + 1]):
                    return True, kind + "List"
    return False, "notObject"


# words that put a case in the sentence as authority for the act, not as what is acted on
AUTH = re.compile(r"(?<![a-z])(?:with|under|following|follow|see|cf\.?|accord|by|than|unlike|like|after|since|"
                  r"from|per|in light of|in view of|relying on|relied on|pursuant to|based on|consistent with|"
                  r"contrary to|in accordance with|approve|approved|approving|adopt|adopted|reaffirm|reaffirmed|"
                  r"affirm|affirmed|followed|applying|applied|citing|quoting|explained in|recognized in|"
                  r"announced in|we said in|we held in)(?![a-z])")


def name_chunk(s, p, ev):
    """The stretch of s that names the case at evidence position p: for a citation, the comma-separated piece
    before it (the case name); for a name token, the piece that holds it. Pieces end at ',', '(', ';', ':'."""
    s = re.sub(VERB_A + r"(?: of)?", _x, s)
    if ev.startswith("cite:"):
        q = p
        while q > 0 and s[q - 1] in " ,":
            q -= 1
        a = max(s.rfind(c, 0, q) for c in ",(;:") + 1
        return s[a:q]
    a = max(s.rfind(c, 0, p) for c in ",(;:") + 1
    return s[a:p + 1]


def case_refs(s):
    """How many case references s holds: citations, 'v.' captions, 'supra', 'ex parte' / 'in re' (rough)."""
    return len(RC.CITE_RX.findall(s)) + len(re.findall(r"(?<![a-z])(?:v\.|vs\.|supra|ex parte|in re)(?![a-z])", s))


def judge(sent, ev, kind, cut=0):
    """(verdict, reason) for one sentence. verdict: 'partial' (a limiting phrase / a part of the case is acted on),
    'whole' (a present act on the named case itself), 'keep' (the rule says nothing)."""
    s = norm(sent)
    m = LIMIT.search(s)
    if m:
        return "partial", "limit:" + m.group(0)
    evpos = ev_positions(ev, s)
    po = part_object(s, evpos)
    if po:
        return "partial", "partObject:" + po
    if not evpos:
        return "keep", "targetNotInSentence"
    if cut:
        return "keep", "sentenceUnbounded"
    m = HEDGE.search(s)
    if m:
        return "keep", "hedge:" + m.group(0)
    hit, how = object_zone_hit(s, evpos)
    if not hit:
        return "keep", how
    if (ANAPHOR_SUBJ.search(s) or ANAPHOR_OBJ.search(s)) and case_refs(sent) > 2:
        return "keep", "anaphor"
    if all(AUTH.search(name_chunk(s, p, ev)) for p in evpos):
        return "keep", "citedAsAuthority"
    return "whole", how


def witness_class(quote, sent):
    s = norm(quote + " " + sent)
    if re.search(r"overruled,? (?:in part|on other grounds?|on another ground|in other respects?|partially|"
                 r"to the extent|insofar)", s) or re.search(r"(?:abrogated|disapproved|receded from),? (?:in part|"
                                                           r"on other grounds?|to the extent)", s):
        return "partialPhrase"
    if re.search(r"(?:overruled|abrogated|disapproved|receded from) by", s):
        return "plainBy"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.path.join(C2, "round6", "history", "stage", "final2"))
    ap.add_argument("--sentences", default=os.path.join(HERE, "sentences.jsonl.gz"))
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    sent = {}
    with gzip.open(a.sentences, "rt", encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            sent[o["id"]] = o
    base_lines = {}
    with open(os.path.join(a.base, "treatments.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            line = line.rstrip("\n")
            if line:
                p = line.split("\t")
                if p[0] in sent:
                    base_lines[p[0]] = p
    hold = Counter()
    hold_issue = {}
    targets = {int(p[2]) for p in base_lines.values()}
    with open(os.path.join(a.base, "holdings.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.split("\t", 3)
            if len(p) >= 3 and p[1].lstrip("-").isdigit() and int(p[1]) in targets:
                hold[int(p[1])] += 1
                hold_issue[int(p[1])] = p[2]

    counts = Counter()
    dec = []
    rep = []
    for i, p in sorted(base_lines.items()):
        o = sent[i]
        cls, old = o["cls"], p[5]
        if "err" in o:
            counts[(cls, "error:" + o["err"])] += 1
            dec.append((i, cls, old, old, "error:" + o["err"], ""))
            continue
        new, why = old, ""
        if cls == "W":
            why = "witness:" + witness_class(p[11], o["sent"])
            counts[(cls, why + " (scope " + ("issues" if old.startswith("issues:") else old) + ")")] += 1
        elif cls == "P":
            v, why = judge(o["sent"], p[12], p[4], o.get("cut", 0))
            if v == "whole":
                new = "all"
                counts[(cls, "%s->all" % old)] += 1
            elif v == "partial":
                if old == "unknown":
                    new = "partialUnknown"
                    counts[(cls, "unknown->partialUnknown")] += 1
                else:
                    counts[(cls, "keep partial: " + why.split(":")[0])] += 1
            else:
                counts[(cls, "keep (rule silent): " + why.split(":")[0])] += 1
        elif cls == "I":
            ks = old[len("issues:"):].split(",")
            t = int(p[2])
            narrow = len(ks) == 1 and hold[t] == 1
            v, why = judge(o["sent"], p[12], p[4], o.get("cut", 0))
            if narrow:
                same = hold_issue.get(t) == ks[0]
                tag = "oneIssueOneHolding(%s)" % ("sameIssue" if same else "otherIssue")
                if v == "whole":
                    new = "all"
                    counts[(cls, tag + " ->all")] += 1
                else:
                    counts[(cls, tag + " kept: " + v)] += 1
            else:
                counts[(cls, "not narrow (%s)" % ("one issue, target holdings %d" % hold[t] if len(ks) == 1 else
                                                  "%d issues" % len(ks)) if hold[t] <= 1 or len(ks) > 1 else
                        "not narrow (one issue, target holdings >1)")] += 1
                counts[(cls, "  (sentence verdict if it were P: %s)" % v)] += 1
        dec.append((i, cls, old, new, why, o.get("sent", "")))
        if new != old:
            q = list(p)
            q[5] = new
            rep.append(q)

    R.write_rows(os.path.join(a.out, "replace.tsv"), rep)
    R.write_rows(os.path.join(a.out, "decisions.tsv"),
                 [("id", "class", "old_scope", "new_scope", "reason", "sentence")] + dec)
    R.write_rows(os.path.join(a.out, "counts.tsv"), [(c, k, n) for (c, k), n in sorted(counts.items())])
    for (c, k), n in sorted(counts.items()):
        print("%s\t%-60s\t%d" % (c, k, n))
    print("replace rows:", len(rep))
    rnd = random.Random(a.seed)
    ch = [d for d in dec if d[2] != d[3]]
    smp = rnd.sample(ch, min(40, len(ch)))
    kept = [d for d in dec if d[1] == "P" and d[2] == d[3] and d[4].split(":")[0] in ("limit", "partObject")]
    ctl = random.Random(a.seed + 1).sample(kept, min(40, len(kept)))
    R.write_rows(os.path.join(a.out, "control_partial40.tsv"), [(d[0], d[4]) for d in ctl])
    R.write_rows(os.path.join(a.out, "sample40.tsv"),
                 [("id", "class", "old_scope", "new_scope", "reason", "quote", "sentence")] +
                 [(d[0], d[1], d[2], d[3], d[4], base_lines[d[0]][11], d[5]) for d in smp])


if __name__ == "__main__":
    main()
