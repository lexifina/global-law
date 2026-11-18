"""Shared helper: run the extended Lean model (per-person households) and score outcomes. Money in pounds."""
import os
import json, subprocess
EXE = os.path.expanduser('~/cmp/loop/uk/lean/.lake/build/bin/uktax')

def hh(persons, married=True, children=0, region=None, id='x'):
    h = {"id": id, "year": 2025, "married": married, "children": [{"age": 5}] * children, "persons": persons}
    if region: h["region"] = region
    return h

def run(hs, flags=()):
    inp = '\n'.join(json.dumps(h) for h in hs) + '\n'
    out = subprocess.run([EXE, *flags], input=inp, capture_output=True, text=True, check=True).stdout
    return [json.loads(l) for l in out.splitlines() if l.strip()]

def burden(o):
    """Income tax (s. 23 liability less relief at source paid into the pension) + CGT + employee NI
    - (child benefit - HICBC)."""
    return round(o['incomeTax'] + o['surtaxes'].get('capitalGainsTax', 0) + o['employeeSocial'] - o['benefits'], 2)

def parts(o):
    d = o['detail']
    return dict(it=d['liabilityITA2007s23'], ras=d['reliefAtSource'], cgt=o['surtaxes'].get('capitalGainsTax', 0),
                ni=o['employeeSocial'], cb=d['childBenefit'], hicbc=d['hicbc'], election=d['election'])
