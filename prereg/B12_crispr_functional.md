# Pre-registration — B12: does FUNCTIONAL gene-dependency predict drug response (and beat baseline expression)? (FINALIZED 2026-07-29, PRE-DATA)
Written BEFORE the DepMap CRISPR file is on disk — a genuine pre-registration.

## Rationale (the thesis this tests)
Our central honest finding: baseline transcriptomics transfers proliferation/cancer-type, not drug-specific
vulnerability (V8/N1/B10). We argued the fix is FUNCTIONAL readouts. DepMap CRISPR **gene-dependency** (Chronos:
more-negative = the cell needs that gene) is a functional readout, public, in cell lines. B12 tests whether it
carries drug-response signal — and whether it beats baseline expression — a direct, us-only test of the thesis.
(Scope honesty: CRISPR is cell-line-only, unmeasurable in patients → this strengthens MECHANISM, it is NOT a
patient-level result.)

## Data (public)
DepMap `CRISPRGeneEffect.csv` (cell lines × genes, Chronos gene effect) + DepMap expression + PRISM AUC / GDSC
LN_IC50. Pan-cancer cell lines.

## Pre-declared drug → target-gene pairs (established pharmacology; frozen now)
FLT3i {sorafenib,quizartinib,gilteritinib,crenolanib}→FLT3; MEKi {trametinib,selumetinib,pd0325901}→MAP2K1;
venetoclax→BCL2; EGFRi {erlotinib,gefitinib,afatinib}→EGFR; PI3Ki {alpelisib,buparlisib}→PIK3CA;
CDK4/6 {ribociclib,palbociclib}→CDK6; BRAFi {dabrafenib,vemurafenib,encorafenib}→BRAF; alisertib→AURKA;
everolimus→MTOR; idasanutlin/nutlin→MDM2. (Only pairs where drug∈PRISM/GDSC and target∈CRISPR are tested.)

## Hypotheses (assumed FALSE)
- **H1 (functional mechanism):** across pairs, Spearman(target gene-effect, drug response) > 0 (cells DEPENDENT on
  the target — more-negative effect — are MORE sensitive — lower AUC/LN_IC50), pooled, permutation p<0.05, BH per pair.
- **H2 (functional > baseline — the thesis):** |Spearman(dependency, response)| > |Spearman(target EXPRESSION,
  response)|, paired across pairs (does the functional readout beat the baseline readout for the SAME target/drug?).
- H0: dependency carries no drug-response signal / does not beat expression.

## Decision rule (fixed)
Per pair (≥25 cell lines with dependency + response): Spearman(gene_effect, response) [+ expression comparator].
Pooled: mean signed ρ + permutation (k=2000, seed=42); BH-FDR per pair. H1 PASS iff pooled ρ>0 & p<0.05. H2 PASS
iff median |ρ_dependency| > median |ρ_expression| & paired-permutation p<0.05.

## Interpretation (fixed in advance)
- H1+H2 pass → functional dependency is a real, superior mechanism signal → justifies pivoting the engine's
  mechanism layer to functional features (and pre-filters novel hypotheses). A genuine, honest advance (still cell-line).
- H1 pass, H2 fail → dependency works but no better than expression for these targets.
- Null → functional dependency doesn't help here (honest, recorded).

## Reproducibility
Deterministic; seed=42, k=2000; reproduce ×2. Output: `experiments/B12_crispr_functional/results/B12_metrics.json`.
