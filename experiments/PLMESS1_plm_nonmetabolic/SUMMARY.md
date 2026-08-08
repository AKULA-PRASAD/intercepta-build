# PLMESS1 — Summary

**Question (4th attempt on the FBA-blind non-metabolic essential half):** does a *learned*
protein-language-model embedding (ESM-2) predict non-metabolic essentiality AND add a signal
**beyond conservation breadth** — where three prior attempts (MET4 PPI, NONMET1 synteny,
REGNET1 regulatory) failed?

## Result: FAIL = rigorous first-class NEGATIVE (the FOURTH principled closure)

Reproduced **x2 byte-identical**, payload SHA-256 `6328bae097afd332a85217c5ed6cb3e253509b40d0687939319cac2e8f750629`.

Pool (reused EXACTLY from NONMET1, apples-to-apples): E. coli non-metabolic subproteome,
**n = 2547**, **179 experimental essentials** (PEC class-1, prevalence 7.0%) — identical to NONMET1.

| Model | AUROC |
|---|---|
| M1 — own conservation breadth only (unbeaten baseline) | **0.9078** (reproduces NONMET1's 0.908) |
| ESM-2 embedding standalone (PCA-50 + L2 logistic) | 0.8784 |
| M2 — conservation + embedding | 0.9161 |
| **ΔAUROC embedding beyond conservation** | **+0.0082** (gate +0.03 → FAIL) |
| M3 — conservation + study proxy | 0.9289 |
| M4 — conservation + study + embedding | 0.9284 |
| **ΔAUROC embedding beyond conservation+study** | **−0.0006** (gate +0.02 → FAIL) |

**Gate (pre-registered): FAIL on both arms.** ΔAUROC-beyond-conservation +0.008 (< +0.03) AND does
not survive the study-bias control (−0.0006).

### The three findings
1. **The PLM embedding carries REAL essentiality signal, but WEAKER than conservation** — standalone
   AUROC 0.878 < conservation 0.908, and it enriches strongly (median-split OR **13.4**, Fisher p≈0).
   ESM-2 has learned functional/structural properties that track essentiality.
2. **It adds almost nothing BEYOND conservation** (+0.008). The signal it carries is largely a
   *re-encoding of conservation* — the same collinearity pattern that sank NONMET1's synteny (which
   also enriched hugely but was collinear with own-conservation). A learned representation does not
   break the ceiling.
3. **Not a dimensionality artifact.** Pre-registered sensitivity sweep is uniformly at/below the gate:
   PCA-k10 +0.005, PCA-k100 −0.003, raw-640 strong-L2 (C=0.1) −0.004. Leakage was structurally
   prevented (PCA + StandardScaler fit on train folds only); because ΔAUROC is *below* the gate, the
   positive-result leakage triple-check is moot — there is no positive to defend.

### Study-bias note
Consistent with the PLM being sequence-derived, its correlation with the PEC PMID study proxy is low
(Pearson 0.24) — it is *not* a study-bias artifact like MET4's PPI. But being clean does not help: it
carries no *independent* signal beyond conservation.

## The bound (now spanning learned representations)
Four INDEPENDENT principled attempts now close the non-metabolic-mechanism door:
- **MET4** — PPI centrality → study-bias artifact.
- **NONMET1** — synteny/genomic context → conservation-collinear (ΔAUROC +0.016).
- **REGNET1** — regulatory-network topology → clean null (ΔAUROC −0.006).
- **PLMESS1** — learned ESM-2 PLM embedding → conservation-collinear / no lift (ΔAUROC +0.008).

**No homology-independent mechanistic signal — network, conservation-context, regulatory, OR a
learned foundation-model representation — has beaten conservation breadth (AUROC 0.908) on the
FBA-blind non-metabolic essential half.** Conservation breadth remains the unbeaten workhorse; FBA
remains the only validated confound-honest mechanistic signal (metabolic-scoped).

## Scope / caveats
E. coli only; non-metabolic subproteome; enrichment/prediction-only; in-silico; **small CPU ESM-2
(150M)** — a genuine capacity caveat: a larger PLM (650M/3B/15B) or a structure-aware model could in
principle carry more; this result bounds the 150M-scale learned representation. PEC truth. No
tuning-to-pass; gate + dimensionality handling locked before scoring.

## Reproduce
```
INTERCEPTA_DATA=/Users/kalki/intercepta_data \
/Users/kalki/miniforge3/envs/intercepta/bin/python run.py
```
Embeddings cached in `$INTERCEPTA_DATA/plmess1/` (2547 x emb_<locustag>.npy). Downstream scoring is
deterministic; payload SHA-256 reproduced x2 byte-identical.
