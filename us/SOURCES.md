# Sources for United States

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked |
|---|---|---|---|---|---|---|---|
| [USLM](https://github.com/usgpo/uslm) | Standards | n/a | partly | n/a | XML schema | The US Code and Statutes XML schema. | yes |
| [LII (Cornell)](https://www.law.cornell.edu) | Legal information institutes | no | partly | no | HTML | US Code and CFR as current text. | yes |
| [US Code (OLRC)](https://uscode.house.gov/) | Official legislation | partly | yes | yes | USLM XML, XHTML; public domain | Release points, each current through a named public law. Only 2026 release-point zips are still served; older ones 404 (our own finding). Source credits cite each amending law. | yes |
| [GovInfo](https://api.govinfo.gov/docs/) · [Bulk data](https://www.govinfo.gov/bulkdata) | Official legislation | no | yes | yes | USLM, XML, PDF; public domain | Statutes at Large, public laws and statute compilations in USLM XML (beta) in bulk. The API needs a free api.data.gov key. | yes |
| [Congress.gov API](https://api.congress.gov) | Official legislation | partly | no | yes | JSON/XML | Bill text versions through /v3/bill/…/text. Key required, 5,000 requests an hour. | yes |
| [eCFR versioner API](https://www.ecfr.gov/reader-aids/ecfr-developer-resources) | Official legislation | yes | yes | yes | XML/JSON; public domain | Federal regulations on any day since January 2017, each change linked to its Federal Register citation. The best native point-in-time API in the Americas. | yes |
| [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) | Official legislation | n/a | yes | yes | JSON | JSON with no key. The oldest document in the API is dated 3 January 1994. The site sends flagged automated traffic to a CAPTCHA page. | yes |
| [Comparative Print Suite](https://compare.house.gov) | Tools | n/a | yes | no | HTML/PDF | Shows how a bill would change current law. House staff only, with a Senate pilot; not public. | yes |
| [Open States (Plural)](https://open.pluralpolicy.com) | Votes and bills | partly | no | yes | API, bulk CSV/JSON, monthly Postgres dump; public domain dedication | Bills in all 50 states, not codes. | yes |
| [LegiScan](https://legiscan.com/legiscan) | Votes and bills | partly | no | yes | API with key (free tier 30,000 queries a month); CC BY 4.0 | Bills and text versions only. | yes |
| [nickvido/us-code](https://github.com/nickvido/us-code) · [Write-up](https://v1d0b0t.github.io/blog/posts/2026-03-29-every-law-a-commit.html) | Git-for-law projects | partly | partly | n/a | git, no licence | 372 stars from an April 2026 HN post; dormant since then. Built from release-point snapshots. | yes |
| [wordstodata](https://www.wordstodata.com) | Git-for-law projects | n/a | n/a | yes | Commercial | Legal database aimed at agents. Its author argues legal diffing differs from git. | yes |
| [unitedstates/congress](https://github.com/unitedstates/congress) | Datasets | n/a | n/a | n/a | CC0 · 1,067 stars · pushed 2026-10-03 | Collectors for bills, amendments and votes. | yes |
| [usgpo/bulk-data](https://github.com/usgpo/bulk-data) | Datasets | n/a | n/a | n/a | 385 stars · pushed 2026-06 | Guides to govinfo bulk XML. | yes |
| [State Decoded](https://github.com/statedecoded/statedecoded) | Datasets | n/a | n/a | n/a | 269 stars · pushed 2026-10-11 | Parser and publisher for state codes. | yes |
| [us-congress-pipeline](https://github.com/junxit/us-congress-pipeline) | Git-for-law projects | yes | partly | n/a | 3 stars · pushed 2026-10-28 | Writes federal law into git: release points of the Code and daily statute compilations. | yes |
| [copyright-history](https://github.com/katelynsills/copyright-history) | Git-for-law projects | yes | partly | n/a | CC0 · 17 stars · pushed 2026-04-15 | US copyright law in git, 1790 to today. | yes |
| [open-us-law](https://github.com/Vaquill-AI/open-us-law) | Datasets | n/a | n/a | n/a | Apache-2.0 · 87 stars · pushed 2026-10-12 | 2M+ sections of state codes, the US Code and state constitutions. | yes |

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
