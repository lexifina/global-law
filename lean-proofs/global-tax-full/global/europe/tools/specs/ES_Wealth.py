S = dict(cc="ES", fam="Wealth",
doc=r'''# Spain 2025 (Comunidad de Madrid): Impuesto sobre el Patrimonio and ITSGF (4200), Sucesiones y Donaciones (4300)

The household is taken as resident in the Comunidad de Madrid (the registry's reference municipality, Madrid).
Sources: BOE legislación consolidada, each article with its amendment notes: Ley 19/1991 del Impuesto sobre el
Patrimonio (`es/law/lip.html`), Ley 38/2022 art. 3 (ITSGF, `es/law/ley38_2022.html`), Ley 29/1987 del ISD
(`es/law/lisd.html`), and the Madrid Decreto Legislativo 1/2010 texto refundido de tributos cedidos
(`BOCM-m-2010-90068`, `es/law/madrid_dleg1_2010_c.html`); sha256 in `law/SHA256SUMS`.
* **LIP art. 4.Nueve**: the vivienda habitual is exempt "hasta un importe máximo de 300.000 euros". **Art. 28**: the
  mínimo exento is the one approved by the Comunidad; **Madrid art. 19** "el mínimo exento ... se fija en 700.000
  euros" (Ley 6/2011, from 1.1.2012). **Art. 30.2**: the state scale applies when the Comunidad has not approved one
  (Madrid has none): 0,2 % to 167.129,45; 0,3 %; 0,5 % from 334.252,88; 0,9 % from 668.499,75; 1,3 % from
  1.336.999,51; 1,7 % from 2.673.999,01; 2,1 % from 5.347.998,03; 3,5 % from 10.695.996,06. **Madrid art. 20**
  "Bonificación general ... del 100 por 100 de dicha cuota si esta es positiva".
* **Ley 38/2022 art. 3** (ITSGF): prorrogued "en tanto no se produzca la revisión de la tributación patrimonial" (RDL
  8/2023 DA 5.2); Tres: net wealth "superior a 3.000.000 de euros"; Cuatro: the IP exemptions apply; Nueve: "mínimo
  exento, en 700.000 euros"; Diez: devengo 31 December; Once: 0 % to 3.000.000, 1,7 % to 5.347.998,03, 2,1 % to
  10.695.996,06, 3,5 % above; Quince: "podrá deducir la cuota del Impuesto sobre el Patrimonio del ejercicio
  efectivamente satisfecha" (in Madrid: none, after the 100 % bonificación).
* **Madrid art. 21 Uno 1** (mortis causa, replacing LISD art. 20.2 a): Grupo I descendants under 21 "16.000 euros,
  más 4.000 euros por cada año menos de veintiuno ... sin que la reducción pueda exceder de 48.000 euros"; Grupo II
  (descendants 21 or older, spouses, ascendants) 16.000; Grupo III (collaterals of 2nd and 3rd degree, in-laws)
  8.000; Grupo IV none. **Art. 23** tarifa: 7,65 % up to 8.313,20 rising to 34 % above 798.817,20. **Art. 24**
  coeficientes for patrimonio preexistente up to 403.000: 1,00 (I-II), 1,5882 (III), 2,00 (IV). **Art. 25.1**
  mortis causa: Grupos I y II "bonificación del 99 por ciento", Grupo III 50 %; **25.2** inter vivos: a) base up to
  1.000 euros 100 %; b) Grupos I y II 99 %, Grupo III 50 %.
''',
lean=r'''
/-- LIP art. 30.2 state scale (Madrid approved none); band limits rounded to the euro. -/
def ipScale : Schedule := Schedule.ofList [(0, 20), (167129, 30), (334253, 50), (668500, 90), (1337000, 130), (2674000, 170), (5347998, 210), (10695996, 350)]

/-- Impuesto sobre el Patrimonio, Madrid: LIP art. 4.Nueve (home to 300 000), Madrid art. 19 (mínimo 700 000). -/
def ip : WealthTax := { name := "Impuesto sobre el Patrimonio", homeExempt := 300000, allowance := 700000, sched := ipScale }

/-- Madrid art. 20: bonificación del 100 % of a positive cuota. -/
def ipDue (as : List Asset) : Int := ip.gross as - ip.gross as

/-- Ley 38/2022 art. 3 Nueve, Once: ITSGF, mínimo 700 000, IP exemptions (home to 300 000). -/
def itsgf : WealthTax := { name := "Impuesto Temporal de Solidaridad de las Grandes Fortunas", homeExempt := 300000, allowance := 700000, sched := Schedule.ofList [(0, 0), (3000000, 170), (5347998, 210), (10695996, 350)] }

/-- art. 3 Quince: less the IP cuota effectively paid (Madrid: the cuota after the 100 % bonificación). -/
def itsgfDue (as : List Asset) : Int := pos (itsgf.gross as - ipDue as)

def wealthCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company || g.assets.isEmpty then [] else
  [charge .wealth ip.name (ip.netWealth g.assets) (fun _ => ip.base g.assets) (fun _ => ipDue g.assets)
     (event := "31 December 2025") (level := .state) (statute := "Ley 19/1991 arts. 4.Nueve, 28, 30.2; DLeg Madrid 1/2010 arts. 19-20 (bonificación 100 %)"),
   charge .wealth itsgf.name (itsgf.netWealth g.assets) (fun _ => itsgf.base g.assets) (fun _ => itsgfDue g.assets)
     (event := "31 December 2025") (statute := "Ley 38/2022 art. 3 (Nueve, Once, Quince)")]

/-- ISD Madrid tarifa (DLeg 1/2010 art. 23), band limits rounded to the euro. -/
def isdScale : Schedule := Schedule.ofList [(0, 765), (8313, 850), (16001, 935), (24002, 1020), (32003, 1105), (40003, 1190), (48004, 1275), (56005, 1360), (64005, 1445), (72006, 1530), (80007, 1615), (119948, 1870), (159888, 2125), (239770, 2550), (399409, 2975), (798817, 3400)]

/-- LISD art. 20.2 a) groups: 1 descendants under 21, 2 descendants 21+, spouse, ascendants, 3 siblings, nieces and
nephews (collaterals of 2nd-3rd degree), 4 the rest. -/
def grupo (t : Transfer) : Nat :=
  match t.relation with
  | .child | .grandchild => if t.recipientAge < 21 then 1 else 2
  | .spouse | .parent => 2
  | .sibling | .nieceNephew => 3
  | _ => 4

/-- Madrid art. 21 Uno 1 (mortis causa only). -/
def reduccion (t : Transfer) : Int :=
  if t.kind != .inheritance then 0 else
  match grupo t with
  | 1 => min 48000 (16000 + 4000 * (21 - (t.recipientAge : Int)))
  | 2 => 16000
  | 3 => 8000
  | _ => 0

/-- Madrid art. 24 coefficient (bp) for patrimonio preexistente up to 403 000. -/
def coef (t : Transfer) : Int := match grupo t with | 1 | 2 => 10000 | 3 => 15882 | _ => 20000

/-- Madrid art. 25.1 (mortis causa) and 25.2 b) (inter vivos): 99 % groups I-II, 50 % group III. -/
def bonifBp (t : Transfer) : Int := match grupo t with | 1 | 2 => 9900 | 3 => 5000 | _ => 0

def isdBase (t : Transfer) : Int := pos (t.statutoryValue - reduccion t)

def isdDue (t : Transfer) : Int :=
  let ct := divR .down (isdScale.tax {} (isdBase t) * coef t) BP
  if t.kind != .inheritance && isdBase t ≤ 1000 then 0 else ct - divR .down (ct * bonifBp t) BP

def isdCharges (g : CanonGlobal) : List Charge :=
  (g.transfers.filter (fun t => t.relation != .charity)).zipIdx.map fun (t, i) =>
    charge .estate (if t.kind == .inheritance then "Impuesto sobre Sucesiones" else "Impuesto sobre Donaciones") t.statutoryValue
      (fun _ => isdBase t) (fun _ => isdDue t) (event := s!"{if t.kind == .gift then "gift" else "inheritance"} {i + 1}") (level := .state)
      (statute := "Ley 29/1987 arts. 20-22; DLeg Madrid 1/2010 arts. 21, 23, 24, 25")
''',
families=[("4200 Patrimonio (Madrid) + ITSGF", [".wealth"], "wealthCharges g"),
          ("4300 Sucesiones y Donaciones (Madrid)", [".estate"], "isdCharges g")],
notes=["ES 4200/4300: household resident in the Comunidad de Madrid"],
unsupported=[("!g.assets.isEmpty", "IP and ITSGF: límite conjunto with the IRPF (60 %, LIP art. 31, Ley 38/2022 art. 3 Doce) not applied; exempt business assets and holdings (LIP art. 4.Ocho) not separated"),
  ("!g.transfers.isEmpty", "ISD: patrimonio preexistente taken in the lowest band (coefficient 1,00 / 1,5882 / 2,00); accumulation of gifts (LISD art. 30) and the business and home reductions (Madrid art. 21-22) not applied; other relatives taken in Grupo IV")],
guards=["-- IP: base 1 000 000 (shares 1 700 000 less the mínimo): 2 506,86 + 331 500,25 x 0,9 % = 5 490,36",
        "ip.gross [{ kind := .listedShares, value := 1700000 }] == 5490",
        "ipDue [{ kind := .listedShares, value := 1700000 }] == 0",
        "ip.base [{ kind := .home, value := 1000000 }] == 0",
        "-- ITSGF: shares 5 000 000, base 4 300 000: 1 300 000 x 1,7 %",
        "itsgfDue [{ kind := .listedShares, value := 5000000 }] == 22100",
        "itsgfDue [{ kind := .home, value := 1000000 }, { kind := .listedShares, value := 3000000 }] == 0",
        "-- ISD: child of 30 inheriting 300 000: base 284 000, cuota 51 350,98, 99 % bonificación",
        "isdBase { kind := .inheritance, relation := .child, value := 300000, recipientAge := 30 } == 284000",
        "let d := isdDue { kind := .inheritance, relation := .child, value := 300000, recipientAge := 30 }; 512 ≤ d && d ≤ 515",
        "isdBase { kind := .inheritance, relation := .child, value := 300000, recipientAge := 15 } == 260000",
        "-- sibling inheriting 100 000: base 92 000, cuota 11 117,0 x 1,5882 = 17 656, less 50 %",
        "let d := isdDue { kind := .inheritance, relation := .sibling, value := 100000 }; 8825 ≤ d && d ≤ 8830",
        "isdDue { kind := .gift, relation := .unrelated, value := 1000 } == 0"],
taxes=[{"oecd": "4200", "tax": "Impuesto sobre el Patrimonio (Comunidad de Madrid)", "statute": "Ley 19/1991 arts. 4.Nueve, 28, 30.2; DLeg Madrid 1/2010 arts. 19, 20", "dated": "BOE consolidado (Madrid art. 19 Ley 6/2011, art. 20 bonificación 100 %)", "grade": "A", "kernel_parts": ["WealthTax (homeExempt, allowance)"], "unsupported": ["límite conjunto (art. 31)", "business exemptions (art. 4.Ocho)"]},
       {"oecd": "4200", "tax": "Impuesto Temporal de Solidaridad de las Grandes Fortunas", "statute": "Ley 38/2022 art. 3", "dated": "BOE consolidado; prorrogued by RDL 8/2023 DA 5.2", "grade": "A", "kernel_parts": ["WealthTax"], "unsupported": ["límite conjunto (apartado Doce)"]},
       {"oecd": "4300", "tax": "Impuesto sobre Sucesiones y Donaciones (Comunidad de Madrid)", "statute": "Ley 29/1987 arts. 20-22; DLeg Madrid 1/2010 arts. 21, 23, 24, 25", "dated": "BOE consolidado (BOCM-m-2010-90068) with its amendment notes", "grade": "B", "kernel_parts": ["Charge (Madrid tarifa, coefficient, bonificaciones)"], "unsupported": ["patrimonio preexistente bands", "gift accumulation (art. 30)", "business and home reductions"]}])

# ---- pass 16 (R1 Europe, 2026-11-21): year-in-force audit (tools/p16_rows.py, tools/yif16_rows.json) ----
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
p16_rows(S)
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
