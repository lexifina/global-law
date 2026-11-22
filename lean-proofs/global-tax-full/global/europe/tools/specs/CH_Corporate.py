S = dict(cc="CH", fam="Corporate",
doc=r'''# Switzerland 2025: direkte Bundessteuer on company profits (1200) and Verrechnungssteuer (1200, withholding)

Sources: fedlex consolidations in force on 1 July 2025: DBG SR 642.11 (2025-01-01, `ch/law/dbg_20250101.html`),
VStG SR 642.21 (2025-01-01, `ch/law/vstg_20250101.html`); sha256 in `law/SHA256SUMS`.
* **DBG Art. 68**: "Die Gewinnsteuer der Kapitalgesellschaften und Genossenschaften beträgt 8,5 Prozent des
  Reingewinns." **Art. 59 (1) lit. a**: "Zum geschäftsmässig begründeten Aufwand gehören auch: a. die eidgenössischen,
  kantonalen und kommunalen Steuern": the federal tax is deductible from its own base, so with the profit before tax P
  and no other tax, t = 8,5 % × (P − t), i.e. t = 8,5 / 108,5 × P (the cantonal and communal taxes, also deductible,
  are not modelled: StG ZH not read).
* **VStG Art. 13 (1) lit. a**: "Die Steuer beträgt: a. 35 Prozent auf Kapitalerträgen" (dividends and bond interest,
  Art. 4 (1) lit. a, b), withheld whoever the recipient is.
''',
lean=r'''
/-- DBG Art. 68 with Art. 59 (1) lit. a: 8,5 % of the profit after the federal tax itself. -/
def bundessteuer (profitBeforeTax : Int) : Int := divR .down (850 * pos profitBeforeTax) 10850

def wht : Wht :=
  { name := "Verrechnungssteuer", rules := [
    { kind := .dividend, rateBp := 3500, statute := "VStG Art. 4 (1) lit. b, Art. 13 (1) lit. a: 35 %" },
    { kind := .interest, rateBp := 3500, statute := "VStG Art. 4 (1) lit. a, Art. 13 (1) lit. a: 35 % (bond and bank interest)" }] }
''',
families=[("1200 direkte Bundessteuer, Verrechnungssteuer", [".cit"],
  "(if g.entity == .company then [charge .cit \"Direkte Bundessteuer (Gewinnsteuer)\" g.company.profit id (fun p => bundessteuer p) (statute := \"DBG Art. 68 (8,5 % des Reingewinns), Art. 59 (1) lit. a\")] else [])\n       ++ (if g.entity == .company then wht.charges g.company else [])")],
notes=["CH 1200: federal profit tax only (cantonal/communal profit and capital taxes not modelled)"],
unsupported=[("g.entity == .company", "Kantons- und Gemeindesteuern on profit and capital (StG ZH) not modelled; the federal tax is computed as if it were the only deductible tax"),
  ("g.entity == .company && g.company.lossesForward > 0", "loss carry-forward (DBG Art. 67, seven years) not modelled"),
  ("g.entity == .company && g.company.dividendsReceived > 0", "Beteiligungsabzug (DBG Art. 69-70) not modelled")],
guards=["bundessteuer 1085000 == 85000", "bundessteuer 10850000 == 850000",
        "wht.amount { kind := .dividend, amount := 100000 } == 35000",
        "wht.amount { kind := .royalty, amount := 100000 } == 0"],
taxes=[{"oecd": "1200", "tax": "Direkte Bundessteuer (Gewinnsteuer)", "statute": "DBG Art. 59 (1) lit. a, Art. 68", "dated": "fedlex 2025-01-01", "grade": "A", "kernel_parts": ["charge (custom: tax deductible from its own base)"], "unsupported": ["cantonal and communal profit and capital taxes", "Art. 67 losses", "Art. 69-70 Beteiligungsabzug"]},
 {"oecd": "1200", "tax": "Verrechnungssteuer", "statute": "VStG Art. 4 (1), Art. 13 (1) lit. a", "dated": "fedlex 2025-01-01", "grade": "A", "kernel_parts": ["Wht"], "unsupported": ["refunds under treaties and to residents (Art. 21 ff.) out of scope"]}])

# ---- pass 2 (R1 Europe, 2026-11-21): Kanton and Stadt Zürich profit tax; joint deduction of the taxes ----
S["doc"] += r'''
## Kanton and Stadt Zürich (pass 2)
Sources: Steuergesetz ZH (LS 631.1), zhlex Nachtrag 127 (pages "1. 1. 25 - 127", `ch/law/stgzh_127.pdf`); Steuerfüsse
2025 from the ESTV Steuerrechner (`TaxRates` of a TaxYear 2025 calculation for TaxLocationID 800100000, Zürich 8001:
"...RateCanton":98, "...RateCity":119; `ch/law/estv_taxrates_2025_zh8001.json`).
* **StG ZH § 71**: "Die Gewinnsteuer der Kapitalgesellschaften und Genossenschaften beträgt 7 Prozent des steuerbaren
  Gewinns" (einfache Steuer), times the Steuerfuss of the canton (98 %) and of the City of Zürich (119 %).
* **DBG Art. 59 (1) lit. a** and **StG ZH § 65 (1) lit. a**: the federal, cantonal and communal taxes are deductible:
  with 8,5 % + 7 % x 217 % = 23,69 % on the profit after taxes, that profit is P x 10 000 / 12 369 (the federal
  charge used P x 850 / 10 850 in pass 1, i.e. without the cantonal taxes).
'''
S["lean"] = S["lean"].replace("/-- DBG Art. 68 with Art. 59 (1) lit. a: 8,5 % of the profit after the federal tax itself. -/\ndef bundessteuer (profitBeforeTax : Int) : Int := divR .down (850 * pos profitBeforeTax) 10850",
  "/-- DBG Art. 68 with Art. 59 (1) lit. a: 8,5 % of the profit after the federal, cantonal and communal profit taxes\n(8,5 % + 7 % x 217 % = 23,69 %: the profit after taxes is P x 10 000 / 12 369). -/\ndef bundessteuer (profitBeforeTax : Int) : Int := divR .down (850 * pos profitBeforeTax) 12369")
assert "12369" in S["lean"]
S["lean"] += r'''
/-- StG ZH § 71: einfache Gewinnsteuer 7 % of the profit after taxes (§ 65 (1) lit. a). -/
def einfacheGewinnsteuer (p : Int) : Int := divR .down (700 * pos p) 12369
/-- Steuerfuss 2025: Kanton 98 %, Stadt Zürich 119 % (ESTV TaxRates 2025). -/
def staatssteuer (p : Int) : Int := divR .down (98 * einfacheGewinnsteuer p) 100
def gemeindesteuer (p : Int) : Int := divR .down (119 * einfacheGewinnsteuer p) 100
'''
_n, _cov, _run = S["families"][0]
S["families"] = [(_n + ", Gewinnsteuer Kanton/Stadt Zürich", _cov, _run +
  "\n       ++ (if g.entity == .company then [charge .cit \"Staatssteuer Zürich (Gewinnsteuer)\" g.company.profit id (fun p => staatssteuer p) (level := .state) (statute := \"StG ZH § 71 (7 %), § 65 (1) lit. a; Steuerfuss Kanton 98 % (2025)\"), charge .cit \"Gemeindesteuer Stadt Zürich (Gewinnsteuer)\" g.company.profit id (fun p => gemeindesteuer p) (level := .local) (statute := \"StG ZH § 71 (7 %), § 65 (1) lit. a; Steuerfuss Stadt Zürich 119 % (2025)\")] else [])")]
S["guards"] = [x for x in S["guards"] if not x.startswith("bundessteuer")] + [
  "-- profit before taxes 1 236 900: after the taxes 1 000 000; 85 000 + 68 600 + 83 300 = 236 900",
  "bundessteuer 1236900 == 85000", "einfacheGewinnsteuer 1236900 == 70000",
  "staatssteuer 1236900 == 68600", "gemeindesteuer 1236900 == 83300",
  "bundessteuer 1236900 + staatssteuer 1236900 + gemeindesteuer 1236900 == 1236900 - 1000000"]
for _t in S["taxes"]:
    if _t["tax"].startswith("Direkte Bundessteuer"):
        _t["unsupported"] = [u for u in _t.get("unsupported", []) if "cantonal" not in u] + ["joint deduction assumes the company is taxed in the City of Zürich"]
S["taxes"] += [
  {"oecd": "1200", "tax": "Staats- und Gemeindesteuer Zürich (Gewinnsteuer)", "statute": "StG ZH § 71, § 65 (1) lit. a; Steuerfüsse 2025 Kanton 98 %, Stadt Zürich 119 %", "dated": "zhlex Nachtrag 127 (1.1.2025); ESTV TaxRates 2025", "grade": "A", "kernel_parts": ["Charge"], "unsupported": ["Kirchensteuer juristischer Personen not modelled", "Beteiligungsabzug (§ 72) not modelled", "patent box and R&D deductions (§§ 64a-64b) not modelled"]}]
S["notes"] = S.get("notes", []) + ["CH 1200: Gewinnsteuer of Kanton (98 %) and Stadt Zürich (119 %), taxes deductible jointly"]
S["notes"] = [n for n in S["notes"] if "cantonal/communal profit and capital taxes not modelled" not in n]

# ---- pass 8 (R1 Europe, 2026-11-21): withholding under kernel 2.3.0, P5/P6 gaps, P7 surcharges, carry-overs (tools/p8_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
p8_rows(S)
p6_finish(S)
