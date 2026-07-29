# Q10 anchor 1 — Open-source vs proprietary landscape for INTERCEPTA components

## 0. Identification (composite review of Decisions 1-9 component licensing)

All Decision 1-9 components reviewed for license + accessibility:

| Component | Implementation | License | Status |
|---|---|---|---|
| scFoundation (Q1) | github.com/biomap-research/scFoundation | Open | Production-ready |
| UCE (Q1) | github.com/snap-stanford/UCE | Open | Production-ready |
| scGPT (Q1) | github.com/bowang-lab/scGPT | MIT | Production-ready |
| Geneformer (Q1) | huggingface.co/ctheodoris/Geneformer | Apache 2.0 | Production-ready |
| scVI/scANVI/MrVI (Q2) | scvi-tools | BSD-3 | Production-ready (Yosef lab) |
| Harmony (Q2) | github.com/immunogenomics/harmony | GPL-3 | Production-ready |
| Seurat v3 (Q2) | satijalab/seurat | MIT | Production-ready |
| scIB (Q2) | github.com/theislab/scib | MIT | Production-ready |
| SCAD (Q3) | github.com/Linwei-Z/SCAD | Open | Research code |
| scDEAL (Q3) | github.com/OSU-BMBL/scDEAL | Open | Research code |
| scAdaDrug (Q3) | github.com/hliulab/scAdaDrug | Open | Research code |
| scRank (Q3) | github.com/ZJUFanLab/scRank | Open | Research code |
| Beyondcell (Q3) | gitlab.com/bu_cnio/beyondcell | Open | Production-ready |
| GDSC (Q3) | cancerrxgene.org | CC0 | Open data |
| CCLE/DepMap (Q3) | depmap.org | CC BY 4.0 | Open data |
| DeepCDR (Q4) | github.com/kimmo1019/DeepCDR | Open | Research code |
| PaccMann (Q4) | github.com/PaccMann | Apache 2.0 | Production-ready (IBM) |
| sci-Plex (Q4) | trapnell-lab data | Open | Open data |
| CPA (Q4) | github.com/facebookresearch/CPA | MIT | Production-ready (Meta) |
| GEARS (Q4) | github.com/snap-stanford/GEARS | Open | Research code |
| scGen (Q4) | scvi-tools (now) | BSD-3 | Production-ready |
| Conformal prediction (Q5) | various | Open | Production-ready |
| Deep Ensembles / MC Dropout (Q5) | PyTorch standard | OS | Production-ready |
| IG / SHAP (Q7) | captum (PyTorch) | BSD-3 | Production-ready |
| Nicheformer (Q8) | github | Open | Research code |
| TEDDY (Q8) | not yet released | TBD | Pre-publication |
| EVA (Q8) | huggingface.co/Scienta-Lab + GitHub Scienta-Lab | **Partially open** (60M-parameter open weights on HF) + commercial deployment via Scienta partnerships | Production-ready (open variant) |

## 1. Critical observation

**Almost the entire INTERCEPTA stack is open-source.** EVA is **partially open** — Scienta released a 60M-parameter version of EVA's transcriptomic model on Hugging Face under the Scienta-Lab GitHub organization, while larger versions remain closed for commercial deployment. **TEDDY release pending.**

**Errata note:** The original 2026-05-10 file incorrectly listed EVA as "Closed/proprietary." Verified correction (Scienta Lab launch announcement Feb 12, 2026 + Hugging Face Scienta-Lab organization page): EVA has an open 60M-parameter variant. This corrects Q10 Drift Instance #5 and updates Decision 8 implication: EVA *is* accessible for academic research, not blocked.

**Charter §7 commitment to single-institution + open science is fully satisfiable** without proprietary dependencies. EVA's open 60M variant means even disease-specific FM coverage (Charter §1.1 universality for I&I) is achievable with open weights.

## 2. License compatibility

- BSD-3 + MIT + Apache 2.0 + GPL-3 + CC: all compatible for academic research use
- GPL-3 (Harmony) requires derivative works to also be GPL-3 — INTERCEPTA must respect this when wrapping Harmony
- CC BY-NC-ND (DiSyn — Q6 ref): non-commercial restriction; OK for INTERCEPTA academic deployment but limits commercial use of DiSyn-derived models
- EVA open variant: license terms must be checked at Hugging Face Scienta-Lab/EVA-RNA-60M page before deployment
- TEDDY: license pending publication

## 3. INTERCEPTA implications

**For Q10:** Open-source stack is the default architecture. **No proprietary dependencies needed.**

— Claude (CSO), 2026-05-10
