# Sources for France

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [Légifrance](https://www.legifrance.gouv.fr) · [LEGI dataset](https://www.data.gouv.fr/datasets/legi-codes-lois-et-reglements-consolides) · [DILA bulk](https://echanges.dila.gouv.fr/OPENDATA/) · [PISTE API](https://piste.gouv.fr) | Official legislation | yes | yes | yes | DILA XML; Licence Ouverte 2.0 | Article-level versions with in-force ranges. Bulk LEGI dumps at echanges.dila.gouv.fr/OPENDATA (full plus daily). The PISTE API needs free registration and OAuth. | yes | allowed |
| [Archéo Lex](https://github.com/Legilibre/Archeo-Lex) | Git-for-law projects | yes | yes | n/a | git from LEGI; WTFPL | Rebuilds the git history of French codes. 106 stars, dormant since 2019. | yes | allowed, crawl delay 1 s |
| [La Fabrique de la Loi](https://www.lafabriquedelaloi.fr) | Git-for-law projects | partly | yes | n/a | GPL-3.0 parser | How each French bill changed through Parliament. Parser dormant since 2022. | yes | allowed |
| [erdal/legifrance](https://huggingface.co/datasets/erdal/legifrance) | Datasets | n/a | n/a | n/a | Etalab-2.0 · pushed 2026 | Légifrance dataset. | yes | allowed |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
