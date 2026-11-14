#!/usr/bin/env bash
# Round 7, agent `queue`: certify the B1 queue answers (ans/ans_<pack>.jsonl) into cert/.
# certify_recog.py here is round5/recog/certify_recog.py with only paths changed (see its header comment):
# items = items_queue.jsonl.gz, pack index = packs/items_index.tsv, live tables = round6/history/stage/final2.
# Extra options pass through (e.g. --skip-explicit, --all-witnesses).
set -euo pipefail
Q="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$Q/cert"
python -X utf8 "$Q/certify_recog.py" --answers "$Q/ans" --out "$Q/cert" --items "$Q/items_queue.jsonl.gz" "$@"
