# A reproducible cell-line–derived transcriptomic drug-response engine: where transfer works, where it doesn't, and an honest human-validation null

**INTERCEPTA build.** Draft manuscript v1 (2026-07-29). Every quantitative claim traces to a committed,
reproduced-×2 metrics file in `experiments/`, `verification/`, and `LEDGER.md` of
`github.com/AKULA-PRASAD/intercepta-build`. Analyses are pre-registered (`prereg/`).

---

## Abstract

Transcriptomic prediction of cancer drug response is widely pursued but its true reach is often obscured by
leakage, weak baselines, and unadjusted confounding. We built a reproducible engine and subjected every claim to
pre-registration, permutation nulls, leakage-corrected splits, multiple-testing correction, and external
replication. We report a graded, honest result. (1) A learned per-drug expression→response map transfers across
independent cell-line datasets (GDSC→CCLE/PRISM) with a leakage-free mean per-drug Spearman ρ = **+0.212**
(94/100 drugs positive; vs a parameter-free proliferation baseline +0.058; Wilcoxon p=1.9×10⁻¹⁵), and this
+0.212 is a genuine **ceiling** — adding a proliferation axis or 50 driver-mutation features does not beat it.
(2) Verified somatic mutation→drug associations exist in acute myeloid leukemia (AML; BeatAML), dominated
genome-wide by **FLT3-ITD→FLT3 inhibitors** and **RAS→MEK inhibitors**; two hand-picked pairs (NPM1→cabozantinib,
DNMT3A→dasatinib) do **not** survive genome-wide correction. (3) A weak but drug-specific, proliferation-
independent cell-line→patient signal is detectable in BeatAML ex-vivo response and replicates across two
independent training screens; combining it with mutation markers beats either alone. (4) Out-of-distribution
distance is a validated confidence signal; per-drug cell-line reliability is not. (5) **Crucially, in real human
patients (TCGA, 12 drugs, 1,079 patients), the engine's apparent association with clinical response is entirely
cancer-type confounding: within-cancer AUROC = 0.504 (p=0.43, null).** We conclude that transcriptomic transfer
is a real but weak tool at the cell-line/ex-vivo level and is **not** a validated human clinical predictor on
available observational data. We release the engine, all pre-registrations, and all negative results. Finally, reframing from baseline to **functional** readouts, we show an expression-inferred gene-dependency layer that identifies FLT3-inhibitor-sensitive AML **beyond FLT3-ITD mutation status** (including in ITD-wildtype patients; ex-vivo, p=1.5e-15) — a mechanistically-coherent, patient-translatable lead.

---

## 1. Introduction

Predicting which drug will help which tumor from transcriptomics is a central promise of computational oncology.
The literature is dominated by positive reports, yet reproducibility and honest scope are inconsistent: cross-
dataset leakage inflates estimates, parameter-free baselines are rarely beaten, multiple testing is often
uncorrected, and the jump from cell lines to patients is asserted more than shown. We took the opposite stance —
loyalty to the evidence over the hypothesis — and built the engine under a fixed protocol: assume every positive
false until it survives permutation, leakage audit, multiple-testing (BH-FDR), confound adjustment, and external
replication; treat well-powered nulls as first-class; and reproduce every result twice. This paper reports what
survived and, equally, what did not.

## 2. Results

### 2.1 A learned expression→response map transfers cross-dataset and defines a ceiling
Training per-drug ridge regressions on GDSC2 cell-line expression and evaluating on CCLE/PRISM with **disjoint
cell lines** (strict leakage correction), the mean per-drug Spearman ρ = **+0.212** (median +0.196; 94/100 drugs
positive), significantly above a frozen parameter-free proliferation axis (R_prolif, +0.058; paired Wilcoxon
W=214, p=1.93×10⁻¹⁵). The leaky design (test lines present in training) inflated this to +0.278, quantifying the
leakage that naive pipelines incur. Adding R_prolif or 50 recurrently-mutated driver-gene features as covariates
did **not** improve on transcriptome-only (Δρ=+0.0000, p=0.98; Δρ=+0.0004, BH-q=0.74): **+0.212 is the public
cell-line ceiling** for this design (B1, B2).

### 2.2 Verified mutation→drug mechanism in AML, and what does not survive correction
In BeatAML ex-vivo drug screening, a systematic screen of 3,051 gene×drug pairs (BH-FDR<0.05, FLT3-ITD– and
proliferation-adjusted, split-half direction-replicated) yielded **177 robust markers**, dominated by the
textbook actionable axis **FLT3-ITD→FLT3 inhibitors** (e.g. sorafenib BH-q=4×10⁻²⁶) and **RAS(KRAS/NRAS)→MEK
inhibitors** (B5). Two associations we had initially highlighted from pairwise tests — NPM1→cabozantinib and
DNMT3A→dasatinib — do **not** survive genome-wide correction once FLT3-ITD is accounted for (cabozantinib
sensitivity is largely the co-occurring FLT3-ITD). We report this as a refinement, not a result (B5; LEDGER
V4/V6 refinement).

### 2.3 A weak, drug-specific cell-line→patient signal in AML ex-vivo response
Applying the cell-line map to BeatAML patient tumors, a raw signal transfers (diagonal ρ=+0.054, permutation
p=5×10⁻⁴) but is not drug-specific on a mismatched microarray→RNA-seq platform (B3). On a matched RNA-seq
platform (DepMap→BeatAML) with proliferation residualized, a **weak but drug-specific** signal emerges
(diagonal−off-diagonal = +0.040, p=0.010) and **replicates with an independent training screen** (GDSC1 labels:
+0.051, p=0.0015, 59 drugs), robust to drug jackknife, bootstrap, and patient split-half (B3b–B3d). This
signal is **not** explained by the pre-declared AML driver-signaling pathways (B3e, null) — it is real but
mechanistically unexplained and small (ρ≈0.07–0.08).

### 2.4 Combining mechanism and transfer beats either alone
For verified drug–marker pairs, a model combining the mutation marker with the expression-transfer prediction
achieves higher cross-validated concordance with patient ex-vivo response than either component alone in all 4
testable pairs (B4); a shipped engine (`InterceptaEngine`) embodying this combination reproduces the effect
(3/3 genome-wide-robust pairs, B4/engine validation). Combination is complementary, not redundant.

### 2.5 Confidence: out-of-distribution distance is calibrated; per-drug reliability is not
Two candidate confidence signals were tested. Per-drug cell-line cross-validation reliability did **not** predict
patient-transfer accuracy (Spearman +0.02, p=0.45). Out-of-distribution (OOD) distance did: patients closer to
the training distribution were more accurately predicted (+0.051, p=0.0055). The engine gates confidence by OOD
only, capped at "moderate" (B6).

### 2.6 External replication is fragile; PDX proxies are underpowered
In an independent patient-derived-xenograft cohort (PDXE, ~399 models), the drug-specific signal was borderline
under one training screen (p=0.036, 9 drugs) but did **not** hold under a broader PRISM-trained set (p=0.076, 11
drugs); overall transfer magnitude was non-significant (p=0.14–0.31) and proliferation transferred better than
drug-specificity (B7, B9). Established solid-tumor markers (PIK3CA→alpelisib) showed the correct direction but
were underpowered (15 mutant models; BH-q=0.087) (B8). PDX drug-specificity is therefore **unestablished**.

### 2.7 The engine does not predict human clinical drug response (decisive null)
In real human patients (TCGA; 12 drugs with clinical RECIST-style response, 1,079 patients with matched
expression), the engine's raw association with response appeared significant (pooled AUROC 0.539, permutation
p=0.036). **However, this is entirely cancer-type confounding.** Within-cancer stratified analysis — which
removes cancer-type structure — gives AUROC = **0.504 (permutation p=0.43), a well-powered null**; a
proliferation-only predictor was likewise uninformative (AUROC 0.444). The engine predicts *which cancers*
respond to *which drugs*, not *which patient within a cancer* will respond (B10). We could not establish drug-
level human clinical prediction on available observational data.

### 2.8 A functional-inference layer rescues actionable-target prediction — and adds beyond the standard biomarker
Because baseline expression encodes proliferation/lineage rather than drug-specific vulnerability, we tested a
**functional** readout: CRISPR gene-dependency (DepMap). Target-gene dependency predicts drug response far better
than baseline expression (pooled ρ=+0.19, p=5×10⁻⁴; e.g. MDM2→idasanutlin ρ=+0.48; median |ρ| dependency 0.13 vs
expression 0.07, p=0.015). Dependency is **learnable from expression** (CV ρ up to 0.59), giving a
**patient-translatable functional layer** (expression→inferred-dependency). Applied to BeatAML patient ex-vivo
response, this layer is **not** a broad improvement over direct transfer, but it **specifically rescues the
dependency-driven actionable targets** where the direct transcriptomic approach fails: FLT3, BCL2, CDK9, AURKA
(9/26 drugs, BH<0.05; FLT3 inhibitors ρ=+0.13…+0.24 and venetoclax +0.22 vs a direct transfer that is ~0 or
wrong-signed). Decisively, **inferred-FLT3-dependency predicts FLT3-inhibitor response beyond FLT3-ITD mutation
status** (meta β=+7.6, p=8×10⁻¹¹) — including **within FLT3-ITD-wildtype patients** (pooled ρ=+0.22, p=1.5×10⁻¹⁵),
i.e. it identifies FLT3-inhibitor-sensitive AML that standard mutation testing misses, from RNA alone. Scope: all
of §2.8 is BeatAML **ex-vivo** (not clinical outcome), AML, dependency-model trained on pan-cancer cells — a
strong, mechanistically-coherent translational lead, not a validated clinical test.

We tested that boundary directly. In a pre-registered Cox model on overall survival (n=644 patients, 395 deaths,
106 FLT3-inhibitor–treated), the inferred-dependency×FLT3i-treatment interaction was **null** (HR=0.89, p=0.56),
as was dependency→survival within treated (HR=0.92, p=0.50) and untreated (HR=0.97, p=0.65). This is expected and
honest: BeatAML records no treatment dates and no first-line FLT3i, so immortal-time and confounding-by-indication
bias *toward* a spurious positive — making the null the interpretable result. The strong *ex-vivo* signal thus
does not, and on this retrospective design cannot, establish a *survival* benefit. It bounds the lead precisely:
the clinical endpoint requires a prospective design, not more observational data (B17).

## 3. Discussion

The honest arc is: transcriptomic transfer is **real but weak** where the readout is a direct in-vitro/ex-vivo
drug measurement (cell lines, AML ex-vivo), and it **fails** at the clinical endpoint once cancer type is
controlled. Three points deserve emphasis. First, **leakage and baselines matter**: the same pipeline reports
+0.278 (leaky) vs +0.212 (clean) vs a +0.058 parameter-free floor — reporting only the first would triple-count
the achievement. Second, **hand-picked associations can evaporate under genome-wide correction** (NPM1→
cabozantinib), while the truly robust markers are the textbook ones (FLT3-ITD, RAS). Third, and most important,
**the cell-line→human gap is not closed by better models but is bounded by confounding**: observational human
response is dominated by cancer type, stage, and regimen (multi-drug), so a per-drug transcriptomic predictor
cannot be validated at the drug level from data of this kind. A dbGaP/EGA application for more observational data
would face the identical ceiling; genuine clinical prediction requires **prospective, controlled, single-agent**
cohorts.

**Limitations.** Cross-platform normalization is crude (per-gene z). PDX/ex-vivo are proxies. TCGA response is
coarse and regimen-attributed. Effect sizes throughout are small. We make no novel-molecule, therapy-selection,
or "any-disease" claims — earlier such claims in this program were falsified or retracted and are archived as
history, not results.

**What this engine is.** A reproducible, mechanism-anchored, calibration-aware **cell-line/ex-vivo drug-response
engine** with an honestly bounded scope — useful for hypothesis ranking and as a rigorous baseline, not as a
clinical decision tool.

## 4. Methods (summary)

Per-drug RidgeCV (α∈{10,100,1000}) on top-2000-variance shared genes, per-gene z-scored within each dataset;
strict splits exclude every test cell line from training. Mutation markers from BeatAML WES (non-silent) and
clinical (FLT3-ITD, NPM1). Genome-wide screen: OLS `AUC ~ mutation + FLT3-ITD + R_prolif`, BH-FDR across all
pairs, md5 split-half direction replication. Transfer to patients/PDX/TCGA: engine trained on DepMap RNA-seq +
GDSC or PRISM labels, applied to query z-expression; proliferation residualization via OLS on R_prolif; drug-
specificity via diagonal vs off-diagonal permutation. Human validation: within-cancer stratified AUROC
(cancer-confound control), permutation k=2000, seed=42. All experiments reproduce ×2 (identical metrics JSON).
Full methods, code, pre-registrations, and per-experiment metrics are in the repository.

## 5. Data and code availability

Code, all pre-registrations (`prereg/`), all metrics (`experiments/*/results/`), the evidence ledger
(`LEDGER.md`), and the integrity record (`INTEGRITY_SWEEP.md`) are public at
`github.com/AKULA-PRASAD/intercepta-build`. Inputs are public (GDSC, DepMap/CCLE, PRISM, PDXE [Gao et al. 2015],
TCGA via UCSC Xena + curated clinical drug response) except BeatAML (dbGaP phs001657, controlled). No patient-
level data is redistributed; `data/MANIFEST.md` gives sha256 + access class for every input.

## 6. Key references
GDSC (Yang 2013); DepMap/CCLE (Ghandi 2019); PRISM (Corsello 2020); BeatAML (Tyner 2018); PDXE (Gao 2015);
TCGA-CDR (Liu 2018); UCSC Xena (Goldman 2020); curated TCGA drug response (lifeome). Full citations to be
completed for submission.
