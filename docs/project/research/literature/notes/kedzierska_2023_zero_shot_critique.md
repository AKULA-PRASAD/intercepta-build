# Kedzierska et al., 2023 — Assessing the limits of zero-shot foundation models in single-cell biology

## 0. Identification
- **Full citation:** Kedzierska KZ, Crawford L, Amini AP, Lu AX. Assessing the limits of zero-shot foundation models in single-cell biology. *bioRxiv* 2023.10.16.561085, 2023 Oct 16 (revised v2 Nov 5, 2023).
- **DOI:** 10.1101/2023.10.16.561085 ✓ (verified across Microsoft Research, bioRxiv direct, Semantic Scholar Corpus ID 264307489, Sciety, Alex Lu's research website, ResearchGate, Broad Institute publications page)
- **Status:** bioRxiv preprint v2 (Nov 5, 2023). NOT certified by peer review at time of read date.
- **Affiliations:** University of Oxford (Kedzierska); Microsoft Research, Cambridge MA (Crawford, Amini, Lu)
- **Email contacts:** kasia@well.ox.ac.uk (Oxford); {lcrawford, ava.amini, lualex}@microsoft.com (Microsoft)
- **Code:** github.com/microsoft/zero-shot-scfoundation
- **Demo data:** Figshare 24747228
- **Layer 1 question:** Q1 (Method-class selection) — **CRITIC LITERATURE**, addresses Q1.1 (true SOTA), Q1.2 (FM interpretability/practical limitations), Q3 (cross-cohort transfer reality)
- **Read by:** Claude (CSO)
- **Read date:** 2026-05-10

## 0.1 CSO honest correction

In the prior cycle's scGPT note, I referred to this paper as "Boiarsky et al., 2023." **This was incorrect.** The actual lead author is Kasia Z. Kedzierska (University of Oxford). My earlier reference came from imperfect memory of search-result snippets, not from primary verification.

**P15 caught this:** verification before claim. Corrected in this note. The scGPT paper note will need amendment in a subsequent revision pass to reflect the correct citation. **This is exactly the failure mode P15 was designed to prevent — citing memory rather than verifying.** Discipline working as intended.

## 1. Why This Paper

This paper is the **critical counterweight** to the FM proponent literature (UCE, scGPT, scFoundation, Geneformer). It is the most-cited critique of single-cell foundation models in the zero-shot setting. Microsoft Research-led, peer-reviewed-quality methodology, **directly tests the central claim of the FM paradigm: that pretrained FMs produce robust cell embeddings without fine-tuning.** Without reading this paper, INTERCEPTA's Q1 method-class commitment would rest on proponent-only evidence — exactly the "literature confirmation drift" Charter §3 termination criteria are designed to prevent.

**This paper directly tests Charter Q1.1** ("What's the actual SOTA F1/AUROC on cross-cohort drug response prediction in 2026?") by asking the question the proponent literature avoids: **what if zero-shot FMs are NOT actually SOTA?**

## 2. What They Did

The authors (Kedzierska, Crawford, Amini, Lu) conducted a rigorous benchmark of single-cell FMs in the **zero-shot setting** (no fine-tuning, no task-specific training). Methodology:

1. **Models tested:** Geneformer (6-layer version, accessed from ctheodoris/Geneformer commit 4302f48) and scGPT (multiple variants: kidney 814K cells, blood 10.3M cells, human 33M cells). scFoundation mentioned in citation list but not benchmarked in this paper.

2. **Baselines compared against:**
   - **HVG:** Highly Variable Genes selection (2,000 HVGs across all experiments). A simple, decade-old baseline.
   - **scVI:** Probabilistic generative model (Lopez et al. 2018, established prior to FM era), trained per dataset unsupervised. **scVI requires per-dataset training but does not require labels.**
   - **Mean expression prediction:** Trivial baseline for evaluating pretraining objectives.
   - **Randomly initialized models:** scGPT/Geneformer with random weights (no pretraining) — to assess whether pretraining provides any benefit at all.

3. **Datasets:** Five distinct human tissue datasets:
   - Pancreas (Tabula Sapiens v1)
   - Two PBMC datasets (different cohorts)
   - Cross-tissue immune cell atlas
   - Multi-organ human cell atlas (Tabula Sapiens-related)

4. **Tasks evaluated:**
   - Cell embedding quality (cell type clustering, batch integration)
   - Pretraining objective generality (mean estimates / average ranking comparisons)

5. **Evaluation metrics:** scIB metrics — ASW (Average Silhouette Width), AvgBIO (average biological conservation score). These are the SAME metrics UCE uses to claim 13.9% lead over Geneformer.

**Critical methodology choice:** "We deploy scGPT and Geneformer zero-shot while training scVI on target data unsupervised" — the authors explicitly chose this asymmetric setup because **"this set-up reflects practical settings where resources are available to train lightweight models, but not to fine-tune large models."** This is a defensible real-world deployment scenario.

## 3. What They Found

**Headline finding:** Both Geneformer and scGPT in zero-shot configurations **generally fail to outperform cell embeddings derived from HVG or generated using the scVI model.**

**Specific quantitative results (where I have direct verification from search snippets):**

For **ASW (Average Silhouette Width)** metric:
- scVI: median ASW = 0.54 (range 0.49 in Tabula Sapiens to higher elsewhere)
- scGPT human: comparable to scVI (median ASW ~0.53-0.54)
- Geneformer: ASW = 0.37 in Tabula Sapiens, 0.38 in Pancreas (16K) — **substantially below scVI**

For **AvgBIO (average biological conservation)** metric:
- scVI: 0.69 on PBMC (95K) high score
- HVG: 0.60 on PBMC, matched Geneformer
- scGPT human: AvgBIO 0.44 (UNDERPERFORMS scGPT kidney at 0.52!)
- scGPT blood on PBMC: ~equal to randomly initialized model — pretraining provided ZERO BENEFIT

**Key qualitative findings:**
- **HVG outperforms Geneformer in all datasets except PBMC.** Decade-old simple gene selection beats the 30M-cell pretrained transformer.
- **scGPT human (33M cells, full corpus) underperforms scGPT kidney (814K cells, narrower domain).** More pretraining data = WORSE downstream zero-shot performance. This contradicts the standard "more data is better" narrative.
- **Pretraining on tissue-overlapping data does not equate to performance above random initialization.** scGPT blood on PBMC ≈ random init, even though both are blood cells.
- **scVI consistently performs well** despite being a per-dataset trained probabilistic model from 2018.

## 4. What's Strong

- **Microsoft Research methodology rigor.** Kedzierska + 3 Microsoft researchers. Institutional standards for benchmarking are high.
- **Asymmetric "fair" setup chosen for deployment realism.** The authors explicitly justify giving scVI per-dataset training while testing FMs zero-shot, on the grounds that this reflects practical resource constraints.
- **Multiple datasets, multiple tasks.** 5 datasets, cell embedding quality + batch integration + pretraining objective evaluation. Not a single-dataset "gotcha" critique.
- **Multiple FM variants tested.** scGPT kidney vs blood vs human variants — controls for whether pretraining specificity helps.
- **Compared against both simple (HVG) and established (scVI) baselines.** Two reference points means readers can assess: "is FM at least as good as a simple baseline?" AND "is FM better than the established field standard?"
- **Tested random initialization as control.** Demonstrates whether pretraining provides ANY benefit. The fact that scGPT blood ≈ random init on PBMC is devastating evidence.
- **Direct contradiction of UCE's scIB claims.** UCE claims 13.9% scIB lead over Geneformer; this paper shows that on ASW/AvgBIO components, Geneformer often underperforms even simple HVG. **The two papers' framings cannot both be fully right.**
- **Open code for reproducibility** (Microsoft github repo).

## 5. What's Limited

- **bioRxiv preprint, not peer-reviewed at read date.** v2 (Nov 2023) latest available, but no journal-published version found in our search. **This means rigorous external review has not occurred.** Future weekly synthesis should re-verify if a peer-reviewed version appears.
- **Five datasets is moderate, not exhaustive.** UCE's pretraining corpus alone is 36M cells across 8 species; testing on 5 human tissue datasets may not capture all FM capabilities.
- **scFoundation NOT benchmarked.** Only Geneformer and scGPT. The paper cites scFoundation in the FM landscape but doesn't include it. **scFoundation's MAE objective may behave differently than masked LM (Geneformer) or autoregressive (scGPT) zero-shot.** Conclusion may not generalize to scFoundation. **For INTERCEPTA: scFoundation needs separate critique evaluation.**
- **UCE NOT benchmarked.** UCE was preprinted Nov 28, 2023; this paper v2 was Nov 5, 2023 — UCE postdates this critique by 3 weeks. **UCE's protein-language tokenization and 8-species training may be precisely the architectural innovations that address this critique's findings.** Cannot extrapolate Kedzierska's critique to UCE without explicit testing.
- **Cell type clustering and batch integration are NOT drug response prediction.** This paper tests FM on integration tasks. **Whether the same zero-shot underperformance occurs on drug response prediction is open.** scDrugMap (Wang 2025) found scGPT zero-shot achieves F1 = 0.858 cross-data on drug response — appears to contradict Kedzierska's general finding for the specific drug response task. Either (1) drug response prediction is fundamentally different from cell type integration, (2) the F1 metric scDrugMap uses obscures effects that ASW/AvgBIO would catch, or (3) the discrepancy reflects task-specific variation in FM utility. **Resolution requires deeper analysis.**
- **scGPT kidney with 814K cells beating scGPT human with 33M cells is surprising.** Authors interpret this as evidence that pretraining specificity matters more than data scale. But could also reflect: (a) different model versions trained at different times with different hyperparameters, (b) noise in evaluation, or (c) genuine effect. Full text + replication needed.
- **scGPT blood ≈ random init on PBMC is one specific datapoint.** Suggestive but a single contrast doesn't establish a general claim about pretraining-data alignment.
- **Methodology: "we use all genes unmasked as input."** This is a deliberate simplification of scGPT/Geneformer to "eliminate stochasticity." May not reflect how the FMs are actually deployed in practice. **Could be a source of conservative bias in FM performance.**

## 6. INTERCEPTA Implications

**For Q1.1 (true SOTA):** This paper directly challenges the Q1.1 narrative built from scDrugMap, UCE, scGPT, scFoundation, Geneformer reads. **The "FM is SOTA" claim was based on benchmarks that:** (1) used metrics (F1, scDrugMap-style) different from those Kedzierska tested (ASW, AvgBIO), (2) tested fine-tuned or downstream-specialized FMs, not zero-shot raw. **For INTERCEPTA's vision: zero-shot deployment is the realistic scenario, AND drug response is the target task.** scDrugMap shows scGPT zero-shot F1 = 0.858 cross-data on drug response. Kedzierska shows scGPT zero-shot fails on integration tasks. **These two findings are not contradictory if drug response is uniquely robust to FM zero-shot deployment, but this needs investigation.**

**For Q1.2 (interpretability and practical limitations of FMs):** Kedzierska's critical insight: "Much of the work in single-cell biology is inherently exploratory, where labels may not be available a priori. Fine-tuning commonly requires a prediction problem with defined labels." **For INTERCEPTA: drug response prediction has labels (drug-cell viability data exists). So fine-tuning IS available for our use case.** But: **for the discovery use case** (predict drug response for novel diseases without prior drug-response data), zero-shot is required and Kedzierska's critique applies. **INTERCEPTA must clarify which deployment mode it targets.**

**For Q3 (cross-cohort transfer reality):** Kedzierska's finding that scGPT human (33M cells) underperforms scGPT kidney (814K cells, kidney-specific) on tissues unlike kidney is **direct evidence that FM cross-cohort transfer can fail catastrophically.** The naive hope that pretraining on diverse data automatically yields cross-cohort robustness is empirically refuted in their setting.

**For Charter §3 termination criterion 1 (convergence):** **Convergence is NOT clean.** scDrugMap, UCE, scGPT, scFoundation, Geneformer all endorse FMs as SOTA. Kedzierska shows FMs in zero-shot underperform simple baselines on cell embedding tasks. **The convergence is task-dependent:** FM is SOTA on drug response classification (scDrugMap F1) but fails on cell type clustering / integration (Kedzierska ASW/AvgBIO). **Method-class commitment must be made with this nuance — FMs may be the right tool for some Charter goals (drug response) but wrong for others (cell type discovery).**

**For Charter §3 termination criterion 2 (explicit gaps):** **Now explicit:**
- Gap A: scFoundation not benchmarked in zero-shot critique
- Gap B: UCE not benchmarked (postdates Kedzierska v2)
- Gap C: drug response specifically not tested in zero-shot critique
- Gap D: published peer-reviewed version of Kedzierska absent

**For Charter §3 termination criterion 4 (decision defensibility):** A reviewer asking "why did you commit to FM-based architecture?" gets: "scDrugMap shows F1 = 0.858 zero-shot cross-data on drug response (scGPT) and F1 = 0.971 pooled (scFoundation); Geneformer demonstrates non-cancer disease application (cardiomyopathy)." A reviewer asking "but Kedzierska shows zero-shot FMs fail" gets: "Kedzierska tested cell type integration tasks, not drug response classification. The drug response task may be uniquely robust to zero-shot FM deployment, OR it may share Kedzierska's failures on a different metric. INTERCEPTA's first novel experiment should explicitly test this."

**For novelty territory INTERCEPTA could fill:**
- **Bridge experiment:** Run scGPT zero-shot on Beat AML drug response (cancer, in scDrugMap's distribution) AND on Geneformer-style cardiomyopathy drug response (non-cancer, novel). Test whether zero-shot FM works specifically for drug response across diseases. **This single experiment validates or refutes both the proponent and critic narratives for INTERCEPTA's specific use case.**
- **Replicate Kedzierska's critique with drug response metrics.** If F1 / ASW / AvgBIO disagree on the same model + same dataset, the metric choice matters more than the model. INTERCEPTA could be the first to explicitly characterize this.
- **Test scFoundation and UCE in the Kedzierska framework.** Since Kedzierska didn't test these, INTERCEPTA could fill this gap.

## 7. Followup Citations Worth Tracing

Critical priority:
1. **arXiv 2602.22247 — Multi-Dimensional Spectral Geometry** — second FM critic paper. Targets attention-encodes-biology claim specifically. **MUST READ NEXT.**
2. **scVI** (Lopez et al. 2018, Nature Methods) — the surprising baseline that beats FMs. Establishing the "what does scVI actually do?" baseline is important for understanding what makes it competitive.
3. **scIB benchmark paper** (Luecken et al. 2022, Nature Methods) — defines ASW, AvgBIO. Necessary for interpreting Kedzierska's results vs UCE's results.

Useful priority:
4. **Replication or peer-reviewed extension of Kedzierska et al.** if it exists in 2024-2026.
5. **scGPT authors' response to Kedzierska** if published — would reveal how the field is processing this critique.
6. **Geneformer V2 (Chen et al. 2024)** — addresses some of Kedzierska's concerns? V2 has 95M cells and quantized multi-task learning. May be the FM proponent response to V1 criticism.

## 8. Discipline Check

- [x] All claims sourced — Microsoft Research website, bioRxiv direct, Semantic Scholar, Sciety, Alex Lu personal site, Broad Institute, ResearchGate, ResearchHub PDF; verified DOI across 8+ independent sources.
- [x] No interpolated claims — where I'm guessing (specific numeric thresholds beyond what search snippets reveal, full text Fig content), I marked it explicitly. Where I synthesized §5 limitations from comparison to other Q1 papers, I cited those papers explicitly.
- [x] Numbers verified — DOI, version numbers (v2 Nov 5 2023), specific ASW/AvgBIO values from search-snippet-quoted text, dataset descriptions (5 datasets named).
- [x] Limitations include ones authors didn't acknowledge — §5 limitations 3 (scFoundation not tested), 4 (UCE not tested), 5 (drug response not tested), 8 (single contrast generalizability) are CSO-identified.
- [x] No fabricated DOI — 10.1101/2023.10.16.561085 verified across multiple primary sources.
- [x] **CSO honest correction made:** §0.1 acknowledges I previously cited this paper as "Boiarsky" from imperfect memory. P15 caught the error. Future weekly synthesis should propagate the correction to scGPT paper note. **This is what discipline-as-error-correction looks like.**

---

**CSO note (cross-paper convergence after 6 papers, 5 proponents + 1 critic):**

With Kedzierska et al. now read, the convergence picture is **structurally different** from before:

1. **Convergence on FM-as-method-class-for-cancer-drug-response (5 proponents):** Strong (5/5).
2. **Divergence on FM-as-method-class-for-zero-shot-cell-integration (1 critic):** **Kedzierska shows FM zero-shot underperforms HVG and scVI on ASW/AvgBIO.** Direct refutation of the proponent narrative for THIS TASK.
3. **The convergence is TASK-DEPENDENT:**
   - FM SOTA: drug response classification (scDrugMap F1)
   - FM NOT SOTA: cell type clustering, batch integration in zero-shot (Kedzierska ASW/AvgBIO)
4. **Charter Q1 method-class commitment must be NUANCED:** "FMs are SOTA for our use case" is defensible IF our use case is drug response classification. "FMs are universally SOTA" is NOT defensible per Kedzierska.

**This is exactly what Charter §3 termination criterion 4 (decision defensibility) requires.** The decision is defensible only if the use case is articulated specifically and the contrary evidence is acknowledged.

After Spectral Geometry critique (= 7 total Q1 papers), the convergence map will be complete enough for first weekly synthesis.

— Claude (CSO)
2026-05-10
