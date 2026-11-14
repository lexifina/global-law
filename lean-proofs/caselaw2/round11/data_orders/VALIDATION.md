# Parser validation on corpus overlap (orders11b, 2026-11-14)

No key read. One extra fetch: `https://www.supremecourt.gov/orders/journal/Jnl16.pdf` (OT2016, 200, logged in
SOURCES.tsv; text in `round11/agents/orders11b/txt/`, PDF deleted). The same parser (`parse_jnl.py`) was run on it and
its entries for Oct 2016 - Jun 2017 compared with the corpus's Supreme Court nodes (court 2906, S. Ct. memorandum
orders + opinions; round-6 cache meta + git texts) month by month (`round11/agents/orders11b/scripts/validate.py`,
per-row files in `round11/agents/orders11b/work/val16/`).

| measure | count |
|---|---|
| Journal entries (Oct 2016 - Jun 2017) | 6,773 |
| entries whose docket(s) match a corpus 2906 node of that month | 6,684 (98.7%) |
| ... of which the node has the same date | 6,667 (99.7%) |
| corpus 2906 nodes of those months | 7,359 |
| corpus nodes matched by a Journal entry | 7,324 (99.5%) |
| caption party-name token overlap >= 0.5 (Journal caption vs corpus title/parties) | 6,046 of 6,684 (90.5%; most misses are short corpus titles or "In re" captions) |
| disposition class agreement (Journal class vs a crude word classifier on the corpus text) | 5,982 of 6,684 (89.5%) |
| Journal GVR entries | 51: all 51 match a corpus node on the same date; the corpus text is GVR-worded in 48, the other 3 carry separate writings that the crude classifier reads as "other"/"affirmed" |
| corpus texts GVR-worded (non-opinion), Journal class | gvr 48, cert_denied 2 (cert denials whose dissents say "vacate ... remand") |

Unmatched Journal entries (89): 49 "other" orders in pending cases (motions, argument allotments) that the reporter
does not print as separate memorandum orders, 25 cert denials absent from the corpus, 13 original-jurisdiction
entries ("65, Original" vs the corpus's "65 Orig." docket form; a docket-form difference of the check only) and 2
others. Unmatched
corpus nodes (35): mostly rule-46 dismissals (docket printed with an "R46" number) and original-jurisdiction dockets.
