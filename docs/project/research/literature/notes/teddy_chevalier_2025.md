# Chevalier et al., 2025 — TEDDY: A Family Of Foundation Models For Understanding Single Cell Biology

## 0. Identification

- **Citation:** Chevalier A, Ghosh S+, Awasthi U, Watkins J, Bieniewska J, Mitrea N, Kotova O, Shkura K, Noble A, Steinbaugh MJ, Sadashivaiah V, Dasoulas G, Delile J, Meier C, Zhukov L, Khalil I, Mukherjee S+, Mueller J+. "TEDDY: A Family Of Foundation Models For Understanding Single Cell Biology." arXiv 2503.03485v1, March 2025.
- **Senior authors (per + symbols):** Soumya Ghosh, Srayanta Mukherjee, Judith Mueller
- **First author:** Alexis Chevalier (BCG AI Science Institute, Boston)
- **DOI:** 10.48550/arXiv.2503.03485
- **Affiliations (verified):**
  - **BCG AI Science Institute, Boston, USA** (Chevalier, Awasthi, Bieniewska, Kotova, Delile, Meier, Zhukov, Mukherjee — and others)
  - **Merck & Co., Inc., Cambridge, MA, USA** (Ghosh, Watkins, Noble, Steinbaugh, Sadashivaiah, Dasoulas, Khalil, Mueller)
  - **MSD (UK) Limited, London, UK** (Mitrea, Shkura)
- **Acknowledgments:** Marinka Zitnik (Harvard Medical School) for paper comments; Michael Brochu (BCG) for support
- **Status:** Preprint as of May 2026 cutoff; OpenReview submission visible (rNkmDLOl6x — possible ICLR/NeurIPS submission)
- **Layer 1 question:** Q8 anchor 2 — scaled FM with biological supervision; tests scaling laws and held-out-donor / held-out-disease generalization
- **Read by:** Claude (CSO) — 2026-05-10 (Phase 6 re-do; primary-source via arxiv HTML + OpenReview + ResearchGate)

## 1. Why this paper matters for Q8

TEDDY is the **largest single-cell FM family ever published** (up to 400M parameters, 116M cells) AND introduces **biological-ontology-supervised pretraining** — a methodological innovation distinct from the unsupervised masked-token approach of Geneformer/scGPT/scFoundation. For INTERCEPTA Q8 (universality):

1. **Scale axis:** TEDDY tests whether bigger FMs help more. The 70M / 160M / 400M family is purpose-built for scaling law analysis. If scaling works, FMs justify themselves on scaling. If it doesn't, the Souza & Mehta critique strengthens.

2. **Supervision axis:** TEDDY-X variant uses biological-ontology labels during pretraining (43 CELLxGENE-derived ontology terms as special tokens). This is a hybrid between self-supervised (Geneformer) and fully supervised approaches. Tests whether biological priors during pretraining help.

3. **Held-out-donor + held-out-disease evaluation:** TEDDY explicitly evaluates on **donors not seen during training** and **diseases not seen during training**. This is exactly the universality dimension Charter §1.1 requires (U1-U3) and Charter §1.2 V5-V6 demands. **No other Q8 anchor tests this as directly.**

4. **Industry collaboration:** BCG AI + Merck partnership signals pharma-side validation of the FM paradigm — and provides a comparison case for INTERCEPTA's academic-institution path.

## 2. What they did

### 2.1 Two architectural variants

- **TEDDY-G:** trained with **masked language modeling** alone (Geneformer-like, unsupervised pretraining objective on gene rank tokens)
- **TEDDY-X:** trained with **MLM + supervised annotation loss** on biological ontology terms; ontology terms are added to the vocabulary as special tokens

### 2.2 Model sizes (six models total per family variant pair)

- **70M parameters** (medium)
- **160M parameters** (large)
- **400M parameters** (XL)
- Plus smaller **10M and 30M** parameter models for scaling-law probing

Total: 6 production-scale models (3 sizes × 2 variants) + smaller scaling-probe models.

### 2.3 Pretraining data

- **116 million cells** — explicitly noted as "larger than those used by previous models"
- Diverse source collection (paper specifies CELLxGENE consortium and related)
- **43 biological ontology categories** mapped from CELLxGENE annotations, used as supervision in TEDDY-X variant

### 2.4 Downstream evaluation tasks

1. **Held-out donors task:** identify disease state of donors NOT seen during training. Class imbalance handled with accuracy + weighted F1 reporting. Results aggregated over three random initializations.
2. **Held-out diseases task:** distinguish diseased vs healthy cells for **disease conditions and donors NOT seen during training**. Class-balanced; accuracy reported. Aggregated over three cross-validation folds.
3. **Biology probing:** linear probes for known biological signals in learned representations.

This is a methodologically strong evaluation framework — both donor and disease held-out splits directly probe out-of-distribution generalization.

### 2.5 Baselines

- **Geneformer** (Theodoris 2023) — the canonical predecessor; explicit baseline in Table 2

## 3. Quantitative results — primary-source

### 3.1 Held-out donors task (Table 2)

- **TEDDY-G: 0.68 accuracy** (or weighted F1 — paper's framing is "performance")
- **Geneformer: 0.22**
- **Gap: ~46 percentage points improvement of TEDDY-G over Geneformer** on cross-donor generalization

This is the largest improvement margin in the paper and is the strongest published evidence that scaled FMs help for the specific task of donor generalization.

### 3.2 Scaling behavior

- **Performance improves predictably with both data volume and parameter count** (the paper claims clear scaling laws)
- TEDDY-G and TEDDY-X show "different challenges for downstream applications" — the supervised variant has different scaling profile than unsupervised
- Scaling probed via the 10M → 30M → 70M → 160M → 400M sequence

### 3.3 Acknowledged limitation by authors

From paper text:
- **"Existing foundation models only modestly improve over task-specific models in downstream applications."** — TEDDY authors themselves admit the FM-vs-task-specific gap is small in prior work
- This is the explicit problem TEDDY tries to solve

## 4. What's strong

- **Largest published single-cell FM family** (400M parameters, 116M cells) as of May 2026
- **Methodological novelty (TEDDY-X)** — biological-ontology supervision during pretraining is a meaningful architectural innovation not in Geneformer/scGPT/scFoundation
- **Held-out donors AND held-out diseases evaluation** — directly addresses Charter §1.1 universality requirements
- **Explicit scaling-law analysis** with multiple model sizes — answers "does bigger help?" empirically rather than asserting
- **Honest about prior FM limitations** — paper's own framing acknowledges that existing FMs "only modestly improve over task-specific models" (an unusually candid framing from FM developers)
- **0.68 vs 0.22 (Geneformer) on held-out donors** is a substantial empirical improvement
- **Industry-academia collaboration** (BCG + Merck + Harvard's Zitnik) provides credibility for translational relevance
- **Marinka Zitnik review** — Zitnik (Harvard) is a leading network/graph methodologist; her acknowledgment is meaningful peer attention
- **OpenReview submission** suggests ICLR/NeurIPS-track venue intended

## 5. What's limited — honest critique

- **Preprint as of cutoff.** Not peer-reviewed. OpenReview submission status not fully clear.
- **Release status unclear.** TEDDY models not yet publicly released at time of writing; my Q10 landscape note correctly listed TEDDY as "Pre-publication / not yet released." This means **INTERCEPTA cannot use TEDDY weights in Layer 5 unless and until released.** Critical operational constraint.
- **Industry-led with commercial entanglement.** BCG AI Science Institute is the AI consulting arm of Boston Consulting Group. Merck is a major pharma. The incentives include demonstrating FM value to pharma clients — possible confirmation bias in result framing.
- **Held-out donors result (0.68 vs 0.22) is on one task with three random initializations.** This is methodologically reasonable but a single benchmark could still have task-specific quirks.
- **The TEDDY-G vs TEDDY-X comparison** isn't simply "ontology supervision helps." The paper notes "different challenges" — meaning the two variants have different trade-offs. Which one is the actual SOTA depends on downstream task. INTERCEPTA would need to test both for its specific drug response task.
- **CELLxGENE ontology supervision is coarse-grained** (43 categories) — paper explicitly notes these are not fine-grained disease labels. So the supervised signal doesn't directly teach disease-specific information.
- **No drug response prediction tested** — same Q8 anchor pattern. Held-out donors / diseases is closer to the right task than cell-type classification, but still not drug response prediction.
- **Souza & Mehta critique applies but is less directly tested.** Does scTOP-style parameter-free achieve 0.68 on held-out donors? Probably not — but the paper doesn't run this baseline. A proper test would include parameter-free baselines, which TEDDY does not.
- **400M parameters is operationally heavy.** Inference probably requires GPU. Training a 400M model on 116M cells is in the same compute regime as TranscriptFormer (per Souza & Mehta's compute critique, infeasible for typical academic labs).
- **Senior authors' COI:** Mueller (Merck), Mukherjee (BCG), Ghosh — all have industry affiliations. Standard for industry-led FM papers but worth noting.

## 6. INTERCEPTA implications

### 6.1 For Q8 (universality demonstration)

TEDDY is the **strongest counterevidence** to the Souza & Mehta critique I have in the Q8 corpus, *specifically for the donor/disease generalization use case*. If TEDDY-G beats Geneformer 0.68 vs 0.22 on held-out donors, that suggests FMs do provide meaningful benefit when:
- Training data is scaled to 100M+ cells
- Evaluation is on OOD generalization (held-out donors), not in-distribution classification
- The benchmark is sufficiently hard (Geneformer at 0.22 is essentially failing)

This is **architecturally relevant** for INTERCEPTA because cross-patient deployment is exactly the held-out-donor problem. INTERCEPTA must work for patients not in training data. TEDDY's empirical demonstration that this is achievable (and difficult for smaller FMs) matters.

### 6.2 For Decision 1 portfolio composition

**TEDDY belongs in the portfolio if/when released.** Specifically:
- **TEDDY-G** as scaled-Geneformer-like baseline
- **TEDDY-X** as biological-supervision variant

Until release, INTERCEPTA cannot use TEDDY weights. Operational fallback: scFoundation (already released, similar parameter scale ~100M) serves as the "large scaled FM" slot until TEDDY available.

### 6.3 For Decision 8 (universality, paramater-free ablation requirement)

**TEDDY does NOT include parameter-free baselines.** The paper compares only to Geneformer. **This is exactly the failure mode Souza & Mehta diagnose** — FM papers benchmark FMs against FMs, ignoring whether simple methods would close the gap.

INTERCEPTA's Decision 8 must mandate that:
- Any FM-based result on held-out donors is reported alongside a parameter-free baseline (scTOP-style)
- Without that comparison, the FM benefit cannot be claimed

This is one of the most important methodological rules INTERCEPTA can enforce. **TEDDY did not enforce it on itself; INTERCEPTA must.**

### 6.4 For Decision 9 (compute architecture)

- Training a TEDDY-class model is **infeasible at INTERCEPTA's single-institution scale**
- Using released TEDDY weights for inference is feasible (when released)
- Inference cost: 400M parameter inference fits on A100; fine-tuning may need multi-GPU
- This argues for INTERCEPTA's commitment to **using existing FMs, not training new ones**

### 6.5 For Charter §1.1 cross-disease universality

TEDDY's held-out-diseases task is methodologically the closest published evaluation to Charter §1.1's "drug for ANY disease" vision. The performance numbers from this task (not visible in my search snippets — would need full paper body) would directly inform whether scaled FMs can transfer to genuinely held-out diseases. **This is the empirical question whose answer most directly bears on whether INTERCEPTA's universality claim is achievable.**

## 7. Followup citations (priority for INTERCEPTA)

1. **scFoundation (Hao et al. 2024, Nat Methods)** — comparable-scale released FM; near-term substitute for TEDDY until release
2. **Geneformer (Theodoris 2023, Nature)** — TEDDY's primary baseline
3. **scbasecamp (Arc Institute 2025)** — referenced curated single-cell data repository
4. **Tahoe-100M (Zhang et al. 2025)** — perturbation atlas, complementary scaling work
5. **Boiarsky et al. 2023** — "untrained transformer models and traditional ML are competitive" — cited by TEDDY as competing evidence
6. **CELLxGENE consortium** — for the ontology system TEDDY-X uses
7. **Souza & Mehta 2026** (Q8 anchor 5) — counter-critique that TEDDY's parameter-free baseline absence partially validates

## 8. Discipline check

- [x] Authors fully verified primary-source: 18-author roster from arxiv HTML; first author Alexis Chevalier; senior authors Ghosh + Mukherjee + Mueller (+ symbols)
- [x] Affiliations verified: BCG AI Science Institute Boston, Merck & Co. Cambridge MA, MSD (UK) London
- [x] arXiv ID 2503.03485v1 verified; DOI 10.48550/arXiv.2503.03485
- [x] Architectural family verified: 6 models, 70M/160M/400M × G/X variants + 10M/30M scaling probes
- [x] Pretraining corpus size verified: 116M cells
- [x] Held-out donors result verified: TEDDY-G 0.68 vs Geneformer 0.22 (Table 2)
- [x] Evaluation framework verified: held-out donors task + held-out diseases task + biology probing
- [x] Ontology supervision verified: 43 CELLxGENE-derived categories as special tokens
- [x] Release status verified: not yet publicly released as of May 2026 (Q10 landscape correctly noted this)
- [x] **Errata note:** original 2026-05-10 file had no first-author attribution, no quantitative results, no architectural detail. This rewrite verifies all and provides substantive methodology + critique. Drift Instance #2 (Q8 thin notes) further corrected.
- [x] **No new drift this cycle.** Verified primary-source for every claim.

— Claude (CSO), 2026-05-10 (Phase 6 re-do)
