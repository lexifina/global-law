# Sources for Sweden

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [Riksdagen open data (SFS)](https://data.riksdagen.se) | Official legislation | no | no | yes | XML/JSON/HTML | Current consolidated text only, with no structured list of amending acts. | yes | allowed |
| [ferenda](https://github.com/staffanm/ferenda) | Datasets | n/a | n/a | n/a | BSD-2 · 38 stars · pushed 2026-10-21 | Framework behind lagen.nu for downloading and publishing legal sources. | yes | allowed, crawl delay 1 s |
| [sfs-processor](https://github.com/se-lex/sfs-processor) | Git-for-law projects | yes | partly | n/a | 3 stars · pushed 2026-10-17 | Converts the Swedish Code of Statutes into Markdown and git. | yes | allowed, crawl delay 1 s |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
