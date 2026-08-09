# DYNAMICS2 — SUMMARY

**Verdict: FIRMED_UP (on the pre-registered primary) — reproduced x2 BYTE-IDENTICAL, payload sha256
`fd06702a3165498bec247ce2a24b4f6fccd6912398175e260b9b1aa0b71b5c25`.** With an explicit, honest bound:
the *effect size* firms up and generalizes across drug classes; the *strict p<0.01* is carried by the
full set and softens to the PARTIAL band under the confound-control subsets.

The FROZEN DYNAMICS1 metric (mean ESM-2 t30 150M masked-marginal contact-residue entropy) was applied
VERBATIM (same code, same params) to an EXPANDED, real, cited, drug-bound set of **n=26 targets
(14 HIGH / 12 LOW)** — DYNAMICS1's 15 reused unrelabeled + 11 new (7 antiviral/antifungal HIGH, 1
antiviral LOW, 3 bacterial LOW cores). This is an out-of-(original-)sample robustness test, not tuning.

## Pre-registered gate (frozen in PREREG.md BEFORE scoring the expanded set)
FIRMED_UP = at n>=25, **AUROC >= 0.75 AND MWU p < 0.01** (firmer than DYNAMICS1's 0.05) AND the signal
generalizes (antibacterial-only >= 0.75; cross-class does not collapse it). PARTIAL = AUROC holds but
p in [0.01,0.05). NEGATIVE = AUROC < 0.75 or drops toward chance when cross-class added.

## Result table
| analysis | n (H/L) | AUROC | MWU p |
|---|---|---|---|
| **PRIMARY mean contact entropy (gated)** | **26 (14/12)** | **0.827** | **0.0051** |
| DYNAMICS1 primary (n=15, reference) | 15 (7/8) | 0.839 | 0.029 |
| AMR1 whole-protein composite (reference) | 17 (9/8) | 0.556 | 0.74 |
| re-derivation of DYNAMICS1's exact 15 under D2 code | 15 (7/8) | 0.839 | 0.0289 |
| antibacterial-only | 18 (7/11) | 0.818 | 0.027 |
| non-antibacterial cross-class only | 8 (7/1) | 0.714 | 0.75 |
| new-targets-only (pure out-of-sample) | 11 (7/4) | 0.821 | 0.109 |
| **no-substrate (confound control)** | 21 (14/7) | 0.827 | 0.016 |
| **clinical-drug-bound only (strict confound control)** | 18 (14/4) | 0.821 | 0.061 |
| secondary MAX contact entropy | 26 (14/12) | 0.798 | 0.011 |
| secondary mean substitution-LLR | 26 (14/12) | 0.869 | 0.0016 |

## What firmed up
- **Significance crossed the firmer bar on the pre-registered primary:** p 0.029 (n=15) -> **0.0051**
  (n=26), below the pre-set 0.01. The stricter substitution-LLR variant is p 0.0016.
- **Effect size is remarkably stable:** AUROC 0.839 (n=15) -> 0.827 (n=26) despite ~doubling n and
  adding THREE new drug classes (antiviral RT/PR/NA/NS3/PA/TK, antifungal CYP51, HCV polymerase).
  AUROC sits in **0.71-0.84 across every pre-registered subset** - the signal did not collapse.
- **Generalizes to antiviral/antifungal:** 5 of 7 cross-class HIGH targets score high-entropy
  (FLU_NA 2.74, FLU_PA 2.73, HIV1_RT 2.49, HSV1_TK 2.11, HIV1_PR 1.65; CYP51 1.02 moderate). The
  frozen metric - invented on antibacterials - flags antiviral/antifungal resistance-liable targets too.
- **Mechanistic anchors present as contacts and behave as expected:** FLU_PA I38 (baloxavir I38T),
  HCV_NS3 R155/A156/D168 triad, HIV_RT K103/Y181/Y188, NA R292/N294, and HCV_NS5B S282 (durable) all
  fall in their targets' drug-contact sets; rpsL streptomycin-contact Lys entropy ~2.66 unchanged.

## Honest bounds (these bind the FIRMED_UP verdict)
- **Strict p<0.01 is NOT robust to the substrate confound.** The LOW class is enriched for
  catalytically-constrained substrate/inhibitor-bound cores (murG,murB,murD,murE,glmU) that are
  low-entropy by construction. Dropping all substrate-bound targets keeps the AUROC (0.827) but
  significance rises to **p 0.016** (PARTIAL band); clinical-drug-bound-only is AUROC 0.821 but
  **p 0.061** (only 4 LOW - badly under-powered). So the honest reading is: **effect size firms up;
  strict significance is firm on the full pre-registered set but degrades to PARTIAL once the
  substrate-contact confound and class imbalance are controlled.**
- **Two mechanistic cross-class MISSES (reported, not dropped):**
  - **HCV_NS3 - HIGH but mean entropy 0.198 (false-negative).** The rigid chymotrypsin-like
    serine-protease active site scores constrained, yet clinically it has a LOW genetic barrier
    (R155K/A156T). Static-structure PLM entropy misses functionally-tolerated escape at a
    geometrically-packed site - the same failure mode as folP (0.038) in the original set.
  - **HCV_NS5B - LOW but mean entropy 1.048 (false-positive-leaning).** The polymerase pocket has
    several tolerant contacts, so a high-genetic-barrier (durable) target scores mid.
  Within the cross-class-only view (7H/1L) these pull AUROC to 0.714 - the signal generalizes but
  is imperfect inside the antiviral class.
- **Cross-class is HIGH-skewed (7H/1L)** because clinically-worrying antiviral/antifungal resistance
  targets are predominantly HIGH; the one clear durable antiviral protein target with a drug-bound
  active-site structure (NS5B/sofosbuvir) is included. Real biology, reported openly.
- Carried from DYNAMICS1: ESM entropy is a **PLM proxy** for tolerance, NOT measured fitness; a single
  **static** structure misses induced-fit/allosteric/**efflux**/activator-loss resistance; labels are
  curated and binarized. **4WTG** (NS5B) is a crystallization construct (engineered mutations + delta8
  loop) - one contact (223) is engineered His, but S282 and the catalytic GDD are wild-type.

## Reproducibility
Deterministic CPU ESM-2 (offline cache); structures + logits under `$INTERCEPTA_DATA/dynamics2/`.
Run x2 -> identical payload sha256 `fd06702a...`. Independent cross-check: the 15 DYNAMICS1 targets were
recomputed **from scratch** (fresh logits) under DYNAMICS2's code and reproduced DYNAMICS1's committed
per-target features and its 0.839 / 0.0289 exactly (frozen-metric integrity confirmed). No git commit;
no data committed.

## One-line LEDGER verdict
FIRMED_UP (pre-registered primary, reproduced x2, sha fd06702a): expanding the FROZEN contact-residue
entropy metric to **n=26 (14H/12L)** across 4 drug classes (antibacterial + antiviral + antifungal +
HCV polymerase) holds the durability signal at **AUROC 0.827 / MWU p 0.0051** - significance crossed
the firmer p<0.01 bar (from 0.029 at n=15) and the effect size is essentially unchanged (0.839->0.827),
generalizing to antiviral/antifungal (5/7 cross-class HIGH high-entropy; sub-LLR variant p 0.0016).
BOUND: the strict p<0.01 is carried by the full set - under confound control it softens to PARTIAL
(no-substrate 0.827/p0.016; clinical-drug-only 0.821/p0.061, 4 LOW under-powered); two honest
cross-class misses (HCV_NS3 rigid-protease false-negative meanH0.20; HCV_NS5B durable false-positive
meanH1.05); ESM entropy is a PLM proxy not fitness; static structure misses efflux/induced-fit; the
effect SIZE (~0.83) is the robust, generalizing, reproduced result, not a population estimate.
