# Cover letter

Dear Editors,

Please consider our manuscript, **"A reproducible cell-line–derived transcriptomic drug-response engine: where
transfer works, where it doesn't, and two decisive replication nulls (clinical and functional),"** for publication.

Transcriptomic prediction of cancer drug response is a crowded field dominated by positive reports, yet its
reproducibility and honest scope are inconsistent: cross-dataset leakage inflates estimates, parameter-free
baselines are rarely beaten, multiple testing is often uncorrected, and the leap from cell lines to patients is
asserted more than demonstrated. We took the opposite stance — loyalty to the evidence over the hypothesis — and
built a drug-response engine under a fixed, pre-registered, falsify-first protocol: every positive is presumed
false until it survives permutation nulls, leakage-corrected splits, multiple-testing correction, confound
adjustment, and external replication; every well-powered null is a first-class result; and every analysis
reproduces twice.

The result is a graded, honest map of the modality:

- A leakage-corrected cell-line→cell-line map transfers at mean per-drug ρ = +0.212 and this is a firm **ceiling**
  (proliferation and 50 driver mutations add nothing); the naive leaky estimate of +0.278 overstates it by a third.
- In 1,079 patients (TCGA), the engine's apparent clinical-response signal is **entirely cancer-type confounding**
  (within-cancer AUROC 0.504, p=0.43).
- Most instructively, a functional-inference layer that beat the standard FLT3-ITD biomarker in one leukemia cohort
  — proliferation-, mutation-, and lineage-independent, and target-specific — **failed independent replication** in
  a second cohort, even though the known biology replicated cleanly.

We believe the contribution is precisely what the field under-produces: a rigorously bounded, fully reproducible
account of where a widely-pursued approach genuinely works and where it does not, including two decisive negatives
and a released, tested engine. The recurring, generalizable lesson — signals that recover *known* biology replicate
across cohorts, whereas novel single-cohort refinements often do not survive independent replication — is directly
useful to anyone building or reviewing drug-response predictors, and it motivates a concrete path forward
(prospective functional-precision cohorts) rather than further observational modeling against the same ceiling.

**Rigor and transparency.** All code, pre-registrations (written before results), per-experiment metrics, an
evidence ledger, an integrity record, and the figure-generation script are public. Every figure regenerates from
committed metrics; every result reproduces twice with byte-identical output. Inputs are public except BeatAML
(dbGaP controlled-access), which we do not redistribute.

This work has not been published elsewhere and is not under consideration by another journal. We declare no
competing interests. We suggest the manuscript is well suited to a venue that values methodological rigor,
reproducibility, and the publication of well-powered negative results.

Thank you for your consideration.

Sincerely,
Prasad Akula (on behalf of the authors)
akula.pra@northeastern.edu

---
*Suggested journals (rigorous-negative / reproducibility fit): PLOS Computational Biology; eLife; Cell Reports
Methods; GigaScience; Bioinformatics. Suggested and opposed reviewers to be added at submission.*
