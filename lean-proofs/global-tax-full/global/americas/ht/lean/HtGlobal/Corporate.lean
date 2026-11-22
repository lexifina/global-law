import HtGlobal.Pit

/-!
# HT 2025: impôt sur les sociétés (1200) and withholding on dividends and interest

Source: Décret du 29 septembre 2005 sur l'impôt sur le revenu (Le Moniteur 5 Oct 2005), DGI consolidated version 'avec modifications intégrées' (dgi.gouv.ht upload Dec 2021, Wayback 2022-07-14; `ht/law/dgi_decret_ir_2005_consolide.*`). **Art. 149 B**: 30 % of the net income of companies and other legal persons; art. 150 (scope), art. 151 (agricultural cooperatives exempt), art. 153 (bénéfice réel). **Art. 121**: distributions, whoever the beneficiary, 15 % at source; **art. 122**: interest on claims, deposits and guarantees 15 % at source. Grade B: the 2021 consolidation is read; the lois de finances 2022-2025 (which may change the barèmes, art. 149 last para.) were not checked. The 2026 Code fiscal (Le Moniteur Spécial 48-A, 30 Sep 2026) is not in force in 2025.
-/

namespace HtGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon HtGlobal

def regime : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 3000 }

def citStatute : String := "Décret du 29 septembre 2005 sur l'impôt sur le revenu (Le Moniteur 5 Oct 2005), DGI consolidated version 'avec modifications intégrées' (dgi.gouv.ht upload Dec 2021, Wayback 2022-07-14; `ht/law/dgi_decret_ir_2005_consolide.*`) art. 149 B: 'L'impôt sur les sociétés et assimilées sera calculé sur les revenus nets réalisés par les sociétés et autres personnes morales au taux de 30%'; art. 150, 153"

def wht : Wht :=
  { name := "Retenues à la source (dividendes, intérêts)", rules := [{ kind := .dividend, rateBp := 1500, statute := "Décret du 29 septembre 2005 sur l'impôt sur le revenu (Le Moniteur 5 Oct 2005), DGI consolidated version 'avec modifications intégrées' (dgi.gouv.ht upload Dec 2021, Wayback 2022-07-14; `ht/law/dgi_decret_ir_2005_consolide.*`) arts. 120-121: revenus distribués, 'quels que soient les bénéficiaires', prélèvement à la source de 15%" }, { kind := .interest, rateBp := 1500, statute := "Décret du 29 septembre 2005 sur l'impôt sur le revenu (Le Moniteur 5 Oct 2005), DGI consolidated version 'avec modifications intégrées' (dgi.gouv.ht upload Dec 2021, Wayback 2022-07-14; `ht/law/dgi_decret_ir_2005_consolide.*`) art. 122: revenus des créances, dépôts et cautionnements, retenue à la source de 15%" }] }

def citF : Family := corpFamily "1200 Impôt sur les sociétés" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "HT: the consolidated decree is the 2021 DGI text; changes by the lois de finances 2022-2025 not checked (grade B); the forfait regime (art. 35, 1 % of turnover) and the 1 % / 5 % insurance forfaits (art. 159) not modelled; losses and exemptions as the kernel default"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "HT withholding: royalties and fees for services paid abroad are not covered by the 2005 decree text read (no rate): not charged; commissions and brokerage 15 % (art. 96) are not a separate payment kind; treaties not modelled"

#guard regime.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 150000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 0

end HtGlobal.Corporate
