# HARDENV1 — CROSS-VIRUS structural target-class recovery (SUMMARY)

**GATE: PASS** — pre-registered before scoring; reproduced x2 byte-identical.
**payload sha256:** `7ac875e789c3f05402a33bae00a57754a5b7da52362b1ac16ac85b1465ec5736`
**Evidence tier:** COMPUTED (in-silico structural class-ID on experimental PDB structures; no wet-lab).
**n = 4 additional viruses** (HIV-1, Influenza A, HCV, HSV-1), hardening GENERALIZE3's n=1 (SARS-CoV-2).

## What it did
Reused GENERALIZE3's cleaning (longest target chain; MSE->MET; drop ligands/ions/waters/nucleic acids) + Foldseek
TMalign (`--alignment-type 1`, query-normalized qtmscore). Foldseek-ranked **9 clinically drugged viral targets**
against a FROZEN **37-structure, 14-class** panel (GENERALIZE3's 31 + 6 same-fold cross-family analogs:
bacterial sialidase, pepsin, renin, EcoRV, E. coli RNase H, adenylate kinase). **Leakage control (per virus):**
references from the test virus's own family were EXCLUDED before ranking (HIV -> drop HIV protease + HIV RT;
HCV -> drop HCV NS5B; Influenza/HSV -> none in panel), so every recovery is genuine CROSS-FAMILY structural
transfer, never a self-match.

## Result (gate frozen before scoring) — recovery 7/9 targets = 0.778, across all 4 viruses (random baseline ~0.071)
| target | virus | correct class | best retained hit (class) | TM | correct-vs-offclass margin | recover |
|---|---|---|---|---|---|---|
| HIV_RT   | HIV-1 | polymerase  | HCV-NS5B (polymerase)          | 0.413 | +0.148 | YES |
| HIV_PR   | HIV-1 | protease    | pepsin (protease, aspartic)   | 0.792 | +0.370 | YES |
| HIV_IN   | HIV-1 | nuclease    | E. coli RNase H (nuclease)    | 0.490 | +0.080 | YES |
| FLU_NA   | Flu A | glycosidase | bacterial sialidase (glycos.) | 0.653 | +0.340 | YES |
| FLU_PA   | Flu A | nuclease    | androgen-receptor (nucl.rec.) | 0.418 | -0.015 | no  |
| HCV_NS3  | HCV   | protease    | thrombin (protease, serine)   | 0.697 | +0.305 | YES |
| HCV_NS5B | HCV   | polymerase  | HIV-RT (polymerase)           | 0.416 | +0.130 | YES |
| HSV_TK   | HSV-1 | kinase      | adenylate kinase (kinase)     | 0.426 | +0.016 | YES |
| HSV_POL  | HSV-1 | polymerase  | HCV-NS5B (polymerase)         | 0.211 | +0.012 | no  |

- **7/9 recover** correct drugged class at TM>=0.40 with the correct class strictly out-scoring every off-class
  option (positive margin) in all 7; **>=1 recovery on all 4 viruses** => GATE PASS.
- **Null/off-class check:** for 8/9 targets the correct class wins over the best off-class hit (positive margin);
  the leakage-excluded same-family analogs are NOT what carried recovery (e.g. HIV_RT recovers via HCV-NS5B and
  Klenow after both HIV polymerases are removed; HCV_NS5B recovers via HIV-RT/Klenow after HCV NS5B removed).

## The two misses — both are the PRE-DISCLOSED confounds, reported first-class (not re-run)
1. **HSV_POL (miss, size artifact):** its TOP hit is still a **polymerase** (HCV-NS5B) — class is correct — but at
   TM 0.211, below the 0.40 bar. Exactly the pre-registered qtmscore query-length-normalization confound: HSV DNA
   pol is ~1035 res, so a real palm-domain match is diluted (same effect that sank SARS-CoV-2 spike in G3).
2. **FLU_PA (miss, near-tie artifact):** PA endonuclease DID match a nuclease (TM 0.403) but a spurious
   androgen-receptor edged it by +0.015 (0.418) for the top slot. Correct class was a very close 2nd; honest miss.

## Meaning
Blind, leakage-controlled, multi-class STRUCTURAL homology recovers the correct drugged-enzyme class for a clear
MAJORITY (7/9) of known drug targets across FOUR additional viruses, far above a ~7% random-class baseline and with
same-family analogs excluded. GENERALIZE3's SARS-CoV-2 finding is NOT a one-off: the structural bridge that recovers
viral intervention-target class where sequence homology gives zero (GENERALIZE1) is a CROSS-VIRUS property. Honest
limits: TMs for several true targets are MODERATE (0.41-0.49, below the 0.5 same-fold convention); qtmscore penalizes
very large multidomain queries (HSV_POL); short/near-tie artifacts exist (FLU_PA). In-silico class-ID on experimental
structures, n=4 viruses / 9 targets; not wet-lab and not a deployed pipeline.
