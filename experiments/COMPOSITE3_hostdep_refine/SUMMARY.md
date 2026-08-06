# COMPOSITE3 — Honest refinement of the router's host-dependent-parasite FBA handling (router v3) — SUMMARY

**Verdict: ALL pre-registered routings hold; ALL assertions PASS; reproduced x2 byte-identical.** The router no
longer blanket-abstains on host-dependent parasites for FBA. It now FIRES FBA when a curated GEM exists, but at
**capped confidence (0.5) with an explicit uncertainty flag** — NEITHER the old class-level abstention (which
wrongly refused Toxoplasma) NOR bacterial full-grade confidence (which would overclaim on Plasmodium). With NO
GEM there is no signal → it STILL ABSTAINS.

- **Payload SHA-256 (reproduced x2):** `f540c4a32e69841cb168e30ce9923a8ed1ab5ddca3dfc1becd4003fa25562d5f`
- **Router unit tests (data-free): 17/17 PASS** (self-run + pytest), incl. the full COMPOSITE1/COMPOSITE2
  regression set. One prior test (`test_parasite_abstains_fba_gated`) was renamed/updated to v3
  (`test_parasite_no_gem_abstains`) because it encoded the falsified blanket-abstain premise; one new test
  (`test_parasite_with_gem_fires_capped_flagged`) was added; `test_gate_table_fba_domain` was extended with the
  uncertain-domain assertions. All other tests unchanged and passing.
- Env: `~/miniconda3/envs/intercepta-build` (python 3.11), CPU-only. Pure logic + reuse of committed
  HARDENP1/GENERALIZE5/DEPEND1/ENGINE/GENERALIZE3 results. No data committed. No git commit/push.

## Why (the correction)
Router v2 blanket-abstained on host-dependent parasites for FBA on an **n=1** premise (GENERALIZE5 Plasmodium
OR 2.47 + HOSTCTX1/2 negatives → "metabolic essentiality is the wrong signal for host-embedded biology").
**HARDENP1 falsified it:** a second host-dependent parasite, *Toxoplasma gondii* (curated iTgo2020 vs Sidik-2016
CRISPR), PASSES strongly (OR 14.10, recall 0.51). Host-embeddedness does NOT decide FBA reliability; **GEM-topology
quality does — and that is NOT knowable a-priori for a novel organism** (Plasmodium fails, Toxoplasma passes;
both host-dependent; n=2, with a GEM-curation/screen-technology confound).

## The router change (v2 → v3, in `src/intercepta/composite_router.py`)
`TRANSFER_GATE[FBA_ESSENTIALITY]`:
- FULL-grade `domain` = `{BACTERIUM, FREE_EUKARYOTE}` — **UNCHANGED**.
- NEW capped/uncertain transfer domain: `uncertain_domain={HOST_DEPENDENT_PARASITE}`,
  `uncertain_requires="curated_gem"`, `confidence_cap=0.5` (a COARSE marker, not a calibrated probability), and
  the verbatim flag `uncertainty_note`:
  > "FBA-essentiality transfer to host-dependent organisms is GEM-topology-dependent, validated at only n=2
  > (Toxoplasma PASS OR 14.10 / Plasmodium FAIL OR 2.47); treat as lower-confidence, GEM-quality-contingent."
- `decide(...)` and `CompositeRouter.decide(...)` gain `has_curated_gem: bool = False`. Host-dependent + GEM →
  FBA fires capped+flagged (`uncertain=True`, `confidence_cap=0.5`, `uncertainty_flags=[...]`); host-dependent +
  no GEM → no signal → ABSTAIN (`HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION`).
- FUNCTIONAL_DEPENDENCY for a parasite is **UNCHANGED**: it still does NOT fire even with a GEM (TRANSFER1 — no
  parasite screen; DEPEND1's label-free arm not organism-transferred). Preserved as the integrity invariant.
- The old `HOST_DEPENDENT_PARASITE_ABSTENTION` / `HOST_EMBEDDED_ABSTENTION` names remain as backward-compatible
  aliases pointing at the no-GEM abstention (the sole remaining parasite-abstention case under v3). Its text no
  longer says "metabolic essentiality falsified" — HARDENP1 corrected that overgeneralization; the honest reason
  is now "no signal available without a GEM (FBA would fire capped-and-flagged IF a GEM existed)."

## The four pre-registered routing outcomes (all asserted, all PASS)
| Case | Input | Output | FBA | Key result |
|---|---|---|---|---|
| **(A)** | *Toxoplasma gondii*, host-dep, GOOD GEM iTgo2020 | **shortlist** (NO LONGER abstains) | **FIRES capped 0.5 + flag** | `uncertain=True`; a-posteriori HARDENP1 **OR 14.10 PASS** surfaced as retrospective validation (not an a-priori input); FD did not fire |
| **(B)** | *Plasmodium falciparum*, host-dep, salvage GEM iPfal19 | **shortlist** | **FIRES, SAME cap + SAME flag** | a-posteriori GENERALIZE5 **OR 2.47 FAIL** surfaced — this FAIL is EXACTLY why confidence is capped; the router could NOT have known a-priori |
| **(C)** | host-dep organism, NO GEM | **abstention** | gated (would fire capped IF a GEM existed) | reason = no-GEM constant; cites HARDENP1/GENERALIZE5/functional-dep non-transfer; NOT "metabolic essentiality falsified"; `uncertain=False` |
| **(D)** | bacterium / virus / human_cancer | shortlist(full) / structural / shortlist | full-grade / not-fired / not-fired | REGRESSION — all unchanged: bacterium FBA full-grade (`uncertain=False`, cap None), ENGINE cores {murA,murG,mraY,dxs} present; SARS-CoV-2 Mpro→protease, RdRp→polymerase; human_cancer functional-dependency fires |

**The two headline corrections:** (A) Toxoplasma no longer abstains — the router now attempts FBA where it in
fact works. (B) Plasmodium fires-but-flagged — the router surfaces a candidate shortlist at capped confidence and
is honest that this is the case where FBA fails; it does not blanket-fire at bacterial grade.

## Advisory diagnostic (INCLUDED, and honestly labeled)
An OPTIONAL screen-free GEM-topology descriptor was included: `gem_topology_advisory(...)` reports the
**fraction of model genes FBA-essential under default medium** (from committed results: Toxoplasma 141/556 =
0.2536; Plasmodium 80/475 = 0.1684). It is labeled **HEURISTIC / ADVISORY / NOT VALIDATED**,
`does_not_predict_fba_reliability=True`, and it **NEVER gates the router**. The script demonstrates the honest
limitation: at n=2 the descriptor does NOT separate the PASS from the FAIL a-priori — the FAILING organism
(Plasmodium, 0.1684) has the LOWER essential fraction than the PASSING one (Toxoplasma, 0.2536), so no usable
threshold/direction can be set. The true discriminators (recall 0.51 vs 0.20; base rate 0.42 vs 0.64) require the
very experimental screen a novel organism lacks. Separating a Plasmodium-type failure from a Toxoplasma-type
success a-priori is UNSOLVED. The advisory is offered as visible CONTEXT, explicitly NOT as a solution.

## Honesty / scope
This is a routing-LOGIC refinement + reuse of committed, reproduced-x2 results — no new wet-lab, no new
enrichment. The core admission is deliberate and encoded in the flag text: **the router cannot a-priori predict
FBA reliability on a novel host-dependent organism** (n=2, one pass / one fail, with a curation/technology
confound). It fires with flagged, capped uncertainty rather than pretending to know. The `confidence_cap=0.5` is
a coarse marker, not a calibrated probability. All outputs are candidate HYPOTHESES.

## Note on the earlier committed demos (COMPOSITE1/COMPOSITE2)
Their in-memory assertions still hold under v3 (verified): bacterium/virus/human_cancer routing unchanged, and
the parasite (no GEM by default) still abstains against the `HOST_EMBEDDED_ABSTENTION` alias. I deliberately did
NOT re-run their `run.py` (which would overwrite their committed metrics/SHA), because the parasite abstention
TEXT evolved from v2 to v3 — exactly the situation COMPOSITE2 itself documented when advancing v1→v2. The routing
BEHAVIOR is unchanged; only the abstention wording (now no-GEM-honest) differs.

## Reproducibility
`run.py` → `results/COMPOSITE3_metrics.json` (sorted keys) + `results/COMPOSITE3_payload.sha256`. Payload =
sorted-key JSON of the four routing decisions + capped-FBA a-posteriori reuse + advisory + assertion booleans
(excludes verdict/provenance). Run twice as separate processes; SHA-256 identical
(`f540c4a32e69841cb168e30ce9923a8ed1ab5ddca3dfc1becd4003fa25562d5f`). Pure logic + committed-result reuse; no
RNG. No git commit/push; no data committed.
