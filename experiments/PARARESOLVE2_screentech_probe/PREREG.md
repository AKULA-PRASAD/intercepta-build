# PARARESOLVE2 — PRE-REGISTRATION (frozen BEFORE scoring)

**Written:** 2026-08-06, before any OR/p was computed against the Bushell truth set.
**One-line question:** Does *Plasmodium* FBA-essentiality ALSO fail against a THIRD screen technology
(Bushell 2017 *P. berghei* PlasmoGEM double-crossover knockout + barseq relative-growth-rate), the same way it
failed against Zhang 2018 piggyBac — i.e. is the malaria FBA failure SCREEN-TECHNOLOGY-ROBUST, or is it a
piggyBac-specific artifact?

## HARD SCOPE (stated up front, non-negotiable)
- This is a **screen-technology ROBUSTNESS probe**, introducing a THIRD technology (targeted double-crossover
  gene knockout + barseq relative growth rate, Bushell 2017) distinct from piggyBac (Zhang 2018) and from
  CRISPR (Sidik 2016, used for Toxoplasma).
- **This does NOT close the CRISPR-specific axis.** No genome-wide saturating *P. falciparum* CRISPR
  essentiality screen exists (Pf CRISPR is gene-by-gene). The clean same-species-CRISPR closure is DATA-GATED
  and is NOT attempted or claimed here.
- Bushell screened *P. berghei*, not *P. falciparum*. Mapping Bushell genes onto the Pf GEMs introduces a
  **cross-species (P. berghei -> P. falciparum) confound**. This is a rodent-malaria blood-stage screen.
- Bushell is a **partial-genome** screen (2578 genes of the ~5000-gene genome), not genome-saturating like
  Zhang's piggyBac. Coverage of the GEM metabolic genes is therefore lower than Zhang's (documented below).
- Verdict must NOT use the word "closure." It is robustness evidence only.

## Data source (obtained; frozen)
- **Bushell et al. 2017, Cell 170(2):260–272.e8**, "Functional Profiling of a Plasmodium Genome Reveals an
  Abundance of Essential Genes." PMID 28708996, PMCID **PMC5509546** (Europe PMC, **isOpenAccess = Y**).
- Supplementary bundle fetched via the Europe PMC REST supplementaryFiles endpoint:
  `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5509546/supplementaryFiles`
  Saved: `$INTERCEPTA_DATA/pararesolve2/bushell2017_europepmc_supplementaryFiles.zip`
  sha256 `c51a765629f51d9d4086a30d232cf0ec8cc17178d92673bd573641b3d163b63d`.
- Essentiality table = **Table S1 = mmc1.xlsx** (sheet "Table S1", 2578 gene rows),
  sha256 `b1d990663d8d8bf18ab48132c08afee178bbc07e4e7b902545a72c1dbd6e3a74`.
  Extracted to CSV `$INTERCEPTA_DATA/pararesolve2/bushell2017_tableS1.csv`
  sha256 `cc0cfd26e3703b1716296c16de8084fb7d6d9022b72145e46feb8139c3b916b4`
  (columns: Pb_current_ID, Pb_previous_ID, **Pf_ID**, Name, Product, **Phenotype**, **RGR**, Confidence).

## Essentiality classification — AUTHORS' OWN, NOT invented
Table S1 column **"Phenotype"** is Bushell's own classification derived from the barseq relative growth rate
(RGR): each gene is called **Essential / Slow / Dispensable / Fast / Insufficient data**. The RGR distribution
(observed pre-scoring, over the whole table) cleanly separates them: Essential n=1196 RGR 0.003–0.482
(median 0.100); Slow n=456 RGR 0.154–0.974 (median 0.595); Dispensable n=911 RGR 0.596–1.160 (median 0.978);
Insufficient data n=13; Fast n=2. **I do NOT invent an RGR cutoff — I use the authors' label directly.**
- **PRIMARY essential call (frozen):** Phenotype == **"Essential"**.
- **PRE-REGISTERED SENSITIVITY:** Phenotype in {"Essential","Slow"} (all reduced-growth = the "slow/no growth"
  reading). Reported alongside; the gate verdict is taken on the PRIMARY definition.
- Rows with Phenotype == "Insufficient data" are EXCLUDED from the contingency (undetermined truth).

## GEM + mapping (option (b), documented choice)
No openly obtainable CPU-only genome-scale *P. berghei* GEM was identified; and Bushell Table S1 provides an
**authoritative PlasmoDB-curated `P. falciparum ID` ortholog column**, which is a cleaner and more defensible
Pb->Pf ortholog map than an ad-hoc mmseqs RBH. Therefore: **option (b)** — score the two *P. falciparum* GEMs
already validated in PARARESOLVE1 against the Bushell essential set via this Pf-ortholog column.
- GEMs: **iPfal19** (PARADIGM, reference/anchor; `$INTERCEPTA_DATA/generalize5/iPfal19.xml`) and
  **iAM-Pf480** (Abdel-Haleem 2018, INDEPENDENT team, UCSD; `$INTERCEPTA_DATA/pararesolve1/pfal2018_abdel_haleem.xml`).
  Both use PF3D7_ gene IDs, matching Bushell's Pf_ID column directly.
- Mapping rule (frozen): GEM gene id `PF3D7_xxxxxxx` (strip any `.N`/`-pN` suffix, uppercase) is looked up in
  Bushell Table S1 `Pf_ID`; the gene enters the contingency iff it maps to a Bushell row with a **definitive**
  phenotype (not "Insufficient data"). Coverage observed pre-scoring (definitive-mapped / model genes):
  iPfal19 268/475 = 0.564; iAM-Pf480 297/480 = 0.619. Reported honestly as partial-genome coverage.

## FBA method (IDENTICAL to GENERALIZE5 / PARARESOLVE1 / HARDENP1)
COBRApy `single_gene_deletion` on the default medium; WT growth = `slim_optimize`; a gene is **FBA-essential**
iff KO growth < 1% of WT. **KO growth rounded to 6 dp** before thresholding. cobra 0.31.1, GLPK, processes=1,
deterministic.

## Estimator (FROZEN, byte-comparable to the anchors)
2×2 contingency (a=both, b=FBA-only, c=exp-only, d=neither) over definitive-mapped genes. **Sample odds ratio
(a·d)/(b·c)** and **one-sided (greater) hypergeometric Fisher p via `math.comb`** — scipy deliberately unused,
exactly as GENERALIZE5/PARARESOLVE1/HARDENP1.

## GATE (frozen) and PRE-REGISTERED INTERPRETATION (all outcomes allowed)
Gate = **OR > 3 AND p < 0.01** (identical bacterial-rigor bar; taken on the PRIMARY essential definition).
Anchors: Zhang/iPfal19 **OR 2.47 (FAIL)**; Toxo iTgo2020/Sidik **OR 14.10 (PASS)**.
- **If Plasmodium FBA ALSO FAILS vs Bushell (barseq-KO)** like it did vs Zhang (piggyBac) → the failure is
  **SCREEN-TECHNOLOGY-ROBUST** (not a piggyBac artifact) → the screen-technology axis is largely **EXONERATED**
  as the cause of the Pf-vs-Toxo gap → points back to GEM topology + base-rate/biology (consistent with
  PARARESOLVE1). Residual: cross-species + no-CRISPR caveats remain.
- **If Plasmodium FBA PASSES vs Bushell** → screen/dataset specifics matter a lot → the confound is real and
  the piggyBac-specificity of Zhang is **IMPLICATED**.
- If BOTH GEMs disagree (one pass, one fail): report the split; the primary-anchor GEM (iPfal19) governs the
  head-to-head with its own Zhang 2.47.

## Reproducibility
Payload = sorted-key JSON EXCLUDING `verdict` and `provenance`. Run twice; print sha256; assert byte-identical.
KO growth rounded 6 dp. NOT git-committed; data NOT committed.

## Residual confounds that will REMAIN unresolved (declared now)
1. CRISPR-specific axis: NOT closed (no genome-wide Pf CRISPR screen exists).
2. Species: Bushell is *P. berghei*; scored on *P. falciparum* GEMs via ortholog — a cross-species mapping.
3. Partial-genome screen + ~56–62% GEM coverage (vs Zhang's ~89%): lower power, possible mapping selection.
4. Base-rate/biology residual (PARARESOLVE1): not eliminated by a screen-tech swap.
