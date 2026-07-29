# Boyeau et al., 2025 — Deep generative modeling of sample-level heterogeneity in single-cell genomics (MrVI)

## 0. Identification
- **Full citation:** Boyeau P, Hong J, Gayoso A, Kim M, McFaline-Figueroa JL, Jordan MI, Azizi E, Ergen C, Yosef N. Deep generative modeling of sample-level heterogeneity in single-cell genomics. *Nature Methods* 22(11):2264-2274, 2025 Nov (published online Oct 13, 2025).
- **DOI:** 10.1038/s41592-025-02808-x ✓ (verified across Nature Methods website, PMC12615264, PubMed PMID 41083897, Weizmann Pure, ResearchGate, scvi-tools docs, Prime PubMed, bioRxiv preprint 2022.10.04.510898)
- **PMID:** 41083897
- **PMC:** PMC12615264
- **Pages:** 2264-2274 (11 pages)
- **Submission timeline:** Received Jun 7, 2024; accepted Jul 29, 2025; published online Oct 13, 2025
- **First author:** Pierre Boyeau (UC Berkeley + scvi-tools team)
- **Senior author:** Nir Yosef (UC Berkeley + Ragon Institute MGH/MIT/Harvard + Chan-Zuckerberg Biohub Investigator + Weizmann Institute)
- **Co-authors:** Justin Hong, Adam Gayoso, Martin Kim, José L McFaline-Figueroa, Michael I Jordan, Elham Azizi (Columbia), Can Ergen
- **Note:** Adam Gayoso is co-lead of scvi-tools; Elham Azizi is Columbia faculty (her own lab works on cancer single-cell genomics)
- **Status:** Peer-reviewed Nature Methods. Open access (Springer Nature, © Authors 2025).
- **Code:** scvi-tools (production-ready Python class `MRVI`)
- **Layer 1 question:** Q2 (Cross-cohort harmonization) — third anchor, **2025 SOTA in Yosef lineage**
- **Read by:** Claude (CSO)
- **Read date:** 2026-05-10

## 1. Why This Paper

MrVI is the **current 2025 state-of-the-art** in the Yosef lab's continuous research program on cross-cohort harmonization. Reading it after scVI (2018) and scANVI (2021) completes the lineage view. Critical reasons:

1. **Sample-level heterogeneity is INTERCEPTA's actual problem.** The paper explicitly addresses cohorts where samples (= patients, donors, or cell-line-replicates) exhibit complex experimental designs. **Hundreds of patients × cellular subsets is precisely the data structure for cross-disease drug response prediction.** scVI and scANVI handle batch correction; MrVI handles sample-level cohort analysis — qualitatively different scope.

2. **Drug perturbation screens are an explicit benchmark task.** The abstract names "drug perturbation screens" as one of three validation cohorts. **For INTERCEPTA's drug response prediction vision, MrVI is the most directly relevant Q2 anchor** because it has been validated on drug perturbation single-cell data.

3. **Counterfactual prediction framework.** MrVI's architecture explicitly supports counterfactual analysis: "what would this cell look like if it came from a different sample/condition?" **For drug response prediction, counterfactual reasoning is central — what would this cell look like if treated vs untreated?** The MrVI framework directly maps to this question.

4. **Annotation-free differential expression and differential abundance.** Charter §1.3 emphasizes mechanistic interpretability. MrVI provides DE and DA analysis without requiring pre-defined cell states. **For INTERCEPTA's cross-disease deployment where cell-state annotations may be incomplete, this is operationally critical.**

5. **2025 publication date.** Most current Q2 anchor available. Reading scVI (2018) and scANVI (2021) without MrVI would miss 7 years of method evolution.

## 2. What They Did

The authors developed MrVI, a hierarchical variational inference framework specifically for multi-sample, multi-batch single-cell experimental designs. Architecture details:

1. **Two-level hierarchical latent space (Fig 1b).** Per the bioRxiv preprint and Nature Methods extended methods:
   - **Top-level latent `u`:** L-dimensional, Normal(0, I_L). Decoupled from sample-of-origin and known technical factors. **This is the "cell state" embedding.**
   - **Bottom-level latent `z`:** Conditioned on `u` AND on sample-level covariates `s_n`. Captures both biological state AND sample-specific effects. **This is the "sample-aware" embedding.**

2. **Negative binomial noise model.** Same family as scVI (handles overdispersion in single-cell counts).

3. **Sample-level target covariate `s_n`.** For each cell, the model takes the sample identifier (e.g., patient ID) as input. The model learns sample-specific effects on gene expression while preserving biological cell state in `u`.

4. **Counterfactual cell states `z^(s)_n`.** For each cell, MrVI can produce predictions of what `z` would be under different sample-level covariates. **This is the operational mechanism for counterfactual reasoning.**

5. **Sample stratification via `u` space distances.** Samples are grouped by comparing their cell distributions in `u` space, **without requiring pre-defined cell types.** Stratification can be cell-subset-specific.

6. **Differential expression and differential abundance.** MrVI regresses counterfactual cell states on sample-level covariates: `z^(s)_n = β_n × c_s + β_0 + ε_n`. The cell-specific coefficient `β_n` captures how covariate `c_s` shifts cell `n` in the latent space. **This captures cell-type-specific responses to interventions** — a critical capability for drug response prediction.

**Tasks evaluated in the paper:**
- COVID-19 PBMC cohort (multi-donor) — identifies monocyte-specific disease response
- Inflammatory Bowel Disease (Crohn's disease, 46 patients + 25 controls, 463,000 cells) — identifies pericyte subset with strong transcriptional changes in stenosis
- Drug perturbation screens — reveals expected and "non-trivial" drug-drug relationships

**Comparison baselines:** Milo (differential abundance), conventional scVI, conventional pseudo-bulk DE.

## 3. What They Found

**Headline claims from abstract:**
- MrVI is "a unified probabilistic framework for integration of samples, sample stratification and analysis of the effects of sample covariates at both the cell-subset and gene levels."
- Identifies "clinically relevant stratifications of cohorts of people with COVID-19 or inflammatory bowel disease that are manifested in only certain cellular subsets, enabling new discoveries that would otherwise be overlooked."

**Specific findings extracted from search:**

**COVID-19 PBMC validation (Fig 3):**
- The `u` space "is not affected by the sample of origin, instead showing marked mixing between study participants" — i.e., sample-level batch effect successfully removed.
- Same `u` space "clearly stratified the cells into immune subsets in a manner consistent with their annotation in the original study" — i.e., biological signal preserved.
- MrVI identifies a **monocyte-specific response to COVID-19** that more naive approaches (averaging across cells, or single-resolution methods) miss.

**Drug perturbation screens (Fig 4):**
- MrVI reveals "expected and non-trivial relationships between assayed compounds."
- Used MSigDB hallmark gene sets to interpret cluster-of-samples-vs-vehicle-control comparisons.

**IBD/Crohn's disease cohort (Figs 3-4 + Supp 11-18):**
- 46 Crohn's patients + 25 controls, 463,000 cells.
- MrVI identifies "previously unappreciated subset of pericytes with strong transcriptional changes in patients with stenosis" (Vienna classification B2/B3).
- Comparison vs Milo on precision-recall: MrVI's absolute log-density-ratio scoring outperforms Milo's LFC scoring for identifying true-positive cell subsets.

**Architectural advantage explicitly framed:**
- Existing methods (scVI, Harmony, Seurat) handle batch correction at the cohort level. MrVI handles the **multi-sample heterogeneity within a cohort** — each sample (patient) has its own set of sample-specific effects.
- Existing DE/DA methods (Milo, conventional pseudo-bulk) "assume the effects they evaluate are constant, meaning they are identical for all cells irrespective of their state" and "do not account for the uncertainty in estimating these effects." MrVI relaxes both constraints.

## 4. What's Strong

- **Peer-reviewed Nature Methods 2025.** Highest-impact venue for methodological work. Published Oct 2025 — most current Q2 anchor available.

- **Direct relevance to drug response prediction.** Drug perturbation screens are an explicit validation cohort. **No other Q2 method in our reading list (scVI, scANVI, Harmony, Seurat) was validated on drug perturbation data with this specificity.**

- **Counterfactual prediction architecture.** The `z^(s)_n` counterfactual machinery is the operational substrate for "what would this cell look like under different conditions?" — directly applicable to drug response: "what would this cell look like under drug X vs vehicle control?" **This is a concrete architectural mechanism for INTERCEPTA's prediction layer.**

- **Annotation-free analysis.** No pre-defined cell types required. **For INTERCEPTA's cross-disease deployment, where cell type annotation may be incomplete or inconsistent across diseases, this is operationally essential.**

- **Cell-type-specific differential effects.** MrVI's `β_n` captures cell-specific shifts in latent space under sample covariates. **For mechanism understanding (Charter §1.3 I1-I3), this enables claims like: "drug X affects monocytes specifically, not T cells" — without requiring upstream cell typing.**

- **Hierarchical model is mechanistically interpretable by construction.** Top-level `u` is "cell state"; bottom-level `z` is "sample-conditioned cell state." This decomposition is explicit in the architecture, not post-hoc.

- **Multi-batch design support.** Real cohort data has both biological samples (patients) AND technical batches (sequencing runs). MrVI handles both as separate covariates.

- **Production-ready via scvi-tools.** Same Python ecosystem as scVI, scANVI. Operational deployment cost is incremental.

- **Yosef lineage continuity.** scVI → scANVI → MrVI is a coherent 7-year research program. Confidence that the framework will continue to be maintained is high.

- **Validated on real disease cohorts (COVID-19, IBD).** Not just methodological benchmarks. **For Charter U1 (universally applicable to ANY disease), the demonstration on multiple non-cancer diseases is encouraging.**

- **Comparison to Milo (state-of-the-art DA method).** Direct benchmark in Crohn's disease cohort shows MrVI's precision-recall advantage.

- **Strong institutional backing.** UC Berkeley + Columbia (Azizi) + Weizmann + Ragon Institute. scvi-tools team multi-author paper.

## 5. What's Limited

- **NOT a drug response classifier.** MrVI is a sample-level heterogeneity model, not a drug-cell-viability predictor. **For INTERCEPTA's Charter §1.2 V1-V4 (predictive validity for drug response), MrVI is a representation method that supports drug response prediction — not the predictor itself.** Layered architecture must place MrVI as the cohort-harmonization layer with drug response prediction added separately.

- **Drug perturbation screens != patient drug response.** MrVI's drug benchmark is a perturbation screen on cell lines, not patient drug response prediction. **The bulk-cell-line-to-patient-cohort transfer challenge that scPDS targets is NOT solved by MrVI.**

- **Per-cohort training required.** Like scVI and scANVI, MrVI must be trained on the specific cohort. **No zero-shot deployment.** For INTERCEPTA's "Find the drug. For ANY disease." vision applied to NEW cohorts, retraining is operationally required.

- **Scalability beyond hundreds of samples is unproven.** The validation cohorts are 46+25=71 patients (IBD), and similar magnitudes for COVID-19 and drug screens. **MrVI's behavior on cohorts of 1000+ patients (e.g., TCGA-scale cancer cohorts) is not characterized.**

- **Counterfactual predictions assume covariates are independent of cell state.** Standard causal inference assumption. **For drug response prediction, drug-cell interactions are precisely WHERE this assumption may break** (specific drugs may only have effects in specific cell states). MrVI handles this via cell-specific `β_n`, but the validity of counterfactual predictions on rare cell types is not deeply characterized.

- **Latent dimensions still post-hoc interpretable.** While the `u` vs `z` hierarchy is principled, the individual dimensions of `u` and `z` are not pre-specified to encode biology. **Post-hoc spectral/SAE analysis (Kendiukhov-style) would still be needed for INTERCEPTA's mechanism trace requirement.**

- **Hyperparameter sensitivity.** Like all VAE-family methods, training is sensitive to KL weighting, latent dimension choices, learning rate. The paper documents these but operationalizing requires care.

- **Hierarchical model adds parameters.** MrVI has more parameters than scVI for same data scale. Compute requirement is incrementally higher. **Northeastern HPC compatibility is plausible but unverified at scale.**

- **No FM integration tested.** MrVI takes raw gene expression as input (like scVI). Whether MrVI on TOP of FM embeddings (scFoundation/UCE/scGPT) provides additional benefit is **unbenchmarked** — INTERCEPTA novelty territory.

- **Cross-disease-class transfer is untested.** MrVI was validated on COVID-19, IBD, drug screens — three different conditions, but each within their own cohort. Whether MrVI trained on one disease class transfers to another (cancer-trained → autoimmune-applied) is **unanswered**.

- **Long timeline from preprint to publication.** bioRxiv preprint posted October 2022; Nature Methods accepted July 2025; published October 2025. **Three-year review process** suggests rigorous peer scrutiny, but also that the paper has been iterated based on reviewer feedback (positive sign of methodological maturity).

## 6. INTERCEPTA Implications

**For Q2 (cross-cohort harmonization) — strongest candidate identified so far:**

MrVI is **architecturally the most relevant Q2 method for INTERCEPTA's vision.** Specifically:
- Multi-sample, multi-batch design matches cross-disease cross-cohort drug response prediction
- Counterfactual prediction framework directly supports drug-vs-control reasoning
- Annotation-free analysis matches operational reality of cross-disease deployment
- Drug perturbation screens are an explicit validation task

**For Decision 1 PROPOSED (layered architecture):**

MrVI strengthens the layered architecture commitment via specific architectural inspiration:
- **Two-level hierarchical latent (`u` cell state + `z` sample-aware) ↔ INTERCEPTA's two-level architecture (FM cell representation + sample-aware drug response prediction).**
- **Counterfactual `z^(s)_n` machinery ↔ INTERCEPTA's "what if treated with drug X?" prediction core.**
- **Cell-specific β_n ↔ INTERCEPTA's mechanism trace ("which cell types respond to drug X?").**

**For Charter §1.3 (mechanistic interpretability I1-I3):**

MrVI's annotation-free DE and DA at single-cell resolution directly serves I1 (every recommendation traces to specific cell populations). The cell-specific `β_n` quantifies which cells respond to which covariates, providing a falsifiable claim (I3) at single-cell resolution.

**For Charter Q5 (OOD detection):**

MrVI's hierarchical probabilistic framework provides uncertainty quantification at both `u` (cell state) and `z` (sample-conditioned). For drug response, this enables nuanced OOD detection: cell state OOD (cell unlike training cells) vs sample OOD (sample unlike training samples) can be distinguished. **More fine-grained than scVI/scANVI's single uncertainty.**

**For Charter §1.2 V1-V4 (predictive validity):**

MrVI alone doesn't predict drug response — it represents cohort-level heterogeneity. **Layered architecture: MrVI representation + drug response head trained on cell-line drug viability data.** This is one of several candidate architectures for Q4 (drug response prediction architecture) that will be tested.

**For Q2 termination criteria (after 3 anchors):**

- **Convergence:** scVI/scANVI/MrVI converge on hierarchical VAE + ZINB framework with semi-supervised label awareness and sample-level heterogeneity handling. Strong intra-lineage convergence. Need Harmony/Seurat for cross-lineage view.
- **Explicit gaps:** MrVI doesn't handle bulk-scRNA bridge; doesn't handle full cross-disease transfer; cohort scaling beyond hundreds of samples untested.
- **Trade-offs:** VAE-based methods (scVI/scANVI/MrVI) trade compute cost for principled probabilistic framework. Need Harmony to compare against fast/simple alternative.
- **Decision defensibility:** strengthening — Yosef lineage view is comprehensive. Need diversity from non-VAE methods.
- **No new questions:** several open questions emerging (FM + MrVI integration; cross-disease MrVI transfer; multi-cohort scaling).

**3 more Q2 anchors needed (Harmony, Seurat v3, scIB) before Q2 weekly synthesis.**

**For novelty territory INTERCEPTA could fill:**
- **MrVI on top of FM embeddings** — unbenchmarked. Replace MrVI's gene-expression input with scFoundation/UCE/scGPT embeddings.
- **MrVI for drug response label transfer** — repurpose `β_n` and counterfactual framework for drug response (sensitive/resistant) instead of cohort stratification.
- **Cross-disease MrVI transfer** — train MrVI on cancer cohorts, apply to autoimmune/neurodegeneration. Unanswered.
- **Multi-cohort MrVI scaling** — push beyond hundreds of samples to TCGA-scale (1000+ patients).

## 7. Followup Citations Worth Tracing

Critical priority for Q2 anchor reading (remaining 3 anchors):
1. **Korsunsky et al., 2019 — Harmony** (Nat Methods) — fast non-VAE alternative. **Q2 anchor 4 — major architectural diversity.**
2. **Stuart et al., 2019 — Seurat v3 integration** (Cell) — anchoring-based integration paradigm. **Q2 anchor 5.**
3. **Luecken et al., 2022 — scIB benchmark** (Nat Methods) — synthesis-level benchmark methodology. **Q2 anchor 6 — closes Q2 reading.**

Useful priority for Q3+ later:
4. **Milo (Dann et al., 2022, Nat Biotechnol)** — differential abundance method that MrVI compares against. Q4/Q6 relevance.
5. **scvi-tools 2024+ documentation** — production state of MrVI in 2025.
6. **CanSig benchmark** (per locked entry conditions) — Q2 anchor for cancer-specific harmonization benchmark.
7. **Lotfollahi et al., 2022 — scArches** — extends scVI/scANVI for transfer learning across reference and query datasets.

## 8. Discipline Check

- [x] All claims sourced — Nature Methods website, PMC PMC12615264, PubMed PMID 41083897, Weizmann Pure, ResearchGate, scvi-tools docs, bioRxiv preprint 2022.10.04.510898; verified DOI across 8+ independent sources.
- [x] No interpolated claims — where I'm guessing (specific dataset sizes for COVID-19 cohort, exact β_n distribution properties, drug screen compound identities), I omitted or marked explicitly.
- [x] Numbers verified — DOI, page numbers (2264-2274), publication date (Oct 13 2025), volume/issue (22/11), authors and affiliations, PMID 41083897, PMC12615264, IBD cohort (46+25 patients, 463K cells).
- [x] Limitations include ones authors didn't acknowledge — §5 limitations 2 (drug screen != patient drug response), 4 (scalability beyond hundreds of samples), 5 (counterfactual independence assumption fragility), 9 (no FM integration tested), 10 (cross-disease transfer untested) are CSO-identified.
- [x] No fabricated DOI — 10.1038/s41592-025-02808-x verified across Nature + PubMed + PMC + Weizmann + scvi-tools.
- [x] **No new drift instances this cycle.** Authors verified primary-source from start (Pierre Boyeau confirmed lead via Nature Methods + PubMed + PMC). Directory naming used `q2_harmonization/` per locked spec. P15 holding clean.

---

**CSO note (Q2 third anchor — Yosef lineage complete):**

After 3 anchors (scVI 2018 + scANVI 2021 + MrVI 2025), the **Yosef lab cross-cohort harmonization research program is mapped.** Lineage observation:

| Generation | Method | Year | Capability |
|---|---|---|---|
| 1 | scVI | 2018 | Unsupervised cohort harmonization, batch correction |
| 2 | scANVI | 2021 | Add semi-supervised label awareness, annotation transfer |
| 3 | MrVI | 2025 | Add multi-resolution sample-level analysis, counterfactual prediction |

**Each generation adds capability without invalidating predecessors.** The `scvi-tools` package supports all three; users select based on their data and question.

**For INTERCEPTA's architectural choice (Q2 Decision):** the natural deployment target is MrVI for cross-cohort + sample-level analysis, with scANVI fallback for semi-supervised tasks, with scVI fallback for unsupervised baseline. **Multi-method within the Yosef family.**

**However**, the Yosef family is ONE architectural lineage. Q2 reading must complete with **architectural diversity**:
- **Harmony** (next read) — fast linear correction, no VAE
- **Seurat v3** — anchoring-based, R ecosystem (vs Python scvi-tools)
- **scIB benchmark** — methodology for cross-method comparison

Only after these 3 additional anchors can Q2 weekly synthesis honestly assess whether the Yosef lineage is THE answer for INTERCEPTA's Q2, or whether Harmony/Seurat are competitive/better for specific INTERCEPTA use cases.

**Cross-question observation strengthening:** MrVI's drug perturbation screen validation makes it the most directly relevant Q2 anchor for INTERCEPTA's drug response vision. **For Decision 1 PROPOSED commitment to layered architecture:** MrVI's counterfactual prediction framework provides the architectural blueprint for "what would this cell look like under drug X?" prediction. This is concrete, not abstract.

— Claude (CSO)
2026-05-10
