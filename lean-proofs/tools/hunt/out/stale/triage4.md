# Chunk 4 triage (82 entries: #4.0 to #4.81)

Counts: noise 70, intended 10, gap 2. Text read through Pub. L. 119-138 with `tools/hunt/sec.py`; earlier text from the
usc-history clone for §951 and §45E.

## Gap 1 (medium): §529(c)(3)(E) Roth rollover and a change of beneficiary — #4.40, #4.38

**New.** §529(c)(3)(E), added by the Consolidated Appropriations Act, 2023: a distribution "from a qualified tuition
program of a designated beneficiary which has been maintained for the 15-year period ending on the date of such
distribution" is not taxed if paid trustee-to-trustee to a Roth IRA of "such designated beneficiary", up to the annual
§408A(c)(2) amount and $35,000 in aggregate "with respect to the designated beneficiary".

**Left alone.** §529(c)(3)(C)(ii): a change of designated beneficiary to a family member "shall not be treated as a
distribution". §529(e)(1)(B): after such a change the designated beneficiary is "the individual who is the new
beneficiary". Neither says anything about the 15 years. The same Act did add §529(d)(2) (reporting) and
§408A(c)(3)(E), (c)(5)(B)(ii), (e)(1)(C).

**Outcome.** The 15 years attach to the program account ("which has been maintained"), and the person tested is whoever
is the designated beneficiary on the day of the transfer. So an old account can be re-pointed at any member of the
family and rolled to that person's Roth IRA straight away. The $35,000 cap is per designated beneficiary, so each new
beneficiary gets a fresh cap. If a restart were read in, the new beneficiary would wait 15 years.

**Example.** Account opened 2008 for A; $70,000 left, 55% earnings. A rolls $35,000 (plainly allowed). Beneficiary is
changed to sibling B, who has wages; B rolls the second $35,000 over about five years. If B's clock restarted, taking
that $35,000 out now is a non-qualified withdrawal: $19,250 earnings x (22% + 10% under §529(c)(6)) = $6,160. The
no-tax ordinary alternative is to leave the money locked for a future student, so the gain is access plus tax-free Roth
growth, not more than about $6,160 per $35,000 at these figures.

**Attack.** (1) "of a designated beneficiary which has been maintained" can be read as maintained for that beneficiary;
the grammar allows either. (2) §529(g) lets Treasury write rules "to prevent abuse" notwithstanding the rest of the
section; nothing in the text does so yet. (3) The 5-year contribution look-back in (E)(i)(I) and the compensation-based
annual limit still bind, so this moves old money slowly. (4) The original beneficiary can already roll $35,000, so the
change only helps for the excess or where A has no compensation. Survives as a real open reading, not a certainty.

## Gap 2 (low): §45E(b) dollar cap not conformed to §45E(f) — #4.24

**New.** §45E(f) (2022): the credit "allowed for the taxable year under subsection (a) (determined without regard to
this subsection) shall be increased by" the applicable percentage (100/100/75/50/25 over five years) of employer
contributions, up to $1,000 per employee.

**Left alone.** §45E(b): "The amount of the credit determined under this section for any taxable year shall not exceed"
$5,000 at most for the first credit year and the next two, and "zero for any other taxable year". The same Act amended
§45E(e)(2) to name subsection (f) but not (b). (The script's own list, §38(b)(14), is noise.)

**Outcome.** Strictly, the increase is part of "the credit determined under this section", so (b) caps the whole at
$5,000 and zeroes years 4 and 5. Read the other way, (b) applies to the (a) amount and (f) is added after.

**Example.** 20 non-highly-compensated employees, $1,000 contributed for each, $4,000 startup costs a year. Intended:
$12,000 + ($20,000 + $20,000 + $15,000 + $10,000 + $5,000) = $82,000. Strict: $5,000 x 3 = $15,000. Difference
$67,000, to the government.

**Attack.** The parenthetical in (f)(1), the word "allowed", and the fact that the 4th- and 5th-year rows of (f)(3)
would never operate all point to (f) sitting outside (b). A taxpayer cannot use this; it only bites if the Service
took the strict reading. Low confidence that the words leave the increase capped.

## Intended / harmless (10)

- #4.0–#4.4, #4.6: MAGI lists add back named exclusions (§135, §137, §911…). §139C, like §104(a)(1) which it extends, is not added back anywhere. Deliberate.
- #4.10: §25(e)(1)(C) does not carve out §25E; right, because §25E has no carryforward and should absorb the §26(a) limit first.
- #4.63, #4.64: §953(c)(5) still refers to "distributions … under subparagraph (B)" of §951(a)(2), which the 2025 Act replaced. Dead words, no dollar effect found.
- #4.67: §964(e)(4)(A)(ii) keeps the old "with or within which such taxable year of the controlled foreign corporation ends" timing while §951(a)(3) now uses the shareholder's last day of ownership. Timing only, offset by the §245A deduction for corporate shareholders.
- #4.34: §48E(h)(4)(C) low-income capacity runs through 2032 though wind and solar end after 2027.

## Noise (70)

§139C against §414(n)(3)(C), §1402(a)(8), §7701(a)(20) (employer-benefit and clergy lists); §168(n)/§168(j);
§25E/§163(g); §30C(h),(i) against §30C(e); §32(n) (2021 only) against the table rule; §3406(b)(8) against (b)(4) and
(h)(4) ((b)(8) is its own threshold rule, parallel to (b)(6)); all §432 entries; §45E(f)/§38(b)(14); §45Y against
§45K, §196, §3131, §3132, §3134, §4104; §45Y(b)(1)(E), (d)(4), (g)(13); §48E(e)(3), (h)(4)(D); the remaining §529
entries (references to (c)(3)(A) or (B) for unrelated reasons); §6343(f) (deals with (d) itself in (f)(4)); §6418
entries ((f)(1)(B) is per-facility production credits, (g)(3) is investment credits); §7448 entries; and every
§951(a)(3) entry that merely cites §951(a)(1) or (a)(2).

## Other things noticed

See `triage4.json` "other": §45AA has no deduction disallowance or coordination with §45E(f) (same contribution
credited twice, about $300 per military spouse per year); differing aggregation rules across §45E, §45T (none), §45AA;
§529(c)(3)(B)(ii) ratio does not carve rollovers out of "distributions"; differing carve-outs in §23(c), §25(e), §25D(c).
