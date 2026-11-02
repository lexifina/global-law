#!/bin/sh
# Starts the MCP server (tools/mcp_server.py) with the first Python 3.9 or newer it finds: python3 on macOS and most
# Linux, python or py on Windows (where python3 is often the Microsoft Store's placeholder, which this skips).
# The project MCP configs (.mcp.json, .cursor/mcp.json, .vscode/mcp.json, .codex/config.toml) start it through git,
# which every clone has and which runs it from the top of the clone with a POSIX shell, Git for Windows included.
#   sh tools/mcp.sh
cd "$(dirname "$0")/.." || exit 1
for p in python3 python py; do
  if "$p" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null; then
    PYTHONDONTWRITEBYTECODE=1 exec "$p" tools/mcp_server.py "$@"
  fi
done
echo 'global-law: the MCP server needs Python 3.9 or newer, as python3, python or py on the PATH' >&2
exit 1
