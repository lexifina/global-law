# Sources for Taiwan

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [Laws & Regulations Database](https://law.moj.gov.tw) · [Bulk data](https://data.gov.tw/dataset/18289) | Official legislation | yes | yes | yes | XML; MOJ reuse licence | An amendment history and links to every old version per law. Open API at /api/swagger and monthly bulk on data.gov.tw. | yes | allowed |
| [mojLawSplit](https://github.com/kong0107/mojLawSplit) | Datasets | n/a | n/a | n/a | MIT · 18 stars · pushed 2026-10-23 | Splits the national laws database into per-law XML and JSON. | yes | allowed, crawl delay 1 s |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
