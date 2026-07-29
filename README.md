# INTERCEPTA — Phase B build

The clean, reproducible build repository for INTERCEPTA Phase B: **transcriptomic drug-response prediction**,
built under [`CONSTITUTION.md`](CONSTITUTION.md). Separate from the exploration tree (`~/INTERCEPTA`,
`~/kaalcura`) on purpose — this repo contains only verified, reproduced, provenance-tracked work.

## What INTERCEPTA is (the honest one-sentence state)
A prognostic + mechanistic-ranking cancer engine built on **known biology**, with one verified transferable
signal (a learned cross-dataset drug-response map) and several verified mechanistic associations
(mutation→drug in AML). It is **not yet** a novel-molecule discovery or therapy-*selection* platform — those
claims were falsified or are untestable on current public data. See [`LEDGER.md`](LEDGER.md).

## Phase B goal
A validated, leakage-corrected model that predicts cancer drug response from transcriptomics, with honest
uncertainty and a known ceiling — beating the parameter-free bar and the transcriptome-only baseline, with
external replication. Nothing here claims clinical utility until a patient-transfer experiment earns it.

## The bar to beat (verified, reproduced ×2 — carried in from `~/kaalcura`)
Leakage-free cross-dataset generalization (GDSC → CCLE/PRISM, disjoint cell lines, per-drug Ridge):

| quantity | value |
|---|---|
| STRICT mean per-drug Spearman ρ | **+0.212** |
| median ρ / frac ρ>0 | +0.196 / 0.94 (94/100 drugs) |
| parameter-free R_prolif bar | +0.058 |
| paired Wilcoxon (strict vs bar) | W=214, p=1.9e-15 |

`experiments/B1_baseline_ceiling/` re-establishes this number **inside this clean repo** as the honest
starting line. Every future model is measured against it.

## Layout
```
CONSTITUTION.md   governing rules
LEDGER.md         verified/falsified/untestable findings carried forward (tiered, never blurred)
DECISIONS.md      running decision log
prereg/           pre-registration written BEFORE each experiment runs
src/intercepta/   library: data (sha256-verified loaders), splits, metrics, axes (frozen)
experiments/      one dir per pre-registered experiment; each writes results/*_metrics.json
data/MANIFEST.md  sha256 of every input; data is referenced by env var, never committed
reproduce.sh      re-run everything from clean
```

## Reproduce
```bash
pip install -r requirements.txt
export INTERCEPTA_DATA=/Users/kalki/kaalcura/data   # sha256-verified against data/MANIFEST.md
bash reproduce.sh
```
Data (GDSC/DepMap/PRISM, public) is not committed; point `INTERCEPTA_DATA` at a checkout matching the manifest.
