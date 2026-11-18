"""Whole-euro tariff 2025 on x = 0..400 000: Lean vs (a) exact Fractions, (b) GETTSIM's own tariff function,
(c) the statute's formula in binary floating point ("Gleitkommarechnung", BMF Tarifhistorie)."""
import os
import sys, math
from fractions import Fraction as F
import numpy as np
lean = [int(l) for l in open(os.path.expanduser('~/cmp/de/runs/tariff/lean_est.txt'))]
N = len(lean)
def exact(x):
    if x <= 12096: return 0
    if x <= 17443:
        y = F(x - 12096, 10000); return math.floor((F(93230, 100) * y + 1400) * y)
    if x <= 68480:
        z = F(x - 17443, 10000); return math.floor((F(17664, 100) * z + 2397) * z + F(101513, 100))
    if x <= 277825: return math.floor(F(42, 100) * x - F(1091192, 100))
    return math.floor(F(45, 100) * x - F(1924667, 100))
def flt(x):
    if x <= 12096: return 0
    if x <= 17443:
        y = (x - 12096) / 10000; return math.floor((932.30 * y + 1400) * y)
    if x <= 68480:
        z = (x - 17443) / 10000; return math.floor((176.64 * z + 2397) * z + 1015.13)
    if x <= 277825: return math.floor(0.42 * x - 10911.92)
    return math.floor(0.45 * x - 19246.67)
ex = [exact(x) for x in range(N)]
print('Lean == exact Fractions:', sum(1 for a, b in zip(lean, ex) if a == b), '/', N)
fl = [flt(x) for x in range(N)]
bad = [x for x in range(N) if fl[x] != ex[x]]
print('float formula != exact:', len(bad), 'first:', bad[:10], 'zones:', {z: sum(1 for x in bad if (x<=17443 and z==2) or (17443<x<=68480 and z==3) or (68480<x<=277825 and z==4) or (x>277825 and z==5)) for z in (2,3,4,5)})
sys.path.insert(0, '')
import yaml, gettsim
from gettsim.germany.einkommensteuer import einkommensteuer as E
from ttsim.tt.piecewise_polynomial import piecewise_polynomial
raw = yaml.safe_load(open(os.path.expanduser('~/cmp/de/venv-gettsim/lib/python3.12/site-packages/gettsim/germany/einkommensteuer/einkommensteuertarif.yaml')))['raw_parameter_einkommensteuertarif']
key = [k for k in raw if str(k).startswith('2025')][0]
fn = getattr(E.parameter_einkommensteuertarif, 'function', None) or getattr(E.parameter_einkommensteuertarif, '__wrapped__', E.parameter_einkommensteuertarif)
params = fn(raw_parameter_einkommensteuertarif=raw[key], xnp=np)
xs = np.arange(N, dtype=float)
g = np.floor(piecewise_polynomial(x=xs, parameters=params, xnp=np)).astype(int)
gd = [x for x in range(N) if g[x] != ex[x]]
from collections import Counter
print('GETTSIM tariff != exact:', len(gd), 'by sign:', Counter(int(np.sign(g[x]-ex[x])) for x in gd), 'zones:',
      Counter(2 if x<=17443 else 3 if x<=68480 else 4 if x<=277825 else 5 for x in gd))
print('examples:', [(x, ex[x], int(g[x])) for x in gd[:8]])
open(os.path.expanduser('~/cmp/de/runs/tariff/gettsim_diff.txt'),'w').write('\n'.join(f'{x} {ex[x]} {int(g[x])}' for x in gd))
open(os.path.expanduser('~/cmp/de/runs/tariff/float_diff.txt'),'w').write('\n'.join(f'{x} {ex[x]} {fl[x]}' for x in bad))
