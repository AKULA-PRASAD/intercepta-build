# PARARESOLVE2 — Screen-technology ROBUSTNESS probe (Bushell 2017 *P. berghei* barseq-KO) — SUMMARY

**VERDICT: SPLIT / NUANCED — the screen-technology axis is NOT cleanly exonerated, but the *core* FBA failure
mode (recall ~0.2) IS screen-technology-robust; the pass/fail gate itself is base-rate-fragile.** The two Pf
GEMs literally *swap* pass/fail between the two screen technologies. Reported without spin. Reproduced x2
byte-identical.
**payload sha256:** `9ce7228a6b98a4afe83bf597ea792e5726a0969744c22d668c0266e2bd78f2d3`
**Evidence tier:** COMPUTED (in-silico enrichment vs a published screen; not wet-lab).

## HARD SCOPE (non-negotiable, stated up front)
This is a **screen-technology ROBUSTNESS probe** using a THIRD technology — Bushell 2017 targeted
double-crossover gene knockout + barseq relative growth rate (distinct from Zhang piggyBac and from Sidik
CRISPR). It **does NOT close the CRISPR-specific axis**: no genome-wide saturating *P. falciparum* CRISPR
essentiality screen exists. Bushell screened ***P. berghei***; it is scored on the *P. falciparum* GEMs via
Bushell's authoritative PlasmoDB **Pf-ortholog column** — a **cross-species (Pb->Pf) mapping**. Bushell is a
**partial-genome** screen (2578 genes). This is robustness evidence only; the word "closure" is not used.

## Data obtained (open access)
Bushell et al. 2017, **Cell 170(2):260** (PMID 28708996, **PMCID PMC5509546, isOpenAccess=Y**). Supplementary
bundle via Europe PMC REST `.../PMC5509546/supplementaryFiles` (zip sha256 `c51a7656...`). Truth table =
**Table S1 / mmc1.xlsx** (sha256 `b1d99066...`), extracted to `bushell2017_tableS1.csv` (sha256 `cc0cfd26...`).
Essential call = **authors' own `Phenotype` label** (barseq RGR), NOT an invented cutoff. Whole-table classes:
Essential 1196 (RGR 0.003-0.482), Slow 456 (0.154-0.974), Dispensable 911 (0.596-1.160), Insufficient data 13
(excluded), Fast 2. PRIMARY essential = "Essential"; SENSITIVITY = "Essential"|"Slow".

## GEM + mapping (option (b))
No open CPU-only *P. berghei* GEM identified; Bushell's PlasmoDB `P. falciparum ID` column is a cleaner Pb->Pf
ortholog than ad-hoc RBH, so both PARARESOLVE1-validated Pf GEMs were scored via that column. Coverage
(definitive-mapped / model genes): **iPfal19 268/475 = 0.56; iAM-Pf480 297/480 = 0.62** — lower than Zhang's
~0.89 (Bushell is partial-genome); reported honestly.

## Result (gate OR>3 & p<0.01), against the two anchors
| GEM | vs **Zhang piggyBac** (prior) | vs **Bushell barseq-KO** PRIMARY (Essential) | Bushell base rate | recall |
|---|---|---|---|---|
| **iPfal19** (PARADIGM, ref) | OR **2.47 FAIL** (GENERALIZE5) | OR **3.667 PASS**, p 1.8e-4, prec 0.72 | 0.46 | **0.25** |
| **iAM-Pf480** (UCSD, indep) | OR **3.07 PASS** (PARARESOLVE1) | OR **2.261 FAIL**, p 9.6e-3, prec 0.58 | 0.41 | **0.22** |

Anchor for scale: Toxoplasma iTgo2020/Sidik CRISPR **14.10 (PASS)**. SENSITIVITY (Essential+Slow): iPfal19 OR
**5.699 PASS** (base 0.675, prec 0.91), iAM-Pf480 OR **2.943 FAIL** (base 0.643) — same split, larger spread.

## What this actually shows (brutally honest)
1. **The two GEMs SWAP pass/fail across screen technologies.** iPfal19 fails Zhang (2.47) but passes Bushell
   (3.67); iAM-Pf480 passes Zhang (3.07) but fails Bushell (2.26). So the pass/fail **verdict is NOT
   screen-technology-robust** — screen/dataset specifics DO move it. The clean pre-registered "ALSO fails ->
   tech axis exonerated" branch did **not** fire; neither did a clean "passes -> piggyBac implicated." The
   honest outcome is a **GEM x screen interaction**, not a one-directional answer.
2. **BUT the underlying failure mode IS screen-technology-robust.** **Recall stays ~0.19-0.25 in every
   GEM x screen x definition cell** — FBA systematically misses ~75-80% of experimentally essential metabolic
   genes regardless of whether the screen is piggyBac or barseq-KO. This is exactly the HOSTCTX/PARARESOLVE1
   salvage-bypass signature (essentials read dispensable), and it is invariant to screen technology. THAT is
   the robust finding.
3. **The pass/fail flip is largely a BASE-RATE-of-the-truth-label artifact, not new biology.** Bushell's strict
   "Essential" label gives base rate ~0.41-0.46 among mapped metabolic genes vs Zhang's 0.64 - a lower base
   rate mechanically **decompresses** the OR, lifting iPfal19 from 2.47 to 3.67 across the OR>3 line without
   the model improving. (PARARESOLVE1 already showed OR is base-rate-capped for Pf.) Conversely iAM-Pf480
   drops below the line on the different Pb-orthologous gene subset. The OR>3 gate sits **right at
   Plasmodium's noise floor**, so which GEM clears it is fragile to truth-definition and gene sampling.
4. **The Pf-vs-Toxoplasma gap does NOT close under any screen.** Best Pf value is 3.67 (primary) / 5.70
   (sensitivity) - still **~2.5-4x below Toxoplasma's 14.10.** No screen-technology swap brings Plasmodium to
   Toxoplasma-grade enrichment.

## Which way it points
**Mixed, and honestly so.** The screen-technology axis is **NOT exonerated** - dataset/technology specifics
flip the binary verdict, so PARARESOLVE1's "piggyBac vs CRISPR" caveat is at least partly vindicated: screen
choice matters. **But** the *mechanism* of failure (low recall from salvage-bypass) and the *ceiling* (never
near Toxo's 14.10) are screen-technology-invariant, so the deeper GEM-topology + base-rate story from
PARARESOLVE1 also survives. Net: **the Plasmodium FBA result is jointly governed by GEM topology AND
truth-set base rate AND screen/dataset sampling - it is multi-causal, and the OR>3 gate is too knife-edge for
Plasmodium to give a stable one-word verdict.**

## Residual confounds that REMAIN unresolved
- **CRISPR-specific axis: still NOT closed** (no genome-wide Pf CRISPR screen exists).
- **Species:** Bushell is *P. berghei*, scored on *P. falciparum* GEMs via ortholog - cross-species.
- **Partial-genome + ~56-62% GEM coverage** (vs Zhang ~89%): lower power; possible mapping-selection effect.
- **Base rate / GEM topology residual** (PARARESOLVE1): not eliminated by a screen-technology swap.

## Provenance
Bushell Table S1 (mmc1) authors' Phenotype label; PlasmoDB Pf-ortholog column for Pb->Pf mapping. GEMs:
iPfal19 (`$INTERCEPTA_DATA/generalize5/iPfal19.xml`), iAM-Pf480 (`$INTERCEPTA_DATA/pararesolve1/pfal2018_abdel_haleem.xml`).
cobra 0.31.1, GLPK, KO growth rounded 6dp. Estimator FROZEN to sample OR + math.comb one-sided
hypergeometric. Gate frozen in PREREG.md before scoring; both outcomes pre-allowed. Reproduced x2
byte-identical, payload sha256 `9ce7228a6b98a4afe83bf597ea792e5726a0969744c22d668c0266e2bd78f2d3`.
NOT git-committed; data not committed.
