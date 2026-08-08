# REGNET1 — SUMMARY (curated regulatory network vs non-metabolic essentiality)

**FAIL against the pre-registered gate → a rigorous first-class NEGATIVE. Reproduced ×2 byte-identical, payload sha256
`e853875792a260a40bce5839e97fdb88890da400af489fea51d5ac4820d466c1`.** Data (Abasy `511145_v2005_sRDB04`, curated
RegulonDB-derived GRN, sha c1f625e5) fetched to `$INTERCEPTA_DATA`, never committed.

## Result
Curated regulatory graph: 1202 genes, 3148 experimentally-curated TF→gene edges. Non-metabolic E. coli pool: 2547 genes,
179 experimentally essential (base rate 7.0%); 412 mapped into the GRN.

- **(a) Master-regulator hypothesis — FALSIFIED.** Regulators (out-degree > 0) are **not** enriched for essentiality —
  odds ratio **0.52** (p = 0.96), if anything slightly anti-correlated. Biologically sensible: TFs are often
  conditionally important (stress/response regulons) but individually dispensable under standard conditions, whereas the
  essential non-metabolic genes are core machinery (translation, replication, secretion), not master regulators.
- **(b) Beyond conservation — no add.** Adding regulatory features (out/in-degree, betweenness) to conservation breadth
  changes 5-fold-CV AUROC by **ΔAUROC = −0.006** (0.908 → 0.902) — below the +0.03 gate; regulatory position adds nothing.
- **(c) Study-bias control — clean null (not an artifact).** Out-degree correlates only **r = 0.077** with the publication
  proxy, so — *unlike* MET4's PPI — this is genuinely study-bias-free; it simply carries no essentiality signal
  (ΔAUROC-beyond-publication-count = −0.004).

## Why this negative matters (the real contribution)
This is the **third independent, principled attempt** to find a homology-independent *mechanistic* signal for the
FBA-blind non-metabolic essential half, each addressing the prior one's specific failure:
1. **MET4** — PPI-network centrality → died of **study bias**.
2. **NONMET1** — conserved genomic context/synteny → study-bias-free but **collinear with conservation** (no add).
3. **REGNET1** — curated regulatory master-regulator influence → **clean null** (not study-biased, but no signal).

**Honest, now-strong bound:** no homology-independent mechanistic signal for the non-metabolic essential half has survived
three independent principled attempts. **Conservation breadth (AUROC 0.908) remains the unbeaten workhorse** for that half,
and **FBA-essentiality remains the only validated confound-honest mechanistic signal — and it is metabolic-scoped.** This
is a publishable, decisive closure, not a gap left open.

## Scope
E. coli only; non-metabolic subproteome; enrichment-only; in-silico. The GRN is the 2005 curated RegulonDB-derived network
(smaller than current RegulonDB — a coverage limit; curation, the load-bearing property, is preserved). A newer/larger
curated network could be tested, but the clean null + zero study-bias correlation make a reversal unlikely.
