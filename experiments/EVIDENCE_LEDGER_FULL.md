# INTERCEPTA — Full Evidence Ledger (per-experiment, auto-extracted)

*Auto-extracted from `LEDGER.md` (evidence-of-record) on 2026-08-10. One row per experiment directory under `experiments/` (169 dirs enumerated). Numbers only — no interpretation. "LEDGER:N" = physical line N of `LEDGER.md`; where a cancer B-experiment has no standalone LEDGER row it is folded into a V-row (noted) or cited to the manuscript (ENG = `papers/intercepta_engine/MANUSCRIPT.md`; ZDD = `papers/zero_data_discovery/REPORT.md`) / audit file. "not in ledger" = no row found; directory exists. Never invented; unknowns marked. `repro?` = reproduced ×2 with committed byte-identical metrics.*

Column order: **Dir/ID | objective | headline result (numbers) | verdict | repro? | source**

---

## Arm 1 — Antimicrobial target-ID / FBA-essentiality (the validated spine)

| Dir / ID | Objective | Headline result (numbers) | Verdict | Repro? | Source |
|---|---|---|---|---|---|
| VALIDATE_essentiality | FBA-ess vs experimental knockouts, incl. held-out WHO pathogens | E.coli/PEC OR 64.3 (p 3.1e-24, prec 0.77, rec 0.22); held-out K.pneumoniae OR 63 (prec 92%), A.baumannii OR 13 (p 3e-6) | VALIDATED | yes | LEDGER:10,12,15 |
| EXPVAL_predictions | 7 pre-locked E.coli essentiality predictions | 6/7 experimentally essential (ribA/ribB/folB/ribD/ispG/ispD; mtnN = confirmed false positive) | PASS | yes | LEDGER:10 (no dedicated row) |
| PREDVAL_target_scorecard | per-target scorecard vs experiment | murB/murG/dxr/murF/ispE essential in all 3 tested orgs; 2/3 & 0/3 controls | VALIDATED | yes | LEDGER:14 |
| CROSSVAL_curated | 6 curated GEMs, 3 phyla, OR>3 gate | OR 4.3–45 (E.coli iML1515 45, Mtb 26.1, Salm 4.3, Bsub 12.5, Saureus 15.9, Kpneu 6.0); 6/6 pass; prec/rec up to 0.68/0.79 | VALIDATED | yes | LEDGER:25 |
| SAUREUS_gram_positive | Gram-positive S.aureus essentiality | OR 5.37 (p 0.0057, prec 0.21, rec 0.11); weakest in panel | PASS (weak) | yes | LEDGER:24 |
| NEWBUG_heldout_pathogen | held-out novel pathogen deployment | 26/29 recovered | VALIDATED | yes | LEDGER:167 |
| PANBACT_catalog | pan-bacterial target catalog | 85 safe predictions across 7 pathogens (validated) | VALIDATED | yes | LEDGER:165 |
| DRUGGABLE_predictions | druggable-pocket subset across pathogens | murB essential 5/7 + MEP/isoprenoid core (per-pathogen counts) | VALIDATED | yes | LEDGER:166 |
| BROADSPEC_predictions | broad-spectrum prediction output | (output artifact, not a hypothesis test) | not in ledger | na | dir only (2 mentions) |
| MET1_fba_essentiality_targets | FBA-ess breaks conservation ceiling (E.coli) | ΔAUROC +0.132 (ess 0.71 > cons 0.35), OR 8.6 | POSITIVE | yes | LEDGER:151 |
| MET2_fba_generalization | ceiling-break generalize across bacteria | replicates E.coli +0.053 / Mtb +0.040; OR 5.8–18.5 | PARTIAL | yes | LEDGER:152 |
| MET3_composed_ranking | essentiality → better ranked shortlist | P@k E.coli 0.28→0.35 (4.9→6.2×); Mtb +0.015 | PARTIAL | yes | LEDGER:153 |
| TID1_zerodata_target_identification | homology-transfer target-ID vs conservation null | AUROC 0.64 vs conservation null 0.72 | NEGATIVE (ceiling) | yes | LEDGER:144 |
| TID2_structural_druggability | pocket druggability beyond conservation? | 0.54 alone; +conservation ΔAUROC +0.005 (coef 0.07 vs 0.70) | NEGATIVE | yes | LEDGER:145 |
| TID3_crosskingdom_generalization | cross-kingdom degradation | degrades bacteria→parasite→fungus; fungus recovers none; abstention doesn't track (silent fail) | NEGATIVE (boundary) | yes | LEDGER:149 |
| TID4_organism_confidence | predict when target-ID fails? | best Spearman −0.31; org-level abstention worse than random | NEGATIVE | yes | LEDGER:150 |
| REACH1_nonmetabolic_recall | recover FBA-missed non-metabolic essentials | real ranking signal at precision cost (mixed) | PARTIAL | yes | LEDGER:16 |
| FRONT1_selective_mechanistic_targets | selectivity + therapeutic-validity warning | conservation-ranking dangerous: host-toxic mean bitscore 123 vs 29 | POSITIVE (finding) | yes | LEDGER:156 |
| FRONT2_structural_selectivity | structure rescue host-homologous targets? | pocket AUROC 0.51; pathogen-vs-host diff 0.53 | NEGATIVE | yes | LEDGER:159 |
| E2E1_pathogen_endtoend | end-to-end pipeline on Mtb | runs proteome→shortlist; composite doesn't beat conservation (demo) | PASS (demo) | yes | LEDGER:146 |
| E2E2_corrected_pipeline | safety/recall tension of hard filter | hard host-nonhomology filter excludes 35–52% of known targets | PARTIAL (tension) | yes | LEDGER:157 |
| ENGINE_endtoend | shipped engine on held-out K.pneumoniae | 15/30 top experimentally essential; 13/13 | VALIDATED | yes | LEDGER:17 |
| SUBSTRATE2_molecule_stage → ENGINE-MOL | molecule-ranking stage | 57/60; AUROC 0.63 | VALIDATED | yes | LEDGER:18 |
| ENGINE-AB (via A.baumannii run) | engine on 2nd held-out pathogen | 5/30 top (native resistance/condition classes) | VALIDATED | yes | LEDGER:23 |
| CONDROB1_condition_robust | condition-robustness quality filter | multi-medium essentials 79% vs 48% experimentally essential (+0.32) | VALIDATED | yes | LEDGER:21 |
| BESTINT1_multiaxis_score | equal-weighted best-intervention score | orders targets by real essentiality Spearman 0.69; 35/49 | VALIDATED | yes | LEDGER:22 |
| CALIB1_substrate_confidence | is confidence calibrated to accuracy? | ordinal-confidence AUROC 0.66, monotonic in 2 regimes | PASS | yes | LEDGER:13 |
| FAIRGATE1_baserate_fair_gate | base-rate-fair transfer gate (replace OR>3) | RR-based gate validated by base-rate invariance + simulation | PASS (invention) | yes | LEDGER:35 |
| META1_transfer_law | meta-analysis of 19 organisms | log-OR vs GEM size ρ +0.55 (p 0.014); OR>3 gate base-rate-confounded (iPfal19 flips) | analysis | na | LEDGER:34 |
| VAL-ESS-MTB (no own dir) | Mtb generalization of experimental validation | OR 7.9 enrichment; fine-rank AUROC ≈ chance | PASS (binary) | yes | LEDGER:11 |

## Arm 2 — Prospective-blind suite (analyst-blind, lock-before-reveal)

| Dir / ID | Objective | Headline result (numbers) | Verdict | Repro? | Source |
|---|---|---|---|---|---|
| BLIND1_ngonorrhoeae | Bacteria β/γ-proteo, DEG | OR 6.1 (p 4e-6, prec 0.78) | PASS | yes | LEDGER:26 |
| BLIND2_cjejuni | Bacteria ε-proteo, Tn-seq | OR 3.9 (p 6e-4) | PASS | yes | LEDGER:27 |
| BLIND3_bacteroides | New phylum Bacteroidetes, INSeq | OR 8.0 (p 4e-6) — strongest | PASS | yes | LEDGER:30 |
| BLIND4_spneumoniae | Firmicute, sparse 13-gene de-novo GEM | OR 3.0 (p 0.06) | FAIL (model-quality floor) | yes | LEDGER:28 |
| BLIND5_kphaffii | Eukaryote/fungus, curated GEM | OR 2.4 (p 4e-5, prec 0.29) — significant but sub-gate | FAIL | yes | LEDGER:32 |
| BLIND6_mmaripaludis | Archaeon (3rd domain), Tn-seq | OR 4.2 (p 1e-15, prec 0.70, rec 0.60) | PASS | yes | LEDGER:31 |
| BLIND7_tbrucei | Eukaryote kinetoplastid, RIT-seq | OR 0.6 (p 0.87) — invariant break | FAIL | yes | LEDGER:29 |

## Arm 3 — Non-metabolic mechanism negatives (FBA-blind half)

| Dir / ID | Objective | Headline result (numbers) | Verdict | Repro? | Source |
|---|---|---|---|---|---|
| MET4_mechanism_beyond_metabolism | PPI-centrality for non-metabolic half | +0.128 → −0.004 after study-bias control (study-intensity alone AUROC 0.826) | NEGATIVE | yes | LEDGER:154 |
| NONMET1_genomic_context_nonmetabolic | synteny/genomic-context signal | ΔAUROC +0.016 E.coli / +0.0007 Mtb (< +0.03 gate); conservation 0.908 | NEGATIVE | yes | LEDGER:37 |
| REGNET1_regulatory_nonmetabolic | curated GRN regulatory signal | master-reg OR 0.52 (p 0.96); ΔAUROC −0.006 | NEGATIVE | yes | LEDGER:48 |
| PLMESS1_plm_nonmetabolic | ESM-2 embedding signal | ΔAUROC +0.008; study-bias-controlled −0.0006; embedding AUROC 0.878 < cons 0.908 | NEGATIVE | yes | LEDGER:49 |
| PLMSTRUCT1_structure_aware_plm_nonmetabolic | structure-aware PLM signal | — | not in ledger | na | dir only (0 mentions) |
| MULTISIG1_nonmetabolic_ensemble | 4-signal ensemble upper-bound | ΔAUROC +0.019 (logistic) / +0.009 (GBM), both < +0.03; conservation 0.908 unbeaten | NEGATIVE | yes | LEDGER:50 |

## Arm 4 — Molecule / affinity / hit-finding

| Dir / ID | Objective | Headline result (numbers) | Verdict | Repro? | Source |
|---|---|---|---|---|---|
| HIT1_transfer_ceiling | ligand-based novel-chemotype ceiling | agg AUROC 0.81/0.90; novel-chemotype 0.90→0.67; analog-vs-inactive 0.82 | PARTIAL (soft ceiling) | yes | LEDGER:155 |
| HIT2_physics_floor | docking within-series potency | AUROC 0.43 (worse than random) | NEGATIVE | yes | LEDGER:158 |
| C1_mpro_zerodata_holdout | zero-data docking binder-vs-nonbinder (Mpro) | AUROC 0.63, MWU p 1e-4, EF1% ≈ 1.25 | PARTIAL (weak-real) | yes | LEDGER:143 |
| AFFINITY1_cofolding_zeroshot | zero-shot co-folding affinity (Boltz-2) | CPU-infeasible with GPU-spec (feasibility gate PASS; not refuted) | OPEN (compute-gated) | yes | LEDGER:40 |
| AFFINITY_IPTM1_structure_confidence | ipTM structure-confidence affinity proxy | — | not in ledger | na | dir only (0 mentions) |
| STRUCTREPURPOSE1_structural_repurposing | structural repurposing coverage gain | raw 18/32 but random null 25/32 → stays 1/32; G1 known 11/11 (0.94–1.00) | NEGATIVE (null guard) | yes | LEDGER:63 |
| INTERVENE1_repurposing | sequence repurposing (bacteria) | 9/9 known recovery; novel coverage 1/32 | VALIDATED (narrow) | yes | LEDGER:55 |
| INTERVENE2_cancer_repurposing | repurposing (cancer dependencies) | 10/10 known; coverage 6.8% (93.2% undrugged) | VALIDATED (narrow) | yes | LEDGER:75 |
| INTERVENE3_synthetic_lethal | SL route around undruggability | recovers 9/12 known SL pairs (~10× null); drugged only 25/3416, 3/192 drivers (~0.5–1%) | PASS (narrow) | yes | LEDGER:76 |
| B26_mechanism_synergy | mechanism-anchored synergy encoding | does NOT beat fingerprints for novel drugs (p 0.001 elsewhere) | NEGATIVE | yes | LEDGER:103 |
| B27_lincs_connectivity | LINCS signature-reversal repurposing | ρ 0.02 (p 5e-4) — significant but negligible | NEGATIVE | yes | LEDGER:104 |
| B30_admet | ADMET module | AUROC 0.893 / 0.700; 22/22 | VALIDATED (module) | yes | LEDGER:105 |
| B30b_admet_uncertainty | ADMET uncertainty | 20/22, 15/22, 13/22; p 0.049 | VALIDATED | yes | LEDGER:106 |
| B31_synthesizability | synthesizability proxy | screening proxy positive | VALIDATED (module) | yes | LEDGER:107 |
| B32_integration_mvp | integration MVP | AUROC 0.819; fusion fails | NEGATIVE | yes | LEDGER:108 |
| B32b_feature_fusion | feature-level fusion | weak/non-decisive positive; FAIL on decisive bar | PARTIAL | yes | LEDGER:109 |
| B33_goal_directed_design | goal-directed design demo | optimization demo validated | VALIDATED (demo) | yes | LEDGER:110 |
| B34_target_id | popularity-controlled target-ID | AUROC 0.522 (near-random; FAIL flag) | PARTIAL | yes | LEDGER:111 |
| B35_integration_paired | paired re-adjudication | p 0.019 / 0.30 (suggestive) | PARTIAL | yes | LEDGER:112 |
| B36_integration_multioutcome | multi-outcome integration | 0/7; p 0.47 (well-powered) | NEGATIVE | yes | LEDGER:113 |
| B37_learned_joint_representation | learned joint representation | 2/3 within-domain only | PARTIAL | yes | LEDGER:114 |
| B38_deep_foundation_model | deep molecular foundation model | 1/7 (5/7 elsewhere); p 0.23 | NEGATIVE/PARTIAL | yes | LEDGER:115 |
| B39_end_to_end_discovery | assembled platform end-to-end | pipeline works (PASS/PASS) | POSITIVE (demo) | yes | LEDGER:116 |
| B40_target_conditioned_generation | target-conditioned generation | steers to target (PASS/PASS) | POSITIVE | yes | LEDGER:117 |
| B41_pareto_reliable_discovery | AD-constrained Pareto | reliability win + honest test (PASS) | PARTIAL | yes | LEDGER:118 |
| B42_retrospective_rediscovery | known-drug re-discovery vs external truth | AUROC 0.806; 3/3 | POSITIVE | yes | LEDGER:119 |
| B43_generality_panel | generality across target panel | AUROC 0.835; 6/6; 4/6 | POSITIVE | yes | LEDGER:120 |
| B44_ligand_3d_scaffold_hop | RDKit O3A 3D scaffold hop | AUROC 0.634 / 0.625 | NEGATIVE | yes | LEDGER:121 |
| B45_hard_split_selfaudit | novel-chemistry self-audit | survives with optimism tax | POSITIVE | yes | LEDGER:122 |
| B46_litpcba_external | LIT-PCBA external benchmark | above-chance on unbiased benchmark | POSITIVE | yes | LEDGER:123 |
| B47_docking_structure_channel | AutoDock Vina docking channel | above-chance + orthogonal | POSITIVE | yes | LEDGER:124 |
| B48_channel_fusion | ligand ⊕ docking fusion | no gain over best single channel | NEGATIVE | yes | LEDGER:125 |
| B49_proteochemometric_pantarget | PCM leave-protein-out | generalizes but ligand-driven; protein features add nothing | PARTIAL | yes | LEDGER:126 |
| B51_active_learning_loop | closed-loop DMTA active learning | loop works | POSITIVE | yes | LEDGER:127 |
| B52_guacamol_generator_benchmark | GuacaMol goal-directed vs SOTA | optimises but below SOTA | PARTIAL (calibration) | yes | LEDGER:128 |
| B53_data_regime_crossover | when structure beats ligand | conditional crossover gated by docking fidelity | PARTIAL (refines) | yes | LEDGER:130 |
| B54_decoy_artifact_discriminator | decoy-bias vs analog-bias | biases independent + additive; modest irreducible signal | POSITIVE (finding) | yes | LEDGER:131 |
| B55_p6_external_dude | P6 replication on DUD-E | inconclusive for P6 (DUD-E too clustered) | INCONCLUSIVE | yes | LEDGER:132 |
| B56_p6_external_htspanel | P6 on TDC/Butkiewicz HTS | P6 replicates | POSITIVE | yes | LEDGER:133 |
| B57_residual_mechanism | mechanism of VS residual | not explained by SAR ruggedness | NULL | yes | LEDGER:134 |
| B58_residual_rogi_repowered | ROGI roughness re-test | roughness matters moderately; multifactorial | PARTIAL | yes | LEDGER:135 |
| B59_assayclass_residual | residual by assay format | null; bounds B58 | NULL | yes | LEDGER:136 |
| B60_continuous_potency_roughness | continuous-potency roughness / interp-extrap | resolves residual-mechanism arc | PARTIAL | yes | LEDGER:137 |
| B61_extrapolation_error_decomposition | per-compound extrapolation error | AD-distance null; error = regression-to-the-mean | NEGATIVE | yes | LEDGER:138 |
| B62_shrinkage_vs_signalloss | shrinkage vs signal-loss | signal-loss dominated → genuine info ceiling | NEGATIVE | yes | LEDGER:139 |
| B63_p6_dude_paradigm_generality | P6 across decoy paradigm | P6 HTS-paradigm-specific | NEGATIVE (boundary) | yes | LEDGER:140 |
| B64_endtoend_fen1_demonstration | full pipeline on FEN1 | capability demo (not a hypothesis test) | PASS (demo) | yes | LEDGER:141 |
| B65_active_learning_novelchem_ceiling | AL label-efficiency in novel-chem | flat null (acquisition not the lever) | NEGATIVE | yes | LEDGER:142 |

## Arm 5 — Cancer / oncology (B1–B25 fold into V-rows; ENG = engine manuscript)

| Dir / ID | Objective | Headline result (numbers) | Verdict | Repro? | Source |
|---|---|---|---|---|---|
| B1_baseline_ceiling | leakage-free cell-line transfer | ρ +0.212 (94/100>0, p 1.9e-15); prolif floor +0.058; leaky +0.278 | VALIDATED (ceiling) | yes | LEDGER:78 (V1); ENG §2.1 |
| B2_beat_ceiling | beat the +0.212 ceiling | +mut Δρ +0.0004 (q 0.74) / +prolif +0.0000 (p 0.98) — null | NEGATIVE (ceiling) | yes | LEDGER:84 (V7); ENG §2.1 |
| B3_patient_transfer | cell-line→patient transfer | diagonal ρ +0.054 (perm p 5e-4); not drug-specific on array (+0.022 p 0.12) | PARTIAL | yes | LEDGER:85 (V8); ENG §2.3 |
| B3b_patient_specificity | matched-platform drug-specificity | diag−off +0.040 (perm p 0.010, 44 drugs) | PASS (weak) | yes | LEDGER:86 (V9); ENG §2.3 |
| B3c_external_replication | independent-label replication | +0.051 (perm p 0.0015, 59 drugs) | PASS | yes | LEDGER:86 (V9); ENG §2.3 |
| B3d_robustness | drug/patient subsetting robustness | jackknife min +0.033; bootstrap CI [+0.008,+0.053] | PASS | yes | LEDGER:87 (V9+) |
| B3e_mechanistic_coherence | AML-mechanism coherence | H1 p 0.29/perm 0.50 — null | NEGATIVE (withdrawn) | yes | LEDGER:88 (N1); DECISIONS D8 |
| B4_mechanism_integration | mechanism + transfer combined | beats both single in 4/4 CV pairs; meta p 0.21 (n.s.) | PARTIAL (rule met) | yes | LEDGER:89 (V10) |
| B5_marker_discovery | genome-wide mutation→drug screen | 177 robust markers/3051 pairs; FLT3-ITD sorafenib q 4e-26 | VALIDATED | yes | LEDGER:91 (V12); ENG §2.2 |
| B6_calibration | confidence gating | OOD-distance +0.051 (p 0.0055); per-drug reliability +0.02 (p 0.45) | PASS (OOD only) | yes | LEDGER:92 (V13) |
| B7_pdxe_external | PDXE external transfer | borderline p 0.036 → not held (broader p 0.076) | NEGATIVE | yes | LEDGER:93 (V14); ENG §2.6 |
| B8_pdxe_mechanism | PDXE mechanism markers | PIK3CA→alpelisib underpowered (15 mutant, q 0.087) | NEEDS-DATA (underpowered) | na | ENG §2.6; WEAKNESS_AUDIT (B8) |
| B9_pdxe_prism | PDXE PRISM-trained replication | non-sig (p 0.14–0.31); prolif transfers better | NULL | yes | LEDGER:93 (V14); ENG §2.6 |
| B10_tcga_outcome | human clinical response (TCGA) | within-cancer AUROC 0.504 (p 0.43); raw 0.539 = cancer-type confound | NULL | na | ENG §2.7; WEAKNESS_AUDIT (B10) |
| B11_novel_replication | novel BeatAML markers replicate? | 0/13 replicate cross-system | NEGATIVE | na | WEAKNESS_AUDIT (B11); ENG §2.2 |
| B12_crispr_functional | measured dependency vs drug | pooled ρ +0.19 (p 5e-4); MDM2→idasanutlin +0.475 | VALIDATED | yes | LEDGER:94 (V15) |
| B13_inferred_dependency | expr→dependency learnable | CV ρ up to 0.59 (MDM2 0.58/EGFR 0.56) | VALIDATED | yes | LEDGER:95 (V16) |
| B14_functional_layer_patients | inferred layer rescues actionable targets | rescues FLT3/BCL2/CDK9/AURKA (9/26 drugs, BH<0.05) | POSITIVE (in-cohort) | yes | LEDGER:96 (V17) |
| B15_functional_landscape | layer specificity vs breadth | not broad; specific to dependency-driven targets (26 drugs) | PARTIAL | yes | LEDGER:97 (V18) |
| B16_beyond_mutation | inferred-FLT3-dep beyond ITD | meta β +7.6 (p 8e-11); ITD-WT ρ +0.22 (p 1.5e-15) | POSITIVE (BeatAML only) | yes | LEDGER:98 (V19) |
| B17_clinical_outcome | ex-vivo→survival (Cox) | interaction HR 0.89 (p 0.56); null | NULL | yes | LEDGER:205 (B17); ENG §2.8 |
| B18_target_specificity | target-specific double-dissociation | diag ρ +0.19 vs off +0.07 (shuffle perm p <1e-4) | POSITIVE (BeatAML only) | yes | LEDGER:99 (V20) |
| B19_lineage_leakage | lineage-leakage control | AML-removed β +7.4 (p 2e-10); ITD-WT ρ +0.23 | VALIDATED (control) | yes | LEDGER:98 (V19) |
| B20_fimm_external_replication | FIMM external replication | inferred-FLT3-dep pooled ρ +0.05 (p 0.08); adds β −0.02 (p 0.92); known FLT3-mut biology replicates | NEGATIVE | yes | LEDGER:98–99 (V19/V20 DOWNGRADED); ENG §2.8 |
| B21_selectivity_crosscohort | FLT3-selective inhibitors across cohorts | per-drug unstable (sorafenib flips sign); selectivity doesn't separate | NEGATIVE | yes | ENG §2.8; LEDGER:99 (V20) |
| B22_modality_ceiling | proteomics vs RNA | proteomics 0.328 vs RNA 0.419 (p 1e-43); combined ≤ RNA | NEGATIVE (ceiling general) | yes | LEDGER:100 (V21); ENG §2.1 |
| B23_functional_ceiling | measured CRISPR-dep vs RNA | dep 0.459 vs RNA 0.487; +0.019 integration; own-target-excluded 0.504 vs 0.514 (p 0.06) | NEGATIVE (target-tautological) | yes | LEDGER:101 (V22); ENG §2.1 |
| B24_synergy_generalization | synergy on unseen known-drug combos | leave-combo-out ρ +0.61 vs baseline +0.47; class AUROC 0.80 | POSITIVE | yes | LEDGER:102 (V23); ENG §2.9 |
| B25_synergy_scaleup | novel-drug synergy on DrugComb | leave-drug-out ρ 0.25→0.025 (collapses); known-combo replicates Δ+0.094 | NEGATIVE (novel) / PASS (known) | yes | LEDGER:102 (V23); WEAKNESS_AUDIT (B24→B25) |
| B28_synergy_crosscorpus | cross-corpus external replication | DrugComb→O'Neil ρ +0.38 (CI [0.36,0.39]), 2.5× retrieval, novel-combo +0.44 | VALIDATED (replicated) | na | ENG §2.9 |
| B29_synergy_conformal_coverage | conformal interval calibration | 90%→89.8/90.5%, 80%→79.5/80.6% (O'Neil/DrugComb) | PASS (calibrated) | yes | ENG §2.9 |
| synergy_module_validation | shipped SynergyRanker tool | (tool wrapping B24–B29; calibrated conformal) | not in ledger | na | dir only; = ENG §2.9 tool |
| engine_v1_validation | shipped cancer engine embodies V10 | markers from B5; combination reproduces | VALIDATED | yes | LEDGER:90 (V11) |
| track1_power | prospective functional-precision power | (prospective design, not run) | not in ledger | na | dir only (0 mentions) |
| DEPEND1_functional_dependency | functional-dependency target-ID (host-embedded) | recovery@10 0.80 (null 6e-4), held-out lines 0.80, expr→dep +0.201 (p 0.003) | PASS | yes | LEDGER:77 |
| F3CLIN1_dependency_patient_relevance | dependency→patient-driver relevance | OR 2.55 (p 3.4e-26); survives study-bias (MH OR 2.72) | PASS (target-relevance only) | yes | LEDGER:71 |
| TRANSFER1_labelfree_zeroscreen | label-free dependency to zero-screen organism | conserved-core OR 3.82 (p 3e-5); selective OR 0.90 (p 0.78 = chance); 28% coverage | NEGATIVE (do not un-gate) | yes | LEDGER:66 |
| B12/B13 shared → V15/V16 | (see B12/B13 above) | — | — | — | — |

## Arm 6 — Durability / resistance-robustness

| Dir / ID | Objective | Headline result (numbers) | Verdict | Repro? | Source |
|---|---|---|---|---|---|
| AMR1_resistance_liability | whole-protein resistance liability | AUROC 0.556 (MWU p 0.74); ablation 0.472 | NEGATIVE | yes | LEDGER:43 |
| DYNAMICS1_contact_residue_durability | contact-residue mutational tolerance | AUROC 0.839 (MWU p 0.029, n=15); n-fragile | PASS (fragile) | yes | LEDGER:51 |
| DYNAMICS2_durability_scaleup | firm-up at larger n | AUROC 0.827 (p 0.0051, n=26); p not robust to substrate confound | FIRMED (AUROC~0.83) | yes | LEDGER:52 |
| DYNAMICS3_predicted_pocket_durability | durability from apo predicted pocket | ρ 0.714 (p 4e-4); G2 AUROC 0.80 | QUALIFIED PASS | yes | LEDGER:54 |
| DYNAMICS4_functional_site_durability | durability from UniProt functional-site residues | ρ 0.687 (p 6e-4), passes ≥0.5 but doesn't beat fpocket 0.714; +0.10 bar FAIL; G2 p 0.060 | PARTIAL (non-improvement) | yes | LEDGER:54 |
| DYNAMICS5_resistance_site_entropy | entropy at resistance sites | — | not in ledger | na | dir only (0 mentions) |
| DURABLETARGETS1_durability_augmented_scorecard | durability-augmented target scorecard | 18/19 assignable; 9/19; n=26 | PASS | yes | LEDGER:53 |
| SYNLETH1_resistance_robust | monotherapy-robust vs isozyme-buffered | 8/9 broad-spectrum targets bypass-robust; 11/15; sample combos jointly lethal | PASS | yes | LEDGER:19 |
| SYNLETH2_heldout_native | held-out native SL verification | 8/8; 6/10; double-deletion verified | PASS | yes | LEDGER:20 |

## Arm 7 — Generalization / hardening (across disease classes)

| Dir / ID | Objective | Headline result (numbers) | Verdict | Repro? | Source |
|---|---|---|---|---|---|
| GENERALIZE1_emerging_virus | virus sequence homology to drug targets | 0/30 SARS-CoV-2 proteins | NEGATIVE | yes | LEDGER:56 |
| GENERALIZE3_viral_structural_blind | blind structural target-prioritization (virus) | 21/30 structural coverage; Mpro/RdRp correct class (TM 0.46–0.47) | PASS | yes | LEDGER:58 |
| GENERALIZE4_fungal_fba | FBA-ess to model eukaryote (S.cerevisiae) | OR 4.65 (p 1.6e-10, rec 0.32, AUROC 0.61) | PASS | yes | LEDGER:60 |
| GENERALIZE5_parasite_fba | FBA-ess to Plasmodium | OR 2.47 (rec 0.20, AUROC 0.56) | FAIL | yes | LEDGER:59 |
| HARDENV1_virus_multi | harden virus→structure to n=5 | 7/9 drug targets recover correct class | PASS | yes | LEDGER:67 |
| HARDENP1_parasite_multi | harden parasite (Toxoplasma) | OR 14.10 (rec 0.51, AUROC 0.725) — corrects "host-embedded fails" | PASS | yes | LEDGER:68 |
| HARDENF1_fungal_multi | real fungal pathogen (C.albicans) | OR 13.93 (p 0.004, prec 0.86, rec 0.025) | PASS | yes | LEDGER:69 |
| HOSTCTX1_eflux_malaria | E-Flux expression-context rescue (Plasmodium) | essential set byte-identical; OR 2.47 | NEGATIVE | yes | LEDGER:61 |
| HOSTCTX2_exchange_curation | host-medium exchange curation | recall 0.20→0.30 but OR flat | NEGATIVE | yes | LEDGER:62 |
| PARARESOLVE1_parasite_confound | Plasmodium GEM-swap (6 models) | OR spans 0.86–3.07 (iAM-Pf480 passes); salvage-mechanism falsified | PARTIAL | yes | LEDGER:72 |
| PARARESOLVE2_screentech_probe | 3rd-technology screen probe | Bushell OR 3.67 PASS vs Zhang FAIL; recall ~0.2 invariant | PARTIAL | yes | LEDGER:73 |
| FOLD1_structural_targetid | structural target-ID (Foldseek) | AUROC 0.69; 4/4; partial nulls | PARTIAL | yes | LEDGER:168 |
| FOLD2_substrate_structural_rescue | structural rescue / fold census | 17/24; 16/65; promiscuity null | NULL/PARTIAL | yes | LEDGER:169 |
| GENERALIZE2 (no own dir) | structure recovers folds sequence missed | confirmatory PASS (n=1) | PASS | yes | LEDGER:57 |

## Arm 8 — Governance / engine / composite / human-arm expansion

| Dir / ID | Objective | Headline result (numbers) | Verdict | Repro? | Source |
|---|---|---|---|---|---|
| CONFORMAL1_ood_abstention | distribution-free coverage on novel organism | marginal 0.90 in-dist/0.87 OOD (driven by no-homolog abstain); essential-class coverage 0.0 in-dist; OOD drops 0.94→0.55 | CAUTIONARY | yes | LEDGER:47 |
| COMPOSITE1_explicit_router | biology-class-aware abstaining router v1 | correct abstention (integrity) | PASS | yes | LEDGER:64 |
| COMPOSITE2_wire_dependency | wire DEPEND1 into router | transfer-condition-precise un-gating | PASS | yes | LEDGER:65 |
| COMPOSITE3_hostdep_refine | host-dependent FBA refinement | per HARDENP1 correction | PASS | yes | LEDGER:70 |
| COMPOSITE4_expanded_integration | additive integration of human arms + drift fix | PASS with some FAIL flags (0/11 infeasible) | PASS | yes | LEDGER:170 |
| CAPSTONE1_composite_demonstration | whole composite across reachable classes | decided end-to-end as one system; per-class validated signals fire/abstain | PASS | yes | LEDGER:74 |
| CAPSTONE2_expanded_integration | fully-expanded autonomous composite (frozen gate) | G1–G4 PASS (routing/abstention/intervention/verdict-stability) | PASS | yes | LEDGER:45 |
| ROUTERAUTO1_autonomous_routing | autonomous class detection + routing | OR 4.23; 19/19, 6/6; FAIL/PASS mix; closed | PASS | yes | LEDGER:38 |
| DARK1_dark_proteome_boundary | dark-proteome abstention boundary | 22/22 abstain; 16/20; 7/22 | PASS (abstains) | yes | LEDGER:33 |
| MODALITY1_intervention_modality | fail-safe cross-class intervention modality | 0 infeasible modality recs | PASS | na | LEDGER:41 |
| CRISPRIDESIGN1_wetlab_ready | wet-lab-ready CRISPRi design | design PASS (p<0.01) | PASS | yes | LEDGER:36 |
| MENDEL1_mendelian_disease_arm | Mendelian/monogenic intervention-mode | AUROC 0.636; 24/28; some nulls | PARTIAL | yes | LEDGER:39 |
| GENETICS1_complex_disease_genetics | complex-disease genetics arm | OR 2.26 (p<0.01); 27/27 | PASS | yes | LEDGER:42 |
| PHENO1_phenotype_to_gene | phenotype→gene mapping | n=3034; PASS (p<0.01) | PASS | yes | LEDGER:44 |
| EXPDESIGN1_experiment_prioritization | experiment prioritization | N=4195; PASS/CLOSED | PASS | yes | LEDGER:46 |
| SIL1_conformal_self_improving_loop | conformal-gated self-improving loop | median ΔAUROC +0.011 (6/6); gated acc 0.886 vs 0.772; shuffled −0.043 | POSITIVE | yes | LEDGER:147 |
| SIL2_loop_under_shift | loop under distribution shift | near-domain only; novel-chem coin-flip (wash) | NEGATIVE (bounded) | yes | LEDGER:148 |
| SUBSTRATE1_engine_demo | engine substrate demo | 33/94; 41/41; PASS | VALIDATED | yes | LEDGER:160 |
| SUBSTRATE2_molecule_stage | molecule-ranking substrate | 42/42; PASS | VALIDATED | yes | LEDGER:161 |
| SUBSTRATE3_continuous_absorption | continuous-absorption guardrail | VALIDATED | VALIDATED | yes | LEDGER:162 |
| SUBSTRATE4_pandemic_stresstest | pandemic stress-test | 3/3; 17/17; fail-flag | VALIDATED | yes | LEDGER:163 |
| SUBSTRATE5_human_disease | human-disease substrate | popularity-confounded/near-random (0/3); 43/43 | POSITIVE (bounded) | yes | LEDGER:164 |

---

## Summary counts
- **Total experiment directories enumerated:** 169
- **Directories with NO ledger row ("not in ledger"):** 6 — `AFFINITY_IPTM1_structure_confidence`, `PLMSTRUCT1_structure_aware_plm_nonmetabolic`, `DYNAMICS5_resistance_site_entropy`, `track1_power`, `BROADSPEC_predictions`, `synergy_module_validation`.
- **Note:** cancer dirs `B1`–`B25` have no standalone LEDGER row of their own ID (they are recorded under the `V`-series rows, LEDGER:78–102, and detailed in ENG §2.1–2.9); `B8`, `B10`, `B11`, `B21`, `B28`, `B29` are documented in the ENG manuscript / audit files rather than as dedicated `B`-ID ledger rows. `EXPVAL_predictions` and `VALIDATE_essentiality` are folded into the `VAL-ESS*` rows (LEDGER:10–15); `engine_v1_validation` = `V11` (LEDGER:90). These are cited to their mapped rows above, not counted as "not in ledger".
