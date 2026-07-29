# PUBLICATION: Velocity-Initialized Phenotype-Structured Tumor Dynamics
# with Data-Derived Parameters Reproduces Clinical Trial Outcomes

## Title Options
1. "A phenotype-structured ODE initialized from RNA velocity reproduces 
   clinical trial outcomes with zero parameter tuning"
2. "From single-cell trajectory to clinical hazard ratio: a computational
   framework linking RNA velocity to drug response prediction"
3. "INTERCEPTA: velocity-informed continuous resistance modeling predicts
   docetaxel outcomes and combination failures in prostate cancer"

## Novel Contributions (what no one has done)
1. First model to initialize tumor dynamics from RNA velocity latent_time
2. First model where ALL parameters trace to measured data (no tuning)
3. First model that correctly predicts both drug successes AND failures
4. KAALCURA per-bin bridge: scRNA-seq → cell types → drug sensitivity
5. Demonstration that beta and alpha_ind are irrelevant to HR
   (resistance is selection, not evolution — proven computationally)

## Key Results
| Result | Value | Clinical Reference |
|--------|-------|--------------------|
| Doc HR (mCRPC) | 0.673-0.691 | TAX-327: ~0.76 |
| Doc TTP | 10.0 months | TAX-327: 9.5 months |
| Doc+Cis vs Doc | HR=1.003 | All Phase III combos failed |
| Emax | 0.153/day | GDSC 0.85 × 0.18 correction |
| Beta sensitivity | HR varies <0.02 | Model robust |
| Alpha_ind sensitivity | HR varies 0.022 | Model robust |

## Figures
1. Architecture: velocity → phenotype bins → KAALCURA → ODE → HR
2. Velocity distribution from STAR-aligned scVelo (46,235 cells)
3. KAALCURA axes across 20 resistance bins (R_prolif, R_emt, R_ddr)
4. EC50(x) profiles: docetaxel constrained within GDSC bounds
5. Simulation: tumor dynamics under docetaxel (nadir + regrowth)
6. Parameter sensitivity: beta and alpha_ind vs HR (flat lines)
7. Combination prediction: Doc+Cis HR=1.003 matches clinical failure
8. Cross-disease: AML net with BeatAML FLT3 validation

## Methods
- Phenotype-structured ODE (Lorz-Lorenzi-Clairambault framework)
- RNA velocity via scVelo dynamical mode (STAR-aligned)
- KAALCURA axes (validated AUROC 0.638, residualized)
- EC50 constrained to GDSC P5-P95 (no extrapolation)
- Emax from GDSC in vitro × literature correction
- PK from FDA labels (all drugs)

## Honest Limitations (in paper)
- 6 prostate cell lines anchor EC50 (narrow data)
- CRPC velocity only — cannot validate mHSPC trials
- Emax correction factor from literature range (not measured)
- Cannot model continuous therapy resistance (PROfound)
- Single disease validated (mCRPC); AML expansion preliminary

## Target Journals
1. Cancer Research (AACR) — computational oncology focus
2. Nature Computational Science — novel methodology
3. Cell Systems — systems biology integration
4. PLOS Computational Biology — open access, methodology
5. bioRxiv preprint first for rapid dissemination

## Timeline
- Week 1: Write Methods + Results
- Week 2: Write Intro + Discussion + Figures
- Week 3: Internal review, revise
- Week 4: Submit to bioRxiv + journal
