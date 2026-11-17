"""Extract numeric worked examples from the BOFiP sanction documents (penalty study).
Usage: python3 -I harness/pen_bofip_examples.py BOFIPDIR OUT"""
import glob, os, re, sys
d, out = sys.argv[1], sys.argv[2]
PAT = ["BOI-CF-INF-10-*", "BOI-CF-INF-20-10-*", "BOI-DAE-*", "BOI-IR-PAS-50-*", "BOI-CF-IOR-30-*", "BOI-REC-PREA-20-20-40*",
       "BOI-CF-INF-20-20-*", "BOI-CF-INF-30-*"]
files = sorted(set(f for p in PAT for f in glob.glob(os.path.join(d, p))))
NUM = re.compile(r"\d[\d  .]*\s*(€|%)")
n = 0
with open(out, "w", encoding="utf-8") as fo:
    for f in files:
        L = open(f, encoding="utf-8").read().split("\n")
        i = 0
        while i < len(L):
            if re.match(r"\s*(Exemple|Illustration|Application)", L[i], re.I):
                j = i + 1
                while j < len(L) and j - i < 80 and not re.fullmatch(r"\d{1,4}", L[j].strip()) and not re.match(r"\s*Exemple", L[j], re.I):
                    j += 1
                blk = "\n".join(x for x in L[i:j] if x.strip())
                if len(NUM.findall(blk)) >= 2:
                    n += 1
                    fo.write(f"##### {os.path.basename(f)} line {i+1}\n{blk}\n\n")
                i = j
            else:
                i += 1
print(len(files), "files,", n, "numeric examples")
