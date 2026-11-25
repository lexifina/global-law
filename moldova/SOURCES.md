# Sources for Moldova

The law built from these sources is in 2 repositories, pinned under `moldova/`; each one's REPRODUCE.md gives the sources it was built from and how.

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

The row for the Monitorul Oficial was added, and the note on the State Register extended, on 25 November 2026; both were checked the same way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [State Register of Legal Acts](https://www.legis.md) | Official legislation | yes | n/a | no | Consolidated | Dated editions of each act, each under its own `doc_id` (`/cautare/getResults?doc_id=<id>&lang=ro`); an act’s page lists them by in-force day (Codul fiscal nr. 1163/1997: 261 editions, 01.01.1998 to 01.01.2028). A search returns the latest edition, which may not be in force yet. Opens in a browser without a challenge; answered 403 to a plain scripted request on 25 November 2026. | yes | allowed |
| [Monitorul Oficial](https://monitorul.gov.md) | Official gazette | n/a | yes (each act as published) | no | HTML | One page per issue, `/ro/monitor/<id>` (3368 is nr. 543-544 of 31.10.2026, 3204 is nr. 659-661 of 31.12.2025). Answers plain requests. | yes | allowed (`Disallow:` empty) |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
