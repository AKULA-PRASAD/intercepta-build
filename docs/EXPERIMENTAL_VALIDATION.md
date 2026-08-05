# INTERCEPTA — minimal experimental validation plan (pre-registered, 2026-08-05)

*The honest question this answers: is the computational work REAL, or noise? Everything so far is in-silico. This document
turns the method into specific, falsifiable predictions and scopes the cheapest rigorous experiments that would confirm or
kill them — no scientific corners cut. Written under the Constitution (pre-register success/falsification BEFORE the test).*

## What is under test
The one genuine positive of the whole program: **zero-data mechanistic target-ID** — FBA gene-essentiality + metabolic
chokepoint + host non-homology (composed by the substrate) identifies real, selective, essential antibacterial targets from
a genome alone, with NO drug/activity data. Everything downstream (the substrate, the "any disease → query" claim) rests on
this being true in reality, not just in-silico.

## The specific, falsifiable predictions (locked here as a pre-registration)
From *E. coli* K-12 (genome + zero drug data), the substrate's top NOVEL predictions — genes that are **FBA-essential AND a
metabolic chokepoint AND host-non-homologous (safe) AND NOT already a known drug target (ChEMBL)** — are exactly 7 genes:

| UniProt | gene | pathway | prior antibacterial-target status |
|---|---|---|---|
| P62620 | **ispG** | MEP / non-mevalonate isoprenoid | **validated target class** (host-absent, essential; active inhibitor programs — J. Med. Chem. 2015; MDPI Molecules 2023) |
| Q46893 | **ispD** | MEP / non-mevalonate isoprenoid | **validated target class** (fragment/inhibitor screening — e.g. P. aeruginosa IspD) |
| P0A7I7 | ribA | riboflavin biosynthesis | recognized target class (host-absent, essential) |
| P0A7J0 | ribB | riboflavin biosynthesis | recognized target class |
| P25539 | ribD | riboflavin biosynthesis | recognized target class |
| P0AC16 | folB | folate biosynthesis | the sulfonamide/trimethoprim pathway (definitively validated) |
| P0AF12 | mtnN | methionine salvage (MTA/SAH nucleosidase) | emerging target (quorum-sensing / methylation) |

**This is already a real, checkable result (Tier-0 literature validation, done):** the method — told nothing about drugs —
independently prioritizes genes in the MEP, riboflavin, and folate pathways, which the antibacterial field independently
pursues precisely because they are host-absent and essential. A coin-toss method does not do this.

## Tier 0 — FREE quantitative truth-test ($0; the cheapest possible experiment: our prediction vs decades of existing experiments)
Our essentiality was **predicted** (FBA). E. coli has definitive **experimental** essentiality (Baba/Keio 2006; Goodall
2018 *The Essential Genome of E. coli K-12*, mBio; PEC) and Mtb has DeJesus 2017 TnSeq. **Test:** does FBA-predicted
essentiality match experimental essentiality (precision/recall, odds ratio, AUROC), and are the 7 predicted genes
experimentally essential? **Pre-registered success:** FBA-essential genes are enriched for experimental-essential at OR > 3
(p<0.01); ≥5/7 of the predicted genes are experimentally essential. **Falsification:** no enrichment / predicted genes not
essential → the mechanism signal is weaker than claimed; report honestly and down-weight MET1–3.
**BLOCKER (honest):** the experimental gene lists sit behind journal/database navigation that resists automated download
(no institutional subscription). **The single unblocking action:** download ONE file — Goodall 2018 mBio Table S1 (essential
gene list), or register + export E. coli essentials from DEG (tubic.org/deg) / OGEE — and drop it at `$INTERCEPTA_DATA/expval/`.
Then this runs to completion in minutes. This is the highest-value, zero-cost next step.

## Tier 1 — the minimal NEW wet-lab experiment (cheapest rigorous prospective test)
**Goal:** prospectively confirm ONE prediction is a real essential (and thus a real target) — the first real-world evidence.
- **Target choice (pre-registered):** test **mtnN** (P0AF12) — the LEAST prior-validated of the 7, so a positive is a
  genuine new finding, not a re-confirmation. (Alternative de-risking choice: ispG, known-good, confirms the method works.)
- **Assay (cheapest rigorous option): CRISPRi essentiality knockdown.**
  - Reagents: an *E. coli* dCas9 CRISPRi system (Addgene, e.g. pdCas9/pgRNA; ~$65–130 total plasmids) + one target sgRNA vs
    a non-targeting-control sgRNA (oligos, ~$20) + standard media/consumables. **Total reagents ≈ $200–400.**
  - Protocol: clone target vs non-targeting sgRNA → induce dCas9 → measure growth (OD600 curve + CFU) vs control, in
    triplicate, with a known-essential positive control (e.g. ftsZ) and a non-essential negative control (e.g. a dispensable gene).
  - **Pre-registered success:** targeting sgRNA reduces growth (final OD or CFU) ≥ 5-fold vs non-targeting control (p<0.01,
    n≥3), matching the positive control's direction. **Falsification:** no growth defect → the gene is not essential under
    these conditions → the prediction is wrong; report as a first-class negative.
  - Time/skill: ~2–3 weeks, standard molecular microbiology bench.
- **Even cheaper variant (if a published inhibitor exists):** MIC/growth-inhibition assay of a commercial MEP-pathway
  inhibitor vs *E. coli* (~$50–200) — tests whether inhibiting the predicted target kills the bacterium.

## Tier 2 — the fullest-vision test (prospective, on a genuinely novel pathogen)
Apply the substrate to a newly-sequenced / emerging pathogen with NO prior known targets → produce a ranked, safe,
confidence-tiered target shortlist → a microbiology collaborator tests the top predictions (essentiality + inhibition). This
is the north-star metric ("a disease it was never trained on → credible candidates → independently validated"). Needs a
collaborator; the computational half is turnkey (the substrate).

## The decision for Prasad (minimal, ranked by leverage-per-cost)
1. **$0, ~2 min, do first:** grab one experimental-essentiality file (Goodall 2018 mBio Table S1, or DEG/OGEE export) → I run
   Tier 0 today and we learn immediately whether the core finding matches decades of experiments.
2. **~$200–400 + a bench, ~3 weeks (or a collaborating micro lab / a professor / a course):** Tier 1 CRISPRi essentiality
   test of one novel prediction (mtnN) → first prospective real-world evidence.
3. **A microbiology collaborator:** Tier 2 prospective test on a novel pathogen → the fullest-vision proof.

## Honest scope
Literature concordance (Tier 0, done) validates the method's BIOLOGY, not a specific new drug. Tier 0 quantitative + Tier 1
would be the first evidence our predictions match reality; Tier 2 is the real vision test. Until a wet-lab result exists,
the 7 predictions above are exactly that — pre-registered, falsifiable HYPOTHESES. That is the honest state, and the point of
this document is to make crossing from "rigorous computation" to "confirmed in reality" as cheap and as rigorous as possible.
