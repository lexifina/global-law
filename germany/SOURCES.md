# Sources for Germany

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [gesetze-im-internet.de](https://www.gesetze-im-internet.de) | Official legislation | no | partly | yes | XML zip per law (custom DTD) | Current text only, with amendments only as footnotes. History comes from community git repos. | yes | allowed |
| [NeuRIS (rechtsinformationen.bund.de)](https://testphase.rechtsinformationen.bund.de) | Official legislation | partly | partly | yes | LegalDocML.de (Akoma Ntoso profile) | Germany’s new legal information service, in test since April 2025. Versioning is planned. | yes | **blocked**: do not fetch with an AI agent |
| [bundestag/gesetze](https://github.com/bundestag/gesetze) | Git-for-law projects | partly | no | n/a | Markdown in git; Unlicense | 1,922 stars, dormant since November 2022. | yes | allowed, crawl delay 1 s |
| [c3e/grundgesetz](https://github.com/c3e/grundgesetz) | Git-for-law projects | yes | partly | n/a | Markdown in git | 531 stars, dormant since 2018. Our Grundgesetz repo is built from it, with corrections. | yes | allowed, crawl delay 1 s |
| [Open Legal Data](https://de.openlegaldata.io) | Datasets | no | no | yes | API; MIT code | German laws and court decisions with a REST API, dumps on Hugging Face and an MCP server. | yes | allowed, crawl delay 60 s |
| [Risks and Limits of Automatic Consolidation of Statutes](https://aclanthology.org/2025.nllp-1.29/) | Papers | n/a | n/a | n/a | NLLP 2025 | LLM consolidation looks 93–99% similar but matches exactly 50% (single) and 20% (chains). | yes | allowed |
| [Asking For An Old Friend](https://arxiv.org/abs/2605.23497) | Papers | n/a | n/a | n/a | arXiv, May 2026 | Models apply superseded rules and favour newer text; 312 expert-checked questions to evaluate against. | yes | allowed, crawl delay 15 s |
| [abgeordnetenwatch](https://www.abgeordnetenwatch.de) | Votes and bills | n/a | n/a | yes | API | MPs and votes. | yes | allowed |
| [gesetze-tools](https://github.com/bundestag/gesetze-tools) | Datasets | n/a | n/a | n/a | LGPL-3.0 · 136 stars · pushed 2026-05-04 | Scripts behind bundestag/gesetze. | yes | allowed, crawl delay 1 s |
| [QuantLaw/gesetze-im-internet](https://github.com/QuantLaw/gesetze-im-internet) | Git-for-law projects | yes | partly | n/a | BSD-3 · 46 stars · pushed 2026-10-28 | Daily snapshots of gesetze-im-internet.de from 10 June 2019 (its 2018 first commit is empty): the only open history of all German federal law. It has gaps (one day in May 2026 lost 3,646 files), so count a law as removed only if it never reappears. Earlier history has to be rebuilt from the federal gazette. | yes | allowed, crawl delay 1 s |
| [kmein/gesetze](https://github.com/kmein/gesetze) | Git-for-law projects | yes | partly | n/a | 49 stars · pushed 2026-10-28 | Daily plain-text snapshots of federal law. | yes | allowed, crawl delay 1 s |
| [bundesrecht (Gesetze für KI)](https://github.com/Gesetze-fuer-KI/bundesrecht) | Git-for-law projects | yes | partly | n/a | pushed 2026-10-28 | All federal law in Markdown with change history, synced nightly. | yes | allowed, crawl delay 1 s |
| [ris-norms (NeuRIS)](https://github.com/digitalservicebund/ris-norms) | Datasets | n/a | n/a | n/a | GPL-3.0 · 15 stars · pushed 2026-10-28 | Official tooling for Germany’s new legal information system and LegalDocML.de. | yes | allowed, crawl delay 1 s |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
