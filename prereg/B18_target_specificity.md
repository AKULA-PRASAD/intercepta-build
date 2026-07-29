# Pre-registration — B18: is the inferred-dependency layer TARGET-SPECIFIC? (double dissociation FLT3 vs BCL2) (FINALIZED 2026-07-29, PRE-RESULT)

## The question (does V19 generalize, or is it a FLT3 one-off?)
V19 showed inferred-FLT3-dependency predicts FLT3-inhibitor ex-vivo response. The decisive generalization test is
not "does it also work for BCL2?" but **is it target-specific?** — i.e. a double dissociation:
- inferred-**FLT3**-dependency predicts **FLT3-inhibitor** response but NOT **venetoclax** (BCL2 inhibitor);
- inferred-**BCL2**-dependency predicts **venetoclax** but NOT **FLT3 inhibitors**.
If the layer only read generic "drug sensitivity" (or proliferation), every inferred-dependency would predict every
drug. A clean diagonal proves it reads **target-specific vulnerability from RNA** — the core methodological claim.

## Data (public + controlled BeatAML)
- Inferred dependency: engine `fit_dependency(["FLT3","BCL2"])` (DepMap CRISPR) applied to BeatAML patient RNA.
  Value = Chronos gene-effect (more negative = more dependent).
- Ex-vivo AUC: FLT3 inhibitors {sorafenib, quizartinib, gilteritinib, crenolanib}; BCL2 inhibitor {venetoclax}.
- R_prolif from BeatAML expression (all correlations proliferation-residualized — controls the known confound).

## Sign convention
Spearman ρ(inferred gene-effect, AUC): a **positive** ρ = more-dependent (lower gene-effect) → lower AUC (more
sensitive) = **sensitizing** (target-consistent). We test for positive ρ on the matched (diagonal) cells.

## Hypotheses (assumed FALSE)
- **H1 (specificity / double dissociation):** proliferation-adjusted diagonal ρ (matched target→drug: FLT3-dep→
  FLT3i, BCL2-dep→venetoclax) is significantly greater than off-diagonal ρ (FLT3-dep→venetoclax, BCL2-dep→FLT3i).
  Tested by a permutation that shuffles the target↔drug pairing (10,000 perms); one-sided p = P(perm gap ≥ observed).
- **H2 (BCL2 pillar holds and is specific):** BCL2-dep predicts venetoclax (prolif-adj ρ>0, p<0.05) AND BCL2-dep
  does NOT predict FLT3 inhibitors (pooled prolif-adj ρ ≈ 0, not significant sensitizing).
- **H3 (FLT3 pillar is specific):** FLT3-dep predicts FLT3i (V19, prolif-adj) AND FLT3-dep does NOT predict
  venetoclax (prolif-adj not significant sensitizing).
- H0: off-diagonal ≈ diagonal — the layer reads generic sensitivity, not target-specific vulnerability.

## Decision rule (fixed)
Per (target, drug) cell with ≥25 patients: prolif-adjusted Spearman ρ (residualize both dep and AUC on R_prolif).
Diagonal = matched; off-diagonal = mismatched. **H1 PASS** iff mean(diagonal ρ) > mean(off-diagonal ρ) with
permutation p<0.05. **H2 PASS** iff venetoclax diagonal ρ>0 & p<0.05 AND BCL2→FLT3i pooled not sig-sensitizing.
**H3 PASS** iff FLT3i diagonal ρ>0 & pooled p<0.05 AND FLT3-dep→venetoclax not sig-sensitizing.

## Interpretation (fixed)
- H1 (+ H2/H3) pass → the inferred-dependency layer is TARGET-SPECIFIC: it reads which vulnerability a tumor has,
  not generic sensitivity — V19 generalizes to a second, mechanistically-independent AML pillar. Genuine advance.
- H1 fails → the layer is not target-specific (reads generic sensitivity/proliferation); V19 is a FLT3-specific
  finding only. Honest bound; still leaves V19 intact but caps the methodological claim.
- BCL2 diagonal null but FLT3 holds → layer works for FLT3 dependence but venetoclax response is not BCL2-
  dependency-encoded in RNA (venetoclax response is known to be complex/monocytic) — honest, partial.

## Honesty / scope
BeatAML ex-vivo (not clinical outcome, per B17). Venetoclax has a single BCL2 inhibitor (n=1 drug on that
diagonal) — a limitation stated up front. All correlations proliferation-adjusted. A null is first-class.

## Reproducibility
Deterministic (fixed seed for permutation); reproduce ×2. Output:
experiments/B18_target_specificity/results/B18_metrics.json.
