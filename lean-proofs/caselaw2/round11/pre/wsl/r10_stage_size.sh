#!/bin/bash
# round 10 (lean10): sizes of the WSL Lean tree and its build products (read only).
du -sh ~/caselaw2/lean-proofs/.lake ~/caselaw2/lean-proofs/.lake/build/lib/lean/LegalProofs/CaseLaw2 2>/dev/null
du -sh ~/caselaw2/lean-proofs --exclude=.lake 2>/dev/null
ls ~/caselaw2/lean-proofs/.lake/packages 2>/dev/null
