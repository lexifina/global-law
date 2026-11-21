import SETax.Theorems

/-!
# The findings of FINDINGS.md as theorems (Stockholm 2025, `decide` on the statute model)

Each statement names the household (one adult: `person p stateFirst age wages selfEmployment pension capital
gifts`) and the amounts; `total` = every income tax, fee and contribution after credits.
-/

namespace SETax
open TaxKernel

/-- F1. The allmän pensionsavgift floor (lag 1994:1744 4 §): one more krona of pay at 24 899 kr costs 1 700 kr. -/
theorem f1_fee_notch :
    (person p2025 false 40 24899 0 0 0 0).total = 0 ∧ (person p2025 false 40 24900 0 0 0 0).total = 1700 := by
  decide

/-- F2. A 70-year-old earning 200 000 kr pays no income tax at all, yet the 14 000 kr pensionsavgift is not
reimbursed: its credit only displaces jobbskatteavdrag (67 kap. 8 §: 29 493 kr) that the municipal tax could not
absorb anyway (13 509 kr used). Everything paid is the fee plus public service and begravningsavgift. -/
theorem f2_old_worker_fee_is_a_cost :
    let r := person p2025 false 70 200000 0 0 0 0
    r.municipalNet = 0 ∧ r.stateNet = 0 ∧ r.fee = 14000 ∧ r.used.pension = 14000 ∧
      r.jsaAmount = 29493 ∧ r.used.jobb = 13509 ∧ r.total = 14000 + 899 + 62 := by
  decide

/-- F2 (under 66): at 40 000 kr of pay the jobbskatteavdrag alone (4 620 kr) equals the municipal tax, so the
2 800 kr fee credit only displaces it: the fee is paid in full. -/
theorem f2_young_low_earner :
    let r := person p2025 false 40 40000 0 0 0 0
    r.fee = 2800 ∧ r.jsaAmount = 4620 ∧ r.municipalTax = 4620 ∧ r.municipalNet = 0 ∧
      r.total = r.fee + r.publicServiceFee + r.burialFee := by
  decide

/-- F3. 67 kap. 2 § does not say which tax a two-tax credit consumes first. Pay 55 000 kr and 20 000 kr of
interest: municipal first (Skatteverket's table method) 10 122 kr; state first 6 602 kr; 3 520 kr apart. -/
theorem f3_credit_order :
    (person p2025 false 40 55000 0 0 20000 0).total = 10122 ∧
    (person p2025 true 40 55000 0 0 20000 0).total = 6602 := by
  decide

/-- F4. 63 kap. 3 a § (SFS 2024:1131): at 1,965 pbb the särskilt belopp jumps up by 0,003973 pbb (233,64 kr):
a 70-year-old with 115 600 kr of pension pays 64 kr less than with 115 500 kr. -/
theorem f4_extra_jump : extraN 58800 115543 - extraN 58800 115542 = 2338367000 := by decide

theorem f4_negative_marginal :
    (person p2025 false 70 0 0 115500 0 0).total = 11812 ∧ (person p2025 false 70 0 0 115600 0 0).total = 11748 := by
  decide

/-- F12. Interest between spouses (67 kap. 10 §: 30 % up to 100 000 kr, 21 % above, per person): 300 000 kr of
interest on one return gives a credit of 72 000 kr, split equally 2 × 40 500 = 81 000 kr. -/
theorem f12_interest_split : deficitCredit p2025 300000 = 72000 ∧ 2 * deficitCredit p2025 150000 = 81000 := by
  decide

/-- F13. Gifts (67 kap. 22, 26 §§): giving 2 000 kr instead of 1 999 kr returns 500 kr; the cap of 3 000 kr is per
person, so a couple giving 24 000 kr saves 3 000 kr more by giving half each. -/
theorem f13_gifts :
    giftCredit 1999 = 0 ∧ giftCredit 2000 = 500 ∧ 2 * giftCredit 12000 - giftCredit 24000 = 3000 := by decide

/-- F10. Individual taxation: 1 300 000 kr of pay on one return costs 479 878 kr; split equally 2 × 150 523. -/
theorem f10_spouse_split :
    (person p2025 false 40 1300000 0 0 0 0).total = 479878 ∧ (person p2025 false 40 650000 0 0 0 0).total = 150523 := by
  decide

/-- F14. Owner-manager: 131 420 kr of company profit beyond a salary of 475 100 kr. As salary (31,42 %
arbetsgivaravgifter): 100 000 kr more pay, taxes 126 171 − (at 475 100) ...; as dividend above the gränsbelopp (20,6 %
bolagsskatt, then inkomstslaget tjänst without jobbskatteavdrag or pensionsavgift, IL 57 kap. 20 §): 104 346 kr.
Net to the owner: 448 929 kr by salary, 451 958 kr by dividend. -/
theorem f14_owner_dividend_beats_salary :
    575100 - (person p2025 false 40 575100 0 0 0 0).total = 448929 ∧
    475100 + 104346 - (person p2025 false 40 475100 0 104346 0 0).total = 451958 := by
  decide

/-- F15. Löneväxling: above the brytpunkt (643 100 kr) 10 000 kr less pay saves 5 067 kr now (50,67 %). -/
theorem f15_salary_sacrifice :
    (person p2025 false 40 653100 0 0 0 0).total - (person p2025 false 40 643100 0 0 0 0).total = 5067 := by
  decide

end SETax
