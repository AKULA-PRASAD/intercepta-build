# Where transcriptomic cancer drug-response prediction works and where it doesn't: an intrinsic single-agent ceiling, two decisive replication nulls, and an externally-validated drug-combination-synergy signal

Prasad Akula¹* *(author list to be finalized before submission)*

¹ Northeastern University, Boston, MA, USA
\* Correspondence: akula.pra@northeastern.edu

**Preprint / working draft — v3 (2026-07-29).** Every quantitative claim traces to a committed, reproduced-×2
metrics file in `experiments/`, `verification/`, and `LEDGER.md` of `github.com/AKULA-PRASAD/intercepta-build`.
All analyses were pre-registered (`prereg/`) before results. All figures are regenerated from committed metrics by
`papers/intercepta_engine/figures/make_figures.py`.

**Keywords:** drug-response prediction; transcriptomics; reproducibility; data leakage; confounding; external
replication; acute myeloid leukemia; functional precision medicine; negative results.

---

## Highlights
- A leakage-corrected cell-line→cell-line drug-response map transfers at mean ρ=**+0.212** and this is a hard
  **ceiling** (proliferation and 50 driver mutations add nothing); the naive leaky estimate (+0.278) overstates it.
- The engine does **not** predict human clinical response once cancer type is controlled (within-cancer AUROC
  0.504, p=0.43) — the apparent signal is cancer-type confounding.
- A functional-inference layer that beat the standard FLT3-ITD biomarker in BeatAML (proliferation-, mutation-, and
  lineage-independent) **failed independent replication** in a second AML cohort — a first-class negative.
- Across the program, signals recovering **known** biology generalize; **novel single-cohort refinements do not** —
  external replication, not internal robustness, is the decisive test.
- **The positive counterpoint:** drug-combination **synergy** prediction *does* generalize — it **externally
  replicates across two independent corpora** (DrugComb→O'Neil ρ=0.38, 2.5× retrieval enrichment) and is shipped as
  a tool with **calibrated** uncertainty. Synergy (a different signal) is not bound by the single-agent ceiling.

## Abstract

Transcriptomic prediction of cancer drug response is widely pursued, but its true reach is often obscured by
leakage, weak baselines, and unadjusted confounding. We built a reproducible engine and held every claim to
pre-registration, permutation nulls, leakage-corrected splits, multiple-testing correction, and — decisively —
external replication. The result is a graded, honest map. A learned per-drug expression→response map transfers
across independent cell-line datasets (GDSC2→CCLE/PRISM) at a leakage-free mean per-drug Spearman ρ=**+0.212**
(94/100 drugs positive; parameter-free proliferation baseline +0.058; p=1.9×10⁻¹⁵), and this is a genuine
**ceiling** — neither a proliferation axis nor 50 driver-mutation features beat it (the naive leaky design inflates
it to +0.278). Genome-wide, the robust somatic mutation→drug associations in acute myeloid leukemia (BeatAML) are
the textbook ones (FLT3-ITD→FLT3 inhibitors, RAS→MEK inhibitors); two hand-picked pairs do not survive correction.
A weak but drug-specific, proliferation-independent cell-line→patient signal exists in ex-vivo response. **But in
1,079 patients (TCGA, 12 drugs), the engine's apparent clinical-response association is entirely cancer-type
confounding (within-cancer AUROC 0.504, p=0.43).** Finally, reframing to a **functional** readout, an
expression-inferred gene-dependency layer appeared in BeatAML to identify FLT3-inhibitor-sensitive AML beyond
FLT3-ITD status (including in ITD-wildtype patients; p=1.5×10⁻¹⁵), target-specifically and robustly — yet this
**did not survive external replication** in an independent AML cohort (FIMM/Malani): the known
FLT3-mutation→inhibitor relationship replicated, but our inferred refinement did not (pooled ρ=+0.05, p=0.08). We
report both nulls as first-class results, and show the single-agent ceiling is **modality-general** — matched
proteomics and even measured genome-wide CRISPR dependency do not beat baseline RNA (the only functional signal is
a drug's own target). **The constructive counterpoint is drug combinations:** synergy — a different signal, not
bound by the single-agent ceiling — generalizes to unseen combinations and, critically, **externally replicates
across two independent corpora** (train on DrugComb, predict O'Neil: Spearman 0.38, 2.5× retrieval enrichment,
holding on novel combinations); we release it as a usable ranker with **calibrated conformal uncertainty** (90%
intervals cover ~90% on unseen combinations). The recurring lesson — signals recovering known biology or robust
combination structure generalize, whereas novel single-cohort single-agent refinements do not — bounds the modality
honestly and motivates prospective functional data over further observational single-agent modeling. Engine,
combination ranker, pre-registrations, and all negative results are released.

## Author summary
Machine-learning models that predict a tumor's drug response from its gene-expression profile are usually reported
as successes. We asked, under a strict falsify-first protocol, how far such a model actually reaches — and where it
breaks. Trained and tested on cancer cell lines without data leakage, the model works but weakly, and its accuracy
has a firm ceiling that simple baselines already approach. In real patients, its apparent link to clinical response
disappears once we account for cancer type: it distinguishes *which cancers* respond, not *which patient within a
cancer*. We then tried a more mechanistic idea — inferring each tumor's genetic dependencies from its expression —
which looked genuinely promising in one leukemia cohort, beating the standard mutation test. But when we tested it
in a second, independent leukemia cohort, it did not replicate, even though the known biology did. We report this
failure openly. The through-line is simple and useful: results that re-capture established biology generalize
across cohorts, whereas novel, single-cohort refinements often do not survive independent replication. Honestly
mapping these boundaries is, we argue, more valuable than another unreplicated positive — and it points to what a
real advance will require: functional measurements made in the patients themselves. There is also a bright spot:
predicting *drug combinations* — whether two drugs work better together — did generalize, and unlike the
single-drug results it held up in a second, independent dataset. We release that as a practical, uncertainty-aware
tool. The takeaway: single-drug prediction from a tumor's baseline profile is fundamentally limited, but drug
*combinations* are a more promising, and honestly-validated, direction.

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
cell-line ceiling** for this design (B1, B2; **Fig 1**). This ceiling is **modality-general, not RNA-specific**: on
291 cell lines with matched mass-spec proteomics (CCLE [Nusinow 2020]), DepMap RNA, and GDSC2 response under an
identical 5-fold protocol (271 drugs), proteomics did **not** beat transcriptomics (mean per-drug ρ 0.328 vs 0.419,
paired p=10⁻⁴³) and added nothing when combined (0.408 ≤ 0.419) — a second baseline molecular modality hits the
same wall (B22). The ceiling even holds for a **measured functional** modality: on 498 cell lines with matched
DepMap CRISPR gene-dependency, dependency alone did not beat RNA (0.459 vs 0.487) and integration added only +0.019
(below a pre-set materiality bar); critically, once each drug's own target-gene dependency was excluded, the
functional advantage vanished (dependency 0.504 vs RNA 0.514, p=0.06) — i.e. the only functional signal is a drug's
*own target* dependency, not a generalizable functional-state predictor (B23). This is the mechanistic explanation
for why the inferred-dependency layer (§2.8) failed to replicate.

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
respond to *which drugs*, not *which patient within a cancer* will respond (B10; **Fig 3**). We could not establish
drug-level human clinical prediction on available observational data.

### 2.8 A functional-inference layer looked promising in BeatAML but failed external replication
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

Crucially, the layer is **target-specific**, not a generic sensitivity readout. In a proliferation-adjusted
double-dissociation (inferred FLT3- vs BCL2-dependency × FLT3 inhibitors vs venetoclax), matched target→drug
correlations exceed mismatched ones (diagonal ρ=+0.19 vs off-diagonal +0.07; target↔drug-shuffle permutation
p<10⁻⁴). The FLT3 side dissociates cleanly — FLT3-dependency predicts FLT3 inhibitors (ρ=+0.20, p=2×10⁻¹⁶) but
not venetoclax (ρ=−0.03) — and venetoclax is predicted only by BCL2-dependency (ρ=+0.21, p=8×10⁻⁵), not FLT3.
The one asymmetry is biologically expected rather than artifactual: BCL2-dependency also carries some signal for
FLT3 inhibitors (ρ=+0.10), consistent with FLT3-ITD AML being BCL2-dependent/venetoclax-sensitive (the rationale
for venetoclax+FLT3-inhibitor combinations) — BCL2-dependence is simply a broader apoptotic-priming feature than
FLT3-dependence. Thus, *within BeatAML*, the functional signal reads *which* vulnerability a tumor carries, extending the FLT3
result (V19) to a second, mechanistically-independent AML pillar (B18) — a within-cohort property that, as the
next paragraphs show, did not survive external replication.

We also tested the obvious circularity concern — that a pan-cancer dependency model including AML lines might
simply re-detect AML lineage in an all-AML patient cohort. Retraining the FLT3-dependency model with **all 25
DepMap AML lines removed** (a model that never sees AML) leaves the V19 result essentially unchanged (beyond-ITD
β=+7.4, p=2×10⁻¹⁰; ITD-wildtype ρ=+0.23, p=5×10⁻¹⁷, vs +7.6/+0.22 with the full panel). The inferred dependency
is therefore genuine cross-lineage functional transfer, not lineage memorization. Removing *all* blood/lymphoid
lines does abolish the beyond-ITD effect, but that reflects the hematopoietic biology of FLT3-dependence (only two
FLT3-dependent solid-tumor anchors remain in DepMap), not a failure of the result (B19).

Within BeatAML the signal was thus robust and target-specific — so we escalated the tests. First, does the
ex-vivo signal reach a *clinical* endpoint? In a pre-registered Cox model on overall survival (n=644 patients,
395 deaths, 106 FLT3-inhibitor–treated), the inferred-dependency×FLT3i-treatment interaction was **null**
(HR=0.89, p=0.56), as was dependency→survival within treated (HR=0.92, p=0.50) and untreated (HR=0.97, p=0.65).
This is honest and expected: BeatAML records no treatment dates and no first-line FLT3i, so immortal-time and
confounding-by-indication bias *toward* a spurious positive — making the null the interpretable result. A survival
benefit is not establishable from retrospective data of this kind and requires a prospective design (B17).

Second, and decisively, does the signal even replicate *ex-vivo* in an independent cohort? The decisive test of any
biomarker is independent replication, and here the functional-inference result did not pass it. We repeated the
analysis in the FIMM/Malani AML cohort (Zenodo 7370747; Helsinki; DSRT drug-sensitivity-score assay — a different
institution and readout from BeatAML), 163 patients with matched RNA, seven FLT3 inhibitors, venetoclax, and
FLT3/NPM1 status, all pre-registered (B20). The known biology replicated cleanly: FLT3-mutation strongly predicted
FLT3-inhibitor sensitivity for all five testable inhibitors (p=10⁻⁵–10⁻³), and the inferred dependency itself
remained coherent (it tracked FLT3 expression, ρ=+0.38, with 96.5% feature-gene overlap) — so this is a fair test,
not a normalization artifact. But the claim of interest failed: inferred-FLT3-dependency did not robustly predict
FLT3-inhibitor response (proliferation-adjusted pooled ρ=+0.05, p=0.08; per drug inconsistent, e.g. sorafenib
−0.13, quizartinib +0.11), it added nothing beyond the mutation (meta β=−0.02, p=0.92), and the target-specificity
double dissociation did not reach significance (permutation p=0.13; only the venetoclax→BCL2 direction was weakly
consistent). A focused post-hoc test of whether the signal at least survives for the FLT3-*selective* inhibitors
(quizartinib, crenolanib) consistently across both cohorts was also negative — per-drug effects are unstable
across cohorts (sorafenib, the strongest in BeatAML, flips sign in FIMM) and selectivity does not separate them
(B21; **Fig 2**). We therefore report V19/V20 honestly as **BeatAML-specific and externally non-replicated**: the
standard FLT3-mutation→FLT3-inhibitor relationship generalizes across cohorts, but our expression-inferred
refinement does not. This is a first-class negative. It suggests that a functional layer with genuine, transferable value likely
requires perturbation data measured *in the patients themselves* (the prospective functional-precision design,
Track-1) rather than dependency inferred from a pan-cancer cell-line map — and it is exactly the kind of result
that a single-cohort analysis would have overstated.

### 2.9 Drug-combination synergy generalizes — an externally-validated positive (Fig 4)
Single-agent response from baseline profiles is capped and its refinements fail; we therefore asked whether a
*different* signal — drug-combination **synergy** — behaves differently. It does. On the open O'Neil/
OncoPolyPharmacology screen (23,052 measurements, 583 pairs × 39 cell lines, Loewe synergy; features = cell-line
expression + order-invariant Morgan fingerprints, gradient-boosted), synergy is predictable for **unseen
combinations of known drugs**: leave-drug-combination-out Spearman ρ=**+0.61** vs an informed drug-marginal
baseline +0.47 (Δ+0.13, bootstrap CI [0.12,0.14]), synergistic-class AUROC 0.80 (B24). Scaling to the larger
DrugComb corpus (124 drugs, 41 cell lines) reproduces the combination-generalization (ρ=+0.38 vs baseline +0.29),
but shows the honest bounds: generalization to genuinely **novel drugs** collapses (leave-drug-out ρ 0.25→0.025 on
the more diverse corpus, B25), and a mechanism-anchored encoding (each drug by its target's CRISPR dependency) does
**not** beat chemical fingerprints for novel drugs (B26); a connectivity/LINCS-signature-reversal repurposing
signal is statistically significant but practically negligible (ρ=0.02, B27). Decisively, the synergy signal
**externally replicates across independent corpora**: a model trained on DrugComb predicts *measured* synergy in
the independent O'Neil dataset (different institution and Loewe computation) at Spearman **+0.38** (CI [0.36,0.39]),
with **2.5× retrieval enrichment** for truly synergistic pairs, and it **holds on novel combinations** (ρ=+0.44);
the reverse (small→diverse) is weak, an expected train-on-diverse asymmetry (B28). We release this as a usable
ranker (`SynergyRanker`) that, given a tumor/cell expression profile, ranks synergistic pairs from a known drug
library with an out-of-distribution confidence gate and **calibrated conformal prediction intervals** — empirical
coverage matches nominal on unseen combinations (90%→89.8%/90.5%, 80%→79.5%/80.6% on O'Neil/DrugComb; B29), with
the intervals deliberately wide to convey that individual point predictions are uncertain. Scope: cell-line Loewe
synergy (not clinical), known-drug library only. This is the program's one externally-validated positive — evidence
that *combination structure*, unlike single-agent baseline signal, carries transferable, practically-useful
information.

## 3. Discussion

The honest arc is: transcriptomic transfer is **real but weak** where the readout is a direct in-vitro/ex-vivo
drug measurement (cell lines, AML ex-vivo), and it **fails** at the clinical endpoint once cancer type is
controlled. Four points deserve emphasis. First, **leakage and baselines matter**: the same pipeline reports
+0.278 (leaky) vs +0.212 (clean) vs a +0.058 parameter-free floor — reporting only the first would triple-count
the achievement. Second, **hand-picked associations can evaporate under genome-wide correction** (NPM1→
cabozantinib), while the truly robust markers are the textbook ones (FLT3-ITD, RAS). Third, **the cell-line→human
gap is not closed by better models but is bounded by confounding**: observational human response is dominated by
cancer type, stage, and regimen (multi-drug), so a per-drug transcriptomic predictor cannot be validated at the
drug level from data of this kind. A dbGaP/EGA application for more observational data would face the identical
ceiling; genuine clinical prediction requires **prospective, controlled, single-agent** cohorts. Fourth, and most
instructive, our single most promising positive — a functional-inference layer that, in BeatAML, appeared to beat
the standard FLT3-ITD biomarker (proliferation-independent, mutation-independent, target-specific, and robust to
lineage-leakage) — **did not survive independent replication**. It is a clean illustration of why external
replication, not internal robustness, is the decisive test: every within-cohort control passed, yet the effect
was BeatAML-specific. The recurring wall across this entire program is the same — signals that recover *known*
biology (proliferation, cancer type, established markers) generalize; putatively *novel*, drug-specific,
single-cohort refinements do not. Nor is the wall specific to transcriptomics: a matched mass-spec proteomic
profile does not beat or add to RNA for cell-line drug response (B22), so the ceiling is a property of baseline
molecular profiling itself, not of one assay. The implication is consistent and constructive: a layer with real,
transferable value must be built on **functional/perturbation** data measured *in the target patients*
(prospective functional-precision cohorts, Track-1), not inferred from, or re-measured as another baseline omic
of, a pan-cancer cell-line map. Fifth, the same falsify-first lens found a genuine **positive**: drug-combination
synergy is a *different* signal that is **not** bound by the single-agent ceiling — it generalizes to unseen
combinations and, unlike every single-agent refinement here, **survives external replication across independent
corpora** (with practically-useful, calibrated predictions). The contrast is the paper's central, constructive
message: baseline single-agent molecular profiling is intrinsically capped, but *combination structure* carries
transferable information — so the productive frontier is combinations (computationally, now) and patient-measured
function (prospectively, next), not more single-agent modeling of existing data.

**Limitations.** Cross-platform normalization is crude (per-gene z). PDX/ex-vivo are proxies. TCGA response is
coarse and regimen-attributed. Effect sizes throughout are small. We make no novel-molecule, therapy-selection,
or "any-disease" claims — earlier such claims in this program were falsified or retracted and are archived as
history, not results.

**What this engine is.** A reproducible, mechanism-anchored, calibration-aware **cell-line/ex-vivo drug-response
engine** with an honestly bounded scope — useful for hypothesis ranking and as a rigorous baseline, not as a
clinical decision tool — plus an **externally-validated drug-combination-synergy ranker** with calibrated
uncertainty (`intercepta.synergy.SynergyRanker`), the program's one transferable positive.

## 4. Methods (summary)

**Transfer engine.** Per-drug RidgeCV (α∈{10,100,1000}) on top-2000-variance shared genes, per-gene z-scored
within each dataset; strict splits exclude every test cell line from training. Mutation markers from BeatAML WES
(non-silent) and clinical (FLT3-ITD, NPM1). Genome-wide screen: OLS `AUC ~ mutation + FLT3-ITD + R_prolif`, BH-FDR
[Benjamini–Hochberg 1995] across all 3,051 pairs, MD5-seeded split-half direction replication. Transfer to
patients/PDX/TCGA: engine trained on DepMap RNA-seq + GDSC or PRISM labels, applied to query z-expression;
proliferation residualization via OLS on a frozen proliferation axis (R_prolif); drug-specificity via diagonal
vs off-diagonal permutation. Human validation: within-cancer stratified AUROC (cancer-confound control),
permutation k=2000, seed=42. Meta-analyses use DerSimonian–Laird random effects [1986].

**Functional-inference layer.** Per-target Ridge models predict DepMap CRISPR gene-effect (Chronos [Dempster et
al. 2021]) from cell-line expression; the fitted model is applied to patient RNA to obtain an *inferred* gene-
dependency. "Beyond-mutation" tests (B16) use OLS `response ~ inferred-dependency + mutation + R_prolif` with
DerSimonian–Laird meta-analysis across drugs and a within-mutation-negative Spearman test. Target-specificity
(B18) uses a proliferation-adjusted dependency×drug matrix with a target↔drug label-shuffle permutation.
Lineage-leakage control (B19) retrains the dependency model with AML (or all blood/lymphoid) lines removed.

**External replication (B20/B21).** The FIMM/Malani AML cohort (Zenodo 7370747; Log2CPM RNA, Ensembl→HGNC via a
GENCODE-derived map; DSRT drug-sensitivity scores, higher = more sensitive; binary mutations) was analyzed with
the identical inferred-dependency pipeline. Effects are oriented so positive = sensitizing in both cohorts
(BeatAML sensitivity = −AUC; FIMM = DSS). Pooling uses sample-size-weighted Fisher-z; permutations use fixed
seed 42. All experiments reproduce ×2 (byte-identical metrics JSON).

**Drug-combination synergy (B24–B29).** Open synergy data via Therapeutics Data Commons [Huang 2021]:
O'Neil/OncoPolyPharmacology [O'Neil 2016] and DrugComb [Zheng 2021], Loewe synergy. Features: DepMap-expression
PCA (cell) + order-invariant Morgan fingerprints (RDKit; sum + bitwise-AND of the two drugs) (drug);
HistGradientBoostingRegressor. Generalization by leave-drug-combination-out and leave-drug-out GroupKFold; external
validation by training on one corpus and predicting measured synergy in the other; retrieval by precision@10%
enrichment over base rate. Prediction intervals are split-conformal, calibrated on leave-combination-out residuals;
empirical coverage validated on disjoint-by-combination test sets (B29). LINCS connectivity (B27) uses dhimmel/lincs
consensus signatures [Subramanian 2017]. Full methods, code, pre-registrations, and per-experiment metrics are in
the repository.

## 5. Figures

All figures are generated deterministically from committed metrics by
`papers/intercepta_engine/figures/make_figures.py`; no values are hand-entered.

- **Fig 1. Cross-dataset transfer and its ceiling (B1).** Mean per-drug Spearman ρ for the leaky design (test
  lines present in training, +0.278), the leakage-corrected design (disjoint lines, +0.212), and a parameter-free
  proliferation baseline (+0.058); 100 drugs, 94% positive, p=1.9×10⁻¹⁵ vs baseline.
- **Fig 2. A functional-inference layer promising in BeatAML fails independent replication.** (A) Proliferation-
  adjusted inferred-FLT3-dependency→FLT3-inhibitor sensitivity per shared drug, BeatAML (AUC) vs FIMM (DSS);
  sorafenib, the strongest BeatAML effect, reverses sign in FIMM. (B) Target-specificity gap (matched minus
  mismatched dependency→drug correlation) with target↔drug-shuffle permutation p: strong in BeatAML (B18,
  p<10⁻⁴), null in FIMM (B20, p=0.13).
- **Fig 3. Human clinical prediction is cancer-type confounding (B10).** Clinical-response AUROC in TCGA
  (12 drugs, 28 within-cancer strata): raw pooled (0.539, p=0.04, confounded), within-cancer controlled (0.504,
  p=0.42, null), and proliferation-only (0.444); dashed line = chance.
- **Fig 4. Drug-combination synergy is the externally-validated positive (B24/B28/B29).** (A) Synergy Spearman ρ:
  within-corpus new combinations (O'Neil, +0.61), external cross-corpus DrugComb→O'Neil (+0.38, 2.5× retrieval
  enrichment), and the weak reverse O'Neil→DrugComb (+0.09). (B) Conformal prediction-interval calibration —
  empirical vs nominal coverage on unseen combinations for both corpora sits on the identity line (calibrated).

## 6. Data and code availability

Code, all pre-registrations (`prereg/`), all metrics (`experiments/*/results/`), the evidence ledger
(`LEDGER.md`), the integrity record (`INTEGRITY_SWEEP.md`), and figure-generation code are public at
`github.com/AKULA-PRASAD/intercepta-build`. Inputs are public — GDSC [Yang 2013], DepMap/CCLE [Ghandi 2019] and
CRISPR gene effect [Dempster 2021], PRISM [Corsello 2020], PDXE [Gao 2015], TCGA via UCSC Xena [Goldman 2020] with
curated clinical drug response and TCGA-CDR [Liu 2018], the FIMM/Malani AML functional-precision cohort
[Malani 2022; Zenodo 7370747, CC-BY 4.0], CCLE quantitative proteomics [Nusinow 2020; gygi.hms.harvard.edu],
drug-combination synergy (O'Neil/OncoPolyPharmacology and DrugComb via Therapeutics Data Commons [Huang 2021]), and
LINCS L1000 consensus signatures [dhimmel/lincs, Zenodo 47223] — except BeatAML [Tyner 2018; dbGaP phs001657,
controlled-access]. No patient-level data is redistributed; `data/MANIFEST.md` gives sha256/MD5 and access class
for every input. The combination ranker ships in `intercepta.synergy.SynergyRanker` (CLI `intercepta synergy`).

## 7. Author contributions, competing interests, funding

**Contributions.** P.A. conceived and directed the project. Study design, implementation, analysis, and manuscript
were carried out with the assistance of an AI coding/analysis system operating under a fixed falsify-first
protocol; all pre-registrations, code, and metrics are committed for independent verification. *(Author list and
contribution statement to be finalized before submission.)*
**Competing interests.** None declared.
**Funding.** No dedicated funding. Analyses used only publicly available and controlled-access (BeatAML) datasets
under their respective terms.

## 8. Reproducibility statement

Every quantitative claim maps to a committed metrics JSON reproduced twice with byte-identical output; every
inferential analysis was pre-registered before results (`prereg/`); figures regenerate from committed metrics via
a single script. Random seeds are fixed (42) and reported. Controlled data (BeatAML) are not redistributed;
reproduction of BeatAML-dependent results requires the reader's own dbGaP access. All other inputs are public.

## 9. References

1. Yang W, Soares J, Greninger P, et al. Genomics of Drug Sensitivity in Cancer (GDSC): a resource for therapeutic
   biomarker discovery in cancer cells. *Nucleic Acids Res.* 2013;41(D1):D955–D961.
2. Ghandi M, Huang FW, Jané-Valbuena J, et al. Next-generation characterization of the Cancer Cell Line
   Encyclopedia. *Nature.* 2019;569:503–508.
3. Corsello SM, Nagari RT, Spangler RD, et al. Discovering the anticancer potential of non-oncology drugs by
   systematic viability profiling. *Nature Cancer.* 2020;1:235–248.
4. Tyner JW, Tognon CE, Bottomly D, et al. Functional genomic landscape of acute myeloid leukaemia. *Nature.*
   2018;562:526–531.
5. Gao H, Korn JM, Ferretti S, et al. High-throughput screening using patient-derived tumor xenografts to predict
   clinical trial drug response. *Nature Medicine.* 2015;21:1318–1325.
6. Liu J, Lichtenberg T, Hoadley KA, et al. An integrated TCGA pan-cancer clinical data resource to drive
   high-quality survival outcome analytics. *Cell.* 2018;173(2):400–416.
7. Goldman MJ, Craft B, Hastie M, et al. Visualizing and interpreting cancer genomics data via the Xena platform.
   *Nature Biotechnology.* 2020;38:675–678.
8. Malani D, Kumar A, Brück O, et al. Implementing a functional precision medicine tumor board for acute myeloid
   leukemia. *Cancer Discovery.* 2022;12(2):388–401. (Data: Zenodo 7370747.)
9. Dempster JM, Boyle I, Vazquez F, et al. Chronos: a cell population dynamics model of CRISPR experiments that
   improves inference of gene fitness effects. *Genome Biology.* 2021;22:343.
10. Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple
    testing. *Journal of the Royal Statistical Society: Series B.* 1995;57(1):289–300.
11. DerSimonian R, Laird N. Meta-analysis in clinical trials. *Controlled Clinical Trials.* 1986;7(3):177–188.
12. Nusinow DP, Szpyt J, Ghandi M, et al. Quantitative proteomics of the Cancer Cell Line Encyclopedia. *Cell.*
    2020;180(2):387–402.
13. O'Neil J, Benita Y, Feldman I, et al. An unbiased oncology compound screen to identify novel combination
    strategies. *Molecular Cancer Therapeutics.* 2016;15(6):1155–1162.
14. Zheng S, Aldahdooh J, Shadbahr T, et al. DrugComb update: a more comprehensive drug sensitivity data repository
    and analysis portal. *Nucleic Acids Research.* 2021;49(W1):W174–W184.
15. Huang K, Fu T, Gao W, et al. Therapeutics Data Commons: machine learning datasets and tasks for drug discovery
    and development. *NeurIPS Datasets and Benchmarks.* 2021.
16. Subramanian A, Narayan R, Corsello SM, et al. A next generation connectivity map: L1000 platform and the first
    1,000,000 profiles. *Cell.* 2017;171(6):1437–1452.
17. Angelopoulos AN, Bates S. Conformal prediction: a gentle introduction. *Foundations and Trends in Machine
    Learning.* 2023;16(4):494–591.

*Reference bibliographic details were drawn from the primary sources; DOIs/PMIDs and any remaining page-number
verification to be added in the submission-formatted bibliography.*
