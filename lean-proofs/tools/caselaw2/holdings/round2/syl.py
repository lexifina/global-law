"""Where the opinion of the Court starts in a slip-opinion text that carries the syllabus (CourtListener Combined)."""
import re
DELIV = re.compile(r"(?m)^[ \t]*(?:(?:CHIEF |Chief )?(?:JUSTICE|Justice) [A-Z][A-Za-z’'\- ]+ delivered the opinion of the Court|PER CURIAM\.?[ \t]*$|Per Curiam\.?[ \t]*$)")
SYL = re.compile(r"(?m)^[ \t]*Syllabus[ \t]*$|constitutes no part of the opinion of the Court")


def opinion_start(t, b, e):
    """offset in t[b:e] where the Court's opinion starts, b if the part has no syllabus, None if a syllabus is
    present but the start of the opinion is not found."""
    if not SYL.search(t, b, min(e, b + 6000)):
        return b
    ms = list(DELIV.finditer(t, b, e))
    if not ms:
        return None
    return ms[0].start()


def court_parts2(t):
    """core.court_parts, with the syllabus of a slip opinion removed: where a part carries a syllabus, the part
    starts at the 'JUSTICE X delivered the opinion of the Court' line (or PER CURIAM) found in the whole section and
    ends at the first separate opinion after it. A part whose opinion start is not found is dropped."""
    import core
    parts, form = core.court_parts(t)
    secs = core.sections(t)
    out = []
    for b, e, part in parts:
        o = opinion_start(t, b, e)
        if o == b:
            out.append((b, e, part))
            continue
        full_e = next((se for (_, sb, se) in secs if sb == b), e)
        ms = list(DELIV.finditer(t, b, full_e))
        if not ms:
            continue
        o = ms[0].start()
        m = core.SEPARATE.search(t, o + 300, full_e)
        out.append((o, m.start() if m else full_e, part))
    return out, form
