# R2 — OOD-generalization testbed — SUMMARY

**Status: BUILT + reproduced ×2 byte-identical** (payload sha `dffa5ef…`). A reusable, leakage-controlled
instrument (roadmap R2). Per the locked `PREREG.md`.

## What it is
`ood_testbed.py` takes any target's train/test SMILES + potency and reports AUROC + bootstrap 95% CI on
**SEEN(analog)** vs **NOVEL** chemotype splits (NOVEL = max ECFP4 Tanimoto to train actives < 0.40), for a
similarity control, a QSAR-RF, and an optional drop-in external score (e.g., a foundation model). It fires a
pre-registered **WALL_BREAKING** alarm iff a non-similarity method's NOVEL-split AUROC CI-lower > 0.60.
Reusable: `python ood_testbed.py <csv> <smiles_col> <potency_col> <split_col> [external_scores.csv]`.

## First instantiation — thrombin (MoleculeACE CHEMBL204), verdict WALL_HOLDS
- `qsar_rf`: SEEN **0.930** CI[0.903,0.954] → NOVEL **0.795 CI[0.417,0.995]** (n_pos=**5**) → **alarm does NOT fire** (CI-lower 0.417 < 0.60).
- `similarity` control: SEEN 0.809 → NOVEL **0.384** (collapses below chance off-manifold, as expected).
- **Verdict: WALL_HOLDS.**

## The finding the instrument surfaced (honest, and it matters)
The thrombin/MoleculeACE benchmark **cannot power the OOD question**: leakage audit shows median test→train
max-Tanimoto **0.75**, 35% ≥0.8, only **12% novel (<0.4)**, and only **5 novel actives**. It is an
*interpolation* benchmark (activity-cliff series), so the NOVEL-split CI is uninformative and the
scaffold-novel split (0.914) is misleading (a novel Murcko scaffold is still ECFP-near here). The instrument
correctly **abstains** (WALL_HOLDS, no false alarm at n=5) — but the real conclusion is: **to measure the wall
we need genuinely-novel-active-rich datasets** (scaffold/temporal splits with many low-Tanimoto actives, e.g.
LIT-PCBA/DUD-E or a temporal ChEMBL split). That is exactly the job of roadmap **R3** (public-data ingestion):
feed R2 powered OOD datasets, and drop foundation-model scores into the `external` slot, on every new release.

## Value
- The vision's core question is now a **monitored, reproducible number**, not an opinion.
- The alarm mechanism is validated (it does not false-fire on underpowered novelty).
- It exposed that our in-hand affinity benchmark is inadequate for OOD — redirecting the next compute to
  *acquiring powered OOD data* rather than re-running interpolation benchmarks.
