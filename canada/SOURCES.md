# Sources for Canada

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [CanLII](https://www.canlii.org) | Legal information institutes | yes | no | partly | HTML; metadata API with key | Point-in-time federal and provincial statutes since 2009 with a compare view. The API needs a key and returns metadata only (5,000 requests a day). | yes | some AI agents blocked: ClaudeBot, anthropic-ai, Claude-Web |
| [Justice Laws Website](https://laws-lois.justice.gc.ca) · [XML on GitHub](https://github.com/justicecanada/laws-lois-xml) | Official legislation | yes | partly | yes | XML; Open Government Licence – Canada | Point-in-time acts from 2003 and regulations from 2006, with in-force ranges per section. Official since 2009. | yes | allowed |
| [Ontario e-Laws](https://www.ontario.ca/laws) | Official legislation (Canada (Ontario)) | yes | partly | no | HTML | Point-in-time from 1 January 2004. History tables were discontinued. | yes | allowed, crawl delay 1 s |
| [OpenParliament.ca](https://openparliament.ca) | Votes and bills | n/a | n/a | yes | AGPL | Active. | yes | allowed |
| [BC Laws](https://www.bclaws.gov.bc.ca) | Official legislation (Canada (British Columbia)) | yes | n/a | yes | Consolidated | Open CiviX API with XML and point-in-time documents. The best sub-national API found. | yes | **blocked**: do not fetch with an AI agent |
| [LégisQuébec](https://www.legisquebec.gouv.qc.ca) | Official legislation (Canada (Québec)) | yes | n/a | no | Consolidated |  | yes | allowed |
| [Manitoba Laws](https://web2.gov.mb.ca/laws) | Official legislation (Canada (Manitoba)) | partly | n/a | no | Consolidated |  | yes | allowed |
| [legalize-ca](https://github.com/sandole/legalize-ca) | Git-for-law projects | yes | partly | n/a | pushed 2026-04 | Federal Acts, one dated commit per amendment. | yes | allowed, crawl delay 1 s |
| [a2aj/canadian-laws](https://huggingface.co/datasets/a2aj/canadian-laws) | Datasets | n/a | n/a | n/a | MIT · pushed 2026-10 | Federal plus 12 provinces and territories. | yes | allowed |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
