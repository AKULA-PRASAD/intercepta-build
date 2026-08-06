# COMPOSITE1 — Explicit biology-class-aware ROUTER (SUMMARY)

**Result: ALL pre-registered routing assertions PASS.** Reproduced x2 byte-identical.
**payload sha256:** `f8e9824313f5095bf5c5b9672f0e4ac28d1178561d6aeb7a608793d58e582905`
**Evidence tier:** COMPOSITION of already-validated parts (the DiscoveryEngine, GENERALIZE3) behind an explicit
transfer-gate. In-silico; not wet-lab.

## What it is
`src/intercepta/composite_router.py` — an explicit biology-class-aware router that wraps the already-validated
`DiscoveryEngine`. It encodes the evidence-derived transfer-condition table (COMPOSITE_ARCHITECTURE.md section 2)
as a hard gate, checks which conditions hold for the input's biology class, composes ONLY those signals, and
returns either a confidence-tiered shortlist OR an explicit **class-level abstention**. **The router's integrity
is its abstention.**

## Transfer-gate table AS IMPLEMENTED
| Signal | Fires (validated domain) | Gated for | Grade | Evidence |
|---|---|---|---|---|
| FBA gene-essentiality | bacterium, free-eukaryote | **host-dep parasite, human/cancer, virus** | discovery | MET1-3/VAL-ESS; GENERALIZE4; **GENERALIZE5+HOSTCTX1+HOSTCTX2 falsified host-dep** |
| Structural homology (class-ID) | virus, bacterium | organisms w/o structure | discovery | GENERALIZE2/3; FOLD1 |
| Sequence repurposing | (any — validation only) | **never a discovery signal** | validation-only | INTERVENE1 9/9; STRUCTREPURPOSE1 (no coverage gain) |
| Functional dependency | (host-dep parasite, human/cancer) | **NOT BUILT -> never fires** | discovery(unbuilt) | V15-18 hypothesis-tier; Wave-3 gap |
| Conservation breadth | bacterium, free-eukaryote | — | discovery | REACH1 |
| Host-safety filter | bacterium, free-eukaryote, virus | — | filter | ENGINE FRONT1/E2E2 |

Class detector is deliberately minimal: virus is auto-detected by a tiny proteome (<=60); host-dependence is NOT
sequence-derivable and must be DECLARED. The integrity is the gate + abstention, not the classifier.

## Three-case routing results (pre-registered, then run)
| Case | Class (source) | Output | FBA fired? | Key assertion |
|---|---|---|---|---|
| **A** K. pneumoniae | bacterium (declared) | **shortlist** | **YES** | cores {murA, murG, mraY, dxs} all present; top-20 identical to committed ENGINE |
| **B** SARS-CoV-2 | virus (**auto**detected, 30 proteins) | **structural_class_id** | **NO** | Mpro->protease (TM 0.462), RdRp->polymerase (TM 0.473); FBA & sequence-repurposing NOT fired |
| **C** P. falciparum | host-dep parasite (declared) | **ABSTENTION** | **NO** | no discovery signal fired; reason = "host-embedded biology: metabolic essentiality falsified (GENERALIZE5/HOSTCTX1/2); functional-dependency layer not yet built" |

**The decisive integrity test HOLDS:** a naive engine would happily FBA the parasite and emit wrong targets
(GENERALIZE5 OR 2.47, sub-threshold); COMPOSITE1 **refused** and abstained at the class level, and the virus did
**not** fire FBA — it routed to the structural signal that is actually validated for that class.

## Reproduction & tests
- **Reproduced x2 byte-identical:** payload sha `f8e9824...` on two separate processes (case A invokes the
  deterministic DiscoveryEngine over cached inputs; B reuses committed GENERALIZE3; C is pure logic).
- **Data-free unit tests:** 14/14 PASS (`test_router.py`) — exercise the pure gate/abstention/detector logic
  with no files, no network, no heavy deps.

## Honest scope
Case A reuses already-validated engine machinery (this is composition, not new biology). Case A's routing
decision lists structural-homology as transfer-capable for bacteria (FOLD1), but no structures were supplied so
the engine honestly degraded and did not compose it (active signals: essentiality, chokepoint, breadth,
conservation, host-safety, resistance, condition-robustness). Class detector is minimal by design. All outputs
are confidence-tiered candidate HYPOTHESES with provenance — not validated drug targets, not wet-lab. Each
frontier class remains n=1.
