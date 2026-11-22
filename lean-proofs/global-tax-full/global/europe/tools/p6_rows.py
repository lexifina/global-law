# pass 6 rows (R1 Europe, 2026-11-21): P5 (4100, 4400) and P6 (4200, 4300). exec'd by the spec after p6lib.py.
# Each row: (cc, oecd, function of S). A row is applied only to the spec that holds a grade-C entry for that code.
# B rows from PwC Worldwide Tax Summaries state facts only (no PwC text is copied); A rows quote the statute.

def _pw(cc, page="Individual - Other taxes", name="pwc_indother_wb2025"):
    return pwc(cc, name, page)


def _pwd(cc, name="pwc_indother_wb2025", page="Individual - Other taxes"):
    p = _pw(cc, page, name)
    return "PwC WWTS " + page + ", " + p.split(", accessed ")[1].split(" (")[0] + " (" + p.split(" (")[-1].split(";")[0] + ")"


HOMES = ("home", "realEstate", "land")

# ---------------------------------------------------------------- 4200 / 4300 / 4400 cited absences (B)
_ABS = {
 # cc: [(oecd, tax, fact)]  (pass 7: facts in short form; PwC wording not copied)
 "BG": [("4200", "Net wealth tax (not levied)", "net wealth tax: none")],
 "BY": [("4200", "Net wealth tax (not levied)", "wealth tax: none (2021 capture, the newest archived)"),
        ("4300", "Inheritance and gift tax (not levied)", "inheritance / gift tax: none as such; receipts fall under the PIT (inheritances exempt, gifts partly exempt; the 1.x PIT)")],
 "CZ": [("4200", "Net wealth tax (not levied)", "net wealth tax: none"),
        ("4400", "Real estate acquisition tax (not levied)", "real estate acquisition / transfer tax: none")],
 "DE": [("4200", "Vermögensteuer (not levied)", "Vermögensteuer: not levied at present")],
 "DK": [("4200", "Formueskat (not levied)", "formueskat: abolished from 1997")],
 "FI": [("4200", "Varallisuusvero (not levied)", "net wealth tax: none")],
 "HR": [("4200", "Net wealth tax (not levied)", "net wealth tax: none")],
 "HU": [("4200", "Net wealth tax (not levied)", "net wealth tax: none")],
 "IE": [("4200", "Net wealth tax (not levied)", "net wealth tax on individuals: none")],
 "IS": [("4200", "Net wealth tax (not levied)", "net wealth tax: none at present")],
 "IT": [("4200", "General net wealth tax (not levied)", "general net wealth tax: none; IVIE (1,06 % from 2024) and IVAFE reach only real estate and financial assets abroad (DL 201/2011 art. 19, not read): not modelled, assets in the input taken as Italian")],
 "LT": [("4200", "Net wealth tax (not levied)", "net wealth tax: none (live page reviewed 2026)")],
 "LU": [("4200", "Impôt sur la fortune des personnes physiques (not levied)", "wealth tax on individuals: abolished from 1.1.2006 (the companies' impôt sur la fortune is outside this household entry)")],
 "LV": [("4200", "Net wealth tax (not levied)", "net wealth tax: none")],
 "MT": [("4200", "Net wealth tax (not levied)", "net wealth tax: none"),
        ("4300", "Inheritance, estate and gift tax (not levied)", "inheritance / estate / gift tax: none; duty on documents on transmissions causa mortis of immovables (5 %) and shares is a stamp duty (4400, not modelled)")],
 "NL": [("4200", "Vermogensbelasting (not levied)", "wealth tax: none as such; deemed return on savings and investments taxed in box 3 of the income tax (1100, the 1.x model)")],
 "PT": [("4200", "Net wealth tax (not levied)", "net wealth tax: none")],
 "RO": [("4200", "Net wealth tax (not levied)", "net wealth tax: none"),
        ("4300", "Inheritance and gift tax (not levied)", "inheritance / gift tax: none; income tax on inherited real estate where the succession is not settled within 2 years (1100)")],
 "RU": [("4200", "Net wealth tax (not levied)", "net wealth tax: none (2022 capture, the newest archived)"),
        ("4300", "Inheritance and gift tax (not levied)", "inheritance / gift tax: abolished from 1.1.2006; some gifts are PIT income (close relatives exempt; the 1.x PIT)")],
 "SK": [("4200", "Net wealth tax (not levied)", "net wealth tax: none")],
 "UA": [("4200", "Net wealth tax (not levied)", "net wealth tax: none"),
        ("4300", "Inheritance and gift tax (not levied)", "inheritance / gift tax: none as such; PIT on inheritances and gifts 0 % (family), 5 % (other residents), 18 % (non-residents) (1100)")],
 "XK": [("4200", "Net wealth tax (not levied)", "net wealth tax: none"),
        ("4300", "Inheritance and gift tax (not levied)", "inheritance / gift tax: none as such; PIT (0-10 %) on inheritances from others than spouse, child or parent and on gifts, each above EUR 5 000 (1100)")],
 "LI": [("4300", "Inheritance, estate and gift tax (not levied)", "inheritance / estate / gift tax: none")],
}
_ABS_CORP = {
 "SK": [("4400", "Real estate transfer tax (not levied)", "transfer tax / stamp duty on property or shares: none (small administrative fees only)")],
 "LT": [("4400", "Real estate transfer or stamp duty (not levied)", "stamp duty: none; state-service fees only (notary, registers)")],
 "RO": [("4400", "Real estate transfer tax (not levied)", "property transfer tax: none; notary fees only")],
}
_ABS_CORPF = {"AL": [("4400", "Stamp duty on property sales (not levied)", "stamp duty on sale contracts of land or property: none; notary tax ALL 1 000 per immovable-property contract (not modelled)")]}

# ---------------------------------------------------------------- 4100 municipal-only notes (stay C)
_NOTE41 = {
 "BG": "rates set by each municipality between 0,01 % and 0,45 % of the tax value (ЗМДТ); no reference municipality's decision read",
 "CZ": "zákon 338/1992 Sb. sets per-m2 rates by type, multiplied by coefficients each municipality sets; area inputs are not in the model",
 "EE": "land tax only (buildings untaxed), at 0,1-1 % of the assessed land value as each municipality sets; reference municipality's rate not read",
 "FI": "kiinteistövero: rates set by each municipality within the Kiinteistöverolaki bands; reference municipality's rates not read",
 "HU": "építményadó / telekadó levied at each municipality's discretion up to the caps of the Htv.; Budapest district decrees not read",
 "IS": "fasteignaskattur set by each municipality; reference municipality's rate not read",
 "NO": "eiendomsskatt is optional and set by each municipality (homes 1-4 per mille, a basic deduction may apply); Oslo's vedtak not read",
 "PL": "podatek od nieruchomości: per-m2 rates set by each gmina within the national maxima of the ustawa o podatkach i opłatach lokalnych (2025: business buildings PLN 34,00/m2); area inputs are not in the model",
 "PT": "IMI: municipal rates on the valor patrimonial tributário (0,3-0,45 % for urban property, CIMI art. 112); Lisboa's deliberação not read",
 "RO": "impozit pe clădiri / teren set by the local council (Codul fiscal art. 457-465 ranges); București rates not read",
 "RS": "porez na imovinu: rates set by each local government within the Zakon o porezima na imovinu ranges; Beograd decision not read",
 "RU": "налог на имущество физических лиц: municipal rates on cadastral value within НК ст. 406 ranges; Moscow law not read",
 "UA": "податок на нерухоме майно: per-m2 rates set by local councils (up to 1,5 % of the minimum wage per m2) with a per-dwelling area exemption; Kyiv decision not read",
 "GR": "ENFIA (ν. 4223/2013) is national but per m2 with location and use coefficients (EUR 2-16,20 per m2 for buildings): area inputs are not in the model",
 "SK": "daň z nehnuteľností (zákon 582/2004 Z. z.): per-m2 rates set by each municipality; area inputs are not in the model",
 "ME": "porez na nepokretnosti: 0,25-1 % of market value as each municipality sets; Podgorica decision not read",
 "MK": "данок на имот: 0,10-0,20 % of market value as each municipality sets; Skopje decision not read",
 "BA": "property tax set by each FBiH canton (per m2 or value); Sarajevo Canton law not read (RS: 0,20 %, BD: 0,05-1 %)",
 "XK": "property tax set by each municipality; Prishtina rate not read",
}
_NOTE44 = {
 "BG": "данък при придобиване на имущество: 0,1-3 % as each municipality sets (ЗМДТ); Sofia rate not read",
 "BA": "FBiH transfer tax set by each canton, at most 5 %; Sarajevo Canton law not read (none in RS and BD)",
 "MK": "данок на промет на недвижности: 2-4 % set by each municipal council, paid by the seller; Skopje decision not read",
 "ME": "porez na promet nepokretnosti: progressive 3-6 % on market value; the band limits are not in the B source and the act was not read",
 "XK": "property transaction fee at municipal level, EUR 150 per unit (100 m2 of building, 1 ha of land): area inputs are not in the model",
}


def _absent_rows(S, table, page, name):
    for o, tax, fact in table.get(S["cc"], []):
        if any(str(t.get("oecd")) == o and t.get("grade") == "C" for t in S["taxes"]):
            p6_absent(S, o, tax, _pw(S["cc"], page, name), fact, _pwd(S["cc"], name, page), grade="B")


# ---------------------------------------------------------------- modelled rows
def _it(S):
    if S["cc"] != "IT":
        return
    if _has(S, "4300"):
        src = ("D.Lgs. 346/1990 (TUS successioni e donazioni) art. 7, normattiva vigente al 2025-07-01 (testo in vigore dal "
               "3-10-2024, effect from 1.1.2025 by D.Lgs. 139/2024 art. 9 c. 3), `it/law/tus346_vig20250701_art7.txt`; art. 56-bis "
               "c. 2 (`..._art56.txt`) refers to the gift rate of art. 56 c. 1 lett. d)")
        p6_inherit(S, "succ", "Imposta sulle successioni e donazioni",
                   [(1000000, [(0, 400)]), (100000, [(0, 600)]), (0, [(0, 600)]), (0, [(0, 800)])],
                   dict(spouse=0, child=0, grandchild=0, parent=0, sibling=1, nieceNephew=2, otherRelative=2),
                   "D.Lgs. 346/1990 art. 7 c. 1 lett. a)-d) (4 % above EUR 1 000 000 per beneficiary; 6 % above EUR 100 000; 6 %; 8 %)",
                   "normattiva, art. 7 testo in vigore dal 3-10-2024 (applies to successions from 1.1.2025)", "A", src,
                   ["art. 7 c. 1 (rates by relationship, each on the beneficiary's net share): a) spouse and lineal relatives 4 % on the part above EUR 1 000 000; b) brothers and sisters 6 % above EUR 100 000; c) other relatives to the fourth degree, lineal in-laws and collateral in-laws to the third degree 6 % with no franchigia; d) everyone else 8 %",
                    "art. 7 c. 2: a disabled beneficiary (L. 104/1992 art. 3 c. 3) is taxed only above EUR 1 500 000 (not modelled)"],
                   uns=[("g.transfers.any (·.kind == .gift)", "gifts: art. 56 (same letters a)-d), cited through art. 56-bis c. 2) not read; the art. 7 rates and franchigie are applied; the coacervo of earlier gifts (art. 57) is not applied"),
                        ("!g.transfers.isEmpty", "imposte ipotecaria e catastale (2 % + 1 %) on inherited real estate, the disabled-beneficiary franchigia (art. 7 c. 2), exempt beneficiaries (art. 3: public bodies, ONLUS) and reductions (arts. 25-26) not modelled")])
    if _has(S, "4400"):
        p6_transfer(S, "reg", "Imposta di registro (trasferimenti immobiliari)", [(0, 900)],
                    "DPR 131/1986 Tariffa parte I art. 1 (9 %; 2 % prima casa, nota II-bis)",
                    "normattiva vigente al 2025-07-01 (Tariffa parte I art. 1, `it/law/tur131_vig20250701_art1_1.txt`)", "A",
                    "DPR 131/1986 (TU imposta di registro), Tariffa parte I art. 1, normattiva vigente al 2025-07-01 (`it/law/tur131_vig20250701_art1_1.txt`)",
                    ["Tariffa I art. 1: \"Atti traslativi a titolo oneroso della proprietà di beni immobili in genere ... 9 per cento\"; \"Se il trasferimento ha per oggetto case di abitazione, ad eccezione di quelle di categoria catastale A1, A8 e A9, ove ricorrano le condizioni di cui alla nota II-bis) 2 per cento\"; terreni agricoli to non-farmers \"15 per cento\"",
                     "nota II-bis: the 2 % needs residence in the comune and no other home there or bought with the relief (the input's firstHome flag stands for these conditions)"],
                    firstCap=10 ** 12, firstBands=[(0, 200)],
                    uns=[("!g.purchases.isEmpty", "base: the price (the prezzo-valore rule on cadastral value for homes, L. 266/2005 c. 497, not applied); minimum EUR 1 000 (D.Lgs. 23/2011 art. 10, not read); imposte ipotecaria/catastale EUR 50 + 50; agricultural land 15 %; sales by builders under IVA (registro EUR 200) not separated")])


def _pl(S):
    if S["cc"] != "PL":
        return
    if _has(S, "4300"):
        p6_inherit(S, "sd", "Podatek od spadków i darowizn",
                   [(36120, [(0, 300), (10278, 500), (20556, 700)]), (27090, [(0, 700), (10278, 900), (20556, 1200)]),
                    (5733, [(0, 1200), (10278, 1600), (20556, 2000)])],
                   dict(nieceNephew=1, otherRelative=1), "ustawa o podatku od spadków i darowizn art. 4a ust. 1, art. 9 ust. 1-2, art. 14 ust. 3, art. 15 ust. 1",
                   "t.j. Dz.U. 2024 poz. 1837 (amended by Dz.U. 2025 poz. 769, 1064: not the rates or allowances)", "A",
                   "ustawa z dnia 28 lipca 1983 r. o podatku od spadków i darowizn, tekst jednolity Dz.U. 2024 poz. 1837 (Sejm ELI API, `pl/law/spadki_tj2024_1837.pdf`); amending act Dz.U. 2025 poz. 1064 read (`pl/law/spadki_zm2025_1064.pdf`: arts. 4a, 6, 12, 13, 18-19, procedure and valuation only)",
                    ["art. 4a ust. 1: \"Zwalnia się od podatku nabycie własności rzeczy lub praw majątkowych przez małżonka, zstępnych, wstępnych, pasierba, rodzeństwo, ojczyma i macochę, jeżeli\" reported within 6 months",
                     "art. 9 ust. 1: tax-free amounts \"36 120 zł\" (grupa I), \"27 090 zł\" (II), \"5733 zł\" (III); ust. 2: acquisitions from the same person in the year and the 5 preceding years are added, less the tax on the earlier ones",
                     "art. 14 ust. 3: grupa I spouse, descendants, ascendants, stepchild, children-in-law, siblings, step-parents, parents-in-law; II descendants of siblings, siblings of parents, ...; III others",
                     "art. 15 ust. 1: I 3 % to 10 278 zł, 308,30 zł + 5 % to 20 556 zł, 822,20 zł + 7 % above; II 7 % / 719,50 + 9 % / 1644,50 + 12 %; III 12 % / 1233,40 + 16 % / 2877,90 + 20 %"],
                   exempt=("spouse", "child", "grandchild", "parent", "sibling"), lookback=6,
                   uns=[("!g.transfers.isEmpty", "art. 4a exemption assumes the 6-month report is made; otherwise grupa I; otherRelative taken as grupa II (in-laws are I, cousins III); the scale's fixed amounts are rounded (308,30 zł vs 3 % of 10 278 = 308,34); look-back taken as 6 years")])


def _hu(S):
    if S["cc"] != "HU":
        return
    if _has(S, "4300"):
        p6_inherit(S, "orokl", "Öröklési illeték", [(0, [(0, 1800)])], {},
                   "Itv. 12. § (1) (18 %); 16. § (1) i)-j) (lineal relatives, surviving spouse, siblings exempt)",
                   "net.jogtar.hu Hatályos Jogszabályok Gyűjteménye (current text, fetched 2026-11-21; provisions unchanged in 2025 not checked against the 2025 időállapot)", "A",
                   "1990. évi XCIII. törvény az illetékekről (Itv.), net.jogtar.hu `docid=99000093.tv` (`hu/law/itv.txt`)",
                   ["12. § (1): \"Az öröklési és az ajándékozási illeték általános mértéke ... az egy-egy örökösnek, hagyományosnak juttatott örökség és a megajándékozottnak juttatott ajándék tiszta értéke után 18%.\" (2): lakástulajdon \"9%\"",
                    "16. § (1) i): \"az örökhagyó egyenes ági rokona ..., valamint túlélő házastársa által megszerzett örökrész\"; j): \"az örökhagyó testvére által megszerzett örökrész\"; d): movables up to 300 000 Ft per heir"],
                   exempt=("spouse", "child", "grandchild", "parent", "sibling"), only="inheritance",
                   uns=[("!g.transfers.isEmpty", "the 9 % rate for a home (12. § (2)), the 300 000 Ft movables exemption (16. § (1) d)) and step-relatives' 20 000 000 Ft (c)) not applied"),
                        ("g.transfers.any (·.kind == .gift)", "ajándékozási illeték (gifts, 11. §, exemptions in 17. §) not modelled")])
    if _has(S, "4400"):
        p6_transfer(S, "vagyon", "Visszterhes vagyonátruházási illeték (ingatlan)", [(0, 400), (1000000000, 200)],
                    "Itv. 19. § (1) (4 % to HUF 1 billion per property, 2 % above, at most HUF 200 million)",
                    "net.jogtar.hu current text (fetched 2026-11-21)", "A",
                    "Itv., net.jogtar.hu `docid=99000093.tv` (`hu/law/itv.txt`)",
                    ["19. § (1): \"ingatlan ... megszerzése esetén ingatlanonként 1 milliárd forintig 4%, a forgalmi érték ezt meghaladó része után 2%, de ingatlanonként legfeljebb 200 millió forint\""],
                    maximum=200000000,
                    uns=[("!g.purchases.isEmpty", "the base is the market value (forgalmi érték): the price stands in; first-home and young-buyer reliefs (26. §) and the home-swap credit (21. §) not applied")])


def _se(S):
    if S["cc"] != "SE":
        return
    if _has(S, "4400"):
        p6_transfer(S, "stamp", "Stämpelskatt (lagfart)", [(0, 150)],
                    "Lag (1984:404) om stämpelskatt vid inskrivningsmyndigheter 8 § (15 kr per full 1 000 kr; legal persons 42,50 kr)",
                    "data.riksdagen.se (ändrad t.o.m. SFS 2025:391)", "A",
                    "Lag (1984:404), data.riksdagen.se `sfs-1984-404.text` (`se/law/sfs-1984-404.txt`, ändrad t.o.m. SFS 2025:391)",
                    ["8 §: \"Stämpelskatten är femton kronor för varje fullt tusental kronor av egendomens värde. Förvärvas egendomen av en juridisk person är dock skatten fyrtiotvå kronor och femtio öre för varje fullt tusental kronor\""],
                    uns=[("!g.purchases.isEmpty", "the value is not rounded down to full thousands (at most 15 kr); a company buyer pays 4,25 % (not separated); the value may be the taxeringsvärde where higher (not read); pantbrev 2 % not modelled")])
    if _has(S, "4100"):
        _drop(S, "4100")
        st = "Lag (2007:1398) om kommunal fastighetsavgift 3 § a) (6 000 kr per småhus for 2008, indexed by the inkomstbasbelopp; at most 0,75 % of the taxeringsvärde)"
        S["lean"] += ("\n/-- " + st + "; IBB 2008 48 000 kr (SFS 2007:1023), 2025 80 600 kr (SFS 2024:987): +67,92 %. -/\n"
                      "def p6fastCap : Int := 6000 + divR .down (6000 * 6792) 10000\n"
                      "def p6fastighetsavgift (a : Asset) : Int :=\n  if a.kind == .home then min p6fastCap (divR .down (75 * pos a.statutoryValue) 10000) else 0\n"
                      "def p6fastCharges (as : List Asset) : List Charge :=\n  (as.zipIdx.filter fun (a, _) => a.kind == .home).map fun (a, i) =>\n"
                      "    charge .propertyRecurrent \"Kommunal fastighetsavgift (småhus)\" a.statutoryValue (fun v => v) (fun _ => p6fastighetsavgift a)\n"
                      "      (event := s!\"asset {i + 1}\") (level := .local) (statute := " + _q(st) + ")\n")
        S["families"].append(("4100 Kommunal fastighetsavgift", [".propertyRecurrent"], "p6fastCharges g.assets"))
        S["guards"] += ["-- 6 000 x (1 + (80 600 - 48 000) / 48 000 = 67,92 %) = 10 075,20 -> 10 075 kr (öretal faller bort)",
                        "p6fastCap == 10075",
                        "p6fastighetsavgift { kind := .home, value := 1000000 } == 7500",
                        "p6fastighetsavgift { kind := .home, value := 3000000, assessed := 1343333 } == 10074",
                        "p6fastighetsavgift { kind := .home, value := 5000000 } == 10075",
                        "p6fastighetsavgift { kind := .realEstate, value := 5000000 } == 0"]
        S["unsupported"] += [("g.assets.any (fun a => a.kind == .home && a.assessed < 0)", "4100 fastighetsavgift: no taxeringsvärde given: the market value stands in (the taxeringsvärde is about 75 % of it)"),
                             ("g.assets.any (fun a => a.kind == .realEstate)", "4100 fastighetsavgift: hyreshus (1 027 kr per lägenhet indexed, at most 0,3 %) and the statlig fastighetsskatt on commercial property not modelled")]
        S["notes"].append("SE 4100: Lag (2007:1398) 3 § with IBB 2008/2025 (A)")
        S["taxes"].append({"oecd": "4100", "tax": "Kommunal fastighetsavgift (småhus)", "statute": st,
                           "dated": "data.riksdagen.se (ändrad t.o.m. SFS 2012:743); Förordning (2007:1023) 48 000 kr; Förordning (2024:987) 80 600 kr för år 2025",
                           "grade": "A", "kernel_parts": ["charge (min of a fixed amount and 0,75 %)"],
                           "unsupported": ["new dwellings' exemption (6 §) and half-fee years", "a bostadsrätt is charged to the förening, not the member", "the taxeringsvärde is an input (asset.assessed)"]})
        _doc(S, "4100 Kommunal fastighetsavgift", "Lag (2007:1398) om kommunal fastighetsavgift, data.riksdagen.se (`se/law/sfs-2007-1398.txt`); Förordning (2007:1023) and (2024:987) om inkomstbasbelopp (`se/law/sfs-2007-1023.txt`, `sfs-2024-987.txt`)",
             ["3 § a): \"6 000 kronor per sådant småhus, dock högst 0,75 procent av byggnadsvärdet och markvärdet\"; \"För år 2009 och senare kalenderår uppgår fastighetsavgiften per småhus ... till fastighetsavgiften för år 2008 ökad eller minskad med ett belopp motsvarande inkomstbasbeloppets förändring mellan år 2008 och det aktuella kalenderåret uttryckt i procent med två decimaler. Avgiften uttrycks i hela krontal så att öretal faller bort.\"",
              "SFS 2007:1023: inkomstbasbeloppet \"48 000 kronor för år 2008\"; SFS 2024:987 1 §: \"80 600 kronor för år 2025\""])


def _no(S):
    if S["cc"] != "NO":
        return
    if _has(S, "4200"):
        p6_wealth(S, "formue", "Formuesskatt (stat 0,475/0,575 %, kommune 0,525 %)", [(0, 1000), (20700000 - 1760000, 1100)], 1760000,
                  "Stortingets skattevedtak 2025 §§ 2-1, 2-3 (allowance 1 760 000 kr, 3 520 000 kr for spouses taxed jointly; state 0,475 % to 20 700 000 kr, 0,575 % above; municipal at most 0,525 %, the maximum applying unless lower is resolved)",
                  "Stortingsvedtak 13.12.2024 for inntektsåret 2025 (lovdata STV/forskrift/2024-12-13-3203)", "A",
                  "Stortingsvedtak om skatt av inntekt og formue mv. for inntektsåret 2025, lovdata (`no/law/stv_skatt2025.txt`)",
                  ["§ 2-1: \"Personlig skattyter og dødsbo svarer formuesskatt til staten av den delen av skattyterens samlede antatte formue som overstiger 1 760 000 kroner. Satsen skal være 0,475 pst. for formue inntil 20 700 000 kroner og 0,575 pst. for den delen av formuen som overstiger 20 700 000 kroner.\"; spouses taxed jointly: \"3 520 000 kroner\" and \"41 400 000 kroner\"",
                   "§ 2-3: \"Personlig skattyter og dødsbo skal ha et fradrag i formuen på 1 760 000 kroner ... Satsen for formuesskatt til kommunene må ikke være høyere enn 0,525 pst. Maksimumssatsen gjelder når ikke lavere sats er vedtatt av kommunen.\"",
                   "state + municipal: 1,0 % of the net wealth above the allowance, 1,1 % above 20 700 000 kr (the state band limit is on the whole wealth: 20 700 000 - 1 760 000 above the allowance)"],
                  marriedAllowance=3520000,
                  uns=[("!g.assets.isEmpty", "asset values: the input's assessed value is taken as the formuesverdi; the skatteloven ch. 4 valuation discounts (home 25 %/70 %, shares and operating assets 80 %) are not applied to market values"),
                       ("g.household.married", "spouses: the joint allowance 3 520 000 kr is applied, but the state band limit stays at 20 700 000 kr (41 400 000 kr jointly in § 2-1)")])


def _fi(S):
    if S["cc"] != "FI":
        return
    if _has(S, "4300"):
        src = _pw("FI")
        p6_inherit(S, "perint", "Perintövero (veroluokka I)", [(0, [(0, 0), (19999, 1000000), (20000, 700), (40000, 1000), (60000, 1300), (200000, 1600), (1000000, 1900)])],
                   {}, "Perintö- ja lahjaverolaki 14 § (veroluokka I scale)", _pwd("FI"), "B", src,
                   ["inheritance tax class I (spouse, parents, lineal descendants, spouse's descendants): EUR 20 000-40 000: 100 + 7 %; 40 000-60 000: 1 500 + 10 %; 60 000-200 000: 3 500 + 13 %; 200 000-1 000 000: 21 700 + 16 %; above: 149 700 + 19 %",
                    "the EUR 100 at 20 000 is written as a 1-euro band at 1 000 000 bp (19 999 to 20 000), so a value of exactly 20 000 bears 100 instead of 0"],
                   only="inheritance",
                   uns=[("g.transfers.any (fun t => t.kind == .inheritance && !(t.relation == .spouse || t.relation == .child || t.relation == .grandchild || t.relation == .parent))", "veroluokka II (other relatives and unrelated persons: higher scale) is not in the B source: the class I scale is applied (understates)"),
                        ("!g.transfers.isEmpty", "the spouse's EUR 90 000 and minor child's EUR 60 000 deductions (PerVL 26 §) are not in the B source")])
        p6_inherit(S, "lahja", "Lahjavero (veroluokka I)", [(0, [(0, 0), (4999, 1000000), (5000, 800), (25000, 1000), (55000, 1200), (200000, 1500), (1000000, 1700)])],
                   {}, "Perintö- ja lahjaverolaki 14 § (veroluokka I gift scale)", _pwd("FI"), "B", src,
                   ["gift tax class I: EUR 5 000-25 000: 100 + 8 %; to 55 000: 10 %; to 200 000: 12 %; to 1 000 000: 15 %; above: 17 %; same-donor gifts aggregated over 3 years"],
                   only="gift", lookback=3, oecdDrop=False,
                   uns=[("g.transfers.any (fun t => t.kind == .gift && !(t.relation == .spouse || t.relation == .child || t.relation == .grandchild || t.relation == .parent))", "gift tax class II not in the B source: the class I scale is applied (understates)")])


def _dk(S):
    if S["cc"] != "DK":
        return
    if _has(S, "4300"):
        p6_inherit(S, "bo", "Boafgift og tillægsboafgift", [(346000, [(0, 1500)]), (346000, [(0, 3625)])],
                   dict(child=0, grandchild=0, parent=0), "boafgiftsloven: boafgift 15 %, tillægsboafgift 25 % of the remainder for other heirs; bundfradrag DKK 346 000 (2025)",
                   _pwd("DK"), "B", _pw("DK"),
                   ["boafgift 15 %: children and their descendants, stepchildren, parents, 2-year cohabitant; spouse exempt",
                    "tillægsboafgift 25 % on the remainder for other heirs: 15 % + 25 % x 85 % = 36,25 %",
                    "bundfradrag DKK 346 000 (2025, per estate)"],
                   exempt=("spouse",), only="inheritance",
                   uns=[("!g.transfers.isEmpty", "the DKK 346 000 bundfradrag belongs to the estate; it is applied per recipient here; charities and the cohabitant rule not modelled"),
                        ("g.transfers.any (·.kind == .gift)", "gaveafgift (gifts) not modelled")])


def _is(S):
    if S["cc"] != "IS":
        return
    if _has(S, "4300"):
        p6_inherit(S, "erfd", "Erfðafjárskattur", [(6789790, [(0, 1000)])], {},
                   "lög nr. 14/2004 um erfðafjárskatt (10 %; first ISK 6 789 790 untaxed; spouse exempt)", _pwd("IS", "pwc_indother_live"), "B",
                   _pw("IS", name="pwc_indother_live"),
                   ["erfðafjárskattur 10 % of net value; allowance ISK 6 789 790; surviving spouse / cohabitant exempt",
                    "advance inheritance: 10 %, no allowance (not modelled)"],
                   exempt=("spouse",), only="inheritance",
                   uns=[("!g.transfers.isEmpty", "the allowance belongs to the estate; applied per recipient here; advance inheritances (10 % without allowance) not separated from gifts"),
                        ("g.transfers.any (·.kind == .gift)", "gifts are income (1100) or advance inheritance: not modelled here")])
    if _has(S, "4400"):
        p6_transfer(S, "stimp", "Stimpilgjald (real estate)", [(0, 80)],
                    "lög nr. 138/2013 um stimpilgjald (0,8 % for individuals; 0,4 % for a first home)", _pwd("IS", "pwc_indother_live"), "B",
                    _pw("IS", name="pwc_indother_live"),
                    ["stimpilgjald on real estate deeds: individuals 0,8 % of registered value; first home 0,4 %"],
                    firstCap=10 ** 12, firstBands=[(0, 40)],
                    uns=[("!g.purchases.isEmpty", "the base is the registered value (fasteignamat): the price stands in; legal persons pay 1,6 % (not separated)")])


def _al(S):
    if S["cc"] != "AL":
        return
    if _has(S, "4300"):
        p6_inherit(S, "trash", "Tatimi mbi trashëgiminë dhe dhuratat", [(1000000, [(0, 1500)])], {},
                   "Ligji për tatimin mbi të ardhurat (15 %; heirs of the first and second order and siblings exempt)", _pwd("AL"), "B", _pw("AL"),
                   ["inheritance / gift: 15 %, gross (no cost deduction)",
                    "exempt: legal heirs of 1st and 2nd order; siblings",
                    "exempt thresholds: immovables ALL 5 000 000; movables ALL 1 000 000"],
                   exempt=("spouse", "child", "parent", "sibling"),
                   uns=[("!g.transfers.isEmpty", "the ALL 1 000 000 movable-asset threshold is applied to the whole transfer (immovable assets: ALL 5 000 000); grandchildren taken as taxable (the order of heirs is not in the source)")])
    if _has(S, "4100"):
        p6_property(S, "tnd", "Tatimi mbi ndërtesat", [(0, 5)], "Ligji 9632/2006 për sistemin e taksave vendore (buildings: residential 0,05 %, commercial 0,2 % of value)",
                    _pwd("AL"), "B", _pw("AL"),
                    ["building tax a year: residential 0,05 %, commercial 0,2 % of value; unfinished construction 30 % of the rate",
                     "land: per ha / m2 by district (not modelled)"],
                    kinds=("home", "realEstate"), level="local", sample=10000000,
                    uns=[("g.assets.any (fun a => a.kind == .realEstate)", "realEstate taken as residential (0,05 %); commercial buildings bear 0,2 %; land per m2 not modelled")])


def _lt(S):
    if S["cc"] != "LT":
        return
    if _has(S, "4300"):
        p6_inherit(S, "pav", "Paveldimo turto mokestis", [dict(allowance=0, slab=[(3000, 0), (150000, 500)], top=1000)], {},
                   "Paveldimo turto mokesčio įstatymas (5 % to EUR 150 000, 10 % above; close relatives exempt; up to EUR 3 000 untaxed)",
                   _pwd("LT", "pwc_indother_live"), "B", _pw("LT", name="pwc_indother_live"),
                   ["exempt: spouse, children, parents, guardians, grandparents, grandchildren, siblings; taxable value ≤ EUR 3 000",
                    "rate 5 % (value ≤ EUR 150 000), 10 % (above; taken as a whole-amount slab)", "gift tax: none (gifts are PIT income, 1100)"],
                   exempt=("spouse", "child", "parent", "grandchild", "sibling"), only="inheritance",
                   uns=[("!g.transfers.isEmpty", "live page reviewed 2026: the 2025 rules are taken as the same; the slab reading (whole value at 10 % above EUR 150 000) is the B source's wording, the Act was not read")])


def _x44(S):
    """B transfer duties from the PwC corporate other-taxes captures (2025)."""
    cc = S["cc"]
    rows = {
     "SI": ("prom", "Davek na promet nepremičnin", [(0, 200)], "Zakon o davku na promet nepremičnin (ZDPN-2) (2 %; not where VAT is charged)",
            ["real estate transfer tax 2 %: transfers and finance leases of real estate; not where VAT is charged"], {}),
     "GR": ("fmа", "Φόρος μεταβίβασης ακινήτων (ΦΜΑ)", [(0, 309)], "ν. 1587/1950 ΦΜΑ 3 % + municipal surcharge 3 % of it = 3,09 %",
            ["ΦΜΑ 3 % of the objective value (transfers outside VAT) + municipal surcharge 3 % of the tax = 3,09 %"], {}),
     "NO": ("dok", "Dokumentavgift", [(0, 250)], "Stortingets vedtak om dokumentavgift (2,5 % of market value)",
            ["dokumentavgift 2,5 % of market value on registration of a real estate title transfer"], {}),
     "BE": ("enr", "Droits d'enregistrement (Région de Bruxelles-Capitale)", [(0, 1250)], "Code des droits d'enregistrement (Bruxelles) art. 44 (12,5 %)",
            ["droits d'enregistrement: Brussels / Wallonia 12,5 %, Flanders 12 %; base max(price, market value); real estate outside VAT; family home Flanders 2 %, Wallonia 3 % (from 1.1.2025)"], {}),
     "FR": ("dmto", "Droits de mutation à titre onéreux (immeubles)", [(0, 580)], "CGI art. 683, 1594 D, 1584, 1595 bis (5,80 % in all)",
            ["DMTO 5,80 % on sales of land and buildings (buyer); up to 6,3 % for acts from 1.4.2025 by départemental decision"], {}),
     "UA": ("mito", "Державне мито (real estate sales)", [(0, 100)], "Декрет КМУ про державне мито (1 % of the sale price of real estate)",
            ["державне мито 1 %: real estate sales, commodity-exchange operations"], {}),
     "HR": ("pn", "Porez na promet nekretnina", [(0, 300)], "Zakon o porezu na promet nekretnina (3 %; not where VAT is charged)",
            ["porez na promet nekretnina 3 %: transfers of real estate outside VAT (sale, exchange, gift, inheritance, liquidation); exemptions exist"], {}),
    }
    if cc not in rows or not _has(S, "4400"):
        return
    key, name, bands, st, facts, kw = rows[cc]
    page, nm = ("Individual - Other taxes", "pwc_indother_wb2025") if cc == "HR" else ("Corporate - Other taxes", "pwc_corpother_wb2025")
    uns = {"SI": "new buildings sold under VAT (first supply) are outside the tax (not separated)",
           "GR": "the base is the objective value where higher (the price stands in); new buildings under VAT not separated",
           "NO": "share transfers and cooperative flats are outside (not separated)",
           "BE": "Brussels taken as the reference region; the abattement for a sole home and Flemish/Walloon rates not modelled; base = higher of price and market value (the price stands in)",
           "FR": "Paris: the département's rate rose for acts from 1 April 2025 (up to 6,3 % in all, not modelled); new buildings under TVA (0,715 %) and first-time-buyer exemptions not separated; notary fees not taxes",
           "UA": "the 1 % levy to the Pension Fund on real estate purchases (not in the source) not modelled",
           "HR": "exemptions (first home of citizens, close-family transfers) not modelled; inheritances and gifts of real estate also bear the tax (not modelled: purchases only)"}[cc]
    p6_transfer(S, key.replace("а", "a"), name, bands, st, _pwd(cc, nm, page), "B", _pw(cc, page, nm), facts,
                uns=[("!g.purchases.isEmpty", uns)])


def _lv(S):
    if S["cc"] != "LV":
        return
    if _has(S, "4400"):
        p6_transfer(S, "nod", "Valsts nodeva (zemesgrāmata)", [(0, 200)], "Cabinet regulation on state fees for the Land Register (2 % of the deal or cadastral value, at most EUR 50 000)",
                    _pwd("LV", "pwc_corpother_wb2025", "Corporate - Other taxes"), "B", _pw("LV", "Corporate - Other taxes", "pwc_corpother_wb2025"),
                    ["Land Register state fee 2 % of max(deal value, cadastral value), cap EUR 50 000"],
                    maximum=50000, uns=[("!g.purchases.isEmpty", "the base is the higher of the deal and cadastral value (the price stands in); reduced fees for family transfers not modelled")])


def _has(S, o):
    return any(str(t.get("oecd")) == o and t.get("grade") == "C" for t in S["taxes"])


def p6_rows(S):
    cc = S["cc"]
    _absent_rows(S, _ABS, "Individual - Other taxes", "pwc_indother_wb2025")
    _absent_rows(S, _ABS_CORP, "Corporate - Other taxes", "pwc_corpother_wb2025")
    _absent_rows(S, _ABS_CORPF, "Corporate - Other taxes", "pwc_other_wb2025")
    for f in (_it, _pl, _hu, _se, _no, _fi, _dk, _is, _al, _lt, _x44, _lv):
        f(S)
    for o, tab in (("4100", _NOTE41), ("4400", _NOTE44)):
        if cc in tab and _has(S, o):
            old = [t for t in S["taxes"] if str(t.get("oecd")) == o and t.get("grade") == "C"][0]
            p6_note(S, o, old["tax"], old.get("statute", ""), tab[cc], "pass 6 note (PwC WWTS 2025 captures on disk)")


# ---------------------------------------------------------------- 1200 withholding rows (pass 6 carry-over)
_WHT = {
 "BG": ([("dividend", 500), ("interest", 1000), ("royalty", 1000)], "ЗКПО чл. 194-195, 200 (dividends 5 %, interest and royalties 10 %)",
        ["non-treaty WHT: dividends / liquidation proceeds 5 %; interest 10 %; royalties 10 % (also technical services, rents, franchising, management fees)"]),
 "RS": ([("dividend", 2000), ("interest", 2000), ("royalty", 2000)], "Zakon o porezu na dobit pravnih lica čl. 40 (20 %; 25 % to listed tax havens)",
        ["non-treaty WHT 20 %: dividends, interest, royalties, some services, rents; 25 %: interest, royalties to listed tax havens"]),
 "MD": ([("dividend", 600), ("interest", 1200), ("royalty", 1200)], "Codul fiscal art. 71, 72, 73 (dividends 6 %; interest and royalties 12 %)",
        ["non-treaty WHT: dividends 6 % (15 % in some cases, not modelled); interest 12 %; royalties 12 %"]),
 "HR": ([("dividend", 1000), ("interest", 1500), ("royalty", 1500)], "Zakon o porezu na dobit čl. 31 (dividends 10 %, interest and royalties 15 %)",
        ["non-treaty WHT to foreign legal entities: dividends 10 %; interest 15 %; royalties / IP fees 15 %"]),
 "LT": ([("dividend", 1600), ("interest", 1000), ("royalty", 1000)], "Pelno mokesčio įstatymas 37 str. (distributed profits 16 % from 1.1.2025; interest and royalties 10 %)",
        ["WHT on a foreign entity without PE: interest 10 %; dividends 16 % (from 1.1.2025); royalties 10 %; 0 % under domestic exemptions (participation, EU interest)"]),
 "SI": ([("dividend", 1500), ("interest", 1500), ("royalty", 1500)], "ZDDPO-2 70. člen (15 %)",
        ["non-treaty WHT 15 %: dividends, interest, royalties; EU directive relief (parent-subsidiary, interest-royalty)"]),
}
_WHT_ABS = {
 "HU": ("Tao. (no withholding on payments to non-individuals)", "domestic WHT on dividends / interest / royalties to non-individuals: none"),
 "MT": ("Income Tax Act Cap. 123 (no withholding on dividends; interest and royalties to non-residents exempt subject to conditions)", "non-treaty WHT to non-resident companies: 0 % on dividends, interest, royalties (interest / royalties exempt unless connected with a Maltese PE)"),
}


def p6_wht_rows(S):
    cc = S["cc"]
    if S["fam"] != "Corporate" or not any(t.get("grade") == "C" and "ithholding" in t.get("tax", "") for t in S["taxes"]):
        return
    nm, page = "pwc_wht_wb2025", "Corporate - Withholding taxes"
    if cc in _WHT:
        rules, st, facts = _WHT[cc]
        p6_wht(S, rules, st, _pwd(cc, nm, page), "B", _pw(cc, page, nm), facts,
               uns=[("g.entity == .company", "EU parent-subsidiary / interest-royalty exemptions and the higher tax-haven rates not modelled")])
    elif cc in _WHT_ABS:
        st, why = _WHT_ABS[cc]
        p6_wht_absent(S, st + "; " + _pw(cc, page, nm), why, _pwd(cc, nm, page))


# ---------------------------------------------------------------- 1100 (P3) gains on disposals, B (PwC Individual - Income determination, 2025)
_GAINS = {
 "SE": ("Kapitalvinstskatt (inkomst av kapital)", "Inkomstskattelagen 41-48 kap., 65 kap. 7 § (30 %; private real property 22/30 of the gain = 22 %)",
        dict(bands=[(0, 3000)]), dict(bands=[(0, 2200)]),
        ["shares / other investments: capital income 30 %", "private real property, tenant-owner flats: 22 % effective; deferral on a replacement home (not modelled)"],
        [("g.disposals.any (·.kind.isRealEstate)", "the deferral (uppskov) on buying a replacement home is not applied; losses on real property count 50 %/70 % (not modelled)")]),
 "FI": ("Luovutusvoittovero (pääomatulo)", "Tuloverolaki 45-50 § (capital income 30 % to EUR 30 000, 34 % above; home used two years exempt)",
        dict(bands=[(0, 3000), (30000, 3400)]), dict(bands=[(0, 3000), (30000, 3400)], mainHome=True),
        ["capital income 30 % to EUR 30 000, 34 % above", "permanent family home used ≥ 2 years: exempt", "de minimis: total sale prices in the year ≤ EUR 1 000 exempt"],
        [("!g.disposals.isEmpty", "the 30 000 band is shared with other capital income (dividends, interest) in the 1.x model: applied to the disposals alone; the EUR 1 000 de-minimis and the deemed acquisition cost (20 %/40 %) not applied; securities and real estate gains each run through the scale separately")]),
 "NO": ("Gevinst på aksjer (oppjustert 1,72 x 22 %)", "Skatteloven § 10-31 (oppjusteringsfaktor 1,72) and § 15-1 (22 %): 37,84 % on gains on shares",
        dict(bands=[(0, 3784)]), None,
        ["shares: gain x 1,72 x 22 % = 37,84 % effective; ordinary capital income 22 %"],
        [("g.disposals.any (·.kind.isRealEstate)", "gains on real property (22 %, home exempt after one year of ownership and use) not modelled: the conditions are not in the B source"),
         ("g.disposals.any (·.kind == .bonds)", "bonds are ordinary capital income at 22 %, taken here at the share rate")]),
 "PT": ("Mais-valias mobiliárias (taxa especial)", "CIRS art. 72.º (28 %)",
        dict(bands=[(0, 2800)]), None,
        ["securities: 28 % (50 % of the gain for unlisted micro / small company shares)", "from 2023: net gain on securities held < 365 days aggregated where taxable income ≥ EUR 83 696"],
        [("g.disposals.any (·.kind.isRealEstate)", "real estate gains (50 % added to income at progressive rates; reinvestment relief for the home) not modelled"),
         ("g.disposals.any (fun d => d.heldMonths < 12)", "short-term gains of high earners are aggregated at progressive rates (not modelled)")]),
 "IE": ("Capital gains tax", "Taxes Consolidation Act 1997 s. 28 (33 %), s. 601 (annual exemption EUR 1 270)",
        dict(bands=[(0, 3300)]), None,
        ["CGT 33 % (40 % on some fund and life-policy interests)", "annual exemption EUR 1 270 per individual"],
        [("!g.disposals.isEmpty", "the EUR 1 270 annual exemption is not deducted"),
         ("g.disposals.any (·.kind.isRealEstate)", "land and buildings (33 %, principal private residence relief) not modelled: the relief's conditions are not in the B source")]),
 "HU": ("Árfolyamnyereség adója", "Szja tv. 67. § (15 %)",
        dict(bands=[(0, 1500)]), None,
        ["capital gains 15 %; social contribution tax 13 % may apply (conditions)"],
        [("!g.disposals.isEmpty", "the 13 % social contribution tax (szocho) where the conditions fail is not applied"),
         ("g.disposals.any (·.kind.isRealEstate)", "real estate gains (15 %, reduced by holding years) not modelled: the reductions are not in the B source")]),
 "LT": ("GPM nuo turto pardavimo pajamų", "Gyventojų pajamų mokesčio įstatymas 6 str. (15 % to EUR 253 065 for 2025, 20 % above); 17 str. exemptions",
        dict(bands=[(0, 1500), (253065, 2000)]), dict(bands=[(0, 1500), (253065, 2000)], mainHome=True),
        ["gain = price - acquisition price: 15 % to EUR 253 065 (2025), 20 % above", "exempt: financial-instrument gains ≤ EUR 500 a year; EEA housing with declared residence (conditions)"],
        [("!g.disposals.isEmpty", "the EUR 253 065 band is applied to each class of disposals alone (it is shared with other income); the EUR 500 exemption is not applied; the declared-residence conditions are taken as met for a main home")]),
 "EE": ("Tulumaks kasult vara võõrandamisest", "Tulumaksuseadus § 15 (gains as ordinary income, 22 % in 2025); § 15 (3) personal residence exempt",
        dict(bands=[(0, 2200)]), dict(bands=[(0, 2200)], mainHome=True),
        ["net gains on disposals: ordinary income, 22 % (2025); losses only against gains", "personal residence: exempt"],
        [("!g.disposals.isEmpty", "the basic exemption (in the 1.x PIT) is not shared with the gains; investment-account deferral not modelled")]),

 "BG": ("Данък върху капиталовите печалби", "ЗДДФЛ чл. 33, 48 (10 %)", dict(bands=[(0, 1000)]), None,
        ["capital gains (residents): 10 %, annual"],
        [("g.disposals.any (·.kind.isRealEstate)", "real estate gains (exemptions for one home and two other properties held five years) not modelled"),
         ("g.disposals.any (·.listed)", "gains on shares traded on EU/EEA regulated markets are exempt (not applied)")]),
 "RO": ("Impozit pe câștigul din transferul titlurilor de valoare", "Codul fiscal art. 94-96 (10 % for 2025)", dict(bands=[(0, 1000)]), None,
        ["shares: net gain (price - acquisition price - broker fees) 10 %"],
        [("g.disposals.any (·.kind.isRealEstate)", "the tax on real estate transfers (1 %/3 % of value, Codul fiscal art. 111) is not modelled")]),
 "LV": ("Iedzīvotāju ienākuma nodoklis no kapitāla pieauguma", "likums Par iedzīvotāju ienākuma nodokli 15. pants (25,5 % from 2025)", dict(bands=[(0, 2550)]), None,
        ["capital assets (real estate, shares, fund units, debentures, IP, virtual currency): 25,5 %; deals begun by 31.12.2024: 20 % on notification"],
        [("g.disposals.any (·.kind.isRealEstate)", "real estate gains (25,5 %; the declared-residence home exemption) not modelled: the exemption's conditions are not in the B source")]),
 "GR": ("Φόρος υπεραξίας από μεταβίβαση μετοχών", "ΚΦΕ (ν. 4172/2013) άρθρο 42 (15 %)", dict(bands=[(0, 1500)]), None,
        ["unlisted shares 15 %; listed shares 15 % for holdings ≥ 0,5 % (else exempt, conditions)", "listed-share sales duty 0,2 % of gross proceeds (4400, not modelled)"],
        [("g.disposals.any (fun d => d.listed && d.stakeBp < 50)", "listed shares below a 0,5 % holding are taken as taxed (the exemption's conditions are not modelled)"),
         ("g.disposals.any (·.kind.isRealEstate)", "real estate gains (tax suspended) not modelled")]),
 "IS": ("Fjármagnstekjuskattur af söluhagnaði", "lög nr. 90/2003 um tekjuskatt (fjármagnstekjur 22 %; residential property owned over two years exempt)",
        dict(bands=[(0, 2200)]), dict(bands=[(0, 2200)], hold=24),
        ["private property gains: capital income 22 %", "exempt: residential property owned > 2 years; private movables"],
        [("g.disposals.any (fun d => d.kind == .realEstate || d.kind == .land)", "the two-year exemption is applied to all real estate (it is for residential property only)")]),
 "SI": ("Dohodnina od dobička iz kapitala", "ZDoh-2 97. člen (25 % to 5 years, 20 %, 15 %, 0 % after 15 years)",
        dict(bands=[(0, 2500)], hold=180, steps=[(0, 2500), (60, 2000), (120, 1500), (180, 0)]),
        dict(bands=[(0, 2500)], hold=180, steps=[(0, 2500), (60, 2000), (120, 1500), (180, 0)]),
        ["final tax by holding period: 0-5 years 25 %; 5-10 20 %; 10-15 15 %; > 15 years 0 %"],
        [("g.disposals.any (fun d => d.heldMonths >= 60 && d.heldMonths < 180)", "pass 7: each disposal is taxed at its holding-period rate (25/20/15 %) and losses offset at their own rates; the act's loss rules (ZDoh-2 98. člen) were not read")]),
}


def p6_gain_rows(S):
    cc = S["cc"]
    if cc not in _GAINS or not _has(S, "1100"):
        return
    name, st, sec, re_, facts, uns = _GAINS[cc]
    nm, page = "pwc_indincome_wb2025", "Individual - Income determination"
    p6_gains(S, "cg", name, st, _pwd(cc, nm, page), "B", _pw(cc, page, nm), facts, sec=sec, re=re_, uns=uns)
