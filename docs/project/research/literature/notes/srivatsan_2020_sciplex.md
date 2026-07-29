# Srivatsan et al., 2020 — Massively multiplex chemical transcriptomics at single-cell resolution (sci-Plex)

## 0. Identification
- **Citation:** Srivatsan SR*, McFaline-Figueroa JL*, Ramani V*, Saunders L, Cao J, Packer J, Pliner HA, Jackson DL, Daza RM, Christiansen L, Zhang F, Steemers F, Shendure J†, Trapnell C†. *Science* 367(6473):45-51, 2020. (* equal first; † co-corresponding)
- **DOI:** 10.1126/science.aax6234 ✓ (verified Science.org, PMC7289078, multiple labs)
- **Senior authors:** Jay Shendure + Cole Trapnell (University of Washington Genome Sciences)
- **Layer 1 question:** Q4 anchor 3 — **multiplexed scRNA-seq drug perturbation data resource + method**
- **Read by:** Claude (CSO) — 2026-05-10

## 1. Why this paper

sci-Plex is **THE landmark paper for scRNA-seq drug perturbation profiling**. It establishes the experimental method (nuclear hashing) AND produces a public dataset (~650K cells × 188 compounds × 3 cancer cell lines × ~5000 conditions). For Q4 architecture, sci-Plex defines what "drug response at single-cell resolution" data looks like operationally.

## 2. What they did

**Method: sci-Plex**
- **Nuclear hashing:** oligonucleotide-tagged antibodies labeling nuclei from different experimental conditions
- **Combinatorial indexing scRNA-seq (sci-RNA-seq3):** scales to many conditions in single experiment
- **One experiment captures gene expression profiles from thousands of independent samples** — orders of magnitude more efficient than separate-experiment scRNA-seq

**Pilot proof-of-concept:**
- **3 cancer cell lines** (A549 lung adenocarcinoma + 2 others)
- **188 compounds** (chemical screen)
- **~5,000 independent samples** (cell line × compound × dose × time)
- **~650,000 single cells profiled** in one experiment

**Specific drugs in initial pilot (Fig 2A):** BMS345541, dexamethasone, nutlin-3a, SAHA (HDAC inhibitor) — diverse mechanisms tested.

## 3. What they found

- sci-Plex captures **substantial intercellular heterogeneity in response to specific compounds**
- **Commonalities in response across compound families** (e.g., all HDAC inhibitors share certain transcriptional signatures)
- **Differential properties within compound families** discriminable
- **HDAC inhibitor results support view that chromatin acts as acetate reservoir in cancer cells** — biological insight beyond methodology
- Method scales: ~650K cells × ~5K samples per experiment is achievable

## 4. What's strong

- **Publication in Science** — top venue.
- **Massive scale** (~650K cells) at low cost — defines economic feasibility for scRNA-seq drug screens.
- **Public dataset.** sci-Plex data is a reference benchmark for INTERCEPTA-like methods.
- **Single-cell heterogeneity in drug response is empirically quantified** — supports motivation for scRNA-seq drug response prediction over bulk.
- **Method is now widely adopted.** Many subsequent papers use sci-Plex data.
- **UW Genome Sciences institutional backing** (Shendure + Trapnell labs).
- **Three equal first authors documented.**
- **Companion sci-Plex-GxE (2023)** extends to gene-by-environment interactions.
- **Uses combinatorial indexing** — scalable infrastructure.
- **Diverse compound families tested** (kinase inhibitors, GR agonists, p53 activators, HDAC inhibitors, etc.) — operationally diverse drug classes.

## 5. What's limited

- **3 cancer cell lines only.** Three cell lines is small for cross-cell-line generalization.
- **Cancer-only.** Same fundamental gap.
- **In vitro 2D culture.** Not in vivo, not patient context.
- **Drug doses not extensively varied per compound.** Limited dose-response analysis.
- **scRNA-seq dropout still present** — sci-Plex doesn't solve dropout, just enables multiplexing.
- **188 compounds is broad but selective.** Not full GDSC/PRISM coverage.
- **A method paper, not a prediction architecture.** sci-Plex is the data-generation tool; prediction methods (CPA, scGen, etc.) use sci-Plex data.
- **No clinical validation.** Results are cell-line-only.
- **Dataset biased toward cancer-relevant compound families.** May underrepresent non-oncology drug mechanisms.
- **Custom Illumina transposase complexes required** — not trivially reproducible without Illumina partnership.

## 6. INTERCEPTA implications

**For Q4:** sci-Plex provides the **gold-standard public benchmark dataset** for scRNA-seq drug response prediction. **INTERCEPTA's Q4 architecture should be benchmarked against sci-Plex data**, alongside any non-cancer extensions.

**For Decision 4 PROPOSED:** sci-Plex defines what "perturbation prediction at single-cell resolution" means operationally:
- Input: cell expression profile + compound identity (+ dose, optionally)
- Output: predicted post-perturbation expression profile
- Validation: hold-out compounds, hold-out cell lines, hold-out doses

**For Charter §1.2 V1-V4 predictive validity:** sci-Plex enables hold-out validation:
- V1 (cross-cell-line): train on 2 cell lines, predict on 3rd
- V2 (cross-compound): train on subset of 188 compounds, predict on held-out
- V3 (cross-family): train on kinase inhibitors, predict on HDAC inhibitors

**For Charter §1.1 universality:** sci-Plex's cancer-only limitation means non-cancer perturbation benchmarks are needed. **This is a gap in the field, not just sci-Plex.**

**For novelty:** Most published methods (CPA, scGen, sams-VAE) use sci-Plex data. INTERCEPTA's contribution would be:
- FM-based architectures benchmarked on sci-Plex (replacing handcrafted encoders)
- Cross-disease extension (sci-Plex-equivalent in non-cancer context)
- Mechanism trace (which cells respond, why) at sci-Plex scale

## 7. Followup citations
1. **CPA — Compositional Perturbation Autoencoder** (Lotfollahi 2023 Mol Syst Biol) — uses sci-Plex
2. **scGen** (Lotfollahi 2019 Nat Methods) — perturbation prediction in latent space
3. **sams-VAE** (Bereket 2024) — Bayesian extension
4. **sci-Plex-GxE** (McFaline-Figueroa 2023 biorxiv) — gene-environment combined
5. **PRISM** (Corsello 2020 Nat Cancer) — alternative high-throughput drug screen at bulk level

## 8. Discipline check
- [x] All claims verified (Science, PMC, lab sites)
- [x] DOI verified across 5+ sources
- [x] Authors verified — Srivatsan/McFaline-Figueroa/Ramani equal first; Shendure + Trapnell senior
- [x] Honest reporting that sci-Plex is data-generation tool, not prediction method
- [x] **No new drift this cycle.**

— Claude (CSO), 2026-05-10
