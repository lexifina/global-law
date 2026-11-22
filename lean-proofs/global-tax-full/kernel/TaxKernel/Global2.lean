import TaxKernel.Global
import TaxKernel.Global2.Basket
import TaxKernel.Global2.DatedVat
import TaxKernel.Global2.ExciseRule
import TaxKernel.Global2.CorpRule
import TaxKernel.Global2.TransferX
import TaxKernel.Global2.Assets
import TaxKernel.Global2.Vehicle
import TaxKernel.Global2.WhtState
import TaxKernel.Global2.Stack
import TaxKernel.Global2.Sector
import TaxKernel.Global2.Employer
import TaxKernel.Global2.Advance
import TaxKernel.Global2.Fx
import TaxKernel.Global2.Zone
import TaxKernel.Global2.Customs
import TaxKernel.Global2.LocalRate
import TaxKernel.Global2.GoodsValue
import TaxKernel.Global2.Zakat
import TaxKernel.Global2.Lease

/-!
# TaxKernel.Global2 (2.9.0, 2026-11-21): parts asked for in cmp20/global/KERNEL_REQUESTS.md

`import TaxKernel.Global2` (it imports the whole of `TaxKernel.Global`). Nothing imports it: `TaxKernel.Global` and
every 2.0 name and signature are unchanged, so a country project that does not import it builds and runs exactly as
before. Names live in `TaxKernel.Global` (all new, none used by a builder at the time of writing).

* `Basket`: `SpendX` (per-line date, mass, degree Plato, sugar, sub-category, origin read from the line's JSON),
  `consumptionX`, ISO dates (`dayOfYear?`, `scaleDays`).
* `DatedVat`: VAT with dated rate periods; dated lines to their period, undated lines spread by days.
* `ExciseRule`: ad valorem on the retail price, the price net of VAT or the value before excise and VAT; per kg/tonne,
  per degree Plato, sugar bands; strength, origin, sub-category and date selection; `exciseRuleFamily`; from 2.4.0
  price tiers by the retail unit price (`minUnitPrice`, `maxUnitPrice`, `priceQty`, `priceDen`, `priceBase`).
* `CorpRule`: CIT with a minimum tax with floor and cap (`MinimumTax`), profit rounding (`step`), taxable ownership
  share read from the line.
* `TransferX` (2.1.1): what a gift or inheritance is made of (`"assetKind"`, `"realPropertyValue"` on the transfer
  record), `realPropertyPart`, `Transfer.restrict`, `PartDuty` (a flat duty by relation on a part: MA CGI art. 133).
* `Assets` (2.4.0): the asset record (`assetJson`), floor area `"areaM2"` (`assetAreaM2`, `assetsArea`), rate tables on
  a quantity (`QtyTable`: bands, marginal steps, started steps, `ofCeilings`), a tax per m² (`AreaTax`).
* `Vehicle` (2.4.0): the vehicle record (`Vehicle`, `CanonGlobal.vehicles`: assets of kind vehicle and a company's
  `company.vehicles`, with kind, cm³, kW, CV, CO2, mass, fuel, first registration, seats, value, months held), annual
  and registration taxes from tables on those attributes (`VehicleTax`, `vehicleTaxCharges`, `vehicleTaxFamily`,
  `vehicleTaxUnknown`, `vehicleTaxUnmatched`).
* `WhtState` (2.4.0): recipient facts on a payment abroad (`PaymentX`: `"recipientState"`, `"lowTax"`,
  `"nonCooperative"`, `"euEea"`, `"treaty"` on the payment record), withholding rules conditional on them (`StateRule`
  with `tests` and a required `ifUnknown := .general | .presume | .gradeC`), `StateWht` (`ofWht`: the same charges as a
  2.0 `Wht`), `StateWht.notes` for `unsupported`.
* `Stack` (2.5.0): income stacked on the 1.x income tax (capital gains at the marginal rate: inclusion rate, annual
  exclusion, asset and income kinds; `StackRule`, `StackField`, `stackCharges`, `GlobalModel.withStack`): the charge is
  the 1.x PIT with the included amount less the 1.x PIT without it, booked under 1100; the 1.x line is unchanged.
* `Vehicle` (2.5.0 additions): the Euro emission class (`"euroClass"`: attributes `.euroClass`, `.euroStage`) and the
  list price (`"listPrice"`: `.listPrice`).
* `Sector` (2.5.0): the company's sector (`company.sector`, canonical names `Sector.canonical`; `companySectors`) and
  CIT rates by sector (`SectorCorp`: a general `CorpRule` and `bySector` rules; what an absent sector means is declared,
  `ifAbsent := .general | .gradeC`).
* `Vehicle` (2.6.0 additions, FT reviewer 6): when in the year the vehicle was first registered (`"firstRegMonth"`, or a
  whole `"firstRegDate"`: attributes `.firstRegMonth`, `.firstRegDay`) and a first-registration date window on a tax
  (`regFromDate`, `regToDate`); a window the vehicle's record cannot decide is grade C, never guessed.
* `Stack` (2.6.0 additions, R1 Europe pass 10): `shareBp` (a share of the stacked charge) and `mode := .averageRate key`
  (the included amount at the global rate of the 1.x line with the amount: LU L.I.R. art. 131 (1) c, half the global
  rate, with `shareBp := 5000`).
* `Employer` (2.6.0, R4-14-1): the employer of each household adult (`"employerPayroll"`, `"employerEmployees"`,
  `"employerSector"`, `"employerRiskClass"` on `household.adults`; `employerOf`) and per-employer levies on the adult's
  wages (`EmployerLevy`: rules with tests on the employer and a required `ifUnknown`, as `StateRule`).
* `Advance` (2.6.0, Asia-Pacific PK): advance income tax collected on a sale or purchase (rate by the size of the base and
  the date of the transaction), credited against the year's income tax (`AdvanceTax`, `credit := .adjustable |
  .refundable | .final`, `advanceTaxFamily`, `advanceTaxUnknown`).
* `Fx` (2.7.0, R4-17-1): amounts fixed in a foreign currency, converted only at an explicitly declared rate (`FxRate` with
  its source and date: the entity's `"fxRates"` input, else a rate the rule declares; `fxFor`, `fxUnknownLine`,
  `QtyTable.amountFx`); no rate: grade C, never a built-in rate.
* `Vehicle` (2.7.0 additions, R1 Europe pass 15, R4-17-1): `VehicleTax.proRataDays` and `dayPeriods` (days held, from
  `"heldFrom"`/`"heldTo"` or the first-registration day), `partWindows` (a part only for the first N months after first
  registration: SE CO2 × months), `currency`/`fxRate` (amounts in US$ and the like).
* `Zone` (2.7.0, R1 Europe pass 15): asset facts `"zoneValueM2"`, `"buildYear"`, `"floor"`, `"frontages"` (`AssetFact`,
  `assetZoneValueM2`) and `ZoneTax` (area × the zone-value band's table × coefficients, or a table on the objective value
  area × zone value × coefficients; a missing fact: grade C). GR ENFIA.
* `Stack` (2.7.0 additions, FT reviewer 7): `StackRule.dateFrom` / `dateTo` on the record's `"date"` (an undated item a
  window needs: grade C) and `rateFromStack` (the global rate of the whole stack: LU art. 99ter quarter / half).
* `Customs` (2.8.0, OECD 5123): basket-line `"hs"`, `"origin"`, `"customsValue"` (`CustomsX`, `consumptionC`) and import
  duties (`TariffRule`: MFN tariff lines by HS heading, the longest prefix winning; specific duties per unit or kg;
  preferences by origin (`TariffPreference`: CARICOM, MERCOSUR, the EU, ECOWAS, SACU …); the duty in the VAT base;
  `GlobalModel.withCustoms`); an imported line without `"hs"`, or without the origin a preference needs, is grade C.
* `LocalRate` (2.8.0): local taxes whose rate each municipality sets inside a national framework (`LocalTax`: base,
  reliefs, statutory minimum and maximum), the rate from the entity's `"localRates"` input (rate, source, date,
  municipality), else a declared municipality rate with its source and date (`LocalRateDecl`), else grade C; a rate
  outside the range is flagged, never used; framework-only taxes book the range as a grade-C note
  (`GlobalModel.withLocalTaxes`).
* `Stack` (2.8.0 addition, R1 Europe pass 17): `StackRule.undatedIfTaxable` (an undated item the rule taxes at 0 does not
  block a date window).
* `Zone` (2.8.0 addition, R1 Europe pass 17): `ZoneTax.coefsAt` (an asset's coefficient list chosen from its record).
* `Customs` (2.9.0 additions, R2-GAP-1): `TariffLine` / `TariffPreference` `validFrom` / `validTo` on the line's `"date"`
  (an undated line whose windows give different duties: grade C), `TariffSurcharge` (additional duties by origin, HS heading
  and date, added to the MFN or preferential duty; `exceptPreferences`), `TariffLine.currency` with `TariffRule.fxRate`
  (specific duties in a foreign currency); a rule using none of them computes as 2.8.0 (`TariffRule.outcome_v28`).
* `GoodsValue` (2.9.0, R3-GAP-2; MY/MM manufacturer's value): basket-line `"containerMl"`, `"exFactoryValue"` /
  `"manufacturerValue"` (`LineValueX`, `consumptionV`) and `GoodsValueTax` (a rate or marginal value bands, per container
  or per litre, on the price, the price net of VAT, the value before the tax, the customs value or the manufacturer's
  value; a missing fact: grade C; `GlobalModel.withGoodsValueTaxes`).
* `Zakat` (2.9.0, R3-GAP-1): adult `"zakatLiable"`, `"religion"`, `"zakatExemptDeclared"`, `"zakatableWealth"`; company
  `"muslimOwnershipBp"`, `"zakatLiable"`, `"zakatBase"`; `ZakatRule` (2.5 % above a declared nisab; wealth, income or field
  bases; companies by the Muslim-held share; a presumption only when the model declares it, else grade C;
  `GlobalModel.withZakat`).
* `Lease` (2.9.0, MENA BH): the tenant on a let asset (`"lessee"` record or `"tenantNationality"` / `"tenantNational"` /
  `"tenantResident"`; `"rent"`), on a rent line, and the adults' `"nationality"` / `"national"` / `"resident"`; `RentLevy`
  (a rate on the rent when the lessee tests hold, a required `ifUnknown`; `GlobalModel.withRentLevies`).
-/
