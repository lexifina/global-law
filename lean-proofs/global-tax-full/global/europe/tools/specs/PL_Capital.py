S = dict(cc="PL", fam="Capital",
doc=r'''# Poland 2025: gains of individuals on securities and real estate (1100)

Source: ustawa o podatku dochodowym od osób fizycznych, tekst jednolity Dz.U. 2025 poz. 163 (Sejm ELI API,
`pl/law/pit_tj2025.pdf`, sha256 in `law/SHA256SUMS`).
* **art. 30b ust. 1**: from gains "z odpłatnego zbycia papierów wartościowych ... z odpłatnego zbycia udziałów (akcji)
  ... – podatek dochodowy wynosi 19 % uzyskanego dochodu".
* **art. 30e ust. 1**: from the sale of real estate "określonych w art. 10 ust. 1 pkt 8 lit. a–c podatek dochodowy
  wynosi 19 % podstawy obliczenia podatku"; **art. 10 ust. 1 pkt 8**: only a sale "przed upływem pięciu lat, licząc od
  końca roku kalendarzowego, w którym nastąpiło nabycie" is a source of income: for a 2025 sale, property acquired in
  2020 or later.
''',
lean=r'''
def isSecurity (d : Disposal) : Bool := d.kind.isShares || d.kind == .bonds

/-- art. 10 ust. 1 pkt 8: a 2025 sale is taxable when acquired in 2020 or later (five years from the end of the year of
acquisition); without an acquisition year, a holding under 60 months is taken as taxable. -/
def withinFiveYears (year : Nat) (d : Disposal) : Bool :=
  if d.acquiredYear == 0 then decide (d.heldMonths < 60) else decide (year ≤ d.acquiredYear + 5)

def securitiesGain (ds : List Disposal) : Int := pos (isum ((ds.filter isSecurity).map (·.gain)))
def realEstateGain (year : Nat) (ds : List Disposal) : Int :=
  isum ((ds.filter fun d => d.kind.isRealEstate && withinFiveYears year d).map (fun d => pos d.gain))

def tax19 (x : Int) : Int := divR .down (1900 * pos x) BP

def charges (g : CanonGlobal) : List Charge :=
  if g.entity == .company || g.disposals.isEmpty then [] else
  [charge .pit "PIT 19 % od zbycia papierów wartościowych (art. 30b)" (isum ((g.disposals.filter isSecurity).map (·.gain)))
     (fun _ => securitiesGain g.disposals) tax19 (event := "securities") (statute := "ustawa o PIT art. 30b ust. 1"),
   charge .pit "PIT 19 % od zbycia nieruchomości (art. 30e)" (isum ((g.disposals.filter (·.kind.isRealEstate)).map (·.gain)))
     (fun _ => realEstateGain g.year g.disposals) tax19 (event := "real estate") (statute := "ustawa o PIT art. 10 ust. 1 pkt 8, art. 30e ust. 1")]
''',
families=[("1100 zyski kapitałowe i zbycie nieruchomości", [], "charges g")],
notes=["PL 1100: art. 30b and 30e flat 19 %"],
unsupported=[("g.disposals.any (fun d => d.kind.isRealEstate && d.mainHome)", "ulga mieszkaniowa (art. 21 ust. 1 pkt 131: reinvestment in housing) not modelled"),
  ("g.disposals.any (fun d => d.kind.isRealEstate)", "art. 30e losses are not offset against other sales (each sale floored at zero)")],
guards=["tax19 10000 == 1900",
        "realEstateGain 2025 [{ kind := .home, proceeds := 500000, cost := 400000, acquiredYear := 2019 }] == 0",
        "realEstateGain 2025 [{ kind := .home, proceeds := 500000, cost := 400000, acquiredYear := 2020 }] == 100000",
        "securitiesGain [{ kind := .listedShares, proceeds := 2000, cost := 5000 }, { kind := .listedShares, proceeds := 9000, cost := 1000 }] == 5000"],
taxes=[{"oecd": "1100", "tax": "PIT on gains from securities (art. 30b)", "statute": "ustawa o PIT art. 30b ust. 1", "dated": "t.j. Dz.U. 2025 poz. 163", "grade": "A", "kernel_parts": ["charge (flat 19 %)"], "unsupported": ["losses of earlier years (art. 9 ust. 3)"]},
 {"oecd": "1100", "tax": "PIT on real-estate sales (art. 30e)", "statute": "ustawa o PIT art. 10 ust. 1 pkt 8, art. 30e", "dated": "t.j. Dz.U. 2025 poz. 163", "grade": "A", "kernel_parts": ["charge (flat 19 %)", "five-year rule"], "unsupported": ["ulga mieszkaniowa", "inherited property holding period"]}])
