import BrGlobal.Pit

/-!
# Brazil 2025: capital income and gains (1100): stacking on the 1.x model and the ganho de capital

* Pass 1 (unchanged): additional interest, dividends, rent and listed-share gains held over 12 months are routed into the
  1.x household and charged as `stackedTax`.
* **Ganho de capital** (Lei 8.981/1995 compilada, planalto, fetched 2026-11-21, `br/law/l8981.htm`): **art. 21** "O ganho
  de capital percebido por pessoa física em decorrência da alienação de bens e direitos de qualquer natureza sujeita-se
  à incidência do imposto sobre a renda, com as seguintes alíquotas: I - 15% ... que não ultrapassar R$ 5.000.000,00;
  II - 17,5% ... entre R$ 5.000.000,00 e R$ 10.000.000,00; III - 20% ... entre R$ 10.000.000,00 e R$ 30.000.000,00; IV -
  22,5% ... que ultrapassar R$ 30.000.000,00" (Lei 13.259/2016). Charged per disposal on the gain (price less historical
  cost). Grade B: the exemptions and reductions of other acts (Lei 9.250 art. 23 single property up to R$ 440,000; Lei
  11.196 arts. 39-40 home reinvestment and reduction factors; Lei 7.713 art. 18 pre-1988 reduction) are not applied
  (upper bound, flagged); stock-exchange gains (Lei 11.033) are left to the stacking family or listed.
-/

namespace BrGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon BrGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- Lei 8.981/1995 art. 21 (Lei 13.259/2016): 15 % to R$ 5,000,000; 17.5 % to R$ 10,000,000; 20 % to R$ 30,000,000;
22.5 % above. -/
def gcSched : Schedule := Schedule.ofList [(0, 1500), (5000000, 1750), (10000000, 2000), (30000000, 2250)]
/-- Disposals outside the stock-exchange regime (listed shares are left to the stacking family or listed). -/
def isGc (d : Disposal) : Bool := d.kind != .listedShares && d.kind != .deposits && d.kind != .pensionFund
def gcTax (gain : Int) : Int := gcSched.tax {} (pos gain)

def gcF : Family :=
  { name := "1100 ganho de capital de pessoa física (Lei 8.981 art. 21)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      (g.disposals.zipIdx.filter fun (d, _) => isGc d).map fun (d, i) =>
        charge .pit "Imposto sobre a renda: ganho de capital" d.gain (fun _ => pos d.gain) gcTax (event := s!"disposal {i + 1}")
          (statute := "Lei 8.981/1995 art. 21 I-IV (Lei 13.259/2016): 15 %, 17,5 %, 20 %, 22,5 %") }

def families : List Family := [capF, gcF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := stackUnsupported g
  ++ when (g.entity != .company && g.disposals.any isGc) "ganho de capital at the art. 21 rates on the historical gain; exemptions and reductions (Lei 9.250 art. 23, Lei 11.196 arts. 39-40, Lei 7.713 art. 18) not applied: upper bound"
  ++ when (g.entity != .company && g.disposals.any fun d => d.kind == .listedShares && !isLongListed d) "stock-exchange gains held 12 months or less (Lei 11.033, monthly R$ 20,000 exemption) not modelled"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
#guard gcTax 1000000 == 150000
#guard gcTax 6000000 == 925000
#guard gcTax 40000000 == 7875000
#guard isGc { kind := .listedShares, proceeds := 10, cost := 5 } == false

end BrGlobal.Capital
