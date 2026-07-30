# Pre-registration — B38: does a DEEP molecular foundation model beat raw structure on held-out outcomes? (FINALIZED 2026-07-30, PRE-RESULT)

## Why (the deepest integration path)
B37 showed a SHALLOW learned representation (sklearn MLP on Morgan+physchem) does not robustly beat raw structure —
but it was still a function of the same Morgan bits. A DEEP molecular foundation model learns fingerprints directly
from molecular structure via large-scale pretraining, so it can carry information NOT in Morgan+physchem. B38 tests
the honest deep-FM hypothesis: does a foundation-model embedding beat / augment raw structure on held-out outcomes,
where every shallower integration attempt (B32→B37) failed?

## Foundation model (pretrained, public — the standard FM transfer protocol)
`DeepChem/ChemBERTa-77M-MLM` (a RoBERTa masked-language model pretrained UNSUPERVISED on 77M molecules; HuggingFace).
Per-molecule embedding = mean-pooled last hidden state (384-d), computed in eval mode (deterministic). Because
pretraining is unsupervised (no task labels), there is NO label leakage into the held-out outcomes — the FM has only
seen molecular structures, never the outcome labels. (Model downloaded once, cached; embeddings deterministic →
reproduce ×2 on the downstream.)

## Held-out outcomes (power via a multi-outcome panel)
7 binary outcomes: clintox, skin_reaction, carcinogens_lagunin, and tox21 {NR-AR, NR-ER, SR-MMP, SR-p53} (seeded cap
4000 molecules each; 50–340 positives). No module-training leakage concern (no INTERCEPTA label-trained modules used).

## Comparison (per outcome; same downstream model)
HistGradientBoostingClassifier (seed=42), Bemis–Murcko scaffold split (5 seeds), on three feature sets:
- **A = raw structure** (Morgan2048 + physchem, 2065-d) — the baseline that has won every integration test so far.
- **B = FM embedding** (ChemBERTa 384-d).
- **C = A + B** (structure augmented with the FM representation).
Report per-outcome mean AUROC(A/B/C), paired ΔAUROC(B−A) and (C−A), and a molecule-level pooled-OOF bootstrap CI.

## Meta-analysis (unit = outcome)
Across the 7 outcome-level deltas: mean Δ(C−A) and Δ(B−A); fraction positive; one-sided Wilcoxon signed-rank;
bootstrap 95% CI over outcomes; count of outcomes with an individually-significant gain.

## Hypotheses (assumed FALSE)
- **H1 (deep FM adds/robustly beats structure):** mean Δ(C−A) > 0 AND Wilcoxon-across-outcomes p<0.05 AND ≥⅔ of
  outcomes positive AND combined bootstrap CI excludes 0. (Optionally B alone > A.)
- **H0:** the FM embedding does NOT robustly beat raw structure → even a deep foundation model adds nothing general
  beyond Morgan+physchem on these outcomes (consistent with the literature that ChemBERTa often ≈ or < classical
  fingerprints on ADMET/tox) → integration is bounded even at the deep-FM level.

## Decision rule & interpretation (fixed)
- **H1 PASS** → a deep FM representation is a real integration win → report effect size honestly; this is the first
  representation that beats raw structure, and would motivate a shippable FM-augmented predictor.
- **H1 FAIL** → decisive across the whole integration ladder (B32→B38): neither module fusion nor shallow nor deep
  learned representations robustly beat raw structure on these outcomes → INTERCEPTA's value is its standalone
  validated modules; representation is not the bottleneck, information/data is. Stated as the honest boundary.

## Honesty / scope
Off-the-shelf FM (not trained by us), 384-d embedding, one pooling choice; small held-out positive classes; scaffold
split; no clinical claim. A negative bounds THIS FM + protocol, not every conceivable deep model. Effect size governs.

## Reproducibility
FM download is one-time (model id pinned); embeddings deterministic (eval mode, fixed batching, rounded to 5 dp);
downstream deterministic (seed=42; fixed CV seeds). Reproduce ×2 byte-identical (payload sha256). Output:
`experiments/B38_deep_foundation_model/results/B38_metrics.json`.
