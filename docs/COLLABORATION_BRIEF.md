# INTERCEPTA — collaboration & funding brief
### A rigor-first program to break the baseline-transcriptomic ceiling in cancer drug-response prediction

**One line.** We have built and openly released a fully pre-registered, leakage- and confound-controlled engine
for transcriptomic drug-response prediction; it delivered an honest, decisive result — *baseline* transcriptomics
predicts cancer type and proliferation, **not** drug-specific clinical response — and we now seek a
functional-precision-oncology partner to generate the perturbation-based data that can actually break that
ceiling, with the analysis layer already validated and ready.

---

## 1. The problem, and the gap we proved
Transcriptomic prediction of drug response is a crowded field dominated by positive reports, but reproducibility
and honest scope are inconsistent: cross-dataset leakage inflates estimates, parameter-free baselines are rarely
beaten, and the leap from cell lines to patients is asserted more than demonstrated. Under a fixed protocol
(pre-registration; permutation nulls; leakage-corrected splits; BH-FDR; **within-cancer confound control**;
external and cross-system replication; every result reproduced twice), we quantified exactly where the approach
works and where it fails:

- **Cell lines:** a leakage-free cross-dataset map transfers (mean per-drug ρ = +0.212) — but this is a **ceiling**:
  adding a proliferation axis or 50 driver-mutation features does not beat it.
- **A second modality doesn't help:** matched mass-spec **proteomics** (CCLE, 291 lines, 271 drugs) does **not**
  beat or add to RNA (protein ρ=0.33 vs RNA 0.42) — the ceiling is a property of *baseline profiling itself*, not
  of one assay.
- **Human clinical (TCGA, 12 drugs, 1,079 patients):** the apparent association with response is **entirely
  cancer-type confounding** — within-cancer AUROC = 0.504 (p=0.43): a **well-powered null.**
- **Even an *inferred* functional layer fails to generalize:** inferring CRISPR gene-dependency from expression
  beat the standard FLT3-ITD biomarker *within* one AML cohort (BeatAML) — proliferation-, mutation-, and
  lineage-independent — but **did not replicate** in an independent cohort (FIMM/Malani); the known biology
  replicated, our inferred refinement did not.

**The decisive insight (now proven from five directions):** what transfers is proliferation and cancer type, not
drug-specific vulnerability; no *baseline* molecular profile (RNA or protein) closes the gap; and a functional
layer *inferred from cell lines* does not transfer between patient cohorts. The way forward is therefore not a
better model or another omic — it is **measuring functional/perturbation response in the patients themselves.**
This is the result the field needs and rarely publishes, and it defines the study below.

## 2. The way forward — and why it needs new data, not new code
If baseline expression mostly encodes lineage and growth, then drug-specific signal must come from **functional
/ perturbation** readouts — how a tumor's cells actually respond when challenged. Our only real drug-specific
signals (ex-vivo BeatAML, and the within-cohort dependency layer) both came from *functional* data — and the one
time we tried to *infer* that functional layer from baseline cell-line data, it did not transfer between cohorts.
The lesson is precise: **functional response must be measured in the patient, not inferred.** We therefore propose
to generate and analyze a **prospective functional-precision cohort**, with our validated, reproducible engine as
the ready analysis layer.

## 3. Proposed study (Track 1)
- **Design.** ≥300 patients, one or two tumor types (AML first — the assay ecosystem exists; then a solid tumor
  via patient-derived organoids/PDX). For each: **ex-vivo per-drug response (AUC)** on the patient's own tumor
  cells across a panel overlapping public cell-line screens; matched **tumor RNA-seq + WES**; and, where feasible,
  ≥12-month clinical follow-up.
- **Pre-registered analyses (protocols frozen before data; `prereg/` templates ready).**
  (a) Replicate the ex-vivo drug-specific transfer at powered n (target: ρ and drug-specificity that clear
  permutation + within-cancer control — the tests our public data was underpowered for).
  (b) The novel step: test whether **measured ex-vivo response predicts clinical outcome**, closing the
  ex-vivo→clinic gap that observational data cannot — with **treatment-timed** analysis (avoiding the immortal-time
  bias that made retrospective survival tests uninterpretable).
  (c) A built-in discriminating test: confirm that the **measured** functional readout outperforms the
  **inferred-from-baseline** layer that failed to transfer between cohorts — turning our sharpest negative into a
  design principle.
- **Success / falsification (set in advance).** Success = drug-specific transfer replicates *and* ex-vivo→clinical
  concordance is significant under confound control. Falsification = if, at n≥300, drug-specificity is again
  ρ≈0.07 and does not beat proliferation, the transcriptomic-transfer thesis is formally bounded and we pivot to
  perturbation-screen mechanism discovery (Track 2). **Either outcome is a publishable, field-moving result** —
  the design cannot produce an uninformative answer.

## 4. What is already built and de-risked (open, reproducible)
- A validated, **pip-installable engine** (`intercepta`) + CLI + a passing unit-test suite; trains on public
  GDSC/PRISM/DepMap and applies to any query cohort with one loader.
- The **full falsification battery as reusable code** (permutation, leakage, BH-FDR, within-cancer confound
  control, cross-system + external-cohort replication) — a new cohort's analysis runs unchanged and reproducibly.
- A **functional-inference layer** (expression→CRISPR-dependency) already built and tested — including the
  external-replication protocol that produced our sharpest negative, now reusable to validate the measured
  functional readouts prospectively.
- A **transparent evidence ledger** (verified results *and* first-class negatives) and an integrity record; all
  public at `github.com/AKULA-PRASAD/intercepta-build` (v0.1.0), MIT-licensed, no patient data committed.
- A **secondary deliverable of independent value:** the pre-registered, leakage/confound-controlled protocols
  constitute a **reproducible benchmark** the field currently lacks.

## 5. Why this partnership
The bottleneck is **data, not analysis** — and the analysis layer that most groups still have to build is done,
validated, and open. A functional-precision or clinical partner contributes the one irreplaceable asset (samples,
ex-vivo screening capacity, clinical linkage); we contribute a uniquely rigorous, ready, reproducible analytical
engine and an integrity-first culture that makes any result — positive or null — trustworthy and publishable.

## 6. What we are asking for
Either (a) a **collaboration** with a lab/clinic that has functional-precision (ex-vivo/organoid/PDX) capacity and
tumor-molecular profiling, or (b) **funding** to commission it. In return: co-development of the frozen protocols,
open analysis, shared authorship, and an honest, high-integrity result.

## 7. Honest risk statement
Our best *inferred* signals are weak or cohort-specific (baseline transfer ρ≈0.07; the functional-inference layer
did not externally replicate); the prospective cohort — measuring function directly, in patients — is powered to
determine whether the *measured* functional readout is real-and-usable at the clinical endpoint or intrinsically
bounded. We make **no** claim of a validated clinical predictor today (we proved the opposite across five fronts),
and we will not overclaim tomorrow. The value proposition is rigor and a decisive, pre-registered answer — not a
promised miracle. That integrity — a platform whose every positive survived falsification and whose two headline
negatives are reported openly — is precisely what makes a genuine breakthrough, if it exists here, believable.

*Contact: Prasad Akula. Full methods, code, pre-registrations, and evidence ledger: github.com/AKULA-PRASAD/intercepta-build (v0.1.0).*
