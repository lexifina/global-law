# Archive

`build-2026-10-29.py` is the script that built this repository from scratch up to 29 October 2026 (commit
`0e10db05b17`), kept byte for byte as it was then, so the blob hash REPRODUCE.md records still matches.

It cannot rebuild today's repository. Since 2 November 2026 the repository grows by fast-forward only, one commit
adding corpora or moving their pins at a time, and the build would write a whole new history from the first commit.
Most of the country repositories it read were also rewritten on 29 October, so it cannot repeat that build hash for
hash either. Never push its output over this repository. REPRODUCE.md, part one, says how the repository grows now
and how to check it (`tools/verify.py`, `tools/describe.py --check`).
