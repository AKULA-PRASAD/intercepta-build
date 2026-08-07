# META1 — The Transfer Law: what drives FBA-essentiality → experimental-essentiality transfer

**PRE-REGISTERED before computing any correlation.** This is a RETROSPECTIVE META-ANALYSIS of
our OWN committed in-silico results (not a new wet experiment). Inputs are committed
`experiments/*/results/*.json` metrics files; numbers are READ from those files (never invented).

## Question
Across every organism where we have an FBA-essentiality vs EXPERIMENTAL-essentiality 2×2 result,
what drives transfer success — the odds ratio (OR) and the pass/fail of the pre-registered gate
(OR>3 AND Fisher p<0.01)? The 7-organism prospective-blind suite plus the curated/held-out sets
show a prokaryote-strong / eukaryote-mixed pattern. Explain it quantitatively.

## Dataset assembly (per-organism PRIMARY set)
One row per unique organism. Fields read from the cited JSON: contingency
{both, FBA_only, exp_only, neither}, odds_ratio, fisher_p, precision, recall, n_fba_essential,
n_gem_genes (GEM size/coverage), committed gate pass/fail. Derived (from contingency):
`n_adjudicable = sum(cells)`, `base_rate = (both+exp_only)/n_adjudicable`,
`fba_ess_frac = (both+FBA_only)/n_adjudicable`, `lift = precision/base_rate`,
`LR_plus = recall / (FBA_only/(FBA_only+neither))`, `log_OR` with Haldane–Anscombe +0.5
per cell (so OR=0 organisms are finite/rankable).

Annotated METADATA (my taxonomic classification, documented — NOT read from a metrics field):
`domain` ∈ {bacteria, archaea, eukaryote}; `host_dependent` (obligate intracellular / host-embedded
parasite) bool; `GEM_type` ∈ {curated, denovo_CarveMe}.

Sources (PRIMARY, per organism):
- CROSSVAL_curated (curated GEMs): E. coli iML1515, K. pneumoniae iYL1228, Salmonella Tm,
  B. subtilis iYO844, S. aureus iYS854, M. tuberculosis iEK1008.
- VALIDATE_essentiality_deg (CarveMe): A. baumannii (held-out), P. aeruginosa.
- BLIND1–7 reveals: N. gonorrhoeae, C. jejuni, B. thetaiotaomicron, S. pneumoniae (all CarveMe
  bacteria); M. maripaludis (curated iMR539, ARCHAEA); K. phaffii (CarveMe, EUKARYOTE yeast);
  T. brucei (CarveMe, EUKARYOTE parasite).
- GENERALIZE4 (S. cerevisiae iMM904), HARDENF1 (C. albicans), GENERALIZE5 (P. falciparum iPfal19),
  HARDENP1 (T. gondii iTgo2020) — curated eukaryote GEMs.

For organisms with MULTIPLE GEM/truth-set results (E. coli, K. pneumoniae, M. tuberculosis appear
in both CROSSVAL-curated and VALIDATE-CarveMe), the PRIMARY row uses the CURATED GEM (reduces
model-source heterogeneity). The alternate de-novo rows (VALIDATE main E. coli PEC OR64, VALIDATE
K. pneumoniae held-out OR63, VALIDATE Mtb CarveMe OR7.9) are retained as a WITHIN-ORGANISM
sensitivity set, not as independent primary rows.

PARARESOLVE1/2 (same organism P. falciparum, varying GEM/screen) are used ONLY as a labelled
within-organism base-rate demonstration, not as primary rows.

## Candidate drivers + hypotheses (fixed before computing)
- **H1 (GEM coverage/quality)**: larger/better GEM → higher OR / pass. Tests: Spearman(log_OR,
  n_fba_essential), Spearman(log_OR, n_gem_genes), Spearman(log_OR, fba_ess_frac); and GEM_type
  (curated vs de-novo) vs pass (Fisher/Mann–Whitney).
- **H2 (base-rate compression)**: higher experimental base rate → lower OR even at equal true
  signal. Tests: Spearman(log_OR, base_rate) (predict NEGATIVE). AND the key methodological test —
  does a base-rate-robust statistic (precision-lift = precision/base_rate; LR+; Fisher p)
  separate committed pass/fail, or reveal "fails" that still carry real signal (small p / lift>1)?
  Within-organism confirmation via PARARESOLVE (same GEM, different-base-rate screens).
- **H3 (host-dependence)**: obligate host-dependent organisms fail. Tests: Mann–Whitney(log_OR by
  host_dep); pass-rate by host_dep.
- **H4 (domain)**: prokaryote vs eukaryote predicts OR AFTER controlling for base rate + coverage.
  Tests: Spearman(log_OR, domain_euk); multivariable OLS `log_OR ~ base_rate + log(n_fba_essential)
  + domain_euk + host_dep` with 95% CIs; report collinearity/VIF honestly.

## Analysis plan (fixed)
1. Spearman rank correlations (effect size ρ + p) of log_OR with each continuous driver.
2. Mann–Whitney U + rank-biserial for each binary driver (domain_euk, host_dep, GEM_type) vs log_OR,
   and vs committed_pass.
3. One multivariable OLS on log_OR (report βs, 95% CIs, R², note n vs p, VIF). Attempt a logistic
   on committed_pass; if near-separation, report as UNSTABLE / directional-only (do not over-read).
4. Base-rate-confound verdict: report Spearman(OR, base_rate); the PARARESOLVE within-organism flip;
   and a per-organism table of {OR, gate, base_rate, precision, lift, Fisher p} flagging which
   committed FAILS retain real signal (Fisher p<0.01 OR lift≥1.5) vs genuine nulls.
5. Propose a base-rate-FAIR gate (SECONDARY LENS ONLY): (Fisher p<0.01) AND (precision-lift ≥1.5).
   Show its reclassification. **Do NOT retroactively flip any committed pass/fail verdict.**

## Reproducibility
SHA-256 over sorted-key JSON of the payload EXCLUDING provenance. Run twice; assert byte-identical.
Fixed inputs (committed files); deterministic stats; no randomness except any sklearn solver
(seeded / not used for the headline).

## Honest scope (pre-committed)
Retrospective meta-analysis of committed IN-SILICO results; small n (~19 organisms, 5 fails);
CORRELATIONAL not causal; heterogeneous truth sets (Tn-seq/CRISPR/INSeq/curated-annotation/piggyBac)
and heterogeneous GEM sources are THEMSELVES a confound (base rate is partly a truth-set artifact —
PARARESOLVE proves it). domain / host_dep / GEM-coverage / base-rate are mutually collinear (all 3
host-dependent organisms are eukaryotes), so with this n the drivers may be INSEPARABLE — an
"underpowered, directional-only" verdict is a first-class allowed outcome. This EXPLAINS the observed
transfer boundary; it is NOT new wet-lab evidence and does not re-open any committed verdict.
