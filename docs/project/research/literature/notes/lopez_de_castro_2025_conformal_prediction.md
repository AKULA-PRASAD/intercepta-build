# López-De-Castro et al., 2025 — Conformal inference for reliable single-cell RNA-seq annotation

## 0. Identification
- **Citation:** López-De-Castro M*, García-Galindo A*, González-Gomariz J, Armañanzas R. *Bioinformatics* 41(10):btaf521, October 2025 (Epub September 18, 2025). (* equal first-author contribution per PMC author contributions statement)
- **DOI:** 10.1093/bioinformatics/btaf521 ✓ (verified across Oxford Academic, PubMed PMID 40973204, PMC PMC12506889, ResearchGate, ovid.com, Universidad de Navarra portal científico)
- **Senior author:** Rubén Armañanzas (Conceptualization, Funding acquisition, Investigation, Methodology, Project administration, Resources, Supervision, Writing-review & editing per CRediT taxonomy)
- **Affiliations:** Institute of Data Science and Artificial Intelligence (DATAI), University of Navarra, Pamplona; TECNUN School of Engineering, University of Navarra, Donostia-San Sebastián; Cancer Center CCUN, Clínica Universidad de Navarra
- **License:** CC BY 4.0 (Open Access via Oxford University Press)
- **Code:** github.com/digital-medicine-research-group-UNAV/conformalized_single_cell_annotator + Zenodo DOI 10.5281/zenodo.15870599
- **Layer 1 question:** Q5 anchor 2 — statistical-guarantee OOD framework for scRNA-seq
- **Read by:** Claude (CSO) — 2026-05-10 (corrected — original 2026-05-10 note had fabricated "Khoshchehreh" attribution; this rewrite verified against primary source)

## 1. Why this paper

**Conformal prediction is the only OOD framework in Q5 with distribution-free statistical guarantees.** Theunissen 2025 benchmark (Q5 anchor 1) tested 6 methods — LogitNorm, MC Dropout, Deep Ensembles, Energy-based OOD, Deep NN, Posterior networks — but explicitly noted that **none provide statistical guarantees**. López-De-Castro et al. 2025 fills exactly that gap for scRNA-seq cell annotation, the most theoretically rigorous Q5 method available as of late 2025.

For INTERCEPTA's Charter §1.2 V1-V4 predictive validity claims, statistical guarantees on prediction sets are non-negotiable for clinical deployment. Conformal prediction is the framework that delivers them.

## 2. What they did

**Architecture (conformal prediction for cell annotation):**
1. **Base classifier** (any supervised model — model-agnostic framework)
2. **Calibration set:** held-out scRNA-seq data with known cell type labels
3. **Non-conformity measure:** scoring function quantifying how unusual a new cell is relative to calibration data
4. **Prediction sets:** for each query cell, return the set of cell type labels that cover the true label with confidence 1-α (typically α=0.05 or α=0.10)
5. **OOD detection:** cell types absent from the calibration reference → prediction sets become empty or contain all classes (signal for novelty/OOD)

**Evaluation:**
- 10 batched experiments derived from various tissues
- 3 annotation taxonomies tested:
  - **Standard** — direct cell-type label prediction
  - **Classwise** — class-conditional conformity scoring
  - **Cluster** — cluster-aware conformity
- 3 non-conformity measure variants tested per taxonomy
- Outcome metrics: anomaly detection performance for unseen cell types + prediction set coverage probabilities

## 3. What they found

- **Anomaly detector effectively identifies previously unseen cell types** across the 10 tissue datasets tested
- **Well-calibrated prediction sets** — coverage probabilities maintained at the expected significance level (i.e., 1-α coverage achieved as theory predicts)
- **Conformal prediction integration enhances downstream analyses** — prediction-set-based uncertainty propagates meaningfully through trajectory analysis, differential expression, etc.
- **Classwise and cluster-aware variants** outperform standard taxonomy in specific scenarios (paper provides experiment-specific guidance)

## 4. What's strong

- **Distribution-free statistical guarantees** — the strongest theoretical property among all Q5 methods. No assumption about underlying data distribution.
- **Model-agnostic.** Wraps around any base classifier (scANVI, MrVI, scGPT, any neural classifier).
- **Open Access CC BY 4.0** with code + Zenodo archive.
- **Three taxonomy variants tested** — methodological rigor; not one-size-fits-all.
- **10 tissue datasets** — broad evaluation; not single-tissue overfit.
- **University of Navarra Cancer Center collaboration** — bridges methodology development with translational context.
- **Calibration coverage maintained empirically** — verifies theory holds in practice on scRNA-seq.
- **Direct address of Theunissen 2025 benchmark's "no statistical guarantees" critique** — fills the field's exact methodological gap.

## 5. What's limited

- **Cell type annotation task, not drug response prediction.** Like every Q5 anchor read, the validation target is cell type identification — INTERCEPTA's actual deployment target (drug response) is not directly tested.
- **Marginal coverage guarantees, not conditional.** Standard conformal prediction guarantees the *average* coverage rate, not coverage *for any specific cell type or patient subgroup*. Pathologically, a model could achieve correct marginal coverage by being overconfident on common cell types and underconfident on rare ones.
- **Calibration set required.** Needs held-out labeled data. For cross-disease deployment (Charter U3), no labeled calibration set exists for held-out diseases — limits direct applicability for V6.
- **2025 publication; limited adoption track record yet.** Theoretically strong but few downstream applications to date.
- **Cancer-biased datasets** in evaluation (Cancer Center CCUN collaboration suggests cancer-context tissue selection).
- **Non-conformity measure choice is a hyperparameter** with significant impact — paper offers guidance but no universal optimum.
- **Computational overhead.** Conformal calibration requires storing calibration scores per class; for large multi-class problems (e.g., hundreds of cell types) overhead grows.

## 6. INTERCEPTA implications

**For Q5 architecture (Decision 5):** Conformal prediction provides the **statistical-guarantee layer** on top of base uncertainty methods. Specifically:
- Base layer: VAE posterior uncertainty (scANVI/MrVI from Decision 2; CPA from Decision 4)
- Middle layer: Deep Ensembles N=5 for epistemic uncertainty (per Decision 5 stack)
- Top layer: **Conformal prediction for distribution-free coverage guarantees**

This is the principled Q5 closure: conformal prediction is the only method providing the guarantees Charter §1.3 falsifiability requires for drug response prediction sets.

**For Charter §1.2 V1-V4 (predictive validity):** Prediction sets with coverage guarantees mean:
- V1-V4 reporting includes coverage probabilities, not just point AUROC
- Calibration of uncertainty is itself testable against held-out data
- Reviewer "is this prediction trustworthy?" answerable quantitatively

**For Charter §1.1 universality (U3 cross-disease):** Limitation — conformal calibration on cancer-trained models will not transfer well to held-out diseases without disease-specific calibration sets. **This is a real architectural challenge for INTERCEPTA's V6 evaluation.** Two paths:
- (a) Cross-disease conformal recalibration when small labeled samples of the new disease become available
- (b) Conditional conformal prediction methods (more sophisticated; less well-validated)

**For Decision 5 PROPOSED:** The original Decision 5 stack ordering is correct (VAE posterior → ensembles → conformal → energy-based). This rewrite reaffirms the architectural commitment with verified primary-source grounding.

## 7. Followup citations
1. **Vovk, Gammerman, Shafer 2005** — foundational conformal prediction textbook ("Algorithmic Learning in a Random World")
2. **Theunissen et al. 2025** (Q5 anchor 1) — companion benchmark of non-conformal OOD methods
3. **Conditional conformal prediction methods** (Lei et al., Romano et al.) — for class-conditional coverage guarantees
4. **Engelmann et al. 2022** (Q5 anchor 4) — atlas-level uncertainty alternative

## 8. Discipline check
- [x] **All claims verified primary-source** this time: Oxford Bioinformatics, PubMed, PMC, ResearchGate, Universidad de Navarra portal científico, ovid.com
- [x] DOI verified across 6+ independent sources
- [x] Authors verified — all four names confirmed across multiple sources; first-author equal contribution confirmed
- [x] Senior author identified via CRediT taxonomy in PMC author contributions
- [x] Affiliations verified (DATAI Univ Navarra + TECNUN + Cancer Center CCUN)
- [x] License verified (CC BY 4.0)
- [x] PMID + PMC + DOI + journal volume/issue all cross-confirmed
- [x] **Errata note:** original 2026-05-10 file fabricated "Khoshchehreh" attribution. This rewrite corrects to verified primary-source authorship. Logged as Drift Instance #25 in audit; corrected here.

— Claude (CSO), 2026-05-10 (corrected pass)
