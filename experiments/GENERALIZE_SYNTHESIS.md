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
- **Corrected statement:** FBA-essentiality's reach is **model/organism-specific** — **NOT determined by
  host-embeddedness as a category** (a host-dependent parasite, Toxoplasma, passes strongly).
- **⚠ Confound partially resolved + a mechanism CORRECTION (PARARESOLVE1, 3487e6c):** a controlled GEM swap
  (same organism *Plasmodium*, same Zhang screen, different independent GEMs) shows the **GEM axis is a major
  driver** — six Pf reconstructions span OR 0.86→3.07; iPfal19 (2.47) is mid-pack, and the independent
  iAM-Pf480 **passes** (3.07) → the failure is not uniquely iPfal19, and GEM choice can flip fail↔pass. **BUT
  GEM choice does NOT close the Plasmodium↔Toxoplasma gap** (best Pf 3.07 vs Toxo 14.10; the two independent Pf
  GEMs disagree; base rate is GEM-invariant ~0.65 vs Toxo 0.42) → a **base-rate/biology residual survives.**
  **And the specific "salvage-bypass topology" mechanism I earlier attributed to iPfal19 is FALSIFIED** — the
  salvage-explained false-negative fraction is iPfal19 0.907 ≈ iTgo2020 0.867 (Toxoplasma's false-negatives are
  *also* salvageable); the PASS/FAIL difference is recall/FN-count, not a qualitatively different salvage
  topology (caveat: fully-open media saturates the salvage category, limiting its discriminating power).
- **Screen-technology axis — PROBED (PARARESOLVE2, ebd2771), no closure:** the clean same-species-CRISPR test
  is data-gated (no genome-wide *Plasmodium* CRISPR screen exists), so it was probed with a 3rd technology
  (Bushell 2017 *P. berghei* barseq-knockout). Result: the **pass/fail VERDICT is NOT screen-tech-robust** —
  iPfal19 flips to PASS (3.67) and iAM-Pf480 flips to FAIL (2.26) vs Bushell, opposite to their Zhang verdicts
  → the tech axis is **not exonerated**. **BUT the FAILURE MECHANISM IS screen-tech-robust:** recall stays
  ~0.19–0.25 across every GEM×screen cell (FBA misses ~75–80% of essentials — the invariant signature).
- **The sharpened conclusion (this reframes the whole parasite story):** the OR>3 gate is **knife-edge at
  Plasmodium's noise floor** — the verdict flips are largely a **base-rate artifact** (Bushell essential base
  rate ~0.46 vs Zhang 0.64 mechanically decompresses the OR, lifting a GEM over the line *without the model
  improving*). So "Plasmodium FBA passes/fails" is **not a stable single-fact**; it is multi-causal (GEM
  topology × truth base-rate × screen sampling). What *is* stable and honest: **Plasmodium FBA is near the
  noise floor (recall ~0.2) regardless of GEM/screen, whereas Toxoplasma is robustly strong (recall 0.51, OR
  14.10) — the Pf↔Toxo gap never closes** (best Pf 3.67 vs 14.10).
- **Residual confounds still UNRESOLVED:** CRISPR-*specific* axis (data-gated); *P. berghei*→Pf species
  confound; partial-genome coverage; base-rate/biology residual; Pf-GEM knowledgebase non-independence.
- **What still stands (not overturned):** DEPEND1 remains a validated functional-dependency signal for human
  cancer; TRANSFER1 still shows that signal does NOT transfer label-free to a zero-screen organism. So
  functional dependency is *a* valid host-embedded signal (where a screen exists), **and** FBA can *also* work
  on host-embedded organisms given a good-topology GEM — they are complementary, not one-replaces-the-other.
- **Router implication — ✅ BUILT (COMPOSITE3, router v3, b1021ae):** the blanket host-dependent→FBA abstention
  was too coarse (wrongly refused Toxoplasma). v3 fires FBA for a host-dependent organism *with a curated GEM*
  at **capped confidence (0.5) + an explicit uncertainty flag** (GEM-topology-dependent, n=2 Toxo-PASS/
  Plasmodium-FAIL), abstains only when no signal (no GEM), and leaves functional-dependency parasite behavior
  unchanged (TRANSFER1). Verified 17/17 tests, reproduced ×2. Honesty kept: an advisory GEM-topology descriptor
  was included but *demonstrated not to separate pass from fail a-priori* (the failing organism has the lower
  essential fraction) → labeled non-predictive, never gates. The router now ADMITS it cannot predict FBA
  reliability a-priori on a novel host-dependent organism — it flags uncertainty rather than pretending.

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
