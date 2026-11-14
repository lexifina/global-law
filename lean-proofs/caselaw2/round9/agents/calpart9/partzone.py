"""calpart9: part zones of a decision text (DESIGN9 section 4) from the reader's part map with rule PJ (partfix.py).

    zones(text) -> (zones, info)
      zones: [(z_start, z_end, part)] covering [0, len(text)), non-overlapping, sorted, adjacent zones of the same
             part merged; part in majority | plurality | perCuriam | concurrence | dissent | headmatter | other
      info:  {"hw": 0|1, "pj": [changes of rule PJ], "pm_old": old part map, "pm_new": fixed part map}

Part map = common.part_map2 for every text (the treatments reader's map since round 2: scan2 sets
scan.part_map = part_map2; its BAD_SEP test drops citation lines such as "Irey, 563 F.3d at 1227 (Hill, J.,
concurring)." that part_map reads as a separate-opinion start), then partfix.fix_parts (rule PJ). With PZ_PM=r6 the
map is r6scan.scan_text's choice (part_map2 for hard-wrapped texts, else part_map) -- for comparison only. Reader part names map to zone parts:
  majority, majority~, majority?        -> majority
  perCuriam                             -> perCuriam
  plurality                             -> plurality
  concurrence, concurrence~             -> concurrence
  dissent, dissent~                     -> dissent
  headmatter, headmatter~               -> headmatter
  front, title, unknown (other heading) -> other
Offsets are characters of the git-HEAD text (UTF-8, CRLF -> LF), the offset space of the rows' start / end.
No answer-key file is read.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, HERE)
import r6lib as L  # noqa: E402
import partfix as PF  # noqa: E402

C = L.reader_common()
NL = chr(10)
ZPART = {"majority": "majority", "majority~": "majority", "majority?": "majority", "perCuriam": "perCuriam",
         "plurality": "plurality", "concurrence": "concurrence", "concurrence~": "concurrence", "dissent": "dissent",
         "dissent~": "dissent", "headmatter": "headmatter", "headmatter~": "headmatter"}


def body_start(text):
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            return nl + 1 if nl >= 0 else len(text)
    return 0


MODE = {"pm": os.environ.get("PZ_PM", "pm2")}  # pm2: part_map2 for every text; r6: r6scan's choice (pm1 unless hw)


def part_maps(text):
    hw = C.hard_wrapped(text, body_start(text))
    if MODE["pm"] == "r6":
        pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    else:
        pm, _ = C.part_map2(text)
    new, ch = PF.fix_parts(text, pm)
    return hw, pm, new, ch


def to_zones(pm, n):
    out = []
    for a, b, p, _s in pm:
        if b <= a:
            continue
        zp = ZPART.get(p, "other")
        if out and out[-1][2] == zp and out[-1][1] == a:
            out[-1] = (out[-1][0], b, zp)
        else:
            out.append((a, b, zp))
    # sanity: cover [0, n) without overlap
    pos = 0
    fixed = []
    for a, b, zp in out:
        if a > pos:
            fixed.append((pos, a, "other"))
        a = max(a, pos)
        if b > a:
            fixed.append((a, b, zp))
            pos = b
    if pos < n:
        fixed.append((pos, n, "other"))
    merged = []
    for a, b, zp in fixed:
        if merged and merged[-1][2] == zp and merged[-1][1] == a:
            merged[-1] = (merged[-1][0], b, zp)
        else:
            merged.append((a, b, zp))
    return merged


def zones(text):
    hw, pm, new, ch = part_maps(text)
    return to_zones(new, len(text)), {"hw": int(hw), "pj": ch, "pm_old": pm, "pm_new": new}


def zone_at(zs, s, e):
    """The zone containing [s, e) or None."""
    for a, b, p in zs:
        if a <= s and e <= b:
            return (a, b, p)
    return None
