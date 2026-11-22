import ThGlobal.Pit

/-!
# Thailand 2025: corporate income tax and withholding on foreign companies (1200)

Revenue Code: the official text on rd.go.th was not read for this package (B, rates from the RD tables).
* **s. 67 + Royal Decree No. 530 (B.E. 2554, extended)**: 20 % of net profit; SMEs (paid-up ≤ 5 m baht, revenue ≤ 30 m;
  flag `sme`): 0 % to 300,000, 15 % to 3 m, 20 % above (`citSme`).
* **s. 70**: foreign juristic companies not carrying on business in Thailand: 15 % on s. 40 (2)-(6) income (interest,
  royalties, services), 10 % on dividends (Royal Decree).
-/

namespace ThGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Corporate income tax",
    sched := Schedule.flat 2000 }

def citStatute : String := "ประมวลรัษฎากร มาตรา 67; บัญชีอัตราภาษีเงินได้ (2) (ก) ร้อยละ 20 (พ.ร.บ. แก้ไขเพิ่มเติมประมวลรัษฎากร (ฉบับที่ 42) พ.ศ. 2559)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 1000, statute := "ประมวลรัษฎากร มาตรา 70; บัญชีอัตราภาษีเงินได้ (2) (ค): เงินได้ตามมาตรา 40 (4) (ข) ร้อยละ 10" },
      { kind := .interest, rateBp := 1500, statute := "ประมวลรัษฎากร มาตรา 70; บัญชีอัตราภาษีเงินได้ (2) (ข): ร้อยละ 15 (มาตรา 40 (4) (ก))" },
      { kind := .royalty, rateBp := 1500, statute := "ประมวลรัษฎากร มาตรา 70; บัญชีอัตราภาษีเงินได้ (2) (ข): ร้อยละ 15 (มาตรา 40 (3))" },
      { kind := .services, rateBp := 1500, statute := "ประมวลรัษฎากร มาตรา 70; บัญชีอัตราภาษีเงินได้ (2) (ข): ร้อยละ 15 (มาตรา 40 (2), paid from or in Thailand)" }] }

def citSme : CorpRegime := { name := "Corporate income tax (SME)", sched := Schedule.ofList [(0, 0), (300000, 1500), (3000000, 2000)] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["SME schedule only through `citSme` (flag not routed); the top-up tax (Emergency Decree B.E. 2567) not modelled"] else [])

#guard cit.citTax { profit := 1000000 } == 200000
#guard citSme.citTax { profit := 1000000 } == 105000
#guard wht.amount { kind := .dividend, amount := 1000 } == 100
#guard wht.amount { kind := .interest, amount := 1000 } == 150
#guard wht.amount { kind := .royalty, amount := 1000 } == 150
#guard wht.amount { kind := .services, amount := 1000 } == 150

end ThGlobal.Corporate
