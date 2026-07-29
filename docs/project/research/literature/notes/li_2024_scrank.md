# Li et al., 2024 — scRank: drug-responsive cell types from untreated scRNA-seq using target-perturbed gene regulatory networks

## 0. Identification
- **Citation:** Li C, Shao X, Zhang S, Wang Y, Jin K, Yang P, Lu X, Fan X, Wang Y. *Cell Reports Medicine* 5(6):101568, 2024 May 15.
- **DOI:** 10.1016/j.xcrm.2024.101568 ✓ (verified Cell Reports Medicine, GitHub ZJUFanLab/scRank, EPMC EPMC11228399)
- **Senior authors:** Xiaohui Fan + Yi Wang (Zhejiang University)
- **License:** CC BY-NC (Elsevier open access)
- **Code:** github.com/ZJUFanLab/scRank
- **Layer 1 question:** Q3 anchor 4 — **alternative paradigm to transfer learning**
- **Read by:** Claude (CSO) — 2026-05-10

## 1. Why this paper

scRank is the **alternative paradigm to all SCAD/scDEAL/scAdaDrug transfer-learning approaches**. Where the DA family transfers drug response labels from bulk to scRNA via learned representations, scRank uses **gene regulatory networks (GRNs) and in silico drug target perturbation** — no transfer learning, no labeled bulk training data needed.

This is critical because **scRank works on untreated scRNA-seq data alone** (with drug target gene as input). For scenarios where bulk training data is sparse (most non-cancer diseases), scRank is the only viable Q3 method.

## 2. What they did

**Architecture (2 components):**
1. **GRN reconstruction:** `Constr_net` function — builds gene regulatory network from expression profiles per cell type
2. **In silico target perturbation:** `rank_celltype` function — perturbs the target gene of the drug in each cell type's GRN, measures network propagation effect, ranks cell types by responsiveness

**Inputs:**
- Untreated scRNA-seq (gene expression + cell type labels)
- Drug name (or specific target gene + MOA: agonist/antagonist)
- Species (human/mouse)

**Outputs:** Ranked list of cell types by predicted drug responsiveness

**Validation:**
- Simulated datasets (controlled ground truth)
- Real datasets: medulloblastoma, major depressive disorder
- Specific case study: **macrophage subpopulation responsive to tanshinone IIA in myocardial infarction (validated experimentally)**

## 3. What they found

- "Superior performance over existing methods" on simulated and real datasets
- Identified drug-responsive cell types consistent with literature for medulloblastoma and major depressive disorder
- **Tanshinone IIA + myocardial infarction case study:** scRank identified specific macrophage subpopulation as responsive; validated by independent in vivo experiments
- Works on diseased datasets that lack drug intervention — fundamentally different operational scope from transfer learning

## 4. What's strong

- **NO BULK TRAINING DATA REQUIRED.** Operates on untreated scRNA-seq alone. **Eliminates the bulk-to-scRNA bridge problem entirely** — by going around it.
- **Validated experimentally** (tanshinone IIA case) — beyond computational metrics
- **Validated on non-cancer disease (major depressive disorder, myocardial infarction)** — broader scope than SCAD/scDEAL/scAdaDrug
- **Cell-type-level interpretability built-in.** Output is "which cell types respond to this drug" — directly answers a clinically actionable question
- **Drug-target-driven mechanism trace.** Perturbs known drug targets, propagates effects through GRN — every prediction is mechanistically traceable
- **Cell Reports Medicine** — clinical-medicine-focused journal, signaling broader impact intent
- **Open-source CC BY-NC** with maintained GitHub
- **Operates with disease-only datasets** — addresses the "drug treatment data is rare" problem head-on

## 5. What's limited

- **Requires known drug target gene.** For drugs with unknown or polypharmacological targets, scRank cannot operate. **For novel drug discovery, scRank is not directly applicable** — it's drug-repurposing-oriented.
- **GRN reconstruction quality is the bottleneck.** Standard GRN methods (correlation-based, regression-based) have known limitations. Garbage-in, garbage-out.
- **Cell-type-level granularity, not single-cell granularity.** Output is "macrophage subset 3 is responsive" not "this individual cell will respond." Less granular than DA-based methods.
- **No quantitative drug response prediction (IC50, AUC).** Output is rank order of cell types, not predicted drug efficacy.
- **In silico perturbation assumes known MOA (agonist/antagonist).** Works for well-studied drugs; less so for new mechanisms.
- **"Superior performance" claim depends on which baseline.** Compared methods include Beyondcell and other signature-based approaches; not directly compared to SCAD/scDEAL/scAdaDrug on same datasets.
- **GRN reconstruction is per-cell-type.** Cells must be pre-clustered/typed before scRank — depends on quality of upstream cell typing.
- **Cross-disease deployment requires known drug targets per disease.** Limited automation.
- **No FM integration.** GRN-based, not embedding-based.

## 6. INTERCEPTA implications

**For Q3:** scRank represents a **fundamentally different solution to the bulk-to-scRNA bridge** — sidestep it entirely by using disease-specific scRNA-seq + known drug targets. **Charter §8.1's layered architecture should accommodate BOTH paradigms:**
- DA-based (SCAD/scDEAL/scAdaDrug) for unknown-MOA drugs with bulk training data
- GRN-perturbation-based (scRank) for known-target drugs in disease-specific scenarios

**For Charter §1.1 universality (especially U1, U3 — non-cancer diseases):** scRank's ability to work on untreated disease-specific scRNA-seq makes it operationally superior for non-cancer deployments where bulk training data is sparse. **For autoimmune, neurodegenerative, rare diseases, scRank may be the primary Q3 method.**

**For Decision 1 layered architecture:** scRank's GRN-perturbation paradigm is consistent with the Charter §8.1 commitment to multi-method architecture. **It is genuinely complementary to DA-based methods**, not redundant.

**For Charter §1.3 mechanistic interpretability (I1-I3):** scRank natively provides:
- I1: cell-type-level traceability (which cells respond)
- I2: pathway-level mechanism (GRN propagation from drug target)
- I3: falsifiable claim (predicted responsive cells testable by experiment — validated in tanshinone IIA case)

**This is the most mechanistically interpretable Q3 method read so far.**

**For novelty:** scRank + FM-derived GRNs (FM-aware regulatory inference) + cross-disease drug repurposing = direct INTERCEPTA candidate architecture. Unbenchmarked.

## 7. Followup citations
1. **Beyondcell** (Fustero-Torre 2021 Genome Med 13:187) — pathway-signature alternative; baseline scRank compares against
2. **Raghavan et al., 2021 Cell** — cell state and drug response in pancreatic cancer; cited in scRank
3. **Goyal et al., 2023 Nature 620:651** — "Diverse clonal fates emerge upon drug treatment" — cell-state plasticity context
4. **GRN methods** (SCENIC, GENIE3) — upstream tools for scRank's Constr_net
5. **DrugFormer** (graph-augmented LLM for drug response, 2024) — graph-based alternative

## 8. Discipline check
- [x] All claims verified (Cell Reports Medicine, GitHub, EPMC, multiple sources)
- [x] DOI verified across 5+ sources
- [x] Authors verified — Chengyu Li first; Xiaohui Fan + Yi Wang senior (Zhejiang University ZJUFanLab)
- [x] Limitations include CSO-identified ones (target requirement, GRN quality dependence, no quantitative prediction)
- [x] Honest reporting that scRank's "superior performance" is vs different baseline set than DA family
- [x] **No new drift this cycle.**

— Claude (CSO), 2026-05-10
