import LegalProofs.USTax.Estate.Theorems

/-!
# Six Tax Court estate and gift tax decisions, recomputed from their findings

Each case takes the opinion's found (or stipulated, or reported) figures as facts, runs them through the rules in
`Transfer.lean`, and compares the result with the dollar figures the opinion states. Valuation (what an asset, a
discount or an actuarial assumption is worth) is judgment: where a case turns on it, the court's value is taken as a
fact. The opinions are on DAWSON (https://dawson.ustaxcourt.gov/case-detail/<docket>); the encoded facts, with the
quoted passages and page references, are in `tax-formalization-data/taxcourt/estate/cases/<slug>.json`.

Verdicts, in one line each:

* **Mikel** (T.C. Memo. 2015-64, 2007 gifts, Crummey powers): match. The $268,950 deficiency and $67,238 addition
  recompute exactly; with the exclusions the court upheld in principle the tax is nil, and the model finds the
  threshold the open question turns on: 53 present-interest donees suffice, 52 do not.
* **Spizzirri** (T.C. Memo. 2023-25, 2015 death): the return's $10,150,307 and the agreed $120,299 addition match;
  from the found payments the model computes adjusted taxable gifts of $342,049, not the $193,441 the court sustained
  (the court declined to look behind the notice); the $2,251,189 deficiency cannot be rebuilt from the opinion.
* **Rowland** (T.C. Memo. 2025-76, DSUE): match on the DSUE ($3,712,562) and the claimed exclusion ($14,892,562); the
  holding sets DSUE to nil, which the model prices at $1,485,025 of extra tax on the base the return implies.
* **MacElhenny** (T.C. Memo. 2023-33, §2512(b) part-sale gift): match, $967,805 a child (the court rounded half up).
* **Steinberg** (145 T.C. 184 (2015), net gift): match. Net gift $71,598,056; the notice's $1,804,908 is the 2007
  table's 45% on the $4,010,907 increase; the court allowed the discount, so no deficiency.
* **Sower** (149 T.C. 279 (2017), DSUE re-examination): the $788,165 deficiency is 40% of the change in base to within
  $1 of rounding; the reduced DSUE of $282,690 cannot be derived from the facts the opinion states.
-/

namespace Legal.USTax.Estate.Cases
open Legal.USTax.Estate

/-- §6651(a)(1): 5% of the net tax due for each month or part of a month late, at most 25%. -/
def lateFiling (netDue : Int) (months : Nat) : Int := pct netDue (5 * min months 5)

/-- §2512(b): a transfer for less than full value is a gift of the excess of the value over the consideration. -/
def partSaleGift (value consideration : Int) : Int := max 0 (value - consideration)

/-! ## Mikel v. Commissioner, T.C. Memo. 2015-64 (dockets 16538-13, 16563-13)

Facts (pp. 1–2, 7–10): in 2007 each spouse made a gift of $1,631,000 to a family trust (half each, by consent under
§2513); each claimed 60 annual exclusions of $12,000 ($720,000), for the trust's 60 beneficiaries' withdrawal rights.
The notice disallowed every exclusion: a deficiency of $268,950 each and a §6651(a)(1) addition of $67,238. Held: the
withdrawal rights were present interests; the number of beneficiaries was left open (fn. 2). The opinion mentions no
earlier taxable gifts; none are assumed. -/

def mikelGifts (n : Nat) : List Gift :=
  -- n beneficiaries' present interests, at the $12,000 they each could withdraw, and the rest as a future interest
  List.replicate n { value := 12000 } ++ [{ value := 1631000 - 12000 * n, present := false }]

/-- No exclusions (the notice): 2007's table gives a tentative tax of $614,750 on $1,631,000; less the $345,800 credit
(a $1,000,000 exclusion in 2007), $268,950. The four-years-late addition, 25%: $67,238. Both as the notice states. -/
theorem mikel_notice : taxableGifts 2007 [{ value := 1631000, present := false }] = 1631000 ∧
    tentative 2007 1631000 = 614750 ∧
    giftTax [⟨2007, 1631000, 0⟩] = 268950 ∧ lateFiling 268950 48 = 67238 := by decide

/-- With the 60 exclusions claimed: taxable gifts $911,000, under the credit; no tax, as the returns reported. -/
theorem mikel_claimed : taxableGifts 2007 (mikelGifts 60) = 911000 ∧
    giftTax [⟨2007, taxableGifts 2007 (mikelGifts 60), 0⟩] = 0 := by decide

/-- **The threshold the open question turns on.** With 53 present-interest donees there is no gift tax; with 52 there
is $2,870. -/
theorem mikel_threshold : giftTax [⟨2007, taxableGifts 2007 (mikelGifts 53), 0⟩] = 0 ∧
    giftTax [⟨2007, taxableGifts 2007 (mikelGifts 52), 0⟩] = 2870 := by decide

/-! ## Estate of Spizzirri v. Commissioner, T.C. Memo. 2023-25 (docket 19124-19)

Death May 12, 2015. Return (p. 7): taxable estate $30,805,768, tax $10,150,307, adjusted taxable gifts nil. Lifetime
payments found by recipient and year (pp. 5–6); annual exclusion $13,000 (2011–12), $14,000 (2013–15) (p. 9). The notice
set adjusted taxable gifts at $193,441 and determined a $2,251,189 deficiency; the court sustained the notice (it "will
not look behind a deficiency notice") and the parties agreed the late-filing addition at $120,299 (p. 19 fn. 11). -/

def spizzirriPayments : List (List (Nat × Int)) := [
  [(2014, 15000)],                                       -- daughter
  [(2014, 25700), (2015, 21000)],                        -- stepdaughter
  [(2011, 27111), (2012, 19175), (2013, 24981), (2015, 12226)],
  [(2013, 37500), (2014, 22714), (2015, 30000)],
  [(2011, 59661), (2012, 16600), (2013, 13400)],
  [(2011, 24100), (2012, 25052)],
  [(2013, 22800), (2014, 50750), (2015, 26600)],
  [(2013, 42900), (2014, 30455)],
  [(2012, 58550), (2013, 34400), (2014, 7350)]]

def spizzirriYear (y : Nat) : Period :=
  ⟨y, taxableGifts y (spizzirriPayments.filterMap fun d => (d.find? (·.1 == y)).map fun p => { value := p.2 }), 0⟩

def spizzirriGifts : List Period := [2011, 2012, 2013, 2014, 2015].map spizzirriYear

def spizzirriReturn : Death := { year := 2015, gross := 30805768 }

/-- The return's tax recomputes: 40% of ($30,805,768 − $5,430,000) = $10,150,307. -/
theorem spizzirri_return : spizzirriReturn.tax = 10150307 := by decide

/-- **Mismatch.** From the payments the court found, the taxable gifts are $71,872, $67,377, $92,581, $74,619 and
$35,600 for 2011–2015: $342,049 of adjusted taxable gifts, all under the credit (no gift tax payable), against the
$193,441 the notice used and the court sustained. The extra $148,608 would have cost the estate another $59,443. -/
theorem spizzirri_gifts : spizzirriGifts.map Period.taxable = [71872, 67377, 92581, 74619, 35600] ∧
    ({ spizzirriReturn with gifts := spizzirriGifts } : Death).adjustedTaxableGifts = 342049 ∧
    ({ spizzirriReturn with gifts := spizzirriGifts } : Death).giftTaxPayable = 0 ∧
    ({ spizzirriReturn with gifts := spizzirriGifts } : Death).tax -
      ({ spizzirriReturn with gifts := [⟨2014, 193441, 0⟩] } : Death).tax = 59443 := by decide

/-- The agreed addition: the return was filed in the fourth month after the extended due date; tax as finally
determined, $10,150,307 + $2,251,189 = $12,401,496, less the $11,800,000 paid by the due date, times 20%: $120,299. -/
theorem spizzirri_addition : lateFiling (10150307 + 2251189 - 11800000) 4 = 120299 := by decide

/-! ## Estate of Rowland v. Commissioner, T.C. Memo. 2025-76 (docket 12736-22)

Fay Rowland died April 8, 2016; her late return computed a DSUE of $3,712,562 from an estimated gross estate of
$3,000,000, estimated deductions of $1,500,000 and adjusted taxable gifts of $237,438 (p. 3). Billy Rowland died
January 24, 2018; his return claimed an applicable exclusion of $14,892,562 and reported net estate tax of $4,477,555
(p. 4). Held: Fay's estate made no valid portability election, so Billy's estate has no DSUE. The opinion is a partial
summary judgment and states no deficiency; the figures for Fay are her return's estimates, not findings. -/

def fay : Death := { year := 2016, gross := 3000000, expenses := 1500000, gifts := [⟨2015, 237438, 0⟩] }

/-- The DSUE recomputes exactly: $5,450,000 − ($1,500,000 + $237,438). -/
theorem rowland_dsue : fay.dsueOut = 3712562 ∧ survivorExclusion 2018 fay.dsueOut = 14892562 := by decide

/-- On the return, with the claimed DSUE, a §2001(b)(1) base of $26,086,450 gives exactly the reported $4,477,555
(the base is implied by the reported tax; the opinion does not state it). With the DSUE at nil, as held, the tax is
$5,962,580: $1,485,025 more. -/
def billy (dsue : Int) : Death := { year := 2018, gross := 26086450, dsue := dsue }
theorem rowland_effect : (billy fay.dsueOut).tax = 4477555 ∧ (billy 0).tax = 5962580 ∧
    (billy 0).tax - (billy fay.dsueOut).tax = 1485025 := by decide

/-! ## Estate of MacElhenny v. Commissioner, T.C. Memo. 2023-33 (dockets 12981-19, 12982-19)

In 2012 the decedent sold a property to his two children. Stipulated value: $3,100,000 for each half (p. 8). The court
counted as consideration only the $1,614,391 mortgage assumed and the $2,650,000 paid for the bank judgment, not the
$485,609 offset against the judgment; held a taxable gift of $967,805 to each child. The deficiencies ($3,335,609 of
2012 gift tax, $3,992,656 of estate tax) are not explained in the opinion and are not recomputed here. -/

theorem macelhenny_gift : partSaleGift (2 * 3100000) (1614391 + 2650000) = 1935609 ∧
    -- each child's half, $967,804.50, which the court rounded to $967,805
    pct (partSaleGift (2 * 3100000) (1614391 + 2650000)) 50 = 967805 := by decide

/-! ## Steinberg v. Commissioner, 145 T.C. 184 (2015) (docket 23865-11)

A 2007 net gift: the daughters agreed to pay the gift tax and any estate tax under §2035(b) if the donor died within
three years. Gross value $109,449,307 (p. 7); gift tax $32,012,711 (the expert's figure, p. 28); the daughters'
assumption of §2035(b) tax valued at $5,838,540 by the donor's unrebutted actuarial expert. The notice raised the net
gifts to $75,608,963 (by $4,010,907) and the tax by $1,804,908. Held: the assumption reduces the gift; decision for
the donor. -/

theorem steinberg_net_gift : 109449307 - 32012711 - 5838540 = (71598056 : Int) := by decide

/-- Under the 2007 table the extra $4,010,907 is taxed at 45%: $1,804,908, the notice's figure, whatever the donor's
other gifts (both amounts are far above $1,500,000). -/
theorem steinberg_deficiency :
    tentative 2007 75608963 - tentative 2007 71598056 = 1804908 ∧ pct 4010907 45 = 1804908 := by decide

/-! ## Estate of Sower v. Commissioner, 149 T.C. 279 (2017) (docket 32361-15)

Frank Sower died in 2012; his estate reported a DSUE of $1,256,033. Minnie Sower died in 2013 having made $997,921 of
taxable gifts in 2003–2005. On examining Frank's return the Commissioner reduced the DSUE to $282,690, added Minnie's
gifts as adjusted taxable gifts and allowed $850 more of funeral costs: $788,165 more tax (p. 6). Held: the
Commissioner may examine the first spouse's return to fix the DSUE. -/

/-- Minnie's gifts, recomputed at 2013 rates, were all within the credit in force when made ($1,000,000), so no gift
tax is subtracted and the whole $997,921 adds to the base. -/
theorem sower_gifts : (schedule 2013 [⟨2004, 997921, 0⟩]).map Row.tax = [0] := by decide

/-- The deficiency: 40% of ($1,256,033 − $282,690 + $997,921 − $850) = 40% of $1,970,414 = $788,165.60; the opinion
says $788,165. Within $1, a rounding difference between two whole-dollar returns. -/
theorem sower_deficiency : pct (1256033 - 282690 + 997921 - 850) 40 = 788166 := by decide

end Legal.USTax.Estate.Cases
