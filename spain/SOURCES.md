# Sources for Spain

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [BOE consolidated legislation](https://www.boe.es) · [API](https://www.boe.es/datosabiertos/api/api.php) | Official legislation | yes | yes | yes | XML, JSON, ELI | Every version since publication, block by block, each tagged with the amending norm. Only express amendments are consolidated; new versions appear 1–3 days later. | yes | allowed |
| [hpalacio/leyes](https://github.com/hpalacio/leyes) | Git-for-law projects | yes | partly | n/a | CC-BY-SA-4.0 · 84 stars · pushed 2026-05-20 | The Spanish constitution in git, an early example. | yes | allowed, crawl delay 1 s |
| [leyabierta/leyes](https://github.com/leyabierta/leyes) | Git-for-law projects | yes | partly | n/a | 4 stars · pushed 2026-10-27 | Consolidated law, one commit per reform at its historical date. | yes | allowed, crawl delay 1 s |
| [legislacion-es](https://github.com/vdr-lex/legislacion-es) | Git-for-law projects | yes | partly | n/a | pushed 2026-10-28 | The BOE plus all 17 regions, updated daily. | yes | allowed, crawl delay 1 s |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
