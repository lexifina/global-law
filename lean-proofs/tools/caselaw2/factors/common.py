import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "holdings"))
import llm  # noqa: E402
W = os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/data")
WORK = os.path.join(W, "factors_work")
llm.USAGE_LOG = os.path.join(WORK, "usage.jsonl")
FAMILIES = {  # family -> (index for factor ids, short scope note for the models)
 "fourth_search": (1, "Fourth Amendment: whether a search or seizure was unreasonable / evidence must be suppressed"),
 "qualified_immunity": (2, "qualified immunity of officials: whether the official is denied immunity (right clearly established and violated)"),
 "personal_jurisdiction": (3, "personal jurisdiction over a defendant consistent with due process (contacts, purposeful availment, fairness)"),
 "standing": (4, "Article III / prudential standing of the party invoking federal jurisdiction"),
 "miranda": (5, "Miranda / Fifth Amendment self-incrimination and voluntariness: whether a statement must be excluded (custody, interrogation, warnings, waiver, coercion)"),
 "agency_deference": (6, "judicial deference to an agency's interpretation (Chevron, Skidmore, Auer): whether the agency's reading prevails"),
 "dormant_commerce": (7, "dormant Commerce Clause: whether a state law or tax unconstitutionally discriminates against or burdens interstate commerce"),
 "takings": (8, "Takings Clause: whether government action is a taking requiring just compensation"),
 "due_process_procedural": (9, "procedural due process: whether the procedures given before a deprivation of life, liberty or property were constitutionally inadequate"),
 "free_speech": (10, "First Amendment free speech/press: whether a government restriction on expression is unconstitutional"),
 "establishment_free_exercise": (11, "Religion Clauses: whether government action violates the Establishment or Free Exercise Clause"),
 "confrontation": (12, "Confrontation Clause: whether admitting out-of-court statements violated the defendant's confrontation right"),
 "ineffective_assistance": (13, "Sixth Amendment ineffective assistance of counsel (Strickland deficiency and prejudice): whether the defendant gets relief"),
 "preemption": (14, "federal preemption: whether federal law preempts the state law or claim"),
 "cruel_unusual": (15, "Eighth Amendment cruel and unusual punishment: whether the punishment or condition is unconstitutional"),
}
