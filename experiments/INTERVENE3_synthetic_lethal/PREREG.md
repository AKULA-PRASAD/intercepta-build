# INTERVENE3 — PRE-REGISTRATION (frozen BEFORE scoring)

**Question.** INTERVENE2 found that **93.2% (3416/3664)** of DEPEND1's validated SELECTIVE cancer
dependencies are UNDRUGGED (de-novo-chemistry-gated). Synthetic lethality (SL) is the one clinically
validated therapeutic route *around* undruggability (precedent: PARP inhibitors in BRCA-mutant tumours —
drug the SL partner of an otherwise-untargetable lesion). **Can a DepMap-derivable SL signal open a
DRUGGED route to those undruggable validated dependencies?**

We use **paralog synthetic lethality**, the most robustly DepMap-derivable SL class: paralogs buffer each
other, so loss of one paralog makes the cell dependent on the other. This is a CONDITIONAL differential-
dependency signal, **deliberately NOT raw co-dependency correlation** (which reflects same-pathway
co-essentiality, not SL — the field-known false equivalence we guard against).

## 0. Hard scope (binds every claim; frozen)
- DepMap paralog-SL is an **in-silico genetic-interaction signal**, NOT a validated drug combination and
  NOT clinical. A "drugged SL partner" is a **hypothesis for a combination/context experiment**, not a therapy.
- **Co-dependency correlation ≠ SL.** Guarded structurally: our test conditions dependency on the *loss
  status* of the partner (expression tertile), never correlates two dependency profiles; and it is
  validated against a curated known-SL set and two nulls.
- "Drugged" = has a ChEMBL-annotated ligand (INTERVENE2 mapper), NOT efficacious/selective/safe.
- Cancer cell-line Chronos layer; NOT wet-lab, NOT patient response, NOT a novel-pathogen result.

## 1. Inputs (open; SHA-256 recorded at scoring)
- DepMap Chronos CRISPR gene-effect: `/Users/kalki/kaalcura/data/depmap_crispr_gene_effect.csv`
  (1095 lines × 17931 genes) — SHA `d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00`
  (identical to the file used by DEPEND1/F3CLIN1/INTERVENE2).
- DepMap expression: `/Users/kalki/kaalcura/data/depmap_expression.csv` (1393 lines × 19177 genes;
  988 lines shared with CRISPR).
- **Paralog universe (open source, fetched once, SHA-recorded):** human paralog pairs from the
  Ryan/De Kegel lab `cancergenetics/paralog_seq_similarity` repo, `data/ens111_human_SL.csv`
  (Ensembl 111-derived; 23,734 pairs with entrez IDs + sequence identity). Stored slim at
  `$INTERCEPTA_DATA/intervene3/paralog_pairs_slim.tsv`. Source URL + SHA recorded in results.
  We do NOT use that file's own `SL` label as our signal (would be circular); it is reported only as a
  descriptive secondary cross-reference.
- **Known-SL ground truth (G1):** the lab's frozen experimentally/literature-curated list
  `cancergenetics/paralog_SL_prediction/local_data/validated_SLs.txt` (12 pairs: SMARCA2/SMARCA4,
  ARID1A/ARID1B, STAG1/STAG2, VPS4A/VPS4B, DDX17/DDX5, ENO1/ENO2, SMARCC1/SMARCC2, CREBBP/EP300, UBB/UBC,
  MAGOH/MAGOHB, ME2/ME3, FAM50A/FAM50B). External, pre-existing — not chosen by us. All 12 have both genes
  in DepMap CRISPR+Expr and are tested directly regardless of Ensembl-111 universe membership.
- ChEMBL drug-target KB `$INTERCEPTA_DATA/intervene/drug_targets.tsv` + max_phase cache
  `$INTERCEPTA_DATA/intervene2/chembl_max_phase.json` (INTERVENE2 mapper, reused verbatim).
- IntOGen Compendium (F3CLIN1) for the patient-driver subset.

## 2. Selective / undrugged set (re-derived, must reproduce)
DEPEND1 frozen definition on the full Chronos matrix: dep = effect < −0.5; SELECTIVE = dep_frac ∈
[0.01, 0.50]; pan-essential (>0.90) EXCLUDED. **Assert n_selective == 3664.** Undrugged = INTERVENE2
mapper returns no human ChEMBL ligand.

## 3. SL test (frozen)
For an ordered paralog direction (A→B): using the 988 CRISPR∩Expr lines, split lines by A's expression
into **bottom tertile (A-low)** vs **top tertile (A-high)** (per-gene quantiles on lines with non-null
expr(A) and non-null Chronos(B); require ≥10 lines/group). Test whether Chronos(B) is **more negative
(stronger dependency)** in A-low vs A-high:
- one-sided **Mann-Whitney U** (alt: A-low < A-high),
- **Cliff's delta** effect size (δ = 2U/(n₁n₂) − 1; more-negative B in A-low ⇒ δ<0),
- median difference Δmed = median(B|A-low) − median(B|A-high).

A **pair is SL-detected** if ≥1 of its two directions satisfies **all** of: (i) p < p\*, (ii) Δmed < 0,
(iii) δ ≤ −0.10. Multiple testing: **BH-FDR < 0.10** over the full directional family (paralog universe ∪
12 curated pairs); p\* = the largest p in that family with BH-FDR < 0.10. The SAME absolute p\* and
criteria (ii)/(iii) are applied to every set below (apples-to-apples across families).

## 4. Pre-registered GATES (frozen before scoring)
- **G1 (validation, decision gate).** PASS iff:
  (a) recovery of the 12 curated known-SL pairs **≥ 0.50** (≥6/12 SL-detected), AND
  (b) recovery ≥ **3×** the paralog-universe base rate (fraction of all paralog pairs SL-detected), AND
  (c) recovery clearly above the **random non-paralog gene-pair** null (K=5000 pairs, seed 42, both genes
      in CRISPR+Expr, not a known paralog; same p\* and criteria).
  **If G1 fails, STOP and report the honest negative — do not proceed to application.**
- **G2 (application, DESCRIPTIVE — reported whatever it is, only if G1 PASS).** Fraction of the 3416
  UNDRUGGED validated selective dependencies that have ≥1 SL-detected paralog partner which **IS drugged**
  in ChEMBL (and the approved-drug subset). Plus the patient-driver (IntOGen) slice. This is the
  vision-relevant number: how much of the 93%-undrugged ceiling paralog-SL opens a real existing-drug
  route to. Examples listed.

## 5. Reproducibility
Deterministic; seed 42, K=5000. `run.py` → `results/INTERVENE3_metrics.json` (sorted keys) +
`results/INTERVENE3_payload.sha256`. Payload = sorted-key JSON of numeric results (excludes
verdict/provenance); run twice, must be byte-identical. CPU-only. No git commit/push; no data committed.
