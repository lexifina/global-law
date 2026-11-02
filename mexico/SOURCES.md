# Sources for Mexico

From the World Law Sources register, 28 October 2026. Each row was checked against the source’s own pages, an official description, or an Internet Archive copy where a site blocks automated readers. “Unconfirmed” rows could not be checked that way.

The rows for the DOF, SIDOF, Orden Jurídico Nacional and SCJN were added on 1 November 2026 and checked the same way.

| Source | Kind | Past versions by date | Names the amending act | API or bulk | Format and licence | Notes | Checked | robots.txt for AI agents |
|---|---|---|---|---|---|---|---|---|
| [Leyes Federales (Diputados)](https://www.diputados.gob.mx/LeyesBiblio/) | Official legislation | no | partly | no | PDF/DOC | Current text and original publication only, plus reform histories by date, article and period for each law. No dated consolidations and no API. | yes | allowed |
| [lex-mx](https://github.com/ingteranalvarez/lex-mx) | Git-for-law projects | yes | partly | n/a | 5 stars · pushed 2026-10-15 | All federal law in versioned Markdown, updated daily from the gazette. | yes | allowed, crawl delay 1 s |
| [Diario Oficial de la Federación](https://www.dof.gob.mx/) | Official gazette | n/a | yes (each decree as published) | no | HTML, PDF | Daily editions by date (matutina, vespertina, extraordinaria). | yes | `/nota_detalle.php?` (every decree’s page), `/nota_to_doc.php?` and `/copias_cert.php?` disallowed for all agents; date indexes allowed except some listed days |
| [SIDOF (Segob)](https://sidof.segob.gob.mx/) | Official gazette | n/a | yes (each decree as published) | yes: JSON web services, listed at /datos_abiertos (editions by date or year; notes by date, code or edition) | JSON, HTML, PDF | The DOF’s own system, from 1917: /dof/sidof/notas/05-02-1917 lists the Constitution as published (a scan). | yes | allowed, except `/CopiasCert?` and 100 listed notes |
| [Orden Jurídico Nacional](http://www.ordenjuridico.gob.mx/) | Official compilation | unconfirmed | unconfirmed | no | HTML; formats per act unconfirmed | Secretaría de Gobernación. Federal law by branch (legislative, judicial, executive, autonomous bodies), the 32 federal entities, municipal law and international instruments. | yes (home page) | none (robots.txt returns 404) |
| [SCJN, Sistema de Consulta de Ordenamientos](https://legislacion.scjn.gob.mx/Buscador/Paginas/Buscar.aspx) | Official compilation | unconfirmed: each act has a chronology page, which did not load in an automated browser | partly: searches the extracts of each reform and the legislative processes | no | HTML, Word, scanned gazette pages | Federal, Mexico City and state law, foreign law and treaties; gives each act’s last update and whether it is in force. | yes (search page) | none (robots.txt returns 404; the root returns 403) |

Before fetching: read each publisher’s robots.txt and obey any `Crawl-delay` and `Disallow` (legislation.gov.uk asks for 5 seconds; ecfr.gov disallows its full-text API). Ask the publisher for bulk access for large jobs, and record the rate used in REPRODUCE.md.

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).
