"""Default ("neutral") withholding-rate grids of CGI art. 204 H, III, 1, a-c, transcribed from the consolidated
text (DILA LEGI, via the global-law record) as in force in each rate year 2021-2026, plus the art. 204 H, II
per-part RFR threshold as codified on 1 September of each year. Writes ~/fr/data/pas_grids.jsonl.
One line per (rate_year, zone): lower bounds of brackets 2..20 (euros of monthly base), rates in per cent."""
import json, os
RATES = [0, 0.5, 1.3, 2.1, 2.9, 3.5, 4.1, 5.3, 7.5, 9.9, 11.9, 13.8, 15.8, 17.9, 20, 24, 28, 33, 38, 43]
G = {
 2021: dict(law="Loi n° 2020-1721 du 29 décembre 2020 (LFI 2021), art. 2", in_force="2021-01-01",
   metropole=[1420,1475,1570,1676,1791,1887,2012,2381,2725,3104,3494,4077,4888,6116,7640,10604,14362,22545,48292],
   gmr=[1629,1728,1904,2079,2296,2421,2505,2755,3406,4359,4952,5736,6872,7640,8684,11940,15865,24215,52930],
   gm=[1745,1887,2104,2371,2463,2547,2630,2922,4033,5219,5887,6830,7515,8325,9661,12997,16533,26496,55926],
   rfr_part=25654, rfr_part_law="Décret n° 2021-744 du 9 juin 2021 (25 000 € until 2021-06-11)"),
 2022: dict(law="Loi n° 2021-1900 du 30 décembre 2021 (LFI 2022), art. 2", in_force="2022-01-01",
   metropole=[1440,1496,1592,1699,1816,1913,2040,2414,2763,3147,3543,4134,4956,6202,7747,10752,14563,22860,48967],
   gmr=[1652,1752,1931,2108,2328,2455,2540,2794,3454,4420,5021,5816,6968,7747,8805,12107,16087,24554,53670],
   gm=[1769,1913,2133,2404,2497,2583,2667,2963,4089,5292,5969,6926,7620,8441,9796,13179,16764,26866,56708],
   rfr_part=25705, rfr_part_law="Décret n° 2022-782 du 4 mai 2022"),
 2023: dict(law="Loi n° 2022-1726 du 30 décembre 2022 (LFI 2023), art. 2", in_force="2023-01-01",
   metropole=[1518,1577,1678,1791,1914,2016,2150,2544,2912,3317,3734,4357,5224,6537,8165,11333,15349,24094,51611],
   gmr=[1741,1847,2035,2222,2454,2588,2677,2945,3641,4659,5292,6130,7344,8165,9280,12761,16956,25880,56568],
   gm=[1865,2016,2248,2534,2632,2722,2811,3123,4310,5578,6291,7300,8031,8897,10325,13891,17669,28317,59770],
   rfr_part=26065, rfr_part_law="Décret n° 2023-422 du 31 mai 2023"),
 2024: dict(law="Loi n° 2023-1322 du 29 décembre 2023 (LFI 2024), art. 2", in_force="2024-01-01",
   metropole=[1591,1653,1759,1877,2006,2113,2253,2666,3052,3476,3913,4566,5475,6851,8557,11877,16086,25251,54088],
   gmr=[1825,1936,2133,2329,2572,2712,2805,3086,3816,4883,5546,6424,7697,8557,9725,13374,17770,27122,59283],
   gm=[1955,2113,2356,2656,2758,2853,2946,3273,4517,5846,6593,7650,8416,9324,10821,14558,18517,29676,62639],
   rfr_part=27473, rfr_part_law="Décret n° 2024-496 du 30 mai 2024"),
 2025: dict(law="Loi n° 2025-127 du 14 février 2025 (LFI 2025), art. 2; applies to income from 1 May 2025 (2024 grid before)", in_force="2025-05-01",
   metropole=[1620,1683,1791,1911,2042,2151,2294,2714,3107,3539,3983,4648,5574,6974,8711,12091,16376,25706,55062],
   gmr=[1858,1971,2171,2371,2618,2761,2855,3142,3885,4971,5646,6540,7836,8711,9900,13615,18090,27610,60350],
   gm=[1990,2151,2398,2704,2808,2904,2999,3332,4598,5951,6712,7788,8567,9492,11016,14820,18850,30210,63767],
   rfr_part=28792, rfr_part_law="Décret n° 2025-547 du 17 juin 2025"),
 2026: dict(law="Loi n° 2026-103 du 19 février 2026 (LFI 2026), art. 4; applies to income from 1 May 2026 (2025 grid before)", in_force="2026-05-01",
   metropole=[1635,1698,1807,1928,2060,2170,2315,2738,3135,3571,4019,4690,5624,7037,8789,12200,16523,25937,55558],
   gmr=[1875,1989,2191,2392,2642,2786,2881,3170,3920,5016,5697,6599,7907,8789,9989,13738,18253,27858,60893],
   gm=[2008,2170,2420,2728,2833,2930,3026,3362,4639,6005,6772,7858,8644,9577,11115,14953,19020,30482,64341],
   rfr_part=29310, rfr_part_law="Décret n° 2026-562 du 29 juin 2026"),
}
ZN = {"metropole": "a) mainland and other", "gmr": "b) Guadeloupe, Martinique, La Réunion", "gm": "c) Guyane, Mayotte"}
out = os.path.expanduser("~/fr/data/pas_grids.jsonl")
with open(out, "w") as f:
    for y, g in G.items():
        for z in ("metropole", "gmr", "gm"):
            lo = g[z]
            assert len(lo) == 19 and lo == sorted(lo) and len(set(lo)) == 19, (y, z)
            f.write(json.dumps({"rate_year": y, "zone": z, "paragraph": "CGI art. 204 H, III, 1, " + ZN[z],
                                "law": g["law"], "in_force": g["in_force"], "lower_bounds": lo, "rates": RATES,
                                "rfr_threshold_per_part_204H_II": g["rfr_part"], "rfr_threshold_source": g["rfr_part_law"],
                                "source": "consolidated CGI (DILA LEGI) via global-law record; cross-check BOI-BAREME-000037"},
                               ensure_ascii=False) + "\n")
print("wrote", out)
