S = dict(cc="TT", fam="Consumption",
doc=r'''# Trinidad and Tobago 2025: VAT (5111); excise and customs duties (5121) unsupported

Source: Value Added Tax Act, Chap. 75:06, Laws of Trinidad and Tobago (Ministry of the Attorney General and Legal
Affairs, `rgd.legalaffairs.gov.tt/laws2/Alphabetical_List/lawspdfs/75.06.pdf`, fetched 2026-11-21; amendment list up
to Act 17/2016 and LN 2016: later Finance Acts not checked: grade B).
* **s. 7 (1)**: "the rate of twelve and one-half per cent" (Act 1 of 2016).
* **Schedule 1** (exempt services): 1 medical, dental, hospital services; 2 bus and taxi services; 4 education; 6
  "Rental of residential property"; 10 financial services.
* **Schedule 2** (zero-rating): 1 (1) (a) "unprocessed food", rice, flour, milk, bread and the listed staples (the
  basket's food line read as these, flagged); 7 "Water and sewerage services supplied by a public authority"; 8 public
  bus services; 9, 10 prescription and listed over-the-counter medicines.
* Excise duties on alcohol, tobacco and petroleum (Customs Act, Excise (General Provisions) Act Chap. 78:50 and their
  Orders) were not read: unsupported.''',
vat=dict(name="Value added tax", standard=1250, statute="VAT Act Chap. 75:06 s. 7 (1) (12.5 %), Sched. 1 items 1, 2, 4, 6, 10, Sched. 2 items 1, 7-10",
  classes={"food":"zero","water":"zero","medicines":"zero","health":"exempt","transport":"exempt","education":"exempt","rent":"exempt","financial":"exempt","insurance":"exempt"}),
unsupported=[["g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel", "excise duties (Customs Act; Excise (General Provisions) Act Chap. 78:50 and Orders) not read: not charged"],
 ["!g.consumption.isEmpty", "food read as the zero-rated staples of Sched. 2 item 1; other food is at 12.5 %"]],
guards=["vat.embedded { good := .clothing, amount := 1125 } == 125", "vat.embedded { good := .food, amount := 1125 } == 0"],
taxes=[dict(oecd="5111", tax="Value added tax", statute="VAT Act Chap. 75:06 s. 7, Scheds. 1, 2", dated="Laws of T&T PDF with amendments to 17/2016; later Finance Acts not checked", grade="B", package="P1", kernel_parts=["Vat"], unsupported=["Finance Act changes after 2016"]),
 dict(oecd="5121", tax="Excise duties (alcohol, tobacco, petroleum)", statute="Customs Act Chap. 78:01; Excise (General Provisions) Act Chap. 78:50", grade="C", status="unsupported", package="P1", unsupported=["would unlock: the Customs/Excise Orders in force in 2025"])])
