import TaxKernel.World2

/-!
# Iran: tax on salary income (مالیات بر درآمد حقوق), year 1404 (21 March 2025 - 20 March 2026)

Access tier B (rescue pass 3). Statute text: **Budget Law 1404 (Part One), Note 1, paragraph ز** (قانون بودجه سال
۱۴۰۴ کل کشور (بخش اول), تبصره ۱ بند «ز»), approved by the Majlis in open session on 8 Bahman 1403 (27 January
2025), confirmed with amendments to other notes by the Expediency Council on 10 Bahman 1403, sent by the Speaker's
letter No. 235/75483 of 13 Bahman 1403 and promulgated for execution under art. 123 of the Constitution on 14 Bahman
1403 (2 February 2025). Read on the scan of the promulgated text carrying the www.dotic.ir watermark and the Majlis
Speaker's letterhead (101 pages, pp. 10-11), downloaded from the copy on ekhtebar.ir
(`www.ekhtebar.ir/wp-content/uploads/2025/02/قانون-بودجه-۱۴۰۴.pdf`, identical to the Internet Archive capture
20250215212522; sha256 561363b2…; `ir/law/rescue3/budget1404_part1_dotic_scan.pdf`); the transcription on the same
site (Internet Archive capture 20251115083103) matches the page images. B and not A: the official hosts (dotic.ir,
rc.majlis.ir, rrk.ir, qavanin.ir) refused or challenged both machines, so the official scan came through a private
legal-news site; the Direct Taxes Act itself (arts. 84-86, 91, 131) was not reached.

Note 1(ز): "در سال ۱۴۰۴، مجموع پرداختی به کارکنان دولتی و غیردولتی تحت هر عنوان ... از یک یا چند منبع ... پس از
کسر معافیت‌های مصرح در قوانین، به شرح زیر مشمول مالیات بر درآمد حقوق است:
۱- سقف معافیت مالیاتی سالانه موضوع ماده (۸۴) قانون مالیات‌های مستقیم در سال ۱۴۰۴ مبلغ دو میلیارد و هشتصد و
هشتاد میلیون (۲.۸۸۰.۰۰۰.۰۰۰) ریال تعیین می‌شود.
۲- نرخ مالیات بر مجموع درآمد حقوق اشخاص حقیقی به شرح زیر می‌باشد:
۲-۱- نسبت به مازاد ... (۲.۸۸۰.۰۰۰.۰۰۰) ریال تا ... (۳.۶۰۰.۰۰۰.۰۰۰) ریال، ده درصد (۱۰٪)
۲-۲- ... (۳.۶۰۰.۰۰۰.۰۰۰) ریال تا ... (۴.۵۶۰.۰۰۰.۰۰۰) ریال، پانزده درصد (۱۵٪)
۲-۳- ... (۴.۵۶۰.۰۰۰.۰۰۰) ریال تا ... (۶.۰۰۰.۰۰۰.۰۰۰) ریال، بیست درصد (۲۰٪)
۲-۴- ... (۶.۰۰۰.۰۰۰.۰۰۰) ریال تا ... (۸.۰۰۰.۰۰۰.۰۰۰) ریال، بیست و پنج درصد (۲۵٪)
۲-۵- نسبت به مازاد هشت میلیارد (۸.۰۰۰.۰۰۰.۰۰۰) ریال، به بالا، سی درصد (۳۰٪)"
University faculty, full-time physicians and judges stay under DTA art. 85 (as amended 1394/4/31); overtime, welfare,
productivity and similar extras are taxed at a flat 10 % "پس از اعمال سقف معافیت به تناسب"; para. 3 replaces the
art. 86 withholding with the tax organisation's system. Note 1(ث) of the same law: the art. 101 exemption for business
income (مشاغل) and the art. 57 exemption for rents of people without other income are 2,000,000,000 rials.

Direct Taxes Act (structure only; version gap): the English translation on the Iran Data Portal (Syracuse
University, irandataportal.syr.edu/section-3-income-tax; it prints art. 85 with the 1388 (2009) figure of
42,000,000 rials, so it is the text as amended up to about 1388, before the amendment of 31 Tir 1394): art. 82
(salary tax on income for work in Iran), art. 83 (salary and job benefits "after calculating all the exemptions"),
art. 84 (an annual exemption, now fixed for 1404 by Note 1(ز)(1)), art. 86 (withholding), art. 91 ("Income from
salary will be tax exempt in the following cases: ... 5. Pensions, retirement allowances, stipends, termination
compensation and benefits, ... dependents' pension ..."; 10. year-end bonuses up to 1/12 of the art. 84 exemption;
14. the armed forces), art. 92 (50 % off in less developed regions). The 1394 wording of these articles was not
reached; pensions are treated as exempt under art. 91(5) as printed there.

Household mapping: `wages` = an adult's total salary income of the year from all sources, after the exemptions "مصرح
در قوانین" (none of which was reached: e.g. the employee's social-security share is not deducted). Each person is
taxed alone (the clause taxes "اشخاص حقیقی"). Pensions: exempt (art. 91(5), pre-1394 text). Not modelled (flagged when present): business income (DTA
art. 131 rates not reached), rents, dividends, interest, the art. 85 groups and the 10 % extras. Rounding: none
printed; whole rials, down.

W5 pattern A (2026-11-20): the insured person's social-security premium, 7 % of wages, is reported (employeeSocial)
and NOT deducted (whether DTA art. 91 in its 1394 wording exempts it was not reached). **قانون تأمین اجتماعی مصوب
۱۳۵۴/۴/۳ (Social Security Act 1975)**, as consolidated with its amendments on ekhtebar.ir (private legal publisher's
transcription of the statute; the official hosts rc.majlis.ir, dotic.ir, qavanin.ir and tamin.ir refused or
challenged a second machine; `ir/law/w5/`), art. 28 (1): "حق‌بیمه از اول مهرماه تا پایان سال ۱۳۵۴ به میزان بیست و هشت
درصد مزد یا حقوق است که هفت درصد آن به عهده بیمه‌شده و هجده درصد به عهده کارفرما و سه درصد به‌وسیله دولت تأمین
خواهد شد"; تبصره ۱: from 1355 the employer's share is 20 % "و با احتساب سهم بیمه‌شده و کمک دولت کل حق‌بیمه به سی
درصد مزد یا حقوق افزایش می‌یابد" (the insured's 7 % unchanged); art. 2 (5): wages include "هرگونه وجوه و مزایای
نقدی یا غیر نقدی مستمر"; art. 36: the employer withholds the insured's share. The Act prints no ceiling: the annual
maximum monthly wage subject to the premium is set administratively (the 1404 figure was not reached) and is NOT
applied, so the premium is overstated for wages above it (flagged). `"w5Contrib": false` restores the pre-W5 model.
-/

namespace IrTax
open TaxKernel

/-- Budget Law 1404 (Part One) Note 1(ز)(1): annual exemption of DTA art. 84 for 1404 (rials). -/
def exemption : Int := 2880000000

/-- Note 1(ز)(2): rates on the whole salary income, by the excess over each printed amount (rials, bp). -/
def salarySched : Schedule := Schedule.ofList
  [(0, 0), (2880000000, 1000), (3600000000, 1500), (4560000000, 2000), (6000000000, 2500), (8000000000, 3000)]

def salaryTax (w : Int) : Int := salarySched.tax Rule.unitDown (pos w)

-- The clause's own figures: nothing up to the exemption; at each printed limit the tax is the sum of the band widths
-- times their rates.
#guard salaryTax 2880000000 = 0
#guard salaryTax 3600000000 = 720000000 * 10 / 100
#guard salaryTax 4560000000 = 72000000 + 960000000 * 15 / 100
#guard salaryTax 6000000000 = 72000000 + 144000000 + 1440000000 * 20 / 100
#guard salaryTax 8000000000 = 72000000 + 144000000 + 288000000 + 2000000000 * 25 / 100
#guard salaryTax 10000000000 = 1004000000 + 2000000000 * 30 / 100
-- the marginal rate on the rial above 8,000,000,000 is 30 %
#guard salarySched.rate 8000000000 = 3000 ∧ salarySched.rate 7999999999 = 2500

/-- Note 1(ث): the art. 101 exemption for business income in 1404 (cited only; the art. 131 rates were not reached). -/
def businessExemption : Int := 2000000000

/-- W5 pattern A: Social Security Act 1354 art. 28 (1), the insured's 7 % of wages (no ceiling in the Act). -/
def ssoInsuredPct : Int := 7
def ssoInsured (w : Int) : Int := pos w * ssoInsuredPct / 100
/- art. 28 (1): 28 % = 7 % + 18 % + 3 %; تبصره ۱: 30 % = 7 % + 20 % + 3 %. -/
#guard ssoInsuredPct + 18 + 3 = 28 ∧ ssoInsuredPct + 20 + 3 = 30 ∧ ssoInsured 1000000000 = 70000000

def out (c : Canon) : Out :=
  let per := c.adults.map fun a => salaryTax a.wages
  let t := sumInts per
  let w5 := (c.bool? "w5Contrib").getD true
  let es := if w5 then sumInts (c.adults.map fun a => ssoInsured a.wages) else 0
  Out.make c "IR" "IRR" t
    (employeeSocial := es)
    (detail := [Out.d "salaryTaxAdult1" (per.headD 0), Out.d "salaryTaxAdult2" ((per.drop 1).headD 0),
      Out.d "annualExemption" exemption,
      Out.dStr "note" "Budget Law 1404 (Part One) Note 1(ز): 2,880,000,000 rials exempt (DTA art. 84), 10/15/20/25/30 % above 2.88/3.6/4.56/6/8 bn rials; per person, all salary sources together"])
    (unsupported := [if w5 then "employee social-security premium 7 % (SSA 1354 art. 28) reported without the administrative wage ceiling (not reached) and not deducted; the other exemptions 'مصرح در قوانین' (DTA art. 91 etc.) not reached" else "employee social-security contributions and the other exemptions 'مصرح در قوانین' (DTA art. 91 etc.): not reached, nothing deducted; employeeSocial = 0",
      "Direct Taxes Act read only in a pre-1394 English translation (academic host); the 1404 figures are from the budget-law clause"] ++
      (if c.adults.any (fun a => a.selfEmployment ≠ 0) then ["business income (DTA art. 131 rates; art. 101 exemption 2,000,000,000 rials by Note 1(ث)): not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: exempt under DTA art. 91(5) as printed before the 1394 amendment (version gap); no tax computed"] else []) ++
      (if c.dividends ≠ 0 ∨ c.interest ≠ 0 then ["dividends / interest: not modelled"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rental income (DTA arts. 52-59; Note 1(ث) exemption): not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: not modelled"] else []))

def country : Country :=
  { code := "IR", name := "Iran", currency := "IRR", year := "1404 (21 March 2025 - 20 March 2026)", compute := out }

theorem salarySched_progressive : salarySched.progressive = true := by decide

end IrTax
