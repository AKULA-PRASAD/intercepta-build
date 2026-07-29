# Pre-registration — B11: cross-system replication of NOVEL BeatAML markers (FINALIZED 2026-07-29, pre-run)

## Question
Do the NON-textbook (novel) mutation→drug-sensitivity associations discovered genome-wide in BeatAML (B5, BH<0.05,
FLT3-ITD/prolif-deconfounded, split-replicated) REPLICATE in an INDEPENDENT system — pan-cancer DepMap cell lines
with matched somatic mutations + drug response (PRISM/GDSC)? A novel marker that replicates across patient AML →
cell-line systems is a genuine (if modest) discovery; one that doesn't is AML-specific or spurious.

## Pre-declared pairs (novel = sensitizing, BHq<0.05 in B5, not FLT3-ITD/RAS→MEK/IDH→IDHi/FLT3→FLT3i; drug in GDSC/PRISM)
DNMT3A→saracatinib; NRAS→mk-2206; NRAS→bortezomib; NRAS→alvocidib(flavopiridol); IDH2→saracatinib; IDH2→vandetanib;
IDH2→afatinib; IDH2→nvp-tae684; IDH2→doramapimod; IDH2→tozasertib; U2AF1→cediranib; U2AF1→pelitinib; WT1→raf265; BCOR→raf265.

## Data (public; no gate)
DepMap non-silent somatic mutations (MAF) + drug response: PRISM secondary AUC (primary; on DepMap cells) or GDSC2
LN_IC50 (fallback, via COSMIC↔DepMap). Pan-cancer cell lines (AML lines too few alone).

## Test + decision rule (fixed)
Per pair, cell lines with mutation status + drug response (≥8 mutant, ≥8 wild-type): Mann–Whitney response
(mut vs wt) + effect direction. Sensitizing in cell lines = mutant has LOWER AUC/LN_IC50 (more sensitive), MATCHING
the BeatAML direction. **REPLICATED** = BH-FDR<0.05 across the tested pairs AND same (sensitizing) direction.
Report per-pair even if null. Also report a lineage caveat: pan-cancer, unadjusted for lineage (a positive that is
lineage-confounded is flagged, not claimed).

## Honesty / scope
Pan-cancer cell lines are a DIFFERENT context than AML patients; non-replication may mean AML-specific (still real,
context-bound) OR spurious. Small mutant-line counts for rare genes (IDH2/U2AF1) → underpowered; expect mostly
null. A single robust cross-system replication would be a genuine, honestly-modest discovery worth pursuing — NOT
a "breakthrough" claim by itself.

## Reproducibility
Deterministic (MWU); BH across pairs; reproduce ×2. Output: `experiments/B11_novel_replication/results/B11_metrics.json`.
