# F3CLIN1 — Do DEPEND1 SELECTIVE cell-line dependencies bridge to PATIENT-tumor DRIVER biology? — PRE-REGISTRATION

*Written and frozen BEFORE any scoring. Confronts FAILURE_AUDIT F3. Rigor constitution: falsify-first,
negatives first-class, reproduce ×2 byte-identical, pre-registered numeric gate, mandatory study-bias +
pan-essential guards, NO drug-response / clinical-outcome claim.*

Date frozen: 2026-08-05. Seed: 42. K (random-null permutations) = 10000.

---

## 0. Motivation (one paragraph, and what this is NOT)
INTERCEPTA's human DRUG-RESPONSE prediction line is tested-and-largely-NEGATIVE: B20 (FIMM 2nd-cohort external
replication) FAILS, B10 (TCGA) is cancer-type CONFOUNDED, B17 (BeatAML survival) is an honest NULL, B9 (PDXE)
null. What IS validated is DEPEND1: SELECTIVE CRISPR dependency recovers known actionable cancer targets, the
signal generalizes to disjoint held-out cell lines, and a label-free expr→dependency arm works — but all on
DepMap cancer CELL LINES, not patients. F3CLIN1 tests one specific, honest bridge that is DISTINCT from (and
not contaminated by) the failed drug-response line: **are the cell-line SELECTIVE dependencies enriched for
genes that are recurrently altered as DRIVERS in PATIENT tumors?** This is a TARGET-RELEVANCE claim
(cell-line→patient biology), NOT a drug-response prediction and NOT a clinical-outcome claim.

## 1. Data (open, public; not committed)
- **Selective-dependency gene set** — REUSED from DEPEND1 by RE-DERIVING with DEPEND1's EXACT frozen definition
  (below) from `depmap_crispr_gene_effect.csv`
  sha256 `d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00` (1095 lines × 17931 genes).
  DEPEND1 reported selective_n = 3664; re-derivation must reproduce this exactly.
- **PATIENT driver ground truth** — IntOGen Compendium of Cancer Genes, release **2024-06-18**
  (`Compendium_Cancer_Genes.tsv`), downloaded from https://www.intogen.org/download
  (`IntOGen-Drivers-20240920.zip`, LICENSE = **CC0 1.0** / public domain).
  zip sha256 `854def4465bcd7f90f0f8c7857dee9a4cf9da66a4c477c3fe4abeb510358a53c`;
  Compendium sha256 `7c1982aa1fae1ff8200f4c2811cdb1707ea3f778b5e95782798d09e792ddb5e8`.
  633 unique driver genes across 260 cohorts / 86 cancer types, each with patient RECURRENCE
  (n_cohorts, n_cancer_types, total mutated SAMPLES) — this is a patient-tumor driver set WITH recurrence,
  as preferred. IntOGen callers (dNdScv/OncodriveCLUSTL/HotMAPS/etc., q<0.1) define drivers by significant
  positive selection in patient tumor sequencing — driver biology, not fame.
- **Study-bias proxy** — `NUM_PAPERS` (CancerMine literature citation count per gene) from the accompanying
  `Unfiltered_drivers.tsv` (same zip). Covers 7716 genes (7339 of the DepMap universe). Used to build a
  publication-matched background and a stratified (Mantel–Haenszel) control. Honest caveat recorded: CancerMine
  driver-citation counts are partially circular with driver status, so this is a CONSERVATIVE (possibly
  over-correcting) study-bias control.
- Env: pandas 2.3.3, numpy 1.26.4, scipy 1.16.3, sklearn 1.8.0, CPU-only. Seed 42.

## 2. Definitions (frozen — copied from DEPEND1 §2)
- **Dependent call:** Chronos gene-effect `< -0.5`. **dependent_fraction(g)** = fraction of screened lines
  in which g is dependent.
- **PAN-ESSENTIAL** (excluded, confound guard): `dependent_fraction > 0.90`.
- **SELECTIVE dependency** (the validated target signal, THIS experiment's test set):
  `0.01 ≤ dependent_fraction ≤ 0.50`.
- **UNIVERSE** for all enrichment tests = the 17931 DepMap-screened genes (the set that COULD be called a
  selective dependency). Driver genes are intersected into this universe (622 of 633 are screened; 11 not
  screened in DepMap are recorded but cannot enter the 2×2).
- **PATIENT DRIVER** = SYMBOL present in the IntOGen Compendium (IS_DRIVER=True).
- **Recurrence tier (frozen):** `recurrent driver` = driver detected in `n_cohorts ≥ 5`
  (≈ the observed 75th percentile of driver recurrence; a fixed, data-independent threshold set here before
  scoring); `focal/rare driver` = driver with n_cohorts < 5. Used for the supporting dose-response check only.
- **selectivity_strength(g)** (frozen, for the reverse-direction sanity only):
  `mean(effect over all lines) − mean(effect over the most-dependent 5% of lines)` (i.e. how much deeper the
  gene's dependency runs in its most-sensitive 5% of lines vs its overall mean). Higher ⇒ more selectively
  essential. Ranked DESCENDING within the SELECTIVE set. No gate depends on this; it is a descriptive sanity.

## 3. Primary test
2×2 over the UNIVERSE (17931 genes): {SELECTIVE vs not-selective} × {PATIENT-DRIVER vs not}.
Fisher exact → odds ratio (OR) + two-sided p. Report the four cell counts and both marginal rates.

## 4. Guards (all mandatory)
1. **PAN-ESSENTIAL** already excluded from the selective set (§2) — housekeeping cannot inflate.
2. **STUDY / ANNOTATION BIAS** — drivers are famous/well-studied. Handled THREE ways:
   (a) **Random-gene null (full universe):** K=10000 random gene sets of size = n_selective drawn from the
       universe; null distribution of the driver-overlap count and of the OR. Empirical one-sided p =
       (#{null_overlap ≥ observed}+1)/(K+1).
   (b) **Publication-matched null:** restricted to universe genes with a NUM_PAPERS value; draw background gene
       sets matched to the selective set's NUM_PAPERS DECILE distribution (K=10000); empirical p for the
       selective set's driver overlap vs this study-bias-matched background.
   (c) **Mantel–Haenszel OR** stratified by NUM_PAPERS decile (same restricted subset): pooled OR + p,
       testing whether selective→driver enrichment survives adjusting for publication count.
3. **SCOPE HONESTY** — TARGET RELEVANCE only. This does NOT test, and must NOT be read as, drug-response
   prediction (B20/B10/B17 negative) or clinical outcome. Stated in every claim.

## 5. PRE-REGISTERED GATE (frozen here, before scoring)
- **PASS** — the dependency target-ID surfaces patient-relevant driver biology — iff:
  Fisher **OR > 2 AND p < 0.01** (primary 2×2), **AND** random-null empirical p < 0.01 (guard 2a),
  **AND** it survives study bias: publication-matched-null empirical p < 0.01 (2b) **AND** Mantel–Haenszel
  **OR > 2 with p < 0.01** (2c).
- **PARTIAL** — Fisher OR > 2 AND p < 0.01 AND random-null p < 0.01 (real enrichment above a random-gene null),
  BUT it does NOT survive the study-bias controls (2b not significant, or MH OR ≤ 2 / not significant) ⇒
  enrichment is real vs random genes but is attenuated/explained by study/annotation bias — reported honestly.
- **NEGATIVE** — Fisher OR ≤ 2, or Fisher p ≥ 0.01, or not above the random-gene null.
- **Supporting (not gated):** recurrence dose-response — OR for `recurrent drivers` (n_cohorts≥5) expected ≥ OR
  for `focal drivers`; reverse-direction sanity — fraction of top-{50,100,200} selectivity_strength genes that
  are patient drivers, vs the universe base rate, with a few named examples.

## 6. What a PASS does and does NOT establish (frozen honesty statement)
A PASS shows ONLY that cancer CELL-LINE selective CRISPR dependencies are ENRICHED for genes that are recurrent
DRIVERS in PATIENT tumors (a cell-line→patient TARGET-RELEVANCE bridge). It does **NOT** rescue patient
drug-RESPONSE prediction (B20 FIMM FAILS, B10 TCGA confounded, B17 BeatAML null), is **NOT** clinical outcome,
is **NOT** a wet-lab or novel-pathogen result, and carries the study/annotation-bias caveat even after the
controls above. A positive here must never be read as "clinical validation."

## 7. Reproducibility
All RNG seeded (42). Payload = sorted-key JSON of all numeric results EXCLUDING `verdict`/provenance
(`git_sha`,`timestamp_utc`,`python`,`pandas`,`scipy`). Script run twice; SHA-256 of payload printed and
matched; `results/payload.sha256` written. NEVER git commit/push. NEVER commit data.
