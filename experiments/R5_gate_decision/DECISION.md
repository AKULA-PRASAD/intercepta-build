# R5 gate decision — CLOSED (molecule-half heavy compute NOT authorized)

*R5 (roadmap): heavy compute on the molecule/affinity half is authorized ONLY if a method cleanly beats the
extrapolation wall on a leakage-free novel split. This is the adjudication of that gate. 2026-08-10.*

## Gate status: NOT MET → R5 stays CLOSED
R2/R3 (corrected, artifact-controlled) → 5/7 WALL_HOLDS; 2/7 marginal (PKM2 +0.13, ALDH1 +0.10 over an
8-descriptor property baseline). Adjudicated those 2 with a **stricter novelty threshold (Tanimoto <0.3)** and
a **stronger 15-descriptor property control** (`r5_gate_adjudication.py`, reproducible):

| target | nn< | n_novel_act | ECFP | ECFP CI-lo | PROP15 | ECFP−PROP | verdict |
|---|---|---|---|---|---|---|---|
| PKM2  | 0.4 | 68 | 0.790 | 0.728 | 0.678 | +0.112 | survives |
| PKM2  | 0.3 | 30 | 0.807 | 0.717 | 0.702 | +0.105 | survives |
| ALDH1 | 0.4 | 327 | 0.694 | 0.661 | 0.615 | +0.079 | CLOSED |
| ALDH1 | 0.3 | 91 | 0.693 | 0.632 | 0.616 | +0.077 | CLOSED |

- **ALDH1 CLOSED:** the stronger control absorbs the residual (gap <0.10).
- **PKM2 marginally survives** but is **(a) a single target, (b) a small effect (~+0.10), and (c) still
  confounded** — ECFP is a richer representation than any fixed descriptor set, so it can out-classify a
  property model without learning target-specific binding.

## Decision
**Do NOT open R5** (no heavy novel-target affinity/generation compute — that remains the proven money-pit,
dead-ends D2/D5). The evidence does not show a method cleanly beating the wall; it shows one single-target,
confounded, marginal residual. Heavy molecule-half investment is unjustified.

## The ONE legitimate follow-up (a bounded R2/R3 refinement, not R5)
Test whether PKM2's residual is genuinely **target-specific**: a **target-agnostic "generic-activeness"
control** — train an ECFP classifier on *other* targets' actives-vs-inactives and see if it also separates
PKM2's novel actives. If yes → the residual is generic ECFP separability, not binding → PKM2 CLOSED too. If
no → a genuine, if tiny, target-specific novel-chemotype signal worth a deeper look. Either way it is a cheap
instrument refinement, **not** authorization to build the molecule half.

---
## FINAL (target-agnostic control) — PKM2 CLOSED → R5 DEFINITIVELY CLOSED
The clean control (`r5_gate_adjudication` follow-up): a **generic-activeness** ECFP model trained on **6 OTHER**
LIT-PCBA targets (never saw PKM2) scores PKM2's novel-split actives (nn<0.3, n_act=30) at AUROC **0.731**;
the PKM2-trained model scores **0.806** → **target-specific advantage only +0.076 (<0.10)**. PKM2's residual
is therefore **generic ECFP separability, not target-specific binding**.

**Both marginal candidates CLOSED. R5 is DEFINITIVELY CLOSED:** across the full powered LIT-PCBA panel, **no
target-specific novel-chemotype extrapolation signal survives** rigorous property + target-agnostic controls.
The extrapolation wall HOLDS. No compute is authorized for the molecule half (dead-ends D2/D5 stand). The
only path that opens R5 is a future model/dataset that clears this same gate — which R2/R3 will auto-detect.
