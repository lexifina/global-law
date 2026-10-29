# Judgments

Judgments that apply or discuss a provision in this tree, one file per provision at
`judgments/<path of the provision without .md>.jsonl`, one judgment per line:

```json
{"decided": "YYYY-MM-DD", "name": "...", "court": "...", "citation": "...", "url": "...", "how": "where it deals with the provision"}
```

A line may also give `"text_date"`: the date whose text the court applied, where that is not the day of the
decision. A bankruptcy court, for example, usually applies the Code as it stood when the petition was filed. Without
`text_date`, the day of the decision stands in for it.

The MCP server's `check_precedent` reads these and, for each judgment, says whether the text the court applied on the
day it decided is the text in force now, and if not, which laws changed it.

How these were gathered: each judgment was found on Find Case Law (The National Archives) and read individually to
confirm that it applies or discusses the provision; only its citation details are recorded here, with a link to the
judgment. No judgment text is copied and nothing was analysed by program. Judgments are © Crown copyright and published
under the Open Justice Licence (https://caselaw.nationalarchives.gov.uk/open-justice-licence); read them there.

US judgments (`judgments/us/...`) were found through the court's own published opinion, or law reports and case
updates, and each decision's court, date and citation were checked against the opinion or two separate sources. A
`url` is left out where no stable link to the opinion was found. US court opinions are public records, but only the
same citation details are kept here.

This is a first, small sample, not a complete list: Children and Families Act 2014 s. 42, and 11 U.S.C. §1182(1)
(subchapter V eligibility).
