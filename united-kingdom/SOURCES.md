# Sources for United Kingdom

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [legislation.gov.uk](https://www.legislation.gov.uk) | Official legislation | yes | yes | yes | CLML XML, Akoma Ntoso; OGL v3 | Append /data.xml or /data.akn to any URL. The effects register pairs each change with the provision it affects. A backlog of unapplied effects means some texts are out of date. | yes | allowed, crawl delay 5 s |
| [BAILII](https://www.bailii.org) | Legal information institutes | no | no | no | HTML | Mostly case law, but it has UK, Scotland, Wales, Northern Ireland and Ireland legislation databases too. | yes | allowed |
| [TheyWorkForYou / ParlParse](https://www.theyworkforyou.com) | Votes and bills | n/a | n/a | yes | API | Hansard and votes, to show the debate behind each UK change. Was returning 503 during our check. | yes | allowed |
| [i-dot-ai/lex](https://github.com/i-dot-ai/lex) | Datasets | n/a | n/a | n/a | MIT · 76 stars · pushed 2026-10-28 | UK government API over legislation.gov.uk. | yes | allowed, crawl delay 1 s |
| [legislation (data docs, CLML schema)](https://github.com/legislation) | Datasets | n/a | n/a | n/a | 5 stars · pushed 2026-07 | Official legislation.gov.uk data model and XML schema. | yes | allowed, crawl delay 1 s |
| [uk-akn-model](https://github.com/MattLynchPCO/uk-akn-model) | Datasets | n/a | n/a | n/a | 5 stars · pushed 2026-01 | UK implementation of Akoma Ntoso. | yes | allowed, crawl delay 1 s |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
