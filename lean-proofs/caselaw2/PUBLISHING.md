# Publishing Lean work to this repository: the checks

This file collects the rules used for the case-law releases of 13 and 16 November 2026 (rounds 2–4, then 5–13, with
the tax Entity and Hunt work). Run every check on the exact set of files to be committed, in a separate clean clone.

## 1. Choose what goes in

**Publish:**
- code and Lean;
- notes and round logs;
- audits and agent briefs;
- scores and aggregate tables;
- linking summaries and errors found in the sources;
- the frozen build's outputs (gzipped);
- film sources.

**Leave out:**
- **Bulk tables rebuilt from the corpus** (`decisions2.tsv`, `cert_text.tsv`, `holdings_cert_text.tsv`,
  `window_sha.tsv`). Publish 200-row samples and row counts instead.
- **Opinion texts handed to readers and auditors** (`store/text/`, `texts/`, `packs*/`), candidate scans, caches and
  staging mirrors.
- **Downloaded datasets** (`raw/`, `src/`). Each key's `SOURCE.md` says where to fetch them.
- **Model usage logs** (`*usage*`, run logs).
- **Site source** (`*.tsx`), and unpublished film cuts with their video IDs.
- **Binaries** (`.exe`, `.olean`, `.lake/`).

**Size:** nothing over 50 MB per file; a release of a few hundred MB of content at most. Gzip large TSVs.

## 2. Licences of third-party data

| Source | Licence | What may be published |
|---|---|---|
| Court opinions (Caselaw Access Project, CourtListener) | Public domain | Quotes, audit packets |
| FJC Integrated Database | US government work; the Dataverse copy is CC BY 4.0 | Keys and rows, with attribution |
| Shadow Docket Database, Beim–Hirsch–Kastellec, Brace & Hall, Federal Circuit Dataset Project | CC0 | Keys and rows |
| Pre-1930 tables of overruled state cases | Public domain (published before 1930) | Extracted facts |
| Constitution Annotated | US government work | The table; the PDFs are not copied |
| Supreme Court Database | CC BY-NC 3.0 US | Our identifiers, mappings and scores only; blank any copied coding column |
| Songer and Shepardized Courts of Appeals data | No licence stated | Identifiers, aggregates and scores only |
| Wikipedia list of overruled decisions | CC BY-SA 4.0 | Pair lists with attribution; not the wikitext |
| Christiansen & Eskridge, Hasen (override appendices) | Copyright | Pair lists only, never the extracted text |
| Lindquist state supreme court data | Click-through terms | Nothing unless someone with authority accepts them |

## 3. Scan the files

1. **Secrets:** API keys and tokens (`gho_`, `ghp_`, `github_pat_`, `sk-ant-`, `sk-…`, `AKIA…`, private-key
   blocks), cloud endpoint host names, and `.env` contents. Scripts must read keys from the environment only.
2. **Personal details:** user names and home paths (`C:\Users\<name>`, `/home/<name>`, `/mnt/c/Users/<name>`), in
   JSON-escaped form too. `../tools/caselaw2/publish/sanitize.py` replaces them with `~`, `$HOME` or `$USER`. Run it on
   every file in the release, then grep again.
3. **Email addresses:** only public contacts, and addresses quoted inside court opinions, may stay.
4. **Compressed files:** check `.gz` contents too (`zcat … | grep`).
5. **Already published files:** grep the whole repository, not only the new files. Earlier pushes can carry the same
   leak.

## 4. Merge with what is already public

Published copies may carry fixes the working folder does not have: path fixes, scripts that read the environment,
runnable layouts. For each modified file, compare the working copy with the published one:
- Where the published side only differs by such fixes, keep it.
- Where the working side has new work, take that, then re-apply the fixes.

Never let a release undo an earlier vetting edit.

## 5. Build and check before pushing

In a Linux file system (WSL on Windows), on a copy of the release:

```sh
lake build LegalProofs LegalProofs.CaseLaw2 TaxCode      # plus any standalone module being published
python3 caselaw2/audit/audit.py check                     # statement lock, axioms, no sorry
```

Files that `gen.py` scripts stitch together (`common.lean`, `tail_*.lean`) are fragments, not modules. Compile
standalone files whose names contain a dot with `lake env lean <file>`.

## 6. Push

- Commit as `Lexifina <global-law@lexifina.com>`, with no attribution lines.
- Push to `main` as a fast-forward only.
- Check `git log` and `git grep` on the pushed commit once more.
- Keep anything that fails these checks in a private repository.
