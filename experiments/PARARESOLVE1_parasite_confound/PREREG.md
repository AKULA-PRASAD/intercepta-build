# PARARESOLVE1 — PRE-REGISTRATION (frozen BEFORE scoring)

**Frozen:** 2026-08-06 (before any OR/p was computed on the independent GEMs).
**Constitution:** truth over vision; falsify-first; negatives are first-class; reproduce ×2 byte-identical
(SHA-256 over sorted-key JSON payload excluding verdict/provenance); zero-budget / CPU-only / open data;
NEVER fabricate; if a GEM will not load CPU-only, report the boundary honestly.

## The confound being attacked
FBA single-gene-essentiality FAILS on *P. falciparum* (iPfal19 vs Zhang 2018, OR 2.47 < 3) but PASSES on
*T. gondii* (iTgo2020 vs Sidik 2016, OR 14.10). The n=2 parasite disagreement is CONFOUNDED across four axes:
(i) GEM curation quality / network topology, (ii) screen technology (Zhang piggyBac vs Sidik CRISPR),
(iii) organism biology, (iv) essential base rate (0.64 vs 0.42). The corrected claim from HARDENP1 —
"the malaria FBA failure is **GEM-topology-specific**, not host-embeddedness" — has never had the **GEM axis
isolated**. This experiment isolates it with a CONTROLLED SWAP: hold organism (*P. falciparum*), screen
(Zhang 2018 piggyBac), gate, and ID-map FIXED; vary ONLY the genome-scale reconstruction.

## Data / models (open; SHA recorded in results)
- **Experimental truth (FIXED):** Zhang et al. 2018 *Science* piggyBac saturation mutagenesis; essential =
  phenotype `"Non - Mutable in CDS"`. Same file as GENERALIZE5 ($INTERCEPTA_DATA/generalize5/zhang2018_essentiality.csv).
- **Reference GEM (anchor):** iPfal19 (Carey/Untaroiu/Papin, PARADIGM, U. Virginia; 475 genes). Must reproduce
  GENERALIZE5 (OR 2.469, contingency 55/14/218/137, n=424) inside this script → validates the pipeline.
- **INDEPENDENT GEMs (PRIMARY — different reconstruction team from iPfal19), fetched openly from PARADIGM's
  `models/published/` redistribution of other teams' published models:**
  1. **Chiappino-Pepe et al. 2017** *PLoS Comput Biol* 13(4):e1005397 (Hatzimanikatis lab, EPFL/LCSB;
     thermodynamics-based reconstruction). File `ipfa2017_chiappino_pepe.xml`, 325 genes.
  2. **Abdel-Haleem et al. 2018 iAM-Pf480** *Cell Reports* 24(9):2337 (Palsson lab, UCSD; Plasmodium-genus
     comparative reconstruction). File `pfal2018_abdel_haleem.xml`, 480 genes.
- **SAME-LINEAGE sensitivity (NOT independent — PARADIGM lineage, labeled as such):**
  - `iPfal17` (PARADIGM's own precursor to iPfal19; SBML model id is literally `plata_orig_xml`),
  - `gf_Pfalciparum3D7.xml`, `gf_no_ortho_Pfalciparum3D7.xml` (PARADIGM gap-filled variants).

### Independence evidence (stated honestly)
The two PRIMARY GEMs are independent **reconstructions by different teams** (different first/last authors,
institutions, and curation methodology, and different gene counts 325/480 vs iPfal19's 475). They are NOT
independent at the *knowledgebase* level — all Pf GEMs draw on shared upstream biochemistry (KEGG/MPMP/
PlasmoDB) and earlier reconstructions (Plata 2010, Huthmacher 2010). "Independent" here means independent
reconstruction/team, not independent underlying biochemical knowledge. This limit is reported.

## Method (IDENTICAL to GENERALIZE5 / HARDENP1 — frozen)
- COBRApy `single_gene_deletion`, one process; KO growth rounded 6 dp (GLPK jitter); FBA-essential if
  KO growth < 1% WT growth. Model used as-loaded (default/open exchange bounds — same as GENERALIZE5).
- 2×2 contingency (both / FBA-only / exp-only / neither) over genes MAPPED to Zhang.
- Estimator FROZEN to GENERALIZE5/HARDENP1: **sample odds ratio (a·d)/(b·c)** + **one-sided hypergeometric
  p via `math.comb`** (scipy present but deliberately unused, for byte-comparability with OR 2.469).
- ID map: model gene id → strip `.N-pN` suffix → match PF3D7_ id in Zhang directly, else via
  `Pfalciparum3D7_GeneAliases.csv` (same alias approach as GENERALIZE5).
- AUROC: rank-based (Mann-Whitney), score = −KO growth vs Zhang label.

## PRE-REGISTERED GATE (frozen, identical bar for every GEM)
**PASS iff OR > 3 AND one-sided p < 0.01** on the PRIMARY definition (phenotype "Non - Mutable in CDS").

## Mechanistic salvage-bypass test (frozen definition)
Directly tests the "salvage topology" hypothesis. For a model, over its FBA **false negatives** (FN =
exp-essential in the screen AND FBA-dispensable, among mapped genes):
1. `B(g)` = reactions r in `g.reactions` with `r.gpr.eval({g.id}) == False` (reactions disabled by removing
   ONLY gene g).
2. If `B(g)` is empty → category **GPR_redundant** (isozyme/OR-rule bypass; NOT salvage).
3. Else `Mets(g)` = all metabolites of reactions in `B(g)`. A metabolite is **salvageable** if its base
   species id (id minus compartment suffix) matches a metabolite carried by a **boundary/exchange reaction
   with import allowed (lower_bound < 0)** under the model's default medium — i.e. the blocked reaction's
   product/substrate can be scavenged from the medium.
   - `B(g)` non-empty AND ≥1 salvageable metabolite → category **salvage_import**.
   - `B(g)` non-empty AND no salvageable metabolite → category **internal_reroute**.
4. `salvage_explained_FN_fraction` = n(salvage_import) / n(FN with non-empty B(g)); also report the fraction
   over ALL FN and the full category breakdown.
Computed for **iPfal19 (FAIL) vs iTgo2020 (PASS)** with their own screens (Zhang / Sidik).

## PRE-REGISTERED INTERPRETATION (all outcomes allowed, frozen)
- **If ≥1 INDEPENDENT Pf GEM PASSES (OR>3) on the same Zhang screen** → the failure was iPfal19-GEM-specific,
  NOT *Plasmodium* biology → confound resolves TOWARD the GEM axis.
- **If independent Pf GEM(s) ALSO FAIL** → the failure is robust to GEM choice → the "just a bad GEM"
  attribution is WEAKENED; biology / screen-technology / base-rate become more likely. Report honestly; do
  NOT cling to the GEM story.
- **Salvage test:** if iPfal19's FNs are dominated by salvageable products and Toxo's are not → mechanistic
  support for GEM-salvage-topology as the discriminator. If not → report that too.
- Report which axis the COMBINED evidence (swap + salvage) supports, and state the RESIDUAL confounds that
  remain UNRESOLVED — in particular **screen technology (piggyBac vs CRISPR)**: note whether any *Plasmodium*
  genome-wide CRISPR/KO essentiality screen exists to control it; if none is obtainable CPU-only, state that
  the CRISPR-vs-piggyBac axis is NOT controllable here and remains a standing limitation.

## Reproducibility
Payload SHA-256 over sorted-key JSON (excluding verdict/provenance). Run twice; print+match. No git commit/push.
