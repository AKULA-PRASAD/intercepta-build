# B64 — End-to-end discovery demonstration on FEN1 (payload `739f5230`)

**What this is:** a single, reproducible run of the *whole* INTERCEPTA computational pipeline, composed end-to-end on
one real disease target, producing a ranked and calibrated candidate shortlist. It is a **capability demonstration**,
not a hypothesis test, and its output is a set of **ranked computational hypotheses — NOT validated actives, NOT drugs,
no wet-lab, no prospective confirmation.**

## Target: FEN1 (flap endonuclease 1)
A structure-specific nuclease essential to DNA replication/repair; a synthetic-lethality / DNA-damage-response
**oncology** target. Chosen deliberately for honesty, not cherry-picking: across our whole benchmark panel, FEN1 has the
**strongest doubly-controlled ligand signal** (B45 novel-chemistry residual AUROC ≈ 0.80). We demonstrate on the target
where the activity channel is *most real*, not one where enrichment is similarity-inflated.

## The pipeline, composed (every stage a previously-validated module)
1. **Activity QSAR** — LIT-PCBA FEN1 (360 actives + 10k seeded inactives), Morgan-1024 → HGB, Tanimoto applicability
   domain (AD) + Mondrian conformal. [B30/B42/B45]
2. **Target-conditioned generation** — BRICS genetic algorithm maximizing a composite objective
   `F = QED × synthesizability × predicted-safety × P(FEN1-active)` over a seeded ChEMBL seed set (pop 60, 8 gens). [B33/B40]
3. **Multi-channel scoring** — per candidate: P(FEN1-active) + conformal set + AD flag; safety = 1 − mean(hERG, AMES,
   DILI) [B30]; synthesizability solvable-prob [B31]; QED; SA score; composite developability F. [B39/B40]
4. **Ranked, honestly-annotated shortlist** — `results/B64_shortlist.csv`, top-20 by F, each flagged reliable vs
   low-confidence and tagged with nearest-known-active Tanimoto + novel-chemistry status.

## Validation reported up front (so the demo is honest before it ranks anything)
| Metric | Value |
|---|---|
| FEN1 QSAR held-out AUROC (random 80/20) | **0.941** |
| FEN1 QSAR held-out AUROC (scaffold-disjoint) | **0.960** |
| FEN1 novel-chemistry doubly-controlled residual (B45 ref) | ≈ **0.80** |

The generation loop measurably optimized the objective: best composite fitness 0.14 → 0.31, mean population fitness
0.003 → ~0.05 over 8 generations.

## Result — and why the honesty IS the result
20 candidates; **only 3 flagged reliable (in-domain)**, 19 are novel chemistry the model marks *"out-of-domain — do not
trust the activity call."* The high-`p_target_active` (0.90+) candidates are almost all out-of-domain, and their
conformal sets are mostly empty `{}` (the model declines to commit). The reliable in-domain candidates sit near known
chemistry (nearest-active Tanimoto ≈ 0.34–0.42), e.g. the top-ranked `O=C(O)c1ccc(O)c(O)c1` (protocatechuic-acid-like;
p_active 0.785; low predicted hERG/AMES/DILI).

This is the point: **the platform doesn't just generate molecules — it reports what it cannot trust.** That behavior is
the direct product of our theory line (P2 similarity-inflation; P9 / B60–B62 that novel-chemistry extrapolation is an
information ceiling): honest calibrated confidence instead of false novel "hits." A pipeline that confidently ranked the
0.90+ out-of-domain molecules as leads would be lying; this one flags them.

## Honest scope (binding)
Retrospective, in-silico, open data only. `p_target_active` is a QSAR probability, **not measured activity** (enrichment
is ~half bias, P2). Generated molecules are BRICS recombinations of known chemistry. Only in-domain predictions are
trustworthy; out-of-domain candidates are shown but must not be treated as leads. This demonstrates a **usable
computational hypothesis engine**, not a drug — the drug still requires wet-lab validation, which is resource-gated and
is a human decision, not a computation.

## Reproduce
```
INTERCEPTA_DATA=/path/to/data  python experiments/B64_endtoend_fen1_demonstration/run.py
# deterministic; payload sha256 over {validation + full shortlist} = 739f5230..., reproduced x2 byte-identical
```
