# Case JSON schema (one file per opinion: cases/<id>.json)

Purpose: each case must let a formal (Lean) model recompute the court's decision from found facts + statute.
Read the full opinion text in cases/text/<id>.txt (pages are marked "=== [page N] ===").
Metadata from DAWSON for each id is in work/meta.json (docket, judge, filingDate, docketEntryId, api_url, caseCaption, documentTitle).

```json
{
  "id": "tcsumm-2021-26",
  "citation": "T.C. Summary Opinion 2021-26",
  "case_name": "Carol Denise Griffin v. Commissioner",
  "docket_numbers": ["9875-18S"],
  "judge": "Vasquez",
  "date": "2021-08-17",                       // filing date, YYYY-MM-DD (from meta.filingDate)
  "opinion_type": "summary" | "memorandum",
  "source": {"dawson_docket_entry_id": "...", "dawson_case_url": "...", "dawson_document_api": "...", "retrieved": "2026-11-11"},
  "tax_years": [2016],
  "taxpayer": {"filing_status_claimed": "head of household", "state": "Texas", "notes": "..."},
  "notice_of_deficiency": {
     "per_year": [{"year": 2016, "deficiency": 5627, "penalties": [{"section": "6662(a)", "amount": 1125.40}], "additions": []}],
     "adjustments": ["disallowed EIC $X", "..."],              // what IRS changed, if stated
     "contested_by_taxpayer": "short description",
     "conceded": ["what either party conceded, short"]
  },
  "findings_of_fact": [
     {"fact_id": "F1", "issue_refs": ["I1"], "fact": "Child A.B. born 2009; age 7 at end of 2016",
      "values": {"child": "A.B.", "birth_year": 2009, "age_end_of_year": 7},   // machine-usable numbers/dates/booleans
      "snippet": "verbatim quote <= 25 words", "locator": "p. 3"}
  ],
  "issues": [
     {"issue_id": "I1", "tags": ["eitc_32"],
      "question": "Is petitioner entitled to the EIC for 2016 with A.B. as qualifying child?",
      "provisions": ["26 U.S.C. §32(c)(3)", "§152(c)"],
      "holding": "Petitioner entitled; A.B. satisfies relationship, age, residency tests",
      "prevailing_party": "petitioner" | "respondent" | "split",
      "amount_determined": {"description": "...", "amount": null},  // any $ amount the court stated
      "rule_155": true|false,
      "computable": true|false,
      "computable_reason": "one line"}
  ],
  "decision": {"text": "Decision will be entered under Rule 155.", "summary": "deficiency sustained except ...; no 6662 penalty"},
  "notes": "anything a modeller should know (e.g., which facts were stipulated, burden of proof, ambiguities)"
}
```

Issue tags (use these strings): eitc_32, qualifying_child_152c, qualifying_relative_152d, dependency_exemption_151, head_of_household_2b, filing_status_other, ctc_24, actc_24d, early_distribution_72t, ira_distribution_income_408d, rollover_408d3, ira_deduction_219, social_security_86, self_employment_tax_1401, education_credit_25a, student_loan_interest_221, alimony_71_215, gambling_165d, penalty_6662a, addition_6651a1, addition_6651a2, addition_6654, other_income_inclusion_61, other (explain in question).

Rules:
- Numbers must be exact as in the opinion (dollars with cents if given). Do not compute amounts the court did not state; if you derive something, put it in notes labelled "derived".
- snippet: verbatim from the text (fix only PDF hyphenation/line-break whitespace), <= 25 words; locator "p. N" using the "=== [page N] ===" markers (the opinion's own page numbers if clearly different, say "pdf p. N").
- computable=true only if the outcome of that issue follows mechanically from found facts + statute for that year (e.g., age/residency/relationship tests, income thresholds, 10% of distribution, 60-day window, 6662 10%/$5,000 test). false for credibility/substantiation/reasonable-cause/discretion-driven issues — say why. Penalty issues decided on Sec. 6751(b) supervisory approval or reasonable cause are computable=false unless purely the arithmetic threshold.
- Write UTF-8 JSON, indent 2, no comments.
