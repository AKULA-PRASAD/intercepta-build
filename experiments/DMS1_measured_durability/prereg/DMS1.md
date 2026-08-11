# DMS1 — measured deep-mutational-scanning durability: the D9 reopen via the "measured fitness" trigger (PRE-REGISTRATION)

*Locked 2026-08-11, BEFORE computing any DMS-tolerance↔resistance relationship. Dead-end D9 (durability) named
two reopen-triggers: "FEP/MD ΔΔG **or measured DMS fitness**." An ultra-analysis found the FEP path not cleanly
drivable (no drug-matched durable comparators in the antibacterial panel; blind-relay alchemical FEP is
inherently iterative = the forbidden trial-and-error). This experiment takes the **measured-DMS** trigger — the
superior, ground-truth instrument where it exists — and re-tests DYNAMICS5's exact falsified question with a
measured observable instead of the computational proxy. Falsify-first: given DYNAMICS5's result, the likely
outcome is another negative, which would close D9 HARDER (even measured fitness lacks the signal); that is a
reportable first-class result, not a hidden failure.*

## The question (identical to DYNAMICS5; only the observable changes)
Are drug-resistance positions measurably more **mutationally tolerant** (mutations there cost less fitness) than
other positions in the same protein? DYNAMICS5 asked this with masked-PLM **entropy** (a computational proxy) →
position-AUROC **0.446** (below chance, falsified). AMR1 asked the target-level analog with **conservation** →
composite AUROC **0.556** (failed). DMS1 asks it with **measured** DMS fitness — the reopen-trigger observable.

## Data (all cached; open)
- **Observable — measured DMS fitness:** ProteinGym v1.1 substitution assays for drug-target/resistance proteins
  (`$INTERCEPTA_DATA/dms1/`): TEM-1 β-lactamase (`BLAT_ECOLX` ×4 studies), *E. coli* DHFR / trimethoprim target
  (`DYR_ECOLI` ×2), aminoglycoside acetyltransferase (`AACC1_PSEAI` ×1). Fields: `mutant`, `DMS_score`
  (organismal-fitness; higher = more fit/tolerant). Per position *i*: **tolerance T_i = mean DMS_score over all
  measured substitutions at i** (uses ONLY measured fitness — no resistance annotation).
- **Labels — resistance positions (independent of the observable):** CARD `card.json` protein-variant-model SNP
  positions, WT-verified against the reference sequence, parsed EXACTLY as DYNAMICS5 (`model_param.snp.param_value`
  = [WT][pos][mut], kept iff 1≤pos≤L and seq[pos-1]==WT). A DMS protein enters the panel only if a CARD
  protein-variant-model reference sequence matches its DMS target sequence (identity ≥ 0.95); matched panel + n
  frozen in the build log before scoring.

## Non-circularity (the crux)
The observable (measured DMS fitness) and the label (CARD resistance position) come from **independent sources**
(a mutagenesis fitness assay vs a curated resistance-variant database). Neither uses the other. Forbidden:
using the DMS score to define resistance, or CARD to define tolerance.

## Falsifiable gates (locked)
- **H1 (the reopen):** pooled across the matched panel, DMS tolerance T separates resistance from non-resistance
  positions with **bootstrap 95% CI lower bound > 0.60** (2000 resamples, seed 42; direction pre-specified —
  resistance positions *more* tolerant, the durability hypothesis). Per-protein AUROCs reported.
  - **PASS → D9 REOPENS via measured data:** durability IS a measurable positional-tolerance property (even
    though the sequence proxies failed) → motivates the FEP/DMS follow-on. **I commit: if H1 passes, drive the
    FEP follow-on** to generalize beyond DMS-covered targets.
- **H2 (measured beats computed — head-to-head):** DMS-tolerance AUROC exceeds the sequence-conservation-tolerance
  AUROC (the AMR1-F1 analog, computed on the same positions) with a paired-bootstrap delta 95% CI excluding 0.
- **FAIL (H1 not met) → HONEST NEGATIVE, D9 CLOSES HARDER:** even *measured* mutational fitness does not mark
  resistance positions as more tolerant → durability is not a general positional-tolerance property by any
  observable (computed or measured); resistance emergence is a drug-binding-specific / epistatic property the
  single-mutant tolerance landscape does not carry. Reported as prominently as a pass.

## Scope (honest, binds the claim)
Small-n panel of well-characterized enzymes (β-lactamase/DHFR/AAC), position-level within-protein test (as
DYNAMICS5). A MEASURED delineation of whether durability is a positional-tolerance property — NOT a general
durability law (D9's generalization concern stands regardless of verdict). Not clinical.

## Rigor
Reproduce ×2 byte-identical (deterministic; seed 42 bootstraps). CPU. `results/DMS1_metrics.json` (sorted keys)
+ `payload.sha256`. CARD + DMS data cached in `$INTERCEPTA_DATA`, never committed. No gate changed after scoring;
any deviation appended as a dated CORRECTION.
