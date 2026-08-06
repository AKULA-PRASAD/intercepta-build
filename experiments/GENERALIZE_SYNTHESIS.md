# GENERALIZATION FRONTIER — fused verdict (GENERALIZE1–5)

*Does the label-free discovery method generalize beyond bacteria toward the North Star's "any disease,
including emerging"? Fusion of five committed, reproduced-×2, prereg'd experiments. 2026-08-05.*

## The five results
| Test | Disease class | Signal tested | Gate | Result |
|---|---|---|---|---|
| GENERALIZE1 | Virus (SARS-CoV-2) | **Sequence** homology → drug | both targets top-5 w/ real homolog | **FAIL** — 0/30 any homolog (cross-family sequence below detection) |
| GENERALIZE2 | Virus | **Structure** (Foldseek TM), confirmatory | correct class @ TM≥0.4 | **PASS** (hand-picked controls) |
| GENERALIZE3 | Virus | **Structure**, BLIND multi-class | both targets correct-class + top-half | **PASS** — Mpro→protease, RdRp→polymerase |
| GENERALIZE4 | Eukaryote (*S. cerevisiae*) | **FBA-essentiality** | OR>3 & p<0.01 | **PASS** — OR 4.65, p 1.6e-10 |
| GENERALIZE5 | Parasite (*P. falciparum*) | **FBA-essentiality** | OR>3 & p<0.01 | **FAIL** — OR 2.47 (p 0.0022, sub-threshold) |

## Fused verdict (the honest frontier)
**The method generalizes across disease classes — but NOT uniformly, and the *correct signal differs by class*.
It is not one algorithm; it is a family of label-free signals, and generalization depends on matching the
signal to the organism's biology.**

1. **FBA-essentiality's reach is governed by how self-contained the organism's metabolism is.**
   - Free-living **bacteria**: STRONG (validated, OR 5–64 across 6 organisms + prospective-blind). 
   - **Eukaryote/fungus** (yeast): TRANSFERS but weaker (OR 4.65) — crosses the prokaryote/eukaryote divide.
   - Host-dependent **parasite** (malaria): FAILS the bar (OR 2.47) — host-salvage metabolism makes
     default-medium GEMs over-permissive (recall collapses to 0.20) and a high metabolic-essential base rate
     compresses the OR. **Boundary found: the more host-embedded the metabolism, the worse FBA does.**
2. **Where metabolism cannot carry the signal, STRUCTURE can.** Viruses have no metabolism → FBA is
   inapplicable, and *sequence* homology to drugged proteins is below detection (GENERALIZE1). But **blind
   structural homology (Foldseek TM) recovers the correct drugged class for both approved SARS-CoV-2 targets**
   (GENERALIZE3) — a *different* label-free signal for a *different* disease class.

## What this means for the North Star ("any disease")
- **Partially and honestly supported.** The approach demonstrably extends beyond bacteria (eukaryote PASS,
  virus structural PASS), but requires **class-appropriate signal selection** and **degrades with
  host-dependence**. This is neither the over-claim ("works for any disease") nor the under-claim ("bacteria
  only"). It is a *map*: signal ↔ organism biology.
- **Direct, evidence-based Wave-2 implications:**
  - **Viruses** → the route is structure; build a proper corona-free *viral* PDB structure reference and make
    the blind structural screen a first-class engine module (resolve the AF-DB-excludes-viruses boundary).
  - **Host-dependent organisms** (parasites — and by extension intracellular pathogens, and ultimately human
    disease/cancer): plain FBA-essentiality is the **wrong or insufficient signal**. They need
    **host-context-aware modeling** (context-/expression-constrained GEMs, host-embedded media) or a different
    reasoning layer. This is exactly the gap the human/oncology line (V-series, mostly weak/single-cohort)
    already hinted at.

## Host-context wall — attack #1 (HOSTCTX1, E-Flux): the wall is STRUCTURAL, not flux
The parasite FAIL (GENERALIZE5) was diagnosed as host-salvage "workarounds" making the default-medium GEM
over-permissive. **HOSTCTX1 tested the first fix — expression-constrained context-specific FBA (E-Flux) — in a
clean controlled A/B (same GEM/truth/gate; only variable = blood-stage transcriptomics). Result: NEGATIVE,
verified, reproduced ×2 (sha a3c5c3c2), robust across 6 scaling variants.** E-Flux left the essential set
byte-identical (OR unchanged 2.47).

**Why it matters (mechanism, not excuse):** single-gene essentiality is governed by **GPR bypass topology**
(can biomass route around the deletion?), *not* by flux magnitude. E-Flux throttles reaction *capacities* but
never *shuts* an expressed reaction, and the salvage workarounds are themselves expressed — so they stay
topologically usable however you down-weight them. **The malaria wall is a property of network *content/
boundary* (which reactions and exchanges exist), not of the *regulatory state* (which genes are on).**

## Host-context wall — attack #2 (HOSTCTX2, exchange/medium curation): partial, still NEGATIVE
Restricting imports to a host-RBC-available set (frozen from published RPMI-1640 + salvage-biology citations;
anti-circularity enforced; precision-collapse guard) **does move the essential set — recall 0.20→0.30 (+28 true
essentials)** — unlike E-Flux. But it adds proportional false positives, so **OR stays flat (~2.43, still <3,
not even above baseline): NEGATIVE, robust across 3 a-priori media, verified reproduced ×2 (sha e1fa792d).**
190 experimentally-essential genes remain FBA-dispensable (residual topology bypass), and iPfal19 lacks
de-novo lipid biosynthesis (a GEM-content ceiling). Boundary curation is *directionally correct but
insufficient*.

## THE UNIFIED HOST-CONTEXT CONCLUSION (three negatives: GENERALIZE5 + HOSTCTX1 + HOSTCTX2)
Plain FBA, expression-context FBA, and boundary-curated FBA **all** fail to clear the bar on the host-dependent
parasite. The wall is not a tuning problem — it is **the wrong signal for host-embedded biology**:
metabolic-essentiality assumes a self-contained metabolism, which host-dependent organisms (parasites →
intracellular pathogens → human cells/cancer) do not have. Patching the GEM (medium, expression, even
compartment modeling + a de-novo-lipid model) has sharply diminishing returns.
**Real redirection (not more FBA patching):** host-embedded target discovery should pivot to a
**functional-dependency reasoning layer** — context-specific dependency signals (CRISPR/knockout fitness),
which is exactly what the human/oncology line's most promising result already uses (V15–V18: expr→CRISPR
dependency rescues FLT3/BCL2 where metabolic/transcriptomic signals fail). **This unifies the parasite wall
with the human-disease route: for host-embedded systems, dependency > metabolic essentiality.** That is the
evidence-based direction for the host-embedded half of the North Star (see FAILURE_AUDIT F2↔F3).

## Honest limits of this fusion
Each class is **n=1** (one virus, one yeast, one parasite) — these are *frontier probes*, not population claims.
All are in-silico enrichment / prioritization; none is wet-lab. The eukaryote is a model organism, not a
fungal pathogen. The virus structural result is the 21/30 structured subset at moderate TM (0.43–0.49). The
conclusions above are directional maps to be hardened with more organisms per class, not settled facts.
