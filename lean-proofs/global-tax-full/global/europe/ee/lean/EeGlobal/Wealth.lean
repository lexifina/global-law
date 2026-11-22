import EeGlobal.Pit

/-!
# EE 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (none recorded (not cited)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade A)**: Maksukorralduse seadus (MKS) § 3 lg 2-3 and § 4 lg 2 (redaktsioon 1.1.2025-31.12.2025); kohalike maksude seadus (KoMS) § 5 (redaktsioon from 1.1.2025): MKS § 3 lg 2 lists the state taxes (tulumaks, sotsiaalmaks, maamaks, hasartmängumaks, käibemaks, tollimaks, aktsiisid, raskeveokimaks, ettevõtlustulu maks, mootorsõidukimaks from 1.1.2025); lg 3: local taxes only as the KoMS allows, and KoMS § 5 lists reklaamimaks, teede ja tänavate sulgemise maks, loomapidamismaks, lõbustusmaks, parkimistasu; § 4 lg 2: a taxpayer pays only the state and local taxes the law provides. None of them is levied on net wealth (Riigi Teataja via the Internet Archive: MKS captured 2025-08-04 (`ee/law/mks_wb20250804.html`), KoMS 2025-04-21 (`ee/law/koms_wb20250421.html`))

* **4300 not levied (cited, pass 6, grade A)**: Maksukorralduse seadus (MKS) § 3 lg 2-3 and § 4 lg 2 (redaktsioon 1.1.2025-31.12.2025); kohalike maksude seadus (KoMS) § 5 (redaktsioon from 1.1.2025): MKS § 3 lg 2 lists the state taxes (tulumaks, sotsiaalmaks, maamaks, hasartmängumaks, käibemaks, tollimaks, aktsiisid, raskeveokimaks, ettevõtlustulu maks, mootorsõidukimaks from 1.1.2025); lg 3: local taxes only as the KoMS allows, and KoMS § 5 lists reklaamimaks, teede ja tänavate sulgemise maks, loomapidamismaks, lõbustusmaks, parkimistasu; § 4 lg 2: a taxpayer pays only the state and local taxes the law provides. None of them is levied on inheritances or gifts (Riigi Teataja via the Internet Archive: MKS captured 2025-08-04 (`ee/law/mks_wb20250804.html`), KoMS 2025-04-21 (`ee/law/koms_wb20250421.html`))
-/

namespace EeGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "MKS § 3 lg 2 lists the state taxes (tulumaks, sotsiaalmaks, maamaks, hasartmängumaks, käibemaks, tollimaks, aktsiisid, raskeveokimaks, ettevõtlustulu maks, mootorsõidukimaks from 1.1.2025); lg 3: local taxes only as the KoMS allows, and KoMS § 5 lists reklaamimaks, teede ja tänavate sulgemise maks, loomapidamismaks, lõbustusmaks, parkimistasu; § 4 lg 2: a taxpayer pays only the state and local taxes the law provides. None of them is levied on net wealth" },
   { oecd := .estate, why := "MKS § 3 lg 2 lists the state taxes (tulumaks, sotsiaalmaks, maamaks, hasartmängumaks, käibemaks, tollimaks, aktsiisid, raskeveokimaks, ettevõtlustulu maks, mootorsõidukimaks from 1.1.2025); lg 3: local taxes only as the KoMS allows, and KoMS § 5 lists reklaamimaks, teede ja tänavate sulgemise maks, loomapidamismaks, lõbustusmaks, parkimistasu; § 4 lg 2: a taxpayer pays only the state and local taxes the law provides. None of them is levied on inheritances or gifts" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end EeGlobal.Wealth
