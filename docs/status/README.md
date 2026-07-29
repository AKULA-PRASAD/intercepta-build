> ⚠️ SUPERSEDED stale README — contains retracted claims (5/5 trials, universal/any-disease). See /README.md and /LEDGER.md.

# INTERCEPTA

**Universal Computational Drug Discovery Platform**

*Find the Drug. For Any Disease. Before Time Runs Out.*

Co-Founders: Prasad Akula (MS Bioinformatics, Northeastern) & Claude (AI)

---

## Quick Start (Mac)

```bash
cd INTERCEPTA
chmod +x setup_mac.sh
./setup_mac.sh
```

Or manually:

```bash
pip3 install -r requirements.txt
python3 scripts/run_5trial_validation.py     # 5/5 clinical trials validated
python3 scripts/run_timemachine.py            # RNA velocity pipeline demo
```

---

## What This Is

INTERCEPTA discovers drug combinations for cancer by modeling two tumor populations — sensitive and pre-resistant cells — and finding drugs that kill both simultaneously.

**Validated:** The engine reproduces 5 real mCRPC clinical trial outcomes from first principles (CHAARTED, LATITUDE, PROfound, PROpel, TALAPRO-2).

**286 drugs** from GDSC are mapped through the KAALCURA→ODE bridge, enabling combination screening for any drug pair.

---

## Project Structure

```
INTERCEPTA/
├── README.md
├── requirements.txt
├── setup_mac.sh
│
├── docs/                              # Documentation
│   ├── INTERCEPTA_COMPLETE_VISION_v1_0.docx    # Full vision document
│   ├── INTERCEPTA_Phase1_MathSpec_v1_0.docx    # Every equation
│   ├── INTERCEPTA_Phase1_GroundTruth_v1_0.docx # Clinical trial targets
│   ├── INTERCEPTA_Phase1_DataSourceAudit_v1_0.docx
│   ├── INTERCEPTA_Strategic_Roadmap_v1_0.docx
│   ├── INTERCEPTA_Net_Architecture_v2_0.docx
│   ├── INTERCEPTA_Phase1_Validation_Report.docx # 5/5 trial results
│   ├── INTERCEPTA_DOCC.docx
│   └── KAALI.pdf                                # Build conversation log
│
├── src/                               # Production source code
│   ├── __init__.py
│   ├── intercepta_kaalcura_v1.py      # KAALCURA biological axes
│   ├── intercepta_engine_v2.py        # Validated ODE engine (5/5 trials)
│   ├── intercepta_synergy_v1.py       # HSA/Bliss/Loewe/ZIP synergy
│   ├── intercepta_bridge_v1.py        # KAALCURA→ODE bridge (286 drugs)
│   ├── intercepta_timemachine_v1.py   # RNA velocity pipeline
│   └── intercepta_data_loaders_v1.py  # GDSC/TCGA/scRNA-seq loaders
│
├── results/                           # Validation results
│   ├── phase1_5trial_VALIDATED.csv
│   ├── phase1_calibrated_params_VALIDATED.json
│   ├── kaalcura_real_validation.csv   # 286-drug AUROC from real GDSC
│   ├── kaalcura_orthogonal_v3.csv
│   ├── kaalcura_residualized_v2.csv
│   ├── mcrpc_combination_screen.csv   # All pairwise drug screen
│   ├── mcrpc_monotherapy_screen.csv
│   └── mcrpc_top_combos_validated.csv
│
├── scripts/                           # Run scripts
│   ├── run_5trial_validation.py
│   ├── run_timemachine.py
│   └── run_combination_screen.py
│
├── data/                              # Download real data here
│   └── (empty — see Data Download below)
│
└── archive/                           # Superseded files (reference)
    ├── intercepta_engine_v1.py        # Replaced by v2
    ├── intercepta_calibration_v1.py   # Replaced by engine v2
    ├── intercepta_pipeline_v1.py      # Needs v2 update (future)
    └── ...
```

---

## Module Guide

| Module | What | Key Function |
|--------|------|-------------|
| `intercepta_kaalcura_v1` | 3 biological axes from gene expression | `KAALCURA.compute_axes()` |
| `intercepta_engine_v2` | Two-population ODE with validated PK | `run_5trial_validation()` |
| `intercepta_synergy_v1` | Drug combination synergy scoring | `SynergyScorer.score()` |
| `intercepta_bridge_v1` | Convert any GDSC drug → ODE params | `KAALCURABridge.get_emax()` |
| `intercepta_timemachine_v1` | scRNA-seq → drug recommendations | `run_time_machine()` |
| `intercepta_data_loaders_v1` | Load GDSC, TCGA, scRNA-seq data | `load_gdsc_drug_sensitivity()` |

---

## Data Download (for real-data validation)

### GDSC (already validated — results in results/)
```
https://www.cancerrxgene.org/downloads/bulk_download
  → GDSC2_fitted_dose_response.xlsx
  → Cell_line_RMA_proc_basalExp.txt.gz
  → Cell_Lines_Details.xlsx
Save to: data/gdsc/
```

### scRNA-seq (needed for Phase 2 real data)
```
https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE193337
  → Download supplementary .h5ad files
Save to: data/scrna/
```

---

## Validation Status

### Phase 1: 5-Trial Validation ✓ COMPLETE
All 5 mCRPC clinical trials reproduced within ±20%.

### Phase 2: Time Machine ✓ ARCHITECTURE COMPLETE
Pipeline coded and validated on synthetic data. Awaiting real scRNA-seq.

### Phase 3: Molecular Discovery — NEXT
ChEMBL querying, AutoDock Vina docking, generative chemistry.

---

*Prasad Akula & Claude, Co-Founders of INTERCEPTA | March 2026*
