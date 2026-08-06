# COMPOSITE3 — PRE-REGISTRATION: honest refinement of the router's host-dependent-parasite FBA handling (router v3)

**Registered (Stage 1) BEFORE running `run.py`.** This file freezes the EXPECTED routing outcomes and the pass
conditions. The router change is a pure-logic edit to `src/intercepta/composite_router.py`; the validation reuses
ONLY committed, reproduced-x2 experiment results (HARDENP1, GENERALIZE5, DEPEND1, ENGINE, GENERALIZE3). No new
biology is computed; no data is committed; no git commit/push.

## Why (the correction being encoded)
Router v2 BLANKET-ABSTAINS on every host-dependent parasite for FBA-essentiality, on the n=1 premise
("metabolic essentiality is the wrong signal for host-embedded biology", GENERALIZE5 Plasmodium OR 2.47 +
HOSTCTX1/2 negatives). **HARDENP1 FALSIFIED that premise:** a second host-dependent parasite, *Toxoplasma gondii*
(curated iTgo2020 vs Sidik-2016 CRISPR), PASSES strongly (OR 14.10, recall 0.51) — the opposite of Plasmodium
(OR 2.47, recall 0.20). So host-embeddedness does NOT decide FBA reliability; **GEM-topology quality does, and
that is NOT knowable a-priori for a novel organism** (both are host-dependent; one passes, one fails; n=2).

- Blanket-abstain is WRONG: it would refuse Toxoplasma, where FBA works.
- Blanket-fire (bacterial-grade) is WRONG: it would overclaim on Plasmodium, where FBA fails.
- **HONEST behavior (v3):** for a host-dependent parasite that HAS a curated GEM, FBA FIRES but at
  **capped/reduced confidence with an explicit uncertainty flag** — neither the class-level abstention nor
  full-grade confidence. If NO GEM exists, there is NO signal → the parasite STILL ABSTAINS.

This refinement ADMITS the router cannot a-priori predict FBA reliability on a novel host-dependent organism.

## The router change (frozen intent, v2 → v3)
`TRANSFER_GATE[FBA_ESSENTIALITY]`:
- `domain` (FULL-grade) = `{BACTERIUM, FREE_EUKARYOTE}` — **UNCHANGED**.
- NEW `uncertain_domain` = `{HOST_DEPENDENT_PARASITE}`, `uncertain_requires="curated_gem"`, `confidence_cap=0.5`,
  and the verbatim `uncertainty_note`:
  *"FBA-essentiality transfer to host-dependent organisms is GEM-topology-dependent, validated at only n=2
  (Toxoplasma PASS OR 14.10 / Plasmodium FAIL OR 2.47); treat as lower-confidence, GEM-quality-contingent."*
- `decide(...)` gains a `has_curated_gem: bool = False` runtime flag. Host-dependent + GEM → FBA fires
  capped+flagged (`uncertain=True`, `confidence_cap=0.5`); host-dependent + no GEM → no signal → ABSTAIN.
- FUNCTIONAL_DEPENDENCY for a parasite is **UNCHANGED**: it still does NOT fire (TRANSFER1 — no parasite screen,
  DEPEND1 label-free arm not organism-transferred). It remains gated even when a GEM is present.
- A class-level abstention is preserved ONLY when NO signal (incl. capped FBA) is available.

## Optional advisory diagnostic (decision recorded here)
An OPTIONAL screen-free GEM-topology descriptor (fraction of model genes FBA-essential under default medium) is
included as **ADVISORY / HEURISTIC / NOT VALIDATED** context ONLY. It is explicitly NOT a predictor of FBA
reliability and does NOT gate the router. Pre-registered honest demonstration: at n=2 it does NOT separate the
PASS from the FAIL a-priori (Toxoplasma frac ≈0.25 PASS vs Plasmodium frac ≈0.17 FAIL — the FAILING organism has
the LOWER fraction, so no threshold/direction is established). Reported to make the limitation visible, never to
imply a solution.

## PRE-REGISTERED routing outcomes (asserted by run.py BEFORE inspecting any SHA)
| Case | Input | Expected output | FBA | Notes to assert |
|---|---|---|---|---|
| **(A)** | *Toxoplasma gondii*, host-dependent, GOOD GEM iTgo2020 (`has_curated_gem=True`) | **shortlist** (NOT abstain) | **FIRES, capped `0.5` + uncertainty flag** | `uncertain=True`; flag note is the verbatim GEM-topology sentence; a-posteriori HARDENP1 OR 14.10 PASS surfaced as retrospective validation (NOT an a-priori input); FUNCTIONAL_DEPENDENCY does NOT fire |
| **(B)** | *Plasmodium falciparum*, host-dependent, salvage GEM iPfal19 (`has_curated_gem=True`) | **shortlist** | **FIRES, SAME capped `0.5` + SAME uncertainty flag** | `uncertain=True`; a-posteriori GENERALIZE5 OR 2.47 FAIL surfaced — this FAIL is EXACTLY why confidence is capped; the router could NOT have known a-priori; SAME flag as (A) |
| **(C)** | host-dependent organism, NO GEM (`has_curated_gem=False`) | **abstention** | gated (would fire capped IF a GEM existed) | reason = `HOST_DEPENDENT_PARASITE_NO_GEM_ABSTENTION`; `uncertain=False`; cites no-GEM / HARDENP1 / GENERALIZE5 / functional-dependency non-transfer; NOT "metabolic essentiality falsified" |
| **(D1)** | *K. pneumoniae*, bacterium | **shortlist**, FBA **full-grade** (`uncertain=False`, cap None) | FIRES full | REGRESSION — unchanged; committed ENGINE cores {murA,murG,mraY,dxs} present |
| **(D2)** | SARS-CoV-2, virus (autodetected) | **structural_class_id** | NOT fired | REGRESSION — unchanged; Mpro→protease, RdRp→polymerase |
| **(D3)** | human_cancer | **shortlist**, functional-dependency FIRES (`uncertain=False`) | NOT fired (gated) | REGRESSION — unchanged (COMPOSITE2) |

## Pass condition
ALL pre-registered assertions across (A)–(D3) hold, AND the payload SHA-256 (sorted-key JSON, excluding
verdict/provenance) is byte-identical across two independent process runs.

## Scope / honesty bounds
This is a ROUTING-LOGIC refinement + reuse of committed results, not new wet-lab or new enrichment. The n=2
host-dependent FBA evidence carries a GEM-curation/screen-technology confound (HARDENP1). The capped confidence
(0.5) is a COARSE marker, not a calibrated probability. All outputs are candidate HYPOTHESES. The core honest
admission stands: the router fires FBA on a host-dependent organism with elevated, flagged uncertainty because it
CANNOT know a-priori whether that organism's GEM is Toxoplasma-like (pass) or Plasmodium-like (fail).
