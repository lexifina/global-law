S = {'cc': 'GR', 'fam': 'Corporate', 'doc': '# GR 2025: Φόρος εισοδήματος νομικών προσώπων (1200) and withholding on payments abroad\n\nSource: ΦΕΚ Α\' 78/18.05.2021 (ν. 4799/2021), Εθνικό Τυπογραφείο et.gr DownloadFeksApi fek_pdf=20210100078 (`gr/law/fek_a78_2021_n4799.pdf`); sha256 in `law/SHA256SUMS`.\n* άρθρο 120: "Η περ. α\' της παρ. 1 του άρθρου 58 του Κ.Φ.Ε. (ν. 4172/2013, Α\' 167) τροποποιείται ως προς τον φορολογικό συντελεστή"\n* "1. α) Τα κέρδη από επιχειρηματική δραστηριότητα που αποκτούν τα νομικά πρόσωπα και οι νομικές οντότητες ... φορολογικού έτους 2021 και εφεξής ο συντελεστής του προηγούμενου εδαφίου μειώνεται σε είκοσι δύο τοις εκατό (22%)."\n* "β) Τα πιστωτικά ιδρύματα ... του άρθρου 27Α, φορολογούνται με συντελεστή είκοσι εννέα τοις εκατό (29%)."\n', 'lean': 'def cit : CorpRegime :=\n  { name := "Φόρος εισοδήματος νομικών προσώπων",\n    sched := Schedule.flat 2200 }\n\ndef citStatute : String := "ΚΦΕ (ν. 4172/2013) άρθρο 58 παρ. 1 α) (22 % from tax year 2021), as replaced by ν. 4799/2021 άρθρο 120"\n', 'families': [('1200 Φόρος εισοδήματος νομικών προσώπων', ['.cit'], '(if g.entity == .company then [cit.citCharge g.company citStatute] else [])')], 'notes': ['GR 1200: amending act ν. 4799/2021 read (22 % for tax year 2021 onwards); the consolidated ΚΦΕ as in force in 2025 not reached (later amendments of άρθρο 58 not checked)'], 'unsupported': [('g.entity == .company && g.company.interestExpense > 0', 'interest limitation (ATAD art. 4 transposition) not modelled'), ('g.entity == .company', 'group regimes, CFC, transfer pricing and treaties out of scope')], 'guards': ['cit.citTax { profit := 100000, turnover := 10000000 } == 22000', 'cit.citTax { profit := 1000000, turnover := 10000000 } == 220000'], 'taxes': [{'oecd': '1200', 'tax': 'Φόρος εισοδήματος νομικών προσώπων', 'statute': 'ΚΦΕ (ν. 4172/2013) άρθρο 58 παρ. 1 α) (22 % from tax year 2021), as replaced by ν. 4799/2021 άρθρο 120', 'dated': 'amending act ν. 4799/2021 read (22 % for tax year 2021 onwards); the consolidated ΚΦΕ as in force in 2025 not reached (later amendments of άρθρο 58 not checked)', 'grade': 'B', 'kernel_parts': ['CorpRegime'], 'unsupported': ['read from the 2021 amending act, not from the 2025 consolidated ΚΦΕ', 'credit institutions under άρθρο 27Α (29 %) and simple-book entities of άρθρο 45 not separated', 'Pillar Two minimum tax not modelled']}, {'oecd': '1200', 'tax': 'Withholding on payments abroad', 'statute': 'statutory withholding on dividends, interest, royalties', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': "the 1.x model's law folder holds PIT articles only; aade.gr 403", 'unsupported': ['would unlock: ΚΦΕ άρθρα 58, 64 as in force 2025']}]}

# ---- pass 8 (R1 Europe, 2026-11-21): withholding under kernel 2.3.0, P5/P6 gaps, P7 surcharges, carry-overs (tools/p8_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
p8_rows(S)
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
