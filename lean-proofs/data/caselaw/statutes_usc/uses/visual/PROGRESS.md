# Code dynamics figure (four measures of the US Code since 1994)

Status: done (2026-11-12). Not committed; blog file not edited.

## Files
- `extract.py`: one pass over all 135,919 versions (6 workers, git cat-file --batch per worker, ~3 min). It writes `vstats.tsv` (words and section references per version), `credit.tsv` and `credit_law.tsv` (word-level blame of today's Code), `events.tsv` (top-level blocks a law rewrote, 1998–2018) and `shingles.tsv` (first 30 words of each inserted run of 30 or more words).
- `analyze.py`: builds `p1_heat.tsv`, `p2_complexity.tsv`, `p3_credit.tsv`, `p4_event.tsv`, `p4_effect.json` and `moved.tsv` (runs about 10 s).
- `figure.py`: builds `code_dynamics.svg`. `render.py` renders `code_dynamics.png` (1400 px) and `code_dynamics_760.png` (blog width) with headless Chrome.
- `BLOG.md`: one paragraph per panel, plus limits.

## Decisions
- Cross-references: **own regex count** (`extract.xrefs`: "section(s) N", each number in a list). `uses/xrefs/by_year.tsv` did not exist when the figure was built. `figure.py` switches to it automatically when it exists and covers 1994–2026; to do that, rerun `python figure.py && python render.py`. The text in BLOG.md would then need updating.
- Year points: the version in force on 1 Feb of the next year, so each January edition is included. 2026 is the record today.
- Titles 7, 28 and 39 start in the record with the 1995 edition (dated 1996-01-16). They are carried back to 1994 and blamed as "pre".
- Blame: diff by line first, then word-level difflib inside the changed lines. Laws of the 103rd Congress or earlier, and editions of 1994 or earlier, count as "pre". Later editions count as "edition".
- Event study: a treated unit is a (section, top-level block) rewritten by a law in year Y (2000–2015), not rewritten again within ±5 years, with at least 5 citations in Y−5..Y−1. Controls are 5 per event: same title, section untouched by any law in Y−5..Y+5, matched on pre-period shape (each year relative to Y−1) plus log level. The effect is post (Y+1..Y+5) relative to Y−1, treated vs control, with a bootstrap 95% CI over events.

## Headline numbers
- P1: 12.6% of sections changed by the 104th Congress, 2.2% by the 118th. Survival of cited sections: 65% at 10 years, 57% at 30 (never reaches half).
- P2: 14.96M → 24.80M words (+66%); 40,276 → 55,524 sections (+38%); 91,559 → 150,237 references (+64%).
- P3: of 24.80M words today, 44.8% were in force by 1994, 40.6% were written by laws since 1995 and 14.5% come from an edition with no law named. The 111th Congress wrote the most (4.8%).
- P4: 836 events (210 laws, 561 sections); +28% (95% CI +4% to +62%). Pre-trends are parallel (Y−5: 72.5 vs 75.9).
