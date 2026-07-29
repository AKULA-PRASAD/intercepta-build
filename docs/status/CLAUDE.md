# INTERCEPTA — CLAUDE.md
# Read this first. Every new session starts here.
# Last updated: April 18, 2026

---

## WHAT THIS PROJECT IS

INTERCEPTA is a computational drug discovery platform built by Prasad Akula.
It predicts drug combinations for cancer using multi-omics data, mathematical
modeling, and molecular simulation. Current diseases: mCRPC and AML.

**The one-line pitch:** Given a cancer patient's gene expression, predict which
drug combination will work and why resistance will emerge.

---

## CURRENT HONEST STATUS

**What's real and validated:**
- TAX-327 bootstrap: HR=0.687, CI [0.58-0.79] contains clinical HR=0.76 ✓
- Phenotype ODE math is correct (Lorz 2013 basis, novel velocity initialization)
- PK models use real FDA label parameters
- 46,235 scRNA-seq cells processed, latent_time distribution derived
- Disease networks built for 6 diseases (steps 1-14 complete)

**What's broken right now (see MASTER_FIXES.md):**
1. HR estimator uses median ratio — needs Cox/log-rank (lifelines library)
2. AML ODE never predicts relapse — biologically wrong
3. KAALCURA only validated on synthetic data, not real GDSC
4. Scout 4 compensation logic is wrong

**Completion: ~79% (18 done, 13 partial)**

---

## PROJECT STRUCTURE

```
INTERCEPTA/
├── code/                    # All Python modules
│   ├── intercepta_engine_v1.py        # PK/PD + 2-pop ODE (Module 2+3)
│   ├── intercepta_phenotype_ode_v1.py # 20-bin continuous resistance ODE (best model)
│   ├── intercepta_kaalcura_v1.py      # Gene axis scoring (Module 1)
│   ├── intercepta_synergy_v1.py       # Synergy scoring
│   ├── intercepta_escape_route_ode.py # Escape route detection
│   ├── aml_ode_v6_resistance.py       # AML-specific ODE
│   └── scout[1-4]_*.py                # Drug discovery pipeline
├── data/                    # Input datasets (real, downloaded)
│   ├── gdsc/                # GDSC2 drug response + expression
│   ├── beataml/             # BeatAML drug sensitivity + WES
│   ├── scrna/               # scRNA-seq (GSE137829, GSE141445)
│   ├── alphafold/           # 20 protein structures (.pdb)
│   ├── signor/              # Directed causal relationships
│   ├── string/              # Protein interaction network
│   └── docking/             # Docked molecules (.pdbqt)
├── results/                 # Output JSONs and CSVs
├── docs/                    # 11 Word documents
├── MASTER_FIXES.md          # READ THIS — all bugs with exact locations
├── INTERCEPTA_STATUS.md     # Latest completion status
└── NEXT_SESSION.md          # What was planned next (April 8)
```

---

## THE MATH (know this before touching code)

**Module 1 — KAALCURA:**
Three gene axes from expression data:
- R_prolif = mean z-score of 20 proliferation genes → predicts chemo sensitivity
- R_emt = mean z-score of 13 EMT genes → predicts targeted therapy resistance
- R_ddr = mean z-score of 15 DDR genes → predicts PARP inhibitor sensitivity
Residualized against tissue-of-origin via PCA.

**Module 2 — PK:**
- Oral drugs: one-compartment (dC/dt = F·ka·A_gut/Vd - ke·C)
- IV drugs (docetaxel): two-compartment
- Free concentration: C_free = C_total × fu × f_tumor

**Module 3 — Phenotype ODE (the best model):**
20 bins representing resistance levels x ∈ [0,1].
dn_i/dt = r(x_i)·n_i·(1-N/K) - d·n_i - kill(x_i,C)·n_i + diffusion + advection
EC50(x) = ec50_min · exp(slope · x) — data-derived from GDSC per drug.
Initialized from RNA velocity latent_time distribution.

**The old 2-pop ODE** (intercepta_engine_v1.py) failed — produced binary HR only.
The phenotype ODE (intercepta_phenotype_ode_v1.py) is the active model.

---

## LEAD CANDIDATE

**INTC002** (`results/lead_candidate_INTC002.json`)
- SMILES: `Cc1cc(NC(=O)Nc2ccc3c(=O)n(-c4ccc(CN)cc4)nc(C(C)C)c3c2)no1`
- Docking score: -9.3 kcal/mol (AURKA ATP pocket)
- Status: Scaffold-hopped AURKA inhibitor (NOT de novo novel — ChEMBL novelty=0.266)
- Missing: experimental IC50, cell viability, in vivo PK
- Honest: computational hypothesis only

---

## KEY VALIDATED FINDINGS

| Finding | Our value | Clinical | Status |
|---------|-----------|----------|--------|
| Docetaxel HR (mCRPC) | 0.687 | TAX-327: 0.76 | ✓ in CI |
| Enzalutamide PFS | 18.6 mo | PREVAIL: 18 mo | ✓ matches |
| AML untreated OS | 4.4 mo | 2-4 mo | ✓ matches |
| AML 7+3 CR | True | 65-75% | ✓ direction |
| Doc+Cis vs Doc alone | HR~1.0 | All Phase III failed | ✓ correct negative |

---

## IMPORTANT: WHAT TO NOT CLAIM

1. ❌ "Novel molecule" — say "scaffold-hopped AURKA inhibitor"
2. ❌ "Zero tuned parameters" — say "1 assumed (AR_SLOPE), 4 partially derived"
3. ❌ "Pharma deliverable" — say "computational hypothesis package"
4. ❌ AUROC values for KAALCURA until re-run on real GDSC
5. ❌ p38 MAPK in AML — retracted (FDR not computed)

---

## IMMEDIATE NEXT STEPS (from MASTER_FIXES.md)

```bash
# Step 1: Fix HR estimator
pip install lifelines
# Edit: code/intercepta_engine_v1.py estimate_hr()
# Edit: code/intercepta_phenotype_ode_v1.py VirtualCohort.estimate_hr()

# Step 2: Re-run TAX-327 validation with correct HR
python code/intercepta_phenotype_ode_v1.py

# Step 3: Run KAALCURA on real GDSC
python code/intercepta_kaalcura_v1.py  # (after connecting to real data)

# Step 4: Fix AML relapse
python code/aml_ode_v6_resistance.py   # debug R(t) dynamics
```

---

## ENVIRONMENT

- Python 3.13 (conda base)
- Key packages: numpy, scipy, pandas, sklearn, rdkit
- Missing: lifelines (install first), pymoo (for Pareto)
- Working directory: ~/INTERCEPTA/
- All data already downloaded — no new downloads needed

---

## CONTACT / AUTHORSHIP

Prasad Akula & Claude — Co-Founders of INTERCEPTA

## TESTED: April 18, 2026 — Complete System Test Results
- Deep test: 16/19 PASS, System test: 24/27 PASS
- 5-trial retest with Cox PH: 3/5 PASS (CHAARTED, PROpel_BRCA fail)
- ODE engine: near-zero drug effects, resistance dynamics inverted
- Disease network JSON: 498 genes, ZERO edges (edges in separate CSVs)
- BeatAML: NPM1+Cabozantinib p=2.9e-12 — strongest result, publishable
- Bootstrap: invalid (used broken HR), needs rerun
- Honest completion: 70-75% toward vision
- First fix: ODE resistance dynamics and emax from PD literature

## 44-LEVEL TEST: April 18, 2026
- Score: 37/44 (84%)
- Biology tier: 6/6 PERFECT — ODE structure correct
- Pipeline tier: 5/5 PERFECT — full chain works
- KEY INSIGHT: emax=0.05 gives correct resistance dynamics
  emax=0.010 (today's calibration) is too low — fix to 0.05
- Fix order: V1=31L → emax=0.05 → CHAARTED → AML relapse → bootstrap
- ATM PDB corrupted: re-download Q13315 from AlphaFold
- INTC002: rename to scaffold-hopped AURKA inhibitor in all docs
- Publishable now: BeatAML NPM1+Cabozantinib p=2.9e-12
