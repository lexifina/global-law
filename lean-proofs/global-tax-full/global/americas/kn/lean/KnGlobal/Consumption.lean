import KnGlobal.Pit

/-!
# Saint Kitts and Nevis 2025: Value Added Tax (5111); excise grade C

Source: Value Added Tax Act, Cap. 18.47, Revised Laws (revision date 31 Dec 2017), lawcommission.gov.kn, Wayback capture
2024-08-07 (`kn/law/vat_ch18_47_2017.pdf`). Later amendments not checked (the Special VAT Reduction Orders of 2018 and
2019 were temporary): grade B.
* **s. 17 (1)**: "(a) 17 percent of the value of every taxable supply ...; (d) to the extent provided in regulations, 10
  percent of the value of a taxable supply ... of (i) accommodation services by a hotel, guest house, inn".
* **Second Schedule (zero rated)** 3 (2) listed basic foods, (4) locally produced bread, (5) fuel.
* **Third Schedule (exempt)**: 2 financial services incl. "long term insurance, general insurance and reinsurance";
  4 education; 6 accommodation in a dwelling; 9 "water provided to a residential dwelling"; 11 transportation of
  passengers; 13 medically-related goods; 15 electricity "to the extent provided in regulations"; 16 medicines for
  chronic disease; 17 medical services.
* Food read as zero rated (listed basic foods only: lower bound); electricity read as standard (regulation relief not
  read: upper bound); medicines standard except those for chronic disease (flagged).

Pass 6: general sales tax (5112) cited not levied (grade A): Value Added Tax Regulations (in the VAT Act Cap. 18.47 Revised Edition 2017, `kn/law/vat_ch18_47_2017.txt`) **reg. 19 (1)**: transition rules "from the coming into force of the value added tax and the repeal of the Consumption Tax Act, Cap. 20.02 and the Hotel Accommodation and Restaurant Tax Act, Cap. 20.20": the VAT of the P1 row replaced the consumption tax.
-/

namespace KnGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon KnGlobal

def vat : Vat :=
  { name := "Value Added Tax", standard := 1700, reduced := 1000,
    classOf := fun gd => match gd with
      | .food | .petrol | .diesel => .zero
      | .hotels => .reduced
      | .water | .education | .transport | .financial | .insurance | .health | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act Cap. 18.47 s. 17 (1) (a) 17 %, (d) 10 % (hotel accommodation); Sched. 2 para 3 (2), (4), (5) (zero); Sched. 3 paras 2, 4, 6, 9, 11, 17 (exempt)"

def vatF : Family := vatFamily "Value Added Tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "the Consumption Tax Act Cap. 20.02 was repealed when VAT came into force (VAT Regulations reg. 19 (1), Cap. 18.47 Rev. Ed. 2017)" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: only the basic foods listed in VAT Sched. 2 para 3 (2) and local bread are zero rated; other food 17 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .electricity || s.good == .medicines) "electricity (exempt to the extent of regulations) and medicines for chronic disease (exempt) charged at 17 % (upper bound)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits) "excise tax not modelled (Excise Tax Act Cap. 20.11 not captured)"

#guard vat.embedded { good := .clothing, amount := 1170 } == 170
#guard vat.embedded { good := .hotels, amount := 1100 } == 100
#guard vat.embedded { good := .water, amount := 1170 } == 0

end KnGlobal.Consumption
