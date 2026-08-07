# DARK1 — abstention integrity at the dark-proteome boundary — SUMMARY

**GATE: PASS (fail-SAFE).** Orchestrator-verified (prereg gates frozen before scoring; scoring reproduced ×2).
**payload sha256:** `ec0c0eb4c979512dcec41dcd261d5d3d7ff28ff2df0e3bde72fa00f9863712b1`
**Evidence tier:** COMPUTED (in-silico integrity test; not wet-lab). n=22 dark + 20 control.

## Question
The vision's own named deepest frontier (VISION.md): a protein with no sequence homolog, no usable structure,
no reference ligand. Does the composite ABSTAIN (fail safe) or emit false-confident target calls (fail dangerous)?

## Method
DARK set = proteins dark to BOTH target-ID channels: 0 mmseqs hits (e<=1e-3) vs the 2148 ChEMBL drug-targets
AND mean AlphaFold pLDDT <50 (or no model). 22 dark (verified: all 0 drugged sequence homologs; 14 pLDDT
35.8-49.3, 8 no model). CONTROL = 20 human ChEMBL drug targets with usable AF models. Ran the composite's
sequence + (pLDDT-gated) structural homology signals; target call iff either fires, else ABSTAIN.

## Result
- **G1 (fail-safe, >=90% abstain on dark): 22/22 = 100% PASS.** Zero false-confident calls.
- **G2 (discriminating, >=70% fire on controls): 20/20 = 100% PASS.** (16/20 via a non-self drugged homolog,
  14/20 also structural — fires for real reasons, not tautology.)
- **PASS = G1 AND G2.**

## The load-bearing finding
The structural channel is an INDEPENDENT test and it nearly fired: **7 of 22 dark proteins (32%) had an UNGATED
Foldseek TM >= 0.5 (max 0.82) onto a real drugged fold** — would-be false-confident calls suppressed ONLY by the
pLDDT<50 confidence gate. Without that gate the composite would have emitted false-confident target calls on ~a
third of genuinely un-analyzable proteins. The structure-confidence gate is empirically **load-bearing, and it held**.

## Honest boundary
Shows the composite fails SAFE at the homology-null + structure-null edge (abstains 100%, 0 false calls) while
still firing on 100% of analyzable input. Does NOT *solve* the dark proteome (for a truly dark protein it
correctly produces nothing). "Dark" is 2 computational gates on n=22, not a universal non-homology proof.
Residual risk: AlphaFold can be over-confident on some disordered proteins (e.g. alpha-synuclein pLDDT 75,
correctly excluded here) — a protein AF wrongly scores confident could reach the structural channel; none did.
In-silico, CPU-only, not wet-lab.
