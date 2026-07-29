# Fustero-Torre et al., 2021 — Beyondcell: targeting cancer therapeutic heterogeneity in single-cell RNA-seq data

## 0. Identification
- **Citation:** Fustero-Torre C, Jiménez-Santos MJ, García-Martín S, Carretero-Puche C, García-Jimeno L, Ivanchuk V, Di Domenico T, Gómez-López G, Al-Shahrour F. *Genome Medicine* 13(1):187, 2021 Dec 16.
- **DOI:** 10.1186/s13073-021-01001-x ✓ (verified Genome Medicine fulltext, BioMed Central, ProQuest, ResearchGate)
- **Senior author:** Fátima Al-Shahrour (Spanish National Cancer Research Centre — CNIO, Bioinformatics Unit)
- **Code:** gitlab.com/bu_cnio/beyondcell + zenodo.org/record/5602819
- **License:** CC BY 4.0 (open access)
- **Layer 1 question:** Q3 anchor 5 — **drug-signature-scoring paradigm**
- **Read by:** Claude (CSO) — 2026-05-10

## 1. Why this paper

Beyondcell is the **third paradigm** for single-cell drug response prediction (alongside DA-based and GRN-perturbation-based). It uses **drug signature enrichment scoring** rather than learned representations or perturbation simulations. This is a different operational philosophy that leverages the prior knowledge encoded in published drug signatures.

For Q3, this fills the architectural diversity requirement — we now have all three major paradigms covered.

## 2. What they did

**Architecture:**
1. **Inputs:**
   - scRNA-seq expression matrix
   - Drug signature collection: drug perturbation signatures (PSC) OR drug sensitivity signatures (SSC) OR user-provided GMT/ranked matrix
2. **BCS computation:** For each drug-cell pair, calculate a **Beyondcell Score (BCS)** based on enrichment of the drug signature in the cell's expression
3. **Therapeutic Cluster (TC) identification:** Cells are grouped by BCS profiles into therapeutic clusters — cells within a TC share drug response patterns
4. **Switch Point (SP) calculation:** For each signature, the value (0-1 scale) where cells switch from down-regulated to up-regulated status. Identifies therapeutic homogeneity (SP=0 or SP=1) vs heterogeneity (intermediate SP)
5. **Sensitivity-based ranking** prioritizes drug candidates per cell or per cluster

**BCS interpretation:**
- BCS ranges 0 to 1
- For PSC: measures cell perturbation susceptibility
- For SSC: measures predicted drug sensitivity
- Functional signatures: evaluates cellular functional status

**Validation:** 5 single-cell datasets (cell lines + tumor patients).

## 3. What they found

- Beyondcell identifies tumor cell subpopulations with distinct drug responses
- Therapeutic clusters can be exploited to target malignant cells in both cell lines and tumor patients
- Switch point analysis distinguishes therapeutically-homogeneous vs heterogeneous tumors
- Specific case studies on melanoma (BRAF inhibitor resistance) and pancreatic cancer

## 4. What's strong

- **Genome Medicine open access (CC BY 4.0).** Highest tier of open licensing; BMC venue.
- **No training required.** Uses pre-computed drug signatures (PRISM, GDSC-derived, LINCS, etc.) — operationally lightweight.
- **Therapeutic Cluster concept is operationally useful.** Maps from "this cell responds to drug X" to "this cluster of cells should be targeted with drug X" — clinically actionable.
- **Switch Point analysis** quantifies tumor heterogeneity in a drug-specific way — original methodological contribution.
- **Compatible with existing drug signature databases** (LINCS, GDSC perturbation signatures) — leverages decades of prior pharmacological work.
- **No FM training required.** Operational simplicity.
- **Spanish CNIO institutional backing** — strong cancer research center.
- **Maintained on GitLab + Zenodo for reproducibility.**
- **Genuine cell-level resolution** for drug response prediction (vs scRank's cell-type-level).
- **Heterogeneity quantification** (Switch Point) is a unique contribution — neither DA-based nor GRN-based methods provide this.

## 5. What's limited

- **Depends on quality of drug signatures.** Garbage signatures → garbage BCS. **Critical dependence on external data quality.**
- **Cancer-only validation.** All five datasets are cancer; non-cancer disease applicability untested.
- **Drug perturbation signatures (PSC) are typically from cell line systems.** Transfer to patient context inherits cell-line-vs-patient gap that DA methods explicitly address. **Beyondcell sidesteps the bridge problem rather than solving it.**
- **No quantitative IC50 prediction.** Like scRank, output is rank order / score, not predicted drug efficacy in standard pharmacological units.
- **No mechanism trace to specific genes.** BCS aggregates signature enrichment — losing gene-level interpretability that scRank provides.
- **Pre-computed signatures may not match deployment scenario.** If a drug isn't in PSC/SSC, Beyondcell can't help (unless user provides signature).
- **No FM integration.** Signature-enrichment paradigm doesn't naturally combine with FM embeddings.
- **No cross-method benchmark vs SCAD/scDEAL/scAdaDrug published.** scRank cited Beyondcell as baseline but DA methods didn't directly compare.
- **Score interpretation can be subtle.** SP, BCS, TC concepts require user education; less plug-and-play than transfer learning frameworks.
- **Switch Point assumes binary up-down regulation.** Doesn't capture continuous response gradients.

## 6. INTERCEPTA implications

**For Q3:** Beyondcell adds the third paradigm — drug signature scoring. **The Q3 architectural landscape is now mapped:**

| Paradigm | Representative | Mechanism | Data requirement |
|---|---|---|---|
| **Domain Adaptation** | SCAD, scDEAL, scAdaDrug | Bulk + scRNA via DA | Requires bulk drug response labels |
| **GRN Perturbation** | scRank | In silico target perturbation in GRN | Requires drug target gene + scRNA |
| **Signature Enrichment** | Beyondcell | Score scRNA against pre-computed drug signatures | Requires drug signatures (LINCS/GDSC) |

**For Decision 1 layered architecture:** Beyondcell's drug signature scoring is the **same paradigm** as the "signature scoring" component already named in Charter §8.1. **This validates the architecture choice.** Beyondcell-style signature scoring is one of the four named layered components.

**For Charter §1.3 mechanistic interpretability:** Beyondcell's interpretability is at the signature level, not gene level. **Less granular than scRank.** For mechanism understanding, INTERCEPTA likely needs to combine Beyondcell-style scoring with scRank-style GRN perturbation.

**For Charter §1.1 universality:** Beyondcell requires drug signatures. For non-cancer diseases where signatures are sparse, **applicability is limited until LINCS/GDSC-equivalent databases exist.** This is a gap, not a Beyondcell-specific weakness.

**For multi-paradigm integration (INTERCEPTA novelty territory):**
- Beyondcell BCS as input feature to DA-based prediction
- Beyondcell signature enrichment + scRank GRN perturbation as orthogonal mechanism evidence
- Beyondcell + FM-derived drug signatures (using FM to compute drug signature from chemical structure) — unbenchmarked

**For Charter §7.1 compute reality:** Beyondcell is the **fastest Q3 method** read so far. No training; only signature enrichment computation. **For HPC-constrained deployments, Beyondcell is operationally trivial.**

## 7. Followup citations
1. **PRISM dataset** (Corsello 2020, Nat Cancer) — ~4500 drug × ~500 cell line pharmacogenomic database; Beyondcell signature source
2. **LINCS Connectivity Map** (Subramanian 2017 Cell) — drug perturbation signatures across cell lines
3. **Ben-David et al., 2018 Nature 560:325-330** — cell-line drug response variation; cited by Beyondcell
4. **Ho et al., 2018 Genome Res** — BRAF inhibitor resistance markers in melanoma scRNA-seq
5. **Suphavilai et al., 2021 (Genome Medicine, same collection as Beyondcell)** — alternative single-cell drug response method

## 8. Discipline check
- [x] All claims verified (Genome Medicine, BMC, ProQuest, ResearchGate, biorxiv preprint)
- [x] DOI verified across 5+ sources
- [x] Authors verified — Coral Fustero-Torre first; Fátima Al-Shahrour senior (CNIO Madrid)
- [x] Limitations include CSO-identified ones (dependency on signature quality, cancer-only, no FM integration)
- [x] **No new drift this cycle.**

— Claude (CSO), 2026-05-10
