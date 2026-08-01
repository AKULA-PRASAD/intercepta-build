# E2E1 — Zero-data END-TO-END discovery on a pathogen (M. tuberculosis): proteome → target → pocket → docked candidate shortlist, composed on the living substrate (finalized 2026-07-31, PRE-RESULT)

## What this is (and is NOT)
A **capability-composition demonstration** — the first time the validated front-half (target-ID) and back-half (binding
+ ADMET + synth) are wired into ONE zero-data pipeline that starts from a pathogen PROTEOME and ends in a ranked,
provenance/confidence-tiered candidate shortlist. NOT a hypothesis test; NOT validated drugs. Output = ranked
COMPUTATIONAL HYPOTHESES for a real TB target, honestly scoped. Uses ZERO TB-specific activity data.

## Vision alignment (the north star, directly)
This is the closest thing yet to the stress test: *"a pathogen appears, no activity data — produce credible candidates
from sequence."* M. tuberculosis stands in for the novel pathogen (we withhold all TB drug-activity data; only its
proteome + transferable knowledge from OTHER organisms is used). Demonstrates the LIVING SUBSTRATE carrying provenance +
confidence tiers through the whole chain, and the extensibility of composing validated adapters. Every capability here
survives the "would it matter for a never-seen disease?" filter.

## The composed pipeline (all steps individually validated; this tests the COMPOSITION)
1. **Target-ID (front half, TID1+TID2):** rank the Mtb proteome by conservation-transfer (mmseqs2 homology to OTHER
   organisms' drug targets, leave-Mtb-out) × structural druggability (fpocket on AlphaFold v6) × host-nonhomology
   selectivity (down-weight human homologs) → prioritized target shortlist; abstain where no homolog. QUANT ANCHOR:
   does the shortlist recover KNOWN Mtb drug targets (UniProt ChEMBL-xref) above random (top-k precision)?
2. **Pick a target:** the top-ranked KNOWN druggable Mtb target with a high-confidence AlphaFold structure + a
   well-defined fpocket pocket (interpretable, docking-ready). Reported explicitly.
3. **Pocket → docking box (bridge front→back):** the chosen target's best fpocket pocket centroid + extent defines the
   Vina search box (the front half's pocket IS the back half's box — pipeline coherence).
4. **Binding (back half, C1):** prepare the receptor (AF structure → pdbqt) + dock a screening library (seeded sample of
   ChEMBL drug-like compounds, RDKit 3D → Vina, seed=42) into the pocket → docking score per compound.
5. **Multi-channel scoring (B30/B31):** per candidate = docking (activity proxy) + ADMET safety (hERG/AMES/DILI,
   disease-agnostic transfer) + synthesizability → composite; rank.
6. **Output:** top-N ranked candidate shortlist, each a **provenance/confidence-tiered substrate record** (target +
   pocket + docking pose score + ADMET + synth + AD/confidence + honest "hypothesis, not validated" flag).

## Metrics / anchors (honest, mixed quantitative + demonstration)
- **Target-ID anchor (quantitative):** top-k precision / AUROC of the composite target ranking vs known Mtb targets, vs
  random + the conservation-only baseline (does the composite ≈ conservation, per the TID1/TID2 arc? — reported honestly).
- **Pocket:** chosen target's fpocket max Druggability Score (is it a real pocket?).
- **Docking:** score distribution + the ranked shortlist; if any known inhibitors of the chosen target happen to be in
  the library, report their rank (opportunistic sanity, not a claim).
- **Composition demonstration:** the end-to-end runs deterministically and emits a coherent, tiered candidate shortlist.

## Hypotheses / expectations (pre-registered, honest)
- **E1 (target-ID composes):** the composite target ranking recovers known Mtb targets above random (top-k precision >
  prevalence); EXPECTED to be ≈ conservation-driven (per TID1/TID2 — the composite is not expected to beat conservation;
  stated up front, not spun).
- **E2 (pipeline coherence):** the chosen target's fpocket pocket yields a valid Vina box and the library docks; the
  multi-channel shortlist is produced deterministically.
- **No efficacy claim:** docking ranks are pose-plausible hypotheses, NOT validated activity (C1 showed docking is weak
  at the top — carried forward as an explicit caveat, not hidden). This is a COMPOSITION demo, not a discovery claim.

## Honesty / scope (binding)
Zero TB activity data used. Output = ranked COMPUTATIONAL HYPOTHESES, NOT validated hits / NOT drugs. Target-ID is
conservation-dominated (TID1/TID2 boundary — the composite does not beat conservation; stated). Docking is retrospective,
single-conformation, Vina-only, and weak at the top (C1); ADMET/synth are disease-agnostic transfers. Screening library
is generic drug-like chemistry (a virtual screen, not curated TB actives). No wet-lab, no clinical claim. The value is
demonstrating the VALIDATED pieces COMPOSE end-to-end from a proteome on the living substrate — the vision's shape at
small scale — with every limitation stated.

## Reproducibility
Deterministic (mmseqs fixed; fpocket cached/deterministic; library sample seed=42; RDKit ETKDG seed=42; Vina seed=42;
ADMET/synth seeded). Reproduce ×2 byte-identical where docking permits (payload over target-ranking metrics + chosen
target + candidate shortlist scores). Output: `experiments/E2E1_pathogen_endtoend/results/E2E1_metrics.json`. Envs:
`bioinfo` (mmseqs/fpocket), `docking` (Vina/obabel/rdkit), `intercepta-build` (admet/synth/analysis). Feasibility-gated:
verify chosen-target AF structure + pocket + library + ADMET/synth load, smoke-test docking on a few compounds before
the full library (B63 no-blind-run lesson).
