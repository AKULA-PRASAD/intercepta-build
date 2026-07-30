# Pre-registration — B37: does a LEARNED joint molecular representation beat raw structure on held-out outcomes? (FINALIZED 2026-07-30, PRE-RESULT)

## Why (the one integration path B32–B36 left open)
B32/B36 showed that fusing FROZEN module OUTPUTS does not beat raw structure — mechanistically expected, because the
modules are themselves Morgan+physchem GBTs, so their outputs are deterministic functions of the structure features
(no new information). The only way integration could add value is a representation LEARNED across tasks that carries
transfer signal not recoverable from a single-task model on raw fingerprints. B37 tests exactly that: learn a joint
molecular representation via MULTI-TASK training, and ask whether it transfers to held-out outcomes beyond raw
structure.

## Method (learned joint representation; deterministic, torch-free)
- **Representation learning:** a multi-task neural net (sklearn `MLPClassifier`, shared hidden layers, random_state=42)
  trained on **tox21** (12 toxicity assays, ~7,265 molecules; dense multi-label; input = Morgan/ECFP4 2048-bit + 17
  physchem = 2065-d). The last hidden layer (manual forward pass through the fitted weights) = the **learned joint
  embedding** (dim = last hidden size). Missing tox21 assay labels filled 0 (standard for tox21; noted as a caveat).
- The embedding is a fixed function of a molecule after pretraining — evaluated on molecules the pretrainer may or
  may not have seen; transfer outcomes are leakage-excluded against the tox21 pretraining set.

## Held-out transfer outcomes (distinct from tox21 pretraining AND from module training endpoints)
`clintox` (~55 pos), `skin_reaction` (~157 pos), `carcinogens_lagunin` (~52 pos). Each leakage-controlled (exclude
molecules present in the tox21 pretraining set).

## Comparison (per outcome; the crux)
Same downstream model (HistGradientBoostingClassifier, seed=42), scaffold split (5 seeds), on three feature sets:
- **A = raw structure** S (Morgan2048 + physchem, 2065-d) — the baseline that won B36.
- **B = learned joint embedding** (tox21-MLP hidden activations).
- **C = S + embedding** (structure augmented with the learned representation).
Report per-outcome mean AUROC for A/B/C + paired ΔAUROC(C − A) and (B − A).

## Hypotheses (assumed FALSE)
- **H1 (representation transfers / adds):** across the held-out outcomes, C (or B) beats A — mean paired ΔAUROC>0
  with the majority of outcomes positive and a combined CI excluding 0. (I.e., the learned joint representation
  carries transfer signal beyond raw structure.)
- **H0:** C ≈ A and B ≤ A → a multi-task-learned representation on these fingerprints does NOT beat raw structure →
  the integration/representation bottleneck is INFORMATION, not representation (cements B36; a shallow learned
  representation over the same features adds nothing transferable here).

## Decision rule & interpretation (fixed)
- **H1 PASS** → learned joint representation is a real (if modest) integration win → report effect size honestly;
  note that a larger/deep molecular foundation model (torch, more data) is the natural scale-up.
- **H1 FAIL** → decisive: even a learned joint representation (the last open integration path) does not beat raw
  structure at this scale → INTERCEPTA's value is its standalone validated modules; a genuine integration win, if it
  exists, requires a much larger pretraining corpus / deep foundation model (beyond torch-free shallow MLP) — stated
  as the honest boundary, not attempted-and-overclaimed.

## Honesty / scope
This is a SHALLOW learned representation (sklearn MLP) over Morgan+physchem features pretrained on one multi-task tox
corpus — NOT a modern deep molecular foundation model. A negative here bounds the shallow/torch-free approach, not
the entire idea of representation learning. Small held-out positive classes; scaffold split; no clinical claim.

## Reproducibility
Deterministic (MLP + HGB random_state=42; fixed CV seeds; tox21 merge deterministic). Reproduce ×2 byte-identical
(payload sha256). Output: `experiments/B37_learned_joint_representation/results/B37_metrics.json`.
