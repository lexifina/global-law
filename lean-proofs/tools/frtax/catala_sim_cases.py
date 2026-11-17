"""Step 3d: one or more returns per disagreement class, for the DGFiP production simulator (sim_run.py ... all,
strictly sequential, 1.2 s apart, under flock ~/fr/.sim.lock). 24 requests.

usage: catala_sim_cases.py out.jsonl
"""
import json, sys

S = {"0AC": 1, "0DA": 1975}
C = {"0AM": 1, "0DA": 1975, "0DB": 1977}
CASES = [
    # P1 attached adult children (art. 196 B)
    ("c_p1_rank", 2022, {**C, "0CF": 2, "0F0": 2010, "0F1": 2012, "0DJ": 1, "0J0": 2002, "1AJ": 60000}),
    ("c_p1_widow", 2022, {"0AV": 1, "0DA": 1960, "0DJ": 1, "0J0": 2002, "1AJ": 40000}),
    ("c_p1_w", 2023, {"0AC": 1, "0DA": 1940, "0AW": 1, "0DJ": 1, "0J0": 2002, "1AS": 30000}),
    ("c_p1_alt", 2023, {**S, "0CH": 1, "0H0": 2012, "0DJ": 2, "0J0": 2002, "0J1": 2003, "1AJ": 40000}),
    # P2 disabled person under the roof (art. 196 A bis)
    ("c_p2_single", 2022, {**S, "0CR": 1, "1AJ": 30000}),
    ("c_p2_widow", 2023, {"0AV": 1, "0DA": 1957, "0CR": 1, "1AJ": 30000}),
    # P3 box W under 75 (art. 195, 1, f)
    ("c_p3_w", 2022, {"0AC": 1, "0DA": 1960, "0AW": 1, "1AJ": 30000}),
    # P4 widow(er) whose children are all in shared residence (art. 194, I)
    ("c_p4_two", 2022, {"0AV": 1, "0DA": 1980, "0CH": 2, "0H0": 2010, "0H1": 2012, "1AJ": 40000}),
    ("c_p4_one", 2023, {"0AV": 1, "0DA": 1980, "0CH": 1, "0H0": 2012, "1AJ": 40000}),
    # P5 box G (war widow's pension) with children, not a couple (art. 195, 5)
    ("c_p5_widow", 2022, {"0AV": 1, "0DA": 1966, "0AG": 1, "0CF": 3, "0F0": 2008, "0F1": 2010, "0F2": 2012,
                          "1AJ": 50000}),
    ("c_p5_div", 2023, {"0AD": 1, "0DA": 1975, "0AG": 1, "0CF": 1, "0F0": 2012, "1AJ": 30000}),
    ("c_p5_alt", 2022, {"0AD": 1, "0DA": 1975, "0AG": 1, "0CH": 1, "0H0": 2012, "1AJ": 30000}),
    # P6 couple with P (or F) and S, both over 74 (art. 195, 3 and 6)
    ("c_p6_ps", 2022, {"0AM": 1, "0DA": 1940, "0DB": 1942, "0AP": 1, "0AS": 1, "1AS": 30000, "1BS": 20000}),
    ("c_p6_fs", 2023, {"0AM": 1, "0DA": 1940, "0DB": 1942, "0AF": 1, "0AS": 1, "1AS": 30000, "1BS": 20000}),
    # P7 box L with box N (art. 195, 1, a, b, e: "vivent seuls")
    ("c_p7_ln", 2023, {**S, "0AL": 1, "0AN": 1, "1AJ": 30000}),
    # X2 boxes L and T together (Catala stops)
    ("c_x2_lt", 2022, {"0AD": 1, "0DA": 1975, "0AL": 1, "0BT": 1, "0CF": 1, "0F0": 2012, "1AJ": 30000}),
    # R1 pension allowance per kind of pension (art. 158, 5, a)
    ("c_r1_ao", 2022, {"0AC": 1, "0DA": 1950, "1AS": 27666, "1AO": 2143}),
    ("c_r1_az", 2022, {"0AC": 1, "0DA": 1950, "1AS": 4205, "1AZ": 7548}),
    ("c_r1_2023", 2023, {"0AC": 1, "0DA": 1950, "1AS": 20000, "1AO": 1500}),
    # O1 OpenFisca leaves out the non-professional BNC deficit 5JJ (Catala tests BNC1 and BNC4)
    ("c_t_bnc1", 2022, {"0AM": 1, "0DA": 1980, "0DB": 1982, "5JG": 1000, "5JJ": 15000, "5LU": 3000}),
    ("c_t_bnc4", 2023, {"0AC": 1, "0DA": 1980, "5KU": 12399, "5JG": 52676, "5JJ": 76988, "5SO": 1374}),
    # Catala tests confirmed against production
    ("c_t_bic1", 2023, {"0AC": 1, "0DA": 1980, "5NO": 7514, "5NP": 3859, "5NC": 11225, "5NG": 1000, "5QS": 3000,
                        "5KC": 60000, "5UI": 500, "5KF": 10000}),
    ("c_t_bnc3", 2022, {"0AM": 1, "0DA": 1980, "0DB": 1982, "0CF": 1, "0F0": 2010, "5JG": 22540, "5JJ": 4000,
                        "5RF": 10000, "5MU": 1000, "5MY": 200, "5MD": 500, "5LT": 1000, "5MT": 25000}),
    ("c_t_ts5", 2022, {"0AM": 1, "0DA": 1980, "0DB": 1982, "0CF": 1, "0F0": 2010, "1AS": 72000, "1BS": 300,
                       "1CT": 100000}),
]

with open(sys.argv[1], "w") as f:
    for i, y, b in CASES:
        f.write(json.dumps({"id": i, "year": y, "boxes": b}) + "\n")
print(len(CASES))
