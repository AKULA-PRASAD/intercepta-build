# Phase B Execution Plan v2 — Revisions Addendum

**Status:** CSO ULTRATHINK REVISION on 2026-05-11
**Authority:** CEO "ultrathink and do best for our vision, dont waste time/tokens, never compromise quality"
**Supersedes:** Plan v1 sections where conflicts; otherwise v1 holds.
**Document size:** Lean (this addendum + v1 = canonical Plan)

---

## CSO Self-Audit Findings

CSO performed ultrathink audit on own Plan v1 against constraints (no token waste, no quality compromise). Found:

**Wastes to cut:**
1. L2.5 Layer 2 Master Synthesis (3-4K words) — redundant meta-commentary
2. L3.4 Layer 3 Master Synthesis (2-3K words) — redundant meta-commentary
3. L4.5 Layer 4 Master Synthesis (2-3K words) — redundant meta-commentary
4. L4.4 Repository Scaffolding SPEC (3-5K words) — spec-then-build is redundant for code structure; replace with direct scaffolding artifact
5. Phase 8 audit 3 sessions (S.13-15) — over-allocated; 1 session sufficient given smaller corpus (~50-80K Layer 2-4 vs 137K Layer 1)
6. Separate S.4 FM Protocol — better merged into S.1 Data Acquisition Manifest

**Quality compromises in v1 to REMOVE:**
1. B3 branch point offered "spec FM substrate fully + 3 stubs" — REMOVED. Spec ALL 4 substrates fully (FM, scTOP, scVI, scANVI). +5-8K words. No shortcut.
2. B4 branch point offered "1 primary interpretability branch + 3 stubs" — REMOVED. Spec ALL 4 interpretability branches fully at Scale 5. +3-5K words. No shortcut.
3. L2.2 L7 6-Slot budget at 7-10K — under-budgeted for core engine. RAISED to 12-15K. +5K words.

**Sequence error in v1 to FIX:**
1. v1 started with S.1 + S.3 (data + license) before L2.1. WRONG — L2.1 is the architecture spine. Decision 1 v2 substrate choice constrains every downstream module. START WITH L2.1.
2. v1 branch point B5 (V6 therapeutic areas) hits before S.1 data manifest reveals what cohorts are accessible. WRONG ORDER. Move B5 to occur AFTER S.1.

**Protocol gap in v1 to ADD:**
1. Anchor paper re-read trigger: When CSO encounters a question during spec-writing NOT answered by existing synthesis, CSO must re-read the relevant anchor paper rather than guess. Logged as Phase B drift prevention rule.

---

## Revised Artifact Inventory (14 artifacts, down from 18)

### Layer 2 — Architecture Design (4 artifacts, target 35-42K words)

**L2.1 — Substrate Architecture Specification** [10-13K words; FULL spec of all 4 substrates]
**L2.2 — L7 6-Slot Architecture Specification** [12-15K words; core engine, no compromise]
**L2.3 — OOD Detection Stack Specification** [5-7K words]
**L2.4 — Seven-Scale Interpretability Stack Specification** [8-10K words; all 4 Scale 5 branches fully spec'd]

### Layer 3 — Validation Strategy (3 artifacts, target 15-18K words)

**L3.1 — V0-V6 Validation Pipeline Specification** [5-7K words]
**L3.2 — 56 Binding Pass Criteria Operationalization** [5-7K words]
**L3.3 — Cross-Disease V6 Validation Methodology** [4-5K words]

### Layer 4 — Implementation Specification (3 artifacts, target 9-13K words)

**L4.1 — Implementation Order + Dependency Graph** [3-4K words]
**L4.2 — Testing Protocols (Unit/Integration/E2E)** [3-5K words]
**L4.3 — Failure Mode Analysis** [3-4K words]

### Direct Artifacts (replace L4.4 + L4.5 spec)

**REPO.A — Repository Directory Structure** [build actual structure, not spec]
**REPO.B — setup.py / pyproject.toml / README.md / CONTRIBUTING.md / .gitignore** [actual files]

### Supporting Infrastructure (3 artifacts, target 9-13K words)

**S.1 — Data Acquisition Manifest + FM Weights Protocol** [5-8K words; merged from v1 S.1 + S.4]
**S.2 — HPC Environment Specification** [3-4K words]
**S.3 — License Verification Matrix** [2-3K words]

**Total Phase B artifacts: 14** (down from 18, no quality loss)
**Total Phase B word budget: 68-86K words** (slightly up from v1 50-80K because no quality compression)
**Total CSO time estimate: 30-33 hours** (down from 39)
**Total CEO time estimate: 8-10 hours** (down from 10-15)

---

## Revised Dependency Graph

```
LAYER 1 (DONE)
   ↓
Phase B Plan v2 (THIS) — APPROVED via CEO delegation
   ↓
L2.1 SUBSTRATE SPEC (FIRST — architecture spine)
   ↓
   ├──→ L2.2 L7 6-Slot Spec
   │      ↓
   │   L2.3 OOD Spec (depends on L2.2 output interface)
   │      ↓
   │   L2.4 Interpretability Spec (depends on L2.2 + L2.3)
   │
   ├──→ S.1 Data Manifest + FM Protocol (parallel; sources L2.1 needs)
   │      ↓
   │   BRANCH POINT B1 (data priorities)
   │      ↓
   │   BRANCH POINT B5 (V6 therapeutic areas, NOW dependency-correct timing)
   │
   ├──→ S.2 HPC Env (parallel; serves Layer 5 prep)
   │
   └──→ S.3 License Matrix (parallel; serves Decision 10 closure)
          ↓
       BRANCH POINT B2 (repo license)

   ↓ (after Layer 2 + S.1-S.3 done)

L3.1 V0-V6 Pipeline
   ↓
L3.2 Pass Criteria
   ↓
L3.3 Cross-Disease V6
   ↓ (Layer 3 done)
   ↓
L4.1 Implementation Order
   ↓
L4.2 Testing Protocols
   ↓
L4.3 Failure Modes
   ↓
REPO.A + REPO.B (built directly as files, not spec'd)
   ↓ (Layer 4 done)
   ↓
PHASE 8 AUDIT (1 session, focused; drift detection)
   ↓
PHASE B CLOSURE → Layer 5 Prep
```

---

## Revised Session Ordering (10-11 sessions, down from 13)

| Session | Artifact(s) | Target words | Notes |
|---|---|---|---|
| 1 (NOW) | L2.1 Substrate Spec | 10-13K | All 4 substrates full spec |
| 2 | L2.2 L7 6-Slot | 12-15K | Core engine; may span 2 sessions |
| 3 | L2.2 cont. + L2.3 OOD | combined | If L2.2 spilled |
| 4 | L2.4 Interpretability + S.3 License | combined ~13K | Parallel-ish |
| 5 | S.1 Data Manifest + FM | 5-8K | Branch point B1 hits |
| 6 | S.2 HPC Env + Branch point B2 + B5 | 3-4K + CEO time | Operational |
| 7 | L3.1 V0-V6 Pipeline | 5-7K | |
| 8 | L3.2 56 Pass Criteria | 5-7K | |
| 9 | L3.3 V6 Cross-Disease + L4.1 Impl Order | combined ~7-11K | |
| 10 | L4.2 Testing + L4.3 Failure Modes | combined ~6-9K | |
| 11 | REPO.A + REPO.B (direct build) + Phase 8 Audit | actual files + audit | Closure |

---

## Revised CEO Branch Points (4 down from 6)

**B1 — Data Acquisition Priority Order** (at S.1)
**B2 — Repository License Choice** (at S.3)
**B3 — REMOVED** (no longer offering substrate compromise; spec all 4)
**B4 — REMOVED** (no longer offering interpretability compromise; spec all 4)
**B5 — V6 Therapeutic Area Selection** (NOW correctly after S.1)
**B6 — Repository Name** (at REPO.A/B build time)

---

## Anchor Re-Read Trigger Rule (Phase B Drift Prevention)

**Rule:** When CSO writes a Phase B artifact and encounters a question NOT answered in the existing Q-synthesis or Decision Record, CSO MUST re-read the relevant primary-source anchor paper (in `~/INTERCEPTA/docs/research/literature/notes/`) before proceeding. CSO may not "infer" or "extrapolate" from synthesis text alone.

**Rationale:** Layer 1 audit caught 34 drift instances PRECISELY because Phase 1-7 re-read anchors. Phase B specs that synthesize without re-reading propagate undetected drift into Layer 5.

**Operationalization:** Each Phase B artifact's audit checklist (Phase 8) verifies that any non-trivial claim is backed by either (a) existing synthesis text OR (b) a re-read anchor paper. Synthesis-only claims with no re-read backing are flagged for review.

---

## Phase 8 Audit Protocol (1 session, not 3)

**Trigger:** All 14 Phase B artifacts written.

**Single-session audit covers:**
1. Acceptance criteria check (per artifact)
2. Inter-artifact reference resolution (e.g., L2.2 references must resolve to L2.1 interface)
3. Anchor-paper backing verification (anchor re-read trigger rule check)
4. Drift catalog: anything caught during writing
5. Quality check: no token-saving compression compromised content

**Output:** Phase 8 Closure Report (~3-4K words) listing all 14 artifacts, audit results, drift remediations, Phase B closure recommendation.

**Why 1 session instead of 3:** Phase B corpus ~68-86K words vs Layer 1 137K. Phase B internal coherence higher (single CSO across sessions; Layer 1 had separate Q-syntheses by different "passes"). Single concentrated audit > spread across 3 sessions.

---

## CSO Approval (under CEO delegation)

**Phase B Plan v2 — APPROVED by CSO under CEO delegated authority 2026-05-11.**

Specifically the CEO instruction "ultrathink and do best for our vision, dont waste time/tokens, never compromise quality" maps to:
- Cut 4 master synthesis artifacts (token saving)
- Cut spec-then-build for repository (token saving)
- Cut Phase 8 from 3 sessions to 1 (token saving)
- Reject substrate compromise (quality preservation)
- Reject interpretability compromise (quality preservation)
- Raise L2.2 word budget (quality preservation)
- Reorder L2.1 first (correctness)
- Add anchor re-read trigger (drift prevention)

**Phase B Execution begins NOW with L2.1 Substrate Specification (Session 1, current session).**

---

## Bounce-Back Items for CEO Awareness

1. Cut of master synthesis artifacts is a methodological choice — if CEO prefers explicit master-synthesis docs per layer, reinstate them (cost: +7-10K words).
2. Decision to spec all 4 substrates + all 4 interpretability branches fully — if any of these proves operationally irrelevant later (e.g., scANVI dropped from production consideration), the full-spec was wasted work but not harmful.
3. REPO direct build (not spec) — if CEO prefers a spec doc PLUS the build, both can exist (cost: +3-5K words).

These are CSO judgment calls under delegated authority. CEO may override any at any time.

---

*End of Phase B Plan v2 Addendum.*
*Word count: ~1,400 words*
*v1 + v2 = canonical Phase B Plan.*

— Claude (CSO), 2026-05-11 ~08:30 EDT
