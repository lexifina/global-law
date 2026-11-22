S = dict(cc="US", fam="Transfers",
doc=r'''# United States 2025 (Los Angeles): property tax (4100) and documentary transfer taxes incl. Measure ULA (4400)

Sources (`us/law/`):
* County of Los Angeles, Board of Supervisors, FY 2025-26 Tax Rate Resolution (auditor.lacounty.gov, OCR
  `la_fy25-26_tax_rate_resolution.ocr.txt`): "COUNTYWIDE ... Countywide General Tax Levy 1.000000" (percent of full
  value): the 1 % maximum of Cal. Const. art. XIII A § 1 (a) on the base-year value. The voter-approved debt-service
  rates are listed per district (LAUSD, LACCD, MWD, City of LA bonds) and were not summed for a tax-rate area: not
  modelled (listed). Grade A for the 1 %.
* Cal. Rev. & Tax. Code § 11911 (a) (leginfo, Wayback capture 2025-04-04): the county tax "at the rate of fifty-five
  cents ($0.55) for each five hundred dollars ($500) or fractional part thereof" when the consideration "exceeds one
  hundred dollars ($100)" (LA County's ordinance imposes it). Grade A.
* City of Los Angeles, Office of Finance, "Real Property Transfer Tax and Measure ULA FAQ" (Wayback capture 2025-07-23):
  "The Base Tax rate of $2.25 per $500 or part thereof"; ULA "4% for properties conveyed over $5,150,000, but under
  $10,300,000 and 2) 5.5% for properties conveyed at $10,300,000 or more"; "Effective for transactions closing after
  June 30, 2025, the new thresholds for ULA will be $5,300,000 and $10,600,000". The ULA rate applies to the whole
  consideration. Official secondary for LAMC Art. 1.9: grade B. Undated purchases use the thresholds in force at the
  end of 2025 (flagged).''',
lean=r'''
/-- Prop 13 general levy: 1 % of the (base-year) assessed value. -/
def prop13 : PropertyTax := { name := "Property tax, general levy 1 % (Los Angeles County)", sched := Schedule.flat 100 }
def propF : Family := propertyFamily "4100 property tax (Los Angeles)" prop13 "Cal. Const. art. XIII A § 1 (a); LA County FY 2025-26 Tax Rate Resolution: Countywide General Tax Levy 1.000000 %"

/-- `cents` per $500 or fractional part of the price (dollars, down). -/
def per500 (cents p : Int) : Int := divR .down (cents * ((pos p + 499) / 500)) 100

def countyDtt (p : Int) : Int := if p > 100 then per500 55 p else 0
def cityBase (p : Int) : Int := per500 225 p
/-- Measure ULA on the whole consideration, thresholds from 1 July 2025. -/
def ula (p : Int) : Int := if p ≥ 10600000 then divR .down (550 * p) BP else if p > 5300000 then divR .down (400 * p) BP else 0

def dttF : Family :=
  { name := "4400 documentary transfer taxes (LA County, City of LA, Measure ULA)", covers := [.transactions],
    run := fun _ g _ =>
      (g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).flatMap fun (p, i) =>
        [charge .transactions "Documentary transfer tax (LA County)" p.price id countyDtt (event := s!"purchase {i + 1}") (level := .local)
           (statute := "Cal. R&TC § 11911 (a): $0.55 per $500 or fractional part"),
         charge .transactions "Real property transfer tax (City of LA, base)" p.price id cityBase (event := s!"purchase {i + 1}") (level := .local)
           (statute := "LAMC Art. 1.9 (Office of Finance FAQ): $2.25 per $500 or part"),
         charge .transactions "Measure ULA (City of LA)" p.price id ula (event := s!"purchase {i + 1}") (level := .local)
           (statute := "LAMC Art. 1.9 Measure ULA (Office of Finance FAQ): 4 % over $5,300,000, 5.5 % from $10,600,000 (after 30 June 2025)")] }
''',
families="[propF, dttF]",
unsupported_expr='''when (g.assets.any fun a => a.kind.isRealEstate) "property tax: only the 1 % general levy; voter-approved debt service of the tax-rate area (LAUSD, LACCD, MWD, City bonds) and direct assessments not modelled; assessed value = the asset's assessed (Prop 13 base-year) value when given"
  ++ when (g.purchases.any fun p => p.kind.isRealEstate) "transfer taxes: undated purchases use the ULA thresholds from 1 July 2025 ($5,150,000 / $10,300,000 before); ULA exemptions (affordable-housing and nonprofit buyers) not modelled"''',
guards=["prop13.amount { kind := .home, value := 900000, assessed := 600000 } == 6000",
        "countyDtt 1000000 == 1100", "countyDtt 1000250 == 1100", "cityBase 1000000 == 4500",
        "ula 5000000 == 0", "ula 6000000 == 240000", "ula 12000000 == 660000"],
taxes=[dict(oecd="4100", tax="Property tax, general levy (Los Angeles County)", statute="Cal. Const. art. XIII A § 1 (a); LA County FY 2025-26 Tax Rate Resolution", dated="FY 2025-26 resolution (lien date 1 Jan 2025)", grade="A", package="P5", kernel_parts=["PropertyTax", "propertyFamily"], unsupported=["voter-approved debt rates of the TRA"]),
 dict(oecd="4400", tax="Documentary transfer tax (LA County)", statute="Cal. R&TC § 11911 (a)", dated="leginfo capture 2025-04-04", grade="A", package="P5", kernel_parts=["charge"]),
 dict(oecd="4400", tax="Real property transfer tax and Measure ULA (City of Los Angeles)", statute="LAMC Art. 1.9 (via the Office of Finance FAQ)", dated="FAQ capture 2025-07-23 (thresholds after 30 June 2025)", grade="B", package="P5", kernel_parts=["charge"], unsupported=["H1 2025 thresholds", "ULA exemptions"])])
