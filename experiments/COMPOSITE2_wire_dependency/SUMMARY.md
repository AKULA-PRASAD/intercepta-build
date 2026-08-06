# COMPOSITE2 — Wiring the VALIDATED DEPEND1 functional-dependency layer into the router — SUMMARY

**Verdict: ALL 4 pre-registered routings hold; ALL assertions PASS; reproduced x2 byte-identical.**
The router's `FUNCTIONAL_DEPENDENCY` slot moved from `built=False` (never fires; host-embedded classes abstain)
to `built=True` with a **transfer-condition-precise, DATA-DEPENDENT** gate whose validated domain is
**HUMAN_CANCER only**. Human/cancer now FIRES a selective-dependency shortlist (reusing DEPEND1's committed
results) and recovers known targets; the novel host-dependent parasite STILL ABSTAINS by design.

- Payload SHA-256 (reproduced x2): `aebe8543c08ffa2d9ff1b6401ebbeb412f714630af58c7b8fd43b78d21ad9dbd`
- Router unit tests (data-free): **16/16 PASS** (self-run + pytest), incl. the COMPOSITE1 regression set.
- Env: python 3.11.14, CPU-only. Pure logic + reuse of committed DEPEND1/ENGINE/GENERALIZE3 results. No data
  committed. No git commit/push.

## The gate change (the router's law, v2)
`TRANSFER_GATE[FUNCTIONAL_DEPENDENCY]`:
- `built`: `False` -> **`True`** (DEPEND1 G1/G2/G3 PASS on DepMap; reproduced x2).
- `domain`: `{host_dependent_parasite, human_cancer}` -> **`{human_cancer}` ONLY**.
- `evidence`: V15-18 hypothesis-tier -> **DEPEND1 G1/G2/G3 PASS** (selective dependency recovers known cancer
  targets 0.80; generalizes to held-out disjoint lines 0.80; label-free expr->dep beats baseline rho 0.36).

**Why HUMAN_CANCER only (data-dependent, not a class blanket):** the transfer condition is *dependency data
(DepMap) OR a validated same-domain label-free expr->dep map exists for the context*. That holds for human
cancer. It does NOT hold for a host-dependent parasite: no parasite dependency screen exists, and DEPEND1's
label-free arm was validated on held-out DepMap **human** lines, **not organism-transferred** to a zero-screen
organism. The parasite is therefore excluded from the domain and abstains. Honest bound: DEPEND1 is cancer
**cell-line** Chronos dependency, NOT patient/clinical.

## The four routing results
| Case | Class | Output | functional_dependency | Key assertion |
|---|---|---|---|---|
| **(A)** human_cancer (declared) | human_cancer | **shortlist** | **FIRES** | skin->**SOX10** rank 1; KRAS-hotspot->**KRAS** rank 1 (from committed DEPEND1); FBA still gated out |
| **(B)** *P. falciparum* (declared) | host_dependent_parasite | **abstention** | **did NOT fire** (gated) | STILL ABSTAINS; reason cites "no dependency data" / "label-free" / "organism-transferred". THE INTEGRITY TEST |
| **(C)** *K. pneumoniae* (declared) | bacterium | shortlist | not fired (out of domain) | FBA + conservation-breadth fire; cores {murA,murG,mraY,dxs} present (committed ENGINE) — REGRESSION |
| **(D)** SARS-CoV-2 (autodetected) | virus | structural_class_id | not fired | structural only; FBA not fired; Mpro->protease, RdRp->polymerase — REGRESSION |

### (A) The NEW capability — human/cancer FIRES and recovers known targets
The router invokes `CompositeRouter.functional_dependency_shortlist_from_depend1(...)`, which REUSES DEPEND1's
committed `results/DEPEND1_metrics.json` (does NOT recompute selectivity a different way). For context `skin`
it returns SOX10 (genome-wide context-selectivity rank 1, in_top10, dep_frac 0.10, not pan-essential); for
`KRAS-hotspot` it returns KRAS (rank 1, in_top10). DEPEND1's G1/G2/G3 gates are all PASS. Output is a
confidence-tiered candidate shortlist, cell-line, not clinical.

### (B) The DECISIVE integrity test — parasite STILL abstains
functional-dependency is GATED OUT for the parasite with the reason: *"out of transfer domain ... VALIDATED for
HUMAN_CANCER only ... does NOT fire ... no parasite dependency data and DEPEND1's label-free expr->dep arm was
NOT organism-transferred ..."*. The class-level abstention reason (`HOST_DEPENDENT_PARASITE_ABSTENTION`) states
both gated signals precisely: (1) metabolic FBA falsified for host-embedded biology (GENERALIZE5/HOSTCTX1/2);
(2) functional-dependency validated-but-not-organism-transferred. The parasite emits NO shortlist. This is the
exact false claim the constitution names — prevented.

## Regression
COMPOSITE1's data-free unit tests all pass. Two tests encoding the OLD (v1) behavior that COMPOSITE2
intentionally changes were updated (human/cancer no longer abstains; functional-dependency now fires for
human/cancer), and three new tests were added (human_cancer fires; parasite non-transfer integrity; the
functional-dependency gate-table domain). Bacterium and virus routing are unchanged.

**Note on COMPOSITE1's committed demo (`run.py`):** the parasite abstention *text* was made truthful about
DEPEND1 (it previously said "functional-dependency layer not yet built", now false). The module keeps the
`HOST_EMBEDDED_ABSTENTION` name as a backward-compatible alias, so COMPOSITE1's assertions that compare against
that constant still hold; the parasite still abstains (the integrity invariant is preserved). Re-running
COMPOSITE1's `run.py` would produce a new payload SHA vs its committed v1 value because the citation text
evolved — expected when advancing the router from v1 to v2; the routing *behavior* (parasite abstains) is
unchanged.

## Honest scope
COMPOSITE2 un-gates functional-dependency ONLY for human/cancer, where dependency data exists. The novel
host-dependent parasite remains an ABSTENTION by design. DEPEND1 is cancer CELL-LINE Chronos dependency — NOT
patient/clinical, NOT wet-lab. All outputs are confidence-tiered candidate HYPOTHESES with provenance.

## Reproducibility
`run.py` -> `results/COMPOSITE2_metrics.json` (sorted keys) + `results/COMPOSITE2_payload.sha256`. Payload =
sorted-key JSON of the four routing decisions + DEPEND1 shortlist + assertion booleans (excludes
verdict/provenance). Run twice as separate processes; SHA-256 identical. Pure logic + committed-result reuse;
no RNG. No git commit/push; no data committed.
