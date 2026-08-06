# COMPOSITE2 — PRE-REGISTRATION (frozen BEFORE running)

*Wiring the VALIDATED DEPEND1 functional-dependency layer into the explicit router
(`src/intercepta/composite_router.py`), transfer-condition-precise. This file freezes the four expected
routing outcomes BEFORE the demonstration/validation script runs.*

**Constitution:** truth over vision; the router's integrity IS its abstention. The specific false claim to
prevent: letting functional-dependency fire for a NOVEL host-dependent PARASITE (which has no dependency data;
DEPEND1's label-free arm was validated on held-out DepMap HUMAN lines, NOT transferred to a zero-screen
organism). The parasite MUST still abstain. Reproduce x2 byte-identical (SHA-256 over sorted-key JSON payload,
excluding verdict/provenance). Deterministic. Zero budget, CPU-only, open data. No git commit/push.

Date frozen: 2026-08-05. Seed: n/a (pure logic + reuse of committed DEPEND1/ENGINE/GENERALIZE3 results).

---

## 1. The gate change being tested (the router's law, v2)

`FUNCTIONAL_DEPENDENCY` in `TRANSFER_GATE` moves from `built=False` (never fires; host-embedded classes abstain)
to:

| field | COMPOSITE1 (v1) | COMPOSITE2 (v2) |
|---|---|---|
| `built` | `False` | **`True`** (DEPEND1 G1/G2/G3 PASS) |
| `domain` | `{host_dependent_parasite, human_cancer}` | **`{human_cancer}` ONLY** |
| `discovery_grade` | `True` | `True` |
| evidence | V15-18 hypothesis-tier | **DEPEND1 G1/G2/G3 PASS on DepMap (0.80 / 0.80 / rho 0.36), reproduced x2** |

**Why HUMAN_CANCER only (data-dependent transfer, NOT a class blanket):** DEPEND1 validated selective-dependency
target-ID on DepMap human cancer cell lines, with held-out (disjoint-line) generalization AND a label-free
expr->dependency arm. The transfer condition is: *dependency data (DepMap) OR a validated same-domain
label-free expr->dep map is available for the context*. That holds for HUMAN_CANCER. It does NOT hold for a
host-dependent parasite: there is no parasite dependency screen, and DEPEND1's label-free arm was validated on
held-out DepMap **human** lines, **not organism-transferred** to a zero-screen parasite. The parasite is
therefore EXCLUDED from the domain and abstains. Honest bound: DEPEND1 is cancer **cell-line** Chronos
dependency, NOT patient/clinical.

## 2. PRE-REGISTERED expected routing outcomes (the four cases)

### (A) HUMAN_CANCER — a concrete DepMap context (declared) — THE NEW CAPABILITY
- **Declared class:** human_cancer.
- **EXPECT signals FIRED:** functional_dependency (discovery-grade). FBA STILL gated out (host-embedded).
- **EXPECT output type:** confidence-tiered **SHORTLIST** (was ABSTENTION in COMPOSITE1).
- **EXPECT firing path:** the router invokes `functional_dependency_shortlist_from_depend1` reusing DEPEND1's
  committed results and returns the context-selective dependency target(s) for the context.
- **EXPECT assertion (known target recovered):**
  - context `skin` (melanoma) -> **SOX10** appears in the shortlist, rank 1, in_top10.
  - context `KRAS-hotspot` (KRAS-mutant) -> **KRAS** appears in the shortlist, rank 1, in_top10.
  - DEPEND1 gates G1/G2/G3 all == PASS.

### (B) HOST_DEPENDENT_PARASITE — *P. falciparum* (declared) — THE DECISIVE INTEGRITY TEST
- **Declared class:** host_dependent_parasite.
- **EXPECT signals FIRED:** NONE.
- **EXPECT functional_dependency:** **did NOT fire**; it is GATED OUT with a reason citing that the validated
  domain is HUMAN_CANCER and the signal was NOT organism-transferred.
- **EXPECT FBA:** gated out (host-embedded metabolism falsified).
- **EXPECT output type:** explicit CLASS-LEVEL **ABSTENTION**.
- **EXPECT abstention reason to contain:** `"no dependency data"`, `"label-free"`, `"organism-transferred"`
  (plus GENERALIZE5 / HOSTCTX1/2 / metabolic essentiality falsified for the FBA half). The parasite MUST NOT
  emit a dependency shortlist. This is the pass/fail integrity criterion of COMPOSITE2.

### (C) BACTERIUM — *K. pneumoniae* (declared) — REGRESSION (FBA path unchanged)
- **EXPECT signals FIRED:** fba_essentiality + conservation_breadth (full bacterial composite), output
  SHORTLIST. functional_dependency NOT fired (out of domain).
- **EXPECT (reuse committed ENGINE report, no recompute):** validated cores **{murA, murG, mraY, dxs}** present.

### (D) VIRUS — SARS-CoV-2 (autodetected by tiny proteome) — REGRESSION (structural path unchanged)
- **EXPECT class:** virus (autodetected). **EXPECT output:** structural_class_id.
- **EXPECT signals FIRED:** structural_homology only. FBA NOT fired; functional_dependency NOT fired.
- **EXPECT (reuse committed GENERALIZE3):** Mpro -> protease, RdRp -> polymerase.

## 3. Reproduction / determinism
All routing decisions are pure logic; the firing path reuses committed DEPEND1 results; the bacterium/virus
regressions reuse committed ENGINE_endtoend / GENERALIZE3 results. No recomputation, no RNG. The COMPOSITE2
payload (four routing decisions + the DEPEND1 shortlist + assertion booleans) is hashed (SHA-256 over sorted-key
JSON, excluding verdict/provenance); the script is run twice as separate processes and the SHA-256 must match
byte-identically.

## 4. Honest scope
COMPOSITE2 un-gates functional-dependency ONLY for human/cancer, where dependency data exists; the novel
host-dependent parasite case remains an ABSTENTION by design; DEPEND1 is cancer CELL-LINE dependency, NOT
patient/clinical, NOT wet-lab. All outputs are confidence-tiered candidate HYPOTHESES with provenance.
