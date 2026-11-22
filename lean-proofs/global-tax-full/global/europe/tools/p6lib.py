# pass 6 helpers (R1 Europe, 2026-11-21): exec'd at the end of tools/specs/<CC>_<Fam>.py after `S` exists.
# Each helper replaces the grade-C stub entries of one OECD code by a modelled entry, a cited absence or a dated note,
# writes the Lean (names prefixed `p6`), the family, the guards (figures recomputed here in Python) and the summary entry.
import json as _json

_CTOR = {"4100": "propertyRecurrent", "4200": "wealth", "4300": "estate", "4400": "transactions"}


def _q(s):
    return _json.dumps(s, ensure_ascii=False)


def _drop(S, oecd):
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == oecd and t.get("grade") == "C")]
    S["unsupported"] = [u for u in S["unsupported"]
                        if not (u[1].startswith(oecd + " ") or f"({oecd})" in u[1] or u[1].startswith(oecd + ":"))]
    S.setdefault("families", [])
    S.setdefault("notes", [])
    S.setdefault("guards", [])
    S["lean"] = S.get("lean") or ""


def _doc(S, title, src, quotes):
    S["doc"] += f"\n\n## {title} (pass 6)\nSource: {src}.\n" + "".join(f"* {x}\n" for x in quotes)


def _sch(b):
    return f"Schedule.flat {b[0][1]}" if len(b) == 1 and b[0][0] == 0 else "Schedule.ofList [" + ", ".join(f"({a}, {c})" for a, c in b) + "]"


def _ticks(bands, x):
    t = 0
    for i, (lo, r) in enumerate(bands):
        hi = bands[i + 1][0] if i + 1 < len(bands) else None
        if x > lo:
            t += r * ((min(x, hi) if hi is not None else x) - lo)
    return t


def _tax(bands, x):
    return _ticks(bands, max(x, 0)) // 10000


def p6_absent(S, oecd, tax, statute, why, dated, grade="B", src=None):
    """A cited absence (status absent; table shows '-')."""
    _drop(S, oecd)
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == oecd and t.get("status") == "absent")]
    S["taxes"].append({"oecd": oecd, "tax": tax, "statute": statute, "dated": dated, "grade": grade, "status": "absent",
                       "kernel_parts": ["Absent"], "unsupported": []})
    S["absent"] = [a for a in S.get("absent", []) if a[0] != _CTOR[oecd]] + [(_CTOR[oecd], why)]
    S["doc"] += f"\n* **{oecd} not levied (cited, pass 6, grade {grade})**: {statute}: {why} ({dated})\n"


def p6_note(S, oecd, tax, statute, note, dated):
    """Stays grade C: rates set only by municipalities (or another sub-national body); the note says where they are."""
    S["taxes"] = [t for t in S["taxes"] if not (str(t.get("oecd")) == oecd and t.get("grade") == "C")] + [
        {"oecd": oecd, "tax": tax, "statute": statute, "dated": dated, "grade": "C", "status": "unsupported", "kernel_parts": [],
         "tried": "pass 6: national law read for the frame only", "unsupported": [note]}]
    S["doc"] += f"\n* **{oecd} {tax} (pass 6 note, grade C)**: {statute}: {note} ({dated})\n"


def p6_transfer(S, key, name, bands, statute, dated, grade, src, quotes, kinds=("home", "realEstate", "land"),
                uns=(), firstCap=None, firstBands=None, additionalBp=None, minimum=None, maximum=None):
    """4400: a TransferDuty on purchases (marginal bands [(from, bp)]); `minimum`/`maximum` = floor/cap in currency units."""
    if maximum:
        return _transfer_capped(S, key, name, bands, statute, dated, grade, src, quotes, kinds, uns, maximum)
    _drop(S, "4400")
    f = [f"name := {_q(name)}", f"sched := {_sch(bands)}", "kinds := [" + ", ".join("." + k for k in kinds) + "]"]
    if firstCap is not None:
        f += [f"firstHomeCap := {firstCap}", f"firstHomeSched := {_sch(firstBands)}"]
    if additionalBp:
        f.append(f"additionalBp := {additionalBp}")
    S["lean"] += f"\n/-- {statute} -/\ndef p6{key} : TransferDuty := {{ " + ", ".join(f) + " }\n"
    run = f"p6{key}.charges g.purchases {_q(statute)}"
    if minimum:
        S["lean"] += (f"def p6{key}Min (p : Purchase) : Int := if p6{key}.kinds.contains p.kind then max {minimum} (p6{key}.amount p) else 0\n"
                      f"def p6{key}Charges (ps : List Purchase) : List Charge :=\n  (ps.zipIdx.filter fun (p, _) => p6{key}.kinds.contains p.kind).map fun (p, i) =>\n"
                      f"    charge .transactions p6{key}.name p.price (fun _ => p6{key}.base p) (fun _ => p6{key}Min p) (event := s!\"purchase {{i + 1}}\") (statute := {_q(statute)})\n")
        run = f"p6{key}Charges g.purchases"
    S["families"].append((f"4400 {name}", [".transactions"], run))
    k = kinds[0]
    for p in (200000, 2000000):
        v = _tax(bands, p)
        if minimum:
            S["guards"].append(f"p6{key}Min {{ kind := .{k}, price := {p} }} == {max(minimum, v)}")
        else:
            S["guards"].append(f"p6{key}.amount {{ kind := .{k}, price := {p} }} == {v}")
    if firstCap is not None:
        S["guards"].append(f"p6{key}.amount {{ kind := .{k}, price := {firstCap}, firstHome := true }} == {_tax(firstBands, firstCap)}")
        S["guards"].append(f"p6{key}.amount {{ kind := .{k}, price := {firstCap + 1}, firstHome := true }} == {_tax(bands, firstCap + 1)}")
    if minimum:
        S["guards"].append(f"p6{key}Min {{ kind := .{k}, price := 1 }} == {minimum}")
    S["guards"].append(f"p6{key}.amount {{ kind := .vehicle, price := 100000 }} == 0")
    S["unsupported"] += [(c, "4400 " + t) for c, t in uns]
    S["notes"].append(f"{S['cc']} 4400 {name}: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "4400", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["TransferDuty"], "unsupported": [t for _, t in uns]})
    _doc(S, f"4400 {name}", src, quotes)


def _transfer_capped(S, key, name, bands, statute, dated, grade, src, quotes, kinds, uns, maximum):
    _drop(S, "4400")
    f = [f"name := {_q(name)}", f"sched := {_sch(bands)}", "kinds := [" + ", ".join("." + k for k in kinds) + "]"]
    S["lean"] += (f"\n/-- {statute} -/\ndef p6{key} : TransferDuty := {{ " + ", ".join(f) + " }\n"
                  f"/-- the duty per purchase, at most {maximum} -/\n"
                  f"def p6{key}Cap (p : Purchase) : Int := min {maximum} (p6{key}.amount p)\n"
                  f"def p6{key}Charges (ps : List Purchase) : List Charge :=\n  (ps.zipIdx.filter fun (p, _) => p6{key}.kinds.contains p.kind).map fun (p, i) =>\n"
                  f"    charge .transactions p6{key}.name p.price (fun _ => p6{key}.base p) (fun _ => p6{key}Cap p) (event := s!\"purchase {{i + 1}}\") (statute := {_q(statute)})\n")
    S["families"].append((f"4400 {name}", [".transactions"], f"p6{key}Charges g.purchases"))
    k = kinds[0]
    # the price at which the cap starts to bind, and either side of it
    top = 10 ** 13
    for p in (200000, 2000000, top):
        S["guards"].append(f"p6{key}Cap {{ kind := .{k}, price := {p} }} == {min(maximum, _tax(bands, p))}")
    S["guards"].append(f"p6{key}Cap {{ kind := .vehicle, price := 100000 }} == 0")
    S["unsupported"] += [(c, "4400 " + t) for c, t in uns]
    S["notes"].append(f"{S['cc']} 4400 {name}: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "4400", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["TransferDuty", "cap (min)"], "unsupported": [t for _, t in uns]})
    _doc(S, f"4400 {name}", src, quotes)


def pwc(cc, name="pwc_indother_wb2025", page="Individual - Other taxes"):
    """Provenance of a PwC Worldwide Tax Summaries capture on disk (B source: facts only, no text copied).
    Pass 7 form: "PwC Worldwide Tax Summaries, <country>, <section>, accessed <date> (<Wayback capture>; file)"."""
    import os
    ts, country = "", cc
    try:
        for l in open(os.path.expanduser(f"cmp20/global/europe/{cc.lower()}/law/ARCHIVE_INDEX.tsv")):
            p = l.rstrip("\n").split("\t")
            if p[0].startswith(name + "."):
                ts = p[3] or p[2][:10]
                if "taxsummaries.pwc.com/" in p[1]:
                    country = p[1].split("taxsummaries.pwc.com/")[1].split("/")[0].replace("-", " ").title().replace(" And ", " and ")
    except OSError:
        pass
    d = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 and ts[:8].isdigit() else ts
    how = f"accessed {d} (Wayback capture" if ts[:2] == "20" and ts[:8].isdigit() else f"accessed {d} (live page"
    return f"PwC Worldwide Tax Summaries, {country}, {page}, {how}; `law/{name}.txt`)"


def p6_property(S, key, name, bands, statute, dated, grade, src, quotes, kinds=("home", "realEstate", "land"),
                ratio=(1, 1), exempt=0, homeBands=None, level="central", uns=(), sample=300000):
    """4100: a PropertyTax on the asset's statutory value (assessed where given, else market value)."""
    _drop(S, "4100")
    f = [f"name := {_q(name)}", f"sched := {_sch(bands)}", "kinds := [" + ", ".join("." + k for k in kinds) + "]"]
    if ratio != (1, 1):
        f += [f"ratioNum := {ratio[0]}", f"ratioDen := {ratio[1]}"]
    if exempt:
        f.append(f"exempt := {exempt}")
    if homeBands is not None:
        f.append(f"homeSched := some ({_sch(homeBands)})")
    S["lean"] += f"\n/-- {statute} -/\ndef p6{key} : PropertyTax := {{ " + ", ".join(f) + " }\n"
    S["families"].append((f"4100 {name}", [".propertyRecurrent"], f"p6{key}.charges g.assets {_q(statute)} (level := .{level})"))
    for k in kinds[:2]:
        for v in (sample, 10 * sample):
            b = max(v * ratio[0] // ratio[1] - exempt, 0)
            bb = homeBands if (k == "home" and homeBands is not None) else bands
            S["guards"].append(f"p6{key}.amount {{ kind := .{k}, value := {v} }} == {_tax(bb, b)}")
    S["guards"].append(f"p6{key}.amount {{ kind := .deposits, value := 100000 }} == 0")
    S["unsupported"] += [(c, "4100 " + t) for c, t in uns]
    S["notes"].append(f"{S['cc']} 4100 {name}: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "4100", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["PropertyTax"], "unsupported": [t for _, t in uns]})
    _doc(S, f"4100 {name}", src, quotes)


_REL = ["spouse", "child", "grandchild", "parent", "sibling", "nieceNephew", "otherRelative", "unrelated", "charity"]


def _cls_lean(c):
    if isinstance(c, dict):
        rows = ", ".join(f"({a}, {b})" for a, b in c["slab"])
        return f"{{ allowance := {c.get('allowance', 0)}, slab := [{rows}], slabTop := {c['top']} }}"
    a, b = c
    return f"{{ allowance := {a}, sched := {_sch(b)} }}"


def _cls_tax(c, v):
    if isinstance(c, dict):
        x = max(v - c.get("allowance", 0), 0)
        r = next((rt for lim, rt in c["slab"] if x <= lim), c["top"])
        return r * x // 10000
    a, b = c
    return _tax(b, v - a)


def p6_inherit(S, key, name, classes, classOf, statute, dated, grade, src, quotes, exempt=(), lookback=0, uns=(),
               giftSmall=0, only=None, oecdDrop=True, ev=None):
    """4300: an InheritanceTax. classes = [(allowance, bands)] or [dict(allowance, slab=[(limit, bp)], top=bp)] (whole-amount
    tariff), classOf = {relation: class index} (others: last class); exempt = relations taxed at 0; giftSmall = an exempt
    value per gift; only = "inheritance" / "gift": the other kind is wholly exempt here (taxed by another object)."""
    if oecdDrop:
        _drop(S, "4300")
    last = len(classes) - 1
    cl = ",\n    ".join(_cls_lean(c) for c in classes)
    arms = "".join(f"  | .{r} => {classOf[r]}\n" for r in _REL if r in classOf)
    wild = "" if all(r in classOf for r in _REL) else f"  | _ => {last}\n"
    ev_in, ev = ev, None
    if giftSmall:
        ev = f"fun t => if t.kind == .gift then min (pos t.statutoryValue) {giftSmall} else 0"
    if only == "inheritance":
        ev = "fun t => if t.kind == .gift then pos t.statutoryValue else 0"
    elif only == "gift":
        ev = "fun t => if t.kind == .gift then 0 else pos t.statutoryValue"
    if ev_in is not None:  # pass 7: an explicit exempt-value function (Lean, fun t => ...)
        ev = ev_in
    S["lean"] += (f"\n/-- {statute} -/\ndef p6{key}Class : Relation → Nat\n{arms}{wild}"
                  f"def p6{key} : InheritanceTax :=\n  {{ name := {_q(name)}, classOf := p6{key}Class,\n    classes := [{cl}],\n"
                  f"    exemptRelations := [{', '.join('.' + r for r in exempt)}], lookbackYears := {lookback}"
                  + (f",\n    exemptValue := {ev}" if ev else "")
                  + " }\n")
    S["families"].append((f"4300 {name}", [".estate"], f"p6{key}.charges g.transfers {_q(statute)}"))
    kind = "gift" if only == "gift" else "inheritance"
    for r in ("spouse", "child", "sibling", "unrelated"):
        for v in (100000, 1000000):
            t = 0 if r in exempt else _cls_tax(classes[classOf.get(r, last)], v)
            S["guards"].append(f"p6{key}.tax {{ kind := .{kind}, value := {v}, relation := .{r} }} == {t}")
    if only:
        other = "inheritance" if only == "gift" else "gift"
        S["guards"].append(f"p6{key}.tax {{ kind := .{other}, value := 1000000, relation := .unrelated }} == 0")
    if giftSmall:
        S["guards"].append(f"p6{key}.tax {{ kind := .gift, value := 100000, relation := .unrelated }} == {_cls_tax(classes[last], 100000 - giftSmall)}")
    S["unsupported"] += [(c, "4300 " + t) for c, t in uns]
    S["notes"].append(f"{S['cc']} 4300 {name}: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "4300", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["InheritanceTax", "TaxClass"], "unsupported": [t for _, t in uns]})
    _doc(S, f"4300 {name}", src, quotes)


def p6_wealth(S, key, name, bands, allowance, statute, dated, grade, src, quotes, level="central", uns=(), marriedAllowance=None,
              exemptKinds=(), entry=-1):
    """4200: a WealthTax on the household's assets less debts (assessed values where given)."""
    _drop(S, "4200")
    f = [f"name := {_q(name)}", f"sched := {_sch(bands)}", f"allowance := {allowance}"]
    if exemptKinds:
        f.append("exemptKinds := [" + ", ".join("." + k for k in exemptKinds) + "]")
    if entry >= 0:
        f.append(f"entryThreshold := {entry}")
    S["lean"] += f"\n/-- {statute} -/\ndef p6{key} : WealthTax := {{ " + ", ".join(f) + " }\n"
    ma = marriedAllowance if marriedAllowance is not None else allowance
    S["lean"] += (f"def p6{key}For (married : Bool) : WealthTax := if married then {{ p6{key} with allowance := {ma} }} else p6{key}\n"
                  f"def p6{key}Charges (g : CanonGlobal) : List Charge :=\n"
                  f"  if g.entity == .company || g.assets.isEmpty then [] else\n"
                  f"  let w := p6{key}For g.household.married\n"
                  f"  [charge .wealth w.name (w.netWealth g.assets) (fun _ => w.base g.assets) (fun _ => w.gross g.assets)\n"
                  f"     (event := \"2025\") (level := .{level}) (statute := {_q(statute)})]\n")
    S["families"].append((f"4200 {name}", [".wealth"], f"p6{key}Charges g"))
    for v in (allowance, allowance + 1000000, 10 * allowance + 5000000):
        S["guards"].append(f"p6{key}.gross [{{ kind := .deposits, value := {v} }}] == {_tax(bands, v - allowance)}")
    S["guards"].append(f"(p6{key}For true).gross [{{ kind := .deposits, value := {ma + 1000000} }}] == {_tax(bands, 1000000)}")
    S["unsupported"] += [(c, "4200 " + t) for c, t in uns]
    S["notes"].append(f"{S['cc']} 4200 {name}: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "4200", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["WealthTax"], "unsupported": [t for _, t in uns]})
    _doc(S, f"4200 {name}", src, quotes)


def p6_finish(S):
    if S.get("lean"):
        S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")


def _drop_wht(S):
    S["taxes"] = [t for t in S["taxes"] if not (t.get("grade") == "C" and "ithholding" in t.get("tax", ""))]
    S["unsupported"] = [u for u in S["unsupported"] if not ("ithholding" in u[1] and "grade C" in u[1])]
    S.setdefault("families", []); S.setdefault("notes", []); S.setdefault("guards", [])
    S["lean"] = S.get("lean") or ""


def p6_wht(S, rules, statute, dated, grade, src, facts, uns=()):
    """1200 withholding on payments to non-resident companies: rules = [(kind, rateBp)] (statutory, treaty-free)."""
    _drop_wht(S)
    rl = ",\n    ".join(f"{{ kind := .{k}, toCompany := none, minStakeBp := 0, rateBp := {r}, statute := {_q(statute)} }}" for k, r in rules)
    S["lean"] += f"\n/-- {statute} -/\ndef p6wht : Wht :=\n  {{ name := \"withholding tax on payments abroad\", rules := [\n    {rl}] }}\n"
    S["families"].append(("1200 withholding on payments abroad (pass 6)", [".cit"], "(if g.entity == .company then p6wht.charges g.company else [])"))
    for k, r in rules:
        S["guards"].append(f"p6wht.amount {{ kind := .{k}, amount := 100000, toCompany := true, stakeBp := 0 }} == {r * 100000 // 10000}")
    S["unsupported"] += [(c, "1200 withholding: " + t) for c, t in uns]
    S["notes"].append(f"{S['cc']} 1200 withholding: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "1200", "tax": "Withholding on payments abroad", "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["Wht"], "unsupported": [t for _, t in uns] + ["treaty rates and EU directives out of scope (statutory, treaty-free)"]})
    _doc(S, "1200 withholding on payments abroad", src, facts)


def p6_wht_absent(S, statute, why, dated, grade="B"):
    _drop_wht(S)
    S["taxes"].append({"oecd": "1200", "tax": "Withholding on payments abroad (not levied)", "statute": statute, "dated": dated, "grade": grade,
                       "status": "absent", "kernel_parts": [], "unsupported": []})
    S["doc"] += f"\n* **Withholding on payments to non-resident companies not levied (cited, pass 6, grade {grade})**: {statute}: {why} ({dated})\n"


def p6_gains(S, key, name, statute, dated, grade, src, facts, sec=None, re=None, uns=()):
    """1100 (P3): tax on the entity's own disposals, outside the 1.x PIT. sec / re = dict(bands=[(from, bp)], incl=bp of
    the net gain counted, hold=months from which the class is exempt (0: none), mainHome=exempt main home) for securities
    (shares, bonds) and real estate; each class's gains and losses net within the class (a net loss counts as 0)."""
    _drop(S, "1100")
    L, ch = [f"\n/-- {statute} -/"], []
    for cls, r, test in (("Sec", sec, "(d.kind.isShares || d.kind == .bonds)"), ("Re", re, "d.kind.isRealEstate")):
        if not r:
            continue
        cond = test
        if r.get("hold"):
            cond += f" && d.heldMonths < {r['hold']}"
        if r.get("mainHome"):
            cond += " && !d.mainHome"
        L.append(f"def p6{key}{cls}Sel (d : Disposal) : Bool := {cond}")
        L.append(f"def p6{key}{cls}Base (ds : List Disposal) : Int := divR .down ({r.get('incl', 10000)} * pos (isum ((ds.filter p6{key}{cls}Sel).map (·.gain)))) BP")
        lab = "securities" if cls == "Sec" else "real estate"
        if r.get("steps"):
            # pass 7: rate by each disposal's holding period, steps = [(fromMonths, bp)] ascending; the class's gains and
            # losses net at their own rates (a net negative counts as 0)
            st = r["steps"]
            rate = " else ".join(f"if m < {st[i + 1][0]} then {bp}" for i, (_, bp) in enumerate(st[:-1])) + f" else {st[-1][1]}"
            L.append(f"def p6{key}{cls}Rate (m : Nat) : Int := {rate}")
            L.append(f"def p6{key}{cls}TaxD (ds : List Disposal) : Int :=\n  let t := isum ((ds.filter p6{key}{cls}Sel).map fun d => p6{key}{cls}Rate d.heldMonths * d.gain)\n  if t > 0 then divR .down t BP else 0")
            ch.append(f"charge .pit {_q(name + ' (' + lab + ')')} (isum ((g.disposals.filter p6{key}{cls}Sel).map (·.gain))) (fun _ => p6{key}{cls}Base g.disposals) (fun _ => p6{key}{cls}TaxD g.disposals) (event := \"disposals 2025\") (statute := {_q(statute)})")
            k = "listedShares" if cls == "Sec" else "realEstate"
            def rt(m):
                return [bp for fm, bp in st if fm <= m][-1]
            for m in (12, 72, 150):
                S["guards"].append(f"p6{key}{cls}TaxD [{{ kind := .{k}, proceeds := 150000, cost := 50000, heldMonths := {m} }}] == {rt(m) * 100000 // 10000}")
            S["guards"].append(f"p6{key}{cls}TaxD [{{ kind := .{k}, proceeds := 150000, cost := 50000, heldMonths := 12 }}, {{ kind := .{k}, proceeds := 50000, cost := 100000, heldMonths := 72 }}] == {max(0, rt(12) * 100000 - rt(72) * 50000) // 10000}")
            if r.get("hold"):
                S["guards"].append(f"p6{key}{cls}Base [{{ kind := .{k}, proceeds := 150000, cost := 50000, heldMonths := {r['hold']} }}] == 0")
            continue
        L.append(f"def p6{key}{cls}Tax (b : Int) : Int := ({_sch(r['bands'])}).tax {{}} b")
        ch.append(f"charge .pit {_q(name + ' (' + lab + ')')} (isum ((g.disposals.filter p6{key}{cls}Sel).map (·.gain))) (fun _ => p6{key}{cls}Base g.disposals) (fun _ => p6{key}{cls}Tax (p6{key}{cls}Base g.disposals)) (event := \"disposals 2025\") (statute := {_q(statute)})")
        g1 = 100000
        S["guards"].append(f"p6{key}{cls}Tax (p6{key}{cls}Base [{{ kind := .{'listedShares' if cls == 'Sec' else 'realEstate'}, proceeds := 150000, cost := 50000, heldMonths := 12 }}]) == {_tax(r['bands'], r.get('incl', 10000) * g1 // 10000)}")
        if r.get("hold"):
            S["guards"].append(f"p6{key}{cls}Base [{{ kind := .{'listedShares' if cls == 'Sec' else 'realEstate'}, proceeds := 150000, cost := 50000, heldMonths := {r['hold']} }}] == 0")
        if r.get("mainHome"):
            S["guards"].append(f"p6{key}{cls}Base [{{ kind := .home, proceeds := 150000, cost := 50000, mainHome := true }}] == 0")
        S["guards"].append(f"p6{key}{cls}Base [{{ kind := .{'listedShares' if cls == 'Sec' else 'realEstate'}, proceeds := 50000, cost := 150000 }}] == 0")
    L.append(f"def p6{key}Charges (g : CanonGlobal) : List Charge :=\n  if g.disposals.isEmpty then [] else\n  [" + ",\n   ".join(ch) + "]")
    S["lean"] += "\n".join(L) + "\n"
    S["families"].append((f"1100 {name}", [], f"p6{key}Charges g"))
    S["unsupported"] += [(c, "1100 " + t) for c, t in uns] + [("g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate))", "1100 gains on other assets (business, vehicles, other) not modelled")]
    S["notes"].append(f"{S['cc']} 1100 {name}: {dated} (grade {grade})")
    S["taxes"].append({"oecd": "1100", "tax": name, "statute": statute, "dated": dated, "grade": grade,
                       "kernel_parts": ["Disposal.gain", "Schedule"], "unsupported": [t for _, t in uns]})
    _doc(S, f"1100 {name}", src, facts)
