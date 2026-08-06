# COMPOSITE1 — PRE-REGISTRATION (frozen BEFORE running)

*The explicit biology-class-aware ROUTER that wraps the already-validated `DiscoveryEngine`. It makes the
transfer-condition gating EXPLICIT: it applies the right validated signal per biology class and ABSTAINS where
none transfers. This file freezes the expected routing behaviour before the demonstration runs.*

**Constitution:** truth over vision; the router's integrity IS its abstention. Reproduce x2 byte-identical
(SHA-256 over sorted-key JSON payload, excluding verdict/provenance). Deterministic. Zero budget, CPU-only,
open data. No git commit/push.

---

## 1. The transfer-gate table being tested (from COMPOSITE_ARCHITECTURE.md §2 + the LEDGER)

A signal fires as a **discovery-grade** signal for a class ONLY IF its evidence-derived transfer condition
holds for that class AND the module is built. Otherwise it is GATED OUT with an explicit reason.

| Signal | Transfer condition (validated domain) | Fires for | GATED for | Evidence |
|---|---|---|---|---|
| **FBA gene-essentiality** | self-contained metabolism captured by a quality GEM | bacterium (VERIFIED), free-eukaryote (VERIFIED-weaker) | **host-dependent parasite, human/cancer** (host-embedded); virus (no metabolism) | MET1-3, VAL-ESS, GENERALIZE4 PASS; **GENERALIZE5 + HOSTCTX1 + HOSTCTX2 FALSIFIED for host-dependent** |
| **Structural homology (Foldseek TM) — target CLASS-ID** | a 3D structure exists; fold is conserved with a known drugged fold | virus, bacterium | (organisms with no structure) | GENERALIZE2/3 PASS (Mpro→protease, RdRp→polymerase); FOLD1 |
| **Sequence repurposing** | shares detectable sequence identity with a drugged homolog | (validation-grade ONLY — recovers known pharmacology) | **NEVER a novel-coverage / discovery signal** | INTERVENE1 9/9 canonical; STRUCTREPURPOSE1: structure did NOT expand coverage (promiscuity) |
| **Functional dependency (CRISPR)** | a context-specific dependency signal / learnable map exists | (would serve host-dependent parasite + human/cancer) | **NOT BUILT YET → cannot fire** | V15-18 (hypothesis-tier, single cohort); Wave-3 gap |
| Conservation breadth | essential is part of a broadly conserved core | bacterium (+ free-euk) | — | REACH1 AUROC 0.86 |
| Host-safety hard filter | targets comparable to a host proteome | any class with a known host | — | ENGINE FRONT1/E2E2 |

**The gate law:** a signal transfers exactly as far as the biological invariant it rides on is conserved. The
router refuses to apply a signal outside its transfer condition (→ abstain) rather than force one model onto
biology it has been shown not to fit.

## 2. Class detector (honest scope)

Minimal by design — the integrity is in the transfer-gate + abstention, NOT in a perfect classifier:
- **virus** is auto-detectable by a tiny proteome (≤ 60 proteins).
- **host-dependence is NOT sequence-derivable** → it must be a DECLARED flag (bacterium vs free-eukaryote vs
  host-dependent parasite vs human/cancer are declared). This is stated as a limitation, not hidden.
- unknown otherwise → apply-what-transfers, abstain if nothing does.

## 3. PRE-REGISTERED expected routing outcomes (the three test cases)

### (A) BACTERIUM — held-out *K. pneumoniae* (reuse ENGINE_endtoend inputs/caches)
- **Detected/declared class:** bacterium (declared; proteome 5126 ≫ virus threshold).
- **EXPECT signals FIRED:** FBA-essentiality + composite (chokepoint, conservation, conservation-breadth,
  host-safety filter, resistance, condition-robustness) — the full validated bacterial composite.
- **EXPECT output type:** confidence-tiered SHORTLIST (not abstention).
- **EXPECT assertion:** the known validated cores **{murA, murG, mraY, dxs}** all present in the shortlist;
  result consistent with the committed ENGINE_endtoend report.

### (B) VIRUS — SARS-CoV-2 (reuse generalize1 mature proteome + committed GENERALIZE3 structural result)
- **Detected class:** virus (AUTO-detected — proteome 30 ≤ 60).
- **EXPECT signals FIRED:** structural-homology class-ID ONLY.
- **EXPECT signals GATED OUT:** FBA-essentiality (no metabolism / out of domain) **must NOT fire**;
  sequence-repurposing **must NOT fire** as a discovery signal (validation-grade only, GENERALIZE1 0/30).
- **EXPECT output type:** structural target-CLASS hypotheses; specifically **Mpro → protease** and
  **RdRp → polymerase** (from GENERALIZE3 PASS).

### (C) HOST-DEPENDENT PARASITE — *P. falciparum* (reuse generalize5) — THE DECISIVE INTEGRITY TEST
- **Declared class:** host_dependent_parasite (host-dependence declared).
- **EXPECT signals FIRED:** NONE (no validated discovery signal transfers).
- **EXPECT signals GATED OUT:** FBA-essentiality gated (host-embedded metabolism — GENERALIZE5/HOSTCTX1/2
  falsified); functional-dependency gated (module not built).
- **EXPECT output type:** explicit CLASS-LEVEL **ABSTENTION** — it must NOT emit a confident FBA shortlist.
- **EXPECT abstention reason to contain:** *"host-embedded biology: metabolic essentiality falsified
  (GENERALIZE5/HOSTCTX1/2); functional-dependency layer not yet built"*.
- A naive engine would happily FBA the parasite and output wrong targets (GENERALIZE5 OR 2.47, sub-threshold);
  COMPOSITE1 must REFUSE. This is the pass/fail integrity criterion of the whole build.

## 4. Reproduction / determinism
Routing decisions are pure logic (deterministic). Case A invokes the deterministic DiscoveryEngine (reproduced
x2 in ENGINE_endtoend). Case B reuses the committed GENERALIZE3 static result. Case C is pure logic. The
COMPOSITE1 payload (routing decisions + assertion booleans + key recovered targets) is hashed; the script is
run twice as separate processes and the SHA-256 must match byte-identically.

## 5. Honest scope
(A) reuses the already-validated engine machinery (this is composition, not new biology). The class detector is
deliberately minimal. All outputs are confidence-tiered candidate HYPOTHESES with provenance, not validated
drug targets and not wet-lab.
