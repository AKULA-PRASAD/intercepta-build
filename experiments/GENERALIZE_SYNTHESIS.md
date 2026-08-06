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
     compresses the OR. **[CORRECTED by HARDENP1 — see below: this is GEM-topology-specific, NOT a
     host-embeddedness rule; Toxoplasma (also host-dependent) PASSES at OR 14.10.]**
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
  - **Host-dependent organisms** — *[SUPERSEDED by HARDENP1, see the CORRECTED conclusion below]* this section
    originally claimed plain FBA is categorically "the wrong signal" for host-embedded biology; Wave-4
    hardening (Toxoplasma PASS) corrected that to a **GEM-topology-specific** statement. Kept here as the
    honest record of the n=1 view that hardening overturned.

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

## THE HOST-CONTEXT CONCLUSION — CORRECTED by Wave-4 hardening (HARDENP1, n=2)
**⚠ SUPERSEDES the earlier n=1 conclusion.** After GENERALIZE5 + HOSTCTX1 + HOSTCTX2 (all on *Plasmodium*), it
looked like FBA is "the wrong signal for host-embedded biology." **HARDENP1 falsified that as a universal rule:**
a *second* host-dependent parasite, *Toxoplasma gondii* (curated iTgo2020 GEM vs Sidik-2016 CRISPR screen),
**PASSES strongly — OR 14.10, recall 0.51** — the opposite of Plasmodium (OR 2.47, recall 0.20).
- **Corrected statement:** FBA-essentiality's reach is **model/organism-specific**, governed by whether the
  *specific GEM's topology encodes genuine biosynthetic dependence* — **NOT by host-embeddedness as a category.**
  Plasmodium's failure is most plausibly iPfal19's pervasive salvage-bypass topology (the HOSTCTX1/2 root cause:
  essentials read dispensable → recall 0.20) + a high metabolic-essential base rate (0.64 vs 0.42), not
  host-dependence per se. Both GEMs run fully-open media, so it is not mere medium permissiveness.
- **Honest confound:** the two GEMs are from different curation teams and the two screens use different
  technologies (CRISPR vs piggyBac), so n=2 cannot be pinned on organism biology alone.
- **What still stands (not overturned):** DEPEND1 remains a validated functional-dependency signal for human
  cancer; TRANSFER1 still shows that signal does NOT transfer label-free to a zero-screen organism. So
  functional dependency is *a* valid host-embedded signal (where a screen exists), **and** FBA can *also* work
  on host-embedded organisms given a good-topology GEM — they are complementary, not one-replaces-the-other.
- **Router implication (COMPOSITE3, flagged not yet built):** the router's blanket host-dependent→FBA-gate is
  now too coarse (it would wrongly abstain on Toxoplasma). FBA's transfer condition is *GEM-topology quality*,
  which is not knowable a-priori for a novel organism (Plasmodium and Toxoplasma are both host-dependent, one
  fails one passes) → the honest behavior is to *attempt* FBA when a quality GEM exists but flag **elevated
  uncertainty** for host-embedded organisms, not blanket-abstain and not blanket-fire.

## Honest limits of this fusion
*[Updated after Wave 4 — see below.]* The original GENERALIZE1–5 fusion was **n=1 per class** (frontier probes,
not population claims). Wave 4 hardened each: virus→n=5 (PASS, population-grade), eukaryote/FBA→n≥2 incl. a real
fungal pathogen (PASS), host-dependent parasite→n=2 (which *corrected* the earlier rule). Standing limits: all
in-silico enrichment / prioritization, none wet-lab; virus structural is class-ID at moderate TM (0.43–0.49) on
the structured subset; fungal FBA is precise-but-narrow (rich-medium → low recall); the n=2 parasite
disagreement carries a GEM-curation/screen-technology confound. Still directional maps, now firmer.

---
## WAVE 4 — frontier hardened to n>1 per class (2026-08-05)
Each n=1 class was hardened with additional organisms (all verified: prereg-frozen, reproduced ×2).
| Class | n=1 (before) | Wave-4 additions | Hardened verdict |
|---|---|---|---|
| **Virus → structure** | SARS-CoV-2 (GENERALIZE3, PASS) | **HARDENV1**: HIV, Influenza, HCV, HSV — 7/9 targets recover correct class across all 4 (leakage-controlled) | **PASS, n=5** — the structural bridge is a genuine **cross-virus property**, not a one-off |
| **Free-living/fungal → FBA** | S. cerevisiae (GENERALIZE4, PASS) | **HARDENF1**: *Candida albicans* (real pathogen) OR 13.93, p 0.004 | **PASS, n≥2 incl. a clinical pathogen** — but precise-and-narrow (rich-medium → low recall) |
| **Host-dependent parasite → FBA** | P. falciparum (GENERALIZE5, FAIL) | **HARDENP1**: *Toxoplasma gondii* OR 14.10, PASS | **DISAGREE (n=2)** → the "FBA fails on host-embedded biology" rule is **CORRECTED** (see above): it's GEM-topology-specific |

**Net:** the two PASS classes (virus/structure, eukaryote/FBA) are now population-grade, not single probes; the
host-embedded FBA story was an n=1 overgeneralization that hardening corrected. The composite's routing table
entries are correspondingly firmer (virus, eukaryote) or honestly nuanced (host-embedded FBA = GEM-dependent,
flag uncertainty). This is hardening working as intended: two entries strengthened, one overclaim retracted.
