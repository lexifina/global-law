# Sources for Italy

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [Normattiva](https://www.normattiva.it) · [Open data](https://dati.normattiva.it) | Official legislation | yes | partly | yes | XML (URN:NIR) | Point-in-time collections. The new open-data service at dati.normattiva.it (2026) exports multiple versions only for acts from the last 5 years. | yes | allowed |
| [italian-laws-history](https://github.com/dej611/italian-laws-history) | Git-for-law projects | yes | partly | n/a | MIT · 5 stars · pushed 2026-10-27 | One commit per change in Normattiva; decree-laws on branches until converted. | yes | allowed, crawl delay 1 s |
| [Senate Akoma Ntoso bulk data](https://github.com/SenatoDellaRepubblica/AkomaNtosoBulkData) | Datasets | n/a | n/a | n/a | CC-BY-4.0 · 41 stars · pushed 2026-10-28 | Official Senate bulk data in Akoma Ntoso. | yes | allowed, crawl delay 1 s |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
