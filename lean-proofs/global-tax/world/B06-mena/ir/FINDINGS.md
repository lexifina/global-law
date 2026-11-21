# Iran (IR) findings, B06-mena (rescue pass 3, 2026-11-20T13:46Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 All salary from all sources is pooled for one exemption and one schedule
- kind: fact
- Note 1(ز) taxes 'مجموع پرداختی ... از یک یا چند منبع ... چه از کارفرمای اصلی و یا غیراصلی' and replaces the art. 86 withholding by the tax organisation's system, which computes the tax for each employer. A person with two jobs gets one 2,880,000,000-rial exemption and climbs the 10-30 % bands on the total; under the old art. 86 note a second employer withheld without the exemption. The model pools wages per person.
- provisions: Budget Law 1404 Note 1(ز) intro and (3); DTA arts. 84, 86
- Lean: IrTax.salaryTax
- status: model result

### F2 Faculty, full-time physicians and judges keep art. 85, outside the 10-30 % schedule
- kind: fact
- The clause excludes members of academic boards, full-time clinical physicians and judges and leaves them under DTA art. 85 as amended on 31 Tir 1394; the pre-1394 text reached prints a flat 10 % for state employees, judges and academics after the exemption. If the 1394 text keeps that, these groups pay at most 10 % at incomes where other employees pay 30 %. Not modelled (the 1394 text was not reached).
- provisions: Budget Law 1404 Note 1(ز)(2) last paragraph; DTA art. 85 (pre-1394 English text)
- Lean: -
- status: model result

### F3 Iran's official legal databases are closed to foreign readers
- kind: gov-error
- qavanin.ir (national laws system), dotic.ir, rc.majlis.ir, rrk.ir (official gazette) and intamedia.ir (tax administration) refused connections, served challenge pages or 403 to both machines on 2026-11-20, and their Internet Archive captures are mostly challenge shells. The promulgated budget law (dotic.ir scan) was reachable only as a copy on a private legal-news site.
- provisions: -
- Lean: -
- status: model result

### F4 Overtime and similar extras pay a flat 10 % after a share of the exemption
- kind: fact
- Overtime, welfare, productivity, extra teaching, research and on-call pay are taxed at 10 % 'پس از اعمال سقف معافیت به تناسب اقلام مذکور و اقلام صدر این بند', so a high earner's overtime pays 10 % against a 30 % top rate on base pay. The model has one wage figure and applies the schedule to all of it (an upper bound for people with such extras).
- provisions: Budget Law 1404 Note 1(ز)(2), second paragraph after the bands
- Lean: -
- status: model result


### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (statute (private reproduction))
- provisions: قانون تأمین اجتماعی مصوب ۱۳۵۴ art. 28 (1) and تبصره ۱, art. 2 (5), art. 36 (consolidated text on ekhtebar.ir, a private legal publisher's transcription; official hosts refused)
- insured person's premium 7 % of wages (Social Security Act 1354 art. 28 (1), تبصره ۱), reported, not deducted. Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: SSO premium: the administrative maximum wage subject to the premium (1404) not reached and not applied; its deductibility (DTA art. 91, 1394 wording) not reached; other exemptions 'مصرح در قوانین' not deducted. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Pooling of salaries from all sources (Budget Law 1404 note 1(ز)): modelled. |
| F2 | lead | Art. 85 groups (judges, academics, physicians) possibly at 10 %: the 1394 text was not reached. |
| F3 | explained | Official databases closed: access record. |
| F4 | lead | Overtime and extras at a flat 10 %: not modelled (one wage figure). |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) | SSO 7 % present (201,600,000 at 2.88 B). |
| Leads | explained | Rescan: no notch; split gain 1.148 B at 4 'AW' = individual assessment. |

<!-- L1-VERIFICATION END -->
