import HrTax.Household

/-!
# Croatia 2025: the model against official figures (kernel-checked)

A. Porezna uprava, "Osobni odbitak ili neoporezivi dio plaće" (`refs/pu_osobni_odbitak.txt`), table "Tablica
   koeficijenata i iznosa osnovnog osobnog odbitka": monthly and annual amounts; also EUROMOD CR Y16 Table 2.17 (2025).
B. Porezna uprava, "Obrtnici paušalisti" (`refs/pu_pausalisti.txt`): annual paušalni dohodak and 12 % tax per class
   (the classes and rate are those of Pravilnik NN 1/24 + 16/25, applied "za 2025. godinu i nadalje", NN 16/25 čl. 4).
C. Naredba NN 137/24 čl. 3-7: bases as average wage × the ZD coefficients.
D. Porezna uprava, "Primjeri izračuna za mlade", 2025 tables, Grad Samobor 18 %/27 % (`refs/kalk/mladi.txt`).
E. EUROMOD CR Y16 Table 2.11 (2b): doplatak amounts and thresholds as % of the proračunska osnovica 441,44 €.
All amounts in cents.
-/

namespace HrTax
open TaxKernel

/-! ## A. Personal allowance table -/
/-- Monthly increments for the 1st … 9th child: 300,00 420,00 600,00 840,00 1.140,00 1.500,00 1.920,00 2.400,00 2.940,00. -/
theorem pu_child_monthly :
    childCoefs.map (fun k => k * basicPA / 10) = [30000, 42000, 60000, 84000, 114000, 150000, 192000, 240000, 294000] := by
  decide
/-- Annual: 3.600,00 5.040,00 7.200,00 10.080,00 13.680,00 18.000,00 23.040,00 28.800,00 35.280,00. -/
theorem pu_child_annual :
    childCoefs.map (fun k => 12 * (k * basicPA / 10)) =
      [360000, 504000, 720000, 1008000, 1368000, 1800000, 2304000, 2880000, 3528000] := by decide
/-- Basic 600,00 / 7.200,00; dependant 300,00 / 3.600,00; I 180,00 / 2.160,00; I* 600,00 / 7.200,00. -/
theorem pu_other_rows :
    (basicPA, 12 * basicPA, coefDependant * basicPA / 10, 12 * (coefDependant * basicPA / 10),
      coefDisability * basicPA / 10, 12 * (coefDisability * basicPA / 10), coefDisability100 * basicPA / 10) =
    (60000, 720000, 30000, 360000, 18000, 216000, 60000) := by decide
/-- The dependant income limit "(3.600,00 eura)". -/
theorem pu_dependant_limit : dependantLimit = 360000 := by decide
/-- Cumulative: two children 720 €/month (EUROMOD Table 2.17: 300 + 420). -/
theorem euromod_two_children : childAllowanceMonthly 2 = 72000 := by decide

/-! ## B. Paušal classes (PU table: dohodak and "GODIŠNJI PAUŠALNI POREZ NA DOHODAK (12 %)") -/
def pausalProbe : List Int := [1130000, 1530000, 1990000, 3060000, 4000000, 5000000, 6000000]
theorem pu_pausal_income :
    pausalProbe.map pausalIncome = [169500, 229500, 298500, 459000, 600000, 750000, 900000] := by decide
theorem pu_pausal_tax :
    pausalProbe.map pausalTax = [20340, 27540, 35820, 55080, 72000, 90000, 108000] := by decide
/-- The lower edge of each class (one cent above the previous limit) is in that class. -/
theorem pu_pausal_lower_edges :
    [1130001, 1530001, 1990001, 3060001, 4000001, 5000001].map pausalIncome =
      [229500, 298500, 459000, 600000, 750000, 900000] := by decide
/-- PU table, druga djelatnost: MO I 7,5 %, MO II 2,5 %, ZO 7,5 % of class 1 (1.695,00): 127,13 / 42,38 / 127,13. -/
theorem pu_pausal_second_activity :
    (rnd (750 * 169500), rnd (250 * 169500), rnd (750 * 169500)) = (12713, 4238, 12713) := by decide

/-! ## C. Naredba NN 137/24 -/
theorem naredba_bases :
    (avgWage * 65 / 100, avgWage * 40 / 100, avgWage * 6, avgWage * 6 * 12, avgWage * 38 / 100) =
    (seMonthlyBase, pausalMonthlyBase, maxMonthlyBase, maxAnnualBase, 68324) := by decide

/-! ## D. Porezna uprava young-worker examples 2025 (Samobor 18 %/27 %) -/
def samobor : Rates := ⟨1800, 2700⟩
/-- A Samobor employee of age `a` with annual pay `w` euros (single, no children). -/
def youngCase (a : Nat) (w : Int) : Person :=
  { age := a, wageDoh := C * w - eeContribYear true (C * w), receipts := C * w }

/-- 16.000 / 24.000 / 32.000 €: contributions 3.200 / 4.800 / 6.400, tax before relief 1.008 / 2.160 / 3.312,
under 25: tax 0 (all as printed). In whole euros: the model rounds each month's contribution to the cent (one twelfth
of 16.000 € is 1.333,33 €), the examples take 20 % of the year (differences of 4 cents). -/
theorem pu_young25 :
    ([16000, 24000, 32000].map fun w => (eur (eeContribYear true (C * w)), eur ((youngCase 24 w).taxBefore samobor),
      eur ((youngCase 24 w).tax samobor))) =
    [(3200, 1008, 0), (4800, 2160, 0), (6400, 3312, 0)] := by decide
/-- Age 26-30: 504,00 and 1.656,00 as printed; 24.000 €: 1.080,00 (printed 1.008,00: FINDINGS F3 (c)). -/
theorem pu_young30 :
    ([16000, 24000, 32000].map fun w => eur ((youngCase 28 w).tax samobor)) = [504, 1080, 1656] := by decide
/-- 9.000 € (750 €/month): ZD čl. 21.a reduces the pillar-I base by 275 €: contributions 1.305 €, not 1.680/1.800;
age 26-30 owes 44,55 € (printed 0: FINDINGS F3 (a)); under 25 owes 0 (as printed). -/
theorem pu_young_9000 :
    (eeContribYear true 900000, (youngCase 28 9000).base, (youngCase 28 9000).tax samobor,
      (youngCase 24 9000).tax samobor) = (130500, 49500, 4455, 0) := by decide

/-! ## E. Doplatak za djecu (EUROMOD Table 2.11 (1b)/(2b): BUB 441,44 € × %) -/
def bub : Int := 44144
theorem euromod_dzd_amounts :
    [1400, 1250, 1100, 900, 700].map (fun p => divR .halfUp (bub * p) BP) = dzdBrackets.map (·.2) := by decide
theorem euromod_dzd_limits :
    [2000, 4000, 6000, 10000, 14000].map (fun p => divR .halfUp (bub * p) BP) = dzdBrackets.map (·.1) := by decide

/-- Round 3: the pre-March-2024 doplatak amounts and limits equal the ZDD percentages (NN 138/06 čl. 3, NN 58/18 čl. 3)
of the proračunska osnovica 441,44 €, rounded half up to the cent. -/
theorem dzd_old_from_statute :
    [900, 750, 600].map (fun p => divR .halfUp (44144 * p) BP) = dzdBracketsOld.map (·.2) ∧
    [1633, 3366, 7000].map (fun p => divR .halfUp (44144 * p) BP) = dzdBracketsOld.map (·.1) := by decide

end HrTax
