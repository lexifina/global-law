# Sources for Japan

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [e-Gov 法令API v2](https://laws.e-gov.go.jp/api/2/swagger-ui/) | Official legislation | yes | yes | yes | XML, JSON (experimental) | Point-in-time retrieval from 1 April 2017. Released March 2025. | yes | allowed |
| [houritsu](https://github.com/Kohei-Wada/houritsu) | Git-for-law projects | yes | partly | n/a | MIT · pushed 2026-10-28 | Git history from the e-Gov law API, one commit per amendment. | yes | allowed, crawl delay 1 s |
| [elaws-history](https://github.com/kissge/elaws-history) | Git-for-law projects | yes | partly | n/a | 8 stars · pushed 2026-10-27 | Periodic archive of the full e-Gov dump. | yes | allowed, crawl delay 1 s |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
