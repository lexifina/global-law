S = {'cc': 'LU', 'fam': 'Capital', 'families': [], 'doc': "# LU 2025: Capital family not reached (grade C)\n\n* 1100 Gains of individuals on shares and property (disposals) (LIR art. 99bis, 99ter (plus-values spéculatives)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)\n", 'notes': [], 'unsupported': [('g.entity == .household && !g.disposals.isEmpty', "1100 Gains of individuals on shares and property (disposals): not modelled (grade C: the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed))")], 'guards': [], 'taxes': [{'oecd': '1100', 'tax': 'Gains of individuals on shares and property (disposals)', 'statute': 'LIR art. 99bis, 99ter (plus-values spéculatives)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed)", 'unsupported': ["would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)"]}]}

# ---- pass 10 (R1 Europe, 2026-11-21): vehicle taxes, conditional withholding, remaining withholding (tools/p10_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
p10_rows(S)
p6_finish(S)

# ---- pass 14 (R1 Europe, 2026-11-21): P6, withholding notes, vehicles (tools/p14_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
p14_rows(S)
p6_finish(S)

# ---- FT review, seventh pass (FT reviewer 7, 2026-11-21): art. 99ter gains of 2025 at a quarter of the global rate (Dataset round 5, R5-6) ----
# Loi du 22 mai 2024 (Mémorial A 219) art. 14: "Les revenus nets réalisés au cours de la période allant du 1er janvier 2024 au
# 31 décembre 2024, par un contribuable, personne physique, aux termes de l'article 99ter ... sont à considérer comme revenus
# extraordinaires imposables par application de l'article 131, alinéa 1er, lettre d)" (a quarter of the global rate); the end
# date replaced by "30 juin 2025" (Loi du 4 avril 2025, Mémorial A 121, art. 7, effect 1.1.2025) and by "30 septembre 2025"
# (Loi du 27 juin 2025, Mémorial A 271, art. 7, in force 1.7.2025). Texts: legilux filestore PDFs fetched 2026-11-21
# (`ftreview/rv7/fetch/lu/l2024_a219.pdf`, `l2025_a121.pdf`, `l2025_a271.pdf`; copies in `lu/law/`). So 99ter gains realised
# 1.1-30.9.2025 pay a quarter (shareBp 2500), from 1.10.2025 half (art. 131 (1) c). Kernel 2.6.0 `StackRule` has no date
# window (KERNEL_REQUESTS "FT reviewer 7"): the rule takes the quarter, which also matches the model's reading of every 2025
# sale under the two-year derogation (art. 99bis, to 30.9.2025 after L. 27.06.25); grade A -> B, flagged.
_a = S["lean"].index("def p14luRe (married : Bool) : StackRule :=")
_b = S["lean"].index("shareBp := 5000 }", _a)
S["lean"] = (S["lean"][:_b] + "shareBp := 2500 }" + S["lean"][_b + len("shareBp := 5000 }"):])
S["lean"] = S["lean"].replace('"Impôt sur le revenu: plus-values immobilières (art. 99ter), demi-taux global"',
    '"Impôt sur le revenu: plus-values immobilières (art. 99ter), quart du taux global (2025: to 30 September)"', 1)
S["lean"] = S["lean"].replace('statute := "L.I.R. art. 99ter (1)-(2), 102 (6), 102bis, 130 (4), 131 (1) c, 132 (2)"',
    'statute := "L.I.R. art. 99ter (1)-(2), 102 (6), 102bis, 130 (4), 131 (1) d, 132 (2); Loi du 22 mai 2024 art. 14 (L. 04.04.25 art. 7, L. 27.06.25 art. 7: gains realised to 30.9.2025)"', 1)
assert "quart du taux global (2025" in S["lean"]
S["unsupported"] = [(c, t.replace("real estate sold from 1 July 2025 is read under the first-half two-year rule",
                                   "real estate sold from 1 October 2025 is read under the two-year rule of 1.1-30.9.2025 (art. 99bis, L. 27.06.25)")) for c, t in S["unsupported"]]
S["unsupported"] += [("g.disposals.any (fun d => (d.kind == .home || d.kind == .realEstate || d.kind == .land) && !d.mainHome && 25 ≤ d.heldMonths)",
    "1100 gains (art. 99ter): taxed at a quarter of the global rate (Loi du 22 mai 2024 art. 14 as amended: gains realised 1.1-30.9.2025); a sale from 1 October 2025 owes half (art. 131 (1) c): the sale date is not read (kernel 2.6.0 StackRule has no date window; grade B)")]
S["guards"] += ["(p14luRe false).shareBp == 2500", "(p14luSub false).shareBp == 5000"]
S["doc"] += ("\n* FT review (seventh pass): art. 99ter gains realised 1 January - 30 September 2025 are taxed at a quarter of the global rate "
             "(Loi du 22 mai 2024 art. 14; L. 04.04.25 art. 7; L. 27.06.25 art. 7); the rule takes the quarter for every 2025 sale (no date "
             "window in kernel 2.6.0); art. 100 stays at half.\n")
for t in S["taxes"]:
    if t.get("tax", "").startswith("Plus-values de cession (art. 99ter, art. 100"):
        t["tax"] = "Plus-values de cession (art. 99ter: quart du taux global to 30.9.2025; art. 100: demi-taux global), stacked"
        t["grade"] = "B"
        t["statute"] = "L.I.R. art. 99ter, 100, 102 (6), 102bis, 130 (4), 131 (1) c, d, 132 (2); Loi du 22 mai 2024 art. 14 (as amended by L. 04.04.25 art. 7 and L. 27.06.25 art. 7)"
        t["dated"] = "texte coordonné en vigueur au 1er janvier 2025 (with L. 04.04.25 and L. 27.06.25); Mémorial A 2024 n° 219, A 2025 n° 121 and n° 271 (legilux)"
        t["unsupported"] = list(t.get("unsupported", [])) + ["the sale date is not read: art. 99ter gains of 1.10-31.12.2025 owe half the global rate, not a quarter (B)"]
p6_finish(S)

# ---- pass 17 (R1 Europe, 2026-11-21): kernel 2.7.0 items, audit follow-ups (tools/p17_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p17_rows.py")).read())
p17_rows(S)
p6_finish(S)
