S = dict(cc="DE", fam="Consumption", family_name="5121 TabSt, AlkSt (beyond the pilot's USt and EnergieSt)",
doc=r'''# Germany 2025: tobacco and spirits duties (5121), added to the pilot's Umsatzsteuer and Energiesteuer

Sources: gesetze-im-internet.de as archived by the Internet Archive in 2025 (`de/law/tabstg_2.html` capture
2025-05-30, `alkstg_2.html` 2025-02-15, `bierstg_2.html` 2025-01-23; sha256 in `law/SHA256SUMS`).
* **TabStG § 2 (1) Nr. 1 lit. d**: cigarettes "für den Zeitraum vom 1. Januar 2025 bis zum 31. Dezember 2025 11,71 Cent
  je Stück und 19,84 Prozent des Kleinverkaufspreises, mindestens jedoch 24,163 Cent je Stück abzüglich der
  Umsatzsteuer des Kleinverkaufspreises der zu versteuernden Zigarette".
* **AlkStG § 2 (1)**: "Sie beträgt für einen Hektoliter reinen Alkohols (hl A) ... als Regelsatz 1 303 Euro."
* **BierStG § 2 (1)**: beer is taxed by degree Plato classes (not modelled: kernel input missing).
The pilot's VAT (`DeGlobal.ust`, UStG § 12) is the VAT deducted inside the cigarette minimum.
''',
lean=r'''
def cigarettes : ExciseRate :=
  { good := .cigarettes, name := "Tabaksteuer (Zigaretten)", perUnitNum := 1171, perUnitDen := 10000, adValoremBp := 1984,
    statute := "TabStG § 2 (1) Nr. 1 lit. d: 11,71 Cent/Stück + 19,84 % des Kleinverkaufspreises, mindestens 24,163 Cent/Stück abzüglich der USt" }

/-- § 2 (1) Nr. 1 lit. d: the larger of the mixed duty and 24,163 Cent per stick less the VAT in the retail price. -/
def cigaretteDuty (s : Spend) : Int :=
  max (cigarettes.specific s + cigarettes.adValorem s) (divR .down (s.quantity * 24163) (100000 * 1000) - DeGlobal.ust.embedded s)

def spirits : ExciseRate :=
  { good := .spirits, name := "Alkoholsteuer", perUnitNum := 1303, perUnitDen := 100, onPureAlcohol := true,
    statute := "AlkStG § 2 (1): 1 303 EUR / hl A (Regelsatz)" }

def charges (xs : List Spend) : List Charge :=
  (xs.filter (·.good == .cigarettes)).map (fun s => charge .excise cigarettes.name s.quantity id (fun _ => cigaretteDuty s)
      (event := "cigarettes") (bearer := .consumer) (statute := cigarettes.statute))
  ++ (xs.filter (·.good == .spirits)).map (fun s => charge .excise spirits.name s.quantity id (fun _ => spirits.duty s)
      (event := "spirits") (bearer := .consumer) (statute := spirits.statute))
''',
families=[("5121 TabSt, AlkSt", [".excise"], "charges g.consumption")],
notes=["DE 5121 (Europe builder): TabStG § 2 and AlkStG § 2 as archived 2025"],
unsupported=[("g.consumption.any (fun s => s.good == .beer)", "Biersteuer (BierStG § 2: by degree Plato) not modelled: the basket has no Plato field"),
  ("g.consumption.any (fun s => s.good == .wine)", "still wine bears no excise; Schaumweinsteuer and Zwischenerzeugnisse not modelled"),
  ("g.consumption.any (fun s => s.good == .tobaccoOther)", "cigars, fine-cut and other tobacco not modelled")],
guards=["cigaretteDuty { good := .cigarettes, amount := 400, quantity := 1000000 } == 117 + 79",
        "-- at 0,30 EUR a stick the minimum binds: 241 - 47 (VAT in 300 EUR) = 194 > 117 + 59",
        "cigaretteDuty { good := .cigarettes, amount := 300, quantity := 1000000 } == 194",
        "spirits.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 521"],
taxes=[{"oecd": "5121", "tax": "Tabaksteuer (cigarettes)", "statute": "TabStG § 2 (1) Nr. 1 lit. d, (2)", "dated": "Internet Archive 2025-05-30 of gesetze-im-internet.de", "grade": "A", "kernel_parts": ["ExciseRate", "custom minimum less VAT"], "unsupported": ["cigars, fine-cut, heated tobacco"]},
 {"oecd": "5121", "tax": "Alkoholsteuer (spirits)", "statute": "AlkStG § 2 (1) (1 303 €/hl A)", "dated": "Internet Archive 2025-02-15", "grade": "A", "kernel_parts": ["ExciseRate (pure alcohol)"], "unsupported": ["§ 2 (2) reduced rates for small distilleries", "Alkopopsteuer"]},
 {"oecd": "5121", "tax": "Biersteuer", "statute": "BierStG § 2 (1)", "dated": "Internet Archive 2025-01-23", "grade": "A", "status": "not modelled (kernel input: degree Plato)", "kernel_parts": [], "unsupported": ["per degree Plato (KERNEL_REQUESTS)"]}])
