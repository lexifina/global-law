"""lean9, round 9 batch 2: put the batch-2 Lean text (DESIGN9 sections 5, 7, 6, 8) into a lean-proofs tree layout.
    python assemble_batch2.py <tree root> <pieces dir>
Run once on a tree that has round 9's section 4 and nothing of batch 2 (it refuses otherwise)."""
import os
import sys

ROOT, PIECES = sys.argv[1], sys.argv[2]
C2 = os.path.join(ROOT, "LegalProofs", "CaseLaw2")


def piece(n):
    return open(os.path.join(PIECES, n), encoding="utf-8").read()


def edit(rel, pairs):
    p = os.path.join(C2, rel)
    s = open(p, encoding="utf-8", newline="").read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:100])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("edited", rel)


edit("Certificate.lean", [
    ("""  | partZone
  deriving Repr, DecidableEq, Inhabited""", """  | partZone
  /-- round 9 batch 2 (`round9/DESIGN9.md` §5, D9-7): a far antecedent joined quote (`joinedFar` claim) beyond
  `joinedFarMax`; no usable window of the row's text covers the gap; an index key of another node begins in the gap -/
  | joinedFarGap | joinedFarWindow | joinedFarKey
  /-- round 9 batch 2 (§7): an `implicitReject` claim on a kind that is not soft -/
  | implicitBadKind
  deriving Repr, DecidableEq, Inhabited"""),
    ("\nend CaseLaw2.Cert", "\n" + piece("cert_b2.lean") + "\nend CaseLaw2.Cert"),
])
s = open(os.path.join(C2, "Certificate.lean"), encoding="utf-8").read()
assert s.rstrip().endswith("end CaseLaw2.Cert") and s.count("end CaseLaw2.Cert") == 1

edit("Spec/AuthorityThms.lean", [("""\nend CaseLaw2.Spec""", "\n" + piece("nj_thm.lean") + "\nend CaseLaw2.Spec")])
edit("Examples.lean", [("""\nend CaseLaw2.Examples""", "\n" + piece("ex_b2.lean") + piece("nj_ex.lean") +
                        "\nend CaseLaw2.Examples")])

mut = piece("mut_b2.lean")
# properties9b: the far / implicit five, then New Jersey (M72's, M73's) and section 8's
i = mut.index("/-- Round 9 batch 2: one property per new rule")
mut_defs, mut_props = mut[:i], mut[i:]
m74 = mut_props[mut_props.index("\n/-- M74"):]
mut_props = mut_props[:mut_props.index("\n/-- M74")]
nj = piece("nj_mut.lean")
nj_defs = nj[:nj.index("/-- Round 9 §6 properties. -/")]
mut_props = mut_props.rstrip()
assert mut_props.endswith("]")
mut_props = mut_props[:-1].rstrip() + """,
  ("adopted_lowerTier_noPower", fun i =>
    -- (the adopted power is never granted below the target's tier; M15 "no power check" grants every refused power
    -- under its own rule id and is M15's, not this property's)
    i.canChange njLx appDiv1977 ea1924 none != some (true, .sameCourtSoft) &&
      (i.canChange njLx sup1954 oldSup1924 none).map (·.1) == some true),
  ("adoptedSameTier_power (New Jersey successors)", fun i =>
    (i.canChange njL appDiv1962 oldSup1948 none).map (·.1) == some true &&
      (i.canChange njL chanDiv1949 chancery1937 none).map (·.1) == some true),
  ("anchorWide9_no_claim", fun i =>
    i.checkHistory8J jgIn (some jgAnc) none { anchorWide := true } == .ok &&
      !(i.checkHistory8J jgIn (some jgAnc) none {}).admitted)
]
"""
edit("Mutants.lean", [
    ("""  partZone : List Cert.Zone → Cert.Input → List Cert.Joined → Cert.Result → Cert.Result :=
    fun raw c js r => Cert.zoneThen (Cert.nodeZones raw) c js r
""", """  partZone : List Cert.Zone → Cert.Input → List Cert.Joined → Cert.Result → Cert.Result :=
    fun raw c js r => Cert.zoneThen (Cert.nodeZones raw) c js r
  /-- round 9 batch 2: the treatment step under a `joinedFar` claim (§5) and under an `implicitReject` claim (§7); the
  round-8 history step with the judge-form anchor cues (§8) -/
  checkTreatmentF : Bool → List Nat → Cert.Input → Bool → Cert.TClaim → List Cert.Joined → Cert.Result :=
    Cert.checkTreatmentF
  checkTreatmentI : Bool → Cert.Input → Bool → Cert.TClaim → List Cert.Joined → Cert.Result := Cert.checkTreatmentI
  checkHistory8J : Cert.Input → Option Cert.Anchor → Option Cert.Bridge → Cert.HClaims → Cert.Result :=
    Cert.checkHistory8J
"""),
    ("""def mutants : List (String × Impl) := [""", mut_defs + nj_defs + m74.strip() + "\n\n" + mut_props + """
def mutants : List (String × Impl) := ["""),
    ("""  ("M66 zones of an overlapping node kept", { partZone := m66 })
]""", """  ("M66 zones of an overlapping node kept", { partZone := m66 }),
  ("M67 far antecedent past another citation", { checkTreatmentF := m67 }),
  ("M68 far antecedent at any distance", { checkTreatmentF := m68 }),
  ("M69 far antecedent without an anaphor", { checkTreatmentF := m69 }),
  ("M70 implicitReject on an overruled row", { checkTreatmentI := m70 }),
  ("M71 implicit cues without the claim", { checkTreatmentI := m71 }),
  ("M72 adoption at any tier (mutAdoptAnyTier)", { canChange := m72 }),
  ("M73 adoption gives no power (mutNoAdoptPower)", { canChange := m73 }),
  ("M74 judge-form anchor cues without the claim", { checkHistory8J := m74 })
]"""),
    ("""  properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9
""", """  properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9 ++ properties9b
"""),
    ("""#guard (properties.length, properties5.length, properties6.length, properties7.length, properties8.length,
  properties9.length, mutants.length) == (27, 8, 6, 13, 10, 3, 66)""", """-- round 9 batch 2: the eight new mutants and the eight new properties form a diagonal; no new mutant is caught by an
-- earlier property and no earlier mutant by a new property
#guard (List.range 8).all fun i => (List.range 8).all fun j =>
  match (mutants.drop 66)[i]?, properties9b[j]? with
  | some (_, m), some (_, p) => (!p m) == (i == j)
  | _, _ => false
#guard (mutants.drop 66).all fun (_, m) =>
  (properties ++ properties5 ++ properties6 ++ properties7 ++ properties8 ++ properties9).all fun (_, p) => p m
#guard (mutants.take 66).all fun (_, m) => properties9b.all fun (_, p) => p m
#guard (properties.length, properties5.length, properties6.length, properties7.length, properties8.length,
  properties9.length, properties9b.length, mutants.length) == (27, 8, 6, 13, 10, 3, 8, 74)"""),
])
# the round-9 (section 4) guards also take every later mutant: `(mutants.drop 63).all` over the earlier properties
# holds for the batch-2 mutants too, and the section-4 diagonal reads the first three of `mutants.drop 63`
edit("Run.lean", [("""      let res (L : Lookups) := Cert.checkHistory9 zs { certInput (.hist kind) r.cert shas cx r.target ordered""",
                   """      let res (L : Lookups) := Cert.checkHistory9J zs { certInput (.hist kind) r.cert shas cx r.target ordered""")])
print("assembled")
