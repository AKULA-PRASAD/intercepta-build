# DURABLETARGETS1 — Summary

**INTEGRATION DELIVERED:** a durability-augmented multi-axis antibacterial **target-quality
scorecard** — the differentiated deliverable's capstone. Composition of committed, reproduced-×2
in-silico axes (BESTINT1 + PREDVAL + DYNAMICS2), **not new science**.

Payload SHA-256 (reproduced ×2 byte-identical): `e3a5ea141f09102175bf599802b300fed88b28dbb7f028768c5021b2756a3993`

## Coverage (honest; 19 targets)
| Axis | Covered |
|---|---|
| durability (drug-binding pocket) | 18 / 19 (ispE = NA, no pocket assigned) |
| BESTINT1 axes (D/B/R/C) | 10 / 19 |
| experimental essentiality (PREDVAL) | 10 / 19 |
| **full multi-axis + durability** | **9 / 19** (the composite core) |

Durability-only (no BESTINT1/PREDVAL axes in the committed set): murA, gyrA, parC, rpoB, rpsL, embB,
inhA, alr, ddlB — canonical drugged / non-nominated targets. ispE is a flagship core with full
BESTINT1 axes but **no drug-bound pocket → durability NA** (not imputed).

## Standalone durability ranking (18 pocket-covered, most → least durable)
`folP` · `dxr` · `murA` · `murB` · `ddlB` · `glmU` · `murG` · `mraY` · `alr` · `gyrA` · `murD` ·
`murF` · `murE` · `embB` · `parC` · `inhA` · `rpsL` · `rpoB`

The ranking is mechanistically sane: the **least-durable** targets are exactly the clinically
resistance-prone drugged targets — `rpoB` (rifampicin), `rpsL` (streptomycin), `inhA` (isoniazid),
`parC`/`embB` — all label **HIGH**; the **most-durable** are the undrugged cell-wall / MEP cores
(`murA`, `murB`, `dxr`, `ddlB`, `glmU`, `murG`, `mraY`), all label **LOW**.

## Durability-augmented composite (9 full-coverage targets; rank_withDur order)
| rank | gene | label | durN | BESTINT1 | z_noDur (rank) | z_withDur (rank) | Δrank |
|---|---|---|---|---|---|---|---|
| 1 | murB | LOW | 0.927 | 0.915 | +1.051 (1) | +0.926 (1) | 0 |
| 2 | dxr | LOW | 0.954 | 0.877 | +0.693 (3) | +0.781 (2) | **+1** |
| 3 | murG | LOW | 0.894 | 0.901 | +0.941 (2) | +0.736 (3) | **−1** |
| 4 | mraY | LOW | 0.872 | 0.804 | +0.067 (5) | +0.076 (4) | **+1** |
| 5 | murF | LOW | 0.705 | 0.872 | +0.658 (4) | −0.107 (5) | **−1** |
| 6 | murD | LOW | 0.818 | 0.794 | −0.061 (6) | −0.194 (6) | 0 |
| 7 | folP | HIGH | 0.987 | 0.634 | −1.378 (8) | −0.486 (7) | **+1** |
| 8 | murE | LOW | 0.702 | 0.776 | −0.203 (7) | −0.690 (8) | **−1** |
| 9 | glmU | LOW | 0.902 | 0.585 | −1.768 (9) | −1.042 (9) | 0 |

**Top-5 durability-augmented shortlist:** murB, dxr, murG, mraY, murF.

## DELTA from adding durability (the point of the capstone)
- **Rise:** `dxr` (+1 → #2, the most durable MEP core climbs past murG/murF), `mraY` (+1), `folP` (+1).
- **Fall:** `murF` (−1), `murE` (−1) — the two **least-durable** cell-wall ligases (highest
  drug-contact entropy among the core) drop; `murG` (−1) slips one behind the more-durable dxr.
- **Stable at top:** `murB` (#1) — durable **and** top multi-axis.

The intended signal holds: **durable cell-wall/MEP cores (dxr, murB, mraY) hold/rise; the
higher-entropy, more escape-prone ligases (murF, murE) fall.**

## Honest wrinkle (disclosed, not hidden)
`folP` rises on durability (lowest drug-contact entropy = "most durable" by the metric) yet its
resistance-liability **label is HIGH** — sulfonamide resistance is clinically real but is driven by
acquired/horizontal and target-overexpression mechanisms that a point-mutation-tolerance (contact-
entropy) proxy on a static structure does not capture. This is the durability axis's boundary,
surfaced by the scorecard rather than smoothed over. `folP` also stays low overall (bottom druggability/
breadth), so it does not enter the shortlist.

## Scope (binds every row)
Target-QUALITY triage / decision-support. Durability carries DYNAMICS's bounds: AUROC ~0.83 (n=26,
PLM-proxy, static single drug-bound structure, confound-softened strict significance); pocket-gated
(NA otherwise). Equal weights unfitted by design (no ground truth to fit). Cross-organism/ortholog-
transferred hypotheses — **not new validation, not a drug, not clinical.**

**LEDGER verdict:** INTEGRATION DELIVERED — a durability-augmented multi-axis antimicrobial
target-quality scorecard (the differentiated deliverable's capstone); composition of committed
results, not new science.
