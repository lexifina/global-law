#!/bin/sh
# Starts the MCP server (tools/mcp_server.py) with the first Python 3.9 or newer it finds that can run it: python3 on
# macOS and most Linux, python or py on Windows (where python3 is often the Microsoft Store's placeholder, which this
# skips), else a versioned python3.N. Each candidate first compiles the server and loads its citation patterns, so a
# Python that cannot run this version of the server is passed over, and when none can, the reason is printed here
# instead of the client showing only "Connection closed".
# The project MCP configs (.mcp.json, .cursor/mcp.json, .vscode/mcp.json, .codex/config.toml) start it through git,
# which every clone has and which runs it from the top of the clone with a POSIX shell, Git for Windows included.
#   sh tools/mcp.sh
cd "$(dirname "$0")/.." || exit 1
why=''
for p in python3 python py python3.14 python3.13 python3.12 python3.11 python3.10 python3.9; do
  "$p" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null || continue
  if out=$(PYTHONDONTWRITEBYTECODE=1 "$p" -c '
import sys
sys.path.insert(0, "tools")
for f in ("tools/mcp_server.py", "tools/law.py"):
    compile(open(f, "rb").read(), f, "exec")
import usc_cite
' 2>&1); then
    GLOBAL_LAW_PYTHON="$p" PYTHONDONTWRITEBYTECODE=1 exec "$p" tools/mcp_server.py "$@"
  fi
  [ -n "$why" ] || why="$("$p" -c 'import platform; print(platform.python_version())' 2>/dev/null) ($p): $(printf '%s\n' "$out" | tail -n 1)"
done
if [ -n "$why" ]; then
  echo "global-law: no Python on the PATH can run this version of the MCP server. Python $why" >&2
  echo 'global-law: please report it at https://github.com/lexifina/global-law/issues, or use the hosted server (MCP.md)' >&2
else
  echo 'global-law: the MCP server needs Python 3.9 or newer, as python3, python or py on the PATH' >&2
fi
exit 1
