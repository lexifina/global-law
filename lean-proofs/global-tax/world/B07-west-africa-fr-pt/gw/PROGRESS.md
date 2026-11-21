# Guinea-Bissau (GW) progress

**Status (2026-11-20T14:21Z): built (access tier B; rescue pass 3, see ~/cmp20/world/RESCUE.md, Pass 3). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: PT, TG.
- Statute read: Código do Imposto Profissional (Decreto n.º 23/83, de 6 de Agosto) as consolidated by the Direcção-Geral das Contribuições e Impostos on the Ministry of Economy and Finance's tax portal Kontaktu: 'Código do Imposto Profissional (Atualizado até 31-01-2021 e LGT de 2022)' (https://kontaktu.mef.gw/legislation, read 2026-11-20; gw/law/rescue3/kontaktu_legislation_2026-11-20.html, section extracted to cip_section_extracted.md): arts. 1-2 (Lei 9/2013 art. 19), 13, 18, 27(1) (Lei 1/2021 art. 10), 27(2) (Lei 8/2020 art. 17, Lei 1/2021 art. 17), 27(3)-(4), 28. Version: law as of 31 January 2021 plus the LGT of 2022. Cross-checks: MEF budget documents on mef.gw (Proposta OGE2023, Proposta OGE24, Proposta OGE25, OGE 2026; gw/law/rescue3/): none amends CIP art. 27 for 2023-2025; OGE 2026 amends CIP art. 1 and adds art. 27-A from 2026. DGCI 'Instruções de preenchimento da DECIRF' (Instrução de Serviço 20/DGCI/2021, kontaktu.mef.gw/api/public_files/BAo5g30BVxKCKoELsx7W.pdf): IP withheld under CIP art. 18; Imposto de Democracia under Lei 1/2021 art. 14.
- Registry correction: Imposto Profissional (CIP, Decreto 23/83) as amended to Lei 1/2021: employees taxed monthly at source on the gross payment by a nine-row table (1 % to 20 %) printed as rate x income minus a 'parcela a abater'; self-employed and authors' rights 10/20/25 %; pensions up to 200.000 FCFA a month outside the tax; no family relief; no later IRS reform in force for 2025 (none in the budget documents reached).
- Lean: 141 lines, 15 defs, 6 theorems, 11 #guard checks, 0 sorry; exe `lean/.lake/build/bin/gwtax` (worldMain). Scale: `scale.json`.
- Sources: `law/`, `law/rescue2/` and `law/rescue3/` (sha256 in each folder's SHA256SUMS).
- Unsupported: INSS employee contributions: rate text not reached (employeeSocial = 0); Imposto de Democracia (Lei 1/2021 art. 14, collected with the IP): text not reached; the OGE 2025 proposal (not law) would replace it by flat monthly amounts (IDDC/IDDPC); Imposto Complementar (CIP art. 10 refers to it): code not reached; capital income (Imposto de Capitais), rental income (Contribuição Predial Urbana) and capital gains: not modelled; enacted budget laws 2022-2025 not reached (version gap: DGCI consolidation to 31-01-2021 + LGT 2022)
- Routes tried in rescue pass 3 (UTC 2026-11-20; pass-1 routes below them):
  - kontaktu.mef.gw (the MEF/DGCI tax portal; laptop, 2026-11-20): /legislation carries the consolidated CIP, CCI (to Lei 1/2022), CIVA (Lei 4/2022), LGT (Lei 3/2022) with dated notes per paragraph: SOURCE USED. /instructions and /downloads: DGCI service instructions (DECIRF 2021) and forms
  - a WebSearch found kontaktu.mef.gw public_files links (DGCI DECIRF instructions) and named Decreto 23/83 / Decreto 4/84 and Lei 2/2015 as the IP's laws (commercial summaries used only to find the law)
  - mef.gw (laptop, answered this time): publicacoes/orcamento-geral-do-estado viewdocument 141 (Proposta OGE2023), 176 (Proposta OGE24), 177 (Proposta OGE25), 195 (OGE 2026, Dec 2025): their 'Alterações à legislação tributária' chapters were read; none touches CIP art. 27 before 2026
  - anp.gw (Assembleia Nacional Popular): legislação pages and WordPress media API: only the Regimento and Estatuto dos Deputados (2 PDFs)
  - dgci.gw, gov.gw, minfinancas.gw, impostos.gw: no answer from the laptop; Internet Archive CDX for dgci.gw, mef.gw, anp.gw: archive 'Temporarily Offline' / 504 during this pass
  - legis-palop.org: subscription/login (not used)
- Earlier routes (build, pass 1, pass 2):
  - build pass: Global law corpus metadata only; Wayback CDX of dgci.gw (156 rows, no documents), mef.gov.gw (0 rows)
  - rescue pass 1: mef.gw publications list OGE 2023, proposals OGE24/25, OGE 2026 (not opened: 'a proposal is not law')
  - rescue pass 2: mef.gw search 'imposto' (IGV/VAT only); dgci.gw no answer; legis-palop login; NATLEX/FAOLEX/Refworld Cloudflare; droit-afrique 403
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B07-west-africa-fr-pt/gw/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py GW`.
