import AtGlobal.Pit

/-!
# AT 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (ErbStG 1955 not applied after 31.7.2008 (VfGH G 54/06): absence not cited from a text): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (Vermögensteuer abolished 1994: absence not cited): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4300 not levied (cited)**: Erbschafts- und Schenkungssteuergesetz 1955 § 1 (1) Z 1-3, § 34 (1) Z 13 (RIS, Fassung vom 01.07.2025): § 1 (1) Z 1 (Erwerb von Todes wegen) "aufgehoben durch VfGH, BGBl. I Nr. 9/2007", Z 2 (Schenkungen) "aufgehoben durch VfGH, BGBl. I Nr. 39/2007"; for Z 3 "Abgaben nach diesem Bundesgesetz werden ... für die die Steuerschuld nach dem 31. Juli 2008 entsteht, nicht mehr erhoben (vgl. § 34 Abs. 1 Z 13)"

* **4200 not levied (cited)**: Steuerreformgesetz 1993, BGBl. Nr. 818/1993, Art. XII (Vermögensteuergesetz 1954 § 25 a): "Außerkrafttreten § 25 a. Dieses Gesetz ist auf Sachverhalte nicht mehr anzuwenden, die nach dem 31. Dezember 1993 liegen." (BGBl. ausgegeben am 30. November 1993, 300. Stück)
-/

namespace AtGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "§ 1 (1) Z 1 (Erwerb von Todes wegen) \"aufgehoben durch VfGH, BGBl. I Nr. 9/2007\", Z 2 (Schenkungen) \"aufgehoben durch VfGH, BGBl. I Nr. 39/2007\"; for Z 3 \"Abgaben nach diesem Bundesgesetz werden ... für die die Steuerschuld nach dem 31. Juli 2008 entsteht, nicht mehr erhoben (vgl. § 34 Abs. 1 Z 13)\"" },
   { oecd := .wealth, why := "\"Außerkrafttreten § 25 a. Dieses Gesetz ist auf Sachverhalte nicht mehr anzuwenden, die nach dem 31. Dezember 1993 liegen.\" (BGBl. ausgegeben am 30. November 1993, 300. Stück)" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end AtGlobal.Wealth
