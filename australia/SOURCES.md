# Sources for Australia

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [AustLII](https://www.austlii.edu.au) | Legal information institutes | partly | no | no | HTML | Point-in-time for NSW in full and SA and Queensland in part. Its usage policy forbids scraping, mirroring, API access and building AI datasets. | yes | **blocked**: do not fetch with an AI agent |
| [Federal Register of Legislation](https://www.legislation.gov.au) | Official legislation | yes | yes | yes | Creative Commons; API at api.prod.legislation.gov.au/v1 | Every compilation since 2013, some from 1973. The API is live, needs no key, and asks you to get in touch before a full crawl. | yes | allowed, crawl delay 10 s |
| [NSW legislation](https://legislation.nsw.gov.au/help/export) | Official legislation (Australia (NSW)) | yes | partly | yes | XML per version | Any historical version as XML by date. Scrape outside NSW business hours. | yes | allowed |
| [They Vote For You](https://theyvoteforyou.org.au) | Votes and bills | n/a | n/a | yes |  | Federal MPs’ votes. | yes | allowed |
| [Queensland Legislation](https://www.legislation.qld.gov.au) | Official legislation (Australia (Queensland)) | yes | n/a | yes | Consolidated | Free API with sign-up; XML from 2016. The only Australian state with a public API. | yes | some AI agents blocked: GPTBot |
| [Victorian Legislation](https://www.legislation.vic.gov.au) | Official legislation (Australia (Victoria)) | yes | n/a | no | Consolidated | Tables of previous versions. | yes | allowed, crawl delay 2 s |
| [WA Legislation](https://www.legislation.wa.gov.au) | Official legislation (Australia (WA)) | yes | n/a | no | Consolidated | Historical versions. | yes | allowed |
| [SA Legislation](https://www.legislation.sa.gov.au) | Official legislation (Australia (SA)) | yes | n/a | partly | Consolidated | Bulk dataset stopped in 2019. | yes | allowed |
| [Tasmanian Legislation](https://www.legislation.tas.gov.au) | Official legislation (Australia (Tasmania)) | yes | n/a | no | Consolidated |  | yes | allowed |
| [ACT Legislation Register](https://www.legislation.act.gov.au) | Official legislation (Australia (ACT)) | yes | n/a | no | Consolidated | Republications. | yes | allowed, crawl delay 10 s |
| [NT Legislation](https://legislation.nt.gov.au) | Official legislation (Australia (NT)) | yes | n/a | no | Consolidated |  | yes | allowed |
| [Open Australian Legal Corpus](https://huggingface.co/datasets/isaacus/open-australian-legal-corpus) | Datasets | n/a | n/a | n/a | 107 stars · pushed 2026 | Australian legislation and cases; 15,000 downloads. | yes | allowed |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
