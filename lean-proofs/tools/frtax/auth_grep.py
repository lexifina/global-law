"""Context search over extracted text files.
Usage: python3 -I harness/auth_grep.py [-w WIDTH] [-n MAXHITS] REGEX FILE_OR_DIR...
Prints file, the BOFiP paragraph number preceding each hit (a number alone on a line, if any), and a window of text."""
import os, re, sys
args = sys.argv[1:]
width, maxhits = 400, 20
while args and args[0].startswith("-"):
    o = args.pop(0)
    if o == "-w": width = int(args.pop(0))
    elif o == "-n": maxhits = int(args.pop(0))
rx = re.compile(args[0], re.I)
paths = []
for p in args[1:]:
    if os.path.isdir(p):
        paths += [os.path.join(p, f) for f in sorted(os.listdir(p))]
    else:
        paths.append(p)
para = re.compile(r"(?:^|\n)(\d{1,4})\n")
for p in paths:
    try: t = open(p, encoding="utf-8", errors="replace").read()
    except IsADirectoryError: continue
    hits = list(rx.finditer(t))
    if not hits: continue
    print(f"##### {p} ({len(hits)} hits)")
    for m in hits[:maxhits]:
        ps = [x.group(1) for x in para.finditer(t, 0, m.start())]
        s, e = max(0, m.start() - width), min(len(t), m.end() + width)
        print(f"--- §{ps[-1] if ps else '?'} @{m.start()}")
        print(t[s:e].replace("\n", " ⏎ "))
