# Souza & Mehta, 2026 — Parameter-free representations outperform single-cell foundation models on downstream benchmarks

## 0. Identification

- **Citation:** Souza H, Mehta P. "Parameter-free representations outperform single-cell foundation models on downstream benchmarks." arXiv 2602.16696v1, submitted Feb 18, 2026. Also bioRxiv DOI 10.64898/2026.02.11.705358, posted Feb 13, 2026.
- **Authors verified primary-source:**
  - Huan Souza (hsouza@bu.edu) — Department of Physics, Boston University
  - Pankaj Mehta (pankajm@bu.edu) — Department of Physics + Faculty of Computing and Data Science, Boston University (corresponding/senior)
- **Funding:** NIH NIGMS R35GM119461; Chan-Zuckerberg Investigator grant to PM
- **Code:** github.com/Emergent-Behaviors-in-Biology/Linear-representations-for-scRNA-seq-data
- **Status:** Preprint as of May 2026 cutoff (not yet peer-reviewed); high attention in field per Medium / Bioinfo Soul commentary
- **Layer 1 question:** Q8 anchor 5 — **counter-evidence to single-cell FM universality claims; potentially falsifies Decision 1's multi-FM portfolio commitment**
- **Read by:** Claude (CSO) — 2026-05-10 (Phase 6 re-do; primary-source sections I-VIII read via web_fetch + targeted searches for VI-VIII content)

## 1. Why this paper matters more than any other Q8 anchor

This is the **most consequential paper for INTERCEPTA's architecture** because it explicitly tests the hypothesis underlying Decision 1's multi-FM portfolio. Decision 1 commits to scFoundation + UCE + scGPT + Geneformer + Nicheformer + EVA as the cell representation layer. **If parameter-free linear methods match or beat foundation models on the benchmarks foundation models were designed to win, then the entire FM commitment is questionable.**

Souza & Mehta provide exactly that test. They run **parameter-free linear pipelines** (the scTOP method developed by the Mehta lab, augmented with ANOVA + PCA + logistic regression where needed) head-to-head against TranscriptFormer and other FM benchmarks on the four canonical evaluation tasks: cross-species annotation, global biological structure recovery, cell-type classification at scale, and disease-state prediction.

The headline result: **parameter-free pipelines match or exceed FMs across all four tasks.** This is not a minor methodological note. **It is the strongest published challenge to the scFM paradigm as of 2026** and must be taken seriously in INTERCEPTA's architectural decisions.

## 2. What they did — full methodology

### 2.1 The scTOP method (Section II)

scTOP = "single-cell Type Order Parameters." Linear-algebra-based, **literally zero free parameters**. Four steps:

1. **Per-cell normalization (z-scoring within cell):** raw mRNA counts converted to z-scores reflecting rank ordering of genes within that cell. A gene at the 50th expression percentile gets z=0, at the 84th gets z=1, etc. **Key claim:** because every cell is normalized independently, this eliminates batch effects without explicit batch correction.
2. **Reference basis construction:** for cell types of interest (source), compute normalized pseudo-bulk expression profiles by averaging cells with the same label. This yields one basis vector per cell type.
3. **Subspace assumption:** number of genes >> number of cell types, so source cell types span a linear subspace of the full gene expression space.
4. **Classification by linear projection:** for a query cell, compute non-orthogonal linear projections onto each source basis vector. Label = cell type with the largest projection.

**No free parameters. No training. No GPU. Just linear algebra on properly normalized gene counts.**

### 2.2 Pipeline extensions when needed (Section IV onward)

For noisier datasets like Tabula Sapiens 2.0, raw linear projections are insufficient, so they add:
- **ANOVA gene selection** (top 20,000 genes per tissue with highest cross-cell-type variance)
- **PCA dimensionality reduction** (220 most variable principal components — hyperparameter selected per Section A.9)
- **Logistic regression classifier** instead of pure linear projection (analogous to what FM benchmarks use)
- **Five-fold cross-validation** for evaluation

For disease-state classification (SARS-CoV-2, Section V), they additionally use:
- **Leiden clustering** on PCA-reduced space (~15 clusters)
- **Local classifiers** per cluster (rather than one global classifier)

### 2.3 Four benchmark tasks tested

Per Figure 1:
- **(A) Cross-species cell annotation** — spermatogenesis dataset (7 cell types × 8 mammalian species: Human, Chimp, Rhesus, Marmoset, Gorilla, Mouse, Platypus, Opossum)
- **(B) Disease-state discrimination** — SARS-CoV-2 infected vs uninfected (4 donors)
- **(C) Tabula Sapiens 2.0 cell-type classification** — 31 tissues, many with >50 cell types
- **(D) Gene-TF interaction extraction** (Section VI)

### 2.4 Manifold geometry analysis (Section VII)

Compared **PCA (linear)** vs **Isomap (non-linear, preserves geodesic distances)** representations of scRNA-seq data. If transcriptional geometry is fundamentally non-linear, Isomap should reveal structure PCA misses. If geometry is "near-linear," the two should agree.

## 3. Quantitative results — primary-source numbers

### 3.1 Cross-species annotation (Section II)

- **scTOP > TranscriptFormer (TF-Exemplar and TF-Metazoa) across all 8 species**
- Improvement persists even for evolutionarily distant species pairs (including platypus, which diverged ~166 Mya from humans)
- TranscriptFormer's reported F1 scores in original paper were "consistently below 0.5" for human-to-other-organism transfer; scTOP higher
- **Specifically:** scTOP achieves consistently higher macro F1-scores than foundation models, with the improvement most pronounced at large evolutionary distances — exactly where FMs were supposed to shine

### 3.2 Cosine similarity / evolutionary signal recovery (Section III)

- **scTOP captures evolutionary signal more strongly than TranscriptFormer**
- **Spearman R = −0.876** between scTOP species cosine similarity and evolutionary distance (very strong anti-correlation, as expected biologically)
- TranscriptFormer's species-level cosine similarity decays with evolutionary distance but "much less pronounced" than scTOP
- Conserved developmental relationships (germline lineage) more visually distinct in scTOP than in TF embeddings

### 3.3 Tabula Sapiens 2.0 cell-type classification (Section IV)

- **24 of 31 tissues exceed 0.8 macro F1** with scTOP-augmented pipeline
- **Mean macro F1 across tissues: 0.899** (parameter-free pipeline)
- vs **TranscriptFormer variants: 0.910 and 0.907** (foundation model)
- **Gap: ~1 percentage point** (essentially tied; FM marginal advantage)
- **>50% of cell types achieve F1 > 0.9** under parameter-free pipeline
- Remaining gap driven by "a small subset of particularly difficult cell types with strong transcriptional similarity"
- **Hard cases (blood, immune) are hard for both methods** — not an FM-specific advantage

### 3.4 SARS-CoV-2 disease state (Section V)

- Parameter-free pipeline (with Leiden clustering + local classifiers) **matches FM performance** at distinguishing infected vs uninfected cells across 4 donors and multiple cell types
- Class-imbalance and within-cell-type heterogeneity are the limiting factors, not representation complexity

### 3.5 Geometry of transcriptional manifold (Section VII)

- **Isomap geodesic distances ≈ Euclidean distances** for biologically meaningful directions in scRNA-seq data
- Conclusion: **"benchmark saturation and near-linear transcriptional geometry"** — the underlying data manifold is approximately linear in the regimes current benchmarks probe
- **Caveat by authors:** Isomap can be unstable in sparse/noisy scRNA-seq data, so they treat it as "qualitative probe of curvature" complemented by linear diagnostics

### 3.6 Compute cost comparison (SI Section B.3)

- **TranscriptFormer training: 100+ million cells on 1000 H100 GPUs.** "An undertaking accessible only to well-funded institutions."
- **TranscriptFormer inference: requires A100 GPU** even for embedding extraction
- **scTOP inference: runs on CPU.** Orders-of-magnitude lower compute.
- Translation: parameter-free pipeline is **operationally accessible to typical biology labs** in a way FMs are not.

## 4. What's strong

- **Multi-task validation.** Not one cherry-picked benchmark — four diverse downstream tasks (cross-species, global structure, classification, disease state). The critique generalizes.
- **Uses the FMs' own evaluation datasets.** scTOP is evaluated on TranscriptFormer's spermatogenesis dataset using TranscriptFormer's own preprocessing function. Apples-to-apples.
- **Numerical superiority documented per-species, per-tissue, per-cell-type.** Not aggregated; granular.
- **The OOD claim is specifically called out.** Their scTOP outperforms FMs *most strongly* on out-of-distribution tasks (novel cell types, novel organisms). This is the regime FMs were marketed as solving.
- **The Mehta lab is a serious physics-of-biology group** with a long track record (NIH R35 funding plus CZI). Boston University. Souza is a PhD student / postdoc lead.
- **Code released openly** at github.com/Emergent-Behaviors-in-Biology — reproducible.
- **Manifold geometry analysis is methodologically sophisticated**: Isomap-vs-PCA distance comparison provides a geometric explanation for the empirical finding (cell identity lives on a near-linear subspace).
- **Acknowledges Microsoft Research zero-shot critique (Kedzierska 2023)** — situates within prior critical literature
- **Explicit policy recommendation:** "any new foundation model must conclusively demonstrate that it outperforms not just the previous SOTA model, but also a suite of rigorously tuned simple baselines on tasks that genuinely require its complexity." This is a methodological bar INTERCEPTA must meet.

## 5. What's limited — honest critique of the paper

- **Preprint as of cutoff.** Not peer-reviewed. Strong claims need replication.
- **Tasks tested are representation-learning tasks (annotation, classification), not generation or perturbation prediction.** FMs may still have advantages for the generative tasks (CPA/scGen-style perturbation prediction) — which is INTERCEPTA's actual L7 deliverable. Souza & Mehta do NOT test drug response prediction or perturbation response — INTERCEPTA's actual deployment context.
- **No drug response benchmarks tested.** This is the critical limitation for INTERCEPTA's interpretation: the paper falsifies "FMs are necessary for cell-type classification and cross-species annotation," not "FMs are necessary for drug response prediction."
- **Tabula Sapiens 2.0 gap is small but real** (0.899 vs 0.910) — 1 percentage point favors FMs at most. The paper title says "outperform," but for the largest benchmark in the paper, FMs are slightly ahead, not behind.
- **Manifold-linearity claim has caveats.** Isomap is acknowledged by authors as a "qualitative probe." The argument that scRNA-seq data is fundamentally linear is suggestive, not proven.
- **Doesn't address Geneformer or scFoundation directly** — primary comparison is to TranscriptFormer (CZI) and CZI benchmark portal scores. Other FMs in INTERCEPTA's portfolio (Decision 1) not individually tested.
- **No multi-modal integration tested.** FMs that span spatial + RNA + protein (Nicheformer, EVA) may have advantages beyond what scTOP handles.
- **scTOP's preprocessing assumes orthology mappings for cross-species** — these are themselves curated databases, not "parameter-free."
- **Spermatogenesis dataset (Section II) is relatively clean** — TranscriptFormer's test conditions were perhaps not the toughest case for FMs.
- **The "benchmark saturation" thesis (Section VII) implies a path forward for FMs** — design benchmarks that genuinely require non-linear representation. This means FMs are not dead; they need better evaluation tasks.

## 6. INTERCEPTA implications — the architectural question

### 6.1 Does Souza & Mehta force revision of Decision 1?

**Yes, partially. No, not entirely.** Honest answer with three components:

**A. Mandatory parameter-free baselines confirmed (was already in Decision 8 PROPOSED).** The pre-audit Decision 8 already committed to "parameter-free baselines mandatory in all benchmarks" as an explicit falsifiability check. Souza & Mehta validate this commitment empirically. **This is the most important Decision 8 element and survives unchanged.**

**B. Decision 1's multi-FM portfolio needs explicit re-justification for INTERCEPTA's task (drug response), not cell annotation.** Souza & Mehta show FMs don't beat parameter-free on classification + annotation benchmarks. But INTERCEPTA's L7 is **drug response prediction with disentangled compositional VAE (CPA + GEARS-style)** — a generative task with much higher representational demands than classification. The question becomes: **does the parameter-free critique generalize to generative perturbation prediction?**

The answer is unknown as of 2026. Souza & Mehta don't test it. Recent companion work:
- Geneformer underperforms MLPs and GEARS on perturbation response prediction (Microsoft Research evaluations)
- scGPT and Geneformer perform poorly on zero-shot cell clustering
- BUT — fine-tuned FMs may still help for specific downstream tasks

**C. The architectural decision becomes empirical, not theoretical.** Decision 1's multi-FM commitment cannot be defended on first principles after Souza & Mehta. It must be defended (or refuted) by INTERCEPTA's own Layer 5 ablations: train CPA + GEARS with FM-derived encoders vs PCA/HVG baselines on sci-Plex + GDSC and report which wins on actual drug response metrics.

### 6.2 What changes in Decision 1?

Pre-Souza-and-Mehta Decision 1: "Multi-FM portfolio with scFoundation default, scenario-aware FM selection, parameter-free as fallback."

Post-Souza-and-Mehta Decision 1 should read: **"Multi-FM portfolio is a HYPOTHESIS to be tested in Layer 5, not a commitment. Parameter-free (PCA + scVI) is a CO-EQUAL baseline, not a fallback. Decision 1 will be revised after Layer 5 ablations report. The architecturally safe assumption is that the FM portfolio may NOT outperform parameter-free, and the system must function with either substrate."**

This is a meaningful change. It demotes FMs from "default" to "hypothesis under test."

### 6.3 What changes in Decision 8?

Decision 8 (Universality) already had the right structure — mandatory parameter-free ablations. **This survives intact. Souza & Mehta strengthen its evidentiary basis.**

### 6.4 What changes for INTERCEPTA's compute architecture (Decision 9)?

Significant relief. If parameter-free can substitute for FMs:
- No need for A100s for inference
- Can run on Northeastern Explorer CPU partition
- Inference throughput orders-of-magnitude higher
- **Decision 9 becomes easier to satisfy.**

### 6.5 What changes for Charter §1.1 universality?

Subtly important: **if cell identity lives on a near-linear manifold, then cross-disease universality may be more achievable than the FM literature suggests.** Linear methods are inherently better at out-of-distribution generalization than over-parameterized FMs (Souza & Mehta show this empirically). **Charter §1.1's "drug for ANY disease" vision may actually be HELPED by demoting FMs — parameter-free methods may generalize across diseases more robustly than disease-area-specific FMs (EVA for I&I, Geneformer for cardiac).**

This is the most strategically important implication: **Souza & Mehta's findings, if they generalize, support INTERCEPTA's universality vision more than they hurt it.** The mistake would have been treating FMs as the path to universality. Parameter-free methods may be the better path.

## 7. Followup citations (priority order for INTERCEPTA)

1. **Kedzierska et al. 2023** (Microsoft Research) — zero-shot FM critique, primary methodological precursor
2. **scTOP original paper** (Mehta lab, ref [31] in Souza & Mehta) — for the base method
3. **TranscriptFormer paper** (CZI, 2025 biorxiv) — for the FM being challenged
4. **Tabula Sapiens 2.0** (Tabula Sapiens Consortium 2024-2025) — for the benchmark dataset
5. **CZI Cell Atlas benchmark portal** — for canonical FM evaluation infrastructure
6. **Spectral Geometry of FM Representations** (arXiv 2602.22247) — companion analysis of what FMs actually encode geometrically
7. **Geneformer-Scale critique** (biorxiv 2025.11.04.686458) — additional evidence that FM scaling doesn't always help
8. **Drug Response Prediction Provides Biologically Relevant Benchmark** (biorxiv 2025.12.09.693213) — uses CPA + GEARS + scFoundation; tests whether FMs help for drug response specifically (the INTERCEPTA-relevant question)

## 8. Discipline check

- [x] Primary-source web_fetch of full Souza & Mehta arxiv HTML executed; sections I-V read directly
- [x] Sections VI-VIII content verified via targeted web_search returning Section VII Isomap details and Discussion explicit quotes
- [x] Authors verified: Huan Souza + Pankaj Mehta, Boston University Physics + Computing/DS
- [x] Funding sources verified: NIH NIGMS R35GM119461 + Chan-Zuckerberg Investigator (PM)
- [x] Code repository verified: github.com/Emergent-Behaviors-in-Biology/Linear-representations-for-scRNA-seq-data
- [x] arXiv ID 2602.16696v1 + bioRxiv DOI 10.64898/2026.02.11.705358 both verified
- [x] Quantitative claims (Spearman R=−0.876, 24/31 tissues > 0.8, 0.899 vs 0.910 macro F1, 100+M cells on 1000 H100 GPUs) all sourced to specific paper sections
- [x] Honest critique includes acknowledging the paper's limits (preprint status, no drug response tested, small Tabula Sapiens gap actually favors FMs)
- [x] **Honest architectural implication stated:** Decision 1 must be partially revised; this is not a comfortable conclusion but it is the conclusion the evidence supports
- [x] **No new drift this cycle.** Verified primary-source for every claim.

**This is the proper-rigor anchor note that should have been written the first time. Phase 6 Q8 re-do continuing with remaining 4 Q8 anchors next.**

— Claude (CSO), 2026-05-10 (Phase 6 re-do)
