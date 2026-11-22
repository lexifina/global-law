S = dict(cc="UK", fam="Capital",
doc=r'''# United Kingdom 2025: capital gains tax on the entity's disposals (1100), stacked on the 1.x model

Sources: TCGA 1992 ss. 222, 223 at 2025-07-01 (legislation.gov.uk, `uk/law/tcga_s22[23]_2025-07-01.html`). The CGT
rates, annual exempt amount and the bands are the 1.x model's (it already taxes the household's `capitalGains` and
prints `capitalGainsTax`): the disposals' gains are routed into `capitalGains` and the tax is the 1.x tax with them less
the 1.x tax without them (`stackedTax`), booked as its own 1100 charge.
* **s. 223 (1)**: "No part of a gain to which section 222 applies shall be a chargeable gain if the dwelling-house ...
  has been the individual's only or main residence throughout the period of ownership".
''',
lean=r'''
/-- s. 222-223: a main residence throughout the ownership is exempt (the flag `mainHome` is read as "throughout"). -/
def chargeable (d : Disposal) : Int := if d.kind.isRealEstate && d.mainHome then 0 else d.gain

def gains (ds : List Disposal) : Int := pos (isum (ds.map chargeable))

def charges (args : List String) (g : CanonGlobal) : List Charge :=
  if g.entity == .company || g.disposals.isEmpty then [] else
  let x := gains g.disposals
  [charge .pit "Capital gains tax (disposals, stacked on the 1.x model)" (isum (g.disposals.map (·.gain))) (fun _ => x)
     (fun _ => stackedTax (pitOf args) g.household { capitalGains := x }) (event := "disposals")
     (statute := "TCGA 1992 ss. 1H, 222-223; rates, bands and annual exempt amount as in the 1.x model")]
''',
families=[("1100 CGT on disposals", [], "charges args g")],
notes=["UK 1100: disposals stacked on the 1.x CGT"],
unsupported=[("g.disposals.any (fun d => d.kind.isRealEstate && d.mainHome)", "private residence relief taken as full (residence throughout ownership); lettings and absence periods (s. 223 (2)-(3)) not modelled"),
  ("g.disposals.any (fun d => d.kind == .business || d.kind == .unlistedShares)", "business asset disposal relief and investors' relief not modelled")],
guards=["chargeable { kind := .home, proceeds := 300000, cost := 100000, mainHome := true } == 0",
        "gains [{ kind := .listedShares, proceeds := 50000, cost := 20000 }, { kind := .realEstate, proceeds := 100000, cost := 110000 }] == 20000"],
taxes=[{"oecd": "1100", "tax": "Capital gains tax (disposals)", "statute": "TCGA 1992 ss. 222, 223 (1); 1.x model CGT", "dated": "legislation.gov.uk 2025-07-01", "grade": "A", "kernel_parts": ["stackedTax"], "unsupported": ["partial main residence relief", "BADR and investors' relief", "losses brought forward"]}])
