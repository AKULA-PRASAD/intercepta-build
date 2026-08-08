# PHENO1 — Phenotype -> candidate-gene retrieval front door

**Verdict: PASS** (reproduced x2 byte-identical, payload sha `c34ddeeed9e8037c4e2ec8c3af61d115c0ab02b8a85f41fe59140b3c25ea7d1d`;
identical under three different `PYTHONHASHSEED` values -> hash-order independent).

## What was built
The phenotype-**INPUT** front door the composite system was missing: a set of HPO phenotype terms -> a ranked
list of candidate causal genes, handed off to the validated genetic arms (MENDEL1 monogenic / GENETICS1 complex).
This is **honest RETRIEVAL over KNOWN HPO->gene associations** -- a validated lookup+ranking -- **NOT** de-novo
mechanism inference (that frontier stays OPEN and is explicitly not attempted).

## Source (open, cited, frozen; data only in `$INTERCEPTA_DATA/pheno1/`, never committed)
Human Phenotype Ontology release **2026-06-23** (`hp/releases/2026-06-23`):
`phenotype.hpoa` (sha `89004f85...`), `genes_to_disease.txt` (sha `a247027a...`), `hp.obo` (sha `a5092cbd...`).

## Method (pre-registered before scoring)
IC-weighted cosine over **ancestor-propagated** HPO term vectors. `IC(t) = -ln(disease-frequency of the
propagated term)`. **Leave-one-disease-out leakage control (the crux):** each gene's phenotype profile is built
from the diseases it causes MINUS the held-out test disease, so the true gene is scored only by its *other*
phenotypic manifestations, never by the disease under test. Baselines: **frequency-prior** = LODO pleiotropy
degree (the "always guess the usual-suspect genes" popularity null); **random** = analytic + permutation null.

## Result (4436 held-out diseases scored; 5524 candidate genes; 12,729 HPO terms)
| metric | ranker | freq-prior | random |
|---|---|---|---|
| recall@1 | **0.272** | 0.006 | 0.0003 |
| recall@5 | **0.447** | 0.018 | 0.0013 |
| recall@10 | **0.529** | 0.026 | 0.0027 |
| MRR | **0.357** | 0.014 | -- |

- **G1 (retrieval lift over popularity null) -- PASS.** recall@10 margin **+0.503** (required >= 0.10); MRR
  0.357 vs 0.014; per-disease reciprocal-rank improvement paired Wilcoxon **p ~ 0**; ranker MRR above the
  random-permutation null (K=10000) **p = 1.0e-4**.
- **G2 (abstention integrity) -- PASS.** Pre-registered rule (abstain if < 3 direct terms OR most-specific term
  IC below the median) abstains on **51.5%** (4706/9142). It targets genuinely harder profiles: those cases
  would score only recall@10 = 0.330 vs 0.529 on the scored set. The rule is deliberately **conservative** --
  abstained cases retain real signal (0.330 >> random), i.e. it errs toward abstaining rather than returning a
  weak ranking, consistent with abstention-integrity over coverage.
- **G3 (robustness) -- PASS.** On the **MENDELIAN-only** ground-truth subset (n=3034, the cohort feeding MENDEL1)
  recall@10 = **0.431** vs freq-prior 0.020; recall@1 lift +0.267.

## Honest bounds (reported, not hidden)
- **Singletons:** 729/4436 scored diseases (16.4%) have a causal gene seen in **no other disease** -> empty LODO
  profile -> **unrecoverable in principle**; counted as misses (they depress recall, not excused).
- **Conservative / high abstention** (51.5%): the front door produces a ranking for about half of diseases;
  the abstained half still carries recoverable signal, so the rule is safe but not coverage-maximal.
- **Scope wall:** identifies **candidate** genes only. It does not validate them, does not perform mechanism
  inference, and does not produce a molecule -- the affinity wall (HIT2/B49/B65) still gates any intervention.
  Value = a phenotype-input bridge into MENDEL1/GENETICS1.

## Reproducibility
Deterministic (seed 42; all term-set iterations sorted so floating-point summation order is
`PYTHONHASHSEED`-independent; symbol tie-breaks via sorted gene index). Payload SHA-256 over sorted-key JSON
excluding verdict/provenance; byte-identical across repeat runs and across differing hash seeds.

## LEDGER verdict (one line)
**PASS -- a validated phenotype-INPUT retrieval front door: IC-weighted HPO overlap recovers the true causal
gene at recall@10 0.53 / MRR 0.36 over 4436 LODO-held-out diseases, +0.50 above the popularity null
(Wilcoxon p~0), with a conservative pre-registered abstention (51.5%) and an honest singleton bound (16%
unrecoverable); extends the "any disease" INPUT modality into the genetic arms (MENDEL1/GENETICS1). Retrieval
over KNOWN associations, NOT de-novo mechanism inference (OPEN); candidate genes only, affinity wall stands.**
