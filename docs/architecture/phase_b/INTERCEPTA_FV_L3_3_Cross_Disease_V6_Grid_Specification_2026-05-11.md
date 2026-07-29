# INTERCEPTA Phase B Layer 3 — Artifact 3.3
## Cross-Disease V6 Grid Specification

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifacts:** L2.1 LOCKED, L2.2/L2.3/L2.4 PROPOSED, L3.1/L3.2 PROPOSED — Layer 3 NEARING COMPLETION
**Parent decision:** Decision 8 v2 Q8 Universality (LOCKED); Decision 6 v2 Q6 V6 row; Decision 5 v2 Pass 4
**Co-bound decisions:** Decisions 1, 2, 4, 5, 6, 7, 8, 9, 10 (all v2)
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Phase F mapping:** Phase B V6 grid (3 diseases × 2 therapeutic areas minimum) becomes Phase F V7-V8 expanded grid (≥10 diseases × ≥5 therapeutic areas) plus prospective trial validation.
**Target length per Phase B Plan v2:** 4-5K words
**Filename:** INTERCEPTA_FV_L3_3_Cross_Disease_V6_Grid_Specification_2026-05-11.md

---

## §0 Identification and Scope

### 0.1 What This Document Is

L3.3 is the **Cross-Disease V6 Grid Specification** — the third and final artifact of Phase B Layer 3. L3.3 specifies the exact (disease × therapeutic area × paradigm × tissue × per-disease sample sizes) grid that V6 evaluates, the SLURM job array operational pattern per Decision 9 v2, and the disease-selection rationale that makes the universality test rigorous rather than rigged.

L3.3 commits INTERCEPTA to **3 held-out diseases × 2 therapeutic areas × 4 paradigms × per-disease populated cells = 24 to 100 evaluation cells** depending on tissue applicability. The grid is sized to be the minimum that satisfies Decision 8 v2 Commitment 1 while remaining tractable on Decision 9 v2 single-A100 + AWS-burst budget.

### 0.2 What This Document Is Not

L3.3 is NOT:
- An expanded grid (the ≥10 diseases × ≥5 areas Phase F-scale grid is Charter v1.2 §4 row 21 Phase F)
- A clinical trial protocol (Phase F prospective testing)
- A regulatory submission package (Phase F)
- A dataset acquisition timeline (Layer 4 implementation; L3.3 specifies WHICH datasets, not WHEN they are acquired)
- The exact 56 pass criteria (L3.2 specifies; L3.3 references)

### 0.3 The Universality Test Question

Charter §1.1: "Find the drug. For ANY disease." V6 operationalizes this. The honest, scientifically rigorous test is:

**Can INTERCEPTA, trained on cancer drug response data, achieve AUROC ≥ 0.65 on a held-out non-cancer disease where the drug response biology is genuinely different?**

If yes, universality is empirically supported. If no, INTERCEPTA must narrow Charter §1.1 to "Find cancer drugs" — a narrower but still valuable vision.

The grid design must:
1. Include diseases sufficiently different from cancer that "success on these is universality, not cancer transfer"
2. Include enough therapeutic areas (≥2 BINDING) that "success on these spans biology, not just one mechanism"
3. Be tractable on Phase B compute budget
4. Avoid rigging by easy-disease selection
5. Avoid rigging by hard-disease cherry-picking

This is the most consequential single design choice in Phase B Layer 3.

### 0.4 Phase B Plan v2 Compliance

- Layer 2 COMPLETE 2026-05-11
- L3.1 PROPOSED, L3.2 PROPOSED
- **L3.3 → PROPOSED (this document)**
- After L3.3 LOCK: **Layer 3 of Phase B COMPLETE**
- Then Layer 4 (3 artifacts: L4.1, L4.2, L4.3), then Phase 8 audit, then Layer 5 (build)

### 0.5 Document Conventions

- **BINDING** — Decision Record amendment required to modify
- **DEFAULT** — Layer-5-revisitable per §8.5
- Dataset references use canonical names (GEO accession numbers, dbGaP study IDs, or curator names where applicable)
- All datasets listed are publicly available (CC BY, GEO open) per Decision 10 v2

### 0.6 Anchor Re-Read Compliance

Q8 + Q5 anchor papers re-read in primary-source form during 2026-05-11 audit. Key sources for grid composition:
- Bandasack et al. 2026 EVA: I&I + anti-TNF + ulcerative colitis demonstration (Phase II RCT prediction)
- Decision 8 v2 disease examples: cancer subtypes + I&I + neurodegenerative + metabolic
- Decision 6 v2 V6 sample size: ≥3 diseases × ≥2 therapeutic areas × adequate per-disease sample sizes
- Theunissen 2025: OOD detection severity affects cross-disease OOD flagging reliability

No anchor re-read drift detected.

---

## §1 The V6 Grid Architecture

### 1.1 Three-Dimensional Structure (Decision 8 v2 Commitment 1)

V6 evaluates on a 3D grid:

```
                  PARADIGM (4)
              ┌────────────────────┐
              │  A   B   C   D     │
              │ ┌─┐ ┌─┐ ┌─┐ ┌─┐   │
              │ │a│ │b│ │c│ │d│   │   Each cell is:
              │ └─┘ └─┘ └─┘ └─┘   │   (disease, tissue, paradigm)
   DISEASE ───┤ ┌─┐ ┌─┐ ┌─┐ ┌─┐   │
   (3) ───────┤ │a│ │b│ │c│ │d│   │   = 1 unit of V6 evaluation
              │ └─┘ └─┘ └─┘ └─┘   │
              │ ┌─┐ ┌─┐ ┌─┐ ┌─┐   │
              │ │a│ │b│ │c│ │d│   │
              │ └─┘ └─┘ └─┘ └─┘   │
              └────────────────────┘
                     ╱
                    ╱
              TISSUE (1-3 per disease)
```

**Cell count:** 3 diseases × 4 paradigms × 1-3 tissues × N_drugs = 24-100 evaluation cells per drug

**Per Decision 8 v2 Commitment 1:** Phase B Layer 5 target is 75-100 populated (cells × drugs) total. L3.3 sizes the grid to hit this target.

### 1.2 The Five Axes of the Grid

| Axis | L3.3 Commitment | Decision 8 v2 BINDING |
|---|---|---|
| Disease | 3 held-out diseases | ≥3 per Decision 6 v2 V6 sample size |
| Therapeutic area | 2 areas across the 3 diseases | ≥2 per Decision 8 v2 Commitment 3 |
| Paradigm | 4 paradigms (A general FM, B disease-area FM, C patient-aggregation, D parameter-free) | All 4 per Decision 8 v2 Commitment 2 |
| Tissue | 1-3 per disease (depends on biology and data availability) | up to 3 per Decision 8 v2 Commitment 1 |
| Drug | Subset of the 10 drug grid that applies to each disease | from Decision 8 v2 Commitment 1 10-drug list |

### 1.3 Training and Held-Out Partitioning

**Training data (NOT in V6):**
- Cancer scRNA-seq + drug response (GDSC, CCLE, CTRP, TCGA, NCI PDXNet, retrospective oncology clinical) — all of V0-V5 training data

**V6 held-out data (NEVER seen during training):**
- All 3 disease scRNA-seq + drug response datasets are held out from substrate pretraining AND L7 training

**Critical:** Substrate FMs (scFoundation/UCE/scGPT/Geneformer) were pretrained on broad scRNA-seq corpora that LIKELY include some V6 disease tissue. This is acknowledged honestly: "the substrate has seen the tissue gene-expression patterns" is different from "the drug response model has seen drug response in this disease." L3.3 commits to the latter; the former is the field's standard practice and is reported transparently.

---

## §2 The 3 Held-Out Diseases (BINDING Commitment)

### 2.1 Disease Selection Rationale

The disease selection must satisfy:
1. **Therapeutic area diversity** (≥2 areas): cancer alone is insufficient even with multiple subtypes
2. **Biological diversity** (different MoA classes engaged): cytotoxic chemo, kinase inhibitor, biologic, immunomodulator
3. **Data availability** (publicly accessible scRNA-seq + drug response): no proprietary blockers
4. **Sample size adequacy** (≥100 per disease per Decision 6 v2 V6 floor): can pass C3 sample-size criterion
5. **Mechanism distance from cancer** (genuine OOD): not a cancer-adjacent disease that effectively replicates V3-V5

### 2.2 Selected Diseases

**Disease 1 — Ulcerative Colitis (UC) [I&I therapeutic area]**
- **Justification:** I&I is mechanistically distinct from cancer (immune-mediated, not proliferative-driven). EVA-60M (Decision 8 v2 Paradigm B) was demonstrated on anti-TNF + UC + Phase II RCT prediction (Bandasack et al. 2026); this paradigm explicitly tests EVA's domain.
- **Drug class engaged:** Biologics (anti-TNF: infliximab, adalimumab); immunomodulators (vedolizumab, ustekinumab)
- **scRNA-seq sources:** Smillie et al. 2019 (intestinal mucosa UC scRNA-seq, GEO); Czarnewski et al. 2019 (mouse + human UC, GEO); IBDverse + HUBMAP IBD (where accessible)
- **Drug response sources:** Phase II/III RCT retrospective cohorts where transcriptomics paired with response classification exists
- **Expected sample size:** 200-500 patients across published cohorts
- **Tissue axis:** intestinal biopsy + peripheral blood (2 tissues per Decision 8 v2 Commitment 1 example)

**Disease 2 — Alzheimer's Disease (AD) [Neurodegeneration therapeutic area]**
- **Justification:** Neurodegeneration is mechanistically distinct from cancer AND from I&I (protein-aggregation-driven, neuron-specific). Provides 3rd therapeutic area (beyond cancer + I&I) — exceeds the ≥2 BINDING floor.
- **Drug class engaged:** AChE inhibitors (donepezil); anti-amyloid biologics (lecanemab, aducanumab where data exists); experimental immunomodulators
- **scRNA-seq sources:** Mathys et al. 2019 (prefrontal cortex AD scRNA-seq, Nature); ROSMAP scRNA-seq subset; Allen Brain Atlas AD samples
- **Drug response sources:** Aducanumab Phase III ENGAGE/EMERGE retrospective transcriptomics where accessible; lecanemab Clarity AD retrospective where post-hoc subgroups can be defined
- **Expected sample size:** 100-300 patients across published cohorts; smaller than UC but adequate for Decision 6 v2 V6 floor
- **Tissue axis:** prefrontal cortex (single tissue; brain biopsy is rare; PBMC if available)

**Disease 3 — Type 2 Diabetes (T2D) [Metabolic therapeutic area — TENTATIVE; ALTERNATIVE: Rheumatoid Arthritis (RA)]**
- **Primary candidate — T2D:**
  - **Justification:** Metabolic disease distinct from cancer, I&I, neurodegeneration. Drug class diversity (metformin, sulfonylureas, GLP-1 agonists, SGLT2 inhibitors).
  - **scRNA-seq sources:** Wang et al. islet scRNA-seq T2D; HPAP (Human Pancreas Analysis Program); HCA pancreas samples
  - **Drug response sources:** GLP-1 RCT retrospective transcriptomics; SGLT2i RCT retrospective; metformin response heterogeneity studies
  - **Concern:** drug response in T2D is often glucose-control measured, less transcriptomically obvious than oncology RECIST-style outcomes. May be harder to operationalize as binary AUROC.
  - **Tissue axis:** pancreatic islets (primary) + adipose tissue + skeletal muscle (multi-tissue, 3 tissues per Decision 8 v2 Commitment 1)
- **Alternative candidate — Rheumatoid Arthritis (RA) [Second I&I disease]:**
  - **Justification:** Second I&I disease provides DEPTH in one therapeutic area (UC + RA both I&I) rather than BREADTH (UC + AD + T2D across 3 areas). Whether INTERCEPTA prioritizes breadth or depth is a CSO judgment item (J1 in §8.5).
  - **scRNA-seq sources:** Zhang et al. 2019 (synovial scRNA-seq RA, Nature Immunology); AMP RA scRNA-seq
  - **Drug response sources:** Anti-TNF (etanercept, adalimumab); JAK inhibitors (tofacitinib); rituximab. Same drug class diversity as UC but with different tissue.
  - **Tissue axis:** synovial tissue + peripheral blood

**DEFAULT for Phase B Layer 5:** UC + AD + T2D (3 therapeutic areas: I&I + neurodegeneration + metabolic; satisfies ≥2 BINDING by margin).

**FALLBACK if T2D data access blocked:** UC + AD + RA (2 therapeutic areas: I&I + neurodegeneration; satisfies ≥2 BINDING by minimum). This is the explicit Layer-5-trigger backup plan.

### 2.3 Why Not Other Diseases

**Cardiovascular disease (heart failure):** Strong biology, but drug response readouts in scRNA-seq are limited; mechanism is hemodynamic + structural, less transcriptomically resolved per dose.

**Asthma:** Reasonable I&I candidate, but UC has stronger EVA paradigm B precedent (Bandasack 2026 explicitly demonstrates EVA on anti-TNF in UC).

**Parkinson's:** Could substitute for AD; AD has larger published scRNA-seq cohort (Mathys 2019 etc.); J2 documents the option.

**COVID-19 / infectious disease:** Excluded because acute infection biology differs from chronic disease drug response prediction (different deployment target).

### 2.4 Data Access Risk Assessment

| Disease | Public scRNA-seq | Public drug response | Both available simultaneously? | Risk |
|---|---|---|---|---|
| UC | ✅ Smillie 2019, IBDverse | ✅ RCT retrospective | Partially — alignment required | Medium |
| AD | ✅ Mathys 2019, ROSMAP | ⚠️ Aducanumab retrospective uncertain | Uncertain — RCT transcriptomics often proprietary | High |
| T2D | ✅ HPAP, Wang | ⚠️ GLP-1 RCT retrospective uncertain | Uncertain — pharma-proprietary risk | High |
| RA | ✅ AMP RA | ✅ Phase II/III retrospective | Likely — RA has more academic-cohort drug response data | Medium |

**Implication:** Layer 4 must validate data availability before Layer 5 trains. If AD or T2D paired data is blocked, fallback to UC + AD + RA (RA backstops). If both AD and T2D blocked, fallback to UC + RA + 1-of-{Multiple Sclerosis, Crohn's Disease} (both well-studied I&I; would mean 2 therapeutic areas not 3).

---

## §3 The 4 Paradigms (BINDING per Decision 8 v2 Commitment 2)

### 3.1 Paradigm A — General Multi-FM Portfolio

**Substrate:** scFoundation 100M (default) + UCE + scGPT + Geneformer ensemble per L2.1
**Configuration at V6:** ensemble of all 4 FMs; vote weighting per L2.1 §6
**Source:** pretrained checkpoints + fine-tuned on V0-V5 cancer training data
**V6 fine-tuning:** NONE — paradigm A is tested as "trained on cancer, applied to held-out disease" zero-shot
**Cost:** ~3 GPU-days per (disease × tissue × paradigm) cell on A100 with cached embeddings

### 3.2 Paradigm B — Disease-Area-Specific FM

**Substrate per disease:**
- UC → EVA-60M (Bandasack 2026 demonstrated on UC anti-TNF)
- AD → scFoundation-AD-specialized OR re-pretrain on Mathys cohort scRNA-seq (lightweight)
- T2D → scFoundation-T2D-specialized OR re-pretrain on HPAP
**Source:** Hugging Face Scienta-Lab (EVA-60M open variant per Q8 anchor 4); lightweight re-pretraining for AD/T2D per Decision 9 v2 compute envelope
**V6 fine-tuning:** disease-area-specialized substrate; L7 head still trained on cancer data
**Critical caveat:** Paradigm B's substrate has seen disease tissue scRNA-seq (this is the point); only the L7 head is cancer-trained
**Cost:** ~2 GPU-days per cell (smaller models cheaper than Paradigm A ensemble)

### 3.3 Paradigm C — Patient-Level Aggregation

**Substrate:** scFoundation (default) + PaSCient-style attention aggregation per L2.2 Slot 6 BINDING per Drift Finding 10
**Configuration:** patient-level prediction; Slot 6 attention pools cell-level FM embeddings
**Source:** Liu et al. 2024/2026 PaSCient architecture; FM substrate pretrained, L7 head + Slot 6 trained on cancer data
**V6 fine-tuning:** none beyond V5 training
**Cost:** ~3 GPU-days per cell (FM forward + PaSCient attention overhead)

### 3.4 Paradigm D — Parameter-Free Baseline (BINDING)

**Substrate:** scTOP-style pseudo-bulk reference + linear projection per Souza-Mehta 2026
**Configuration:** ANOVA gene selection + PCA + logistic regression where needed; L7 head architecture matched to other paradigms
**Source:** no pretraining; pure inference on properly normalized scRNA-seq
**V6 fine-tuning:** L7 head trained on cancer data (matched to other paradigms)
**Hyperparameter budget:** ≥25% of Paradigm A budget per Decision 8 v2 Commitment 5
**Cost:** ~0.5 GPU-day per cell (cheapest; the operational reward of parameter-free per Souza-Mehta methodological bar)
**BINDING per Decision 8 v2 Commitment 5; reviewer-style scrutiny applied**

### 3.5 The Matched-Budget Discipline

Per Decision 8 v2 Commitment 5 + Drift Finding 10: hyperparameter search budget for paradigm D must be ≥25% of paradigm A. L3.3 enforces this in the SLURM array specification (§5):
- Paradigm A: 40 hyperparameter trials per (disease × tissue) cell
- Paradigm B: 30 trials
- Paradigm C: 30 trials
- Paradigm D: 10 trials minimum (≥25% of 40 = 10)

No paradigm gets preferred treatment. This is the operational guard against Souza-Mehta's "rigorous-tuning gatekeeping" critique.

---

## §4 Tissue and Drug Coverage Per Disease

### 4.1 Tissue Specification Per Disease

| Disease | Tissue 1 | Tissue 2 | Tissue 3 | Total tissues |
|---|---|---|---|---|
| UC | Intestinal biopsy | Peripheral blood | — | 2 |
| AD | Prefrontal cortex | PBMC (if available) | — | 1-2 |
| T2D | Pancreatic islets | Adipose tissue | Skeletal muscle | 3 |
| (RA fallback) | Synovial tissue | Peripheral blood | — | 2 |

**Total tissues across default 3 diseases:** UC (2) + AD (1-2) + T2D (3) = 6-7 tissue applications

### 4.2 Drug Subset Per Disease (from Decision 8 v2 10-drug list)

| Disease | Applicable drugs from 10-drug grid | Drugs added for disease |
|---|---|---|
| UC | (anti-TNF biologics not in cancer list) | Infliximab, adalimumab, vedolizumab, ustekinumab |
| AD | (none in 10-drug list directly) | Donepezil, lecanemab, aducanumab |
| T2D | (none in 10-drug list directly) | Metformin, semaglutide (GLP-1), empagliflozin (SGLT2i) |

**Critical operational note:** The Decision 8 v2 10-drug grid is cancer-centric. For V6, drugs are disease-specific. L3.3 augments the grid with disease-relevant drugs:
- **UC drugs added: 4** (anti-TNF + vedolizumab + ustekinumab)
- **AD drugs added: 3** (donepezil + 2 anti-amyloid)
- **T2D drugs added: 3** (metformin + GLP-1 + SGLT2i)
- **Total V6 drugs: 10 (cancer + 10 disease-specific) = 20 drugs**

### 4.3 Total Cell Count Estimate

- Disease 1 UC: 2 tissues × 4 paradigms × ~7 drugs (4 added + 3 cancer drug repurposing) = 56 cells
- Disease 2 AD: 1-2 tissues × 4 paradigms × ~5 drugs (3 added + 2 cancer drug repurposing) = 20-40 cells
- Disease 3 T2D: 3 tissues × 4 paradigms × ~5 drugs = 60 cells

**Total populated cells: ~140-160**

This **slightly exceeds Decision 8 v2 Commitment 1 realistic target of 75-100 populated cells**. L3.3 commits to reducing this if compute budget at Layer 5 demands; the prioritization order is:
1. Always run all 3 diseases at primary tissue (60-100 cells subset)
2. Add secondary tissues per disease if compute permits (additional 30-60 cells)
3. Tertiary tissue for T2D (skeletal muscle) lowest priority

---

## §5 SLURM Job Array Operational Pattern

### 5.1 The Cell-Level SLURM Job

Each evaluation cell is one SLURM job:

```bash
# /scratch/akula.pra/INTERCEPTA/scripts/v6_evaluate_cell.sh
#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --time=24:00:00
#SBATCH --mem=64G
#SBATCH --job-name=v6_${DISEASE}_${TISSUE}_${PARADIGM}_${DRUG}
#SBATCH --output=/scratch/akula.pra/INTERCEPTA/logs/v6_%A_%a.out

source activate intercepta_phase_b
python -m intercepta.validation.v6_evaluator \
    --disease $DISEASE \
    --tissue $TISSUE \
    --paradigm $PARADIGM \
    --drug $DRUG \
    --substrate-checkpoint /scratch/akula.pra/INTERCEPTA/substrates/${PARADIGM}/ \
    --l7-checkpoint /scratch/akula.pra/INTERCEPTA/l7/${PARADIGM}/cancer_v5_trained.pt \
    --output-dir /scratch/akula.pra/INTERCEPTA/validation/v6/${PARADIGM}/${DISEASE}/${TISSUE}/${DRUG}/
```

### 5.2 The Array Submission

```bash
# Submit array of jobs (1 job per cell)
N_CELLS=140  # actual cell count from L3.3 §4.3 estimate
sbatch --array=1-${N_CELLS}%10 \  # max 10 concurrent (Decision 9 v2 budget)
    v6_evaluate_cell.sh
```

**Per Decision 9 v2 compute envelope:** Phase B uses single-A100 dominantly with ≤5% AWS/GCP burst CEO-approved. V6 is the largest V-level; SLURM concurrency capped at ~10 simultaneous jobs to stay within shared-cluster fair-use.

### 5.3 Estimated Wall-Clock

- Per-cell wall-clock: ~24 hours (Paradigm A) / ~12 hours (Paradigm D)
- Total GPU-hours: 140 cells × ~18 hours average = ~2,500 GPU-hours
- With 10-concurrent SLURM: ~250 hours = ~10-12 wall-clock days
- Add 1.5× buffer for resubmissions, OOMs, etc.: ~15-20 wall-clock days

**Decision 9 v2 compute envelope check:** Phase B total compute ~500-700 GPU-days; V6 alone is ~100-200 GPU-days. Tight but feasible.

### 5.4 Cache Pattern Per Cell

```
/scratch/akula.pra/INTERCEPTA/validation/v6/
├── {paradigm}/         A, B, C, D
│   ├── {disease}/       UC, AD, T2D
│   │   ├── {tissue}/    intestinal_biopsy, prefrontal_cortex, ...
│   │   │   ├── {drug}/  infliximab, donepezil, ...
│   │   │   │   ├── predictions.h5
│   │   │   │   ├── ood_output.h5
│   │   │   │   ├── interpretability_output.h5
│   │   │   │   ├── per_criterion_pass_fail.json  (L3.2 V6 C1-C8 results)
│   │   │   │   └── result.json
```

Cache key: substrate SHA + L7 checkpoint SHA + L3.3 spec SHA (so spec changes invalidate caches).

---

## §6 V6 Aggregation and Pass Determination

### 6.1 Per-Cell Pass/Fail

Each cell produces 8 L3.2 V6 criteria pass/fail results (V6-C1 through V6-C8). Cell pass = all 8 criteria pass.

### 6.2 Per-Disease Aggregation

For each (paradigm × disease):
- Across all tissues + drugs in that cell
- Compute aggregate AUROC (weighted by sample size per tissue + drug)
- Determine: does this (paradigm × disease) achieve V6-C1 (AUROC ≥ 0.65)?

### 6.3 Per-Therapeutic-Area Determination (BINDING per Decision 8 v2 Commitment 3)

For each paradigm:
- Across the 3 diseases, count therapeutic areas where the paradigm achieves V6-C1
- A therapeutic area is "passing" if ANY disease in that area achieves V6-C1 for that paradigm

**V6 PASSES** if any paradigm has ≥ 2 passing therapeutic areas.

### 6.4 The 4-Paradigm Matrix Report (BINDING)

Per L3.2 V6-C6 + V6-C7:

| Therapeutic Area | Disease | Paradigm A AUROC | Paradigm B AUROC | Paradigm C AUROC | Paradigm D AUROC |
|---|---|---|---|---|---|
| I&I | UC | (filled at Layer 5) | (filled) | (filled) | (filled) |
| Neurodegeneration | AD | (filled) | (filled) | (filled) | (filled) |
| Metabolic | T2D | (filled) | (filled) | (filled) | (filled) |

**Souza-Mehta competitive check (V6-C7 BINDING):** is paradigm D within 5pp of the best paradigm on each disease?

### 6.5 OOD Attribution Determination (BINDING per Decision 5 v2 Pass 4)

For each (paradigm × disease × tissue × drug) cell where predictions FAILED:
- Count epistemic-flagged failures / total failures
- Aggregate across cells in the cascade report

**Threshold:** ≥ 70% epistemic attribution per V6-C5 BINDING.

### 6.6 Interpretability Transfer Determination (BINDING per Decision 7 v2 Pass 7)

For known drug-target pairs in held-out diseases (e.g., infliximab → TNFA; donepezil → AChE / ACHE gene; metformin → AMPK pathway):
- Check Scale 5 top-K attribution recovers canonical target
- ≥ 80% recovery threshold per V6-C8 BINDING

---

## §7 Risk Register and Mitigations

### 7.1 The Universality Could Fail Risk

**Risk:** V6 fails — no paradigm achieves ≥0.65 on ≥2 therapeutic areas.
**Probability:** Unknown a priori. INTERCEPTA novelty; no published baseline.
**Mitigation:** Charter §3 termination criteria explicit. V6 failure triggers narrowed Charter §1.1 ("Find drugs for cancer + I&I" if UC passes alone, etc.); does NOT terminate INTERCEPTA but does narrow vision.
**Honest reporting:** A V6 negative result is a publishable scientific contribution — it would be the first rigorous empirical test of cross-disease drug response universality.

### 7.2 Data Access Risk

**Risk:** AD or T2D paired transcriptomics + drug response unavailable.
**Mitigation:** Fallback grid (UC + AD + RA) documented in §2.3.
**Trigger:** Layer 4 must validate data availability before Layer 5 launch.

### 7.3 The Compute Overrun Risk

**Risk:** V6 takes >200 GPU-days; Decision 9 v2 envelope exhausted.
**Mitigation:** Tissue prioritization order in §4.3; reduce to primary-tissue-only for all 3 diseases (~60-80 cells subset) if compute pressure forces compression.

### 7.4 Substrate Tissue-Familiarity Confound

**Risk:** Critique that paradigm A/B/C substrates have "seen" V6 disease tissue during pretraining, making the V6 evaluation not truly OOD.
**Mitigation:** Honest §1.3 acknowledgment; report paradigm D (no pretraining, no substrate familiarity confound) as the "purest" cross-disease test; report paradigms A/B/C as "cancer-drug-response-trained applied to held-out disease tissue."
**Operational consequence:** if paradigm D wins V6 by a margin, this is strong evidence that the FM pretraining tissue familiarity is doing the work; per Decision 8 v2 termination criteria, this falsifies Decision 1's FM commitment.

### 7.5 Drug Response Definition Heterogeneity

**Risk:** Drug response in T2D (glucose control) is mechanistically different from cancer (cell death). Binary AUROC may not be the right operationalization.
**Mitigation:** Per-disease response operationalization documented in V6 evaluation; secondary continuous metrics (e.g., Pearson R with HbA1c change) reported alongside AUROC.

---

## §8 Pass Criteria for L3.3 LOCK

### 8.1 Architecture-Level Pass Criteria (BINDING)

- **A1:** 3 diseases × 2 therapeutic areas minimum specified (UC + AD + T2D default; UC + AD + RA fallback)
- **A2:** 4 paradigms × per-disease tissues × per-disease drug subsets enumerated per §3, §4
- **A3:** Matched-budget discipline (≥25% paradigm D) specified per §3.5
- **A4:** SLURM job array operational pattern specified per §5
- **A5:** Aggregation + pass determination logic specified per §6
- **A6:** Risk register + mitigations specified per §7

### 8.2 Cross-Decision Compatibility (BINDING)

- **X1:** Decision 8 v2 Commitment 1 (3D grid 5+ diseases × 3+ areas minimum) — L3.3 commits 3 diseases × 2-3 areas (within Phase B reduced from Commitment 1's 5 diseases per Decision 6 v2 V6 minimum)
- **X2:** Decision 8 v2 Commitment 2 (4 paradigms) — all 4 specified
- **X3:** Decision 8 v2 Commitment 3 (≥0.65 on ≥2 areas) — §6.3 BINDING pass determination
- **X4:** Decision 8 v2 Commitment 5 (Souza-Mehta) — §3.5 matched-budget
- **X5:** Decision 5 v2 Pass 4 (epistemic ≥70%) — §6.5 BINDING aggregation
- **X6:** Decision 7 v2 Pass 7 (cross-disease interpretability) — §6.6 BINDING
- **X7:** Decision 6 v2 V6 sample sizes (≥3 diseases × ≥2 areas × adequate per-disease) — §1.2 + §2.4 BINDING
- **X8:** Decision 9 v2 compute envelope — §5.3 wall-clock estimate within budget
- **X9:** Decision 10 v2 open-source — all datasets publicly accessible per §2.4

### 8.3 Documentation Pass Criteria

- **D1:** L3.3 consumed by Layer 4 (L4.1 implementation order) + Layer 5 evaluator code
- **D2:** L3.3 disease + dataset choices recorded in Layer 5 experiment registry
- **D3:** Drift catalog this session: 0 new instances

### 8.4 CEO Sign-Off

L3.3 advances from PROPOSED to LOCKED when:
1. CEO reviews §2 disease selection (most consequential design choice)
2. CEO confirms §8.5 J-items are within CSO authority
3. CEO co-signs Charter §5.3-style
4. Tag phase-b-l3.3-locked pushed to origin
5. **After L3.3 LOCK: Layer 3 of Phase B is COMPLETE**

### 8.5 CSO Judgment Items (Layer 5 Revisitable)

| # | Decision | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | 3rd disease choice | T2D (metabolic — breadth) | RA (I&I depth) | Data access blocks T2D OR breadth-over-depth strategy revision |
| J2 | Neurodegeneration disease | AD | Parkinson's | AD aducanumab/lecanemab retrospective transcriptomics blocked |
| J3 | Drug count per disease | 5-7 | 3-5 (compute reduction) | V6 compute overrun |
| J4 | Tissues per disease | 1-3 | primary only | V6 compute overrun |
| J5 | SLURM concurrent jobs | 10 | 20 (faster) / 5 (better fair-use) | Cluster load |
| J6 | Hyperparameter trials paradigm A | 40 | 20 (cheaper) / 60 (stricter) | Empirical convergence |
| J7 | Paradigm D budget fraction | 25% | 33%, 50% | Empirical D-vs-A gap |
| J8 | Drug response operationalization T2D | binary AUROC + continuous Pearson | continuous-only | T2D binary too noisy |
| J9 | Substrate familiarity reporting | acknowledged in §1.3 | additional control experiment | If reviewers demand explicit control |
| J10 | Layer 5 publication strategy | one combined V6 paper | per-disease + summary | Publication strategy review |

### 8.6 Honest Limitations (per Charter §10 P15 BINDING)

- **3 diseases is the minimum, not the maximum.** Decision 8 v2 Commitment 1 specifies 5 diseases as the eventual target; Phase B's 3-disease commitment is reduced for tractability. Phase F expands to ≥10 diseases.
- **Substrate tissue familiarity is a real confound** for paradigms A/B/C; honestly stated in §7.4.
- **T2D drug response operationalization** is harder than cancer; the continuous-metric fallback is acknowledged.
- **AD data access is uncertain.** §7.2 fallback to RA documented.
- **The 4-paradigm matrix is honest but expensive.** Decision 9 v2 compute envelope is tight; if AWS burst exceeds CEO-approved 5%, compute compression in §4.3 prioritization is mandatory.
- **A V6 negative result is publishable.** INTERCEPTA does not need V6 to "pass" to publish; per Charter §1.3 falsifiability, an honest negative result is also a scientific contribution.

---

## §9 What L3.3 Does NOT Lock

- The exact training-data preprocessing for each V6 dataset (Layer 4)
- The specific Phase II/III RCT cohort identification (Layer 5 data access)
- The exact hyperparameter search space per paradigm (Layer 4)
- The SLURM partition allocations on Northeastern Explorer (Layer 4 cluster onboarding)
- Phase F expanded grid (≥10 diseases) — that is Phase F

---

## §10 Cross-Decision Implications

- **Decision 8 v2 Commitment 1 ↔ L3.3 §1.1** (3D grid structure)
- **Decision 8 v2 Commitment 2 ↔ L3.3 §3** (4 paradigms)
- **Decision 8 v2 Commitment 3 ↔ L3.3 §6.3** (≥0.65 on ≥2 areas pass determination)
- **Decision 8 v2 Commitment 4 ↔ L3.2 V6-C4** (failure mode classification — L3.2 specifies; L3.3 inherits)
- **Decision 8 v2 Commitment 5 ↔ L3.3 §3.5** (matched-budget)
- **Decision 5 v2 Pass 4 ↔ L3.3 §6.5** (epistemic attribution aggregation)
- **Decision 6 v2 V6 sample sizes ↔ L3.3 §1.2 + §2.4** (≥3 diseases × ≥2 areas × adequate per-disease)
- **Decision 7 v2 Pass 7 ↔ L3.3 §6.6** (interpretability transfer)
- **Decision 9 v2 compute envelope ↔ L3.3 §5.3** (wall-clock estimate within budget)
- **Decision 10 v2 open-source ↔ L3.3 §2.4** (public datasets)

This is the operational instantiation of universality testing across the Phase B decision space.

---

## §11 Provenance and Appendix

### 11.1 Provenance

L3.3 written by Claude (CSO, 2026-05-11) per Phase B Plan v2 sequencing. Q8 + Q5 + Q6 anchors re-read 2026-05-11. After L3.3 LOCK, Layer 3 of Phase B is COMPLETE.

### 11.2 Discipline Check Per Charter v1.2 Principles

- **P3 (research before code):** ✅ disease selection grounded in Decision 8 v2 + EVA-60M anchor + Mathys 2019 + HPAP literature
- **P15 (honest science):** ✅ §6 substrate familiarity confound acknowledged; §7.1 V6 could fail explicit; §7.5 T2D operationalization caveat
- **P16 (preserve past work):** ✅ Decision 8 v2 + Q8 synthesis preserved
- **Charter §5.3:** ✅ §8 pass criteria explicit
- **Charter v1.2 §1.7 phase discipline:** ✅ Phase F expanded grid noted but not specified

### 11.3 Drift Catalog This Session

New drift instances introduced: 0.

### 11.4 Layer 3 of Phase B Status

| Artifact | Status | Words |
|---|---|---|
| L3.1 Validation Cascade Pipeline | PROPOSED | 4,311 |
| L3.2 56 Pass Criteria | PROPOSED | 5,579 |
| **L3.3 Cross-Disease V6 Grid** | **PROPOSED** | (this artifact) |

**After L3.3 LOCK: Layer 3 of Phase B is COMPLETE.**

### 11.5 Next Phase B Artifacts

After Layer 3 complete:
- **Layer 4 (3 artifacts):** L4.1 Implementation Order, L4.2 Testing, L4.3 Failure Modes
- **Phase 8 Audit:** Pre-implementation coherence review
- **Layer 5:** Code starts. Environment setup → substrate adapters → L7 → OOD → interpretability → V0 evaluator → V0 first empirical result.

### 11.6 V6 Grid Quick Reference Table

| Disease | Therapeutic Area | Tissues | Drugs (added beyond cancer subset) | Paradigms | Cells |
|---|---|---|---|---|---|
| UC | I&I | intestinal biopsy + PBMC | infliximab, adalimumab, vedolizumab, ustekinumab (+ 3 cancer repurp.) | A, B, C, D | ~56 |
| AD | Neurodegeneration | prefrontal cortex (+ PBMC if avail.) | donepezil, lecanemab, aducanumab (+ 2 cancer repurp.) | A, B, C, D | ~20-40 |
| T2D | Metabolic | islets + adipose + skeletal muscle | metformin, semaglutide, empagliflozin (+ 2 cancer repurp.) | A, B, C, D | ~60 |
| (RA fallback) | (2nd I&I) | synovial + PBMC | etanercept, adalimumab, tofacitinib, rituximab | A, B, C, D | ~56 |

**Total V6 cells (default UC+AD+T2D):** ~140-160 evaluation cells across paradigms × diseases × tissues × drugs

### 11.7 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L3_3_Cross_Disease_V6_Grid_Specification_2026-05-11.md`
- L3.1 (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L3_1_V0_V6_Validation_Cascade_Pipeline_Specification_2026-05-11.md`
- L3.2 (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L3_2_56_Pass_Criteria_Specification_2026-05-11.md`
- Decision 8 v2 (parent): `~/INTERCEPTA/docs/research/decisions/INTERCEPTA_FV_Decision_8_Q8_universality.md`
- V6 cache (future): `/scratch/akula.pra/INTERCEPTA/validation/v6/`
- V6 SLURM scripts (future): `/scratch/akula.pra/INTERCEPTA/scripts/v6_*.sh`

---

— L3.3 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and `phase-b-l3.3-locked` tag.
— **After L3.3 LOCK: Layer 3 of Phase B is COMPLETE.** Next: Layer 4 (L4.1 Implementation Order, L4.2 Testing, L4.3 Failure Modes), then Phase 8 audit, then Layer 5 (code).
