# PLMSTRUCT1 — Pre-Registration (locked BEFORE any scoring)

*The FIFTH and (by construction) LAST CPU-feasible attempt on the #1 core gap — a homology-independent
MECHANISTIC signal for the FBA-blind **non-metabolic** essential proteome. Locked 2026-08-09.*

## The gap and the four prior closures
FBA validates the metabolic essential half. The non-metabolic half has **no** validated
homology-independent mechanistic signal; the unbeaten baseline is **own sequence-conservation
breadth (AUROC ≈ 0.908)**. Four principled attempts closed, each on a distinct signal class:
- **MET4** — PPI-network centrality → study-bias artifact (lift collapsed under an effort control).
- **NONMET1** — conserved genomic context / synteny → collinear with own-conservation (ΔAUROC +0.016 < +0.03).
- **REGNET1** — curated regulatory-network topology → clean null (ΔAUROC −0.006).
- **PLMESS1** — a **sequence** protein-LM embedding (ESM-2 **t30 / 150M**) → ΔAUROC +0.008 < +0.03; study-bias-ctrl −0.0006.
- **MULTISIG1** — the ENSEMBLE of all four → still < +0.03 (the signal-union is collinear with conservation).

## Why this attempt is genuinely DIFFERENT (not a forbidden re-attack of a closed door)
PLMESS1 explicitly logged a **capacity caveat**: "a larger or **structure-aware** PLM could carry more."
MULTISIG1 showed the *sequence/network* signal-union is collinear with conservation. Neither tested a
**STRUCTURE-aware** representation — a genuinely orthogonal modality: it encodes the residues' **3D fold
microenvironment** (via the foldseek 3Di structural alphabet), not sequence-conservation counting or
network topology. This is the ONE lever the plan itself names as remaining (§4-O2 terminal, §5-#1). I had
mislabeled it "GPU-gated"; it is **CPU-feasible** (SaProt-650M / ESM-2-650M inference on CPU, minutes-hours
for this pool). Attempting it once, rigorously, either (a) **breaks** the conservation ceiling — a genuine
breakthrough on the core gap — or (b) **closes the structure-aware class too**, making the closure
definitive across *all* CPU-feasible signal modalities (sequence, network, regulatory, sequence-PLM,
structure-PLM). Either outcome COMPLETES this step honestly. This is closure-completion, not random re-attack.

## Hypotheses
- **H1 (PRIMARY, structure-aware):** a **SaProt** (structure-aware PLM, real AlphaFold 3Di tokens)
  embedding predicts non-metabolic essentiality **AND adds signal BEYOND conservation breadth**.
- **H2 (CONTROL, capacity):** an **ESM-2 650M** (sequence, 4× PLMESS1's 150M) embedding does the same —
  isolates whether merely *scaling the sequence model* (not structure) is what was missing.

## Models (LOCKED)
- **PRIMARY:** `westlake-repl/SaProt_650M_AF2` — mean-pooled last-layer hidden state over real
  residues; deterministic eval; structure tokens = **foldseek 3Di** computed from **AlphaFold DB**
  structures for the E. coli proteome (UP000000625).
- **CONTROL:** `facebook/esm2_t33_650M_UR50D` — mean-pooled, same pipeline as PLMESS1 (its 150M twin).
- Both CPU-only, single-thread-deterministic; embeddings **cached** to
  `$INTERCEPTA_DATA/plmstruct1/{saprot,esm650}_<locustag>.npy` → downstream scoring byte-reproducible.
- Truncation 1022 residues (as PLMESS1). Proteins with no AFDB structure (SaProt arm only) are reported
  **DROPPED, not fabricated**; the ESM-650M arm still scores the full pool.

## Pool, truth, baseline (REUSED VERBATIM from PLMESS1/NONMET1 — apples-to-apples, LOCKED)
- Pool = E. coli **non-metabolic subproteome** (UniProt NOT in the MET2 GEM); import `build_pool()`
  logic from PLMESS1 unchanged (n ≈ 2547, ≈ 179 essential).
- Truth = **PEC** experimental essentiality (class-1), keyed by b-number.
- Baseline `own` = NONMET1 conservation-breadth (must reproduce AUROC ≈ 0.908 as M1).
- Study proxy = `log1p(PEC PMID count)` (identical study-bias control).

## Scoring pipeline (LOCKED — identical anti-leakage/anti-overfit protocol to PLMESS1)
- Per arm: **PCA → k = 50** (fit on TRAIN folds only, inside CV), **L2-logistic (C = 1.0, lbfgs)**.
- CV = `StratifiedKFold(n_splits=5, shuffle=False)`; pooled out-of-fold AUROC.
- `M1` = conservation only; `M2` = conservation + embed-PCA; **`Δ = M2 − M1`** (decisive).
- Study-bias: `M3` = own+study, `M4` = own+study+embed; `Δ_study = M4 − M3`.
- SENSITIVITY (reported, NOT gated): k ∈ {10, 100}; raw-dim L2 (C = 0.1).

## Feasibility gate (LOCKED)
- ESM-2 650M: ~2–4 s/protein × ~2547 ≈ **~1.5–3 h** wall — FEASIBLE (background).
- SaProt arm adds: AFDB E. coli proteome bulk fetch (one archive) + foldseek `createdb`/3Di (~minutes) +
  SaProt inference (~like 650M). If the AFDB fetch or foldseek/SaProt install FAILS, or timing blows a
  **6 h hard wall-clock cap**, the SaProt arm is declared **honestly infeasible-here + exact spec delivered**;
  the ESM-650M capacity arm still runs and is reported. (Do NOT fake either arm.)

## PRE-REGISTERED GATE (decisive, per arm)
- **PASS (ceiling BROKEN → breakthrough on the core gap):** `Δ ≥ +0.03` **AND** `Δ_study ≥ +0.03`
  (survives study-bias) **AND** reproduces ×2 byte-identical **AND** a triple leakage check passes.
- **FAIL (structure-aware class CLOSED → the definitive, complete closure):** `Δ < +0.03` on both arms.
- Honest interpretation is fixed in advance either way. A leakage-suspicious PASS is NOT claimed until the
  triple check (PCA/scaler train-only; no b-number/target overlap across folds; label-shuffle null Δ≈0) passes.

## What a FAIL buys (why running it still COMPLETES the step)
A fifth failure across a genuinely-orthogonal modality (structure) makes the non-metabolic-mechanism
closure **complete across every CPU-feasible signal class** — sequence-conservation, synteny, regulation,
sequence-PLM, structure-PLM — leaving only experimental mechanism data (a true acquisition). That is the
honest, evidence-backed *completion* of the #1 core gap, not an open wound. No further CPU attempt would
be warranted; the door is closed with a full evidence set.
