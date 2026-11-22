S = dict(cc="AF", family_name="5112 business receipts tax",
doc=r'''# Afghanistan 2025: business receipts tax (5112); no VAT; excise not modelled

Source: Income Tax Law 2009, MoF consolidated English version "Version: December 2016" (`cmp20/world/B11-south-asia/af/law/
itl2009_consol2016.pdf`, text `itl.txt`; sha256 in `law/SOURCES.tsv`). Whether every 2016 provision was applied unchanged in
2025 could not be checked (grade B).
* **art. 64 (1)**: "A legal person who provides goods or services in exchange for consideration shall be required to pay
  business receipts tax"; (2) natural persons from "Afs. 750,000 or more per quarter"; (3) imports 4 % on cost incl. duty.
* **art. 66**: (1) "Four percent of income received (before any deductions)" (Presidential Decree No. 149 of 13.02.2016);
  (3) "Five percent … from hotels or guest houses and restaurants" above the threshold; (5) "Ten percent … from
  telecommunication, hotels and restaurants providing superior services".
* **art. 65**: exempt 1- interest. In the basket the tax is taken inside the final seller's price (rate × price);
  restaurants and hotels at 5 %, communication at 10 %, interest-bearing financial services exempt; its cascade through
  earlier stages is not modelled.''',
extra_lean=r'''def brtBp (g : Good) : Int :=
  match g with
  | .restaurants | .hotels => 500
  | .communication => 1000
  | .financial | .rent | .health | .education => 0
  | _ => 400

def basketBrt (xs : List Spend) : List Charge :=
  (xs.filter fun s => brtBp s.good > 0).map fun s =>
    charge .salesTax "Business receipts tax" s.amount id (fun x => divR .down (pos x * brtBp s.good) BP) (event := s.good.name)
      (bearer := .consumer) (statute := s!"Income Tax Law 2009 art. 64, 66 ({brtBp s.good / 100} % of receipts)")

def businessBrt (g : CanonGlobal) : List Charge :=
  if g.entity == .company && g.company.turnover > 0 then
    [charge .salesTax "Business receipts tax" g.company.turnover id (fun x => divR .down (pos x * 400) BP) (event := "receipts")
      (bearer := .consumer) (statute := "Income Tax Law 2009 art. 64 (1), 66 (1) (4 %)")]
  else []''',
extra_run=["basketBrt g.consumption","businessBrt g"], extra_covers=[".salesTax"],
absent=[["vat","no VAT in force: the business receipts tax of Income Tax Law 2009 ch. 10 (arts. 64-67) is the general tax on sales (a VAT law was never brought into force)"]],
notes=["AF 5112: Income Tax Law 2009 ch. 10, consolidated version December 2016"],
unsupported=[["basket","BRT taken at the final seller only (no cascade); rent, health and education taken as not supplied by BRT payers"],
 [["cigarettes","beer","wine","spirits","petrol","diesel"],"customs and fixed taxes on imports, excise-like fees: not modelled"]],
guards=["(basketBrt [{ good := .clothing, amount := 1000 }]).map (·.due) == [40]","(basketBrt [{ good := .communication, amount := 1000 }]).map (·.due) == [100]",
  "(basketBrt [{ good := .financial, amount := 1000 }]).length == 0"],
taxes=[{"oecd":"5112","tax":"Business receipts tax","statute":"Income Tax Law 2009 arts. 64, 65, 66 (as amended by Presidential Decree No. 149 of 2016)","dated":"MoF consolidation December 2016 (2025 application not confirmed)","grade":"B","kernel_parts":["charge"],"unsupported":["cascade through the supply chain","small natural-person threshold per quarter","import BRT at customs"]},
 {"oecd":"5111","tax":"VAT (not levied)","statute":"Income Tax Law 2009 ch. 10 (BRT instead)","grade":"B","kernel_parts":["Absent"],"unsupported":["the absence of a VAT law in force is inferred from the BRT chapter; no statute says it expressly"]},
 {"oecd":"5121","tax":"Excise","statute":"none found","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["no excise statute reached; customs tariff fixed taxes not read"]}])


# --- R3 session 11 (2026-11-21): year-in-force audit: downgraded to C (old content kept in S['_pre11']) ---
_N11 = "session 11 year-in-force audit: the only text is the MoF consolidation 'Version: December 2016' of the Income Tax Law 2009; no 2025 version, amendment list or 2025 official source reached (the 2025 application of the 2016 text is not established): grade C"
S['_pre11'] = {k: S.get(k) for k in ('sched', 'wht', 'guards', 'extra_lean', 'extra_run', 'extra_covers', 'taxes', 'unsupported')}
for _k in ['extra_lean', 'extra_run', 'extra_covers']:
    S[_k] = [] if _k != 'extra_lean' else ''
S['guards'] = [g for g in S.get('guards', []) if g.startswith('absent')]
S['unsupported'] = [u for u in S.get('unsupported', []) if not True] + [['*', _N11]]
for _t in S['taxes']:
    if _t['oecd'] in ['5112']:
        _t.update(grade='C', dated='not modelled (' + _N11 + ')', kernel_parts=[], unsupported=[_N11])
