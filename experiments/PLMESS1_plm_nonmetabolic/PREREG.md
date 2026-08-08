# PLMESS1 — Pre-Registration (locked BEFORE scoring)

## The gap (three prior closures)
The FBA-blind **non-metabolic** essential half of the E. coli proteome has no validated
homology-independent MECHANISTIC signal. Three principled attempts have closed the door:
- **MET4** — PPI-network centrality → a study-bias artifact (lift collapsed under a study-effort control).
- **NONMET1** — conserved genomic context / synteny → collinear with own-conservation (ΔAUROC +0.016, below +0.03).
- **REGNET1** — curated regulatory-network topology → a clean null (ΔAUROC −0.006).

The unbeaten baseline on this subproteome is **own sequence-conservation breadth (AUROC ≈ 0.908)**;
FBA remains the only validated confound-honest mechanistic signal (metabolic-scoped).

## Why this attempt is genuinely DIFFERENT
Prior attempts used **network / conservation** signals. PLMESS1 uses a **learned protein
language-model (PLM) representation** — a mean-pooled ESM-2 embedding — which encodes learned
functional/structural properties beyond raw sequence-conservation counting. This is a distinct
signal class (a foundation-model capability), warranting the 4th attempt despite 3 closures.

## Hypothesis (H1)
An ESM-2 protein-language-model embedding predicts non-metabolic essentiality **AND adds a
signal BEYOND conservation breadth** on the E. coli non-metabolic subproteome.

## Model (LOCKED)
- **ESM-2 `facebook/esm2_t30_150M_UR50D`** (30-layer, 150M params, hidden dim 640). CPU-only.
  (Small CPU-feasible model — a stated capacity caveat; NOT the 650M+.)
- Embedding = **mean-pooled last-layer hidden state** over real residue positions (attention-masked),
  deterministic eval mode, `torch.manual_seed(0)`, single-thread-safe (pooler head UNUSED → its
  random init does not enter the embedding).
- **Truncation at 1022 residues** (`max_length=1024` incl. BOS/EOS). ~1.2% of proteins exceed this.
- Embeddings **cached** to `$INTERCEPTA_DATA/plmess1/emb_<locustag>.npy` → downstream scoring is
  deterministic and byte-reproducible.

## Feasibility gate (LOCKED, see FEASIBILITY.md)
- HARD CPU-time cap: total embedding of the non-metabolic pool must finish in **≤ 60 min wall-clock**.
- Measured: ~0.5–0.7 s/protein × ~2547 proteins ≈ **~25 min** → FEASIBLE.
- If install had failed or timing blew the cap → declare CPU-INFEASIBLE + deliver the exact spec. (Not triggered.)

## Pool (REUSED from NONMET1 — apples-to-apples, LOCKED)
- E. coli **non-metabolic subproteome** = genes whose UniProt is NOT in the MET2 GEM.
- Own-conservation breadth = NONMET1 `context_scores("ecoli")` `own` (fraction of the 11 panel
  organisms with a reciprocal-best-hit ortholog). Imported directly from NONMET1's `run.py`.
- Truth = **PEC** experimental essentiality (class-1), keyed by b-number.
- Study proxy = `log1p(PEC PMID count)`.
- Expected pool: n ≈ 2547 genes, ≈ 179 essential (matches NONMET1).

## Dimensionality handling (LOCKED, anti-overfit / anti-leakage)
640-dim embedding with only ~179 positives → high overfitting risk. Locked BEFORE scoring:
- **PRIMARY:** PCA → **k = 50** components, then **L2-regularized logistic (C = 1.0, lbfgs)**.
- **PCA + StandardScaler fit on TRAIN folds ONLY** inside CV (NO test leakage into scaler/PCA fit).
- CV = `StratifiedKFold(n_splits=5, shuffle=False)` (identical to NONMET1). Pooled out-of-fold AUROC.
- **SENSITIVITY (reported, NOT part of the gate):** k ∈ {10, 100} and raw-640-dim L2 with strong
  reg (C = 0.1) — to show the result is not an artifact of the specific k.

## Metrics (LOCKED)
- `auroc_M1_own_only` — conservation breadth alone (must ≈ reproduce NONMET1's 0.908).
- `auroc_embed_standalone` — PCA-50 embedding features alone (CV OOF).
- `auroc_M2_own_plus_embed` — conservation + embedding-PCA.
- **`delta_auroc_embed_beyond_own` = M2 − M1** (the decisive number).
- Enrichment: median-split of the standalone-embedding CV OOF probability, Fisher exact (one-sided greater).
- **Study-bias control:** `M3 = own + study`, `M4 = own + study + embed`;
  `delta_auroc_embed_beyond_own_study = M4 − M3`; and Pearson(study, embed-OOF-prob).

## GATE (LOCKED — decision made before any number is seen)
**PASS ⇔** `delta_auroc_embed_beyond_own ≥ +0.03` **AND** survives the study-bias control
(`delta_auroc_embed_beyond_own_study ≥ +0.02`).
- **PASS** = first non-metabolic homology-independent mechanistic signal, via a learned PLM
  (a foundation-model capability). If PASS, **triple-check for leakage** before claiming a ceiling break
  (proper train-only PCA/scaler already enforced; also report the sensitivity sweep).
- **FAIL** = a rigorous first-class NEGATIVE — the **4th principled closure** of the
  non-metabolic-mechanism door, now spanning **learned representations** as well as
  network/conservation signals. A very strong bound.

## Reproducibility (LOCKED)
- SHA-256 over sorted-key JSON of the payload **EXCLUDING** `verdict` + `provenance`.
- Embeddings cached (deterministic) → downstream scoring reproduced **x2 byte-identical**.

## Scope / caveats (LOCKED)
E. coli only; non-metabolic subproteome; enrichment/prediction-only; in-silico; small CPU ESM-2
(150M) model (capacity caveat — a larger model could carry more signal); PEC truth. No tuning-to-pass.
