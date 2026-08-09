# DYNAMICS3 — predicted-pocket durability: QUALIFIED PASS (reproduced x2, sha 5b572a61)

**Solves:** durability (DYNAMICS1/2) needed a drug-BOUND crystal to define contact residues, so it could not
score undrugged/novel targets (DURABLETARGETS1 left ispE = NA). DYNAMICS3 replaces crystal contacts with the top
fpocket pocket on the apo AlphaFold structure, keeping the ESM masked-marginal-entropy metric byte-frozen.

## Pre-registered gates — PASS
- Feasibility 20/26 usable top pocket (bar >=18); 9 HIGH / 11 LOW. 6 infeasible (no AF-DB model / viral strain-
  specific / RT-domain-uncovered) -> applicability bound: bacterial + eukaryotic single cores, not strain-specific viral.
- G1 agreement (Spearman predicted vs crystal durability): rho 0.714, p 4.0e-4 (bar rho>=0.5) -> PASS.
- G2 discrimination (AUROC predicted durability vs HIGH-liability): 0.899, MWU p 3.0e-3 (bar >=0.70); abx-only
  (n=18) 0.883 -> PASS, robust within bacteria.

## CENTRAL HONEST CAVEAT (bounds the PASS -- it is a QUALIFIED pass)
fpocket's blind top pocket is USUALLY NOT the actual drug site (0.0 crystal-site overlap for embB/gyrA/parC/rpoB/
rpsL/CYP51/mraY/murA/murE; only HSV1_TK/ddlB/dxr/glmU hit it), and predicted durability sits systematically higher
than crystal (murA predH 2.00 vs crysH 0.18). Yet the durability RANK (rho 0.71) and HIGH/LOW separation (AUROC 0.90)
survive. Interpretation: the recovered signal is a **functional-cavity / partly whole-protein mutational-tolerance**
proxy, NOT calibrated drug-contact tolerance. Informative vs AMR1 (whole-protein mean FAILED 0.556; restricting to a
functional cavity -- even the "wrong" one -- recovers the signal). PRACTICALLY: you can triage a novel target's
durability without knowing its drug pocket, but it is a COARSER rank/triage proxy, advisory, not a calibrated substitute.

## Application
ispE (E. coli, P62615), previously durability=NA, now scores predicted-pocket durability 1.89 (advisory: mid-high
tolerance, but its top pocket is not verified to be the CDP-ME/ATP site). The pipeline generalizes to any undrugged
core with an AF model -- filling the DURABLETARGETS1 NAs as advisory values.

## Scope
In-silico; n=20; ESM entropy = PLM proxy for mutational fitness, not measured fitness; apo static structure; the
signal is a functional-cavity tolerance proxy (see caveat). A coarse durability TRIAGE for novel/undrugged targets,
not a calibrated drug-contact predictor.
