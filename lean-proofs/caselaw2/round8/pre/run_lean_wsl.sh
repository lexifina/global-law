#!/bin/bash
# caselaw-lean-2 under WSL Ubuntu (Linux Lean 4.35.0). Windows Application Control blocks the Windows toolchain
# (lean.exe, lake.exe) and the compiled caselaw2.exe, so Lean is built and run inside WSL instead. The Windows tree
# stays the source of truth: every command first copies the code into the WSL mirror ~/caselaw2 (wsl/sync.sh).
# Call from Git Bash on Windows:
#   ./run_lean_wsl.sh sync [code|data|all]     copy code (lean-proofs, runner, audit, fixtures) and/or data + edges
#   ./run_lean_wsl.sh build                    lake build LegalProofs.CaseLaw2 + Run, and the native runner
#   ./run_lean_wsl.sh audit [check|lock]       audit/audit.py; lock, registry and log are copied back to Windows
#                                              (lock reads its --reason from wsl/lock_reason.txt)
#   ./run_lean_wsl.sh run <shards> [data] [edges] [out] [asOf]   run_lean.sh in the mirror (paths relative to the
#                                              mirror's caselaw-lean-2/); <out>/*.tsv is copied back to Windows
#   ./run_lean_wsl.sh sh '<command>'           a command in the mirror's caselaw-lean-2/, elan on PATH
# One-off setup in WSL (official installer, non-interactive):
#   curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.35.0
export MSYS_NO_PATHCONV=1   # Git Bash must not rewrite the /mnt/c path
exec wsl.exe -d Ubuntu -- bash -l /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/do.sh "$@"
