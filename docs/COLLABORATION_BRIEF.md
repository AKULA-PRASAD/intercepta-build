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
- **Ex-vivo (AML, BeatAML):** a *weak but genuine* drug-specific, proliferation-independent signal (ρ≈0.07)
  replicates across independent training screens.
- **Human clinical (TCGA, 12 drugs, 1,079 patients):** the apparent association with response is **entirely
  cancer-type confounding** — within-cancer AUROC = 0.504 (p=0.43): a **well-powered null.**

**The decisive insight:** what transfers is proliferation and cancer type, not drug-specific vulnerability. The
ceiling on *baseline*-expression drug prediction is therefore **intrinsic to the data modality, not a modeling
deficiency** — no algorithm closes it. This is the result the field needs and rarely publishes, and it defines
the way forward.

## 2. The way forward — and why it needs new data, not new code
If baseline expression mostly encodes lineage and growth, then drug-specific signal must come from **functional
/ perturbation** readouts — how a tumor's cells actually respond when challenged. Our only real drug-specific
signal (ex-vivo BeatAML) already came from a functional assay. We therefore propose to generate and analyze a
**prospective functional-precision cohort**, with our validated, reproducible engine as the ready analysis layer.

## 3. Proposed study (Track 1)
- **Design.** ≥300 patients, one or two tumor types (AML first — the assay ecosystem exists; then a solid tumor
  via patient-derived organoids/PDX). For each: **ex-vivo per-drug response (AUC)** on the patient's own tumor
  cells across a panel overlapping public cell-line screens; matched **tumor RNA-seq + WES**; and, where feasible,
  ≥12-month clinical follow-up.
- **Pre-registered analyses (protocols frozen before data; `prereg/` templates ready).**
  (a) Replicate the ex-vivo drug-specific transfer at powered n (target: ρ and drug-specificity that clear
  permutation + within-cancer control — the tests our public data was underpowered for).
  (b) The novel step: test whether **ex-vivo response predicts clinical outcome**, closing the ex-vivo→clinic gap
  that observational data cannot.
- **Success / falsification (set in advance).** Success = drug-specific transfer replicates *and* ex-vivo→clinical
  concordance is significant under confound control. Falsification = if, at n≥300, drug-specificity is again
  ρ≈0.07 and does not beat proliferation, the transcriptomic-transfer thesis is formally bounded and we pivot to
  perturbation-screen mechanism discovery (Track 2). **Either outcome is a publishable, field-moving result** —
  the design cannot produce an uninformative answer.

## 4. What is already built and de-risked (open, reproducible)
- A validated, **pip-installable engine** (`intercepta`) + CLI + a passing unit-test suite; trains on public
  GDSC/PRISM/DepMap and applies to any query cohort with one loader.
- The **full falsification battery as reusable code** (permutation, leakage, BH-FDR, within-cancer confound
  control, cross-system replication) — a new cohort's analysis runs unchanged and reproducibly.
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
Our best drug-specific signal is weak (ρ≈0.07); the prospective cohort is powered to determine whether it is
real-and-usable or intrinsically bounded. We make **no** claim of a validated clinical predictor today (we proved
the opposite), and we will not overclaim tomorrow. The value proposition is rigor and a decisive, pre-registered
answer — not a promised miracle. That integrity is precisely what makes a genuine breakthrough, if it exists here,
believable.

*Contact: Prasad Akula. Full methods, code, pre-registrations, and evidence ledger: github.com/AKULA-PRASAD/intercepta-build (v0.1.0).*
