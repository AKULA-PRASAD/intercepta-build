# HOSTCTX2 — pre-registered test: does HOST-EXCHANGE / MEDIUM CURATION rescue the malaria FBA-essentiality signal?

**Registered (Stage 1) BEFORE computing ANY curated contingency table / odds ratio / Fisher p / precision / recall /
AUROC.** The three host-available nutrient sets below are FROZEN by this document. Only feasibility (does WT biomass
carry flux at all) was checked during design — an outcome-blind, Zhang-independent criterion — and is disclosed in
full. The ENRICHMENT ANSWER for the curated media has NOT been looked at when this file is written.

## Context / prior (why this experiment)
- **GENERALIZE5**: plain default-medium FBA essentiality on iPfal19 vs Zhang 2018 piggyBac screen FAILED the OR>3 &
  p<0.01 gate: **OR 2.469, p 0.00217, precision 0.797, recall 0.201, contingency both 55 / FBA-only 14 / exp-only 218 /
  neither 137**, n=424 mapped. Recall collapses to 0.20 — the model calls almost nothing essential.
- **HOSTCTX1** (E-Flux, expression-context): NEGATIVE, essential set byte-identical to baseline (OR unchanged 2.469).
  Mechanism: single-gene essentiality is GPR **bypass topology**, not flux magnitude; host-salvage "workaround"
  reactions stay topologically usable however you down-weight them by expression.
- Mechanistically-indicated next lever (this experiment): change network **content/boundary** — restrict the model's
  import/exchange reactions to what the host RBC actually provides, forcing reliance on the parasite's own biosynthesis.

## Hypothesis
Restricting iPfal19's import (uptake) reactions from the default all-open medium (all 195 exchanges open at uptake
1000) to a host-RBC-available nutrient set — defined from INDEPENDENT published sources, frozen below — increases the
enrichment of FBA single-gene-deletion essentiality for the parasite's experimentally essential genes (Zhang 2018),
because closing spurious salvage imports removes the topological bypasses that made true essentials look dispensable.

## Controlled A/B design (ONLY the exchange bounds change)
Everything else is copied from GENERALIZE5 read-only assets and code: same GEM (`iPfal19.xml`), same truth
(`zhang2018_essentiality.csv`, essential = phenotype `"Non - Mutable in CDS"`), same alias map, same PF3D7 gene-ID
mapping, same 2x2 one-sided Fisher gate, same essential-if-KO-growth < 1% WT rule, same 6-dp GLPK-jitter rounding.
The ONLY manipulated variable is the set of exchange reactions permitted to carry uptake flux (lower_bound = -1000 if
the metabolite is host-available, else lower_bound = 0 which blocks import but LEAVES SECRETION/export open).

## BASELINE ANCHOR (validity precondition)
Baseline = default open medium, bounds untouched. MUST reproduce GENERALIZE5: OR ~2.469, contingency 55/14/218/137,
n_fba_essential(mapped) = 69, precision 0.797, recall 0.201. **If baseline is not reproduced, STOP — the A/B is invalid.**

## Host-RBC-available nutrient set — FROZEN, per-class independent source (ANTI-CIRCULARITY)
**ANTI-CIRCULARITY RULE (binding): no metabolite may be added to or removed from any host-available set on the basis of
its effect on the odds ratio or on agreement with Zhang. Membership is fixed by the published citations below. The only
design-time computation performed was WT-growth feasibility (an outcome-blind criterion); every feasibility-driven
inclusion was a biomass-REQUIRED cofactor the model needs to grow at all, disclosed here, never a Zhang-tuned choice.**

Primary published anchor: blood-stage *P. falciparum* is cultured continuously in **RPMI 1640** + human serum +
hypoxanthine (**Trager & Jensen 1976 Science 193:673**; RPMI 1640 formulation **Moore et al. 1967 JAMA 199:519**). RPMI
1640 fixes the amino-acid, vitamin, salt and glucose ingredient list — an external standard set decades before any
essentiality screen, so it cannot be circular w.r.t. Zhang. Supplemented per established blood-stage salvage biology:

| Class | Metabolites (model EX IDs) | Independent source / justification |
|---|---|---|
| Carbon | glc__D | RPMI 1640 glucose (Moore 1967); primary blood-stage carbon source |
| Amino acids (serum/RPMI) | arg,asn,asp,cysi(cystine),glu,gln,gly,his,ile,leu,lys,met,phe,pro,ser,thr,trp,tyr,val (all __L) | RPMI 1640 amino-acid formulation (Moore 1967). RPMI lacks Ala (parasite transaminates) and free Cys (supplies cystine). |
| Isoleucine (special) | ile__L | Only amino acid ABSENT from human hemoglobin → must be salvaged from serum (**Liu et al. 2006 PNAS 103:8840**). Required import even in STRICT. |
| Vitamins/cofactor precursors | pnto_R & pnto__R (pantothenate), fol (folate), ncam (nicotinamide), 4abz (PABA), pydxn (pyridoxine), ribflv (riboflavin), thm (thiamine), inost (myo-inositol), chol (choline) | RPMI 1640 vitamin formulation (Moore 1967). Pantothenate is an established blood-stage essential/auxotrophy (**Saliba et al. 1998 JBC 273:10190**; **Divo et al. 1985 J Protozool 32:59**). |
| Purine (supplement) | hxan (hypoxanthine) | Blood-stage purine auxotroph; hypoxanthine is the standard essential purine supplement (**Divo et al. 1985**; salvage via HGPRT, **Cassera et al. 2011**). |
| Host hemoglobin | hb (import) + hemozoin (export, secretion left open) | Blood-stage parasite ingests & digests host hemoglobin as major amino-acid + heme source (**Goldberg 2005**; **Francis et al. 1997 Annu Rev Microbiol 51:97**). |
| Host lipid (bulk) | lipid_c (EX_lipid_c, the lumped `bm_lipid_c` pool) | Cholesterol auxotroph; scavenges bulk host lipid (fatty acids, cholesterol, phospholipids) from serum/RBC (**Mi-Ichi et al. 2006 Mol Biochem Parasitol 150:22**; **Labaied et al. 2011 Cell Microbiol 13:569**). See MODEL-BOUNDARY note below. |
| Iron | fe2 | RBC hemoglobin + serum transferrin iron; physiologically abundant in blood. |
| Ions | pi (phosphate), so4 (sulfate, from MgSO4), hco3 (bicarbonate), no3 (from Ca(NO3)2 in RPMI) | RPMI 1640 inorganic salts (Moore 1967). |
| Glutathione | gthrd | RPMI 1640 reduced glutathione (Moore 1967). |
| Gases / water / proton | o2, co2, h2o, h | Physiological; required for any FBA solution. |

### MODEL-BOUNDARY note (reportable GEM artifact, fixed a priori)
Design-time feasibility testing established that iPfal19 **cannot synthesize its biomass membrane-lipid pool de novo**:
biomass consumes lumped `bm_lipid_c`, produced either by the assembly reaction `lipid_bm` (needs pools all_pc/pe/pg/pi/
dgl/apg/tag/chsterol/sphmyln) OR by the dedicated pseudo-exchange `EX_lipid_c`. With `EX_lipid_c` closed, the model
cannot produce ANY of all_pc/pe/pg/pi/dgl/apg/tag even when cholesterol + fatty acids + head groups (choline,
ethanolamine, glycerol, inositol) imports are all open (max producible flux = 0 for each). Hence `EX_lipid_c` is a
gap-filling lump with no de-novo route, and ANY medium that closes it makes WT biomass infeasible (growth 0). Because
the host demonstrably supplies bulk lipid to the blood-stage parasite (Mi-Ichi 2006; Labaied 2011), I keep `EX_lipid_c`
OPEN in all curated media as the host-scavenged lipid pool. **Documented CEILING: this forecloses recovery of
lipid-biosynthesis essential genes; the curation can only sharpen the NON-lipid subnetwork.** This is failure-mode (a)
from the task (curated medium infeasible = GEM gap-fill artifact), handled honestly rather than gap-filled away.

## The THREE frozen host-available variants (sensitivity defined a priori)
Graded by biological permissiveness; all confirmed WT-feasible at design time (growth shown, Zhang NOT consulted):
1. **PRIMARY — "RPMI+Hx+Hb" (physiological blood-stage):** the full table above (43 exchanges). WT growth = 15.57.
2. **STRICT — "minimal salvage":** documented auxotrophies + biomass-required cofactors + Hb + lipid lump ONLY;
   DROPS the serum free amino acids (parasite must derive them from hemoglobin digestion), keeps only Ile (Hb lacks it).
   Set: glc__D, hxan, pnto_R, pnto__R, ile__L, hb, fe2, so4, o2, ribflv, pi, hco3, h2o, h, co2, fol, ncam, pydxn, thm,
   inost, chol, EX_lipid_c (22 exchanges). WT growth = 15.56. Feasibility-driven cofactor inclusions
   (fol/ncam/pydxn/thm/ribflv/inost/chol) are biomass-required, disclosed, OR-blind.
3. **PERMISSIVE — "RPMI+Hx+Hb + full RBC purine pool":** PRIMARY + the purine nucleosides/bases abundant in the
   erythrocyte (adn, ins, ade, gua, xan, gsn, dad_2, dgsn, din) + glycerol + ethanolamine (54 exchanges). WT growth =
   31.29. Tests whether broadening the physiologically-real purine supply collapses the purine-salvage signal.

## Pre-registered decision gate (fixed now) WITH MANDATORY PRECISION-COLLAPSE GUARD
Report side-by-side for baseline vs each curated medium: OR, Fisher one-sided p, precision, recall, AUROC, full
contingency (both/FBA_only/exp_only/neither), n_fba_essential (total and among mapped), n mapped.
- **RESCUE (PASS)** iff a curated medium clears **OR > 3 AND p < 0.01 AND OR improves over baseline (2.469) AND precision
  does NOT collapse** — precision stays >= 0.5 AND the essential-set size does not balloon such that the OR gain is
  merely from calling far more genes essential. If OR rises only because n_essential ballooned while precision dropped,
  that is an ARTIFACT → report as **NEGATIVE-with-artifact**, NOT a rescue.
- **PARTIAL** = materially improves (higher OR than 2.469, p<0.01, no precision collapse) but OR still < 3.
- **NEGATIVE** = no improvement / worse / rescue-only-via-artifact.
Verdict must be ROBUST across the three variants to be called a rescue; report per-variant and note any disagreement.

## Scope / honest limits (fixed now)
Essentiality-enrichment only; in-silico FBA vs a published screen (not wet-lab); one curated model, one parasite (n=1),
blood stage; the lipid-lump ceiling above; RPMI is an in-vitro proxy for the in-vivo blood environment. Deterministic;
reproduced x2 byte-identical (SHA-256 over sorted-key metrics payload EXCLUDING verdict/provenance). KO growth rounded
6 dp before thresholding. NEVER git commit/push; NEVER commit data.
