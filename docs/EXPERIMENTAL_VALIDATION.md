# INTERCEPTA — experimental validation plan & collaboration ask (updated 2026-08-07)

*The honest question this answers: is the computational work REAL, or noise? This document turns the method into specific,
falsifiable predictions and scopes the cheapest rigorous experiments that confirm or kill them — no corners cut. Written
under the Constitution (pre-register success/falsification BEFORE the test). **This is also the concrete collaboration ask:
the computational half is done and validated as far as is possible without a lab; the one thing needed is a wet-lab partner
to cross into reality.***

## ⭐ Evidence now in hand (what changed since the original 2026-08-05 plan — the collaboration lead)
The original "Tier 0" below fretted about *downloading* experimental essentiality data. **That blocker is gone and Tier 0
is DONE and massively exceeded** — lead any collaborator/reviewer with this:
- **Computational validation against decades of lab experiments, across 6 organisms / 3 phyla** (VAL-ESS/CROSSVAL): FBA
  gene-essentiality is enriched for *experimental* gene-knockout essentiality at odds ratios **5–64**, all clearing a
  pre-registered OR>3 gate (E. coli 44.9, K. pneumoniae, Salmonella, B. subtilis, S. aureus/MRSA, M. tuberculosis).
- **A prospective-blind SUITE of 4 never-seen pathogens across multiple phyla** (BLIND1–4; predictions locked — 3 of them
  git-committed — *before* the experimental answer was consulted): **3 of 4 PASS** — *N. gonorrhoeae* OR 6.1, *C. jejuni*
  OR 3.9, *B. thetaiotaomicron* (a new phylum) OR 8.0; the 4th (*S. pneumoniae*, OR 3.0) **failed on a sparse de-novo model
  and is reported first-class**. This is the strongest "predicts, not postdicts" evidence obtainable without a wet lab.
- **A ranked, actionable flagship target list** (`FLAGSHIP_TARGETS.md`): validated targets split into *repurposing-ready*
  (already-drugged, testable now) vs *undrugged high-value* (novel-chemistry frontier).
So the method's *biology* is validated to the strongest possible in-silico degree. **The remaining gap is a single wet-lab
rung** — the experiments below — which is exactly what a collaborator provides.

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
**✅ RESOLVED — Tier 0 is DONE and exceeded (the original blocker is obsolete).** The experimental essentiality data was
obtained (PEC, DEG, DeJesus, Goodall/Keio, CRISPRi) and the test run across 6 organisms + the 4-pathogen prospective-blind
suite (see "Evidence now in hand" above): FBA-essential genes are enriched for experimental essentiality at OR 5–64
(6/6 curated organisms) and 3/4 prospective-blind pathogens clear the gate. 6/7 of the E. coli predicted genes above are
experimentally essential (mtnN is the confirmed false positive — salvage redundancy). The core finding matches decades of
experiments. Tier 0 no longer requires any action; it is committed and reproduced ×2 in the LEDGER.

## Tier 1 — the minimal NEW wet-lab experiment (cheapest rigorous prospective test)
**Goal:** prospectively confirm ONE prediction is a real essential (and thus a real target) — the first real-world evidence.
- **Target choice (pre-registered; refined by BROADSPEC cross-bacteria robustness):** the substrate's top predictions by
  BREADTH (essential ortholog across N/7 bacteria) are **ispG (4/7) and ispD (4/7)** — both MEP/isoprenoid pathway,
  independently literature-validated AND broad-spectrum → the **highest-value, most de-risked** test (confirming one
  validates a broad-spectrum target). **mtnN (3/7, methionine salvage)** is the least prior-validated → a positive there is
  a genuinely novel finding. Recommended: test **ispG** (broadest-spectrum, highest value) first; **mtnN** for novelty.
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

## The decision (minimal, ranked by leverage-per-cost) — updated
1. ~~grab an essentiality file~~ **✅ DONE** — Tier 0 completed and exceeded (6 organisms + 4-pathogen prospective-blind suite).
2. **~$200–400 + a bench, ~3 weeks (a collaborating micro lab / a professor / a course):** Tier 1 CRISPRi essentiality test
   of ONE nominated target → the first *prospective wet-lab* rung. Most de-risked pick: **ispG/ispD** (broad-spectrum,
   MEP-pathway, literature-corroborated); highest-novelty pick: a target we nominated **prospective-blind** in the BLIND
   suite (e.g. a *C. jejuni* or *B. thetaiotaomicron* FBA-essential gene from the locked, gate-passing predictions) — a
   knockdown growth-defect there would confirm a *blind* computational prediction in the lab, the strongest single result.
3. **A microbiology collaborator:** Tier 2 prospective test on a genuinely novel pathogen → the fullest-vision proof (the
   composite/`intercepta route` produces the ranked, abstaining shortlist turnkey; the lab tests the top calls).

**The ask, in one sentence:** the method is computationally validated to the strongest degree possible without a lab
(6 organisms + 3/4 prospective-blind across phyla); a single ~$300, ~3-week CRISPRi experiment on one nominated target
converts it into the first real-world confirmation — that is the highest-leverage step toward the fullest vision, and it is
the one thing computation cannot do alone.

## Honest scope
Literature concordance (Tier 0, done) validates the method's BIOLOGY, not a specific new drug. Tier 0 quantitative + Tier 1
would be the first evidence our predictions match reality; Tier 2 is the real vision test. Until a wet-lab result exists,
the 7 predictions above are exactly that — pre-registered, falsifiable HYPOTHESES. That is the honest state, and the point of
this document is to make crossing from "rigorous computation" to "confirmed in reality" as cheap and as rigorous as possible.
