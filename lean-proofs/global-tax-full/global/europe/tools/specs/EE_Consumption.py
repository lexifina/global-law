S = dict(cc="EE", fam="Consumption", imports=["TaxKernel.Global2"],
lean=r"""
/-- January-June 2025: standard rate 22 % (the § 15 (1) wording before RT I, 2024 amendment in force 1.7.2025). -/
def vatH1 : Vat := { vat with standard := 2200 }

/-- Kernel 2.1 `DatedVat`: 22 % to 30 June, 24 % from 1 July 2025; an undated basket is split by days. -/
def vatDated : DatedVat :=
  { periods := [{ vat := vatH1, statute := "Käibemaksuseadus § 15 (1) 22 % (to 30.6.2025)" },
                { start := "2025-07-01", vat := vat, statute := "Käibemaksuseadus § 15 (1) 24 % (from 1.7.2025)" }],
    undatedSupplies := .split }
""",
families=[("5111 käibemaks (two rate periods)", [".vat"], "vatDated.charges g")],
doc=r'''# Estonia 2025: käibemaks (5111); excises not read

Source: Käibemaksuseadus, Riigi Teataja (official) as captured by the Internet Archive on 2025-08-07
(`ee/law/kmss_wb.html`, sha256 in `law/SHA256SUMS`; riigiteataja.ee itself answers scripts with Cloudflare).
* **§ 15 (1)**: "Käibemaksumäär on 24 protsenti maksustatavast väärtusest" (in force from 1 July 2025; 22 % in January
  to June 2025); **(1¹)** "13 protsenti majutuse"; **(2)** 9 %: "1) raamat ja õppekirjandus", "2) ... ravim",
  "5) ajakirjandusväljaanne" (from 1 January 2025).
* **§ 19 (1)**: registration when the year's turnover "ületab kalendriaasta algusest alates 40 000 eurot".
''',
vat=dict(name="Käibemaks", standard=2400, reduced=1300, reduced2=900, threshold=40000,
  statute="Käibemaksuseadus § 15 (1) 24 % (from 1.7.2025), (1¹) 13 %, (2) 9 %; § 16 (maksuvabad); § 19 (1) (40 000 eurot)",
  classes={"hotels": "reduced", "books": "reduced2", "medicines": "reduced2", "newspapers": "reduced2",
           "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"}),
notes=["EE 5111: standard rate 22 % to 30 June and 24 % from 1 July 2025 (kernel 2.1 DatedVat)"],
unsupported=[("!g.consumption.isEmpty", "undated basket lines split by days between the 22 % and 24 % periods; the 22 % wording of § 15 (1) is taken from the rate change, not from a capture dated before July 2025"),
  ("g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits)", "alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus not read")],
guards=["vat.embedded { good := .clothing, amount := 124 } == 24",
        "vat.embedded { good := .hotels, amount := 113 } == 13",
        "vat.embedded { good := .books, amount := 109 } == 9",
        "vat.net { turnover := 40000, sales := [{ good := .other, net := 40000 }] } == 0",
        "vatH1.embedded { good := .clothing, amount := 122 } == 22"],
taxes=[{"oecd": "5111", "tax": "Käibemaks", "statute": "Käibemaksuseadus §§ 15, 16, 19", "dated": "Riigi Teataja via Internet Archive 2025-08-07", "grade": "A", "kernel_parts": ["Vat"], "unsupported": ["22 % January-June: rate known from the amendment, capture dated 2025-08-07", "exemptions (§ 16) not quoted"]},
 {"oecd": "5121", "tax": "Aktsiisid (alcohol, tobacco, fuel)", "statute": "alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus", "grade": "C", "status": "unsupported", "kernel_parts": [], "unsupported": ["not read; riigiteataja.ee behind Cloudflare: would unlock: an Internet Archive capture of the act in force in 2025"]}])

# ---- gap pass (R1 Europe, 2026-11-21): gap-closing pass (tools/pgap_rows.py, tools/gap_rows.json) ----
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
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p18_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/pgap_rows.py")).read())
pgap_rows(S)
p6_finish(S)
