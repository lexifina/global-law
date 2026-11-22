# US findings

## FT review, third pass (2026-11-21; dev cases only; IMPROVE_FT.md "Third pass")
- **US FTR-1 (1200).** 26 U.S.C. § 172 (a) (2) (B): post-2017 NOLs at most 80 % of taxable income (the entity's losses read as post-2017, flagged). `us_ft_cit_ekwo_grid` dev 592 -> 688 / 688; 1200 on 96 of 103,970 US dev lines.

- **US FTS-1, Tax-Calculator employer (`us_ft_employer_taxcalc_grid`, software error / scope; FT review 4).** No FUTA: the model
  is +$41,8-42 on every case (26 U.S.C. § 3301: 6,0 %, less the § 3302 credit 5,4 %, on the first $7 000).

## FT review, fifth pass (2026-11-21)
- **US FTS-2 (DarnOsint v2 CGT)**: the near-constant +$12-16 k is the alternative minimum tax the page omits (exemption
  phased out above $626 350 of AMTI; 26 % on wages without the standard deduction). Hand checks of e00220, e00809, e00126
  put the model within 0,3 % of § 55 and the tool within 0,4 % of the tax without AMT.
- **US FTC-1 (PolicyEngine)**: its QBI sources include `rental_income`; § 199A needs a qualified trade or business.
