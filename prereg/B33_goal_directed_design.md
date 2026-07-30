# Pre-registration — B33: goal-directed molecular design (pipeline module #2) (FINALIZED 2026-07-30, PRE-RESULT)

## The question (honest, non-toy)
A drug-discovery platform needs a *design* stage: propose molecules that optimize a developability objective. The
honest, buildable version (no deep learning; RDKit-only) is **goal-directed OPTIMIZATION over known chemistry** via
a fragment-recombination genetic algorithm. Question: can a BRICS-fragment goal-directed GA improve a
**multi-objective developability score** (drug-likeness AND synthesizability) beyond (a) the ChEMBL seed population
and (b) a no-selection random-generation baseline — while producing VALID, UNIQUE, NOVEL molecules — AND does a
naive single-objective (QED-only) run REWARD-HACK (sacrifice synthesizability), showing the multi-objective is
necessary?

## Data (OPEN, prefetched)
Seed molecules sampled (seed=42) from the prefetched **ChEMBL** corpus (`$INTERCEPTA_DATA/tdc_gen/chembl.tab`,
1.96M drug-like molecules; sha in MANIFEST). Novelty is assessed against this ChEMBL reference set.

## Method (RDKit-only, deterministic)
- **Generator:** BRICS fragment decomposition of the current population → `BRICS.BRICSBuild` recombination →
  valid-by-construction candidate molecules (validity = 1.0 by construction).
- **Goal-directed GA:** elitist. Each generation: score population by the objective; keep top-k elites; rebuild the
  fragment pool from the top molecules (selection pressure) + generate offspring by BRICSBuild; form the next
  population from elites + offspring. G generations, fixed population size. Seeded (`random`+`numpy`, seed=42) for
  determinism; reproduce ×2 byte-identical.
- **Objective (multi-objective developability, in [0,1], higher=better):**
  `F = QED × synth`, where `synth = (10 − SAscore)/9` (RDKit QED + Contrib SAscore; both instant, no model fit).
  Also tracked separately: QED and SAscore, to expose reward-hacking.

## Baselines & metrics
- **Baselines:** (a) seed ChEMBL population best/mean F; (b) **random generation** — BRICSBuild from the full seed
  fragment pool with NO selection pressure (same total candidates), best/mean F. The GA must beat both.
- **Distribution metrics (GuacaMol-style):** validity, uniqueness, novelty (fraction of generated canonical SMILES
  not in the ChEMBL seed set).
- **Metric:** best-F and mean-F trajectory across generations; final GA vs baselines.

## Hypotheses (assumed FALSE)
- **H1 (optimization works):** GA final best-F and mean-F > random-generation baseline > seed population, with
  validity=1.0 and high uniqueness/novelty. (Improvement over generations demonstrated.)
- **H2 (multi-objective is necessary — honest insight):** a single-objective **QED-only** GA reaches high QED but
  its molecules are **less synthesizable** (higher mean SAscore) than the multi-objective GA — i.e. naive
  single-objective optimization reward-hacks; the multi-objective mitigates it. (If QED-only does NOT degrade SA,
  report that honestly — BRICS may keep molecules synthesizable regardless.)
- **H0:** GA ≈ random-generation baseline → the selection pressure adds nothing (fragment recombination alone
  explains any gain) — a first-class negative.

## Decision rule & interpretation (fixed)
- **H1 PASS** → a working goal-directed design module → SHIP `intercepta.generate.MoleculeOptimizer` + CLI
  `intercepta generate`. Report H2 (reward-hacking) honestly. **HONEST SCOPE:** goal-directed optimization of
  cheminformatics proxies (QED/SAscore) over KNOWN chemistry via fragment recombination — a *design/optimization*
  demonstration, NOT de novo discovery of real, better, or synthesizable-in-practice drugs; every output is a
  computational hypothesis, not a validated molecule.
- **H1 FAIL** → the GA does not beat random recombination → first-class negative; ship the generator as a
  library-enumeration tool only, no optimization claim.

## Reproducibility
Deterministic (seed=42; seeded `random`/`numpy`; sorted fragment lists). Reproduce ×2 byte-identical (payload
sha256). Provenance JSON. Output: `experiments/B33_goal_directed_design/results/B33_metrics.json`.
