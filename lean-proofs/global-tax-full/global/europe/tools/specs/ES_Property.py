S = {'cc': 'ES', 'fam': 'Property', 'doc': '# ES 2025: transfer duties on purchases (4400); recurrent property tax not modelled\n\nSource: RDLeg 1/1993 (TRLITPAJD), BOE consolidado (`es/law/itpajd.html`); sha256 in `law/SHA256SUMS`.\n* art. 11.1 a): "Si la Comunidad Autónoma no hubiese aprobado el tipo a que se refiere el párrafo anterior, se aplicará el 6 por 100 a la transmisión de inmuebles"\n', 'lean': 'def d0 : TransferDuty :=\n  { name := "Impuesto sobre Transmisiones Patrimoniales Onerosas (inmuebles)",\n    sched := Schedule.flat 600,\n    kinds := [.home, .realEstate, .land] }', 'families': [('4400 transfer duties', ['.transactions'], 'd0.charges g.purchases "TRLITPAJD art. 11.1 a) (6 %, tipo supletorio)"')], 'notes': ['ES 4400: BOE consolidado (current text with amendment notes)'], 'unsupported': [('!g.purchases.isEmpty', "the Comunidad de Madrid's own rate (DLeg 1/2010, not reached) replaces the 6 % default; new dwellings sold by developers bear IVA + AJD instead (not separated)"), ('g.assets.any (·.kind.isRealEstate)', 'recurrent property tax (4100) not modelled')], 'guards': ['d0.amount { kind := .home, price := 200000 } == 12000', 'd0.amount { kind := .home, price := 2000000 } == 120000'], 'taxes': [{'oecd': '4400', 'tax': 'Impuesto sobre Transmisiones Patrimoniales Onerosas (inmuebles)', 'statute': 'TRLITPAJD art. 11.1 a) (6 %, tipo supletorio)', 'dated': 'BOE consolidado (current text with amendment notes)', 'grade': 'B', 'kernel_parts': ['TransferDuty'], 'unsupported': ["the Comunidad de Madrid's own rate (DLeg 1/2010, not reached) replaces the 6 % default; new dwellings sold by developers bear IVA + AJD instead (not separated)"]}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'local', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["the default municipality's act and rate not read in the P5 pass; would unlock: the property-tax act and the reference municipality's rate (registry choice)"]}]}

# ---- pass 3 (R1 Europe, 2026-11-21): IBI, Madrid 2025 ----
S["doc"] = S["doc"].replace("; recurrent property tax not modelled", "; IBI (4100), Madrid") + r'''

## Impuesto sobre Bienes Inmuebles, Madrid 2025 (pass 3)
Sources (sha256 in `law/SHA256SUMS`):
* **TRLRHL** (RDLeg 2/2004, BOE consolidated text, `es/law/trlrhl.html`): art. 65 "La base imponible de este impuesto
  estará constituida por el valor catastral de los bienes inmuebles"; art. 71.1 "La cuota íntegra de este impuesto
  será el resultado de aplicar a la base liquidable el tipo de gravamen".
* **Ordenanza Fiscal reguladora del Impuesto sobre Bienes Inmuebles (Madrid), de 15 de diciembre de 1989**, as
  amended by the Pleno del Ayuntamiento de Madrid (BOCM núm. 308, 27 de diciembre de 2024, BOCM-20241227-61;
  `es/law/madrid_ibi_bocm20241227_61.pdf`): art. 8.2 "El tipo de gravamen aplicable a los bienes inmuebles de
  naturaleza urbana queda fijado en el 0,428 %, el de los bienes de naturaleza rústica en el 0,567 % y el de los
  bienes inmuebles de características especiales en el 1,141 %"; art. 3.2 "Estarán asimismo exentos, los inmuebles
  de naturaleza rústica o urbana cuya cuota líquida por este impuesto no supere los seis euros"; "La ordenanza
  entrará en vigor el 1 de enero de 2025" (the preamble: "de un tipo de gravamen del 0,442 % al 0,428 %").
Base: the asset's `assessed` value is the valor catastral; without it the market value stands in. All real estate
is urban (0,428 %). Not read: the differentiated rates for non-residential uses above a value threshold (art. 8.3,
which the preamble says exist), the base-liquidable reduction (TRLRHL arts. 66-70) and the bonificaciones: grade B.
'''
S["lean"] = (S.get("lean") or "") + r'''
/-- Ordenanza IBI Madrid art. 8.2 (BOCM 27.12.2024): tipo urbano 0,428 % (thousandths of a percent). -/
def tipoUrbanoMadrid2025 : Int := 428
/-- TRLRHL arts. 65, 71.1: cuota = valor catastral x tipo (euros, rounded down); art. 3.2: exempt if not above 6 euros. -/
def ibiMadrid (vc : Int) : Int :=
  let c := divR .down (pos vc * tipoUrbanoMadrid2025) 100000
  if c ≤ 6 then 0 else c
def ibiCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => a.kind.isRealEstate).map fun (a, i) =>
    charge .propertyRecurrent "Impuesto sobre Bienes Inmuebles (Madrid)" a.statutoryValue (fun v => v) (fun v => ibiMadrid v)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "TRLRHL arts. 65, 71; Ordenanza Fiscal IBI Madrid arts. 3.2, 8.2 (BOCM 27.12.2024: 0,428 %)")
'''
S["families"] = S.get("families", []) + [("4100 IBI (Madrid)", [".propertyRecurrent"], "ibiCharges g.assets")]
S["unsupported"] = [u for u in S["unsupported"] if "4100" not in u[1]] + [
  ("g.assets.any (fun a => a.kind.isRealEstate && a.assessed < 0)", "4100 IBI: no valor catastral given: the market value stands in"),
  ("g.assets.any (fun a => a.kind == .realEstate || a.kind == .land)", "4100 IBI: differentiated rates for non-residential uses (ordenanza art. 8.3, not read), recargo on empty dwellings (TRLRHL art. 72.4), bonificaciones and the base-liquidable reduction (arts. 66-70) not applied")]
S["notes"] = S.get("notes", []) + ["ES 4100: IBI Madrid 2025 tipo urbano 0,428 % (BOCM 27.12.2024, BOCM-20241227-61)"]
S["guards"] = S.get("guards", []) + [
  "-- valor catastral 200 000 x 0,428 % = 856",
  "ibiMadrid 200000 == 856",
  "-- art. 3.2: a cuota of 6 euros or less is exempt (1 400 x 0,428 % = 5,99)",
  "ibiMadrid 1400 == 0", "ibiMadrid 1700 == 7"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "4100"] + [
 {"oecd": "4100", "tax": "Impuesto sobre Bienes Inmuebles (Madrid)", "statute": "TRLRHL (RDLeg 2/2004) arts. 65, 71; Ordenanza Fiscal reguladora del IBI de Madrid arts. 3.2, 8.2 (modificación BOCM núm. 308, 27.12.2024)",
  "dated": "ordinance amendment in force 1.1.2025 (BOCM-20241227-61); TRLRHL BOE consolidated text",
  "grade": "B", "kernel_parts": ["charge (valor catastral x tipo)"],
  "unsupported": ["differentiated non-residential rates (art. 8.3) not read", "base-liquidable reduction (TRLRHL arts. 66-70), bonificaciones, recargo on empty dwellings", "valor catastral is an input (asset.assessed)"]}]
S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")

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
