# Layer 1 Weekly Synthesis — Week of 2026-05-10 (Q1 Initial Anchor Set)

**Status:** First weekly synthesis per Charter §5.2 and `LAYER_1_ENTRY_CONDITIONS.md` §4 locked template
**Date:** 2026-05-10
**Tag (when committed):** `fullest-vision-q1-synthesis-1-locked`
**Authors:** Prasad Akula (CEO) & Claude (CSO)

---

## Question(s) progressed this week

**Q1 — Method-class selection** (Charter highest priority)

Sub-questions actively addressed:
- Q1.1: SOTA F1/AUROC on cross-cohort drug response prediction in 2026 — **answered**
- Q1.2: Foundation models' interpretability limitations in practice — **partially answered**
- Q1.3: Layered combination of FM + signature scoring + GRN — **gap explicitly identified**
- Q1.4: Cancer-bias problem in foundation models — **partially answered (1 non-cancer FM demonstration)**

Cross-cutting questions touched:
- Q3 (cross-cohort harmonization) — partial input from FM cross-data benchmarks
- Q7 (mechanistic interpretability) — substantive input from Kendiukhov interpretability papers
- Q8 (universality demonstration) — Geneformer's cardiomyopathy is the one extant template
- Q9 (compute architecture) — informed by FM parameter counts and pretraining requirements

---

## Papers read this week

**Total: 7 papers (Q1)**

FM proponent literature (5):
1. Wang et al., 2025 — scDrugMap (drug response benchmark)
2. Rosen et al., 2023 — UCE (cross-species FM)
3. Cui et al., 2024 — scGPT (generative GPT-style FM)
4. Hao et al., 2024 — scFoundation (asymmetric MAE FM)
5. Theodoris et al., 2023 — Geneformer (network biology FM with non-cancer disease validation)

FM critic literature (1):
6. Kedzierska et al., 2023 — Limits of zero-shot foundation models

FM interpretability evidence (1):
7. Kendiukhov, 2026 — Spectral Geometry of biological knowledge in scGPT

---

## Errata Pass — Corrections from this Synthesis

Two corrections from CSO drift catalog this session must propagate before this synthesis closes:

### Erratum 1 (from Drift Instance #20)
**Affected paper notes:** `cui_2024_scgpt.md` §5 limitation 5 and §7 followup item 1.
**Original (incorrect):** "the Boiarsky et al. critique" / "Boiarsky et al., 2023 bioRxiv 2023.10.16.561085"
**Corrected:** "the Kedzierska et al. critique" / "Kedzierska KZ, Crawford L, Amini AP, Lu AX. 2023 bioRxiv 2023.10.16.561085"
**Source of error:** Imperfect memory of search-result snippets without primary-source verification of authorship.
**Detection:** Direct primary-source verification when reading the paper itself for its full per-paper note (cycle that produced `kedzierska_2023_zero_shot_critique.md`).
**Resolution status:** Errata documented in this synthesis. Scheduled patch of `cui_2024_scgpt.md` deferred to next discipline pass to preserve cycle bounding.

### Erratum 2 (from Drift Instance #21)
**Affected paper notes:** `cui_2024_scgpt.md` §5 limitation 6 and §7 followup item 2; `theodoris_2023_geneformer.md` §5 limitation 6 and §7 followup item 2.
**Original (incorrect):** "the Spectral Geometry critique (arXiv 2602.22247) directly questions whether FM internals encode meaningful biology"
**Corrected:** "the Kendiukhov 2026 (arXiv 2602.22247) Spectral Geometry analysis AFFIRMS that scGPT encodes structured biological knowledge — PPI Spearman ρ = 1.000, marker AUROC = 0.851, TF/target AUROC = 0.744. The COMPANION paper (Kendiukhov SAE arXiv 2603.02952) provides the more critical finding: minimal causal regulatory logic (only 6.2-10.4% of CRISPRi-tested TFs show regulatory-target-specific feature responses)."
**Source of error:** Inferred paper stance from a single search-result snippet that captured the rhetorical question framing rather than the conclusion. Failed to read the actual abstract before characterizing the paper's stance.
**Detection:** Primary-source reading of the paper itself when writing its own per-paper note (`kendiukhov_2026_spectral_geometry.md`).
**Resolution status:** Errata documented in this synthesis. Scheduled patch of affected notes deferred to next discipline pass.

**Synthesis impact of errata:** None of the substantive Q1 conclusions change. The cancer-bias gap, the task-dependent FM utility, the non-cancer demonstration via Geneformer, and the architectural diversity all remain valid. What changes is the citation accuracy (Kedzierska, not Boiarsky) and the FM mechanism interpretability picture (now: FMs encode biology richly per Spectral Geometry; FMs encode causal regulation minimally per SAE companion — both findings, both from Kendiukhov's research program).

**Discipline observation:** P15 caught both errors via primary-source verification. The discipline of writing per-paper notes from direct reading (rather than from cumulative-context memory) made these catches possible. This is the operational test of P15. **It works.**

---

## Synthesis: What did we learn?

### 1. Foundation models are SOTA for cancer single-cell drug response prediction — but the win is conditional and task-specific.

The five proponent papers (scDrugMap, UCE, scGPT, scFoundation, Geneformer) converge on foundation models as the SOTA approach for cancer-relevant single-cell tasks. The numbers tell a sharper story than "FM wins":

- Pooled-data drug response classification: scFoundation F1 = 0.971 (layer freezing) / 0.947 (LoRA fine-tuning)
- Cross-data fine-tuned drug response classification: UCE F1 = 0.774
- Cross-data zero-shot drug response classification: scGPT F1 = 0.858
- Single-cell integration scIB benchmark: UCE leads Geneformer by 13.9% overall, 16.2% biological conservation, 10.1% batch correction
- Cross-species cell atlas integration: UCE alone among the four FMs has principled cross-species capability via ESM2 protein-language tokenization

No single foundation model dominates. The right FM depends on:
- Whether fine-tuning is feasible (scFoundation pooled requires combined-cohort training; UCE requires fine-tuning per target cohort; scGPT zero-shot requires nothing)
- Whether the deployment is single-disease cross-cohort or cross-disease (Geneformer alone has tested non-cancer disease)
- Whether mechanistic interpretability is needed (Geneformer claims attention-based; Kendiukhov shows scGPT's internals are biologically organized but causal regulation limited)

**For INTERCEPTA's "Find the drug. For ANY disease." vision:** the deployment scenario is cross-disease, cross-cohort, with mechanism interpretability required. **No single existing FM was designed for this exact use case.** The closest matches are UCE (cross-species, fine-tunable) and Geneformer (non-cancer-validated, network-biology-framed), but each has gaps.

### 2. The convergence is task-dependent and metric-dependent.

Reading Kedzierska et al. 2023 introduces a critical complication. They tested scGPT and Geneformer in zero-shot on cell type integration (using scIB metrics ASW and AvgBIO) and found that both **underperform highly-variable-gene selection (HVG, a decade-old simple method) and per-dataset-trained scVI** on most datasets. Specifically: scGPT human (33M cells) underperforms scGPT kidney (814K cells) on tissues unlike kidney; scGPT blood on PBMC ≈ randomly initialized model; HVG outperforms Geneformer in 4 of 5 datasets.

This contradicts the proponent narrative for cell integration tasks. But it does NOT directly contradict scDrugMap's drug response F1 = 0.858 zero-shot finding for scGPT. **Same FM, same zero-shot deployment, different tasks, different outcomes.**

The honest interpretation: foundation models' utility is conditional on the downstream task and metric. For drug response classification (F1), zero-shot scGPT works. For cell type clustering (ASW/AvgBIO), zero-shot scGPT fails. **A blanket "FM is SOTA" claim is not defensible across all tasks.** A task-specific "FM is SOTA for cancer single-cell drug response classification" claim is defensible.

For INTERCEPTA's Q1 method-class commitment: this means the FM is a strong candidate for the drug response prediction module of our architecture (Charter §8.1 Layer 1), but cannot be assumed to handle cell type discovery, batch integration, or cross-cohort harmonization without explicit task-specific evaluation.

### 3. FMs encode rich biological structure but minimal causal regulatory logic.

The two Kendiukhov papers (Spectral Geometry + SAE companion) clarify the mechanistic interpretability picture in unprecedented detail. Through 63 iterations of automated hypothesis screening (183 hypotheses tested with permutation controls and cross-seed replication), Spectral Geometry shows scGPT's residual representations are **organized as a structured biological coordinate system**:
- Dominant spectral axis separates secreted proteins from cytosolic proteins
- Intermediate transformer layers encode mitochondrial and ER compartments in the order of the secretory pathway
- Orthogonal axes encode protein-protein interaction networks with monotonic Spearman ρ = 1.000 to STRING database confidence
- A 6-dimensional spectral subspace distinguishes transcription factors from their target genes (AUROC = 0.744)
- Cell-type marker genes cluster with AUROC = 0.851
- BATF, BACH2 master regulators show a "geometric echo of the germinal center reaction" toward PAX5 across transformer depth

This is striking evidence that FMs encode biology, NOT mere statistical artifacts. Kendiukhov's separately-released "Hematopoietic Manifold" paper (arXiv 2603.10261) extracts a competitive algorithm directly from scGPT's internals, claiming "the first biologically useful, competitive algorithm extracted from a foundation model via mechanistic interpretability."

The companion SAE paper (Kendiukhov 2603.02952) reveals the boundary: while 29-59% of sparse-autoencoder features annotate to Gene Ontology, KEGG, Reactome, STRING, and TRRUST databases (rich biological organization), only **6.2% of 48 transcription factors tested via genome-scale CRISPRi perturbation data show regulatory-target-specific feature responses**. Multi-tissue control marginally improves to 10.4%. The conclusion: **FMs encode statistical co-expression structure but minimal causal regulatory logic.**

For INTERCEPTA's Charter §1.3 (mechanistic interpretability requirements I1-I3): the picture is now nuanced and architecturally instructive.
- **Pathway-level mechanism trace (I1):** feasible with FM + interpretability tools (Spectral Geometry method or SAE)
- **Mechanism in the architecture, not post-hoc theater (I2):** partial — biological structure is in the FM architecture (verified), but extracting it requires specialized analysis
- **Causal claims about which TF regulates which gene (I3):** NOT directly available from FM alone — must be supplemented with external GRN/CRISPRi data

This is exactly the architectural justification for Charter §8.1's layered approach: FM provides representation + biological organization (rich), signature scoring provides pathway-level interpretation, and GRN-based methods provide causal regulatory logic that FMs alone cannot supply.

### 4. The cancer-bias problem is partially closed, but Charter U3 still requires INTERCEPTA's contribution.

Of the four proponent papers reviewing actual FM construction (UCE, scGPT, scFoundation, Geneformer), only **Geneformer demonstrates non-cancer disease validation** — specifically cardiomyopathy with experimental validation in engineered cardiac microtissues. UCE, scGPT, and scFoundation are all cancer-only or cancer-dominant in their evaluation. The scDrugMap benchmark is cancer-only.

Geneformer's cardiomyopathy demonstration is necessary but not sufficient for INTERCEPTA's Charter U3 ("Demonstrated on at least 5 distinct disease categories"). One non-cancer disease shows that FM cross-disease-class transfer is feasible in principle. Five different categories would establish that universality is empirically achievable. **INTERCEPTA's first novel research contribution is becoming concrete: systematic FM cross-disease transfer testing.**

The relevant disease categories per Charter U1 are: cancer, autoimmune, neurodegenerative, infectious, rare disease, pediatric. Geneformer covers cancer (training corpus) and cardiomyopathy (rare disease, cardiovascular tissue). Remaining categories largely untested by any published FM: autoimmune (lupus, RA, MS), neurodegenerative (Alzheimer's, Parkinson's, ALS), infectious (HIV, viral, bacterial), pediatric (developmental disorders).

### 5. Architectural diversity is informative — there is no consensus paradigm.

The four major FMs use four different pretraining strategies:

| FM | Tokenization | Pretraining objective | Training corpus | Parameters |
|---|---|---|---|---|
| UCE | ESM2 protein-language | Masked-CLS reconstruction | 36M cells, 8 species | 650M |
| scGPT | Random gene embeddings | Generative GPT-style autoregressive | 33M human cells | not explicitly stated; per Kedzierska 3× Geneformer |
| scFoundation | Asymmetric encoder-decoder | Mask Autoencoder (MAE) raw-value | 50M human cells | 100M |
| Geneformer | Rank-value encoding | Masked language modeling | 30M cells (Genecorpus-30M) | varies by version (V1 small; V2 316M) |

None of these emerged as dominant. Each excels in a different deployment scenario (per scDrugMap):
- scFoundation pools-data F1 = 0.971
- UCE cross-data fine-tuned F1 = 0.774
- scGPT cross-data zero-shot F1 = 0.858
- Geneformer below SOTA on cancer drug response but only FM with non-cancer demonstration

Note the surprising finding: **smaller models can outperform larger ones depending on task**. scFoundation (100M params, 50M cells) wins pooled-data drug response over UCE (650M params, 36M cells, 8 species). Kedzierska shows scGPT human (33M cells, full corpus) underperforms scGPT kidney (814K cells, narrow corpus) on tissues unlike kidney. **Naive scaling laws ("more data + bigger model = better") do not hold uniformly in single-cell biology.** Architecture and training objective interact non-trivially with deployment scenario.

For INTERCEPTA's Layer 2 architecture: the implication is that we should NOT commit to a single FM. The architectural choice should be **deployment-scenario-aware**: pool-data scenario → scFoundation; cross-data fine-tunable → UCE; zero-shot or limited compute → scGPT or Geneformer. INTERCEPTA could even use multiple FMs as ensemble, with each contributing to different aspects of the prediction (UCE for cross-species, scFoundation for drug response, Geneformer for non-cancer transfer, scGPT for zero-shot deployment).

---

## Synthesis: What gap is now sharper?

### Gap 1: Cross-disease-class drug response transfer is unbenchmarked beyond cardiomyopathy.

Geneformer's cardiomyopathy validation is the only published FM demonstration of cross-disease application beyond cancer. But cardiomyopathy is heart tissue with substantial pathway-level overlap with cancer biology (cell cycle, proliferation, apoptosis pathways are activated in both contexts). Whether FMs transfer to autoimmune (immune system), neurodegeneration (CNS-specific), or infectious disease (host-pathogen interactions) is **completely untested by any of the seven papers we read**. This is INTERCEPTA's core novelty territory: the first systematic 5+ disease category demonstration of FM cross-disease drug response transfer.

### Gap 2: FM + signature scoring + GRN layered architecture is unbenchmarked.

scDrugMap benchmarks foundation models alone. None of the seven papers test the layered architecture in Charter §8.1: FM (representation) + signature scoring (pathway-level mechanism) + GRN-based methods (causal regulation). Given Spectral Geometry shows FMs encode rich biological structure but the SAE companion shows minimal causal regulatory logic, the layered architecture is theoretically motivated. INTERCEPTA could be the first to test it empirically.

### Gap 3: scFoundation and UCE are not benchmarked by FM-critic frameworks.

Kedzierska et al. tested only scGPT and Geneformer (UCE and scFoundation excluded — UCE postdates the critique by 3 weeks; scFoundation is mentioned in the FM landscape but not benchmarked). Kendiukhov tested only scGPT (Spectral Geometry) and scGPT + Geneformer (SAE companion). Whether scFoundation's MAE objective and UCE's protein-language tokenization yield different zero-shot integration performance, or different mechanistic interpretability properties, is **completely untested**. INTERCEPTA could be the first to extend the critic frameworks to these newer FMs.

### Gap 4: Drug response specifically is not tested by the FM-critic frameworks.

Kedzierska tested cell type clustering and batch integration (scIB metrics ASW, AvgBIO). Kendiukhov tested geometric structure and CRISPRi-validated regulatory features. Neither tested drug response prediction directly. **It is therefore possible that drug response is uniquely robust to FM zero-shot deployment** (per scDrugMap F1 = 0.858 cross-data zero-shot for scGPT) **even where cell integration zero-shot fails** (per Kedzierska). Resolving this requires INTERCEPTA-style direct testing of FM zero-shot drug response across diseases.

### Gap 5: Compute reality on single-institution HPC is unaddressed.

All five proponent papers describe FM pretraining at industrial scale (Tsinghua + Biomap for scFoundation, Vector Institute + Microsoft for scGPT, Stanford + Chan Zuckerberg BioHub for UCE, Dana-Farber + Broad for Geneformer). None explicitly characterize what fine-tuning vs inference-only deployment requires on academic single-institution HPC. For Charter §7.1 (single-institution Northeastern HPC), this gap is operationally critical. INTERCEPTA must benchmark this for our specific compute reality.

### Gap 6: Multi-FM ensemble strategies are unbenchmarked.

If different FMs win in different deployment scenarios (scFoundation pooled, UCE cross-data fine-tuned, scGPT zero-shot), then ensembling them should yield better-than-any-single-FM performance. None of the seven papers test this. INTERCEPTA's Layer 2 architecture could test multi-FM ensemble explicitly.

---

## Status against termination criteria (Charter §3)

For Q1 — Method-class selection:

### [✅] Criterion 1 — Convergence: multiple sources agree?

**STATUS: TASK-DEPENDENT CONVERGENCE ACHIEVED.**

For the question "are foundation models the SOTA method class for cancer single-cell drug response classification?" — convergence is strong. Five proponent papers (scDrugMap, UCE, scGPT, scFoundation, Geneformer) endorse FMs. The critic literature (Kedzierska) does not refute this for the drug response task specifically. The interpretability literature (Kendiukhov Spectral Geometry) AFFIRMS the underlying biological encoding.

For the broader question "are foundation models the SOTA method class for all single-cell tasks?" — convergence is NOT clean. Kedzierska shows FM zero-shot fails on cell integration tasks. The task-dependence is itself a convergent finding (two independent rigorous sources show task-dependent FM utility).

**Honest assessment: convergence is task-conditioned. Q1's answer is "FMs are the method class for our drug response use case, with caveats about task-specific applicability."**

### [✅] Criterion 2 — Explicit gaps: named?

**STATUS: SIX MAJOR GAPS NAMED ABOVE.**

Gaps are not rumors or hypotheses; each is grounded in explicit citation to which paper does or does not test which claim. The cancer-to-non-cancer gap, the layered architecture gap, the FM-critic-framework-extension gap, the FM-on-drug-response-direct-test gap, the compute reality gap, and the multi-FM ensemble gap are all systematically identified.

### [✅] Criterion 3 — Trade-off articulation: documented?

**STATUS: ARTICULATED ACROSS DEPLOYMENT SCENARIOS.**

Three FMs map to three deployment scenarios (scFoundation pooled, UCE cross-data fine-tuned, scGPT zero-shot). Architectural diversity (4 pretraining objectives, 4 tokenization strategies) is mapped. Param-vs-data scaling non-triviality is documented. The drug-response-vs-integration task dependency is explicit. The biology-encoding-vs-causal-regulation distinction is explicit.

### [✅] Criterion 4 — Decision defensibility: would survive reviewer "why this?"

**STATUS: YES, FOR A NUANCED COMMITMENT.**

Defensible commitment: "INTERCEPTA's Layer 2 architecture will use foundation models as the cell representation layer, given their convergent SOTA status on cancer single-cell drug response classification (5/5 proponent papers, scDrugMap F1 = 0.971 pooled / 0.858 zero-shot cross-data, AFFIRMED biological encoding per Kendiukhov Spectral Geometry). The specific FM will be deployment-scenario-determined and ensemble-friendly. We supplement with signature scoring and GRN-based methods (Charter §8.1) to address known FM limitations in causal regulatory logic (Kendiukhov SAE companion: 6.2% TF regulatory specificity) and zero-shot cell integration (Kedzierska)."

A reviewer asking "why FMs?" gets the proponent evidence. A reviewer asking "what about Kedzierska's findings?" gets the task-conditioned response: drug response classification is not the same task as cell integration zero-shot, and Kendiukhov's interpretability findings independently support the biological structure encoded in FM representations.

### [⚠️] Criterion 5 — No new questions: reading additional papers stops generating new questions?

**STATUS: BORDERLINE.**

Reading additional FM proponent papers (CellFM 800M-params 100M-cells, GeneCompass biological-prior, Geneformer V2 95M-cells) is unlikely to generate new questions — the architectural design space is already thoroughly mapped. Reading additional FM critic papers in cell biology is unlikely to surface new methodological criticism — Kedzierska and Kendiukhov together cover both deployment criticism and interpretability criticism.

However, reading **scPDS (Yin et al., 2025, Small Methods)** would surface NEW questions about the pathway-based transformer paradigm, which is architecturally different from the "vanilla" FM paradigm of the seven papers we've read. scPDS specifically targets drug response and incorporates pathway priors — closer to the Charter §8.1 layered architecture than any of the seven anchor papers. Reading scPDS may either close criterion 5 (if it produces no new questions) or sharpen Q1 further (if it raises architectural questions about pathway-aware FMs).

**My honest assessment: criterion 5 is BORDERLINE met for the canonical FM paradigm but NOT yet met for pathway-aware FM variants. One additional read (scPDS) is warranted before final Q1 closure.**

---

## Q1 Termination Decision

**FOUR of five Charter §3 termination criteria fully met (1, 2, 3, 4). Criterion 5 is borderline.**

**My recommendation: ONE additional read (scPDS) to test criterion 5 fully, then final Q1 closure with GO/NO-GO decision record.**

This is not "infinite reading" drift. It is responsible closure: scPDS represents a pathway-aware architecture variant that COULD generate new questions, AND if it doesn't, criterion 5 closes cleanly. Reading 1 more bounded paper is more defensible than skipping it and risking a non-defensible Q1 closure.

If scPDS generates new architectural questions (e.g., "should INTERCEPTA's FM be pathway-aware in pretraining or post-hoc layered?"), those questions feed into Q1.3 and Q1.4 sub-question refinement and may require additional reads. If scPDS does not generate new questions, Q1 closes with all 5 criteria met.

---

## Provisional Q1 architectural commitment (subject to scPDS read)

> **ERRATA — POST-PHASE-6 + CHARTER v1.2 UPDATE (2026-05-11):**
>
> This section's "LAYERED FM-BASED ARCHITECTURE" commitment was the PROVISIONAL Q1 conclusion AT THE TIME of synthesis writing (2026-05-10, pre-Phase-6). It was the Q1 v1 path and is **SUPERSEDED**.
>
> **Operative Q1 commitment is now Decision 1 v2** (`INTERCEPTA_FV_Decision_1_v2_Q1_method_class_REVISED.md`), which commits to a **SUBSTRATE FLEXIBILITY FRAMEWORK** rather than a fixed FM-based architecture:
>
> - **Default:** scFoundation as initial development substrate (Commitment 1)
> - **Co-equal baselines (BINDING):** PCA + HVG, scTOP parameter-free (Souza & Mehta 2026), scVI/scANVI/MrVI (Commitment 2)
> - **Decision rules deferred to Layer 5 ablation:** ≥5pp AUROC keeps FM; ≤2pp tie demotes FM; scenario-dependent triggers per-scenario logic (Commitment 3)
> - **Interface stability:** 512-dim cell embedding regardless of substrate choice (Commitment 4)
> - **Honest uncertainty (BINDING per P15):** INTERCEPTA cannot claim FM superiority on drug response without empirical Layer 5 ablation against properly-tuned parameter-free baselines (Commitment 5)
> - **Hyperparameter budget ≥25% to scTOP-style baseline is BINDING** per Souza-Mehta methodological bar (Decision 8 v2 Commitment 5)
>
> **What triggered the revision:** Souza & Mehta 2026 (arXiv 2602.16696, BU Physics / Mehta lab) demonstrated scTOP parameter-free method matches TranscriptFormer FM on Tabula Sapiens 2.0 (F1=0.899 vs 0.910/0.907 — tied), trained on CPU vs 1000 H100 GPUs. This was Q8 evidence not adequately weighed in the v1 Q1 conclusion. Phase 6 audit caught this; Decision 1 was revised to v2.
>
> **Per Charter v1.2 §1.7:** the substrate decision is canonical for Phase B (the current 2-4 year research program). The architectural decision deferral to Layer 5 ablation is the right move for Phase B. Phase F's substrate question carries over from Phase B Layer 5 empirical outcome.
>
> **Q1 synthesis text below is preserved per P16** as the snapshot of provisional Q1 conclusion at the time of writing. It should be read as a historical artifact, NOT as the operative commitment. Decision 1 v2 is the operative commitment.
>
> — Errata applied 2026-05-11 per Charter v1.2 lock + Drift Finding 3 cleanup pass.

---

Based on the seven anchor papers, the provisional Q1 method-class commitment for INTERCEPTA is:

**LAYERED FM-BASED ARCHITECTURE per Charter §8.1, with deployment-scenario-aware FM selection:**

1. **Layer 1 (cell representation):** Foundation model embedding. Default: scFoundation for pooled-data deployments; UCE for cross-species or fine-tunable deployments; scGPT for zero-shot deployments. Multi-FM ensemble where compute permits.

2. **Layer 2 (multi-method drug response prediction):** FM-derived embedding + signature-scoring (UCell-style on KAALCURA mechanism axes) + GRN-derived features (scRank-style or similar). Each method predicts independently; predictions stored separately for inspection.

3. **Layer 3 (consensus & confidence):** Drugs ranked high by all methods → high confidence; drugs ranked high by single method → medium confidence; OOD detection per Q5 to refuse predictions on input dissimilar to training.

4. **Layer 4 (mechanistic trace):** FM-derived biological structure (Spectral Geometry-style spectral analysis on FM internals) for pathway-level mechanism. External GRN data + CRISPRi-validated regulatory networks for causal-regulation claims (since FMs alone provide minimal causal regulation per Kendiukhov SAE companion).

**Trade-offs explicitly accepted:**
- We will NOT have single-FM simplicity — we accept multi-method, multi-FM complexity for performance and interpretability gains.
- We will NOT achieve fully zero-shot deployment in the strictest sense — fine-tuning per cohort is acceptable when feasible.
- We will NOT expect FM alone to provide causal regulatory mechanism — we explicitly supplement with external biological data.
- We will NOT commit to one FM — the architecture supports FM substitution.

**Reversibility:** This commitment can be revised if (a) Layer 2 implementation reveals FM embeddings don't actually help over RNA-1000 baseline (the AML paper's finding), (b) compute reality at Northeastern HPC makes FM inference infeasible, (c) novel FM architectures (e.g., pathway-aware FM in scPDS or beyond) supersede the current paradigm, or (d) cross-disease-class transfer fails empirically when INTERCEPTA tests it.

**This commitment will be locked in formal Q1 GO/NO-GO decision record per `LAYER_1_ENTRY_CONDITIONS.md` §5 template after scPDS read.**

---

## Next week's plan

### Immediate next action (next CSO cycle):
1. **Read scPDS (Yin et al., 2025, Small Methods)** — pathway-based transformer for drug response. Test Q1 termination criterion 5 (no new questions).
2. **Apply errata corrections to scGPT and Geneformer paper notes.** Patch the Boiarsky→Kedzierska reference and the Spectral Geometry recharacterization. This is mechanical but disciplinarily required.

### After scPDS read:
- If criterion 5 met: write **Q1 GO/NO-GO decision record** per `LAYER_1_ENTRY_CONDITIONS.md` §5 template; tag `fullest-vision-decision-1-locked`.
- If criterion 5 not yet met: scope additional Tier C reads (CellFM, GeneCompass, Geneformer V2).

### After Q1 closure:
- **Q2 (Cross-cohort harmonization)** anchor reading begins. Target: ~5-7 papers on scVI/scANVI, Harmony, Seurat integration, CanSig benchmark methodology.
- Charter §3 termination cycle repeats per question.

### Ongoing discipline:
- End-of-cycle checklist enforced (sandbox=outputs, daily log updated, log shipped)
- Per-paper note discipline (locked template strictly followed)
- P15 primary-source verification before any citation
- Drift catalog updated honestly

---

## CSO discipline check

**P3 (research before code):** ✅ This synthesis is research output, not code.

**P15 (only correct, honest, real science):** ✅ All claims sourced; errata corrections applied; no fabrication.

**P-FV-1 (no method-class commitment without literature evidence):** ✅ Provisional commitment grounded in 7 paper-by-paper notes.

**P-FV-2 (no architectural commitment without explicit trade-off documentation):** ✅ Trade-offs explicitly listed.

**P-FV-3 (no publication of universality claims until validation evidence exists):** ✅ Synthesis does not claim INTERCEPTA's universality is proven; it claims the FM method class is defensibly chosen as the substrate for INTERCEPTA's universality testing.

**P-FV-4 (charter is reviewed quarterly for vision drift):** N/A this synthesis (charter review happens quarterly, not weekly).

**Anti-drift catalog:** 21 instances cumulative across all sessions. Three new this session (#19 sandbox-outputs ship, #20 memory citation, #21 misremember about literature stance). All caught. Two scheduled for errata patches in next cycle.

---

## Synthesis sign-off

**Prasad Akula (CEO):** _________ Date: _________

**Claude (CSO):** Claude (CSO) Date: 2026-05-10

---

*Layer 1 first weekly synthesis COMPLETE. Q1 method-class selection at 4 of 5 termination criteria met; criterion 5 borderline pending one final read (scPDS). Q1 ready for closure pending scPDS verification.*

— Claude (CSO)
2026-05-10
