import json
D = 'C:/Users/alany/Documents/tax-formalization-data/taxcourt/estate/cases/'
M = json.load(open('C:/Users/alany/Documents/tax-formalization-data/taxcourt/estate/work/meta.json'))


def src(i):
    m = M[i]
    return {"dawson_case_url": m['dawson_case_url'], "dawson_document_api": m['api_url'],
            "dawson_docket_entry_id": m['docketEntryId'], "document_title": m['documentTitle'],
            "raw_text": f"raw/{i}.txt", "raw_pdf": f"raw/{i}.pdf", "retrieved": "2026-11-11"}


cases = {}
cases['mikel'] = {
    "id": "tcmemo-2015-64", "slug": "mikel",
    "caption": "Israel Mikel v. Commissioner; Erna Mikel v. Commissioner (consolidated)",
    "citation": "T.C. Memo. 2015-64", "date": "2015-04-06", "docket_numbers": ["16538-13", "16563-13"],
    "judge": "Lauber", "tax_type": "gift", "gift_year": 2007, "source": src('mikel'),
    "posture": "Cross-motions for partial summary judgment (facts deemed established for the motions).",
    "found_facts": [
        {"fact": "Notice determined against each petitioner a deficiency and a 6651(a)(1) addition",
         "values": {"deficiency_each": 268950, "addition_6651a1_each": 67238},
         "snippet": "determined against each petitioner a tax deficiency of $268,950 and a late-filing addition to tax under section 6651(a)(1) of $67,238.",
         "locator": "pp. 1-2"},
        {"fact": "Each spouse's 2007 gift to the trust", "values": {"gift_each": 1631000, "total_transferred": 3262000},
         "snippet": "During 2007 each petitioner made to a family trust a gift with an asserted value of $1,631,000.",
         "locator": "p. 2; total $3,262,000 at p. 3"},
        {"fact": "Annual exclusions claimed: 60 beneficiaries x $12,000",
         "values": {"claimed_exclusion_each": 720000, "per_donee_exclusion_2007": 12000, "beneficiaries": 60},
         "snippet": "each petitioner claimed under section 2503(b) an annual exclusion of $720,000. The claimed annual exclusions of $720,000 were based on the contention that each petitioner's gift included a $12,000 gift of a present interest to each of the trust's 60 beneficiaries.",
         "locator": "p. 2"},
        {"fact": "Gift-splitting consent; no gift tax reported after unified credit",
         "snippet": "The Forms 709 included consents by each petitioner that the gifts were to be \"considered as made one-half by each of [us].\" ... After application of unified credits, the Forms 709 reported no gift tax due.",
         "locator": "pp. 7-8"},
        {"fact": "2007 per-donee exclusion",
         "snippet": "for gifts made during 2007, the exclusion was $12,000 per donee. Rev. Proc. 2006-53, sec. 3.32",
         "locator": "pp. 9-10"},
        {"fact": "Returns filed late (Dec. 15, 2011) for 2007",
         "snippet": "Neither petitioner timely filed Form 709 ... for 2007. On December 15, 2011, after being contacted by the IRS, each petitioner submitted a separate Form 709",
         "locator": "p. 7"}],
    "issue": "Whether the gifts to the trust were gifts of present interests (Crummey withdrawal rights) qualifying for the sec. 2503(b) annual exclusion, given an in terrorem clause and a beth din arbitration provision.",
    "holding": "Present interests; petitioners' motion for partial summary judgment granted, respondent's denied. Each beneficiary held a legally enforceable withdrawal right. The exact number of beneficiaries was left open (fn. 2: 'not material to this opinion'); valuation not at issue.",
    "stated_tax_figures": {"deficiency_each": 268950, "addition_6651a1_each": 67238},
    "recomputation": {
        "what": "Deficiency = gift tax on 1,631,000 with no exclusions, minus gift tax on 1,631,000 - 720,000 (zero after unified credit); assumes no prior taxable gifts (opinion mentions none).",
        "steps": [
            "2007 sec. 2001(c) table: tentative tax(x) = 555,800 + 45% x (x - 1,500,000) for x > 1,500,000",
            "tentative tax(1,631,000) = 555,800 + 58,950 = 614,750",
            "sec. 2505 credit (2007, $1,000,000 exemption) = tentative tax(1,000,000) = 345,800",
            "gift tax with exclusions disallowed = 614,750 - 345,800 = 268,950 == stated deficiency",
            "with 60 x 12,000 = 720,000 exclusions: taxable gift 911,000 < 1,000,000 -> tax 0 (matches 'no gift tax due')",
            "sec. 6651(a)(1) at 25% max: 0.25 x 268,950 = 67,237.50 -> $67,238 == stated addition"],
        "reconciles": True,
        "court_outcome_effect": "Holding sustains the exclusions in principle, so the deficiency falls to 0 if 60 present-interest donees are established (number left open)."},
    "judgment_vs_computation": {
        "judgment": ["legal question: present vs future interest (enforceability of Crummey right)",
                     "number of beneficiaries not finally resolved"],
        "computation": ["exclusion = beneficiaries x per-donee amount",
                        "taxable gift, tentative tax, unified credit, late-filing addition"]},
    "caveats": ["Summary-judgment opinion; final decision figures are not in the opinion.",
                "Assumes no pre-2007 taxable gifts; opinion is silent."]}

cases['spizzirri'] = {
    "id": "tcmemo-2023-25", "slug": "spizzirri",
    "caption": "Estate of Richard D. Spizzirri, Deceased, John J. McAtee, Jr., Personal Representative v. Commissioner",
    "citation": "T.C. Memo. 2023-25", "date": "2023-02-28", "docket_numbers": ["19124-19"], "judge": "Urda",
    "tax_type": "estate (+ adjusted taxable gifts)", "date_of_death": "2015-05-12", "source": src('spizzirri'),
    "found_facts": [
        {"fact": "Lifetime payments by donee and year",
         "values": {"daughter": {"2014": 15000}, "stepdaughter": {"2014": 25700, "2015": 21000},
                    "Huper": {"2011": 27111, "2012": 19175, "2013": 24981, "2015": 12226},
                    "Lawner": {"2013": 37500, "2014": 22714, "2015": 30000},
                    "Pacziga": {"2011": 59661, "2012": 16600, "2013": 13400},
                    "Seiler": {"2011": 24100, "2012": 25052},
                    "Mardovina": {"2013": 22800, "2014": 50750, "2015": 26600},
                    "Preston": {"2013": 42900, "2014": 30455},
                    "Levine": {"2012": 58550, "2013": 34400, "2014": 7350}},
         "snippet": "He paid one of his daughters $15,000 in 2014 and one of his stepdaughters $25,700 and $21,000 in 2014 and 2015, respectively ... (5) $58,550, $34,400, and $7,350 during 2012, 2013, and 2014, respectively, to Vivien Levine.",
         "locator": "pp. 5-6"},
        {"fact": "Annual exclusion amounts", "values": {"2011": 13000, "2012": 13000, "2013": 14000, "2014": 14000, "2015": 14000},
         "snippet": "the annual exclusion was $13,000 during 2011 and 2012 and $14,000 for 2013 through 2015.", "locator": "p. 9"},
        {"fact": "Return as filed",
         "values": {"taxable_estate": 30805768, "tax_due": 10150307, "adjusted_taxable_gifts_reported": 0},
         "snippet": "The return showed a gross estate exceeding $81 million, a taxable estate of $30,805,768, and tax due of $10,150,307. The Estate reported on the return zero dollars in adjusted taxable gifts.",
         "locator": "p. 7"},
        {"fact": "Deductions claimed (the first four disallowed by the notice)",
         "values": {"claims_stepchildren": 3000000, "easthampton_residence_right": 623255, "aspen_deck_repairs": 314890,
                    "easthampton_maintenance_5yr": 455166, "nyc_emergency_repairs_not_listed_as_disallowed": 22034},
         "snippet": "It deducted as claims against the estate both the $3 million in payments to Ms. Lueders's children and the $623,255 appraised value ... emergency repairs of $22,034 for the New York City apartment and $314,890 for two decks at the Aspen property ... $455,166 for five years of estimated \"property maintenance\" expenses",
         "locator": "p. 7"},
        {"fact": "Payments and notice",
         "values": {"extension_payment": 11800000, "refund_issued": 1649693, "deficiency": 2251189,
                    "addition_6651a1_noticed": 450238, "adjusted_taxable_gifts_determined": 193441},
         "snippet": "the Estate remitted an estate tax payment of $11,800,000 ... the IRS issued a refund of $1,649,693 ... determining a deficiency in estate tax of $2,251,189 as well as an addition to tax under section 6651(a)(1) of $450,238 ... increased Mr. Spizzirri's lifetime adjusted taxable gifts from zero to $193,441.",
         "locator": "pp. 6-7"},
        {"fact": "Filing dates",
         "snippet": "return was due on February 10, 2016 ... extending the deadline to August 12, 2016 ... On November 29, 2016 ... the Estate filed Form 706",
         "locator": "pp. 6-7"},
        {"fact": "Agreed addition", "values": {"addition_6651a1": 120299},
         "snippet": "Consistent with the parties' agreed calculations, the addition to tax shall be reduced to $120,299.",
         "locator": "p. 19 fn. 11; p. 20"}],
    "issues": ["Whether lifetime payments were taxable gifts (adjusted taxable gifts)",
               "sec. 2053(a)(3)/(c)(1)(A): $1M payments to each stepchild and residence right under prenup deductible as claims",
               "sec. 2053(a)(2): Aspen deck repairs and Easthampton maintenance",
               "sec. 6651(a)(1) addition"],
    "holding": "IRS determinations sustained subject to concessions: payments were gifts; prenup claims not contracted for adequate and full consideration (and not marital-deduction property); repair/maintenance expenses not deductible; no reasonable cause; addition reduced to $120,299 per agreed computation; decision under Rule 155.",
    "stated_tax_figures": {"tax_per_return": 10150307, "deficiency": 2251189, "addition_final": 120299},
    "recomputation": {
        "steps": [
            "Return check: 2015 BEA 5,430,000 (not stated in opinion; Rev. Proc. 2014-61); tentative tax(x) = 345,800 + 40% x (x - 1,000,000). tt(30,805,768) = 12,268,107; credit = tt(5,430,000) = 2,117,800; tax = 10,150,307 == return figure (exact)",
            "sec. 6651(a)(1) check: total tax 10,150,307 + 2,251,189 = 12,401,496; less timely payment 11,800,000 = 601,496 net unpaid; extended due date Aug 12 -> filed Nov 29, 2016 = 4 months or part -> 20%; 0.20 x 601,496 = 120,299 == agreed addition",
            "Adjusted taxable gifts from the found payments (per donee per year excess over exclusion): 2011 71,872; 2012 67,377; 2013 92,581; 2014 74,619; 2015 35,600; total 342,049"],
        "reconciles": "partial",
        "non_reconciling": [
            "Found-fact ATG 342,049 > the 193,441 determined in the notice; the court sustained the notice figure and would not look behind it (fn. 5). At least 13 different subsets of donee-years sum to exactly 193,441, so the IRS's selection cannot be identified.",
            "40% x (disallowed deductions 4,393,311 + ATG 193,441) = 1,834,701 != deficiency 2,251,189; the gap (~1,041,220 of base) comes from adjustments not described in the opinion."]},
    "judgment_vs_computation": {
        "judgment": ["whether payments were gifts vs compensation", "bona fides/adequate consideration of prenup claims",
                     "whether repairs were necessary administration expenses", "reasonable cause"],
        "computation": ["annual-exclusion netting per donee-year", "tentative tax / unified credit", "late-filing addition"]},
    "caveats": ["The deficiency itself is not reproducible from the opinion alone; the return tax and the agreed sec. 6651 addition are."]}

cases['rowland'] = {
    "id": "tcmemo-2025-76", "slug": "rowland",
    "caption": "Estate of Billy S. Rowland, Deceased, James A. Park, Executor v. Commissioner",
    "citation": "T.C. Memo. 2025-76", "date": "2025-07-15", "docket_numbers": ["12736-22"], "judge": "Urda (Chief Judge)",
    "tax_type": "estate (DSUE/portability)", "date_of_death": "2018-01-24",
    "predeceased_spouse_date_of_death": "2016-04-08", "source": src('rowland'),
    "found_facts": [
        {"fact": "DSUE computed on Fay's (late) return",
         "values": {"bea_2016": 5450000, "estimated_gross_estate": 3000000, "estimated_total_allowable_deductions": 1500000,
                    "adjusted_taxable_gifts": 237438, "dsue": 3712562},
         "snippet": "It calculated a DSUE amount of $3,712,562, derived from the following inputs: Basic Exclusion Amount $5,450,000 Estimated Gross Estate (3,000,000) Estimated Total Allowable Deductions 1,500,000 Adjusted Taxable Gifts (237,438) Total DSUE 3,712,562",
         "locator": "p. 3"},
        {"fact": "Fay's return filing",
         "snippet": "moved the due date from January 9 to July 8, 2017 ... mailed the Form 706 ... on December 29, 2017, which the Internal Revenue Service (IRS) received on January 2, 2018.",
         "locator": "pp. 2-3"},
        {"fact": "Specific bequests / payments", "values": {"specific_bequests": 950000, "payments_to_13_beneficiaries": 1401000},
         "snippet": "specific bequests totaling $950,000 ... payments to 13 named beneficiaries, totaling $1,401,000", "locator": "pp. 2-3"},
        {"fact": "Billy's return",
         "values": {"bea_2018": 11180000, "applicable_exclusion_claimed": 14892562, "net_estate_tax": 4477555,
                    "refund_claimed": 22445, "prior_payment": 4500000},
         "snippet": "Billy's Return added this amount to the 2018 basic exclusion amount, $11,180,000, resulting in an applicable exclusion of $14,892,562. Billy's Return reported a net estate tax of $4,477,555 and claimed a refund of $22,445 based on a previous payment of $4,500,000.",
         "locator": "p. 4"}],
    "issue": "Whether Fay's estate made a valid portability election (late return under the Rev. Proc. 2017-34 safe harbor; 'complete and properly prepared' return despite estimated values).",
    "holding": "No valid election; Billy's estate cannot use any DSUE. Partial summary judgment for the Commissioner; substantial compliance and equitable estoppel rejected.",
    "stated_tax_figures": {"net_estate_tax_reported": 4477555, "deficiency": "not stated in opinion"},
    "recomputation": {
        "steps": [
            "DSUE as claimed (sec. 2010(c)(4)): 5,450,000 - [(3,000,000 - 1,500,000) + 237,438] = 3,712,562 == stated",
            "Applicable exclusion as claimed: 11,180,000 + 3,712,562 = 14,892,562 == stated",
            "Holding: DSUE = 0 -> applicable exclusion = 11,180,000",
            "Incremental tax from losing DSUE at 40% marginal rate: 0.40 x 3,712,562 = 1,485,025 (derived, not stated)",
            "Implied tax base if net tax = tt(B) - tt(14,892,562) with no other credits: B = 26,086,450 (derived; the return may include other credits)"],
        "reconciles": "DSUE and applicable exclusion exact; deficiency not in opinion"},
    "judgment_vs_computation": {"judgment": ["validity/completeness of return; substantial compliance; estoppel"],
                                "computation": ["DSUE formula, applicable exclusion, effect of DSUE = 0"]},
    "caveats": ["Fay's gross estate and deductions were estimates on her return; the DSUE inputs are reported figures, not court findings.",
                "Order on partial summary judgment; final deficiency not determined in this opinion."]}

cases['macelhenny'] = {
    "id": "tcmemo-2023-33", "slug": "macelhenny",
    "caption": "Estate of Bernard J. MacElhenny, Jr., Deceased, Donor, Michael P. MacElhenny and Catherine MacElhenny Dann, Co-Executors v. Commissioner (consolidated estate and gift cases)",
    "citation": "T.C. Memo. 2023-33", "date": "2023-03-15", "docket_numbers": ["12981-19", "12982-19"],
    "judge": "Kerrigan (Chief Judge)", "tax_type": "gift (sec. 2512(b) part-sale) + estate (sec. 2053 claims)",
    "date_of_death": "2015-04-27", "gift_year": 2012, "source": src('macelhenny'),
    "found_facts": [
        {"fact": "Deficiencies", "values": {"gift_2011": 188000, "gift_2012": 3335609, "estate": 3992656},
         "snippet": "Respondent determined gift tax deficiencies ... for 2011 and 2012 of $188,000 and $3,335,609, respectively. Respondent also determined a $3,992,656 estate tax deficiency.",
         "locator": "pp. 1-2"},
        {"fact": "El Mercado sale terms (Oct. 26, 2012)",
         "values": {"stated_price": 4750000, "mortgage_assumed": 1614391, "credit": 3135609,
                    "union_bank_judgment_purchase": 2650000, "offset": 485609},
         "snippet": "for a stated price of $4,750,000. The purchase agreement provided that Mr. MacElhenny and Ms. Dann assumed an existing $1,614,391 mortgage and received a $3,135,609 credit for the remainder. The credit comprised (1) the $2,650,000 paid to acquire the Union Bank judgment and (2) a $485,609 offset against the Union Bank judgment.",
         "locator": "p. 7"},
        {"fact": "Stipulated value", "values": {"fmv_each_50pct": 3100000, "mortgage_each_50pct": 807196},
         "snippet": "The parties have since stipulated that each 50% interest in the El Mercado property was worth $3,100,000 and encumbered by a $807,196 mortgage at the time of sale.",
         "locator": "p. 8"},
        {"fact": "Adjusted taxable gifts increase", "values": {"atg_increase": 3497609},
         "snippet": "Respondent increased the estate's adjusted taxable gifts by $3,497,609.", "locator": "p. 8"},
        {"fact": "sec. 2053 deductions claimed (disallowed)", "values": {"union_bank_judgment": 3638083, "westamerica_judgment": 1007320},
         "snippet": "They claimed a $3,638,083 deduction attributable to the remaining value of the Union Bank judgment. They also claimed a $1,007,320 deduction attributable to the Westamerica Bank judgment. Respondent disallowed both deductions.",
         "locator": "p. 8"}],
    "issues": ["sec. 2053(a)(3): deductibility of consent judgments assigned to the children",
               "sec. 2512(b): whether the children received taxable gifts in the discounted purchase"],
    "holding": "Both sec. 2053 deductions disallowed (debts extinguished when the children paid $2,650,000 and $432,000; assignments not bona fide). Consideration limited to mortgage + $2,650,000; each child received a $967,805 taxable gift. Decisions under Rule 155.",
    "stated_tax_figures": {"gift_each_child": 967805},
    "recomputation": {
        "steps": [
            "Value transferred (whole property) = 2 x 3,100,000 = 6,200,000 (stipulated)",
            "Consideration recognized = 1,614,391 + 2,650,000 = 4,264,391 (the $485,609 judgment offset is not consideration)",
            "sec. 2512(b) gift = 6,200,000 - 4,264,391 = 1,935,609; per child / 2 = 967,804.50 -> $967,805 == holding",
            "Gross-estate deductions removed = 3,638,083 + 1,007,320 = 4,645,403"],
        "reconciles": "gift amount exact; deficiencies not reproducible (2012 annual exclusions, prior gifts, and the $3,497,609 ATG figure are not explained)"},
    "judgment_vs_computation": {
        "judgment": ["bona fides / arm's length of judgment assignments", "whether debt offset counts as consideration"],
        "computation": ["sec. 2512(b) excess of value over consideration (value itself stipulated)"]},
    "caveats": ["The $3,335,609 2012 gift 'deficiency' and the $3,497,609 ATG increase are not explained in the opinion."]}

cases['steinberg'] = {
    "id": "tc-145-7", "slug": "steinberg", "caption": "Jean Steinberg, Donor v. Commissioner",
    "citation": "145 T.C. 184 (2015) (145 T.C. No. 7)", "date": "2015-09-16", "docket_numbers": ["23865-11"],
    "judge": "Kerrigan", "tax_type": "gift (net gift with assumed sec. 2035(b) estate tax)", "gift_year": 2007,
    "gift_date": "2007-04-17", "source": src('steinberg'),
    "related": "Steinberg v. Commissioner, 141 T.C. No. 8 (2013) (summary judgment, 'Steinberg I'; separate DAWSON docket entry 7fd46e10-ee5d-4a27-ad43-cb253ea917ed)",
    "found_facts": [
        {"fact": "Deficiency", "values": {"gift_tax_increase": 1804908},
         "snippet": "increasing petitioner's gift tax liability by $1,804,908 for tax year 2007.", "locator": "p. 2"},
        {"fact": "Gross value transferred", "values": {"gross_fmv": 109449307},
         "snippet": "The fair market value of the properties transferred ... before consideration of the gift tax liability and section 2035(b) estate tax liability assumed by the daughters was $109,449,307.",
         "locator": "p. 7"},
        {"fact": "Escrow", "values": {"escrow_total": 40000000, "gift_tax_paid_from_escrow_before_credits": 32437261},
         "snippet": "the daughters each transferred $10 million to an escrow fund ... Of the $40 million, $32,437,261 was used to pay the Federal gift tax",
         "locator": "p. 7 & fn. 1"},
        {"fact": "Return", "values": {"net_gift_reported": 71598056, "gift_tax_reported": 32034311},
         "snippet": "petitioner reported taxable gifts of $71,598,056 and total gift tax of $32,034,311.", "locator": "p. 8"},
        {"fact": "Notice", "values": {"net_gift_per_notice": 75608963, "increase": 4010907, "discount_claimed": 5838540},
         "snippet": "increased the aggregate value of petitioner's net gifts to her daughters from $71,598,056 to $75,608,963, for a total gift tax increase of $1,804,908 ... increased the value of petitioner's total gifts for tax year 2007 by $4,010,907 ... petitioner's entire $5,838,540 discount",
         "locator": "pp. 8-9 & fn. 2"},
        {"fact": "Expert's computed gift tax assumed", "values": {"gift_tax_assumed": 32012711},
         "snippet": "The report calculated the gift tax liability to be $32,012,711.", "locator": "p. 28"}],
    "issue": "Whether the donees' assumption of potential sec. 2035(b) estate tax reduces the value of the net gift, and by how much.",
    "holding": "Yes; reduction of $5,838,540 (petitioner's unrebutted expert: IRS mortality tables + sec. 7520 rate). Decision for petitioner.",
    "stated_tax_figures": {"deficiency_determined": 1804908, "decision": "for petitioner (no deficiency)"},
    "recomputation": {
        "steps": [
            "Net gift = 109,449,307 - 32,012,711 - 5,838,540 = 71,598,056 == reported/allowed",
            "Deficiency = 45% (2007 top rate) x 4,010,907 = 1,804,908.15 -> $1,804,908 == notice",
            "Holding: discount allowed -> net gift 71,598,056 -> deficiency 0"],
        "reconciles": "net gift and deficiency exact",
        "non_reconciling": [
            "Notice increased the gift by 4,010,907, not the full 5,838,540 discount (fn. 2; parties nonetheless treat it as disallowing the entire discount).",
            "Reported gift tax 32,034,311 vs expert 32,012,711 vs escrow-paid 32,437,261 (before credits) differ; prior gifts/credits are not stated, so the circular net-gift solve (Rev. Rul. 75-72) cannot be reproduced exactly."]},
    "judgment_vs_computation": {
        "judgment": ["value of sec. 2035(b) assumption ($5,838,540, actuarial expert)", "gross FMV $109,449,307 (appraisals)"],
        "computation": ["net-gift subtraction; marginal-rate deficiency"]},
    "caveats": ["The main amount at issue is a valuation; the arithmetic around it is exact."]}

cases['sower'] = {
    "id": "tc-149-11", "slug": "sower",
    "caption": "Estate of Minnie Lynn Sower, Deceased, Frank W. Sower, Jr. and John R. Sower, Co-Executors v. Commissioner",
    "citation": "149 T.C. 279 (2017) (149 T.C. No. 11)", "date": "2017-09-11", "docket_numbers": ["32361-15"],
    "judge": "Buch", "tax_type": "estate (DSUE examination)", "date_of_death": "2013-08-07",
    "predeceased_spouse_date_of_death": "2012-02-23", "source": src('sower'), "secondary": True,
    "found_facts": [
        {"fact": "Lifetime taxable gifts (2003-2005)", "values": {"frank": 997920, "minnie": 997921},
         "snippet": "During their lifetimes, Frank and Minnie gave $997,920 and $997,921 in taxable gifts, respectively. All of the gifts were given between 2003 and 2005.",
         "locator": "p. 4"},
        {"fact": "Frank's return", "values": {"taxable_gifts_reported": 0, "worksheet_taxable_gifts": 945420, "dsue_reported": 1256033},
         "snippet": "reported zero in taxable gifts but included $945,420 in taxable gifts on the worksheet ... Frank's estate reported a DSUE of $1,256,033 and elected portability",
         "locator": "pp. 4-5"},
        {"fact": "Minnie's return and payments", "values": {"tax_reported_paid": 369036, "additional_tax_and_interest": 386424},
         "snippet": "reported and paid an overall estate tax liability of $369,036. Three months later the estate paid an additional $386,424 in tax and interest",
         "locator": "p. 5"},
        {"fact": "Adjustments", "values": {"dsue_as_adjusted": 282690, "funeral_cost_reduction": 850, "deficiency": 788165},
         "snippet": "the Commissioner reduced the DSUE available to Minnie's estate from $1,256,033 to $282,690. The Commissioner also adjusted Minnie's taxable estate by the amount of her lifetime taxable gifts. Finally, the Commissioner reduced Minnie's taxable estate by $850 to account for funeral costs. Together these adjustments increased the estate tax liability for Minnie's estate by $788,165.",
         "locator": "p. 6"},
        {"fact": "2013 BEA", "values": {"bea_2013": 5250000},
         "snippet": "At the time of Minnie's death the basic exclusion was $5,250,000.", "locator": "p. 9"}],
    "issue": "Whether the IRS may examine the predeceased spouse's return (after a closing letter and after its limitations period) to recompute the DSUE available to the surviving spouse's estate.",
    "holding": "Yes (sec. 2010(c)(5)(B)); closing letter not a sec. 7121 agreement, no estoppel, not a second examination, pre-2010 gifts count. Decision for respondent ($788,165).",
    "stated_tax_figures": {"deficiency": 788165},
    "recomputation": {
        "steps": [
            "Marginal check: 40% x [(1,256,033 - 282,690) + 997,921 - 850] = 40% x 1,970,414 = 788,165.60 -> $788,165 == deficiency (whole change in the 40% bracket)",
            "DSUE reduction = 973,343"],
        "reconciles": "deficiency exact as 40% of (DSUE reduction + Minnie's ATG - funeral costs)",
        "non_reconciling": [
            "DSUE reduction 973,343 != Frank's taxable gifts 997,920 or worksheet figure 945,420; Frank's taxable estate and the IRS's DSUE computation are not in the opinion, so DSUE = 282,690 cannot be derived from stated facts (2012 BEA 5,120,000 is not stated in the opinion)."]},
    "judgment_vs_computation": {"judgment": ["procedural/legal issues only"],
                                "computation": ["deficiency = 40% x total base change"]},
    "caveats": ["Mainly a procedural holding; listed as secondary."]}

for k, v in cases.items():
    with open(D + k + '.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(v, f, indent=2, ensure_ascii=False)
print('ok', list(cases))
