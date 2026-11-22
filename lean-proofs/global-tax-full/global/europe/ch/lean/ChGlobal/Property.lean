import ChGlobal.Pit

/-!
# CH 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (kantonale Handänderungssteuer (Bern/Genf); Stempelabgaben StG Art. 13-16 (Umsatzabgabe)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (kantonale Liegenschaftssteuer): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4400 not levied (cited, pass 6, grade A)**: StG ZH (LS 631.1) § 1, § 205 (Fassung vom 30.11.2003, in Kraft seit 1.1.2005), Nachtrag 127 (1.1.2025): real-estate transfer tax: none in the canton of Zurich in 2025 (StG ZH § 1 lists the Staatssteuern, § 205: the municipalities' only Grundsteuer is the Grundstückgewinnsteuer) (zhlex Nachtrag 127 (in force 1.1.2025, `ch/law/stgzh_127.pdf`))
-/

namespace ChGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .transactions, why := "real-estate transfer tax: none in the canton of Zurich in 2025 (StG ZH § 1 lists the Staatssteuern, § 205: the municipalities' only Grundsteuer is the Grundstückgewinnsteuer)" }]

def notes : List String := ["CH 4400 pass 18: no Handänderungssteuer in the canton of Zurich (StG ZH § 1, § 205; grade A, cited absence); Umsatzabgabe grade C"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if g.purchases.any (fun p => p.kind == .listedShares || p.kind == .unlistedShares) then ["4400 Eidgenössische Umsatzabgabe (StG Art. 13-16) on securities bought through a Swiss securities dealer: not modelled (grade C)"] else [])


end ChGlobal.Property
