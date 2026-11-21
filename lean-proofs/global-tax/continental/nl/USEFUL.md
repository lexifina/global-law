# Netherlands 2025: what this work is useful for

Evidence: FINDINGS.md (F-numbers), CATALOGUE.md (K), NOVEL.md (N), Lean theorems in `lean/NLTax/Theorems.lean`.

## For a taxpayer
1. **Partners choose who reports box 3 and box 2 (art. 2.17).** Book box-3 wealth on a partner with little income:
   her algemene heffingskorting, which is otherwise lost, absorbs the box-3 tax (€ 1.676 on € 250.000 of shares, K3).
   Split box-2 dividend so both use the 24,5 % band (€ 4.969 at € 154.000 of dividend, K2).
2. **Watch the 1 January wealth test of the kindgebonden budget.** One euro over € 179.429 (partners) or € 141.896
   (single) of box-3 wealth on 1 January loses the whole budget (€ 4.225 for a couple at € 45.000 with two children,
   K6/N5). Repaying an own-home mortgage before 1 January moves the money out of box 3.
3. **A parent of a child under 12 who is the lower earner pays no income tax or premies on the first € 30.000**
   (F10/N3, Lean `parent_no_levy`): extra hours there cost only the household's kgb afbouw (7,1 %).
4. **Between € 76.821 and € 129.077 every extra euro of wage costs 56 cents** (49,50 % + 6,51 % arbeidskorting
   afbouw, Lean `levy_step_top`); for a single parent 63 cents (F9). Pension contributions and other deductions save at
   that rate, but art. 2.10 lid 2 limits the value of most deductions (own home, persoonsgebonden aftrek) to 37,48 %.
5. **Time variable pay around € 129.077.** Above it the marginal rate falls from 56 % (63 % for a parent) to 49,5 %:
   putting a bonus into one year instead of spreading it saved a single employee € 3.540 and a single parent € 8.234
   over two years in our runs (F17). The withholding tables leave up to € 3 a year to pay at assessment (F13).

## For an adviser
1. **Owner-managers:** gebruikelijk loon € 56.000 (Wet LB art. 12a) plus dividend beats an all-salary payout by € 5.000
   (profit € 100.000) to € 17.600 (€ 250.000), K1; split the dividend with a partner (K2).
2. **Self-employed vs employee at € 60.000:** € 2.278 less levy as an ondernemer (zelfstandigenaftrek + MKB-
   winstvrijstelling, net of the Zvw 5,26 %), K7; employer-side premiums are not in either figure.
3. **Partners born before 1963:** the non-earner's algemene heffingskorting is still paid out (art. 8.9): € 3.068 (K9).
4. **Box 3 costs more than 36 %** of the deemed return for clients in an afbouw band (42-49 %, F18), and over 100 % of
   a low actual return (tegenbewijs). **Box 3 2025 rates are definitive only after the year** (art. 10.6ter): 1,37 % savings, 5,88 % other assets,
   2,70 % debts (set in February 2026); an art. 5.2 text read during 2025 shows other years' rates (`law/`).
5. **AOW-aged clients:** the Belastingdienst's AHK table gives € 1.536 (statute € 1.534,86) and drops € 1,37 to zero at
   € 76.818 (F12): use the statute when a figure must reconcile to the cent.

## For the Dutch government
1. **Fix the kolom III rounding** (F6): the statutory box-1 and box-2 tax falls when income crosses € 38.441, € 76.817
   and € 67.804 (Lean `t210_not_monotone`). Round kolom III up, or state the tariff as rates per band.
2. **Index related amounts together** (F7, F8): the arbeidskorting never reaches its € 5.599 maximum (max € 5.598,96)
   and the algemene heffingskorting runs € 3 into the top bracket, because each amount is rounded separately.
3. **Correct the texts** (F14, F15): Wet LB art. 22a lid 2 c uses "arbeidsinkomen", undefined in the Wet LB (since
   2020); Wet IB art. 10.6b lid 3 cites "artikel 8,10".
4. **Publications:** the rekenvoorschriften 2025 §2.2.5 example still uses Lmax € 125.010 (2025: € 129.330, F11); the
   AOW-age AHK table has a € 1,37 notch the statute does not have (F12); the OECD's 2025 kinderbijslag lines are € 5,12
   short for two children (F2).
5. **Non-refundable kortingen below € 30.000** (F10): for parents of young children the IACK and arbeidskorting are
   partly wasted up to € 30.000, so they give no extra work incentive there; if that range matters, a refundable part
   would be needed.
