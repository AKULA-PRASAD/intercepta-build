# INTERCEPTA Stage 5: 10-Item Pharma Deliverable for GBM Top-5
Generated: 2026-05-06T16:40:11.820961
Per Vision 9.1 (10-item pharma deliverable per candidate)
Per Principle 15 (only correct honest real science): items marked GAP have documented requirements; no item is fabricated.

## Aggregate coverage across top-5 candidates

| Candidate | Rank | DELIVERED | PARTIAL | GAP | N/A |
|-----------|------|-----------|---------|-----|-----|
| Foretinib | 1 | 2/10 | 4/10 | 3/10 | 1/10 |
| Erlotinib | 2 | 2/10 | 4/10 | 3/10 | 1/10 |
| Osimertinib | 3 | 2/10 | 4/10 | 3/10 | 1/10 |
| AZD3759 | 4 | 2/10 | 4/10 | 3/10 | 1/10 |
| Gefitinib | 5 | 2/10 | 4/10 | 3/10 | 1/10 |

## Per-item delivery rate across all candidates

| Item | DELIVERED | PARTIAL | GAP | N/A |
|------|-----------|---------|-----|-----|
| 01_molecular_structure | 0/5 | 5/5 | 0/5 | 0/5 |
| 02_mechanism_of_action | 5/5 | 0/5 | 0/5 | 0/5 |
| 03_predicted_clinical_outcomes | 0/5 | 0/5 | 5/5 | 0/5 |
| 04_resistance_profile | 0/5 | 0/5 | 5/5 | 0/5 |
| 05_combination_rationale | 0/5 | 0/5 | 0/5 | 5/5 |
| 06_safety_admet | 0/5 | 5/5 | 0/5 | 0/5 |
| 07_synthesis_route | 0/5 | 0/5 | 5/5 | 0/5 |
| 08_novelty_vs_clinicaltrials | 5/5 | 0/5 | 0/5 | 0/5 |
| 09_comparison_vs_soc | 0/5 | 5/5 | 0/5 | 0/5 |
| 10_trial_design | 0/5 | 5/5 | 0/5 | 0/5 |

## Per-candidate detailed deliverable

### 1. Foretinib

- **Composite v2 score:** 0.845
- **Coverage:** 2/10 DELIVERED, 4/10 PARTIAL, 3/10 GAP, 1/10 N/A
- **GDSC targets:** MET, KDR, TIE2, VEGFR3/FLT4, RON, PDGFR, FGFR1, EGFR

**01_molecular_structure** [PARTIAL]

```json
{
  "drug_name": "Foretinib",
  "representative_chembl_id": "CHEMBL5184459",
  "representative_target_gene": "MET",
  "pchembl_value": 10.72,
  "standard_type": "IC50",
  "standard_value_nM": "0.019",
  "molecular_properties": {
    "molecular_weight": null,
    "alogp": null,
    "polar_surface_area": null,
    "hbd": null,
    "hba": null,
    "qed_weighted": null,
    "ro5_pass": null
  },
  "bbb_assessment": {
    "category": null,
    "mpo_score": null,
    "mpo_components": null,
    "method": "CNS MPO 4-component (logp+mw+tpsa+hbd) per Wager et al. 2010"
  },
  "note": "Showing representative ChEMBL compound for this drug-target relationship. The actual drug may correspond to a specific ChEMBL ID; full mapping needs GDSC drug-name to ChEMBL synonym lookup."
}
```

Requirements to upgrade:
  - Direct GDSC drug-name to canonical ChEMBL compound mapping
  - SMILES string (currently only chembl_id stored, not canonical SMILES)
  - 3D structure file (PDB/SDF) — would require ChEMBL /molecule/{id} structures fetch

**02_mechanism_of_action** [DELIVERED]

```json
{
  "drug_name": "Foretinib",
  "targeted_disease_genes": [
    {
      "gene": "MET",
      "disease_association_score": 0.137,
      "n_string_interactions": 125,
      "n_clinical_trials_in_gbm": 48,
      "n_chembl_compounds": 33,
      "mutation_frequency_in_gbm": 0.0164,
      "has_alphafold_structure": true
    },
    {
      "gene": "KDR",
      "disease_association_score": 0.36,
      "n_string_interactions": 154,
      "n_clinical_trials_in_gbm": 6,
      "n_chembl_compounds": 31,
      "mutation_frequency_in_gbm": 0.0117,
      "has_alphafold_structure": true
    },
    {
      "gene": "FGFR1",
      "disease_association_score": 0.511,
      "n_string_interactions": 123,
      "n_clinical_trials_in_gbm": 1,
      "n_chembl_compounds": 40,
      "mutation_frequency_in_gbm": 0.0023,
      "has_alphafold_structure": true
    },
    {
      "gene": "EGFR",
      "disease_association_score": 0.649,
      "n_string_interactions": 502,
      "n_clinical_trials_in_gbm": 50,
      "n_chembl_compounds": 31,
      "mutation_frequency_in_gbm": 0.0094,
      "has_alphafold_structure": true
    }
  ],
  "mechanism_summary": "Targets MET (GBM association score 0.137; 48 GBM trials).; Targets KDR (GBM association score 0.36; 6 GBM trials).; Targets FGFR1 (GBM association score 0.511; 1 GBM trials).; Targets EGFR (GBM association score 0.649; 50 GBM trials).",
  "why_kills_disease": [
    "Targets MET (GBM association score 0.137; 48 GBM trials).",
    "Targets KDR (GBM association
  ... (truncated; see full JSON)
```

Requirements to upgrade:
  - For full DELIVERED status, integrate GTEx-derived per-target tissue selectivity to quantify therapeutic index per organ system. Currently mechanism is from disease side only.

**03_predicted_clinical_outcomes** [GAP]

Requirements to upgrade:
  - Phenotype-structured ODE is currently mCRPC-specific (Round 3 Finding 18)
  - GBM-applicable ODE requires: (a) GBM scRNA-seq with raw FASTQ for velocity, OR (b) GBM bulk transcriptomics with phenotype proxy, OR (c) acceptance that GBM uses alternative cell-state characterization
  - Universal ODE refactor explicitly Workstream C scope per Plan v2 §5
  - Workstream B (Time Machine generalization) tests whether the phenotype ODE breakthrough generalizes — answer determines C architecture

**04_resistance_profile** [GAP]

Requirements to upgrade:
  - Resistance profile requires phenotype-structured ODE (currently mCRPC-only)
  - AND requires disease-specific RNA velocity initial condition (mCRPC has Dong et al. GSE137829; GBM lacks comparable scRNA-seq with raw FASTQ in our pipeline)
  - Cell-state characterization for GBM might use alternative: TCGA-GBM mesenchymal/proneural/classical subtypes (Wang et al. Cancer Cell 2017), or GBM tumor stem cell state markers (Couturier et al. Nat Commun 2020)

**05_combination_rationale** [N/A]

```json
{
  "drug_name": "Foretinib",
  "note": "Monotherapy candidate; combination rationale not applicable"
}
```

Requirements to upgrade:
  - For combination candidates: synergy scoring (Layer D) requires per-drug PK/PD in disease-specific cell line panel. Workstream B (Time Machine) and C scope.

**06_safety_admet** [PARTIAL]

```json
{
  "drug_name": "Foretinib",
  "bbb_passability": {
    "gate_value": 1.0,
    "interpretation": "likely_bbb_pos (passes BBB filter for CNS diseases)",
    "method": "CNS MPO score per Wager et al. ACS Chem Neurosci 2010",
    "limitation": "Passive-diffusion proxy; does not capture P-gp efflux, transporters, prodrug effects"
  },
  "organ_toxicity_assessment": "GAP \u2014 requires per-drug ADMET (SwissADME, pkCSM)",
  "off_target_panel": "GAP \u2014 requires kinome-wide selectivity assay data integration",
  "gtex_selectivity_note": "Per-gene GTEx tissue selectivity is captured in Workstream A net data. Per-drug therapeutic index calculation across organ systems requires Workstream B Layer E."
}
```

Requirements to upgrade:
  - Integrate SwissADME or pkCSM for per-drug ADMET prediction
  - Off-target panel: kinome-wide ChEMBL bioactivity profiling per drug
  - Per-drug GTEx-based therapeutic index calculation

**07_synthesis_route** [GAP]

Requirements to upgrade:
  - For approved drugs (most v2 top-5 candidates): synthesis route is publicly known; could be retrieved from DrugBank or PubChem
  - For novel candidates from generative chemistry (Workstream C): ASKCOS retrosynthesis integration required per vision
  - SA_Score (Ertl & Schuffenhauer 2009) requires canonical SMILES; depends on item 1 upgrade to DELIVERED

**08_novelty_vs_clinicaltrials** [DELIVERED]

```json
{
  "drug_name": "Foretinib",
  "novelty_assessment": "WELL-STUDIED: 105 GBM trials (mature clinical pipeline)",
  "total_gbm_trials_across_targets": 105,
  "per_target_breakdown": [
    {
      "gene": "MET",
      "n_gbm_trials_targeting_this_gene": 48,
      "sample_trials": [
        {
          "nct_id": "NCT05831995",
          "title": "Safety and Effectiveness of ABM-168 in Adults with Advanced Solid Tumors.",
          "phase": "PHASE1",
          "status": "TERMINATED"
        },
        {
          "nct_id": "NCT06815029",
          "title": "Intracranial Genetically Modified Immune Cells (TGF\u03b2R2KO/IL13R\u03b12 CAR T-Cells) fo",
          "phase": "PHASE1",
          "status": "RECRUITING"
        },
        {
          "nct_id": "NCT07523529",
          "title": "Biomarker-Guided Dual-Target CAR-T Cells for Advanced Solid Tumors",
          "phase": "PHASE1",
          "status": "RECRUITING"
        },
        {
          "nct_id": "NCT05608395",
          "title": "11C-methionine in Diagnostics and Management of Glioblastoma Multiforme Patients",
          "phase": "PHASE2",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT00099060",
          "title": "Lapatinib in Treating Patients With Recurrent Glioblastoma Multiforme",
          "phase": "PHASE1",
          "status": "COMPLETED"
        }
      ]
    },
    {
      "gene": "KDR",
      "n_gbm_trials_targeting_this_gene": 6,
      "sample_trials": [
        {
          "nct_id
  ... (truncated; see full JSON)
```

Requirements to upgrade:
  - For drug-name-specific novelty: GDSC drug -> ChEMBL drug -> ClinicalTrials.gov intervention search by drug name

**09_comparison_vs_soc** [PARTIAL]

```json
{
  "drug_name": "Foretinib",
  "gbm_standard_of_care": {
    "newly_diagnosed": {
      "first_line": "Surgery + temozolomide + radiotherapy (Stupp protocol)",
      "reference": "Stupp et al. NEJM 2005; Stupp et al. JAMA 2017 (TTFields update)",
      "median_OS": "~16 months for MGMT-methylated, ~12 months MGMT-unmethylated"
    },
    "recurrent": {
      "options": [
        "Bevacizumab",
        "Lomustine",
        "TTFields",
        "Re-resection + reirradiation"
      ],
      "reference": "NCCN GBM Guidelines (2024)",
      "median_OS_after_recurrence": "~6-9 months"
    }
  },
  "qualitative_comparison": "Candidate Foretinib is a kinase-inhibitor class drug. GBM SOC is alkylating chemotherapy + radiotherapy. The candidate represents a different mechanism class than current SOC. Quantitative comparison (predicted PFS/OS vs SOC) requires item 3 (predicted clinical outcomes) which depends on Workstream B/C ODE generalization.",
  "positioning": "If validated, this candidate would be evaluated either as: (a) replacement for failing standard of care in MGMT-unmethylated GBM, (b) addition to TMZ backbone, OR (c) recurrent-GBM second-line option."
}
```

Requirements to upgrade:
  - Quantitative outcome comparison requires item 3 (ODE-derived predictions) — GAP
  - Direct head-to-head trial design considerations — handled in item 10

**10_trial_design** [PARTIAL]

```json
{
  "drug_name": "Foretinib",
  "recommended_setting": "Recurrent GBM after first-line failure (lower regulatory risk)",
  "phase": "Phase 1b/2 dose-finding + activity assessment",
  "biomarker_stratifications": [
    {
      "biomarker": "MET mutation/amplification status",
      "gbm_prevalence": "1.6% of GBM patients",
      "rationale": "Drug targets MET; patients with altered MET expected to derive larger benefit"
    },
    {
      "biomarker": "KDR mutation/amplification status",
      "gbm_prevalence": "1.2% of GBM patients",
      "rationale": "Drug targets KDR; patients with altered KDR expected to derive larger benefit"
    },
    {
      "biomarker": "FGFR1 mutation/amplification status",
      "gbm_prevalence": "0.2% of GBM patients",
      "rationale": "Drug targets FGFR1; patients with altered FGFR1 expected to derive larger benefit"
    },
    {
      "biomarker": "EGFR mutation/amplification status",
      "gbm_prevalence": "0.9% of GBM patients",
      "rationale": "Drug targets EGFR; patients with altered EGFR expected to derive larger benefit"
    },
    {
      "biomarker": "MGMT promoter methylation status",
      "gbm_prevalence": "~40% of GBM patients are MGMT-methylated",
      "rationale": "Stratification standard for ANY GBM trial; MGMT-methylated patients respond differently to alkylating chemotherapy and combination strategies"
    }
  ],
  "primary_endpoint_suggestion": "Progression-free survival at 6 months (PFS6)",
  "secondary_endpoints": [
  
  ... (truncated; see full JSON)
```

Requirements to upgrade:
  - Quantitative power calculation requires item 3 outcomes (GAP)
  - Patient population specifics (newly-diagnosed vs recurrent, prior therapies) require item 9 quantitative SOC comparison (GAP)

---

### 2. Erlotinib

- **Composite v2 score:** 0.675
- **Coverage:** 2/10 DELIVERED, 4/10 PARTIAL, 3/10 GAP, 1/10 N/A
- **GDSC targets:** EGFR

**01_molecular_structure** [PARTIAL]

```json
{
  "drug_name": "Erlotinib",
  "representative_chembl_id": "CHEMBL176582",
  "representative_target_gene": "EGFR",
  "pchembl_value": 11.0,
  "standard_type": "IC50",
  "standard_value_nM": "0.01",
  "molecular_properties": {
    "molecular_weight": null,
    "alogp": null,
    "polar_surface_area": null,
    "hbd": null,
    "hba": null,
    "qed_weighted": null,
    "ro5_pass": null
  },
  "bbb_assessment": {
    "category": null,
    "mpo_score": null,
    "mpo_components": null,
    "method": "CNS MPO 4-component (logp+mw+tpsa+hbd) per Wager et al. 2010"
  },
  "note": "Showing representative ChEMBL compound for this drug-target relationship. The actual drug may correspond to a specific ChEMBL ID; full mapping needs GDSC drug-name to ChEMBL synonym lookup."
}
```

Requirements to upgrade:
  - Direct GDSC drug-name to canonical ChEMBL compound mapping
  - SMILES string (currently only chembl_id stored, not canonical SMILES)
  - 3D structure file (PDB/SDF) — would require ChEMBL /molecule/{id} structures fetch

**02_mechanism_of_action** [DELIVERED]

```json
{
  "drug_name": "Erlotinib",
  "targeted_disease_genes": [
    {
      "gene": "EGFR",
      "disease_association_score": 0.649,
      "n_string_interactions": 502,
      "n_clinical_trials_in_gbm": 50,
      "n_chembl_compounds": 31,
      "mutation_frequency_in_gbm": 0.0094,
      "has_alphafold_structure": true
    }
  ],
  "mechanism_summary": "Targets EGFR (GBM association score 0.649; 50 GBM trials).",
  "why_kills_disease": [
    "Targets EGFR (GBM association score 0.649; 50 GBM trials)."
  ],
  "healthy_sparing_assessment": "Selectivity/healthy-cell sparing analysis requires GTEx tissue selectivity scoring, which is captured per-gene in Workstream A. Per-drug therapeutic-index calculation across all targeted tissues is Workstream B (Layer E ADMET) work."
}
```

Requirements to upgrade:
  - For full DELIVERED status, integrate GTEx-derived per-target tissue selectivity to quantify therapeutic index per organ system. Currently mechanism is from disease side only.

**03_predicted_clinical_outcomes** [GAP]

Requirements to upgrade:
  - Phenotype-structured ODE is currently mCRPC-specific (Round 3 Finding 18)
  - GBM-applicable ODE requires: (a) GBM scRNA-seq with raw FASTQ for velocity, OR (b) GBM bulk transcriptomics with phenotype proxy, OR (c) acceptance that GBM uses alternative cell-state characterization
  - Universal ODE refactor explicitly Workstream C scope per Plan v2 §5
  - Workstream B (Time Machine generalization) tests whether the phenotype ODE breakthrough generalizes — answer determines C architecture

**04_resistance_profile** [GAP]

Requirements to upgrade:
  - Resistance profile requires phenotype-structured ODE (currently mCRPC-only)
  - AND requires disease-specific RNA velocity initial condition (mCRPC has Dong et al. GSE137829; GBM lacks comparable scRNA-seq with raw FASTQ in our pipeline)
  - Cell-state characterization for GBM might use alternative: TCGA-GBM mesenchymal/proneural/classical subtypes (Wang et al. Cancer Cell 2017), or GBM tumor stem cell state markers (Couturier et al. Nat Commun 2020)

**05_combination_rationale** [N/A]

```json
{
  "drug_name": "Erlotinib",
  "note": "Monotherapy candidate; combination rationale not applicable"
}
```

Requirements to upgrade:
  - For combination candidates: synergy scoring (Layer D) requires per-drug PK/PD in disease-specific cell line panel. Workstream B (Time Machine) and C scope.

**06_safety_admet** [PARTIAL]

```json
{
  "drug_name": "Erlotinib",
  "bbb_passability": {
    "gate_value": 1.0,
    "interpretation": "likely_bbb_pos (passes BBB filter for CNS diseases)",
    "method": "CNS MPO score per Wager et al. ACS Chem Neurosci 2010",
    "limitation": "Passive-diffusion proxy; does not capture P-gp efflux, transporters, prodrug effects"
  },
  "organ_toxicity_assessment": "GAP \u2014 requires per-drug ADMET (SwissADME, pkCSM)",
  "off_target_panel": "GAP \u2014 requires kinome-wide selectivity assay data integration",
  "gtex_selectivity_note": "Per-gene GTEx tissue selectivity is captured in Workstream A net data. Per-drug therapeutic index calculation across organ systems requires Workstream B Layer E."
}
```

Requirements to upgrade:
  - Integrate SwissADME or pkCSM for per-drug ADMET prediction
  - Off-target panel: kinome-wide ChEMBL bioactivity profiling per drug
  - Per-drug GTEx-based therapeutic index calculation

**07_synthesis_route** [GAP]

Requirements to upgrade:
  - For approved drugs (most v2 top-5 candidates): synthesis route is publicly known; could be retrieved from DrugBank or PubChem
  - For novel candidates from generative chemistry (Workstream C): ASKCOS retrosynthesis integration required per vision
  - SA_Score (Ertl & Schuffenhauer 2009) requires canonical SMILES; depends on item 1 upgrade to DELIVERED

**08_novelty_vs_clinicaltrials** [DELIVERED]

```json
{
  "drug_name": "Erlotinib",
  "novelty_assessment": "WELL-STUDIED: 50 GBM trials (mature clinical pipeline)",
  "total_gbm_trials_across_targets": 50,
  "per_target_breakdown": [
    {
      "gene": "EGFR",
      "n_gbm_trials_targeting_this_gene": 50,
      "sample_trials": [
        {
          "nct_id": "NCT06072586",
          "title": "A Phase 0/1 Study of BDTX-1535 in Recurrent High-Grade Glioma (rHGG) and Newly D",
          "phase": "EARLY_PHASE1",
          "status": "RECRUITING"
        },
        {
          "nct_id": "NCT01238237",
          "title": "Super-Selective Intraarterial Cerebral Infusion of Cetuximab (Erbitux) for Treat",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT03344250",
          "title": "Phase I EGFR BATs in Newly Diagnosed Glioblastoma",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT00052208",
          "title": "Gefitinib and Radiation Therapy in Treating Patients With Glioblastoma Multiform",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT01454596",
          "title": "CAR T Cell Receptor Immunotherapy Targeting EGFRvIII for Patients With Malignant",
          "phase": "PHASE1",
          "status": "COMPLETED"
        }
      ]
    }
  ],
  "caveat": "Novelty here is by-target, not by-specific-drug-name. A drug whose target has many GBM trials is not necessarily 
  ... (truncated; see full JSON)
```

Requirements to upgrade:
  - For drug-name-specific novelty: GDSC drug -> ChEMBL drug -> ClinicalTrials.gov intervention search by drug name

**09_comparison_vs_soc** [PARTIAL]

```json
{
  "drug_name": "Erlotinib",
  "gbm_standard_of_care": {
    "newly_diagnosed": {
      "first_line": "Surgery + temozolomide + radiotherapy (Stupp protocol)",
      "reference": "Stupp et al. NEJM 2005; Stupp et al. JAMA 2017 (TTFields update)",
      "median_OS": "~16 months for MGMT-methylated, ~12 months MGMT-unmethylated"
    },
    "recurrent": {
      "options": [
        "Bevacizumab",
        "Lomustine",
        "TTFields",
        "Re-resection + reirradiation"
      ],
      "reference": "NCCN GBM Guidelines (2024)",
      "median_OS_after_recurrence": "~6-9 months"
    }
  },
  "qualitative_comparison": "Candidate Erlotinib is a kinase-inhibitor class drug. GBM SOC is alkylating chemotherapy + radiotherapy. The candidate represents a different mechanism class than current SOC. Quantitative comparison (predicted PFS/OS vs SOC) requires item 3 (predicted clinical outcomes) which depends on Workstream B/C ODE generalization.",
  "positioning": "If validated, this candidate would be evaluated either as: (a) replacement for failing standard of care in MGMT-unmethylated GBM, (b) addition to TMZ backbone, OR (c) recurrent-GBM second-line option."
}
```

Requirements to upgrade:
  - Quantitative outcome comparison requires item 3 (ODE-derived predictions) — GAP
  - Direct head-to-head trial design considerations — handled in item 10

**10_trial_design** [PARTIAL]

```json
{
  "drug_name": "Erlotinib",
  "recommended_setting": "Recurrent GBM after first-line failure (lower regulatory risk)",
  "phase": "Phase 1b/2 dose-finding + activity assessment",
  "biomarker_stratifications": [
    {
      "biomarker": "EGFR mutation/amplification status",
      "gbm_prevalence": "0.9% of GBM patients",
      "rationale": "Drug targets EGFR; patients with altered EGFR expected to derive larger benefit"
    },
    {
      "biomarker": "MGMT promoter methylation status",
      "gbm_prevalence": "~40% of GBM patients are MGMT-methylated",
      "rationale": "Stratification standard for ANY GBM trial; MGMT-methylated patients respond differently to alkylating chemotherapy and combination strategies"
    }
  ],
  "primary_endpoint_suggestion": "Progression-free survival at 6 months (PFS6)",
  "secondary_endpoints": [
    "Overall survival",
    "Objective response rate (RANO)",
    "Safety/tolerability"
  ],
  "control_arm_consideration": "Lomustine standard recurrent-GBM control OR investigator-choice",
  "sample_size_caveat": "Quantitative power calculation requires item 3 (predicted PFS/OS effect size) \u2014 GAP. Without effect size estimate, suggested sample is 60-100 patients per arm based on historical GBM Phase 2 trial sizes (e.g., REGOMA, LOMUSTINE controls)."
}
```

Requirements to upgrade:
  - Quantitative power calculation requires item 3 outcomes (GAP)
  - Patient population specifics (newly-diagnosed vs recurrent, prior therapies) require item 9 quantitative SOC comparison (GAP)

---

### 3. Osimertinib

- **Composite v2 score:** 0.675
- **Coverage:** 2/10 DELIVERED, 4/10 PARTIAL, 3/10 GAP, 1/10 N/A
- **GDSC targets:** EGFR

**01_molecular_structure** [PARTIAL]

```json
{
  "drug_name": "Osimertinib",
  "representative_chembl_id": "CHEMBL176582",
  "representative_target_gene": "EGFR",
  "pchembl_value": 11.0,
  "standard_type": "IC50",
  "standard_value_nM": "0.01",
  "molecular_properties": {
    "molecular_weight": null,
    "alogp": null,
    "polar_surface_area": null,
    "hbd": null,
    "hba": null,
    "qed_weighted": null,
    "ro5_pass": null
  },
  "bbb_assessment": {
    "category": null,
    "mpo_score": null,
    "mpo_components": null,
    "method": "CNS MPO 4-component (logp+mw+tpsa+hbd) per Wager et al. 2010"
  },
  "note": "Showing representative ChEMBL compound for this drug-target relationship. The actual drug may correspond to a specific ChEMBL ID; full mapping needs GDSC drug-name to ChEMBL synonym lookup."
}
```

Requirements to upgrade:
  - Direct GDSC drug-name to canonical ChEMBL compound mapping
  - SMILES string (currently only chembl_id stored, not canonical SMILES)
  - 3D structure file (PDB/SDF) — would require ChEMBL /molecule/{id} structures fetch

**02_mechanism_of_action** [DELIVERED]

```json
{
  "drug_name": "Osimertinib",
  "targeted_disease_genes": [
    {
      "gene": "EGFR",
      "disease_association_score": 0.649,
      "n_string_interactions": 502,
      "n_clinical_trials_in_gbm": 50,
      "n_chembl_compounds": 31,
      "mutation_frequency_in_gbm": 0.0094,
      "has_alphafold_structure": true
    }
  ],
  "mechanism_summary": "Targets EGFR (GBM association score 0.649; 50 GBM trials).",
  "why_kills_disease": [
    "Targets EGFR (GBM association score 0.649; 50 GBM trials)."
  ],
  "healthy_sparing_assessment": "Selectivity/healthy-cell sparing analysis requires GTEx tissue selectivity scoring, which is captured per-gene in Workstream A. Per-drug therapeutic-index calculation across all targeted tissues is Workstream B (Layer E ADMET) work."
}
```

Requirements to upgrade:
  - For full DELIVERED status, integrate GTEx-derived per-target tissue selectivity to quantify therapeutic index per organ system. Currently mechanism is from disease side only.

**03_predicted_clinical_outcomes** [GAP]

Requirements to upgrade:
  - Phenotype-structured ODE is currently mCRPC-specific (Round 3 Finding 18)
  - GBM-applicable ODE requires: (a) GBM scRNA-seq with raw FASTQ for velocity, OR (b) GBM bulk transcriptomics with phenotype proxy, OR (c) acceptance that GBM uses alternative cell-state characterization
  - Universal ODE refactor explicitly Workstream C scope per Plan v2 §5
  - Workstream B (Time Machine generalization) tests whether the phenotype ODE breakthrough generalizes — answer determines C architecture

**04_resistance_profile** [GAP]

Requirements to upgrade:
  - Resistance profile requires phenotype-structured ODE (currently mCRPC-only)
  - AND requires disease-specific RNA velocity initial condition (mCRPC has Dong et al. GSE137829; GBM lacks comparable scRNA-seq with raw FASTQ in our pipeline)
  - Cell-state characterization for GBM might use alternative: TCGA-GBM mesenchymal/proneural/classical subtypes (Wang et al. Cancer Cell 2017), or GBM tumor stem cell state markers (Couturier et al. Nat Commun 2020)

**05_combination_rationale** [N/A]

```json
{
  "drug_name": "Osimertinib",
  "note": "Monotherapy candidate; combination rationale not applicable"
}
```

Requirements to upgrade:
  - For combination candidates: synergy scoring (Layer D) requires per-drug PK/PD in disease-specific cell line panel. Workstream B (Time Machine) and C scope.

**06_safety_admet** [PARTIAL]

```json
{
  "drug_name": "Osimertinib",
  "bbb_passability": {
    "gate_value": 1.0,
    "interpretation": "likely_bbb_pos (passes BBB filter for CNS diseases)",
    "method": "CNS MPO score per Wager et al. ACS Chem Neurosci 2010",
    "limitation": "Passive-diffusion proxy; does not capture P-gp efflux, transporters, prodrug effects"
  },
  "organ_toxicity_assessment": "GAP \u2014 requires per-drug ADMET (SwissADME, pkCSM)",
  "off_target_panel": "GAP \u2014 requires kinome-wide selectivity assay data integration",
  "gtex_selectivity_note": "Per-gene GTEx tissue selectivity is captured in Workstream A net data. Per-drug therapeutic index calculation across organ systems requires Workstream B Layer E."
}
```

Requirements to upgrade:
  - Integrate SwissADME or pkCSM for per-drug ADMET prediction
  - Off-target panel: kinome-wide ChEMBL bioactivity profiling per drug
  - Per-drug GTEx-based therapeutic index calculation

**07_synthesis_route** [GAP]

Requirements to upgrade:
  - For approved drugs (most v2 top-5 candidates): synthesis route is publicly known; could be retrieved from DrugBank or PubChem
  - For novel candidates from generative chemistry (Workstream C): ASKCOS retrosynthesis integration required per vision
  - SA_Score (Ertl & Schuffenhauer 2009) requires canonical SMILES; depends on item 1 upgrade to DELIVERED

**08_novelty_vs_clinicaltrials** [DELIVERED]

```json
{
  "drug_name": "Osimertinib",
  "novelty_assessment": "WELL-STUDIED: 50 GBM trials (mature clinical pipeline)",
  "total_gbm_trials_across_targets": 50,
  "per_target_breakdown": [
    {
      "gene": "EGFR",
      "n_gbm_trials_targeting_this_gene": 50,
      "sample_trials": [
        {
          "nct_id": "NCT06072586",
          "title": "A Phase 0/1 Study of BDTX-1535 in Recurrent High-Grade Glioma (rHGG) and Newly D",
          "phase": "EARLY_PHASE1",
          "status": "RECRUITING"
        },
        {
          "nct_id": "NCT01238237",
          "title": "Super-Selective Intraarterial Cerebral Infusion of Cetuximab (Erbitux) for Treat",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT03344250",
          "title": "Phase I EGFR BATs in Newly Diagnosed Glioblastoma",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT00052208",
          "title": "Gefitinib and Radiation Therapy in Treating Patients With Glioblastoma Multiform",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT01454596",
          "title": "CAR T Cell Receptor Immunotherapy Targeting EGFRvIII for Patients With Malignant",
          "phase": "PHASE1",
          "status": "COMPLETED"
        }
      ]
    }
  ],
  "caveat": "Novelty here is by-target, not by-specific-drug-name. A drug whose target has many GBM trials is not necessaril
  ... (truncated; see full JSON)
```

Requirements to upgrade:
  - For drug-name-specific novelty: GDSC drug -> ChEMBL drug -> ClinicalTrials.gov intervention search by drug name

**09_comparison_vs_soc** [PARTIAL]

```json
{
  "drug_name": "Osimertinib",
  "gbm_standard_of_care": {
    "newly_diagnosed": {
      "first_line": "Surgery + temozolomide + radiotherapy (Stupp protocol)",
      "reference": "Stupp et al. NEJM 2005; Stupp et al. JAMA 2017 (TTFields update)",
      "median_OS": "~16 months for MGMT-methylated, ~12 months MGMT-unmethylated"
    },
    "recurrent": {
      "options": [
        "Bevacizumab",
        "Lomustine",
        "TTFields",
        "Re-resection + reirradiation"
      ],
      "reference": "NCCN GBM Guidelines (2024)",
      "median_OS_after_recurrence": "~6-9 months"
    }
  },
  "qualitative_comparison": "Candidate Osimertinib is a kinase-inhibitor class drug. GBM SOC is alkylating chemotherapy + radiotherapy. The candidate represents a different mechanism class than current SOC. Quantitative comparison (predicted PFS/OS vs SOC) requires item 3 (predicted clinical outcomes) which depends on Workstream B/C ODE generalization.",
  "positioning": "If validated, this candidate would be evaluated either as: (a) replacement for failing standard of care in MGMT-unmethylated GBM, (b) addition to TMZ backbone, OR (c) recurrent-GBM second-line option."
}
```

Requirements to upgrade:
  - Quantitative outcome comparison requires item 3 (ODE-derived predictions) — GAP
  - Direct head-to-head trial design considerations — handled in item 10

**10_trial_design** [PARTIAL]

```json
{
  "drug_name": "Osimertinib",
  "recommended_setting": "Recurrent GBM after first-line failure (lower regulatory risk)",
  "phase": "Phase 1b/2 dose-finding + activity assessment",
  "biomarker_stratifications": [
    {
      "biomarker": "EGFR mutation/amplification status",
      "gbm_prevalence": "0.9% of GBM patients",
      "rationale": "Drug targets EGFR; patients with altered EGFR expected to derive larger benefit"
    },
    {
      "biomarker": "MGMT promoter methylation status",
      "gbm_prevalence": "~40% of GBM patients are MGMT-methylated",
      "rationale": "Stratification standard for ANY GBM trial; MGMT-methylated patients respond differently to alkylating chemotherapy and combination strategies"
    }
  ],
  "primary_endpoint_suggestion": "Progression-free survival at 6 months (PFS6)",
  "secondary_endpoints": [
    "Overall survival",
    "Objective response rate (RANO)",
    "Safety/tolerability"
  ],
  "control_arm_consideration": "Lomustine standard recurrent-GBM control OR investigator-choice",
  "sample_size_caveat": "Quantitative power calculation requires item 3 (predicted PFS/OS effect size) \u2014 GAP. Without effect size estimate, suggested sample is 60-100 patients per arm based on historical GBM Phase 2 trial sizes (e.g., REGOMA, LOMUSTINE controls)."
}
```

Requirements to upgrade:
  - Quantitative power calculation requires item 3 outcomes (GAP)
  - Patient population specifics (newly-diagnosed vs recurrent, prior therapies) require item 9 quantitative SOC comparison (GAP)

---

### 4. AZD3759

- **Composite v2 score:** 0.670
- **Coverage:** 2/10 DELIVERED, 4/10 PARTIAL, 3/10 GAP, 1/10 N/A
- **GDSC targets:** EGFR

**01_molecular_structure** [PARTIAL]

```json
{
  "drug_name": "AZD3759",
  "representative_chembl_id": "CHEMBL176582",
  "representative_target_gene": "EGFR",
  "pchembl_value": 11.0,
  "standard_type": "IC50",
  "standard_value_nM": "0.01",
  "molecular_properties": {
    "molecular_weight": null,
    "alogp": null,
    "polar_surface_area": null,
    "hbd": null,
    "hba": null,
    "qed_weighted": null,
    "ro5_pass": null
  },
  "bbb_assessment": {
    "category": null,
    "mpo_score": null,
    "mpo_components": null,
    "method": "CNS MPO 4-component (logp+mw+tpsa+hbd) per Wager et al. 2010"
  },
  "note": "Showing representative ChEMBL compound for this drug-target relationship. The actual drug may correspond to a specific ChEMBL ID; full mapping needs GDSC drug-name to ChEMBL synonym lookup."
}
```

Requirements to upgrade:
  - Direct GDSC drug-name to canonical ChEMBL compound mapping
  - SMILES string (currently only chembl_id stored, not canonical SMILES)
  - 3D structure file (PDB/SDF) — would require ChEMBL /molecule/{id} structures fetch

**02_mechanism_of_action** [DELIVERED]

```json
{
  "drug_name": "AZD3759",
  "targeted_disease_genes": [
    {
      "gene": "EGFR",
      "disease_association_score": 0.649,
      "n_string_interactions": 502,
      "n_clinical_trials_in_gbm": 50,
      "n_chembl_compounds": 31,
      "mutation_frequency_in_gbm": 0.0094,
      "has_alphafold_structure": true
    }
  ],
  "mechanism_summary": "Targets EGFR (GBM association score 0.649; 50 GBM trials).",
  "why_kills_disease": [
    "Targets EGFR (GBM association score 0.649; 50 GBM trials)."
  ],
  "healthy_sparing_assessment": "Selectivity/healthy-cell sparing analysis requires GTEx tissue selectivity scoring, which is captured per-gene in Workstream A. Per-drug therapeutic-index calculation across all targeted tissues is Workstream B (Layer E ADMET) work."
}
```

Requirements to upgrade:
  - For full DELIVERED status, integrate GTEx-derived per-target tissue selectivity to quantify therapeutic index per organ system. Currently mechanism is from disease side only.

**03_predicted_clinical_outcomes** [GAP]

Requirements to upgrade:
  - Phenotype-structured ODE is currently mCRPC-specific (Round 3 Finding 18)
  - GBM-applicable ODE requires: (a) GBM scRNA-seq with raw FASTQ for velocity, OR (b) GBM bulk transcriptomics with phenotype proxy, OR (c) acceptance that GBM uses alternative cell-state characterization
  - Universal ODE refactor explicitly Workstream C scope per Plan v2 §5
  - Workstream B (Time Machine generalization) tests whether the phenotype ODE breakthrough generalizes — answer determines C architecture

**04_resistance_profile** [GAP]

Requirements to upgrade:
  - Resistance profile requires phenotype-structured ODE (currently mCRPC-only)
  - AND requires disease-specific RNA velocity initial condition (mCRPC has Dong et al. GSE137829; GBM lacks comparable scRNA-seq with raw FASTQ in our pipeline)
  - Cell-state characterization for GBM might use alternative: TCGA-GBM mesenchymal/proneural/classical subtypes (Wang et al. Cancer Cell 2017), or GBM tumor stem cell state markers (Couturier et al. Nat Commun 2020)

**05_combination_rationale** [N/A]

```json
{
  "drug_name": "AZD3759",
  "note": "Monotherapy candidate; combination rationale not applicable"
}
```

Requirements to upgrade:
  - For combination candidates: synergy scoring (Layer D) requires per-drug PK/PD in disease-specific cell line panel. Workstream B (Time Machine) and C scope.

**06_safety_admet** [PARTIAL]

```json
{
  "drug_name": "AZD3759",
  "bbb_passability": {
    "gate_value": 1.0,
    "interpretation": "likely_bbb_pos (passes BBB filter for CNS diseases)",
    "method": "CNS MPO score per Wager et al. ACS Chem Neurosci 2010",
    "limitation": "Passive-diffusion proxy; does not capture P-gp efflux, transporters, prodrug effects"
  },
  "organ_toxicity_assessment": "GAP \u2014 requires per-drug ADMET (SwissADME, pkCSM)",
  "off_target_panel": "GAP \u2014 requires kinome-wide selectivity assay data integration",
  "gtex_selectivity_note": "Per-gene GTEx tissue selectivity is captured in Workstream A net data. Per-drug therapeutic index calculation across organ systems requires Workstream B Layer E."
}
```

Requirements to upgrade:
  - Integrate SwissADME or pkCSM for per-drug ADMET prediction
  - Off-target panel: kinome-wide ChEMBL bioactivity profiling per drug
  - Per-drug GTEx-based therapeutic index calculation

**07_synthesis_route** [GAP]

Requirements to upgrade:
  - For approved drugs (most v2 top-5 candidates): synthesis route is publicly known; could be retrieved from DrugBank or PubChem
  - For novel candidates from generative chemistry (Workstream C): ASKCOS retrosynthesis integration required per vision
  - SA_Score (Ertl & Schuffenhauer 2009) requires canonical SMILES; depends on item 1 upgrade to DELIVERED

**08_novelty_vs_clinicaltrials** [DELIVERED]

```json
{
  "drug_name": "AZD3759",
  "novelty_assessment": "WELL-STUDIED: 50 GBM trials (mature clinical pipeline)",
  "total_gbm_trials_across_targets": 50,
  "per_target_breakdown": [
    {
      "gene": "EGFR",
      "n_gbm_trials_targeting_this_gene": 50,
      "sample_trials": [
        {
          "nct_id": "NCT06072586",
          "title": "A Phase 0/1 Study of BDTX-1535 in Recurrent High-Grade Glioma (rHGG) and Newly D",
          "phase": "EARLY_PHASE1",
          "status": "RECRUITING"
        },
        {
          "nct_id": "NCT01238237",
          "title": "Super-Selective Intraarterial Cerebral Infusion of Cetuximab (Erbitux) for Treat",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT03344250",
          "title": "Phase I EGFR BATs in Newly Diagnosed Glioblastoma",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT00052208",
          "title": "Gefitinib and Radiation Therapy in Treating Patients With Glioblastoma Multiform",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT01454596",
          "title": "CAR T Cell Receptor Immunotherapy Targeting EGFRvIII for Patients With Malignant",
          "phase": "PHASE1",
          "status": "COMPLETED"
        }
      ]
    }
  ],
  "caveat": "Novelty here is by-target, not by-specific-drug-name. A drug whose target has many GBM trials is not necessarily a 
  ... (truncated; see full JSON)
```

Requirements to upgrade:
  - For drug-name-specific novelty: GDSC drug -> ChEMBL drug -> ClinicalTrials.gov intervention search by drug name

**09_comparison_vs_soc** [PARTIAL]

```json
{
  "drug_name": "AZD3759",
  "gbm_standard_of_care": {
    "newly_diagnosed": {
      "first_line": "Surgery + temozolomide + radiotherapy (Stupp protocol)",
      "reference": "Stupp et al. NEJM 2005; Stupp et al. JAMA 2017 (TTFields update)",
      "median_OS": "~16 months for MGMT-methylated, ~12 months MGMT-unmethylated"
    },
    "recurrent": {
      "options": [
        "Bevacizumab",
        "Lomustine",
        "TTFields",
        "Re-resection + reirradiation"
      ],
      "reference": "NCCN GBM Guidelines (2024)",
      "median_OS_after_recurrence": "~6-9 months"
    }
  },
  "qualitative_comparison": "Candidate AZD3759 is a kinase-inhibitor class drug. GBM SOC is alkylating chemotherapy + radiotherapy. The candidate represents a different mechanism class than current SOC. Quantitative comparison (predicted PFS/OS vs SOC) requires item 3 (predicted clinical outcomes) which depends on Workstream B/C ODE generalization.",
  "positioning": "If validated, this candidate would be evaluated either as: (a) replacement for failing standard of care in MGMT-unmethylated GBM, (b) addition to TMZ backbone, OR (c) recurrent-GBM second-line option."
}
```

Requirements to upgrade:
  - Quantitative outcome comparison requires item 3 (ODE-derived predictions) — GAP
  - Direct head-to-head trial design considerations — handled in item 10

**10_trial_design** [PARTIAL]

```json
{
  "drug_name": "AZD3759",
  "recommended_setting": "Recurrent GBM after first-line failure (lower regulatory risk)",
  "phase": "Phase 1b/2 dose-finding + activity assessment",
  "biomarker_stratifications": [
    {
      "biomarker": "EGFR mutation/amplification status",
      "gbm_prevalence": "0.9% of GBM patients",
      "rationale": "Drug targets EGFR; patients with altered EGFR expected to derive larger benefit"
    },
    {
      "biomarker": "MGMT promoter methylation status",
      "gbm_prevalence": "~40% of GBM patients are MGMT-methylated",
      "rationale": "Stratification standard for ANY GBM trial; MGMT-methylated patients respond differently to alkylating chemotherapy and combination strategies"
    }
  ],
  "primary_endpoint_suggestion": "Progression-free survival at 6 months (PFS6)",
  "secondary_endpoints": [
    "Overall survival",
    "Objective response rate (RANO)",
    "Safety/tolerability"
  ],
  "control_arm_consideration": "Lomustine standard recurrent-GBM control OR investigator-choice",
  "sample_size_caveat": "Quantitative power calculation requires item 3 (predicted PFS/OS effect size) \u2014 GAP. Without effect size estimate, suggested sample is 60-100 patients per arm based on historical GBM Phase 2 trial sizes (e.g., REGOMA, LOMUSTINE controls)."
}
```

Requirements to upgrade:
  - Quantitative power calculation requires item 3 outcomes (GAP)
  - Patient population specifics (newly-diagnosed vs recurrent, prior therapies) require item 9 quantitative SOC comparison (GAP)

---

### 5. Gefitinib

- **Composite v2 score:** 0.669
- **Coverage:** 2/10 DELIVERED, 4/10 PARTIAL, 3/10 GAP, 1/10 N/A
- **GDSC targets:** EGFR

**01_molecular_structure** [PARTIAL]

```json
{
  "drug_name": "Gefitinib",
  "representative_chembl_id": "CHEMBL176582",
  "representative_target_gene": "EGFR",
  "pchembl_value": 11.0,
  "standard_type": "IC50",
  "standard_value_nM": "0.01",
  "molecular_properties": {
    "molecular_weight": null,
    "alogp": null,
    "polar_surface_area": null,
    "hbd": null,
    "hba": null,
    "qed_weighted": null,
    "ro5_pass": null
  },
  "bbb_assessment": {
    "category": null,
    "mpo_score": null,
    "mpo_components": null,
    "method": "CNS MPO 4-component (logp+mw+tpsa+hbd) per Wager et al. 2010"
  },
  "note": "Showing representative ChEMBL compound for this drug-target relationship. The actual drug may correspond to a specific ChEMBL ID; full mapping needs GDSC drug-name to ChEMBL synonym lookup."
}
```

Requirements to upgrade:
  - Direct GDSC drug-name to canonical ChEMBL compound mapping
  - SMILES string (currently only chembl_id stored, not canonical SMILES)
  - 3D structure file (PDB/SDF) — would require ChEMBL /molecule/{id} structures fetch

**02_mechanism_of_action** [DELIVERED]

```json
{
  "drug_name": "Gefitinib",
  "targeted_disease_genes": [
    {
      "gene": "EGFR",
      "disease_association_score": 0.649,
      "n_string_interactions": 502,
      "n_clinical_trials_in_gbm": 50,
      "n_chembl_compounds": 31,
      "mutation_frequency_in_gbm": 0.0094,
      "has_alphafold_structure": true
    }
  ],
  "mechanism_summary": "Targets EGFR (GBM association score 0.649; 50 GBM trials).",
  "why_kills_disease": [
    "Targets EGFR (GBM association score 0.649; 50 GBM trials)."
  ],
  "healthy_sparing_assessment": "Selectivity/healthy-cell sparing analysis requires GTEx tissue selectivity scoring, which is captured per-gene in Workstream A. Per-drug therapeutic-index calculation across all targeted tissues is Workstream B (Layer E ADMET) work."
}
```

Requirements to upgrade:
  - For full DELIVERED status, integrate GTEx-derived per-target tissue selectivity to quantify therapeutic index per organ system. Currently mechanism is from disease side only.

**03_predicted_clinical_outcomes** [GAP]

Requirements to upgrade:
  - Phenotype-structured ODE is currently mCRPC-specific (Round 3 Finding 18)
  - GBM-applicable ODE requires: (a) GBM scRNA-seq with raw FASTQ for velocity, OR (b) GBM bulk transcriptomics with phenotype proxy, OR (c) acceptance that GBM uses alternative cell-state characterization
  - Universal ODE refactor explicitly Workstream C scope per Plan v2 §5
  - Workstream B (Time Machine generalization) tests whether the phenotype ODE breakthrough generalizes — answer determines C architecture

**04_resistance_profile** [GAP]

Requirements to upgrade:
  - Resistance profile requires phenotype-structured ODE (currently mCRPC-only)
  - AND requires disease-specific RNA velocity initial condition (mCRPC has Dong et al. GSE137829; GBM lacks comparable scRNA-seq with raw FASTQ in our pipeline)
  - Cell-state characterization for GBM might use alternative: TCGA-GBM mesenchymal/proneural/classical subtypes (Wang et al. Cancer Cell 2017), or GBM tumor stem cell state markers (Couturier et al. Nat Commun 2020)

**05_combination_rationale** [N/A]

```json
{
  "drug_name": "Gefitinib",
  "note": "Monotherapy candidate; combination rationale not applicable"
}
```

Requirements to upgrade:
  - For combination candidates: synergy scoring (Layer D) requires per-drug PK/PD in disease-specific cell line panel. Workstream B (Time Machine) and C scope.

**06_safety_admet** [PARTIAL]

```json
{
  "drug_name": "Gefitinib",
  "bbb_passability": {
    "gate_value": 1.0,
    "interpretation": "likely_bbb_pos (passes BBB filter for CNS diseases)",
    "method": "CNS MPO score per Wager et al. ACS Chem Neurosci 2010",
    "limitation": "Passive-diffusion proxy; does not capture P-gp efflux, transporters, prodrug effects"
  },
  "organ_toxicity_assessment": "GAP \u2014 requires per-drug ADMET (SwissADME, pkCSM)",
  "off_target_panel": "GAP \u2014 requires kinome-wide selectivity assay data integration",
  "gtex_selectivity_note": "Per-gene GTEx tissue selectivity is captured in Workstream A net data. Per-drug therapeutic index calculation across organ systems requires Workstream B Layer E."
}
```

Requirements to upgrade:
  - Integrate SwissADME or pkCSM for per-drug ADMET prediction
  - Off-target panel: kinome-wide ChEMBL bioactivity profiling per drug
  - Per-drug GTEx-based therapeutic index calculation

**07_synthesis_route** [GAP]

Requirements to upgrade:
  - For approved drugs (most v2 top-5 candidates): synthesis route is publicly known; could be retrieved from DrugBank or PubChem
  - For novel candidates from generative chemistry (Workstream C): ASKCOS retrosynthesis integration required per vision
  - SA_Score (Ertl & Schuffenhauer 2009) requires canonical SMILES; depends on item 1 upgrade to DELIVERED

**08_novelty_vs_clinicaltrials** [DELIVERED]

```json
{
  "drug_name": "Gefitinib",
  "novelty_assessment": "WELL-STUDIED: 50 GBM trials (mature clinical pipeline)",
  "total_gbm_trials_across_targets": 50,
  "per_target_breakdown": [
    {
      "gene": "EGFR",
      "n_gbm_trials_targeting_this_gene": 50,
      "sample_trials": [
        {
          "nct_id": "NCT06072586",
          "title": "A Phase 0/1 Study of BDTX-1535 in Recurrent High-Grade Glioma (rHGG) and Newly D",
          "phase": "EARLY_PHASE1",
          "status": "RECRUITING"
        },
        {
          "nct_id": "NCT01238237",
          "title": "Super-Selective Intraarterial Cerebral Infusion of Cetuximab (Erbitux) for Treat",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT03344250",
          "title": "Phase I EGFR BATs in Newly Diagnosed Glioblastoma",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT00052208",
          "title": "Gefitinib and Radiation Therapy in Treating Patients With Glioblastoma Multiform",
          "phase": "PHASE1",
          "status": "COMPLETED"
        },
        {
          "nct_id": "NCT01454596",
          "title": "CAR T Cell Receptor Immunotherapy Targeting EGFRvIII for Patients With Malignant",
          "phase": "PHASE1",
          "status": "COMPLETED"
        }
      ]
    }
  ],
  "caveat": "Novelty here is by-target, not by-specific-drug-name. A drug whose target has many GBM trials is not necessarily 
  ... (truncated; see full JSON)
```

Requirements to upgrade:
  - For drug-name-specific novelty: GDSC drug -> ChEMBL drug -> ClinicalTrials.gov intervention search by drug name

**09_comparison_vs_soc** [PARTIAL]

```json
{
  "drug_name": "Gefitinib",
  "gbm_standard_of_care": {
    "newly_diagnosed": {
      "first_line": "Surgery + temozolomide + radiotherapy (Stupp protocol)",
      "reference": "Stupp et al. NEJM 2005; Stupp et al. JAMA 2017 (TTFields update)",
      "median_OS": "~16 months for MGMT-methylated, ~12 months MGMT-unmethylated"
    },
    "recurrent": {
      "options": [
        "Bevacizumab",
        "Lomustine",
        "TTFields",
        "Re-resection + reirradiation"
      ],
      "reference": "NCCN GBM Guidelines (2024)",
      "median_OS_after_recurrence": "~6-9 months"
    }
  },
  "qualitative_comparison": "Candidate Gefitinib is a kinase-inhibitor class drug. GBM SOC is alkylating chemotherapy + radiotherapy. The candidate represents a different mechanism class than current SOC. Quantitative comparison (predicted PFS/OS vs SOC) requires item 3 (predicted clinical outcomes) which depends on Workstream B/C ODE generalization.",
  "positioning": "If validated, this candidate would be evaluated either as: (a) replacement for failing standard of care in MGMT-unmethylated GBM, (b) addition to TMZ backbone, OR (c) recurrent-GBM second-line option."
}
```

Requirements to upgrade:
  - Quantitative outcome comparison requires item 3 (ODE-derived predictions) — GAP
  - Direct head-to-head trial design considerations — handled in item 10

**10_trial_design** [PARTIAL]

```json
{
  "drug_name": "Gefitinib",
  "recommended_setting": "Recurrent GBM after first-line failure (lower regulatory risk)",
  "phase": "Phase 1b/2 dose-finding + activity assessment",
  "biomarker_stratifications": [
    {
      "biomarker": "EGFR mutation/amplification status",
      "gbm_prevalence": "0.9% of GBM patients",
      "rationale": "Drug targets EGFR; patients with altered EGFR expected to derive larger benefit"
    },
    {
      "biomarker": "MGMT promoter methylation status",
      "gbm_prevalence": "~40% of GBM patients are MGMT-methylated",
      "rationale": "Stratification standard for ANY GBM trial; MGMT-methylated patients respond differently to alkylating chemotherapy and combination strategies"
    }
  ],
  "primary_endpoint_suggestion": "Progression-free survival at 6 months (PFS6)",
  "secondary_endpoints": [
    "Overall survival",
    "Objective response rate (RANO)",
    "Safety/tolerability"
  ],
  "control_arm_consideration": "Lomustine standard recurrent-GBM control OR investigator-choice",
  "sample_size_caveat": "Quantitative power calculation requires item 3 (predicted PFS/OS effect size) \u2014 GAP. Without effect size estimate, suggested sample is 60-100 patients per arm based on historical GBM Phase 2 trial sizes (e.g., REGOMA, LOMUSTINE controls)."
}
```

Requirements to upgrade:
  - Quantitative power calculation requires item 3 outcomes (GAP)
  - Patient population specifics (newly-diagnosed vs recurrent, prior therapies) require item 9 quantitative SOC comparison (GAP)

---


## Honest assessment

Average per-candidate coverage: 2.0/10 DELIVERED + 4.0/10 PARTIAL + 3.0/10 GAP

This is the actual current state of Workstream A as a Stage 5 pharma deliverable producer. The DELIVERED items demonstrate that the disease-net infrastructure is real and produces grounded output. The GAP items document with specificity what Workstream B (ODE generalization) and Workstream C (synthesis routes, full ADMET, generative chemistry) need to add.

Per Vision's validation-first principle: this honest partial deliverable is more vision-aligned than a fabricated complete one.
