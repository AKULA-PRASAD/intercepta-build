# Pre-registration — B52: our de novo generator on the GuacaMol goal-directed benchmark vs published SOTA (FINALIZED 2026-07-30, PRE-RESULT)

## Why (external SOTA footing for the design module; feeds the loop)
Our generator (B33 BRICS fragment-recombination GA) has only ever been scored on our own objectives. B52 places it on
the community-standard **GuacaMol goal-directed benchmark** (Brown et al., JCIM 2019) with the *exact* published scoring
functions, and compares to the published leaderboard (Graph GA, SMILES-LSTM, Best-of-Dataset). This is honest external
calibration of the design module — expected to reveal a real gap to SOTA on rediscovery (our fragment reach is
analog-level, per B42), and is deliberately un-optimistic. NO SOTA claim is anticipated.

## Data / tooling (OPEN)
`guacamol` 0.5.2 (pip, open) with a one-line compat shim (`scipy.histogram = numpy.histogram`) — goal-directed only,
no FCD/distribution-learning needed. Seed population = 3,000 ChEMBL SMILES sampled (seed=42) from
`$INTERCEPTA_DATA/tdc_gen/chembl.tab` (MANIFEST). Generator = `intercepta.generate.MoleculeOptimizer` (BRICS-GA),
wrapped as a guacamol `GoalDirectedGenerator`.

## Method (deterministic; env `docking`: guacamol + rdkit + intercepta)
Six canonical GuacaMol goal-directed benchmarks spanning rediscovery / similarity / isomer / median / MPO:
**Celecoxib rediscovery, Aripiprazole similarity, C11H24 isomers, Median (camphor/menthol), Osimertinib MPO,
Fexofenadine MPO.** For each, guacamol calls our generator with its scoring function + `number_molecules`; our wrapper
re-seeds (random+numpy=42), runs the BRICS-GA (pop = max(120, n+20), 15 generations, seed=42) over the ChEMBL seeds
with objective = `scoring_function.score`, and returns the top-`number_molecules` unique molecules. guacamol computes
the official benchmark score. Compared against **published baselines (Brown et al. 2019): Graph GA, SMILES-LSTM,
Best-of-Dataset** (hard-coded reference values, cited, ~approx across paper versions).

## Metrics & aggregate
Per benchmark: our score, and the published Graph-GA / SMILES-LSTM / Best-of-Dataset scores; gap = ours − Graph-GA.
Panel: mean of our scores vs mean Graph-GA; count of benchmarks where we ≥ Best-of-Dataset (a meaningful floor).

## Hypotheses (pre-registered; honest, un-optimistic)
- **H1 (functional optimiser):** our **mean goal-directed score across the 6 benchmarks > 0.30** — the GA genuinely
  optimises above a trivial floor. If FALSE → our generator barely optimises the standard tasks (first-class negative).
- **H2 (honest SOTA gap, expected):** our **mean score is BELOW the published Graph-GA mean** — we do NOT claim SOTA;
  quantify the per-benchmark gap and identify where we are competitive (expected: MPO) vs weak (expected:
  rediscovery/similarity, where exact reconstruction is needed and fragment reach is analog-level).
- **Reported regardless:** per-benchmark scores vs all three published baselines; how many tasks we clear the
  Best-of-Dataset floor.

## Honesty / scope
Retrospective, in-silico benchmark. Published baselines are hard-coded reference values (minor version variance noted).
Our GA outputs are computational hypotheses over KNOWN chemistry, NOT real/validated/synthesizable molecules. Six of
20 goal-directed tasks (a representative subset, not the full suite). No distribution-learning (FCD) run. NO SOTA claim.

## Reproducibility
Deterministic: ChEMBL sample seed=42, GA seed=42 + per-benchmark random/numpy re-seed, guacamol scoring deterministic.
Reproduce ×2 byte-identical (payload sha256 over summary+per-benchmark). Output:
`experiments/B52_guacamol_generator_benchmark/results/B52_metrics.json`. Env: `docking`; INTERCEPTA_DATA owned path.
