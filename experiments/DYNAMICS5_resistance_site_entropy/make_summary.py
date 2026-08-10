#!/usr/bin/env python
"""Generate SUMMARY.md from results/DYNAMICS5_metrics.json (honest, either verdict)."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, "results", "DYNAMICS5_metrics.json")))
p = m["payload"]
pr = p["primary_protein_level_paired"]
se = p["secondary_position_level_clustered"]
sn = p["sensitivity_local_context_control_NOT_GATED"]
rep = os.path.join(HERE, "REPRODUCE.txt")
repro = open(rep).read().strip() if os.path.exists(rep) else "(reproduction pending)"

verdict = p["verdict"]
firm = p["overall_pass"]
head = ("MECHANISM FIRM" if firm else "CEILING (honest negative)")

md = f"""# DYNAMICS5 - within-protein paired resistance-site entropy

**Verdict: {verdict} - {head}.**

## Question (PREREG, LOCKED)
Is ESM-2 masked-marginal Shannon entropy HIGHER at documented resistance-conferring positions
than at matched-control positions in the SAME protein? Each protein is its own control, firming
DYNAMICS1's n-fragile (n=15) target-level demonstration at position scale.

## Data (CARD protein-variant-model, WT-verified)
- Targets: **{p['n_targets']}** (expected 198). Verified resistance positions: **{p['n_resistance_positions_verified']}** (expected 1162).
- Used in 1022-windows: {p['n_resistance_positions_used_in_window']}; dropped out-of-window (large proteins): {p['n_resistance_positions_dropped_out_of_window']}.
- Metric (FROZEN, == DYNAMICS1-4): {p['metric']}.
- Units: **{p['entropy_units']}**. Model: `{p['model']}`.
- Control pool: {p['control_pool_size_rule']}; termini guard {p['term_guard']}; {p['n_control_draws']} size-matched draws (rng {p['rng_seed']}).

## Gate results
### PRIMARY - protein-level paired (n={pr['n_proteins']})
- Wilcoxon signed-rank (one-sided, resistance higher) p = **{pr['wilcoxon_greater_p']:.4g}**  (gate p<0.01)
- median dH = **{pr['median_dH']:+.4f}** nats  (gate >0)
- positive-direction fraction = **{pr['positive_fraction']:.3f}**  (gate >=0.60)
- => **{'PASS' if p['primary_pass'] else 'FAIL'}**

### SECONDARY - position-level, protein-clustered (n_res={se['n_resistance_positions']}, n_ctrl={se['n_control_positions']})
- pooled AUROC = **{se['auroc']:.4f}**  (gate >=0.60)
- clustered-permutation p = **{se['clustered_perm_p']:.4g}** ({se['n_perm']} within-protein shuffles)  (gate <0.01)
- => **{'PASS' if p['secondary_pass'] else 'FAIL'}**

### SENSITIVITY - local-context control (+/-{p['local_window']} window; NOT gated)
- median dH = **{sn['median_dH']:+.4f}** nats; positive fraction {sn['positive_fraction']:.3f}; Wilcoxon p = {sn['wilcoxon_greater_p']:.4g}.
- (Controls restricted to a window around resistance sites -> tests whether the effect survives
  local structural-context matching, addressing the active-site-clustering confound.)

## Reproduction (SHA-256 sorted-key payload, x2)
```
{repro}
```

## Ledger verdict
**{'FIRM' if firm else 'CEILING'}** - {'resistance sites are locally high-entropy at n~1162 within-protein-controlled; DYNAMICS1 becomes evidence-backed.' if firm else 'entropy does NOT locally mark resistance sites at scale; DYNAMICS1 stays a small-n demonstration and is down-tiered.'}

## Honest scope / caveats
- PLM-proxy for mutational tolerance, not a fitness measurement; in-silico.
- Confound disclosed in PREREG: resistance sites may cluster in structural contexts; the
  matched-random control handles per-protein baseline, the local-context sensitivity above
  probes context-specific enrichment.
- {p['n_resistance_positions_dropped_out_of_window']} resistance positions dropped as out-of-window in proteins > 1022 aa (reported, not fabricated).
- This firms the MECHANISM underpinning the target-level signal; NOT a validated per-target
  clinical predictor (that remains experiment-gated).
"""
open(os.path.join(HERE, "SUMMARY.md"), "w").write(md)
print("SUMMARY.md written:", verdict)
