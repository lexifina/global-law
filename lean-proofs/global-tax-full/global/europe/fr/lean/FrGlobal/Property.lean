import FrGlobal.Pit

/-!
# FR 2025: taxe foncière (4100), Paris

* 4400 Real-estate transfer and stamp duties (CGI art. 683, 1594 D (DMTO; 1594 D not among the local copies)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)

## Taxe foncière sur les propriétés bâties, Paris 2025 (pass 3)
Sources (sha256 in `law/SHA256SUMS`, provenance in `law/ARCHIVE_INDEX.tsv`):
* **CGI art. 1380** (Légifrance via the Internet Archive, capture 2025-01-13, `fr/law/cgi_art1380_wb.html`; "Version en
  vigueur depuis le 01 juillet 1979"): "La taxe foncière est établie annuellement sur les propriétés bâties sises en
  France à l'exception de celles qui en sont expressément exonérées".
* **CGI art. 1388** (capture 2024-11-05, `fr/law/cgi_art1388_wb.html`; "Version en vigueur depuis le 11 janvier
  1980"): "La taxe foncière sur les propriétés bâties est établie d'après la valeur locative cadastrale de ces
  propriétés ... et sous déduction de 50 % de son montant".
* **Paris 2025 rates**: DGFiP open data "Fiscalité locale des particuliers" (data.economie.gouv.fr, exercice 2025,
  insee_com 75056 VILLE DE PARIS; `fr/law/dgfip_fiscalite_locale_particuliers_paris.json`, field labels in
  `..._meta.json`): "FB - COMMUNE / TAUX VOTE" 20.5; "FB - TSE / TAUX NET" 0.221; "FB - TSE AUTRES" 0.156;
  "FB - TASA" 0.189; "FB - GEMAPI" 0.143; "FB - TAUX GLOBAL (commune, syndicat de commune, intercommunalité, taxes
  spéciales, GEMAPI)" 21.21; TEOM taux plein 6.21. The Conseil de Paris rate deliberation was not read: grade B.
Base: the valeur locative cadastrale is an annual value (`annualValue`, or `assessed` where only that is given);
without either no charge is made (flagged). Applied to `home` and `realEstate` (bâti); tax rounded down to euros.


## 4400 Droits de mutation à titre onéreux (immeubles) (pass 6)
Source: PwC Worldwide Tax Summaries, France, Corporate - Other taxes, accessed 2025-06-17 (Wayback capture; `law/pwc_corpother_wb2025.txt`).
* DMTO 5,80 % on sales of land and buildings (buyer); up to 6,3 % for acts from 1.4.2025 by départemental decision
-/

namespace FrGlobal.Property
open TaxKernel TaxKernel.Global

/-- DGFiP 2025, Paris: taux global TFPB 21,21 % (hundredths of a percent). -/
def tauxGlobalTfbParis2025 : Int := 2121
/-- CGI art. 1388: base = valeur locative cadastrale less 50 %. -/
def baseTfb (vlc : Int) : Int := divR .down (pos vlc) 2
def tfbParis (vlc : Int) : Int := divR .down (baseTfb vlc * tauxGlobalTfbParis2025) 10000
def vlcOf (a : Asset) : Int := if 0 ≤ a.annualValue then a.annualValue else a.assessed
def tfbCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => (a.kind == .home || a.kind == .realEstate) && 0 ≤ vlcOf a).map fun (a, i) =>
    charge .propertyRecurrent "Taxe foncière sur les propriétés bâties (Paris)" (vlcOf a) baseTfb (fun b => divR .down (b * tauxGlobalTfbParis2025) 10000)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "CGI art. 1380, 1388; Paris 2025 taux global TFPB 21,21 % (DGFiP)")

/-- CGI art. 683, 1594 D, 1584, 1595 bis (5,80 % in all) -/
def p6dmto : TransferDuty := { name := "Droits de mutation à titre onéreux (immeubles)", sched := Schedule.flat 580, kinds := [.home, .realEstate, .land] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4100 taxe foncière (Paris)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       tfbCharges g.assets },
   { name := "4400 Droits de mutation à titre onéreux (immeubles)", covers := [.transactions],
     run := fun args g prev =>
       p6dmto.charges g.purchases "CGI art. 683, 1594 D, 1584, 1595 bis (5,80 % in all)" }]

def absent : List Absent :=
  []

def notes : List String := ["FR 4100: CGI art. 1380, 1388 (Légifrance via Wayback); Paris 2025 taux global TFPB 21,21 % (DGFiP open data)", "FR 4400 Droits de mutation à titre onéreux (immeubles): PwC WWTS Corporate - Other taxes, 2025-06-17 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => (a.kind == .home || a.kind == .realEstate) && a.annualValue < 0 && a.assessed < 0) then ["4100 taxe foncière: no valeur locative cadastrale (annualValue) given: no charge made"] else [])
  ++ (if g.assets.any (fun a => a.kind == .land) then ["4100 taxe foncière sur les propriétés non bâties not modelled"] else [])
  ++ (if g.assets.any (·.kind.isRealEstate) then ["4100 taxe foncière: TEOM (6,21 %), frais de gestion (CGI art. 1641), exonérations and dégrèvements not applied"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 Paris: the département's rate rose for acts from 1 April 2025 (up to 6,3 % in all, not modelled); new buildings under TVA (0,715 %) and first-time-buyer exemptions not separated; notary fees not taxes"] else [])

-- VLC 4 000: base 2 000 (art. 1388, 50 %); x 21,21 % = 424,20
#guard baseTfb 4000 == 2000
#guard tfbParis 4000 == 424
#guard tfbParis 0 == 0
#guard p6dmto.amount { kind := .home, price := 200000 } == 11600
#guard p6dmto.amount { kind := .home, price := 2000000 } == 116000
#guard p6dmto.amount { kind := .vehicle, price := 100000 } == 0

end FrGlobal.Property
