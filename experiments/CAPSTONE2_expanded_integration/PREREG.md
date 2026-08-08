# CAPSTONE2 — pre-registration (frozen BEFORE the integration exists)

*The end-to-end integration proof of the FULLY-EXPANDED INTERCEPTA composite: "any disease → honest decision coverage",
demonstrated across every covered class through the AUTONOMOUS router, verdict-stable and fail-safe. Pre-registered per the
Constitution (gate fixed before running). This is the last item on the DEFINITION-OF-DONE critical path (docs/INVENTION_ROADMAP.md):
GENETICS1 ✓ + MODALITY1 ✓ + AMR1 (in flight) + COMPOSITE4 (in flight, the router wiring) → **CAPSTONE2**.*

## What CAPSTONE2 is (and is NOT)
- **IS:** an integration DEMONSTRATION that the composite, after the Wave-A/B expansion, drives one representative input per
  covered class through `router.decide_auto()` (autonomous class detection, ROUTERAUTO1) → fires only the validated signal(s)
  at the confidence each earned → appends a fail-safe intervention-modality recommendation (MODALITY1) → or **abstains** where no
  signal transfers. No new science; it composes committed, reproduced-×2, validated arms.
- **IS NOT:** a new discovery, a drug, a clinical claim, or a benchmark. It is the honest "any disease" coverage claim made
  concrete — a real answer where a signal transfers, an explicit abstention where none does.

## Inputs (one representative case per covered class; held-out/novel where feasible)
1. **Bacterium** (held-out, e.g. a WHO-priority genome never in dev) → FBA full-grade + chokepoint + conservation + host-safety
   + **AMR resistance-durability axis** (AMR1) + modality.
2. **Archaeon** → FBA full-grade (BLIND6-class, self-contained genome).
3. **Free-living eukaryote / fungus** → FBA (capped per eukaryote attenuation).
4. **Virus** → structural class-ID only; FBA correctly NOT fired (no metabolism).
5. **Host-dependent parasite WITH a curated GEM** → FBA CAPPED + uncertainty-flagged (COMPOSITE3).
6. **Human cancer** → functional dependency (DEPEND1) + modality.
7. **Human monogenic** → causal-gene given → intervention-MODE (MENDEL1) + modality.
8. **Human complex/polygenic** → GENETIC_ASSOCIATION (GENETICS1) fired **CAPPED** (attenuated bound [1.67,2.26]) + modality.
9. **FAIL-SAFE A — dark proteome** (DARK1) → ABSTAIN, 0 signals fired.
10. **FAIL-SAFE B — novel zero-screen parasite, no GEM** (TRANSFER1) → ABSTAIN.

## Pre-registered PASS gate (fixed before running; ALL must hold)
- **G1 routing correctness:** each of cases 1–8 auto-detects the empirically-correct class and fires exactly the signal(s)
  validated for it, at the earned confidence (full-grade / capped where the arm is attenuated or GEM-contingent). Every fired
  signal must trace to a committed, reproduced-×2, pre-registered validation (VAL-ESS/CROSSVAL/BLIND*, GENERALIZE/HARDEN*,
  DEPEND1/F3CLIN1, MENDEL1, GENETICS1, AMR1).
- **G2 fail-safe (HARD):** cases 9–10 ABSTAIN with **zero** signals fired and **zero** mis-fires (preserves DARK1 22/22 and
  TRANSFER1). A single fail-safe violation = CAPSTONE2 FAIL.
- **G3 intervention fail-safe (HARD):** the appended modality stage emits **zero** infeasible recommendations across all cases
  (MODALITY1's hard fail-safe), and abstains where features are absent.
- **G4 verdict-stability (the reproducibility fix):** the CAPSTONE2 payload hashes ONLY `verdict_skeleton()` (class, sorted
  fired-signal names, abstain, capped, recommended_modality_class) — NOT volatile reason-prose — and reproduces **×2
  byte-identical**. This is the fix for the router-drift hygiene finding (LEDGER 2026-08-07).
- **G5 honesty labels:** capped/attenuated arms (eukaryote FBA, host-dependent parasite, human-complex genetics) carry an
  explicit uncertainty flag; the affinity wall + wet-lab + clinical remain labeled GATED; no case is presented as a
  validated drug or clinical claim.

**FAIL (first-class, reported not hidden):** any mis-route, any fail-safe violation (G2/G3), any verdict-skeleton drift (G4),
or any missing honesty label (G5) → CAPSTONE2 FAILS and the defect is fixed before the compute-complete claim is made.

## Scope (binds every output)
Composition of validated in-silico target-PRIORITIZATION + intervention-modality TRIAGE; outputs are provenance-tagged
HYPOTHESES with honest confidence, not drugs/clinical/wet-lab. Demonstrates "any disease" as honest DECISION coverage —
applies what is validated per biology, abstains where not — NOT a universal model. Remaining frontiers (novel-target affinity
= AFFINITY1 GPU-gated; wet-lab = CRISPRIDESIGN1 turnkey; clinical) are evidence-gated and explicitly out of scope for this
integration proof.

## Reproduction
Deterministic (no RNG); payload = SHA-256 over the sorted-key list of per-case `verdict_skeleton()` dicts, excluding
provenance/prose; run twice, assert byte-identical.

*Frozen 2026-08-07, before COMPOSITE4/AMR1 landed. run.py + results to be added once the router integration (COMPOSITE4) and
the AMR durability axis (AMR1) are committed and independently verified.*
