"""Candidate Horty families over SCOTUS decision holdings: keyword pre-filter (recall-oriented); the LLM confirms."""
import re, sys, os, json, collections
FAM = {
 "fourth_search": r"fourth amendment|unreasonable search|warrantless|probable cause to search|search and seizure|exclusionary rule|reasonable expectation of privacy",
 "qualified_immunity": r"qualified immunity|clearly established",
 "personal_jurisdiction": r"personal jurisdiction|minimum contacts|purposeful(ly)? avail|long-arm",
 "standing": r"\bstanding\b|injury in fact|case or controversy|redressab",
 "miranda": r"miranda|custodial interrogation|in custody|self-incrimination|voluntar\w+ (of the )?confession|coerced confession",
 "agency_deference": r"chevron|skidmore|deference to (the )?agency|agency'?s interpretation|auer|seminole rock",
 "dormant_commerce": r"dormant commerce|negative commerce|burden(s)? (on )?interstate commerce|discriminat\w+ against interstate commerce|state tax\w* .*interstate",
 "takings": r"takings? clause|taking of (private )?property|just compensation|regulatory taking|inverse condemnation|taken for public use|physical (invasion|occupation)",
 "due_process_procedural": r"procedural due process|notice and (an )?opportunity|hearing before|property interest|liberty interest",
 "equal_protection": r"equal protection|strict scrutiny|rational basis|suspect class|intermediate scrutiny",
 "free_speech": r"first amendment|free speech|freedom of speech|public forum|content-based|prior restraint",
 "establishment_free_exercise": r"establishment clause|free exercise",
 "double_jeopardy": r"double jeopardy",
 "confrontation": r"confrontation clause|testimonial",
 "ineffective_assistance": r"ineffective assistance|strickland",
 "sovereign_immunity": r"eleventh amendment|sovereign immunity|abrogat\w+ .*immunity",
 "preemption": r"preempt|pre-empt|supremacy clause",
 "habeas_procedural": r"habeas|procedural default|aedpa|exhaust\w+ state",
 "jury_trial": r"right to (a )?jury|sixth amendment.*jury|seventh amendment",
 "cruel_unusual": r"eighth amendment|cruel and unusual|death penalty|capital sentenc",
 "contract_clause": r"contract clause|impair\w* the obligation",
 "federal_question_removal": r"removal|federal question jurisdiction|diversity jurisdiction|arising under",
 "commerce_power": r"commerce clause|power to regulate commerce",
 "state_action_1983": r"under color of|state action|section 1983|§ ?1983",
}
P = {k: re.compile(v, re.I) for k, v in FAM.items()}
def main(path):
    dec = collections.defaultdict(set); hol = collections.Counter()
    for line in open(path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        txt = f[3] + " " + f[11]
        for k, p in P.items():
            if p.search(txt):
                dec[k].add(f[1]); hol[k] += 1
    for k in sorted(dec, key=lambda k: -len(dec[k])):
        print(k, len(dec[k]), hol[k])
if __name__ == "__main__":
    main(sys.argv[1])
