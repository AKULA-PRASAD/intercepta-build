# AMR1 — Zero-data RESISTANCE-LIABILITY predictor for antibacterial targets (PRE-REGISTRATION)

**Frozen before any scoring.** Author: AMR1 module. Env: intercepta-build (scoring/stats) + bioinfo (mmseqs conservation/paralogs). Zero budget, CPU-only, open data.

## Problem / gap
INTERCEPTA validates target ESSENTIALITY (VAL-ESS/CROSSVAL/PREDVAL) and metabolic-bypass resistance-robustness (SYNLETH1/BESTINT1), but does NOT predict whether an essential target is a *durable* drug target or one where clinical resistance emerges trivially (rpoB/rifampin, gyrA/fluoroquinolone, katG/isoniazid). A target-ID system for the fullest antibacterial vision must FLAG resistance-prone targets. AMR1 builds a **zero-data resistance-liability score** from objective target biology and tests whether it separates documented HIGH- from LOW-liability targets **without using any resistance rate/MIC as input**.

## Ground truth (frozen: `ground_truth.json`)
n = 17 antibacterial targets, each label from a REAL cited source (CARD / WHO 2023 catalogue / landmark review). 9 HIGH-liability (single-step target-site mutation or dispensable-activator loss: rpoB, gyrA, parC, rpsL, katG, inhA, embB, pncA, folP) vs 8 LOW/durable (murA, alr, ddlB, dxr, murG, mraY, murB, murF). Liability is graded; binary HIGH/LOW is a defensible ordinal collapse (ordinal field also stored). Honest asymmetry, pre-declared: 4 LOW targets are UNDRUGGED cell-wall cores whose "resistance rare" partly reflects low clinical exposure — flagged (`clinical_exposure`) and a drugged-only sensitivity is reported.

## Zero-data features (inputs; NO resistance data used) — all oriented so HIGHER = MORE liability
- **F1 mutational tolerance = 1 − conservation.** conservation = mean best-hit fraction-identity of the target protein across a fixed panel of 7 diverse bacterial proteomes (mmseqs easy-search, `--threads 1`, e≤1e-5), 0 for no homolog. Hypothesis: a highly-conserved active site (low tolerance) resists escape mutations → LOW liability.
- **F2 prodrug-activator dispensability** ∈ {0,1}: the drug requires a *dispensable* activator gene whose loss-of-function is tolerated (katG, pncA). Curated biology fact (drug pharmacology + activator non-essentiality), cited; declared the most mechanism-informed feature → reported WITH and WITHOUT F2.
- **F3 target redundancy (paralogs)** = count of same-proteome paralogs (mmseqs self-search, fident≥0.30, e≤1e-5, excluding self), min-max normalized. Hypothesis: a paralog/isozyme rescues loss → HIGHER liability.
- **F4 metabolic bypass** ∈ {0,1}: reused from SYNLETH1 iML1515 classes (combination_required/non_essential → bypassable=1; monotherapy_robust=0; non-metabolic targets → 0, no known metabolic reroute). Hypothesis: a bypassable target escapes via reroute → HIGHER liability.

**Composite liability = unweighted mean(F1,F2,F3,F4).** NO fitted weights (no ground-truth of "best liability weighting" exists → fitting would fabricate confidence and is tuning-to-pass). Deterministic; fixed params; cached mmseqs outputs.

## Pre-registered hypothesis & gate (frozen BEFORE scoring)
**H1:** the zero-data composite liability score separates documented HIGH- from LOW-liability targets above chance.
**Primary gate — PASS iff:** composite AUROC(score vs HIGH=1) **≥ 0.70** AND Mann-Whitney U p **< 0.05**.
**Baseline:** random AUROC = 0.50 (no-skill).
**NEGATIVE (first-class):** AUROC < 0.70 or p ≥ 0.05 → the zero-data biology features do NOT predict clinical resistance liability → an honest bound: resistance emergence needs data the target's static biology alone does not carry.
**Mandatory regardless of verdict:** per-feature AUROC **ablation** (which feature carries the signal), the F2-removed composite AUROC, and a drugged-only-LOW sensitivity AUROC.

## Analyses (all reported)
1. Composite AUROC + Mann-Whitney U p (primary gate).
2. Per-feature AUROC (F1,F2,F3,F4) — ablation.
3. Composite-without-F2 AUROC (guards against the answer riding on the one mechanism-informed feature).
4. Drugged-only sensitivity (drop the 4 undrugged LOW cores) AUROC.

## Reproducibility
SHA-256 over sorted-key JSON of the payload (per-target features + scores + all AUROC/p), EXCLUDING verdict/provenance/runtime. Run twice; require BYTE-IDENTICAL. mmseqs `--threads 1` for determinism; fixed seeds. Data to `$INTERCEPTA_DATA/amr1/`; NEVER committed.

## Honest scope (binds the result)
Predicts a resistance-liability CLASS from zero-data biology, NOT actual resistance rates/MICs/time-to-resistance. In-silico; modest cited n=17 (wide AUROC CI); graded labels collapsed to binary; multi-organism targets scored from a single reference ortholog; F4 non-metabolic targets defaulted to 0. Hypotheses, not wet-lab. Not tuned to pass; if it fails, the NEGATIVE is the result.
