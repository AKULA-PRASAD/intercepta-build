# TRANSFERLAW1 — a quantitative, a-priori transfer-condition law for FBA target-ID (PRE-REGISTRATION)

*Locked 2026-08-11, BEFORE computing any autonomy feature or looking at any autonomy↔outcome relationship.
Converts the program's central *qualitative* transfer-condition principle ("a label-free signal transfers as
far as the biological invariant it rides on is conserved") into a *quantitative, falsifiable, a-priori
predictor* for the one validated signal — FBA metabolic gene-essentiality. Falsify-first: the design's most
likely alternative outcome (autonomy does not predict transfer) is a reportable HONEST NEGATIVE that bounds the
principle to the qualitative, not a hidden failure.*

## The question (the vision's meta-question, made computable)
For a genuinely new disease/organism, *before* running any validation, can we predict from its genome-scale
metabolic model (GEM) **alone** whether zero-data FBA target-ID will transfer (clear the essentiality-enrichment
gate)? If yes, the transfer-condition principle is a deployable **law with a computable deployment envelope**;
if no, it remains an after-the-fact qualitative framework.

## Hypothesis
The FBA-essentiality signal rides on the invariant **"self-contained, adequately-modelled metabolism."** We
predict transfer success is a function of a GEM-intrinsic **metabolic-autonomy / model-adequacy score S**,
computed from the model topology with **zero use of the experimental essentiality ground truth or the OR
outcome** — high S (autonomous, complete metabolism) → transfer; low S (host-scavenging or sparse/incomplete
model) → failure. Concretely, host-embedded parasites (Plasmodium, T. brucei) and sparse de-novo models
(S. pneumoniae) should score LOW; complete free-living bacterial/fungal/archaeal GEMs should score HIGH.

## The non-circularity analysis (the crux — stated before any computation)
The **outcome** (OR of FBA-essential vs *experimentally* essential genes) depends on BOTH (a) the model AND
(b) independent lab knockout data. The **predictor S** depends on the model **only**, and specifically on
*model-adequacy/autonomy topology* (size, blocked fraction, exchange ratio, biomass self-synthesis, GPR
coverage) — **not** on the essentiality calls themselves. Therefore "S predicts the outcome" is the non-trivial
claim *"a model's structural adequacy predicts how well its essentiality calls match reality,"* which is a
genuine, useful, non-circular deployment law — not a restatement of the model. **Forbidden features (would be
circular, excluded):** the FBA single-gene-deletion essentiality set, its size/fraction, or anything derived
from comparing predictions to experimental essentiality.

## Predictor S (pre-specified, computed from the GEM only; frozen here)
Per GEM, five outcome-independent, interpretable features:
1. `log10_reactions` — model size/adequacy (sparse models are incomplete).
2. `blocked_fraction` — fraction of reactions carrying zero flux under FVA on the model's own medium (gap/incompleteness proxy). *(sign: −)*
3. `exchange_fraction` — n(exchange reactions)/n(reactions): a **host-scavenging** proxy (parasites import biomass precursors). *(sign: −)*
4. `biomass_synth_fraction` — of the biomass-reaction precursors, the fraction the model can each produce (demand-reaction test) on its medium (metabolic self-sufficiency). *(sign: +)*
5. `gpr_coverage` — fraction of reactions with a gene-protein-reaction rule (model completeness). *(sign: +)*

**Composite score:** `S = z(log10_reactions) − z(blocked_fraction) − z(exchange_fraction) + z(biomass_synth_fraction) + z(gpr_coverage)`
(equal weights, signed by the pre-registered direction above; z-scored across the panel). No weight fitting.

### CORRECTION 2026-08-11 (pre-scoring; before ANY S↔OR relationship was computed on the panel)
A 3-GEM validation (E. coli, P. falciparum iPfal19, Toxoplasma iTgo2020, run before full scoring) showed
`biomass_synth_fraction` is **degenerate — 1.0 for all three, including the failing Plasmodium** — because GEMs
are gap-filled *by construction* to produce biomass on their own medium, so the feature has no variance (and
z-scoring it divides by ~0). The principled fix (biomass synthesis on a *minimal* medium) requires organism-
specific minimal-medium definitions that would be **post-hoc and arbitrary** (a p-hacking surface). To preserve
non-circularity and pre-registration integrity, `biomass_synth_fraction` is **dropped** (recorded for the log,
excluded from S). Frozen score: **`S = z(log10_reactions) − z(blocked_fraction) − z(exchange_fraction) +
z(gpr_coverage)`** — four unambiguous, medium-free topology features. Signs are the pre-registered mechanistic
directions and are **not** re-tuned to the 3-GEM hints. Score is computed once; the verdict is reported as-is.
(Honest a-priori expectation from the 3-GEM look: S will likely separate clear cases — free-living bacteria vs
grossly-scavenging/sparse models — but may NOT resolve the subtle Toxo-passes/Pf-fails axis, which PARARESOLVE1
already localized to a base-rate noise floor. Whatever it shows is the reported result.)

## Panel (locked by GEMs already on disk + committed OR outcomes)
Bacteria/archaeon/fungi/parasites with a cached GEM AND a committed transfer OR: E. coli (iML1515), Salmonella
(STM_v1_0), B. subtilis (iYO844), S. aureus (iYS854), M. tuberculosis (iEK1008), K. pneumoniae (iYL1228),
A. baumannii (iCN718), N. gonorrhoeae, C. jejuni, B. thetaiotaomicron, S. pneumoniae (sparse), M. maripaludis
(archaeon, iMR539), S. cerevisiae (iMM904), C. albicans, K. phaffii, Toxoplasma (≥1 recon), and the **six
P. falciparum reconstructions** (iPfal19, iPfal17, pfal2018, ipfa2017, gf/gf_no_ortho). Final list + OR mapping
frozen in DATA.md before scoring. Gate-pass defined by the committed OR>3 verdict per organism (as recorded).

## Falsifiable gates (locked)
- **H1 (continuous law):** Spearman ρ(S, log-OR) across organisms with **bootstrap 95% CI lower bound > 0**
  (2000 resamples, seed 42). PASS → autonomy quantitatively predicts transfer strength.
- **H2 (classification):** S separates gate-PASS from gate-FAIL organisms with **AUROC ≥ 0.75** (leave-one-out
  is not required for a fixed unfitted score, but reported).
- **H3 (within-organism natural experiment — the clean test):** across the six P. falciparum reconstructions of
  the *same organism/screen* (OR spans ~0.86–3.07), S is **rank-correlated with their OR** (Spearman ρ > 0).
  This isolates model-adequacy from organism identity.
- **PASS (law established):** H1 AND (H2 or H3). **FAIL → HONEST NEGATIVE:** "the transfer-condition principle
  is real but NOT quantifiable from GEM topology alone — it stays qualitative." Reported as prominently as a pass.

## Relationship to META1 (what is genuinely new — stated honestly, before results)
`META1_transfer_law` already ran a **post-hoc** meta-analysis and found (directionally) that transfer strength
correlates with GEM coverage (`n_gem_genes`, `n_fba_essential`) and that host-dependent organisms pass far less
(14 free-living pass / 1 host-dependent), with an OLS the authors flagged "DIRECTIONAL ONLY (n small, collinear)."
TRANSFERLAW1 does **three things META1 structurally cannot**, and claims novelty only in these:
1. **A-priori & non-circular:** META1's strongest predictors are outcome-entangled — `n_fba_essential` is derived
   from the essentiality calls; `base_rate` needs the experimental knockout data. TRANSFERLAW1's score S uses
   **only GEM topology** (blocked/exchange/biomass-synthesis/GPR), so it is computable for a new organism *before
   any validation or lab data exists* — the first actually-deployable transfer predictor.
2. **Mechanistic unification:** if S works, it explains META1's *categorical* host-dependence finding as a
   *continuous* quantity — host-dependent parasites fail because they have low metabolic autonomy (high exchange
   fraction / low biomass self-synthesis), not because "host-dependence" is a brute category.
3. **A pre-registered within-organism causal test (H3):** does S rank-order the six *P. falciparum*
   reconstructions by OR? META1 varied the *screen* for Pf; it did not test whether a topology score predicts the
   *reconstruction-adequacy* ordering. If S fails all three, that is an HONEST NEGATIVE bounding META1's hint:
   the topology alone is insufficient; the entangled features were doing the work. Either way, non-redundant.

## Rigor / integrity
Reproduce ×2 byte-identical (deterministic; COBRApy FVA is deterministic given the solver; seed 42 for
bootstraps). `results/TRANSFERLAW1_metrics.json` (sorted keys) + `payload.sha256`. GEMs and outcomes are
existing committed/open artifacts; no new data committed. The forbidden-feature list is enforced in code. Any
deviation appended as a dated CORRECTION with rationale, before scoring.
