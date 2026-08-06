# HARDENF1 — does FBA gene-essentiality hold on a REAL FUNGAL PATHOGEN (*Candida albicans*)?

**Pre-registered (Stage 1) BEFORE computing the 2x2 Fisher / any gate score.** Method, data, ID-mapping
strategy and the decision rule are fixed here first. Metrics are produced by `run.py` in a later step and
reported (PASS/FAIL) exactly as written below. Negatives are first-class and will not be hidden or re-run to a
nicer number.

## Motivation (what this hardens)
`experiments/GENERALIZE4_fungal_fba` showed FBA single-gene-deletion essentiality transfers from bacteria to a
**eukaryote** — but on ONE organism, the *model* yeast *Saccharomyces cerevisiae*, which is **not a pathogen**.
That is n=1 for eukaryotes and not a real fungal pathogen. HARDENF1 tests whether the same in-silico
essentiality signal holds on **another eukaryote — a REAL FUNGAL PATHOGEN**, taking the eukaryote→FBA entry
from n=1 (model yeast) toward n>1 with a clinically relevant organism.

## Organism & rationale (deliberate, disclosed)
**PRIMARY = *Candida albicans* SC5314** — the leading cause of invasive candidiasis; a genuine human fungal
pathogen (the true goal named in the GENERALIZE4 pre-reg). A curated genome-scale metabolic model AND a large
curated experimental essentiality resource are both openly available CPU-only (below), so this is doable with
the same rigor as the bacterial panel and GENERALIZE4.

**SECONDARY = *Schizosaccharomyces pombe* — ATTEMPTED, reported as an HONEST BOUNDARY (not run).** A clean
eukaryotic essentiality label exists (DEG accession DEG2009, 1260 essential genes, already local), but no
openly-downloadable curated *S. pombe* GEM usable for gene-deletion FBA CPU-only was found: the curated
SpoMBEL1693 (BioModels MODEL1507180061) carries **no machine-readable gene–protein–reaction associations**
(cobra parses 0 genes); Pitkanen-2014 CoReCo (MODEL1302010035) also parses 0 genes and has no objective; the
Lu-2021 pan-fungi model (MODEL2109240001) has 874 genes but opaque internal IDs
(`Schizosaccharomyces_pombe@Seq_N`) with no clean bridge to the DEG2009 symbol/GI namespace — mapping it would
be a guess and namespace mismatch is our declared #1 failure mode. Rather than fabricate a mapping, we report
this as the honest boundary and deliver the real-pathogen result (*C. albicans*), which is the higher-value test.

## Data (open, CPU-only, downloaded; provenance in results/)
- **GEM:** Mirhakkak & Schäuble 2021 curated *C. albicans* genome-scale metabolic model. BioModels
  **MODEL2110210002**, file `Suppl_Data_S1.xml` (SBML L3V1); 771 genes, 3316 reactions, 2733 metabolites;
  curated with phenotypic-microarray data and de-cycled of erroneous energy-generating loops.
  Publication: Mirhakkak et al. 2021, *ISME J*, doi:10.1038/s41396-020-00848-z.
  URL: `https://www.ebi.ac.uk/biomodels/model/download/MODEL2110210002?filename=Suppl_Data_S1.xml`
  sha256 `b92fe385e452c09b29f6205e66f1009c22aa6b4c7252425de7ceb3a55d8df972`.
  Local: `$INTERCEPTA_DATA/hardenf1/calb_gem_Mirhakkak2021.xml`.
  Gene IDs = CGD Assembly-22 systematic names in SBML-safe form, e.g. `CAALFM_C100070WA` (a few `CM_*`
  mitochondrial-genome genes).
- **Experimental essentiality:** Candida Genome Database (CGD) curated phenotype annotations,
  `C_albicans_SC5314_phenotype_data.tab` (27,841 annotations; includes the GRACE conditional-knockout
  essentiality of Roemer et al. 2003 plus subsequent deletion studies). URL:
  `http://www.candidagenome.org/download/phenotype/C_albicans_SC5314_phenotype_data.tab`
  sha256 `7a05dd6615aa093599013b50aea12fcc72da0fbba76ee66e3b1dfee250e22587`.
  Local: `$INTERCEPTA_DATA/hardenf1/CGD_C_albicans_SC5314_phenotype_data.tab`.
  Columns used: `Feature Name` (A22 systematic ID, e.g. `C1_00070W_A`), `Phenotype`, `Mutant Type`.
- **ID-universe check (coverage denominator):** CGD `ORF19_Assembly22_mapping.tab`
  (`http://www.candidagenome.org/download/chromosomal_feature_files/C_albicans_SC5314/ORF19_Assembly22_mapping.tab`,
  sha256 `d209144131ad781e19c9643969b45d99390e7be01aa6465ecc6922bb77792936`), used only to validate that the GEM
  gene IDs resolve to real A22 systematic IDs — not used to define the essential set.

## Experimental essential-gene definition (FROZEN before scoring)
A *C. albicans* gene (A22 systematic ID) is **EXPERIMENTALLY ESSENTIAL** iff the CGD phenotype file records
**≥1 annotation with `Phenotype == "inviable"` AND `Mutant Type` ∈ {null, repressible, conditional}** — i.e.
loss-of-function (complete null OR tet-repressible/conditional knockdown, the GRACE assay) renders the strain
inviable. This is the standard CGD/OGEE essentiality call. All other GEM genes are treated as non-essential
(same absence-of-evidence convention as GENERALIZE4 and the bacterial pipeline; disclosed as a caveat).

## ID-mapping strategy (the #1 declared failure mode: namespace mismatch)
The GEM gene IDs are the CGD A22 systematic IDs in SBML-safe form; the phenotype-file `Feature Name` uses the
canonical A22 form `C{chr}_{coord}{W|C}_{A|B}`. Deterministic normalization of each GEM gene ID to the
canonical form:
`CAALFM_C{chr}{coord}{W|C}{hap}` → `C{chr}_{coord}{W|C}_{hap}` (regex `^CAALFM_C([1-7R])(\d{5})([WC])([AB])$`);
IDs already in canonical form (or `CM_*` mitochondrial) are left as-is. A GEM gene is experimentally-essential
iff its normalized A22 ID is in the essential set. **Coverage is reported** (GEM genes resolving to the CGD A22
universe). Pre-run reconnaissance (no outcome metric computed): 768/771 GEM genes resolve; the 3 misses are
mtDNA-encoded `CM_*` genes absent from the nuclear feature map — clean, no namespace artifact.

## Method (mirrors CROSSVAL_curated / GENERALIZE4 exactly)
COBRApy `single_gene_deletion` on the curated model in its default medium; WT growth = `slim_optimize()`; a gene
is **FBA-essential** iff KO growth `< 0.01 * WT`. KO growth rounded to 6 dp to absorb GLPK alternate-optima
jitter → byte-identical reproduction. Universe = the model's 771 metabolic genes. 2x2 Fisher (one-sided
'greater', env-independent `math.comb` hypergeometric so the odds-ratio definition a·d/(b·c) matches
GENERALIZE4 regardless of scipy presence). Also report precision, recall, full contingency, growth-ratio AUROC
(tie-aware Mann–Whitney, sklearn-independent). `processes=1`, deterministic; reproduced ×2 (SHA-256 over
sorted-key JSON of the metrics payload, excluding verdict/provenance).

## Pre-registered hypothesis & decision gate (FIXED before scoring)
**H1:** the FBA-essential set is enriched for the CGD experimental essential set among the *C. albicans* GEM's
metabolic genes.
**GATE: odds ratio > 3 AND Fisher one-sided p < 0.01.** (Identical to every bacterial organism and to
GENERALIZE4.)
- **PASS** ⇒ FBA-essentiality enrichment holds on a **real fungal pathogen**, hardening the eukaryote→FBA
  entry to n>1 with a clinically relevant organism (essentiality-enrichment, in-silico vs curated lab data).
- **FAIL** ⇒ reported first-class as an honest negative (signal does not transfer to *C. albicans* metabolism,
  or GEM/medium/label assumptions break the enrichment). Recorded, not hidden, not re-tuned.

## Scope (true regardless of outcome)
Essentiality-ENRICHMENT only; in-silico FBA vs a curated published essentiality resource (NOT a wet-lab
experiment we ran); a curated model is still a model (medium/gap-fill assumptions); recall is bounded by the
metabolic subproteome; non-annotated genes treated as non-essential (absence of evidence); single real
pathogen. This is a legitimate real-fungal-pathogen generalization test, disclosed as such.
