S = dict(cc="CH", fam="Capital",
doc=r'''# Switzerland 2025: private capital gains (1100) are exempt from the federal income tax

Source: DBG SR 642.11, fedlex consolidation 2025-01-01 (`ch/law/dbg_20250101.html`).
* **DBG Art. 16 (3)**: "Die Kapitalgewinne aus der Veräusserung von Privatvermögen sind steuerfrei."
Gains on private real estate are taxed by the cantons (Grundstückgewinnsteuer, StHG Art. 12): not modelled.
''',
lean=r'''
def charges (g : CanonGlobal) : List Charge :=
  if g.entity == .company || g.disposals.isEmpty then [] else
  let movable := g.disposals.filter fun d => !d.kind.isRealEstate
  if movable.isEmpty then [] else
  [charge .pit "Direkte Bundessteuer auf private Kapitalgewinne" (isum (movable.map (·.gain))) (fun _ => 0) (fun _ => 0)
     (event := "disposals (private wealth)") (statute := "DBG Art. 16 (3): steuerfrei")]
''',
families=[("1100 private Kapitalgewinne (steuerfrei)", [], "charges g")],
notes=["CH 1100: private gains exempt federally (DBG Art. 16 (3))"],
unsupported=[("g.disposals.any (fun d => d.kind.isRealEstate)", "Grundstückgewinnsteuer (cantonal, StHG Art. 12; Zürich StG §§ 216 ff.) not modelled"),
  ("!g.disposals.isEmpty", "professional securities trading (gains as self-employment income) not considered")],
guards=["(charges { id := \"x\", household := { id := \"x\" }, disposals := [{ kind := .listedShares, proceeds := 5000, cost := 1000 }] }).map (·.due) == [0]"],
taxes=[{"oecd": "1100", "tax": "Direkte Bundessteuer on private capital gains (exempt)", "statute": "DBG Art. 16 (3)", "dated": "fedlex 2025-01-01", "grade": "A", "kernel_parts": ["charge (zero, cited)"], "unsupported": ["cantonal Grundstückgewinnsteuer", "quasi-professional trading"]}])
