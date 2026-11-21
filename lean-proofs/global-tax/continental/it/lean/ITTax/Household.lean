import ITTax.Local
import ITTax.Auu

/-!
# The contract household (`~/cmp/shared/CONTRACT.md`) under Italian law, 2025, resident in Roma Capitale

* Each adult is a taxpayer (individual taxation). Household investment income, rent, pension-fund contributions and
  gifts are split equally between two adults (`half1`/`half2`, contract convention).
* Wages are gross pay of an ordinary private-sector employee; INPS employee contributions are deducted from them to
  give the reddito di lavoro dipendente (TUIR art. 51 c. 2 a)). Self-employment income is taken as net income under
  the ordinary regime, with no INPS contributions (not modelled). Pensions: art. 13 c. 3.
* Interest, dividends and capital gains: 26 % imposta sostitutiva (DL 66/2014 art. 3), outside IRPEF and the
  addizionali (reported as a surtax). Government-bond interest (12,5 %) is not distinguished.
* Rent: the landlord chooses cedolare secca (21 % of the canone, D.Lgs. 23/2011 art. 3) or IRPEF on 95 % of it;
  `--rent=cedolare|irpef` forces a choice; the default takes whichever leaves the household more.
* Spouse: "a carico" when married and the other's reddito complessivo (with cedolare income) is at most 2.840,51;
  children aged 21-29 are taken as dependants with no income; their art. 12 c) detrazione is split 50/50 between
  married parents, or 100 % to the parent whose spouse is dependent.
* AUU: children under 21; ISEE from current incomes, no assets (see `ITTax.Auu`).
-/

namespace ITTax
open TaxKernel Lean

inductive RentMode | cedolare | irpef
  deriving Repr, DecidableEq, Inhabited

structure Result where
  people : List (Person × Irpef × Int × Int × Int)  -- person, irpef, regionale, comunale, inps
  cedolareTax : Int
  capitalTax : Int
  auu : Int
  isee : Int
  rent : RentMode
  deriving Inhabited

def Result.incomeTax (r : Result) : Int :=
  r.people.foldl (fun a (_, t, _, _, _) => a + t.netta - t.ti - t.cuneo) 0
def Result.local (r : Result) : Int := r.people.foldl (fun a (_, _, g, c, _) => a + g + c) 0
def Result.social (r : Result) : Int := r.people.foldl (fun a (_, _, _, _, s) => a + s) 0
def Result.net (r : Result) (gross : Int) : Int :=
  gross - r.incomeTax - r.cedolareTax - r.capitalTax - r.local - r.social + r.auu

/-- Split a household total over `n` adults (1 or 2), cents. -/
def share (n : Nat) (i : Nat) (x : Int) : Int := if n < 2 then x else if i = 0 then half1 x else half2 x

def compute (c : Canon) (mode : RentMode) (oecd : Bool := false) (em : Bool := false) : Result :=
  let n := c.adults.length
  let y := c.year
  let rentC := eur c.rentalIncome
  let base (i : Nat) (a : Adult) : Person :=
    let w := eur a.wages
    let rentI := share n i rentC
    { wages := w, inps := inpsY y oecd w em, pension := eur a.pension, selfEmp := eur a.selfEmployment,
      rentIrpef := if mode = .irpef then divR .halfUp (rentI * rentIrpefShare) BP else 0,
      rentCed := if mode = .cedolare then rentI else 0,
      pensionContrib := share n i (eur c.pensionContributions), charity := share n i (eur c.charitable),
      kidsDependent := c.children.length,
      -- art. 12 c. 1 c): 21-29 from 2025 (L. 207/2024 c. 2); 21 and over in 2022-2024 (text in force 2022-06-30)
      kids2129 := (c.children.filter fun k => 21 ≤ k.age ∧ (k.age < 30 ∨ y < 2025)).length,
      year := y, oecd, kidsOld := if y = 2022 then c.children.map (·.age) else [] }
  let ps0 := c.adults.zipIdx.map fun (a, i) => base i a
  let rrOf (p : Person) : Int := (p.irpef).redditoRif
  let ps := match ps0 with
    | [p] => [{ p with kids2129Share := 100 }]
    | [p, q] =>
      let pDep := c.married ∧ rrOf p ≤ caricoLimit
      let qDep := c.married ∧ rrOf q ≤ caricoLimit
      -- if both qualify (both near zero), the first claims the second
      let pClaims := qDep
      let qClaims := pDep ∧ !qDep
      let pShare : Int := if !c.married then 100 else if pClaims then 100 else if qClaims then 0 else 50
      [{ p with spouseDependent := pClaims, kids2129Share := pShare },
       { q with spouseDependent := qClaims, kids2129Share := (if c.married then 100 - pShare else 0) }]
    | l => l
  let people := ps.map fun p =>
    let t := p.irpef
    (p, t, t.regionale y oecd, t.comunale y, p.inps)
  let ced := divR .halfUp (rentC * cedolare) BP
  let cap := divR .halfUp (eur (c.interest + c.dividends + c.capitalGains) * sostitutiva) BP
  -- AUU
  let ages := c.children.map (·.age)
  let minors := ages.any (· < 18)
  let under3 := ages.any (· < 3)
  let allWork := c.adults.all fun a => a.wages + a.selfEmployment > 0
  let magB : Int := if minors ∧ (allWork ∨ n = 1) then (if under3 then 30 else 20) else 0
  let iseeAdults := people.map fun (p, t, _, _, _) => (t.redditoRif, t.rld, p.pension)
  let i := isee iseeAdults c.children.length magB
  let bothWork := n = 2 ∧ allWork
  let a := auuYear ages i bothWork y oecd
  { people, cedolareTax := if mode = .cedolare then ced else 0, capitalTax := cap, auu := a, isee := i,
    rent := mode }

/-- The rent choice: forced by `--rent=...`, else the one that leaves the household more. -/
def computeBest (args : List String) (c : Canon) : Result :=
  let o := args.contains "--oecd"
  let e := args.contains "--euromod"
  if args.contains "--rent=cedolare" then compute c .cedolare o e
  else if args.contains "--rent=irpef" then compute c .irpef o e
  else if c.rentalIncome = 0 then compute c .cedolare o e
  else
    let a := compute c .cedolare o e
    let b := compute c .irpef o e
    let g := eur c.gross
    if b.net g > a.net g then b else a

/-- Output in cents (`toJsonCents` prints euros with two decimals). -/
def out (args : List String) (c : Canon) : Out :=
  let r := computeBest args c
  let sumOf (f : Irpef → Int) : Int := r.people.foldl (fun a (_, t, _, _, _) => a + f t) 0
  let per := r.people.zipIdx.map fun ((_, t, g, cm, s), i) =>
    (s!"adult{i+1}", Json.mkObj [("redditoComplessivo", Json.num ⟨t.redditoComplessivo, 2⟩),
      ("imponibile", Json.num ⟨t.imponibile, 2⟩), ("impostaLorda", Json.num ⟨t.lorda, 2⟩),
      ("detrazioniArt13", Json.num ⟨t.d13, 2⟩), ("detrazioniArt12", Json.num ⟨t.d12, 2⟩),
      ("ulterioreDetrazione", Json.num ⟨t.ulteriore, 2⟩), ("detrazioneErogazioni", Json.num ⟨t.dCharity, 2⟩),
      ("impostaNetta", Json.num ⟨t.netta, 2⟩), ("trattamentoIntegrativo", Json.num ⟨t.ti, 2⟩),
      ("sommaCuneo", Json.num ⟨t.cuneo, 2⟩), ("addizionaleRegionale", Json.num ⟨g, 2⟩),
      ("addizionaleComunale", Json.num ⟨cm, 2⟩), ("inps", Json.num ⟨s, 2⟩)])
  Out.make c "IT" "EUR" r.incomeTax
    (surtaxes := [("cedolareSecca", r.cedolareTax), ("impostaSostitutiva", r.capitalTax)])
    (localIncomeTax := r.local) (employeeSocial := r.social) (benefits := r.auu)
    (detail := [("taxableIncome", Json.num ⟨sumOf (·.imponibile), 2⟩),
      ("impostaLorda", Json.num ⟨sumOf (·.lorda), 2⟩),
      ("trattamentoIntegrativo", Json.num ⟨sumOf (·.ti), 2⟩), ("sommaCuneo", Json.num ⟨sumOf (·.cuneo), 2⟩),
      ("isee", Json.num ⟨r.isee, 2⟩),
      ("rent", Json.str (if r.rent = .cedolare then "cedolare secca" else "IRPEF")),
      ("region", Json.str "Lazio / Roma Capitale"), ("units", Json.str "money lines in euros with cents")] ++ per)
    (unsupported := ["INPS contributions on self-employment (gestione separata/artigiani) not modelled",
      "regime forfettario not applied by default (see ITTax.Forfettario)",
      "ISEE without assets and on current-year income (OECD convention)",
      "government-bond interest at 12.5% not distinguished",
      "detrazioni for expenses other than gifts (medical, mortgage interest, renovation) not modelled"] ++
      (if c.year < 2025 then [s!"tax year {c.year}: INPS band and massimale derived from the 2025 values by the ISTAT index of DL 384/1992 art. 3-ter (INPS circulars not retrieved); exemption points from L. 234/2021 art. 1 c. 121, L. 197/2022 art. 1 c. 281 (normattiva Akoma Ntoso texts), DL 115/2022 art. 20 and DL 48/2023 art. 39; pay taken as 13 equal instalments",
        "assegno unico transitional maggiorazione (D.Lgs. 230/2021 art. 5, ISEE <= 25.000 with ANF received in 2021) not modelled"] ++
        (if c.year = 2022 then ["2022: ANF and assegno art. 65 L. 448/1998 for January-February 2022 not modelled (tables not retrieved)",
          "2022 Lazio: the 50.000 thresholds for three or more children, disabled children and disabled over-70s (L.R. 7/2022) not modelled"] else [])
       else []) ++
      (if args.contains "--oecd" then ["--oecd: OECD Taxing Wages conventions (2022: 0,8 points all year, assegno unico 12 months, no January-February child detrazioni; 2024-2025: no Lazio reliefs)"] else []) ++
      (if args.contains "--euromod" then ["--euromod (EUROMOD CR Italy 2022-2025, s. 2.2.1 and the employee SIC table notes): the IVS decontribution as EUROMOD's yearly average (2022: 1,4 points; 2023: 5 / 4 points) on the whole year's pay; FYA is on in the IT baseline (CR s. 2.4: 'The default for the baselines is on'), so no 30-June re-timing of other within-year changes"] else []) ++
      (if args.contains "--eurostat" then ["--eurostat (Eurostat earn_net ESMS 3.4, sha256 89ab2734...): no IRPEF, addizionale or INPS parameter changes within 2025, and the assegno unico is the same for every age 6-11, so the flag changes nothing in 2025" ++ (if c.year < 2025 then "; for tax years before 2025 the within-year changes (DL 115/2022 art. 20, DL 48/2023 art. 39, the March 2022 art. 12 change) are not re-timed to 1 January" else "")] else []))

/-- An `Out` whose money fields are cents, as a JSON line in euros with two decimals. -/
def toJsonCents (o : Out) : Json :=
  let j (x : Int) : Json := Json.num ⟨x, 2⟩
  Json.mkObj [("id", Json.str o.id), ("country", Json.str o.country), ("currency", Json.str o.currency),
    ("incomeTax", j o.incomeTax), ("surtaxes", Json.mkObj (o.surtaxes.map fun (k, v) => (k, j v))),
    ("localIncomeTax", j o.localIncomeTax), ("employeeSocial", j o.employeeSocial), ("benefits", j o.benefits),
    ("detail", Json.mkObj o.detail), ("unsupported", Json.arr (o.unsupported.map Json.str).toArray)]

/-- The kernel's `Country` (whole euros, half up), for `tax20`. -/
def toEuro (o : Out) : Out :=
  let e (x : Int) : Int := divR .halfUp x 100
  { o with incomeTax := e o.incomeTax, surtaxes := o.surtaxes.map (fun (k, v) => (k, e v)),
           localIncomeTax := e o.localIncomeTax, employeeSocial := e o.employeeSocial, benefits := e o.benefits }

def country : Country :=
  { code := "IT", name := "Italy (IRPEF + Lazio + Roma Capitale)", currency := "EUR", year := "2025",
    compute := fun c => toEuro (out [] c), computeWith := fun args c => toEuro (out args c) }

end ITTax
