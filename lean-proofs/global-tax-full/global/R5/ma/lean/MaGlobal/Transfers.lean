import TaxKernel.Global
import R5Common

/-!
# Morocco 2025: droits d'enregistrement on real-estate transfers (4400)

CGI 2025 (`law/cgi2025fr.txt`), art. 133-I (rates of the proportional registration duties):
* F-1° (4 %): the acquisition, by natural or legal persons, of built premises (locaux construits) for dwelling,
  commercial, professional or administrative use, with the land they stand on up to five times the covered area;
* G-1° (5 %): acts acquiring, for consideration or free of charge, bare land or land with buildings to be demolished;
* A-1° (6 %): the deeds of art. 127-I-A-1-b) only, that is transfers of businesses (fonds de commerce) and clienteles
  (LF 73-16 for 2017 narrowed A-1° to them).

Gap-closing pass (2026-11-21): **corrected.** Up to now every real-estate purchase was charged 6 % under A-1°; that
paragraph no longer covers immovables. Homes and other buildings are now charged 4 % (F-1°), land 5 % (G-1°), a
business purchase 6 % (A-1°). Reduced rates and exemptions for first homes and social housing (art. 129, 133) and the
land-registry fee (conservation foncière, outside the CGI) are not modelled.
-/

namespace MaGlobal
open TaxKernel TaxKernel.Global R5Common

def deBuilt : TransferDuty :=
  { name := "Droits d'enregistrement (locaux construits)", sched := Schedule.flat 400, kinds := [.home, .realEstate] }
def deLand : TransferDuty :=
  { name := "Droits d'enregistrement (terrains)", sched := Schedule.flat 500, kinds := [.land] }
def deBusiness : TransferDuty :=
  { name := "Droits d'enregistrement (fonds de commerce)", sched := Schedule.flat 600, kinds := [.business] }

def transfers : Family :=
  { name := "4400 droits d'enregistrement", covers := [.transactions],
    run := fun _ g _ =>
      deBuilt.charges g.purchases "CGI art. 133-I-F-1° (4 %: locaux construits)" ++
      deLand.charges g.purchases "CGI art. 133-I-G-1° (5 %: terrains nus)" ++
      deBusiness.charges g.purchases "CGI art. 133-I-A-1°, art. 127-I-A-1-b) (6 %: fonds de commerce)" }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (·.firstHome) then ["first-home and social-housing reductions (art. 129, 133) not modelled"] else []

#guard deBuilt.amount { kind := .home, price := 1000000 } == 40000
#guard deBuilt.amount { kind := .land, price := 1000000 } == 0
#guard deLand.amount { kind := .land, price := 500000 } == 25000
#guard deBusiness.amount { kind := .business, price := 200000 } == 12000

end MaGlobal
