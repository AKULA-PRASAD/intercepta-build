# Pre-registration — B16: does inferred-FLT3-dependency predict FLT3-inhibitor response BEYOND FLT3-ITD? (FINALIZED 2026-07-29, PRE-RESULT)

## The decisive question (CSO-chosen; ultra-analyzed)
The functional layer (V17/V18) predicts FLT3-inhibitor ex-vivo response. But FLT3-ITD mutation status ALREADY
predicts it (standard clinical practice; B5 BHq=4e-26). So the layer is only a real advance if it adds signal
**beyond the mutation biomarker** — otherwise you'd just test FLT3-ITD. B16 tests exactly this. (A raw survival
test was rejected as confounded/underpowered in BeatAML — treatment heterogeneity; this biomarker-conditioned
ex-vivo test is the clean, powered, honest one.)

## Data (public + controlled BeatAML)
Inferred FLT3 dependency: engine `fit_dependency(["FLT3"])` on DepMap CRISPR, applied to BeatAML patient RNA.
FLT3-ITD: BeatAML clinical (positive/negative). Ex-vivo AUC for FLT3 inhibitors: sorafenib, quizartinib,
gilteritinib, crenolanib. R_prolif from BeatAML expression.

## Hypotheses (assumed FALSE)
- **H1 (adds beyond mutation):** in OLS `AUC ~ inferred_FLT3_dep + FLT3_ITD + R_prolif`, the inferred_dep
  coefficient is significant with correct sign (more inferred-dependent [more negative] → lower AUC = sensitive),
  pooled across the 4 FLT3 inhibitors, BH per drug. I.e., the functional layer adds over the clinical biomarker.
- **H2 (value where mutation is silent):** WITHIN FLT3-ITD-negative patients, inferred_FLT3_dep still predicts
  FLT3-inhibitor sensitivity (Spearman p<0.05 pooled) — the clinically-useful case (RNA finds FLT3-dependence the
  mutation test misses).
- H0: inferred_dep does not add beyond FLT3-ITD (redundant with mutation testing).

## Decision rule (fixed)
Per drug (≥25 patients with AUC + ITD + inferred_dep): OLS partial p/sign for inferred_dep (H1); Spearman in
ITD-negative subset (H2). Pooled via count + DerSimonian–Laird meta of the standardized inferred_dep coefficient;
BH across drugs. **H1 PASS** iff meta coef>0 (sensitizing) & p<0.05. **H2 PASS** iff pooled ITD-WT ρ>0 & p<0.05.

## Interpretation (fixed)
- H1+H2 pass → the functional layer is a GENUINE advance over standard FLT3-ITD testing (captures FLT3-dependence
  beyond the mutation, including in ITD-WT patients) — real clinical value, honestly bounded to AML ex-vivo.
- H1 pass, H2 fail → adds modestly but mainly refines within ITD+ (still useful).
- Null → redundant with FLT3-ITD; the layer re-detects the known biomarker (honest, bounds the advance).

## Honesty / scope
BeatAML ex-vivo (not clinical outcome). Inferred dependency correlates with FLT3-ITD by construction, so H1/H2
are stringent (asking for signal ON TOP of the mutation). A null is fully expected and first-class.

## Reproducibility
Deterministic; reproduce ×2. Output: experiments/B16_beyond_mutation/results/B16_metrics.json.
