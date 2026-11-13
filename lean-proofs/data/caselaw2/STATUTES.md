# Statutes: law changes and supersession of holdings by enactment (caselaw-lean-2)

Agent: statutes. Files: `lawchanges.tsv`, `supersessions.tsv` (schema in SCHEMA.md). Scripts: `global-law-lean/lean-proofs/tools/caselaw2/statutes/` (s1_blocks, s2_fetch, s3_lawinfo, s4_pairs, s5_score, s6_retro_llm, s7_write, s8_audit, s9_validate). Work files and caches: `caselaw-lean-2/statutes/`.

## Counts

- lawchanges.tsv: 34,696 (law, US Code block) rewrites, each after at least one decision citing the block (1,931,153 citations, 1995 on). Dates from: llm 542, record 22,984, rx 11,170. Rows with retroactive_to set: 758.
- supersessions.tsv: 13,977 rows over 6,385 decisions; by evidence: lawNamesDecision 256, quotedWordsStruck 12,265, reportNamesDecision 1,456; explicit = 1: 238; issue_key attached: 0; laterCourtSays rows: 0.
- `retroactive_to`: 0 none; a yyyymmdd day = the earliest conduct/claim day the change reaches (before enactment); 1 = applies to matters pending on its effective date whatever the conduct date, no earlier bound stated. `effective` is the law's own effective date where it states one (src `llm:` or `rx:`), else the record's in-force day (src `record:<how the record dated it>`; `record:enacted` = dated on enactment because the record does not read effective dates).

## Recall: Christiansen & Eskridge (+ Hasen), 1995-2011 Supreme Court decisions overridden by 2011

- Any evidence linking the decision to the overriding law: 23/36 (64%) (overrides work: 20/36). Explicit (law, report or court states it): 16/36 (44%). Score >= 0.5: 15/36 (42%).
- Per item: `statutes/recall2.tsv`.

## Precision per evidence type (blind audits; override = express or implicit)

| evidence | stratum | pairs | audited | override | express | precision | Wilson 95% | score used |
|---|---|---|---|---|---|---|---|---|
| lawNamesDecision | first10y | 29 | 29 | 11 | 10 | 0.379 | 0.227-0.56 | 0.387 |
| reportNamesDecision | first10y | 234 | 31 | 8 | 8 | 0.258 | 0.137-0.432 | 0.273 |
| quotedWordsStruck | SA | 2,315 | 25 | 4 | 0 | 0.16 | 0.064-0.347 | 0.185 |
| quotedWordsStruck | FT | 3,445 | 20 | 1 | 0 | 0.05 | 0.009-0.236 | 0.091 |
| lawNamesDecision | later | 11 | 1 | 0 | 0 | 0.0 | 0.0-0.793 | 0.333 |
| reportNamesDecision | later | 142 | 20 | 1 | 1 | 0.05 | 0.009-0.236 | 0.091 |
| lawNamesDecision | cite | 54 | 4 | 0 | 0 | 0.0 | 0.0-0.49 | 0.167 |
| reportNamesDecision | cite | 349 | 16 | 2 | 2 | 0.125 | 0.035-0.36 | 0.167 |

Strata: first10y = first rewrite of the cited block within 10 years (overrides census/samples); later = another rewrite or 10-15 years (new, blind reads here); cite = reporter cite in the law/report resolved to the decision, linked by section (new, blind reads here); SA/FT = Supreme Court + appeals / other courts. Audited pairs carry their verdict (0.97 / 0.03) as score; others the smoothed stratum precision (k+1)/(n+2).

## Retroactivity extraction (gpt-5.4-mini, effective-date provisions)

- Calls: 242 (law x amended section, for the 34 confirmed overrides and the top 300 candidates), errors 0, tokens 1,170,337. Classes: appliesToPendingCases 11, asIfIncluded 4, noProvision 140, prospectiveOnly 66, retroactiveToDate 21.
- Hand reads: subagents read the law text blind (no model output) and classified each item; RETRO_INSTRUCTIONS.md.
- Final prompt/packet (v2) on a fresh hand-read sample [headline] (30): class 18/30 (60%); retroactive yes/no 25/30 (83%); effective date 21/30 (70%); retroactive_to 25/30 (83%).
- First run (v1) on the first hand-read sample (blind) (30): class 17/30 (57%); retroactive yes/no 26/30 (87%); effective date 21/30 (70%); retroactive_to 26/30 (87%).
- v2 on the first sample (used to diagnose v1, so optimistic) (30): class 19/30 (63%); retroactive yes/no 25/30 (83%); effective date 21/30 (70%); retroactive_to 25/30 (83%).
- v1 -> v2: v1 packets missed the amending section when a tax law names "section N of the Internal Revenue Code" (no U.S.C. cite) and dropped passages that name the section by number; v1 also called a delayed effective date "noProvision".
- The regex/record reading (used for every row the LLM did not read) on both samples: retroactive yes/no 50/60 (83%); effective date 38/60 (63%).
- Confusion, fresh sample (hand -> v2): asIfIncluded -> noProvision 1; asIfIncluded -> prospectiveOnly 1; noProvision -> noProvision 13; noProvision -> prospectiveOnly 4; noProvision -> retroactiveToDate 1; prospectiveOnly -> noProvision 3; prospectiveOnly -> prospectiveOnly 5; prospectiveOnly -> retroactiveToDate 1; retroactiveToDate -> noProvision 1
- Disagreements on the fresh sample (hand class -> LLM class; hand date / LLM date):
  - Pub. L. 110-246|7:2279: retroactiveToDate -> noProvision; 2008-05-22 / 2008-06-18. Sec. 4(b) makes the amendments by secs. 14001, 14004 and 14005 effective on the enactment of H.R. 2419 (Pub. L. 110-234, May 22, 2008), earlier than this Act's June 18, 2008 enactment.
  - Pub. L. 105-219|12:1759: noProvision -> prospectiveOnly; 1998-08-07 / 1999-08-07. No effective-date provision covers the secs. 101-103 amendments to 12 U.S.C. 1759 (only a grandfather of existing members and a filing-date scope rule for new subsection (g)), so they take effect on a
  - Pub. L. 108-173|42:1395i: noProvision -> retroactiveToDate; 2003-12-08 / 2003-12-08. The amendments to section 1817 by secs. 736(a)(5)-(6), 801(d)(1) and 900(e)(1)(D) carry no effective-date provision, so they take effect on approval, Dec. 8, 2003.
  - Pub. L. 105-277|16:1011: noProvision -> prospectiveOnly; 1998-10-21 / 1999-04-19. Sec. 136 of the Interior appropriations division amending 16 U.S.C. 1011(a) has no timing provision, so it takes effect on approval, Oct. 21, 1998.
  - Pub. L. 105-33|29:1169: asIfIncluded -> prospectiveOnly; 1996-08-22 / 1997-08-05. Sec. 5612(b) makes its 1169(a)(2)(B) amendment effective as if included in PRWORA sec. 381 (Aug. 22, 1996), while secs. 5611 and 5613 apply only to medical child support orders issued on or after the 
  - Pub. L. 111-148|42:1396n: prospectiveOnly -> prospectiveOnly; 2010-04-01 / 2010-10-01. Sec. 2402(g) delays the sec. 2402 amendments to 1915(i) to the first fiscal quarter after enactment (sec. 2401 adds 1915(k) operative October 1, 2010; sec. 2601 has no timing provision); nothing reach
  - Pub. L. 105-206|26:1045: asIfIncluded -> noProvision; 1997-08-05 / 1998-07-22. Sec. 6005(f) technical amendments to section 1045 (related to sec. 313 of the 1997 Act) take effect under sec. 6024 as if included in the Taxpayer Relief Act of 1997.
  - Pub. L. 104-104|15:5714: noProvision -> prospectiveOnly; 1996-02-08 / 1996-02-08. Sec. 701(b)(1) redefines pay-per-call services in 15 U.S.C. 5714(1); the only nearby effective-date clause covers subsection (a)(1), so the amendment takes effect on approval.
  - Pub. L. 109-59|26:4081: prospectiveOnly -> noProvision; 2005-10-01 / 2005-08-10. The main sec. 11161 kerosene amendments to section 4081 apply only to fuel removed, entered or sold after September 30, 2005 (other amendments: sec. 11101 and 11166 on enactment, sec. 11151(b) as if i
  - Pub. L. 105-33|42:1101: noProvision -> prospectiveOnly; 1997-08-05 / 1997-08-05. Section 5408 adds 42 U.S.C. 1101(c)(5) with no effective-date or applicability provision, so it takes effect on approval, August 5, 1997.
  - Pub. L. 109-59|26:4051: prospectiveOnly -> noProvision; 2005-10-01 / 2005-08-10. Section 11112(b) applies the light-tractor exclusion only to sales after September 30, 2005, a date after enactment (August 10, 2005).
  - Pub. L. 104-208|16:1827: prospectiveOnly -> noProvision; 1996-10-26 / 1996-09-30. Title II section 211(b) delays the name change to 15 days after the Sustainable Fisheries Act's enactment (October 11, 1996), a date after this law's approval, with no reach back.
  - Pub. L. 111-21|31:3730: prospectiveOnly -> retroactiveToDate; 2009-05-20 / 2009-05-20. Section 4(f) limits section 4's amendments, including 4(d) to 31 U.S.C. 3730(h), to conduct on or after enactment; its exceptions cover only sections 3729(a)(1)(B), 3731(b), 3732 and 3733.

## Two dates: confirmed overrides (question date vs conduct date)

For a question asked on or after `effective`, the holding still governs conduct before `effective` unless `retroactive_to` reaches it (rule AB1, doctrine.md 7). One row per confirmed (decision, law), its first linked block.

| decision | decided | law | block | enacted | effective | retroactive_to | holding still governs conduct | src |
|---|---|---|---|---|---|---|---|---|
| Harvey v. Veneman | 20050126 | Pub. L. 109-97 | 7:6509(e) | 20051110 | 20060101 | 0 | before 20060101 | rx:onDate:sec1:rank0 |
| United States ex rel. Atkins v. McInteer | 20041027 | Pub. L. 111-21 | 31:3729(a) | 20090520 | 20090520 | 20080607 | before 20080607 | llm:retroactiveToDate:statedDate:hand:FERA4f1:3729a1B-as-if-enacted-20080607-for-pending-claims;rest-of-block-prospective-from-20090520(mixedWithinBlock) |
| Ledbetter v. Goodyear Tire & Rubber Co. | 20050823 | Pub. L. 111-2 | 42:2000e-5(e) | 20090129 | 20070528 | 20070528 | before 20070528 | llm:asIfIncluded:asIfIncluded |
| United States v. Turner | 19960201 | Pub. L. 105-386 | 18:924(c) | 19981113 | 19981113 | 0 | before 19981113 | llm:noProvision:notStated |
| United States ex rel. DRC, Inc. v. Custer Battles, LLC | 20050708 | Pub. L. 111-21 | 31:3729(a) | 20090520 | 20090520 | 20080607 | before 20080607 | llm:retroactiveToDate:statedDate:hand:FERA4f1:3729a1B-as-if-enacted-20080607-for-pending-claims;rest-of-block-prospective-from-20090520(mixedWithinBlock) |
| United States ex rel. DRC, Inc. v. Custer Battles, LLC | 20090410 | Pub. L. 111-21 | 31:3729(a) | 20090520 | 20090520 | 20080607 | before 20080607 | llm:retroactiveToDate:statedDate:hand:FERA4f1:3729a1B-as-if-enacted-20080607-for-pending-claims;rest-of-block-prospective-from-20090520(mixedWithinBlock) |
| United States v. Nagarwala | 20181120 | Pub. L. 116-309 | 18:116(a) | 20210105 | 20210105 | 0 | before 20210105 | llm:noProvision:enactment |
| Freightliner of Grand Rapids, Inc. v. United States | 20040929 | Pub. L. 109-59 | 26:4051(a) | 20050810 | 20051001 | 0 | before 20051001 | llm:prospectiveOnly:enactment:handRead |
| United States ex rel. Huangyan Import & Export Corp. v. Nature's Farm Products, Inc. | 20050503 | Pub. L. 111-21 | 31:3729(a) | 20090520 | 20090520 | 20080607 | before 20080607 | llm:retroactiveToDate:statedDate:hand:FERA4f1:3729a1B-as-if-enacted-20080607-for-pending-claims;rest-of-block-prospective-from-20090520(mixedWithinBlock) |
| Bossier Parish School Board v. Reno | 19980501 | Pub. L. 109-246 | 42:1973c | 20060727 | 20060727 | 0 | before 20060727 | llm:noProvision:notStated |
| United States v. Hung Shun Lin | 19961210 | Pub. L. 105-386 | 18:924(c) | 19981113 | 19981113 | 0 | before 19981113 | llm:noProvision:notStated |
| Lachance v. White | 19990514 | Pub. L. 112-199 | 5:2302(b) | 20121127 | 20121127 | 0 | before 20121127 | llm:prospectiveOnly:enactment |
| Hubbard v. United States | 19950515 | Pub. L. 104-292 | 18:1001 | 19961011 | 19961011 | 0 | before 19961011 | llm:noProvision:notStated:handRead |
| Bailey v. United States | 19951206 | Pub. L. 105-386 | 18:924(c) | 19981113 | 19981113 | 0 | before 19981113 | llm:noProvision:notStated |
| Commissioner v. Lundy | 19960117 | Pub. L. 105-34 | 26:6501(a) | 19970805 | 19970805 | 0 | before 19970805 | record:enacted |
| National Credit Union Administration v. First National Bank & Trust Co. | 19980225 | Pub. L. 105-219 | 12:1759 | 19980807 | 19980807 | 0 | before 19980807 | llm:noProvision:statedDate:handRead |
| Sutton v. United Air Lines, Inc. | 19990622 | Pub. L. 110-325 | 42:12101(7) | 20080925 | 20090101 | 0 | before 20090101 | llm:prospectiveOnly:statedDate:handRead |
| Reno v. Bossier Parish School Board | 20000124 | Pub. L. 109-246 | 42:1973b(a) | 20060727 | 20060727 | 0 | before 20060727 | llm:noProvision:enactment:handRead |
| Immigration & Naturalization Service v. St. Cyr | 20010625 | Pub. L. 109-13 | 8:1227(a) | 20050511 | 20050511 | 1 | none (pending matters reached) | llm:retroactiveToDate:statedDate:handRead |
| Lorillard Tobacco Co. v. Reilly | 20010628 | Pub. L. 111-31 | 15:1333 | 20090622 | 20100922 | 0 | before 20100922 | llm:prospectiveOnly:periodAfterEnactment |
| Toyota Motor Manufacturing, Kentucky, Inc. v. Williams | 20020108 | Pub. L. 110-325 | 42:12101 | 20080925 | 20090101 | 0 | before 20090101 | llm:prospectiveOnly:statedDate:handRead |
| Ashcroft v. Free Speech Coalition | 20020416 | Pub. L. 108-21 | 18:2251 | 20030430 | 20030430 | 0 | before 20030430 | llm:noProvision:notStated:handRead |
| Holmes Group, Inc. v. Vornado Air Circulation Systems, Inc. | 20020603 | Pub. L. 112-29 | 28:1295(a) | 20110916 | 20110916 | 0 | before 20110916 | llm:prospectiveOnly:statedDate |
| Moseley v. V Secret Catalogue, Inc. | 20030304 | Pub. L. 109-312 | 15:1127 | 20061006 | 20061006 | 0 | before 20061006 | llm:noProvision:enactment |
| Georgia v. Ashcroft | 20030626 | Pub. L. 109-246 | 42:1973c | 20060727 | 20060727 | 0 | before 20060727 | llm:noProvision:notStated |
| Hamdan v. Rumsfeld | 20060629 | Pub. L. 109-366 | 10:802(a) | 20061017 | 20061017 | 0 | before 20061017 | record:enacted |
| Ledbetter v. Goodyear Tire & Rubber Co. | 20070529 | Pub. L. 111-2 | 42:2000e-5(e) | 20090129 | 20070528 | 20070528 | before 20070528 | llm:asIfIncluded:asIfIncluded |
| Allison Engine Co. v. United States ex rel. Sanders | 20080609 | Pub. L. 111-21 | 31:3729(a) | 20090520 | 20090520 | 20080607 | before 20080607 | llm:retroactiveToDate:statedDate:hand:FERA4f1:3729a1B-as-if-enacted-20080607-for-pending-claims;rest-of-block-prospective-from-20090520(mixedWithinBlock) |
| Baizer v. United States Department of the Air Force | 19950313 | Pub. L. 104-231 | 5:552 | 19961002 | 19970331 | 0 | before 19970331 | llm:prospectiveOnly:periodAfterEnactment:handRead |
| Kenseth v. Commissioner | 20010807 | Pub. L. 108-357 | 26:1 | 20041022 | 20041022 | 0 | before 20041022 | record:enacted |
| T.W.R., Inc. v. United States Secretary of Agriculture | 20080528 | Pub. L. 111-5 | 19:2401a(d) | 20090217 | 20090518 | 0 | before 20090518 | llm:prospectiveOnly:periodAfterEnactment:handRead |
| Louis Vuitton Malletier v. Dooney & Bourke, Inc. | 20060630 | Pub. L. 109-312 | 15:1052 | 20061006 | 20061006 | 0 | before 20061006 | llm:noProvision:notStated |
| United States v. Cisneros | 19991028 | Pub. L. 108-458 | 18:1958 | 20041217 | 20041217 | 0 | before 20041217 | llm:noProvision:notStated |
| United States v. Wright | 20110420 | Pub. L. 115-299 | 18:2259 | 20181207 | 20181207 | 0 | before 20181207 | llm:prospectiveOnly:conductAfter |
| Food & Drug Administration v. Brown & Williamson Tobacco Corp. | 20000321 | Pub. L. 111-31 | 15:1333(a) | 20090622 | 20100922 | 0 | before 20100922 | llm:prospectiveOnly:periodAfterEnactment |
| Dunaway v. Ford Motor Co. | 20050525 | Pub. L. 110-325 | 42:12102(2) | 20080925 | 20090101 | 0 | before 20090101 | llm:prospectiveOnly:statedDate:handRead |
| Santos v. United States | 20060825 | Pub. L. 111-21 | 18:1957 | 20090520 | 20090520 | 0 | before 20090520 | llm:noProvision:enactment |

## Gaps

- Citations are read only from 1995 on, so block-level links start in 1995; earlier decisions enter only through a reporter cite in a law or report (`cite` stratum, linked by section).
- Block rewrites the record credits to an edition rather than a law (174,795 first rewrites in the overrides work) have no law, so no row here.
- Law texts: govinfo PLAW starts with the 104th Congress; earlier laws (Civil Rights Act of 1991, etc.) have no text (`record:...:notext`), so no effective-date reading and no naming evidence.
- Effective dates for rows the LLM did not read come from regex rules over the law's effective-date passages (src `rx:<kind>:sec<n>:rank<r>`; rank 0 = in the amending section, 1 = names it, 2 = its title, 3 = Act-wide), or the record's in-force day. See the regex accuracy line above.
- quotedWordsStruck covers only the first rewrite of a cited block (decision-text features were not recomputed for later rewrites).
- Committee reports: only those listed in the law's legislative-history note, part 1 of multi-part reports.
- `explicit` for unaudited rows: the naming passage contains override language (overrul, supersed, in response to, reject the, restore, clarify that, ...); the audits show naming alone often means codification (see the codifies counts).
- laterCourtSays and issue_key depend on the reader's treatments.tsv and the holdings agent's holdings.tsv/issues.tsv; rows are added by rerunning s7_write.py and s9_validate.py when those files exist.

