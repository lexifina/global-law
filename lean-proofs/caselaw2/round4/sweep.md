# Round 4 item 3: sweep residue (fork `sweep`, 12 Nov 2026, 23:16-23:22)

## State
- `r3_drt2` (seeds 62000-62499): 3 universes (62003, 62350, 62391), 10 conflict keys only in the reference.
- The universes were still in the WSL mirror (`~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/difftest/r3_drt2/r<seed>`).
  Copied to `work/round4/sweep/wsl_r<seed>/` (data, edges, lean, ref, diff.tsv). Debug scripts: `work/round4/sweep/dbg.py`, `dbg2.py`.
- No Lean or WSL build was run. No file of either engine was edited.

## Cause (same shape in all three)
Two good-law candidates on `tx.a` at a court outside the Texas line (62003: 2d Cir. 102 and D. Vt. 202; 62350: 1st
Cir. 101 and D. Me. 201; 62391: SCOTUS 2906), both binding by E1:
- A: a Texas court of appeals decision (703/704) promoted by an admitted "writ refused" row (S-TX-3);
- B: a Texas Commission of Appeals decision (court 2948, epoch 1918-1945, ceased) held by the Supreme Court of
  Texas (701) by binding adoption.
ROUND3's note "no epoch on asOf and none before" is not right: 2948 has a last epoch, so R3-80 applies. As it last
sat, the Commission is bound by A (H1 through the promotion; reference `binding`). B binds A's court (H1 through the
adopter). The adopter 701 is not in the destination's line, so it is not asked. A and B bind each other: neither is
displaced, on either side (the two `binds` are the same code shape).
The difference is after displacement. Lean's `resolve` keeps the highest precedence first. `candFor`
(`Exec/Verdicts.lean`) gives B precedence 3 (adopted: the adopter's tier) and A precedence 2: it reads the tier from
the unpromoted source epoch, although `forceOn` gave A its force as a promoted (last-resort) source. So Lean drops A
and reports no conflict. The reference has no precedence step and reports `no,yes`.

## Verdict: Lean is wrong
Doctrine (`research/doctrine.md` line 104, S-TX-3): a writ-refused decision has the precedential value of a Supreme
Court of Texas opinion. An adopted Commission opinion is also the Supreme Court's (H4). At a federal court both are
the state's highest court speaking (E1), with opposite answers; the model has no later-in-time rule among them, so
both answers are permissible. Lean's precedence is inconsistent with its own force (`sourceEpoch` promotes the tier,
`candFor` does not). The reference is right and is unchanged.

## Proposed Lean change (not applied; coordinator owns Lean)
File `LegalProofs/CaseLaw2/Exec/Verdicts.lean`, `candFor`:

old:
    let prec := if path.contains .adopted then max (tierPrec S) adoptPrec else tierPrec S
new:
    -- S-TX-3 (round 4, sweep 62003/62350/62391): a promoted decision ranks as the court of last resort's, as its
    -- force already does (`sourceEpoch`)
    let S' := if path.contains .TXpromoted then { S with tier := .last } else S
    let prec := if path.contains .adopted then max (tierPrec S') adoptPrec else tierPrec S'

`force`/`forceDiv` put `RuleId.TXpromoted` in the path exactly when `promoted` is true. No theorem statement names
`candFor`; one `Examples.lean` use (line 310, no promotion) is unaffected.

## Verification done / not done
- Reference re-run on regenerated copies (`work/round4/sweep/r<seed>/ref0`): the 10 keys reproduce
  (`tx.a 102/-, 202/-, 202/1, 202/2`; `tx.a 101/-, 101/1, 201/-, 201/1, 201/2`; `tx.a 2906/-`).
- Forces checked with `dbg2.py` (62003): A -> 2948 binding, A -> 701 persuasiveStrong, B -> 703/704 binding.
- Reasoned, not run: where a higher candidate displaces a promoted one (a real Supreme Court of Texas or CCA
  decision: binds one way), displacement happens before `resolve` on both sides, so the precedence change has no
  effect there. Promoted vs promoted was already 2 vs 2.
- Not verified: the Lean change itself (needs the WSL build, the 3 universes, the regression set and the sweep).
  Suggest adding the 3 universes to `fixtures/regress/` (`r4-promoted-62003`, `-62350`, `-62391`) from
  `work/round4/sweep/wsl_r<seed>/{data,edges}`.
- DEVIATIONS text: "82. Conflict precedence of a promoted Texas decision: `candFor` ranks a writ-refused decision as
  the court of last resort's (S-TX-3), as `force` does. Before, it ranked as an intermediate court's and lost to an
  adopted Commission opinion at courts outside the Texas line. Lean changed; reference unchanged."

## Final sweep `r4_drt` (seeds 63000-63499): universe 63322 (fork, 23:29-23:31)

- 3 conflict keys only in the reference: `ca.a` at 703/1, 705/-, 705/1 (`no,yes`). Copy: `work/round4/sweep/wsl_r63322/`.
- Candidates at court 703 (Court of Appeals of Texas, First District), both good law, both binding (own court,
  strong): h30 (node 30, 1963, `no`, promoted by "writ refused": holder 701 via writRefused) and h43 (node 43,
  1993, `yes`, same court, not promoted). They bind each other, so neither is displaced on either side.
- Lean after the round-4 `candFor` change (DEVIATIONS 82): h30 has precedence 3 (TXpromoted), h43 precedence 2;
  `resolve` keeps h30 only: no conflict. Before the change both had 2 and Lean would also have said `no,yes`. So
  the change exposed this; it is the same family (writ-refused precedence), seen from the other side.
- Verdict: Lean is right. A writ-refused decision has Supreme Court of Texas value (doctrine.md line 104); a later
  unpromoted decision of the same court of appeals does not stand equal to it. The reference has no precedence
  step, only displacement, and its `binds` treats the two as equals of one court.
- Reference change (not applied; tested on a private copy `work/round4/sweep/t63/precedent_ref.py`): in `_resolve`
  / `binds`, inside `if D.court[na] == D.court[nb]:`, after the Kentucky tier clause, add
  `promoted(n) = any(h.via == 'writRefused' for h in self.holders(n, asof) or ())` and
  `if promoted(nb) and not promoted(na): return False`.
- Check: 63322 new reference vs stored Lean: conflicts 0/23, all other layers 0. On 62003, 62350, 62391 the new
  reference's outputs (conflicts, status, findings, splits, certs, horty) are identical to the old reference's, so
  the `r4-*` regress universes stay at 0. A wider variant (count writRefused holders like adopters) was tried and
  rejected: it adds conflict rows at 703/705 in the three older universes.
- Not checked: the real data (no reference run made). The clause only fires for two same-court conflict candidates
  of which exactly one is writ-refused; real data has 92 conflict rows, 0 disagreements before.
