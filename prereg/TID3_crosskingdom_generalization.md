# TID3 — Does zero-data target-ID generalize across KINGDOMS, and where does it break? (finalized 2026-08-01, PRE-RESULT)

(TID3 = Target-ID chapter 3 — the development-ladder's BREADTH step: stress-test the TID1/TID2 conservation-ceiling across disease classes / kingdoms.)

## Why (breadth as an OOD stress test, not repetition)
TID1/TID2 established, on 4 bacteria/parasite, that zero-data target-ID is dominated by generic conservation. The honest
generalization question (development ladder step 3): does this hold ACROSS KINGDOMS, and — the informative part — does
target-recovery DEGRADE when the held-out organism is phylogenetically ISOLATED from the reference (cross-kingdom
transfer, where homology weakens)? Value = mapping WHERE the pipeline breaks by class, not a uniform "it works" demo
(Thread-3 recommendation). Viruses are EXCLUDED (data-infeasible: species-level UniProt proteomes are strain-fragmented
/ near-empty — a stated honest limitation).

## Data (OPEN; UniProt reference proteomes + ChEMBL-xref targets; verified in-proteome)
7-organism panel across 3 kingdoms: **bacteria** mtb/ecoli/paeruginosa · **protozoan parasites**
pfalciparum/tbrucei/lmajor · **fungus** calbicans. Full reference proteomes (4.4k–8.6k proteins); positives = UniProt
ChEMBL-xref drug targets, verified in-proteome (mtb131/ecoli182/paeruginosa46/pfalciparum52/calbicans19/tbrucei13/lmajor12).
K. pneumoniae dropped (0 in-proteome targets — strain mismatch).

## Design (TID1's validated leave-organism-out mmseqs pipeline, over the 7-org panel + per-class analysis)
For each held-out organism X: transfer druggability via mmseqs2 homology of X's proteome to the OTHER organisms' known
drug targets; a CONSERVATION null = homology to other orgs' FULL proteomes; abstain where no homolog. Recovery of X's
known targets (AUROC, precision@k) vs random + conservation nulls. NEW: tag each organism by kingdom; compute, per
held-out organism, whether the reference contains SAME-KINGDOM organisms, and relate recovery to kingdom-isolation.

## Metrics
Per organism (as TID1): druggability AUROC, conservation-null AUROC, precision@k, abstain rate. Panel + PER-KINGDOM
medians. Cross-kingdom contrast: recovery for organisms WITH same-kingdom references (bacteria, parasites — ≥2 per
class) vs the kingdom-ISOLATED fungus (calbicans; reference all non-fungal). Abstain-rate vs kingdom isolation.

## Hypotheses (pre-registered)
- **H1 (generalizes):** the TID1 pattern holds across the 7-org panel — druggability transfer recovers known targets
  above random (precision@top), abstention calibrated; the conservation ceiling persists (druggability ≈/< conservation).
- **H2 (cross-kingdom degradation — KEY):** target-recovery (precision@k / AUROC) is LOWER for the kingdom-isolated
  fungus (and higher for organisms with same-kingdom references) → zero-data target-ID degrades cross-kingdom (homology
  weakens); maps a class-specific boundary. First-class either way.
- **H3 (abstention tracks isolation):** abstain rate is HIGHER for kingdom-isolated organisms (fewer homologs) — the
  system correctly knows it's out of its depth on distant kingdoms.
- **H0:** no cross-kingdom degradation (recovery uniform across classes) → the conservation signal transfers across
  kingdoms as well as within — also informative.

## Honesty / scope
Retrospective known-target recovery; full reference proteomes; leave-organism-out; small target-sets for the new classes
(12–19 → modest per-organism power, reported); viruses excluded (data-infeasible, stated); not wet-lab. Confirms/bounds
the TID1/TID2 ceiling's generality across kingdoms — a breadth/robustness result, not a new capability.

## Reproducibility
Deterministic (mmseqs fixed params, fixed panel, seeded sampling). Reproduce ×2 byte-identical (payload over per-organism
metrics). Output: `experiments/TID3_crosskingdom_generalization/results/TID3_metrics.json`. Env: bioinfo (mmseqs2) +
intercepta-build. Data: UniProt (MANIFEST). Smoke-test 1 held-out organism before the full panel (B63 lesson).
