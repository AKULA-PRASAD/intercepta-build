# DYNAMICS5 — Pre-Registration (locked BEFORE any ESM scoring)

*Firm the resistance-durability MECHANISM past DYNAMICS1's n-fragility (n=15) using a large,
open, position-resolved resistance-mutation set (CARD) and a clean within-protein paired design.
Locked 2026-08-09.*

## The result being firmed, and its prior fragility
DYNAMICS1 found: mean ESM-2 masked-marginal entropy over drug-CONTACT residues is higher for
resistance-liable targets (AUROC 0.84) — but **n-fragile** (n=15 targets; subset p 0.05–0.12; a
demonstration, not a validated predictor). The weakness was the TARGET-level label: a clean
"LOW-liability target" set is hard (absence of documented resistance ≠ low liability).

## The genuinely stronger design (why this firms it honestly)
Instead of a noisy LOW-target set, test the **mechanistic sub-claim at the position level**, where
each protein is its OWN control: **do documented resistance-conferring positions carry higher
masked-marginal entropy (more mutational tolerance) than non-resistance positions in the SAME
protein?** If the durability mechanism is real, resistance sites should be locally high-entropy.
This sidesteps the LOW-target problem and scales n by ~80×.

## Data (STAGED + WT-verified, LOCKED) — CARD protein variant model
- Source: CARD `card.json` (card.mcmaster.ca, fetched 2026-08-09 → `$INTERCEPTA_DATA/card/`, NOT committed).
- HIGH-liability = **protein-variant-model** targets = resistance arises by **target mutation** (target
  alteration) — the correct scope for TARGET durability (acquired/efflux homolog-model genes EXCLUDED).
- Positions = CARD `model_param.snp.param_value`, format `[WT][pos][mut]`, kept ONLY where the stated
  WT residue matches the reference sequence at that position (sanity filter already applied).
- Staged set: **198 targets, 1,162 WT-verified resistance positions** (`dynamics5_high_targets.json`),
  sequences from CARD's variant-model reference (WT-verified). Median length 488.

## Metric (LOCKED — identical FROZEN metric to DYNAMICS1–4)
- ESM-2 **`facebook/esm2_t30_150M_UR50D`** (same model as the whole DYNAMICS arc — comparability), CPU,
  deterministic eval. Per position i: mask i, softmax over the 20 standard AA at i, **Shannon entropy**
  (masked-marginal). 1022-residue windowing verbatim from DYNAMICS1. Cached to
  `$INTERCEPTA_DATA/dynamics5/ent_<aro>.npy` → downstream scoring byte-reproducible.
- Entropy is computed **BLIND to the resistance labels** (whole-sequence entropy profile), THEN compared
  → non-circular.

## Control positions (LOCKED, anti-bias)
For each protein: the resistance positions vs a **size-matched RANDOM control** set of non-resistance
positions (same count, drawn with `np.random.default_rng(0)`, averaged over **20 draws**), excluding
the 5 N/C-terminal residues (termini are artefactually high-entropy). Reported alongside: the
all-other-positions baseline (sensitivity, not gated).

## PRE-REGISTERED GATE (decisive)
- **PRIMARY (protein-level paired):** per protein, mean entropy at resistance sites − mean entropy at
  matched-control sites (ΔH). Across the 198 proteins: **one-sided Wilcoxon signed-rank p < 0.01**
  (resistance higher) **AND median ΔH > 0 AND the positive-direction fraction ≥ 0.60**.
- **SECONDARY (position-level, protein-clustered):** pooled AUROC of entropy discriminating resistance
  vs non-resistance positions ≥ **0.60**, with a protein-**clustered permutation** null (shuffle
  labels within protein, 2000×) giving p < 0.01 (guards against protein-level confounding).
- **PASS → the durability MECHANISM is FIRM** (resistance sites are high-entropy at n=1,162, real sites,
  within-protein-controlled): DYNAMICS1's fragile demonstration becomes an evidence-backed mechanism.
- **FAIL → honest ceiling:** entropy does NOT locally mark resistance sites at scale; DYNAMICS1's
  target-level AUROC stays a small-n demonstration and is down-tiered accordingly. Reported either way.
- Reproduce ×2 byte-identical (SHA-256 sorted-key payload) required before any claim.

## Honest scope / bounds (stated in advance)
- Confound to report (not gate-defeating, but disclosed): resistance sites may cluster in specific
  structural contexts (e.g., active-site/binding pockets); the within-protein matched-random control
  addresses per-protein baseline but not context-specific enrichment — flagged as a caveat, and a
  secondary check restricts controls to a ±window around resistance sites (local-context sensitivity).
- Scope: target-alteration resistance in characterized ARGs; PLM-proxy for tolerance, not a fitness
  measurement. In-silico. This firms the MECHANISM underpinning the target-level signal, and I will not
  overstate it as a validated per-target clinical predictor (that remains EXPERIMENT-gated).
