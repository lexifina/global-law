S = dict(cc="AR", fam="Property",
doc=r'''# Argentina 2025: Impuesto sobre los Bienes Personales (4200); inheritance grade C

Source: ARCA (ex AFIP) official pages for the período fiscal 2025 (fetched 2026-11-21, `ar/law/arca_bp_*.html`,
ARCHIVE_INDEX.tsv), giving the indexed amounts of Ley 23.966 Título VI (as amended by Ley 27.743):
* "¿Qué es?" (facts paraphrased): for período 2025 the non-taxable minimum on the value of the estate is
  $384.728.044,57, and a home used as the owner's dwelling is outside the tax when valued at $1.346.548.155,99 or less.
* "Alícuotas", Tabla general período 2025, on the value of the taxed assets in the country and abroad "que exceda de
  $384.728.044,57": to 52.664.283,73: 0,50 %; to 114.105.948,16: $263.321,42 + 0,75 %; above: $724.133,89 + 1,00 %.
* "Bienes exentos": among others, deposits in Argentine banks, government securities (Nación, provinces,
  municipalities, CABA), qualifying obligaciones negociables and funds, rural real estate of individuals.
Grade B (official tables; the Act's text was not read). Model: each person's assets (by `person`), at their statutory
value; the home is out of the tax when its value is at most $1,346,548,155 (whole pesos) and fully in above it;
deposits, bonds and pension funds are treated as exempt; shares and participations in companies are left out (for
Argentine companies the company pays 0.5 % as responsable sustituto, not modelled); debts not deducted; the
contribuyente cumplidor scale (0 / 0.25 / 0.5 %) not applied. Bands and the minimum in whole pesos (centavos dropped).
Inheritance and gift: no national tax; the Province of Buenos Aires ITGB was not read (C row).''',
lean=r'''def mni : Int := 384728044
def casa : Int := 1346548155
def bpSched : Schedule := Schedule.ofList [(0, 50), (52664283, 75), (114105948, 100)]

/-- Value counted for one asset (exempt kinds 0; the home is out when worth at most `casa`). -/
def counted (a : Asset) : Int :=
  if [AssetKind.deposits, .bonds, .pensionFund, .listedShares, .unlistedShares].contains a.kind then 0
  else if a.kind == .home && a.statutoryValue ≤ casa then 0
  else pos a.statutoryValue

def base (as : List Asset) : Int := pos (isum (as.map counted) - mni)
def bpTax (as : List Asset) : Int := bpSched.tax {} (base as)

def wealthF : Family :=
  { name := "4200 impuesto sobre los bienes personales", covers := [.wealth],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.assets.map (·.person)).eraseDups.map fun p =>
        let as := g.assets.filter (·.person == p)
        charge .wealth "Impuesto sobre los Bienes Personales" (isum (as.map counted)) (fun _ => base as) (fun _ => bpTax as)
          (event := s!"person {p + 1}, 31 December 2025")
          (statute := "Ley 23.966 Título VI (Ley 27.743); ARCA período 2025: MNI $384.728.044,57, casa-habitación $1.346.548.155,99, 0.5/0.75/1 %") }''',
families="[wealthF]",
unsupported=[["!g.assets.isEmpty && g.entity != .company", "bienes personales: deposits, bonds and pension funds taken as exempt (only Argentine bank deposits and public securities are); shares left out (company pays as responsable sustituto); debts not deducted; cumplidor scale not applied"],
 ["!g.transfers.isEmpty", "inheritance and gift: no national tax; provincial ITGB (Buenos Aires) not modelled"]],
guards=["bpTax [{ kind := .realEstate, value := 436728044 }] == 260000", "bpTax [{ kind := .home, value := 1000000000 }] == 0",
        "bpTax [{ kind := .deposits, value := 5000000000 }] == 0"],
taxes=[dict(oecd="4200", tax="Impuesto sobre los Bienes Personales", statute="Ley 23.966 Título VI as amended by Ley 27.743 (via ARCA tables)", dated="ARCA pages 'Alícuotas' and '¿Qué es?' (período fiscal 2025), fetched 2026-11-21", grade="B", package="P6", kernel_parts=["charge", "Schedule"], unsupported=["exempt kinds approximated", "responsable sustituto on shares", "cumplidor scale"]),
 dict(oecd="4300", tax="Inheritance and gift taxes", statute="none national; Provincia de Buenos Aires ITGB (Ley 14.044)", grade="C", status="unsupported", package="P6", kernel_parts=[], tried="not read", unsupported=["would unlock: the provincial ITGB law and 2025 tariff, or a text citing the national absence"])])
