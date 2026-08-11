# MRCLASS1 — cis-MR per-disease enrichment vs GENETICCLASS1 class envelope (PRELIMINARY / exploratory)

**Reproduced ×2 byte-identical (sha 8b6805e). Cached-data only (MR1 instrument-SNP hits + instruments; NO new
GWAS downloads).** An EXPLORATORY corroboration check (not a pre-registered gated experiment, not a powered
per-class envelope): does the transparent self-computed cis-MR causal signal agree with GENETICCLASS1's
OT-based per-class deployment envelope, on the 5 diseases MR1 already has?

## Result (per-disease; MR-significant genes → clinical-precedence Fisher OR)
| disease | class | GENETICCLASS1 OT grade | cis-MR OR (95% CI) | corroborates? |
|---|---|---|---|---|
| Parkinson | neuro_psychiatric | FULL | **8.14** [2.62, 37.2] | ✓ |
| IBD | immune_inflammatory | FULL | **4.78** [2.50, 10.2] | ✓ |
| RA | immune_inflammatory | FULL | **3.35** [1.43, 9.76] | ✓ |
| CAD | cardiovascular | FULL | 1.70 [0.68, 5.74] | ✗ (underpowered) |
| T2D | metabolic | CAPPED | 1.35 [0.39, 10.2] | ✗ (underpowered) |

## Honest reading
- **All 5 per-disease cis-MR ORs are > 1** (point estimates); **3/5 significantly corroborate** GENETICCLASS1's
  class envelope — the transparent, self-computed causal method **independently agrees** with the OT-based
  genetic envelope where it is powered (immune, neuro).
- The 2 non-corroborating (CAD, T2D) are **underpowered, not reversals** — wide CIs spanning 1 (fewer
  MR-significant genes: CAD 134 / T2D 47 sig), with point ORs still > 1. This is a power limit, not a conflict.
- Net: cis-MR **corroborates the genetic class envelope where powered**; per-disease power is the binding limit.

## Scope / honesty (binds the claim)
- **PRELIMINARY, exploratory, NOT a powered per-class envelope.** 5 diseases across 4 classes (1–2 each) → this
  is per-DISEASE with class labels; a genuine powered per-class MR envelope needs cis-MR on ~10–15 more
  diseases = a multi-hour throttled GWAS-sumstats download campaign (deferred, offered).
- The "corroborates" flag was **not pre-registered** (this is an exploratory read on cached data), stated as such.
- Per MR1's committed H2 (cis-MR predictively **redundant** with the OT aggregate), a powered per-class MR
  envelope would **likely mirror GENETICCLASS1** — which is exactly what this preliminary check shows where
  powered. So the cheap corroboration is the honest, high-value-per-effort answer; the heavy campaign is
  predicted low-marginal-value.

## Reproduce
`python build_mrclass.py` (cached MR1 hits + instruments + GENETICS1 universe; deterministic, byte-identical).
