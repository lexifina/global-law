import TaxKernel.Global
import R5Common

/-!
# Tunisia 2025: registration duties on property sales (4400) and on gifts and successions (4300)

Code des droits d'enregistrement et de timbre, DGELF edition 2025 (jibaya.tn, uploaded 29/04/2025,
`law/tn_cdet_2025.pdf` + `.txt`):
* art. 20, "Biens immeubles", 1): sales and all acts transferring for consideration the ownership, usufruct or bare
  ownership of immovable property: **5 %**; 4) building land for individual dwellings 1 / 2 / 3 / 5 % by area (up to
  120, 300, 600 m², above; not computed: area); 3) exchanges 2,5 %. Due from the buyer (art. 4 of the Code: the
  acquirer).
* art. 20, 16) donations and successions: between ascendants and descendants and between spouses 2,5 %; between
  brothers and sisters 5 %; uncles, aunts, nephews, nieces, great-uncles and cousins 25 %; relatives beyond the fourth
  degree and non-relatives 35 %.
* art. 23, 18 ter (Law 2006-69): gifts between ascendants and descendants and between spouses bear only the fixed duty
  (30 dinars), not the proportional duty (taken as 0).
* art. 51-I: on successions, an abatement of 5 000 dinars per living child, dependent ascendant and surviving spouse, at
  most 30 000 dinars per estate (applied as 5 000 per direct-line or spouse heir; the estate cap not applied).
Relations: spouse, child, grandchild, parent -> 2,5 %; sibling 5 %; nieceNephew and otherRelative 25 % (relatives
beyond the fourth degree would be 35 %); unrelated and charity 35 %. **Grade A** (statute text read).
-/

namespace TnGlobal
open TaxKernel TaxKernel.Global R5Common

def mutation : TransferDuty := { name := "droit d'enregistrement (mutation d'immeubles)", sched := Schedule.flat 500 }

def relClass : Relation → Nat
  | .spouse | .child | .grandchild | .parent => 0
  | .sibling => 1
  | .nieceNephew | .otherRelative => 2
  | _ => 3

def successions : InheritanceTax :=
  { name := "droits de mutation par décès", classOf := relClass,
    classes := [{ allowance := 5000, sched := Schedule.flat 250 }, { allowance := 0, sched := Schedule.flat 500 },
                { allowance := 0, sched := Schedule.flat 2500 }, { allowance := 0, sched := Schedule.flat 3500 }] }

def donations : InheritanceTax :=
  { name := "droits de donation", classOf := relClass, exemptRelations := [.spouse, .child, .grandchild, .parent],
    classes := [{ allowance := 0, sched := Schedule.flat 250 }, { allowance := 0, sched := Schedule.flat 500 },
                { allowance := 0, sched := Schedule.flat 2500 }, { allowance := 0, sched := Schedule.flat 3500 }] }

def transfers : Family :=
  { name := "4400 droits de mutation d'immeubles, 4300 donations et successions", covers := [.transactions, .estate],
    run := fun _ g _ =>
      mutation.charges g.purchases "CDET art. 20, biens immeubles 1) (5 %)"
      ++ successions.charges (g.transfers.filter (·.kind != .gift)) "CDET art. 20-16) (2,5 / 5 / 25 / 35 %), art. 51-I (5 000 dinars per direct-line or spouse heir)"
      ++ donations.charges (g.transfers.filter (·.kind == .gift)) "CDET art. 20-16) (5 / 25 / 35 %); art. 23-18 ter (direct line and spouses: fixed duty only)" }

def transfersUnsupported (g : CanonGlobal) : List String :=
  (if g.purchases.any (fun p => p.kind == .land) then
    ["registration duty: building land for individual dwellings is 1-5 % by area (art. 20-4)); taken at 5 %"] else [])
  ++ (if !g.transfers.isEmpty then
    ["gift and succession duty: the 30 000-dinar estate cap of the art. 51 abatement, relatives beyond the fourth degree (35 %), the 30-dinar fixed duty on direct-line gifts and exempt beneficiaries not applied"] else [])

#guard mutation.amount { kind := .home, price := 300000 } == 15000
#guard successions.tax { kind := .inheritance, value := 105000, relation := .child } == 2500
#guard successions.tax { kind := .inheritance, value := 100000, relation := .sibling } == 5000
#guard donations.tax { kind := .gift, value := 100000, relation := .child } == 0
#guard donations.tax { kind := .gift, value := 100000, relation := .unrelated } == 35000

end TnGlobal
