# AMR1 — Resistance-liability predictor for antibacterial targets: SUMMARY

**Verdict: NEGATIVE (first-class, pre-registered).** Zero-data static target biology does NOT predict documented clinical resistance liability. Composite AUROC = **0.556** (Mann-Whitney p = **0.74**), below the pre-registered gate (AUROC >= 0.70 AND p < 0.05). Reproduced x2 byte-identical (payload SHA-256 `7e5be5581aad9bedd08b13bb3921d43f16a815306d7e3332833cd976876d0dfb`).

## What was tested
Can a zero-data resistance-liability score — composed only from objective target biology, with NO resistance rate/MIC as input — separate documented HIGH- from LOW-liability antibacterial targets? (Gap: INTERCEPTA validates essentiality + metabolic-bypass robustness but has no target-mutation/activator-loss resistance filter.)

## Ground truth (REAL, cited; ground_truth.json)
n = 17, balanced **9 HIGH / 8 LOW**. Each label cited to CARD (Alcock 2023, NAR), the WHO 2023 2nd-ed Catalogue of mutations in M. tuberculosis complex (ISBN 9789240082410), and/or landmark reviews (Blair 2015; Hooper 2016; Vilcheze 2014; Silver 2017; Skold 2000; Telenti 1997; Goldstein 2014; Nakatani 2017; Bugg 2011; Masini 2014).
- HIGH (single-step target-site mutation or dispensable-activator loss): rpoB/rifampin, gyrA/FQ, parC/FQ, rpsL/streptomycin, katG/isoniazid (activator), inhA/isoniazid, embB/ethambutol, pncA/pyrazinamide (activator), folP/sulfonamide.
- LOW/durable: murA/fosfomycin (target-mutation rare; resistance via uptake/FosA), alr & ddlB/D-cycloserine (rare/slow), dxr/fosmidomycin (low exposure), and 4 undrugged cell-wall cores murG/mraY/murB/murF (mechanistic-durable, flagged low-exposure).

## Features (zero-data, HIGHER = more liability)
F1 mutational tolerance = 1 - cross-ortholog conservation (mmseqs, 7-organism panel); F2 prodrug-activator dispensability (curated, cited); F3 paralog redundancy (mmseqs self-search); F4 metabolic bypass (reused from SYNLETH1 iML1515 classes). Composite = **unweighted mean** (no fitted weights — avoids tuning-to-pass).

## Result + ablation (which feature carries signal — none do)
| quantity | AUROC |
|---|---|
| composite (primary) | 0.556 (p=0.74) |
| composite without F2 | 0.500 (pure chance) |
| drugged-only sensitivity (n=13) | 0.472 (below chance) |
| F1 mutational tolerance | 0.569 |
| F2 activator dispensability | 0.611 |
| F3 redundancy (paralogs) | 0.500 |
| F4 metabolic bypass | 0.486 |

**No feature separates the classes.** The only feature with any lift (F2, 0.611) is the most mechanism-informed and fires for just 2 activator-loss cases (katG, pncA); remove it and the composite collapses to exactly chance (0.500).

## Why this is the honest answer (not a bug)
The HIGH single-step-mutation targets (rpoB, gyrA, folP, rpsL) are highly-conserved, single-copy, non-bypassable essential enzymes — biologically indistinguishable from the durable cell-wall cores (murA, mraY, murG) on every static feature. rpsL (streptomycin, canonical single-step K43R) is the MOST conserved protein in the set (cons 0.78) yet HIGH liability. Metabolic bypass actively ANTI-tracks liability: the durable cycloserine targets alr/ddlB are isozyme-buffered (bypass=1) while HIGH-liability folP is monotherapy-robust (bypass=0). Resistance emergence is a property of the drug-target-mutation dynamics (does a functional escape mutation exist, is the activator dispensable), which the target's static sequence/topology does not encode.

## Honest bound (the result)
Zero-data biology alone CANNOT predict antibacterial resistance liability at the pre-registered bar. The single partial signal — prodrug-activator dispensability — is mechanism-specific and does not generalize to target-site-mutation resistance, the dominant HIGH-liability route. Predicting resistance liability needs information the static target biology does not carry (functional mutational-scanning / clinical resistance data). Useful bound for target-ID: essentiality + bypass-robustness (already validated) do NOT double as a durability filter.

## Scope
In-silico; modest cited n=17 (wide AUROC CI); graded liability collapsed to binary; multi-organism targets scored from one reference ortholog; F4 defaults non-metabolic targets to 0; embB has no panel homolog (actinobacteria-specific -> F1 inflated, noted). Hypotheses, not wet-lab. Not tuned; the NEGATIVE is the pre-registered outcome.
