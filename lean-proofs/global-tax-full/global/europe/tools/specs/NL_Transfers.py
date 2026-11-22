S = dict(cc="NL", fam="Transfers",
doc=r'''# Netherlands 2025: erfbelasting (4300)

Source: Successiewet 1956 (BWBR0002226), wetten.overheid.nl geldend 2025 (`nl/law/sw1956_g2025.html`).
* **art. 24 lid 1** tarief: "Gedeelte van de belaste verkrijging tussen € 0 | € 154.197 | 10% | 30%"; "€ 154.197 en
  hoger | 20% | 40%" (column I "indien verkregen door partner of afstammelingen in de rechte lijn", II "in overige
  gevallen"); note 1: "Voor afstammelingen in de tweede of verdere graad bedraagt de belasting ... vermeerderd met 80%
  daarvan".
* **art. 32 lid 1 onderdeel 4°** (vrijstellingen erfbelasting): "a. partner: € 804.698"; "c. kinderen ...: € 25.490";
  "d. kleinkinderen: € 25.490"; "e. ouders: € 60.359"; "f. overige verkrijgers: € 2.690".
Gifts (schenkbelasting, art. 33 exemptions) are not modelled.
''',
lean=r'''
def tariefI : Schedule := Schedule.ofList [(0, 1000), (154197, 2000)]
def tariefKleinkind : Schedule := Schedule.ofList [(0, 1800), (154197, 3600)]
def tariefII : Schedule := Schedule.ofList [(0, 3000), (154197, 4000)]

/-- art. 24, 32: 0 partner, 1 child, 2 grandchild (+80 %), 3 parent (tarief II), 4 others (tarief II). -/
def classIdx (r : Relation) : Nat :=
  match r with
  | .spouse => 0 | .child => 1 | .grandchild => 2 | .parent => 3 | _ => 4

def erfbelasting : InheritanceTax :=
  { name := "Erfbelasting", classOf := classIdx,
    classes := [{ allowance := 804698, sched := tariefI }, { allowance := 25490, sched := tariefI },
                { allowance := 25490, sched := tariefKleinkind }, { allowance := 60359, sched := tariefII },
                { allowance := 2690, sched := tariefII }] }

def charges (g : CanonGlobal) : List Charge :=
  erfbelasting.charges (g.transfers.filter fun t => t.kind == .inheritance && t.relation != .charity)
    "Successiewet 1956 art. 24 lid 1, art. 32 lid 1 onderdeel 4°"
''',
families=[("4300 erfbelasting", [".estate"], "charges g")],
notes=["NL 4300: Successiewet 1956, geldend 2025"],
unsupported=[("g.transfers.any (·.kind == .gift)", "schenkbelasting (art. 33 exemptions) not modelled"),
  ("g.transfers.any (·.relation == .charity)", "ANBI exemption (art. 32 lid 1 3°) not read: charities not charged"),
  ("g.transfers.any (fun t => t.homeValue ≠ 0 || t.businessValue ≠ 0)", "bedrijfsopvolgingsregeling (art. 35b) not modelled")],
guards=["erfbelasting.tax { kind := .inheritance, value := 200000, relation := .child } == 19482",
        "erfbelasting.tax { kind := .inheritance, value := 800000, relation := .spouse } == 0",
        "erfbelasting.tax { kind := .inheritance, value := 100000, relation := .grandchild } == 13411",
        "erfbelasting.tax { kind := .inheritance, value := 100000, relation := .unrelated } == 29193"],
taxes=[{"oecd": "4300", "tax": "Erfbelasting", "statute": "Successiewet 1956 art. 24 lid 1, art. 32 lid 1 onderdeel 4°", "dated": "wetten.overheid.nl geldend 2025", "grade": "A", "kernel_parts": ["InheritanceTax"], "unsupported": ["schenkbelasting", "ANBI", "bedrijfsopvolgingsregeling", "partner pension deduction"]}])
