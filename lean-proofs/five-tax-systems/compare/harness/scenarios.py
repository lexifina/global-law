"""The households of every analysis, defined in multiples of the average wage (AW) and turned into each country's
currency. Each scenario returns {country: [canonical household, ...]} plus a meta dict per household id.

Conventions (written into the blog post):
* adults are 40; the two children are 6 and 11 (inside the OECD Taxing Wages assumption "aged between 6 and 11",
  so no country's age rules separate them);
* "two-earner couple" splits household earnings 60:40 (the OECD's 100 % + 67 % couple has a 59.9:40.1 split);
* amounts are rounded half up to the whole currency unit.
"""
from common import AW, COUNTRIES, adult, household

CHILD_AGES = (6, 11)

FAMILIES = {
    # name: (adults, married, children, principal share)
    "single": (1, False, (), 1.0),
    "single_parent_2": (1, False, CHILD_AGES, 1.0),
    "couple_1earner_2": (2, True, CHILD_AGES, 1.0),
    "couple_2earner_2": (2, True, CHILD_AGES, 0.6),
}


def fam_household(country, hid, fam, h_aw, married=None, share=None, children=None, extra=None):
    n, m0, kids, s0 = FAMILIES[fam]
    married = m0 if married is None else married
    share = s0 if share is None else share
    kids = kids if children is None else children
    total = h_aw * AW[country]
    if n == 1:
        adults = [adult(wages=total)]
    else:
        w1 = round(total * share)
        adults = [adult(wages=w1), adult(wages=round(total) - w1)]
    return household(hid, adults, married=married, children=kids, **(extra or {}))


def oecd_households(countries=COUNTRIES):
    """The eight family types of Taxing Wages, at the OECD's own average wage."""
    types = {
        "S67": (1, False, (), 0.67, 0.0), "S100": (1, False, (), 1.00, 0.0), "S167": (1, False, (), 1.67, 0.0),
        "SP67": (1, False, CHILD_AGES, 0.67, 0.0), "M100_0": (2, True, CHILD_AGES, 1.00, 0.0),
        "M100_100": (2, True, CHILD_AGES, 1.00, 1.00), "M100_67": (2, True, CHILD_AGES, 1.00, 0.67),
        "M100_67nc": (2, True, (), 1.00, 0.67),
    }
    out, meta = {}, {}
    for c in countries:
        hs = []
        for t, (n, married, kids, m1, m2) in types.items():
            hid = f"oecd-{c}-{t}"
            ads = [adult(wages=AW[c] * m1)] + ([adult(wages=AW[c] * m2)] if n == 2 else [])
            hs.append(household(hid, ads, married=married, children=kids))
            meta[hid] = {"scenario": "oecd", "type": t}
        out[c] = hs
    return out, meta


def curves(countries=COUNTRIES, step=0.01, top=5.0):
    """Average and marginal rate curves: household earnings 0 to `top` AW for the four family types."""
    out, meta = {}, {}
    n = int(round(top / step))
    for c in countries:
        hs = []
        for fam in FAMILIES:
            for i in range(n + 1):
                x = round(i * step, 6)
                hid = f"curve-{c}-{fam}-{i}"
                hs.append(fam_household(c, hid, fam, x))
                meta[hid] = {"scenario": "curves", "family": fam, "h_aw": x}
        out[c] = hs
    return out, meta


def scan(countries=COUNTRIES, top=5.0, units=None):
    """The fine scan for cliffs: household earnings in steps of `units[c]` currency units (default 10, JPY 1000)."""
    units = units or {"US": 10, "FR": 10, "UK": 10, "DE": 10, "JP": 1000}
    out, meta = {}, {}
    for c in countries:
        hs = []
        u = units[c]
        n = int(top * AW[c] // u)
        for fam, (na, married, kids, share) in FAMILIES.items():
            for i in range(n + 1):
                g = i * u
                hid = f"scan-{c}-{fam}-{i}"
                if na == 1:
                    ads = [adult(wages=g)]
                else:
                    w1 = round(g * share)
                    ads = [adult(wages=w1), adult(wages=g - w1)]
                hs.append(household(hid, ads, married=married, children=kids))
                meta[hid] = {"scenario": "scan", "family": fam, "gross_units": g}
        out[c] = hs
    return out, meta
