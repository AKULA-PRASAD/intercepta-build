# Pre-registration — B25: does more diverse open data fix B24's weak synergy generalization? (FINALIZED 2026-07-29, PRE-RESULT)

## The question (fixing a FIXABLE weakness, per WEAKNESS_AUDIT)
B24 showed synergy generalizes strongly to unseen combinations of *known* drugs (leave-combination-out ρ=0.61) but
only weakly to **novel drugs** (leave-drug-out ρ=0.25) — root-caused to limited chemical diversity (38 drugs). The
honest, buildable fix: re-run on the larger open **DrugComb** corpus (124 drugs, 41 DepMap-mapped cell lines,
207k measurements) and test whether the *novel-drug* generalization improves. This is a genuine design/data fix on
open data — not re-litigating an intrinsic limit.

## Data (OPEN — DrugComb via TDC; cell features from local DepMap expression)
drugcomb_synergy.parquet (Drug1_ID, Drug2_ID, Cell_ACH, Synergy_Loewe; 207,195 rows, 5,618 pairs, 124 drugs, 41
cells mapped to DepMap). Target: Synergy_Loewe (DrugComb; note its distribution differs from O'Neil — mean ≈ −9,
so we rely on Spearman/ranking, not an absolute-threshold class). Features: cell = DepMap expression PCA (≤20
comps, fit on the 41 cells); drug = order-invariant Morgan fingerprints (sum + bitwise-AND). Model:
HistGradientBoostingRegressor, deterministic seed=42. (Rows may be subsampled with a fixed seed to bound runtime;
the subsample preserves all 124 drugs and 41 cells — reported in results.)

## Splits & baselines
- Leave-drug-COMBINATION-out (grouped 5-fold by pair) — reference; baseline = drug-marginal mean.
- **Leave-DRUG-out (124 drugs partitioned; test = pairs with BOTH drugs held out) — the fix test**; baseline =
  global mean (drug unseen).
- Leave-cell-line-out (grouped by cell) — expected still weak (41 cells ≈ B24's 39; honest).

## Hypotheses (assumed FALSE)
- **H1 (the fix works):** DrugComb leave-drug-out Spearman ρ(pred, Loewe) **> B24's 0.25** (novel-drug
  generalization improves with more chemical diversity), and > 0 with bootstrap CI excluding 0.
- **H2:** leave-combination-out generalizes (ρ>0, beats drug-marginal baseline) — sanity that the larger corpus
  behaves consistently.
- H0: leave-drug-out ρ ≤ 0.25 (no improvement) → novel-drug synergy generalization is intrinsically limited, not a
  data-diversity artifact — an honest bound that reclassifies this weakness from FIXABLE to INTRINSIC.

## Decision rule & interpretation (fixed)
- **H1 PASS** → the weakness was data-diversity-limited and is genuinely improved by more open data → a real fix;
  strengthens the combinations arm and its usefulness for prioritizing novel combinations.
- **H1 FAIL** → honest: novel-drug synergy generalization does not improve with ~3× the drugs → the B24 leave-drug
  weakness is closer to intrinsic; update WEAKNESS_AUDIT accordingly. First-class either way.
- Cross-corpus note: DrugComb Loewe ≠ O'Neil Loewe in scale/definition, so ρ magnitudes are compared as
  *generalization quality within each corpus*, not as identical numbers.

## Honesty / scope
Cell-line synergy (not clinical). Cell diversity is only modestly larger (41 vs 39) so leave-cell-out is not
expected to improve — the honest, targeted claim is about *drug/chemistry* diversity. Subsampling (if used) is
seeded and reported. A null is fully expected and first-class.

## Reproducibility
Deterministic (seed=42); reproduce ×2. Output: experiments/B25_synergy_scaleup/results/B25_metrics.json.
