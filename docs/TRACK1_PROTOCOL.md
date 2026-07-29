# Track-1 study protocol — prospective functional-precision cohort to test drug-specific transcriptomic transfer
**Version 1.0 (2026-07-29). Status: pre-registration draft (frozen analysis plan; to be locked before data).**
Companion to `docs/BREAKTHROUGH_ROADMAP.md`, `docs/COLLABORATION_BRIEF.md`. Power calc: real Monte-Carlo
simulation, `experiments/track1_power/` (reproduced ×2).

## 1. Background & rationale (earned from our own evidence)
On public/ex-vivo data (LEDGER B1–B11) we proved: baseline transcriptomics transfers **proliferation and
cancer-type**, not drug-specific vulnerability; human clinical prediction is a **cancer-confounded null** (B10,
within-cancer AUROC 0.504); the only genuine drug-specific signal is **weak (ρ≈0.07) and functional** (BeatAML
ex-vivo, V9), replicated across screens but underpowered externally. The ceiling on baseline-expression prediction
is therefore intrinsic; the way to test drug-level prediction is a **prospective functional (ex-vivo) cohort**,
powered, with confound control built in. This protocol specifies that study.

## 2. Objectives
- **Aim 1 (primary).** Determine whether the cell-line-trained transfer predicts **per-drug ex-vivo response** in
  fresh patient tumors with genuine **drug-specificity** (beyond proliferation/cancer-type), at adequate power.
- **Aim 2 (key secondary).** Determine whether ex-vivo response (and the engine score) predicts **clinical
  outcome** (response/PFS) — the ex-vivo→clinic link observational data cannot establish.
- **Aim 3 (exploratory).** Confirmatory/discovery mutation→drug and expression-signature analyses (BH-controlled).

## 3. Design
Prospective, observational, functional-precision cohort. Tumor type **1: AML** (mature ex-vivo drug-screen
ecosystem; extends BeatAML/V9). Tumor type **2 (optional, phase 2): a solid tumor** via patient-derived organoids
or PDX. Per patient at diagnosis/relapse: viable tumor cells → standardized **ex-vivo drug-response assay**;
matched **tumor RNA-seq + WES**; prospective clinical follow-up.

## 4. Population & sample size
- Inclusion: confirmed diagnosis, adequate viable tumor material for the ex-vivo panel + sequencing, consent.
- **Target N = 200 (minimum 150) evaluable patients per tumor type**, drug panel **K ≥ 20** agents overlapping
  public GDSC/PRISM (so the cell-line transfer model exists for each). Rationale = the power calc (§8).

## 5. Assays & data
- **Ex-vivo drug response:** standardized viability assay (e.g., 72–96 h), ≥7-point dose, per-drug **AUC/IC50**;
  ≥20-drug panel spanning targeted + cytotoxic classes present in GDSC/PRISM (e.g. MEK/PI3K/FLT3/BCL2/CDK
  inhibitors + standard chemo). QC: replicate wells, positive/negative controls, viability thresholds.
- **Tumor RNA-seq** (bulk; gene-symbol quantification) and **WES** (somatic variants).
- **Clinical:** regimen, RECIST/response, PFS/OS, key covariates (age, stage, prior lines).

## 6. Endpoints
- Primary (Aim 1): per-drug ex-vivo AUC; the drug-specificity contrast (diagonal vs off-diagonal, prolif-residualized).
- Secondary (Aim 2): clinical responder/non-responder and PFS.

## 7. Statistical analysis plan (FROZEN before data; blind to outcomes)
The engine (`intercepta`, v0.1.0, trained on public DepMap+GDSC/PRISM) is applied to each patient's RNA-seq to
produce per-drug transfer predictions — **no fitting on the new cohort** (pure external test).
- **Aim 1 test (identical to B3b/B7/B9):** per drug, Spearman(transfer prediction, ex-vivo AUC). Residualize both
  on R_prolif. Primary statistic = mean **diagonal** ρ minus mean **off-diagonal** ρ (drug-specificity beyond a
  generic axis), permutation p (k=2000). Confirmatory: raw pooled diagonal ρ; per-drug BH-FDR. Reproduce ×2.
- **Aim 2 test:** does the engine's per-drug score / ex-vivo AUC predict clinical response? Logistic (responder ~
  score + cancer-type + proliferation) and Cox (PFS); **within-cancer stratified** (the B10 confound control);
  permutation + BH. 
- Everything pre-registered; deterministic; provenance-stamped metrics; controlled data never leaves the secure
  environment (§10).

## 8. Power calculation (real Monte-Carlo of the exact Aim-1 test; `experiments/track1_power/`)
Simulated the pre-registered proliferation-residualized diagonal−off-diagonal specificity test with permutation,
under the observed effect range. Power vs cohort size N and panel size K:

| K (drugs) | true ρ | N=50 | N=75 | N=100 | N=150 | N=200 | N=300 |
|---|---|---|---|---|---|---|---|
| 20 | 0.05 | 0.45 | 0.59 | 0.70 | **0.84** | 0.91 | 0.97 |
| 20 | 0.07 | 0.68 | **0.85** | 0.91 | 0.98 | 0.99 | 1.00 |
| 20 | 0.10 | **0.90** | 0.98 | 0.99 | 1.00 | 1.00 | 1.00 |
| 12 | 0.07 | 0.49 | 0.57 | 0.76 | **0.84** | 0.94 | 1.00 |

**Smallest N for ≥80% power (K=20):** ρ=0.10→N=50; ρ=0.07→N=75; ρ=0.05→N=150.
**Recommendation: N=200 with K≥20 gives >90% power across the plausible effect range (ρ=0.05–0.10)**; N=150 is the
minimum (≥84% at the conservative ρ=0.05). Pooling across ≥20 drugs is what makes even a weak per-drug effect
detectable. *(Planning caveat: gaussian, true-proliferation-residualized; real power is somewhat lower with
imperfect proliferation estimation and drug-drug correlation — hence the 200 target, not 75.)*
**Aim 2 (clinical):** N=150–200 with ~40% response is powered (≈80%) to detect an engine→response AUROC ≥ 0.66
(standard AUROC power); underpowered below that — reported honestly if so.

## 9. Success & falsification (set in advance)
- **Aim 1 success:** diagonal−off-diagonal specificity > 0, permutation p<0.05 (replicates V9 at power).
  **Falsification:** at N≥150, K≥20, specificity not significant and diagonal does not beat proliferation → the
  transcriptomic-transfer thesis is formally bounded; pivot to Track 2 (perturbation mechanism).
- **Aim 2 success:** engine/ex-vivo score predicts clinical outcome under within-cancer control, p<0.05.
- **Either outcome is publishable and field-moving.** The design cannot yield an uninformative result.

## 10. Data governance & ethics
IRB/ethics approval and informed consent required. Patient-level molecular/clinical data are **controlled** and
remain on the partner's secure environment; only aggregate, de-identified metrics leave it. **No patient data is
ever committed to the public repository** (policy: `data/MANIFEST.md`, `INTEGRITY_SWEEP.md`). Analysis code is open.

## 11. Analysis readiness
The engine, the full falsification battery (permutation, leakage, BH-FDR, within-cancer control, cross-system
replication), and frozen pre-registration templates are built, validated, tested, and released (v0.1.0). A new
cohort requires only a data loader; analyses run unchanged and reproducibly.

## 12. Roles, timeline, milestones
- **Partner:** samples, ex-vivo screening, sequencing, clinical linkage, ethics. **Us:** frozen protocol,
  blinded analysis, reproducible pipeline, reporting. Shared authorship.
- **Timeline (indicative):** M0–3 protocol lock + ethics + assay QC; M3–15 accrual + profiling (N=150–200);
  M15–18 locked analysis (Aim 1/2); M18–24 clinical follow-up maturation + manuscript. Solid-tumor arm phase 2.

## 13. Honest limitations
Our prior drug-specific effect is weak (ρ≈0.07); this study is powered to determine whether it is real-and-usable
or intrinsically bounded — not to guarantee a positive. We make no clinical-utility claim in advance. The value
is a decisive, pre-registered, confound-controlled answer with a validated analysis layer.
