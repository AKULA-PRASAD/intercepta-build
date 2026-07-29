# INTERCEPTA VERIFICATION LEDGER (independent, falsify-first)
Date 2026-07-29. Claims from INTERCEPTA docs re-verified by Claude(CSO) under the Constitution.
Tag: [VERIFIED] reproduced+hard-tested by me | [SELF-AUDIT] from INTERCEPTA's own audit | [CLAIM] not yet re-verified.

| # | Claim | Verification | Status |
|---|---|---|---|
| 1 | BeatAML NPM1-mut → Cabozantinib sensitivity (strongest claim, p=2.9e-12) | reproduced (p=4.4e-11, n=157/425); FLT3-ITD dominant (p=5.1e-21); NPM1 INDEPENDENT of ITD+FLT3-point+DNMT3A (OLS p=2.6e-3; strict subset p=1.6e-2); reproduced ×2 | **[VERIFIED] real & deconfounded; needs external replication** |
| 2 | KAALCURA R_prolif prognostic (chemo pCR/response) | CRC OR=0.570, breast pCR AUROC 0.734/0.653/0.654, melanoma scRNA 0.719 (kaalcura repo, reproduced ×2) | [VERIFIED] real prognostic (≈GGI, not novel) |
| 3 | KAALCURA multi-axis therapy SELECTION / specificity | 0/16 axis×arm interactions BH-sig at n=988 (I-SPY2 990) | [VERIFIED] NOT supported (prognostic, not selective) |
| 4 | I-SPY2 two-axis coordinate (OR=12.80) | reproduces OR=12.19, R_immune adds p=0.019, perm p=0.0005; bounded single trial | [VERIFIED] real, bounded |
| 5 | ODE reproduces 5 mCRPC trials | 2/6 Framework A, 0/3 growth-rate; directional not quantitative | [SELF-AUDIT] over-claimed→corrected |
| 6 | Novel-molecule generation (Scout 2) | scaffold-hopping, not de novo; no generative model | [SELF-AUDIT] fake claim, corrected |
| 7 | NRAS→MEK inhibitors (Selumetinib/Trametinib/CI-1040) | REPRODUCED, all 3 consistent (p=3e-11/6e-10/1.7e-9), NRAS-mut more sensitive | **[VERIFIED] real, KNOWN RAS/MAPK biology (positive control)** |
| 8 | DNMT3A→Dasatinib | REPRODUCED p=1.6e-5; deconfounded (OLS β=−23.7 p=1.2e-4, independent of NPM1/FLT3-ITD) | **[VERIFIED] real & deconfounded; possibly novel; needs external replication** |
| 9 | Drug-SPECIFICITY of NPM1 effect | NPM1 independent for Cabozantinib (p=2.6e-3) but NOT Dasatinib (p=0.45) | **[VERIFIED] NPM1 effect is drug-specific, not a generic artifact** |

## Net status
INTERCEPTA's strongest result is now independently VERIFIED and deconfounded (row 1). The KAALCURA module is
fully hard-tested (rows 2-4). The ODE and generative claims are honestly downgraded (rows 5-6, self-audited).
Next verification targets: DNMT3A-Dasatinib (row 8); external replication of NPM1-Cabo; then the untested
RNA-velocity pre-resistance idea.

## Row 10 — [VERIFIED] NPM1->Cabozantinib internal split-replication
Deterministic md5 subject-id parity split. Half0 (n_mut=82): MW p=8.6e-6, OLS adj-ITD p=6.6e-3, beta=-19.6.
Half1 (n_mut=75): MW p=1.2e-6, OLS adj-ITD p=1.6e-3, beta=-24.4. Correct direction (mutant more sensitive)
and significant in BOTH halves, adjusted and unadjusted. -> `beataml_npm1_cabo_split_replication.json`.

## Row 11 — [NOT TESTABLE / NEEDS-DATA] RNA-velocity "time machine" (pre-resistance)
Most novel idea. Velocity outputs = per-cell latent_time + per-cluster magnitudes only; NO per-cell
drug-response/resistance ground truth in any available scRNA (prostate: velocity+clusters no outcome; AML
vangalen: CellType+genotyping no drug response). Predictive claim NOT falsifiable on current data. Minimum
missing data: paired longitudinal scRNA (baseline + relapse, same patients) with matched outcome, ideally
lineage-traced. Architecturally novel, empirically untested. Do NOT claim it works. -> `RNA_VELOCITY_FEASIBILITY.md`.
