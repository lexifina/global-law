import TaxKernel.Global
import R5Common

/-!
# Algeria 2025: IRG on capital gains of individuals (1100: real property and company shares)

Source: DGI CIDTA 2025 Arabic edition pp. 23-24 and 32 (`law/dgi_cidta_2025_ar.pdf`; Arabic OCR
`law/dz_cidta25_ar_gains_ocr.txt`, rates checked on the page image), wording from the 2023 French edition:
* art. 77: gains realised outside a business on sales of built or unbuilt immovables and real rights (gifts to
  relatives beyond the second degree and to non-relatives count as sales); art. 77 bis: gains on shares, company
  interests and similar securities sold outside a business;
* art. 78: the gain is the sale price (less duties, taxes and justified costs of the sale) minus the acquisition price
  or construction value, raised by justified costs of acquisition, upkeep and improvement up to 30 % of that price;
  an asset received by gift or inheritance takes its market value at that date;
* art. 79: **5 % a year from the third year of possession, at most 50 %** off the taxable gain;
* art. 79 bis: shares: sale price (or fair value) less acquisition or subscription price;
* art. 80 bis 1 (LF 2022, LF 2025): exempt: sales to end an inherited co-ownership, Mourabaha / Ijara contracts;
* art. 104-5 (last changed by LF 2025 art. 8): (a) property gains **15 %**, final; **50 % less** for the sale of a
  dwelling in a collective or individual building that is the seller's only property and main home; (b) share gains
  **15 %**, final, **5 %** if the gain is reinvested by 31 December of the next year.
Model (households): per disposal of a home, real estate or land: gain = proceeds − cost − costs (costs taken as the
sale and acquisition costs, the latter within 30 % of the cost); abatement 5 % per full year held beyond two, at most
50 %; 15 %; halved for a disposal flagged `mainHome` when the household holds no other home or real estate. Unlisted
shares: 15 % of proceeds − cost − costs. Listed shares: not charged (the exemption for listed securities was not
read; listed). Interest, dividends and rents stay with the 1.x model. Grade A (2025 code text read).
-/

namespace DzGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 79: 5 % per full year from the third year, at most 50 % (bp) -/
def dzAbatementBp (heldMonths : Nat) : Int := min 5000 (500 * max 0 (((heldMonths / 12 : Nat) : Int) - 2))

def dzPropertyGain (d : Disposal) : Int := pos (d.proceeds - d.cost - min d.costs (d.cost * 3 / 10))

def dzSoleHome (g : CanonGlobal) (d : Disposal) : Bool :=
  d.mainHome && !(g.assets.any fun a => a.kind.isRealEstate)

def dzPropertyTax (g : CanonGlobal) (d : Disposal) (b : Int) : Int :=
  let t := b * 1500 / 10000
  if dzSoleHome g d then t / 2 else t

def capital : Family :=
  { name := "1100 الضريبة على الدخل الإجمالي: فوائض القيمة", covers := [.pit],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      g.disposals.zipIdx.filterMap fun (d, i) =>
        if d.kind.isRealEstate then
          some (charge .pit "IRG: plus-value de cession immobilière" (dzPropertyGain d)
            (fun v => v - v * dzAbatementBp d.heldMonths / 10000) (fun b => dzPropertyTax g d b)
            (event := s!"disposal {i + 1}")
            (statute := "CIDTA art. 77, 78, 79 (5 % a year from the 3rd year, at most 50 %), 104-5-a (15 % final; 50 % less for the only home; LF 2025 art. 8)"))
        else if d.kind == .unlistedShares && !d.listed then
          some (charge .pit "IRG: plus-value de cession d'actions" (pos (d.proceeds - d.cost - d.costs)) pos
            (fun b => b * 1500 / 10000) (event := s!"disposal {i + 1}")
            (statute := "CIDTA art. 77 bis, 79 bis, 104-5-b (15 % final)"))
        else none }

def capitalUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then [] else
  (if g.disposals.any (fun d => d.kind == .listedShares || (d.kind.isShares && d.listed)) then
    ["IRG on share gains: listed shares not charged (the exemption for securities listed on the stock exchange was not read)"] else []) ++
  (if g.disposals.any (·.kind.isRealEstate) then
    ["IRG on property gains: costs taken within 30 % of the cost (art. 78 caps acquisition and upkeep costs only); 'from the third year' read as 5 % per full year beyond two; a gift or inheritance value replacing the cost must be given as cost; Mourabaha/Ijara and co-ownership exits (art. 80 bis 1) not identified"] else []) ++
  (if g.disposals.any (fun d => d.kind == .unlistedShares && !d.listed) then
    ["IRG on share gains: the 5 % rate for a reinvested gain (art. 104-5-b) not applied (reinvestment not in the record)"] else [])

#guard dzAbatementBp 36 == 500 && dzAbatementBp 24 == 0 && dzAbatementBp 240 == 5000

end DzGlobal
