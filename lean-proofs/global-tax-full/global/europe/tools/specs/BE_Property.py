S = {'cc': 'BE', 'fam': 'Property', 'families': [], 'doc': "# BE 2025: Property family not reached (grade C)\n\n* 4400 Real-estate transfer and stamp duties (Code des droits d'enregistrement (Région de Bruxelles-Capitale, 12,5 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)\n* 4100 Recurrent property tax (précompte immobilier (Bruxelles)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)\n", 'notes': [], 'unsupported': [('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)'), ('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)')], 'guards': [], 'taxes': [{'oecd': '4400', 'tax': 'Real-estate transfer and stamp duties', 'statute': "Code des droits d'enregistrement (Région de Bruxelles-Capitale, 12,5 %)", 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act's 2025 rate articles (and the reference region's rate where regional)"]}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'précompte immobilier (Bruxelles)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act and the reference municipality's 2025 rate (registry choice)"]}]}

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_finish(S)

# ---- FT review, seventh pass (FT reviewer 7, 2026-11-21): securities purchases are grade C, not a silent 0 (Dataset round 5, R5-5) ----
# The 4400 family books the Brussels droits d'enregistrement on real estate only; a purchase of shares or other securities is
# liable to the taxe sur les opérations de bourse (Code des droits et taxes divers, livre II, art. 120 ff.), whose text is not
# held: the entity is reported as not reached (grade C) instead of a computed 0.
S["unsupported"] += [("g.purchases.any (fun p => p.kind == .listedShares || p.kind == .unlistedShares)",
                      "4400 Taxe sur les opérations de bourse (Code des droits et taxes divers art. 120 ff.) on a purchase of securities: not modelled (grade C: text not read)")]
p6_finish(S)
