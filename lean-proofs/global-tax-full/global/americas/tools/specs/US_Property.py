S = dict(cc="US", fam="Property",
doc=r'''# United States 2025: federal estate and gift tax (4300); no federal wealth tax; California: no estate tax

Sources: 26 U.S.C. (Cornell LII, fetched 2026-11-21; `us/law/usc26_2001.html` ...): §§ 2001, 2010, 2055, 2056, 2501,
2502, 2503, 2505, 2522, 2523; Rev. Proc. 2024-40 (irs.gov, `us/law/rp-24-40.pdf`) § 3.41 "For an estate of any
decedent dying in calendar year 2025, the basic exclusion amount is $13,990,000"; § 3.43 (1) "the first $19,000 of
gifts to any person ... are not included in the total amount of taxable gifts". The $15,000,000 of Pub. L. 119-21
§ 70106 applies "to estates of decedents dying and gifts made after December 31, 2025": not in 2025. Grade A.
* **§ 2001 (c)** rate schedule: "Not over $10,000: 18 percent ... Over $1,000,000: $345,800, plus 40 percent of the
  excess". **§ 2001 (b)**: tax = tentative tax on (taxable estate + adjusted taxable gifts) less the gift tax payable on
  those gifts; **§ 2010 (a), (c)**: credit = the tentative tax on the basic exclusion amount. Hence
  estate tax = max(0, T(E + G) − max(T(G), T(BEA))) with T the § 2001 (c) schedule, G the adjusted taxable gifts.
* **§§ 2502 (a), 2505**: gift tax for the period = T(prior + current) − T(prior), less the unused applicable credit:
  = max(0, T(P + C) − max(T(P), T(BEA))). **§ 2503 (b)** annual exclusion $19,000 per donee; **§§ 2056, 2523** marital
  deduction (spouse), **§§ 2055, 2522** charitable deduction (charity): nothing taxable.
* Reading of the line: the entity's `transfers` are the estate passing (inheritances: one decedent, the estate is the
  sum of the inheritances to recipients other than a spouse or charity; adjusted taxable gifts = the `prior` gifts of
  the first inheritance record) and the donor's gifts (each gift with its own `prior` taxable gifts). The tax is
  borne by the estate or the donor. GST tax (§ 2601) on skips to grandchildren and the non-citizen spouse rules are not
  modelled (listed).''',
lean=r'''
/-- § 2001 (c): (lower bound, tax at the lower bound, percent above it). -/
def brackets : List (Int × Int × Int) :=
  [(0, 0, 18), (10000, 1800, 20), (20000, 3800, 22), (40000, 8200, 24), (60000, 13000, 26), (80000, 18200, 28),
   (100000, 23800, 30), (150000, 38800, 32), (250000, 70800, 34), (500000, 155800, 37), (750000, 248300, 39),
   (1000000, 345800, 40)]

/-- Tentative tax of § 2001 (c) on an amount (dollars, down). -/
def tentative (x : Int) : Int :=
  let x := pos x
  let (lo, base, pct) := brackets.foldl (fun acc b => if x > b.1 then b else acc) (0, 0, 18)
  base + divR .down (pct * (x - lo)) 100

/-- Basic exclusion amount for 2025 (Rev. Proc. 2024-40 § 3.41) and the annual gift exclusion (§ 3.43 (1)). -/
def bea : Int := 13990000
def annualExclusion : Int := 19000

/-- Tax on `x` after `prior` taxable transfers, with the unified credit (§§ 2001 (b), 2010, 2502, 2505). -/
def unified (prior x : Int) : Int := pos (tentative (pos prior + pos x) - max (tentative (pos prior)) (tentative bea))

def exemptRel (r : Relation) : Bool := r == .spouse || r == .charity

def estateTax (ts : List Transfer) : Int :=
  let inh := ts.filter fun t => t.kind == .inheritance
  let estate := isum ((inh.filter fun t => !exemptRel t.relation).map (·.statutoryValue))
  let gifts := match inh.head? with | some t => isum (t.prior.map (·.1)) | none => 0
  unified gifts estate

def giftTax (t : Transfer) : Int :=
  if exemptRel t.relation then 0 else unified (isum (t.prior.map (·.1))) (pos (t.statutoryValue - annualExclusion))

def estateF : Family :=
  { name := "4300 federal estate and gift tax", covers := [.estate],
    run := fun _ g _ =>
      let inh := g.transfers.filter fun t => t.kind == .inheritance
      (if inh.isEmpty then [] else
        [charge .estate "Federal estate tax" (isum (inh.map (·.statutoryValue))) id (fun _ => estateTax g.transfers)
          (event := "estate") (statute := "26 U.S.C. §§ 2001 (b), (c), 2010 (BEA $13,990,000, Rev. Proc. 2024-40 § 3.41), 2055, 2056")])
      ++ (g.transfers.zipIdx.filter fun (t, _) => t.kind == .gift).map fun (t, i) =>
        charge .estate "Federal gift tax" t.statutoryValue id (fun _ => giftTax t) (event := s!"gift {i + 1}")
          (statute := "26 U.S.C. §§ 2502 (a), 2503 (b) ($19,000, Rev. Proc. 2024-40 § 3.43), 2505, 2522, 2523") }
''',
families="[estateF]",
absent=[["wealth", "no federal or California net wealth tax (26 U.S.C. has none; California levies none)"]],
unsupported_expr='''when (g.transfers.any fun t => t.relation == .grandchild) "generation-skipping transfer tax (26 U.S.C. § 2601) on transfers to grandchildren not modelled"
  ++ when (g.transfers.any fun t => t.relation == .spouse) "marital deduction read as unlimited (spouse a U.S. citizen; the $190,000 non-citizen spouse exclusion not modelled)"
  ++ when ((g.transfers.filter fun t => t.kind == .inheritance).length > 1) "all inheritances of the line read as one estate; adjusted taxable gifts from the first record's prior gifts"
  ++ when (g.transfers.any fun t => !t.prior.isEmpty) "prior gifts read as taxable gifts after annual exclusions and deductions"''',
guards=["tentative 10000 == 1800", "tentative 1000000 == 345800", "tentative 13990000 == 5541800",
        "unified 0 13990000 == 0", "unified 0 15000000 == 404000",
        "-- prior gifts using the exclusion: the estate pays 40 % on everything above the exclusion",
        "unified 5000000 10000000 == 404000",
        "giftTax { kind := .gift, value := 1000000, relation := .child } == 0",
        "giftTax { kind := .gift, value := 1000000, relation := .child, prior := [(13990000, 2)] } == 392400",
        "estateTax [{ kind := .inheritance, value := 20000000, relation := .child }, { kind := .inheritance, value := 9000000, relation := .spouse }] == 2404000"],
taxes=[dict(oecd="4300", tax="Federal estate and gift tax", statute="26 U.S.C. §§ 2001, 2010, 2055, 2056, 2501-2505, 2522, 2523; Rev. Proc. 2024-40 §§ 3.41, 3.43", dated="U.S. Code (Cornell LII, with the Pub. L. 119-21 note: $15M only after 2025); Rev. Proc. 2024-40 for 2025", grade="A", package="P6", kernel_parts=["charge"], unsupported=["GST tax", "non-citizen spouse", "state death taxes (none in California)"]),
 dict(oecd="4200", tax="Net wealth tax", statute="none in 26 U.S.C. or California law", grade="A", status="not levied", package="P6", kernel_parts=["Absent"])])

# ---- gap pass 2026-11-21: 5200 California vehicle license fee (R&TC §§ 10751-10753.2) ----
S['imports'] = sorted(set((S.get('imports') or []) + ['TaxKernel.Global2']))
S['lean'] = (S.get('lean') or '') + '\n\n' + "/-! ## 5200 California vehicle license fee (gap pass 2026-11-21; kernel `VehicleTax`) -/\n/-- R&TC § 10752 (a) (3): 0.65 % of the market value for registrations due on and after 1 July 2011; § 10753.2 (c): the\nmarket value is the cost class's midpoint x 100 % in the first year, 90, 80, 70, 60, 50, 40, 30, 25, 20 % in the 2nd-10th,\n15 % from the 11th; minimum tax $1. -/\ndef caVlf : VehicleTax :=\n  { name := \"California vehicle license fee\", parts := [(.value, { steps := [(0, 65)], den := 10000 })],\n    ageFactors := [(0, 10000), (1, 9000), (2, 8000), (3, 7000), (4, 6000), (5, 5000), (6, 4000), (7, 3000), (8, 2500),\n                   (9, 2000), (10, 1500)],\n    minAmount := 1, proRata := false, level := .state,\n    statute := \"Cal. R&TC § 10751 (fee for the privilege of operating a registered vehicle), § 10752 (a) (3) (0.65 % of market value, registrations due on and after 1 July 2011), § 10753 (a) (cost price to the purchaser), § 10753.2 (c) (depreciation schedule by registration year; minimum $1)\" }\n\ndef vlfF : Family := vehicleTaxFamily \"California vehicle license fee\" [caVlf]\n"
S['families'] = S['families'].rstrip()[:-1] + ', vlfF]'
S['unsupported_expr'] = '(' + S['unsupported_expr'] + ') ++ ' + "when (!g.vehicles.isEmpty) \"California vehicle license fee: the vehicle's value is read as its cost price to the owner (R&TC § 10753) and its age from the first registration year (the schedule restarts when a used vehicle is sold to a new owner, § 10753.2 (c)); the $200 cost class's midpoint (§ 10753.2 (b)) not applied (at most $0.65 a year); registration fees (Veh. Code § 9250 ff.) and the transportation improvement fee (R&TC § 11052, indexed) not computed (grade C)\" ++ vehicleTaxUnknown \"California vehicle license fee\" [caVlf] g"
S['taxes'] = S['taxes'] + [{"oecd": "5200", "tax": "Vehicle license fee (California)", "statute": "Cal. R&TC §§ 10751, 10752 (a) (3) (0.65 % of market value), 10753 (a), 10753.2 (c) (100/90/80/70/60/50/40/30/25/20 %, then 15 %; minimum $1)", "dated": "lexifina/united-states-california-law rtc/10751.md, 10752.md (amended by Stats. 2011, Ch. 35, effective 30 June 2011), 10753.md, 10753.2.md (official source leginfo.legislature.ca.gov as recorded in the repository); in force throughout 2025; gap pass 2026-11-21", "grade": "A", "status": "modelled", "package": "P7", "kernel_parts": ["VehicleTax", "vehicleTaxFamily"], "unsupported": ["cost-class midpoint not applied (at most $0.65)", "age from first registration (used-vehicle restart not read)", "registration fees (Veh. Code § 9250 ff.) and the transportation improvement fee (R&TC § 11052) not computed"], "gap_pass": "2026-11-21 approach 6 (5200 vehicles; OECD Interpretative Guide §12: vehicle licence fees are taxes)"}]
S['guards'] = (S.get('guards') or []) + ["-- $40,000 car in its second registration year (age 1): 40 000 x 0.65 % = 260; x 90 % = 234", "caVlf.amount 2025 { value := 40000, firstRegYear := 2024 } == 234", "-- the same car in its 13th year (15 %): 260 x 15 % = 39", "caVlf.amount 2025 { value := 40000, firstRegYear := 2013 } == 39", "-- a $100 vehicle in its 13th year: 0.65 x 15 % rounds to 0, the minimum $1 applies", "caVlf.amount 2025 { value := 100, firstRegYear := 2013 } == 1"]
S['doc'] = S['doc'] + '\n\n' + "**5200 (gap pass)**: California vehicle license fee, R&TC § 10752 (a) (3) 0.65 % of the market value; § 10753.2 (c) depreciation by registration year (100 % ... 15 %), minimum $1 (a state tax, kernel `VehicleTax` with `ageFactors`). OECD Interpretative Guide §12/§14: vehicle licence fees are taxes (5200)."
