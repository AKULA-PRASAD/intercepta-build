# GENERALIZE4 — FBA essentiality bacteria → EUKARYOTE (*S. cerevisiae*) — SUMMARY

**GATE: PASS** (same OR>3 AND p<0.01 gate as every bacterium; frozen before scoring; orchestrator-verified).
Reproduced ×2 byte-identical.
**payload sha256:** `c5386549b8a315df5c8987193169c76bac3a3fde2158949a173ebf8db67e9903`
**Evidence tier:** VERIFIED (in-silico FBA vs an external gold-standard experimental deletion set). Model
eukaryote, not a direct *C. albicans* claim.

## Organism choice (deliberate, disclosed)
*Saccharomyces cerevisiae* — the single cleanest eukaryotic essentiality label in existence (Giaever 2002
genome-wide systematic deletion collection, DEG2001) + curated benchmark GEM iMM904 (BiGG). *Candida albicans*
is the true fungal-pathogen goal, but S. cerevisiae maximizes ground-truth quality for a first
bacteria→eukaryote generalization test; the essential metabolic machinery is shared with fungal pathogens.

## Result (gate frozen before scoring)
COBRApy single-gene-deletion FBA on iMM904 (essential if KO growth <1% WT, mirroring CROSSVAL_curated) vs
DEG2001. **OR 4.65, Fisher p 1.64e-10, precision 0.364, recall 0.315, AUROC 0.610.** Universe 905 metabolic
genes; contingency both 40 / FBA-only 70 / exp-only 87 / neither 708. ID mapping clean:
1107/1110 DEG essentials resolved to systematic ORF names via SGD_features.tab — no namespace artifact.

## Meaning + honest caveats
The FBA-essentiality signal — validated so far only in bacteria — **transfers across the prokaryote/eukaryote
divide** (highly significant). But it is **somewhat weaker than the strongest bacterial cases** and does not
strengthen in yeast. Medium asymmetry caveat (fair, same as the bacterial pipeline): iMM904 runs
glucose-minimal-style while Giaever essentiality is rich-medium (YPD) → in-silico biosynthetic essentials
inflate FBA-only (70) and cap precision. Scope: essentiality-enrichment only; in-silico vs published lab data
(not wet-lab); recall bounded by the metabolic subproteome; model eukaryote, not *C. albicans*.
