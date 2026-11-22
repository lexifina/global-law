import TaxKernel.World

/-!
# Indonesia: Pajak Penghasilan of a resident individual (employee), tax year 2025

Statutes (pajak.go.id, the Directorate General of Taxes; files in `id/law/`):
* UU 7/2021 (Harmonisasi Peraturan Perpajakan), official copy "Salinan UU Nomor 7 Tahun 2021" (sha256 4e4be3e2…):
  Pasal 17 (1) a as amended: "sampai dengan Rp60.000.000,00 5% / di atas Rp60.000.000,00 sampai dengan
  Rp250.000.000,00 15% / di atas Rp250.000.000,00 sampai dengan Rp500.000.000,00 25% / di atas Rp500.000.000,00 sampai
  dengan Rp5.000.000.000,00 30% / di atas Rp5.000.000.000,00 35%"; Pasal 7 (1) PTKP "paling sedikit" Rp54.000.000
  (self), Rp4.500.000 (married), Rp54.000.000 (wife whose income is joined), Rp4.500.000 per dependant "paling banyak 3
  (tiga) orang"; the Penjelasan of Pasal 7 (1) worked example: a husband with a wife employed by one employer and four
  children gets "Rp72.000.000,00 {Rp54.000.000,00 + Rp4.500.000,00 + (3 x Rp4.500.000,00)}" while the wife gets
  "Rp54.000.000,00" at withholding (checked by `#guard`).
* PMK 101/PMK.010/2016 Pasal 1 (pajak.go.id page, sha256 97ad65b5…): the same PTKP amounts, "mulai berlaku pada Tahun
  Pajak 2016" (no later PTKP regulation found in the DGT's catalogue search for "penghasilan tidak kena pajak").
* PMK 168/2023 (sha256 ae7db3db…), Pasal 10 (2) "biaya jabatan … 5% (lima persen) dari penghasilan bruto, paling
  banyak Rp6.000.000,00 … setahun"; Pasal 11 (2) "biaya pensiun … 5% … paling banyak Rp2.400.000,00 … setahun";
  Pasal 8 (4) "penghasilan kena pajak … dibulatkan ke bawah hingga ribuan rupiah penuh"; Pasal 9 (2) a "bagi karyawati
  kawin, sebesar Penghasilan Tidak Kena Pajak untuk dirinya sendiri".
Unit: the husband's return carries the family PTKP; a wife's employment income from one employer is taxed apart with
her own PTKP (Penjelasan Pasal 7 (1)). Investment income (interest, dividends, rent, share sales) is subject to final
taxes set by government regulations that were not read: flagged and excluded. BPJS employee contributions (JHT, JP,
JKN) are not modelled (regulations not read) and are therefore not deducted either.
-/

namespace IdTax
open TaxKernel

/-- Pasal 17 (1) a (UU 7/2021). -/
def sched : Schedule :=
  Schedule.ofList [(0, 500), (60000000, 1500), (250000000, 2500), (500000000, 3000), (5000000000, 3500)]

def ptkpSelf : Int := 54000000
def ptkpMarried : Int := 4500000
def ptkpDependant : Int := 4500000
def maxDependants : Nat := 3

def ptkp (married : Bool) (deps : Nat) : Int :=
  ptkpSelf + (if married then ptkpMarried else 0) + ptkpDependant * (min deps maxDependants : Nat)

/- The Penjelasan example: husband, wife employed elsewhere, four children: 72 000 000; joined: 126 000 000. -/
#guard ptkp true 4 = 72000000 ∧ ptkp true 4 + ptkpSelf = 126000000

def jabatan (gross : Int) : Int := min 6000000 (divR .down (500 * gross) BP)
def pensiun (gross : Int) : Int := min 2400000 (divR .down (500 * gross) BP)

/- PMK 168/2023 Pasal 5 (3): the employee's income includes "d. pembayaran iuran jaminan kecelakaan kerja dan iuran
jaminan kematian ... yang dibayarkan oleh pemberi kerja; e. pembayaran iuran jaminan pemeliharaan kesehatan ... yang
dibayarkan oleh pemberi kerja; f. pembayaran premi asuransi kesehatan, asuransi kecelakaan kerja, asuransi jiwa ...
yang dibayarkan oleh pemberi kerja"; Pasal 10 (1) b: deductible "iuran terkait program pensiun dan hari tua, yang
terkait dengan gaji, yang dibayar oleh Pegawai melalui pemberi kerja" (JHT, JP). The rates are in government
regulations not read (PP 44, 45, 46/2015; the BPJS Kesehatan Perpres): optional inputs in basis points of wages,
`idEmployerInsuranceRate` (employer-paid JKK + JKM + health contributions and premiums) and `idEmployeeRetirementRate`
(employee JHT + JP); caps on the contribution bases are not applied. -/
/-- Employee contributions, compulsory for workers of employers other than the state (W4, texts from JDIH Kemnaker,
`id/law/w4/`): PP 46/2015 Pasal 16 (1) "Iuran JHT ... sebesar 5,7% ... dari Upah, dengan ketentuan: a. 2% (dua persen)
ditanggung oleh Pekerja" (pp46_2015.pdf, sha256 ac289e99...); PP 45/2015 Pasal 28 (1) "Iuran Jaminan Pensiun wajib
dibayarkan setiap bulan", (3) b "1% (satu persen) dari upah ditanggung oleh Peserta"; Pasal 29 (2) "Batas paling tinggi
Upah ... untuk tahun 2015 ditetapkan sebesar Rp7.000.000,00 ... setiap bulan", (3)-(4) adjusted every year by BPJS
Ketenagakerjaan by 1 + the previous year's GDP growth and announced by it (pp45_2015.pdf, sha256 cadb2b02...). The
2025 announcement was not reached: the cap is the input `idJpWageCapMonthly`, default the statute's own Rp7,000,000
(flagged). `idEmployeeRetirementRate` (W2) still overrides JHT + JP with one uncapped rate. -/
structure Bpjs where
  employerRate : Int := 0
  override : Option Int := none
  jhtRate : Int := 200
  jpRate : Int := 100
  jpCapMonthly : Int := 7000000

def employerPaid (b : Bpjs) (w : Int) : Int := divR .down (b.employerRate * pos w) BP
/-- Employee JHT + JP for wages `w` paid evenly over 12 months. -/
def employeeRetirement (b : Bpjs) (w : Int) : Int :=
  match b.override with
  | some r => divR .down (r * pos w) BP
  | none => perPeriod 12 (fun m => divR .down (b.jhtRate * pos m) BP + divR .down (b.jpRate * min (pos m) b.jpCapMonthly) BP) w

/-- Net employment income: gross (wages + employer-paid insurance) less biaya jabatan on that gross, less the
employee's own pension / JHT contributions. -/
def empNeto (b : Bpjs) (w : Int) : Int :=
  if w ≤ 0 then 0 else
  let g := w + employerPaid b w
  pos (g - jabatan g - employeeRetirement b w)

/-- Net income of one person (employment + pension + business net). -/
def neto (b : Bpjs) (a : Adult) : Int :=
  empNeto b a.wages + pos (a.pension - pensiun a.pension) + a.selfEmployment

/- Without the inputs the employment net is wages less biaya jabatan, as before; with 0.54 % employer JKK + JKM
+ 4 % health and 3 % employee JHT + JP on 120 million: gross 125.448 million, jabatan 6 million, less 3.6 million. -/
#guard empNeto { jhtRate := 0, jpRate := 0 } 120000000 = 114000000
#guard empNeto { employerRate := 454, override := some 300 } 120000000 = 125448000 - 6000000 - 3600000
/- Default: 10 million a month: JHT 200,000 + JP 1 % of the capped 7,000,000 = 70,000 a month. -/
#guard employeeRetirement {} 120000000 = 12 * (200000 + 70000)

/-- W5 pattern A (2026-11-20): BPJS Kesehatan employee share. Perpres 82/2018 as amended by Perpres 64/2020
(peraturan.go.id/files/ps64-2020.pdf, `id/law/w5/`), Pasal 30 (1) "Iuran bagi Peserta PPU yaitu sebesar 5% (lima persen)
dari Gaji atau Upah per bulan ... b. 1% (satu persen) dibayar oleh Peserta"; Pasal 32 (1) "Batas paling tinggi Gaji atau
Upah per bulan ... Rp12.000.000,00"; (2) the lowest base is the regional minimum wage (not applied: region-specific).
Perpres 59/2024 (third amendment) leaves Pasal 30 and 32. Not deductible: PMK 168/2023 Pasal 10 (1) b deducts only the
pension / JHT contributions. Reported as employeeSocial only; input `"w5Contrib": false` drops it. -/
def kesehatanMonth (m : Int) : Int := divR .down (100 * min (pos m) 12000000) BP
def kesehatan (w : Int) : Int := perPeriod 12 kesehatanMonth (pos w)

#guard kesehatan 120000000 = 1200000 ∧ kesehatan 600000000 = 12 * 120000

def taxOn (pkp : Int) : Int := sched.tax Rule.unitDown (toMultiple .down 1000 (pos pkp))

def out (c : Canon) : Out :=
  let kids := c.nChildren
  let b : Bpjs := { employerRate := (c.int? "idEmployerInsuranceRate").getD 0,
                    override := c.int? "idEmployeeRetirementRate",
                    jpCapMonthly := (c.int? "idJpWageCapMonthly").getD 7000000 }
  let neto := neto b
  let a1 := c.adult1
  let (t, ti) : Int × Int := match c.adult2? with
    | none => let ti := pos (neto a1 - ptkp false kids); (taxOn ti, ti)
    | some a2 =>
      if c.married then
        -- wife (second adult) taxed apart on her employment income with her own PTKP; any other income joined
        let wifeEmp := empNeto b a2.wages
        let wifeOther := pos (a2.pension - pensiun a2.pension) + a2.selfEmployment
        let ti1 := pos (neto a1 + wifeOther - ptkp true kids - (if wifeOther > 0 && a2.wages = 0 then ptkpSelf else 0))
        let ti2 := pos (wifeEmp - ptkpSelf)
        (taxOn ti1 + taxOn ti2, ti1 + ti2)
      else
        let ti1 := pos (neto a1 - ptkp false kids)
        let ti2 := pos (neto a2 - ptkp false 0)
        (taxOn ti1 + taxOn ti2, ti1 + ti2)
  Out.make c "ID" "IDR" t
    (employeeSocial := sumInts (c.adults.map fun a => employeeRetirement b a.wages) +
      (if (c.bool? "w5Contrib").getD true then sumInts (c.adults.map fun a => kesehatan a.wages) else 0))
    (detail := [Out.d "taxableIncome" ti,
      Out.d "bpjsKesehatanEmployee" (if (c.bool? "w5Contrib").getD true then sumInts (c.adults.map fun a => kesehatan a.wages) else 0)])
    (unsupported := (if c.interest + c.dividends + c.capitalGains + c.rentalIncome ≠ 0 then
        ["interest, dividends, rent and share gains: final taxes under government regulations not read; excluded"] else []) ++
      ["BPJS: employee JHT 2 % (PP 46/2015 Pasal 16) and JP 1 % (PP 45/2015 Pasal 28) deducted (PMK 168/2023 Pasal 10 (1) b) and reported as employeeSocial; JP base capped at idJpWageCapMonthly, default the statute's 2015 Rp7,000,000 (the BPJS-indexed 2025 cap not read); wages taken as Upah (basic + fixed allowances); employer-paid JKK/JKM/health contributions are income (Pasal 5 (3) d-f) but their rates (risk class, Perpres) not read: idEmployerInsuranceRate, default 0; employee health contribution 1 % up to Rp12 million a month (Perpres 64/2020 Pasal 30, 32) reported, not deducted; its regional-minimum-wage floor not applied",
       "the wife's PTKP when her employment income must be joined with the husband's (Pasal 8 (2)-(3)) not modelled"])

def country : Country := { code := "ID", name := "Indonesia (PPh orang pribadi)", currency := "IDR", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end IdTax
