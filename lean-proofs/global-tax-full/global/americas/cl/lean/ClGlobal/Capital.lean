import ClGlobal.Pit

/-!
# Chile 2025: 1100 mayor valor (pilot, unchanged)

* **LIR** art. 17 N° 8 a) i)-iii), vi): gains on shares and other assets; cost "reajustado de acuerdo al porcentaje de
  variación … del índice de precios al consumidor"; "Cuando el conjunto de los resultados … no exceda del equivalente a
  10 unidades tributarias anuales … ingreso no constitutivo de renta".
* art. 17 N° 8 b) i)-iv): real estate: indexed cost; "No constituirá renta … la suma total equivalente a 8.000
  unidades de fomento"; the excess "se gravará … con el impuesto global complementario … o bien … con un impuesto único
  y sustitutivo de 10%, a elección del enajenante"; ii) and iii) apply only if held more than one year.
* art. 107 N° 1 (Ley 21.420): listed shares with stock-market presence: "un impuesto con tasa de 10%, que tendrá el
  carácter de impuesto único".
-/

namespace ClGlobal.Capital
open TaxKernel TaxKernel.Global ClGlobal

def gainOf (d : Disposal) : Int := ({ indexCost := true } : GainRule).gain d.indexBp BP d

def isListed107 (d : Disposal) : Bool := d.kind == .listedShares && d.listed

structure GainsResult where
  reLong : Int
  excess : Int
  sole10 : Int
  gcOnExcess : Int
  gcIncome : Int
  gcTax : Int
  listed : Int

def gains (args : List String) (g : CanonGlobal) : GainsResult :=
  let ds := g.disposals
  let reLong := pos (isum ((ds.filter fun d => d.kind.isRealEstate && decide (d.heldMonths > 12)).map gainOf))
  let reShort := pos (isum ((ds.filter fun d => d.kind.isRealEstate && decide (d.heldMonths ≤ 12)).map gainOf))
  let others := isum ((ds.filter fun d => !d.kind.isRealEstate && !isListed107 d).map gainOf)
  let othersTaxable := if others ≤ 10 * uta then 0 else others
  let excess := pos (reLong - ufToPesos 8000)
  let gcIncome := othersTaxable + reShort
  let st (x : Int) : Int := stackedTax (pitOf args) g.household { rentalIncome := x }
  { reLong, excess, sole10 := divR .down (1000 * excess) BP, gcOnExcess := st (gcIncome + excess) - st gcIncome,
    gcIncome, gcTax := st gcIncome,
    listed := pos (isum ((ds.filter isListed107).map gainOf)) }

def capitalGains : Family :=
  { name := "1100 mayor valor", covers := [],
    run := fun args g _ =>
      if g.entity == .company || g.disposals.isEmpty then [] else
      let r := gains args g
      let electSole := decide (r.sole10 ≤ r.gcOnExcess)
      [charge .pit (if electSole then "Impuesto único sustitutivo 10 % (bienes raíces)" else "Global complementario (bienes raíces, exceso)")
         r.reLong (fun x => pos (x - ufToPesos 8000)) (fun _ => if electSole then r.sole10 else r.gcOnExcess)
         (event := "real estate held > 1 year")
         (statute := "LIR art. 17 N° 8 b) ii)-iii): 8.000 UF exempt; excess: 10 % or global complementario, the seller's election (cheaper taken)"),
       charge .pit "Global complementario (mayor valor)" r.gcIncome id (fun _ => r.gcTax) (event := "other gains")
         (statute := "LIR art. 17 N° 8 a) vi) (≤ 10 UTA exempt), b) iv) (real estate held ≤ 1 year): stacked on the 1.x global complementario"),
       charge .pit "Impuesto único art. 107" r.listed id (fun x => divR .down (1000 * x) BP) (event := "listed shares")
         (statute := "LIR art. 107 N° 1 (Ley 21.420): 10 %")] }

def families : List Family := [capitalGains]
def absent : List Absent := []
def notes : List String := []
def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.kind.isRealEstate) then
        ["art. 17 N° 8 b) ii): the 8.000 UF limit is lifetime; earlier use is not known and taken as nil"] else [])
  ++ (if g.disposals.any (fun d => !d.kind.isRealEstate && !isListed107 d) || g.disposals.any (fun d => d.kind.isRealEstate && decide (d.heldMonths ≤ 12)) then
        ["gains taxed in global complementario are routed through the 1.x model as rent, which it splits equally between adults"] else [])

end ClGlobal.Capital
