# HOSTCTX1 — does E-Flux (expression-constrained context-specific FBA) RESCUE the malaria essentiality signal? — SUMMARY

**GATE: NEGATIVE — honest first-class negative.** Adding host/biological context via E-Flux does NOT rescue (or even
move) the essentiality signal. The wall is deeper than expression-context. Reproduced x2 byte-identical.
**payload sha256:** `a3c5c3c21dfd277384ad036e9a51f7885e19ba9b12922e44b7b67beb7ce7064f`
**Evidence tier:** COMPUTED (in-silico enrichment; not wet-lab). n=1 parasite, blood-stage.

## Baseline anchor — REPRODUCED (Y)
Plain default-medium FBA on iPfal19 recomputed in this script recovers GENERALIZE5 EXACTLY:
OR **2.469**, Fisher p 0.00217, precision 0.797, recall 0.201, AUROC 0.559, contingency **both 55 / FBA-only 14 /
exp-only 218 / neither 137**, n=424 mapped. `baseline_reproduced_vs_GENERALIZE5 = True`. The A/B is valid.

## Expression source
**Malaria Cell Atlas** (Howick et al. 2019 *Science* 365:eaaw2619; single-cell RNA-seq across the *P. falciparum* life
cycle; open via PlasmoDB / malariacellatlas.org), asexual blood-stage mean expression per PF3D7_ gene, redistributed in
the PlasmoDB / Pf Target Browser annotation table (Figshare 27190545). Extract sha256
`936a0f4af14fdbe965042c91a2cbbb077645d8eff1fde822edf457406513a206`. Coverage: **412/475** model genes match MCA
directly, +1 via alias, 62 fall back to the covered-gene median (0.364). Primary stage = Trophozoite.

## Plain FBA vs E-Flux — side by side (primary, trophozoite)
| metric | PLAIN FBA | E-FLUX (troph) | delta |
|---|---|---|---|
| odds ratio | 2.469 | **2.469** | 0.000 |
| Fisher p (one-sided) | 0.00217 | 0.00217 | - |
| precision | 0.797 | 0.797 | 0.000 |
| recall | 0.201 | 0.201 | **0.000** |
| AUROC | 0.559 | 0.572 | +0.013 |
| contingency (both/FBAonly/exponly/neither) | 55/14/218/137 | 55/14/218/137 | identical |

The binary essential set is **byte-identically the same 80 genes** (symmetric difference = 0). Only the continuous
growth-ratio ranking shifts marginally (AUROC +0.013, still ~0.5 = near-random). Recall stays pinned at 0.20 — the 218
experimentally-essential-but-FBA-dispensable genes are NOT recovered.

## Robustness to E-Flux scaling — verdict does NOT flip
Every sensitivity variant returns the **exact same contingency 55/14/218/137** and OR 2.469:
- stage = Ring / Schizont / IDC-average (mean of Ring+Troph+Schizont): identical.
- scaling = median-norm uncapped (WT growth 47.4), capped-at-1000 (WT 29.6, 331/662 reactions genuinely tightened),
  max-normalization (WT **crushed to 3.63**, ~88% below baseline): identical essential set.
- epsilon = 1e-3 or 0: identical.

Even the most aggressive tightening (maxnorm, which slashes achievable biomass by ~88%) does not flip a **single**
essentiality call. The conclusion is fully robust to the arbitrary E-Flux scaling choice.

## Honest mechanism (why E-Flux cannot rescue here)
E-Flux scales flux *capacities* but never fully shuts a reaction (all 662 gene-associated reactions have positive
expression, so all keep positive bounds). Single-gene-KO essentiality is governed by GPR **bypass structure** — can
biomass route around the deleted reaction? — not by flux *magnitude*. The host-RBC salvage "workarounds" that made 218
essential genes read FBA-dispensable in GENERALIZE5 are themselves expressed, so they retain capacity and remain
available. Reducing their throughput (even to 12% of baseline) leaves them topologically usable, so the KO still finds
the same detours. Expression context reshapes flux distribution but not the essentiality topology.

## Meaning
Expression-constrained context-specific FBA (E-Flux) is a NEGATIVE for rescuing host-dependent-parasite essentiality:
the failure in GENERALIZE5 is not an over-permissive-flux artifact that transcriptomics can fix — it is structural
(salvage routes exist in the network topology). A real rescue would require **removing** salvage reactions (medium /
gap-fill / host-exchange curation) or integrating host-parasite compartment modeling, not down-weighting flux by
expression. Scope: essentiality-enrichment only; in-silico vs a published screen; one stage / one atlas / one curated
model; n=1 parasite; not drug-target/clinical; not wet-lab.

## Provenance
iPfal19 sha `7a19f5b7...`, Zhang sha `b8790819...`, MCA expression sha `936a0f4a...`. cobra 0.31.1, GLPK, KO growth
rounded 6 dp. Gate frozen in PREREG.md before scoring. payload sha256
`a3c5c3c21dfd277384ad036e9a51f7885e19ba9b12922e44b7b67beb7ce7064f` (reproduced x2).
