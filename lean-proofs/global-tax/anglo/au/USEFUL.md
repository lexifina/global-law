# Australia: what this work is useful for (2024-25 / 2025-26)

## A taxpayer
1. Families near $80,000 or $117,194 of income: one dollar more can cost $1,833 (FTB A supplement, two children) or
   $3,884 (FTB B for a one-earner family or sole parent). A deductible gift or work expense counts against these
   limits; salary sacrifice and rental losses do not (they are added back). Evidence: F4, F5, F15;
   `notch_ftb_supplement`, `notch_ftb_b_primary_limit`, `sacrifice_blocked_ftb`.
2. Low earners ($19,000-$45,000) have several hundred dollars too much withheld every year, by design of the PAYG
   tables: up to $765 in 2024-25 at $27,820. Lodge a return. Evidence: F9, `sched1_max_over_2025`.
3. Singles over $97,000 (families over $194,000) without hospital cover pay at least $970 of surcharge the moment
   they cross the line. Evidence: F6, `notch_mls_single`.
4. HELP debtors: the 2024-25 cliffs (up to $629 for a dollar) are gone from 2025-26. Evidence: F7.

## An adviser
1. Investment income held by the lower-earning spouse is the largest lever for most couples ($17,512 on $60,000 at
   $180,000), and it can also restore FTB B by bringing the higher earner under the primary-earner limit (moving
   $5,000 saved $5,483.60). Evidence: K5, F5, `split_crosses_ftb_b`.
2. For an owner-manager, franked dividends to one shareholder cost more than salary + SG; split between spouses they
   save $8,811 on $200,000. Evidence: K9.
3. A sole parent receiving any Parenting Payment (Single) gets FTB A without its income test; the end of that
   residual is a ~$1,700 cliff (annualised). Evidence: F3, `notch_income_support_passport`.
4. FTB is annual on ATI: alternating high and low years can be worth up to $13,424 over two years for a family
   (lead). Evidence: F14.

## The government
1. Index the FTB A supplement's $80,000 limit (FA Act Sch 1 cl 38A(1A) is missing from Sch 4 cl 2) or taper the
   supplement: it is a $916.15-per-child notch that catches more families every year. Evidence: F4.
2. Update PAYG Schedule 1's Medicare levy parameters: the instruments in force from 1 July 2024 to 2026 still use
   2023-24 thresholds; and consider building LITO into scale 2 (low earners are over-withheld by up to $765-$844).
   Evidence: F8, F9; `sched1_never_under`.
3. Publish the indexed amounts in the law (or a legislative instrument): the FA Act and PHI Act print base amounts
   ($100,000, $98,988, $90,000) that have not applied for years. Evidence: F11.
4. Legislate the Medicare low-income thresholds before the year starts (2025-26's were enacted on its last day).
   Evidence: F13.
5. Correct the ATO's HELP example 4 (5.5 % x $99,736 = $5,485.48). Evidence: F10.

## A researcher
A checkable model of 2024-25 (and 2025-26) on the shared kernel: rates as a kernel `Schedule` (progressive, convex,
Lipschitz 45 %: kernel theorems instantiated), the Medicare levy as a `Surcharge` proved equal to the statute's
wording, LITO as two `Credit`s proved equal to s. 61-115, FTB income tests as `Taper`s; the OECD's 2025 lines
reproduced 40/40 once its two assumptions are stated; all 240 PAYG sample amounts reproduced.
