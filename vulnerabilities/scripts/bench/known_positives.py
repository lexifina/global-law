"""Recall on the cases confirmed by hand: does the expected detector flag each one?
python bench/known_positives.py [FLAGS.jsonl.gz] -> prints a table and writes bench/out/known_positives.json"""
import gzip, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAGS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "release" / "out" / "flags.jsonl.gz"

# (case, expected detectors, corpus prefix, path regex, reference regex or None)
CASES = [
    ("DE AWaffV § 34 no. 11 → deleted § 12", {"dead_fine", "placeholder_ref"}, "germany", r"^awaffv/0034\.md$", r"12"),
    ("DE AO § 31b(3a) → GwG § 50c never enacted", {"publisher_flag", "cross_act_missing"}, "germany", r"(verzeichnis\.json|ao_1977/0031b\.md)", r"50c|"),
    ("DE EIGV § 41 → deleted § 38", {"dead_fine", "placeholder_ref"}, "germany", r"^eigv/0041\.md$", r"38"),
    ("DE SchSiHafV § 42 → deleted §§ 27-30", {"dead_fine", "placeholder_ref"}, "germany", r"^schsihafv/0042\.md$", r"2[6-9]|30"),
    ("DE FuttMV § 40 → deleted § 4", {"dead_fine", "placeholder_ref"}, "germany", r"^futtmv_1981/0040\.md$", r"\b4\b"),
    ("DE EnergieStV § 111 → deleted § 101", {"dead_fine", "placeholder_ref"}, "germany", r"^energiestv/0111\.md$", r"101"),
    ("BR CLT art. 413 → repealed art. 376", {"dangling_ref", "placeholder_ref"}, "brazil", r"clt/art-413\.md$", r"376"),
    ("BR CPP art. 571 → repealed arts. 500/537", {"dangling_ref", "placeholder_ref"}, "brazil", r"codigo-de-processo-penal/art-571\.md$", r"537|500"),
    ("CH LwG art. 154 → repealed art. 151", {"dangling_ref", "placeholder_ref"}, "switzerland", r"^910\.1/art-154\.md$", r"151"),
    ("AR CP art. 23 → repealed arts. 213 ter/quáter", {"dangling_ref", "placeholder_ref"}, "argentina", r"codigo-penal/art-023\.md$", r"213"),
    ("CL Ley 17.798 art. 19 A → repealed art. 17 C", {"dangling_ref", "placeholder_ref"}, "chile", r"ley-17798/art-019-a\.md$", r"17"),
    ("FJ VAT Act s 71 → repealed s 63", {"dangling_ref", "placeholder_ref"}, "fiji", r"value-added-tax-act-1991/S71\.md$", r"63"),
    ("MT Cap. 31 art. 43 → repealed art. 33", {"dangling_ref", "placeholder_ref"}, "malta", r"^cap/31/43\.md$", r"33"),
    ("MT Cap. 31 art. 90 → repealed art. 88", {"dangling_ref", "placeholder_ref"}, "malta", r"^cap/31/90\.md$", r"88"),
    ("MT Cap. 10 art. 319 → repealed art. 190", {"dangling_ref", "placeholder_ref"}, "malta", r"^cap/10/319\.md$", r"190"),
    ("NWT Boilers Act s 43 → repealed s 47", {"dangling_ref", "placeholder_ref"}, "canada", r"boilers-pressure-vessels/s-043\.md$", r"47"),
    ("NL Stb. 2022, 7 in force before publication", {"retroactive_date"}, "netherlands", r"", r"2022.{0,4}7\b"),
    ("FR discard cap: end date amended to a past date", {"late_extension", "backdated_end"}, "france", r"arrete-2015-06-08-709246", r""),
    ("CH GTG art. 37a empty period", {"late_extension"}, "switzerland", r"^814\.91/art-037a\.md$", r""),
    ("FR loi 2023-380 art. 10 empty period", {"late_extension"}, "france", r"loi-2023-380/10\.md$", r""),
    ("ES Ley 16/1985 DT 5 empty period", {"late_extension"}, "spain", r"BOE-A-1985-12534/.*quinta", r""),
    ("ES RDL 11/2020 evictions empty period", {"late_extension"}, "spain", r"BOE-A-2020-4208/a1", r""),
    ("FR loi 2022-1158 art. 6 empty period", {"late_extension"}, "france", r"loi-2022-1158/6\.md$", r""),
    ("US-CA Gov. Code § 51298.5 empty period", {"late_extension"}, "united-states", r"gov/51298\.5\.md$", r""),
    ("US-IN IC 9-32-11-20 empty period", {"late_extension"}, "united-states", r"9-32-11-20\.md$", r""),
]


def main():
    with gzip.open(FLAGS, "rt", encoding="utf-8") as fh:
        flags = [json.loads(l) for l in fh]
    res = []
    for name, dets, jur, prx, rrx in CASES:
        hits = [f for f in flags if f["jurisdiction"] == jur and (not prx or re.search(prx, f["path"]))
                and (not rrx or re.search(rrx, f["reference"] + " " + f["summary"]))]
        good = [f for f in hits if f["detector"] in dets]
        res.append({"case": name, "expected": sorted(dets), "found": bool(good),
                    "by": sorted({f["detector"] for f in good}), "other_detectors": sorted({f["detector"] for f in hits} - dets)})
    n = sum(r["found"] for r in res)
    w = max(len(r["case"]) for r in res)
    for r in res:
        print(f"{'✔' if r['found'] else '✘'} {r['case']:<{w}}  {','.join(r['by']) or '-'}")
    print(f"\nrecall on confirmed cases: {n}/{len(res)} = {n / len(res):.0%}")
    out = ROOT / "bench" / "out"; out.mkdir(parents=True, exist_ok=True)
    (out / "known_positives.json").write_text(json.dumps({"recall": n / len(res), "cases": res}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
