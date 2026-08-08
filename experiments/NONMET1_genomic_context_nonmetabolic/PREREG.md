# NONMET1 — Pre-registration: Does CONSERVED GENOMIC CONTEXT (synteny) crack the non-metabolic essential half?

**Pre-registered BEFORE computing any outcome.** Analyst: INTERCEPTA NONMET1 module. Date: 2026-08-07.
This document locks the hypothesis, the exact deterministic scoring formula, the reference panel, all thresholds,
and the PASS/FAIL gate BEFORE any essentiality label is looked at against the context score.

## 1. The gap this addresses
FBA gene-essentiality (MET1–3, experimentally VALIDATED, VAL-ESS) is a genuine mechanistic, homology-independent
signal — but it is METABOLIC-SCOPED. It is blind to ~half of drug-target space: proteases, polymerases,
ribosomal / structural / translational essentials. Recall of FBA on experimental essentials is only 9–25%.
Raw sequence-conservation breadth partly covers the non-metabolic half (it recovers dnaE/ileS/leuS/secA/topA),
but that is the established BASELINE, not a new signal. MET4 tried PPI-network centrality for this half and it
COLLAPSED under study bias (literature-derived interaction edges track research attention, not biology;
lift +0.128 → −0.004 once a coexpression/study control was applied). We do NOT re-run MET4.

## 2. Hypothesis (novel; study-bias-RESISTANT by construction)
**Essentiality of NON-METABOLIC genes is encoded in CONSERVED GENOMIC CONTEXT.** Genes embedded in
synteny-conserved neighborhoods — those that keep the *same gene neighbors* co-located across many bacterial
genomes — are enriched for essentiality, and this signal is distinct from (adds beyond) the gene's own
sequence-conservation breadth. Genomic coordinates / gene order are NOT subject to research-attention bias the
way curated interaction databases are, so unlike MET4 this signal is structurally study-bias-free.
This is different from MET4 (PPI, literature-derived) AND from raw conservation (own-conservation breadth):
it is about NEIGHBORHOOD conservation, not the gene's own conservation.

## 3. Organisms (focal) and truth sets — locked
- **E. coli K-12 MG1655** (PRIMARY). Genome NC_000913.3 (local CDS FASTA, crispridesign1). Truth =
  **PEC** (PECData.dat, local; Class(1)=essential). Whole-genome experimental single-gene-knockout essentiality.
- **M. tuberculosis H37Rv** (GENERALITY). Genome NC_000962.3. Truth = **DeJesus 2017** Tn-seq
  (local dejesus_es_ids.txt; call == 'ES' = essential), Rv→UniProt via local rvmap.tsv.

## 4. Reference panel (fixed, 12 genomes; each focal scored vs the OTHER 11) — locked
RefSeq main-chromosome accessions, fetched via NCBI efetch `rettype=fasta_cds_na` (CDS-from-genomic nt FASTA,
carries [locus_tag] and [location]); SHA-256 of each fetched file recorded in the data manifest.
1. NC_000913.3  Escherichia coli K-12 MG1655           (local)
2. NC_000962.3  Mycobacterium tuberculosis H37Rv
3. NC_003197.2  Salmonella enterica sv. Typhimurium LT2
4. NC_002516.2  Pseudomonas aeruginosa PAO1
5. NC_000964.3  Bacillus subtilis 168
6. NC_007795.1  Staphylococcus aureus NCTC8325
7. NC_000915.1  Helicobacter pylori 26695
8. NC_002505.1  Vibrio cholerae O1 biovar El Tor chr I
9. NC_003112.2  Neisseria meningitidis MC58
10. NC_003028.3 Streptococcus pneumoniae TIGR4
11. NC_016845.1 Klebsiella pneumoniae HS11286 chromosome
12. NC_011916.1 Caulobacter crescentus NA1000

## 5. Non-metabolic subproteome (the half FBA cannot see) — locked
Metabolic = genes present in the organism's GEM (FBA-scoped), reusing the MET2 essentiality cache gene lists
($INTERCEPTA_DATA/met2/essentiality.tsv rows for that organism; these are exactly the GEM-modelled genes).
Non-metabolic subproteome = all protein-coding genes of the focal genome (from its CDS FASTA) that map to a
protein but are NOT in the MET2 metabolic gene set. Join key: E. coli = locus_tag (b-number); Mtb = Rv locus_tag.
All scoring, enrichment, and the PASS/FAIL gate are computed ON THE NON-METABOLIC SUBPROTEOME ONLY.

## 6. Orthology (deterministic) — locked
For each focal genome, CDS nucleotide sequences are translated (standard genetic code, table 11 start-agnostic,
translation stops at first in-frame stop) to protein. Orthologs between focal and each panel genome are
**reciprocal best hits (RBH)** via `mmseqs easy-rbh` with `--threads 1` (deterministic), thresholds:
min sequence identity `--min-seq-id 0.30`, coverage `-c 0.5 --cov-mode 0`, e-value `-e 1e-5`.
RBH (not unidirectional best-hit) is used so an "ortholog" is a mutual best match. mmseqs alignment outputs are
cached to $INTERCEPTA_DATA/nonmet1/ (data, never committed); run.py consumes the cache and is what is
reproduced ×2 byte-identical.

## 7. Genomic-context conservation score (EXACT formula, locked BEFORE scoring)
Let focal genes be ordered by genomic midpoint along the chromosome: g_1 … g_N (rank position = index).
- **Neighborhood** of g_i: `k = 4` nearest neighbors by rank = {g_{i-2}, g_{i-1}, g_{i+1}, g_{i+2}}
  (2 upstream + 2 downstream; truncated at chromosome ends).
- For panel genome p, RBH gives a partial ortholog map o_p(gene)→(panel gene, panel rank position).
- `present_p(g_i) = 1` iff g_i has an RBH ortholog in p.
- **Synteny window** `W = 5` (gene-rank positions), tolerant of insertions/short inversions.
- `syntenic_p(g_i) = 1` iff present_p(g_i)=1 AND ∃ neighbor n ∈ neighborhood(g_i) with present_p(n)=1 AND
  `|rank_p(o_p(g_i)) − rank_p(o_p(n))| ≤ W`.  (Same-neighbor co-localization preserved in genome p.)
- Panel size for a focal organism P = 11 (the other genomes).
- **own_conservation(g) = (1/P) Σ_p present_p(g)**   ← the BASELINE (sequence-conservation breadth).
- **context_conservation(g) = (1/P) Σ_p syntenic_p(g)**   ← PRIMARY new feature (synteny breadth).
- **conditional_synteny(g) = context_conservation(g) / own_conservation(g)** if own>0 else 0  ← SECONDARY
  (fraction of the genomes where g is present that also preserve synteny; most decorrelated from own).
Note context_conservation ≤ own_conservation by construction; the decisive question is whether the SYNTENY
part adds predictive value BEYOND own_conservation.

## 8. Pre-registered tests (on the NON-METABOLIC subproteome) — locked
Truth label y = experimentally essential (PEC Class 1 / DeJesus ES).
- **(A) Add-on to the conservation null (decisive).** Stratified 5-fold CV (StratifiedKFold, shuffle=False,
  no RNG — deterministic), standardized features, sklearn LogisticRegression(C=1.0, max_iter=1000, solver=lbfgs).
  - M1 = own_conservation only.  M2 = own_conservation + context_conservation.
  - Out-of-fold pooled AUROC for each. **ΔAUROC = AUROC(M2) − AUROC(M1).**
  - Report the partial (standardized) coefficient of context_conservation in a full-data M2 fit and its sign.
  - Secondary: M2b = own + conditional_synteny; report ΔAUROC(M2b−M1).
- **(B) Enrichment.** Binarize: "syntenic-conserved" = context_conservation ≥ its median over the non-metabolic
  set (pre-registered threshold = median; ties → ≥). 2×2 Fisher exact vs essential; report OR and p.
- **(C) Study-bias control (E. coli only; PEC carries a PMID column).** study_proxy = log(1 + #distinct PMIDs)
  from PEC per gene. M3 = own + study_proxy; M4 = own + study_proxy + context_conservation.
  Report ΔAUROC(M4−M3): if the context add-on SURVIVES conditioning on study intensity, the signal is not a
  study-bias artifact (expected, since context is coordinate-derived). Mtb: no clean PMID proxy → noted, not run.

## 9. PASS / FAIL gate (locked BEFORE outcomes)
**PASS** (E. coli, primary) requires BOTH:
  1. **ΔAUROC (A, M2−M1) ≥ +0.03** (context adds beyond the conservation null), AND
  2. **Enrichment (B) OR > 2 with Fisher p < 0.01.**
Additionally, for the PASS to be called study-bias-robust, (C) ΔAUROC(M4−M3) must remain ≥ +0.02.
**FAIL** = otherwise → this is a FIRST-CLASS NEGATIVE: it closes the "conserved genomic context cracks the
non-metabolic half" door (as MET4 closed the PPI door), demonstrating that neighborhood conservation merely
re-encodes raw conservation and adds no independent mechanistic signal for the non-metabolic essential half.
Mtb is reported as a generality replication (same gate), not required for the primary verdict.

No tuning, no threshold search, no trial-and-error. Single planned hypothesis. The verdict is reported either way.

## 10. Reproducibility
Deterministic: mmseqs `--threads 1`, no seeds, StratifiedKFold(shuffle=False). run.py prints a SHA-256 over the
sorted-key JSON metrics payload EXCLUDING `verdict` and `provenance`; run twice; SHAs must match byte-identical.
Floats in the payload rounded to 6 decimals to avoid platform float noise. Data (genomes, mmseqs caches) live
ONLY in $INTERCEPTA_DATA/nonmet1/. Nothing is git-committed.

## 11. Scope of any claim
In-silico; enrichment-only; NON-METABOLIC subproteome; small 12-genome bacterial panel; two focal organisms.
No clinical, selectivity, or drug-target claim. A PASS would be a candidate mechanistic signal for the
non-metabolic half; a FAIL closes that specific door honestly.
