# DYNAMICS4 — Durability from KNOWN FUNCTIONAL-SITE residues (not fpocket's blind pocket) (PRE-REGISTRATION)

**Frozen BEFORE any ESM scoring of functional-site residues.** Author: DYNAMICS4 module.
Env: ESM-2 (miniforge `intercepta`, torch+transformers, CPU-only, offline HF cache). Zero budget.
Data → `$INTERCEPTA_DATA/dynamics4/`; NEVER committed. NEVER git commit.

## The problem DYNAMICS4 SOLVES (does not bypass)
DYNAMICS3 replaced the drug-BOUND crystal's contact residues with fpocket's **blind top pocket** on
the apo AlphaFold model, so durability became computable for undrugged targets. It PASSED (G1 rho
0.714, G2 AUROC 0.899) but with a **central caveat**: fpocket's blind top pocket is USUALLY NOT the
real drug site — **0.0 crystal-site overlap** for embB/gyrA/parC/rpoB/rpsL/CYP51/mraY/murA/murE
(only HSV1_TK/ddlB/dxr/glmU hit it). So DYNAMICS3's recovered signal is only a **coarse
functional-cavity / partly whole-protein tolerance proxy**, not calibrated drug-contact tolerance.

DYNAMICS4 SOLVES the wrong-pocket problem at its root: **drugs bind functional sites**, and for a
CHARACTERIZED enzyme those sites are ALREADY ANNOTATED in UniProt (Active site + Binding site +
catalytic Site). We define the durability site from those annotations — a PRINCIPLED, accurate site
that needs neither a drug-bound crystal (DYNAMICS1/2) nor a blind pocket guess (DYNAMICS3).

## HYPOTHESIS (frozen)
Durability = mean ESM-2 masked-marginal entropy over UniProt-annotated FUNCTIONAL-SITE residues
(a) AGREES with the DYNAMICS2 crystal drug-contact durability BETTER than fpocket did (beat rho
0.714) and hits the real drug site with HIGHER crystal-site OVERLAP than fpocket's ~0 (the actual
solve); and (b) still SEPARATES HIGH/LOW resistance-liability (AUROC >= 0.75) — giving a principled,
accurate durability site for novel/undrugged but characterized targets.

## FROZEN METHOD
### Target set + accessions
The DYNAMICS2 n=26 set VERBATIM. Per-gene UniProt accession + crystal domain span = the FROZEN
DYNAMICS3 SIFTS-resolved `ACC` map (verbatim; not re-resolved). Crystal drug-contact durability
(`mean_entropy`) and crystal contact residues are READ from
`experiments/DYNAMICS2_durability_scaleup/results/DYNAMICS2_metrics.json`. The fpocket baseline
(predicted-pocket durability + crystal_site_overlap per target) is READ from
`experiments/DYNAMICS3_predicted_pocket_durability/results/DYNAMICS3_metrics.json`.

### Functional-site residue definition (frozen)
For each accession, fetch UniProt REST `.json` (browser-UA; cached under
`$INTERCEPTA_DATA/dynamics4/uniprot/`). Functional-site residues = the union of residue positions
covered by every feature of type **Active site**, **Binding site**, or **Site** (catalytic),
enumerating each feature's `[start,end]` range, **restricted to the crystal domain span** (this
scopes polyprotein accessions — HCV NS3/NS5B, HIV-1 Pol/RT — to the correct mature domain). Fabricate
NOTHING: a target with no annotation is reported infeasible, not invented.

### Sequence source (frozen)
UniProt **canonical sequence** (REST `.json` `sequence.value`), UniProt numbering: annotated position
p → sequence index p-1. This is identical to the AlphaFold canonical sequence DYNAMICS3 used for the
20 AF-modelled targets (so agreement is apples-to-apples), and requires NO AlphaFold/crystal
structure — only a characterized protein's UniProt entry — which is the generalizable use case.

### Functional-site durability (FROZEN metric — identical to DYNAMICS1/2/3)
`functional_site_durability` = MEAN masked-marginal Shannon entropy (`facebook/esm2_t30_150M_UR50D`,
CPU, eval, torch.manual_seed(0), float32, 1022-window centred on median target index if len>1022)
over the functional-site residue indices. `masked_marginal` is copied **VERBATIM** from
DYNAMICS1/2/3; the frozen 1022-window pre-slice + drop-out-of-window logic is copied VERBATIM from
DYNAMICS3. The metric is NOT changed — the ONLY change is the residue set = annotated functional site.
ESM logits cached under `$INTERCEPTA_DATA/dynamics4/esm_logits/`.

## FEASIBILITY (resolved in FEASIBILITY.md BEFORE the gates below are scored)
A target is **annotation-feasible** iff it has **>= 3** annotated functional-site residues within its
crystal domain span (need a SITE, not a single residue, to define a durability region).
**PROCEED to the gates iff >= 15 / 26 targets are feasible.** Infeasibility is reported honestly (no
UniProt functional-site annotation, or < 3 residues) as a real applicability bound of the method.

## PRE-REGISTERED GATES (frozen BEFORE scoring)
Computed over the annotation-feasible set (headline), AND head-to-head vs fpocket on the
**intersection** with DYNAMICS3's feasible set restricted to numbering-aligned bacterial/eukaryotic
targets (crystal auth_seq == UniProt numbering, so crystal-site overlap is comparable).

- **G1 (agreement / beat fpocket):** Spearman rho between `functional_site_durability` and DYNAMICS2
  `crystal_durability` over feasible targets. **Require rho >= 0.50 AND p < 0.05.** Report vs
  DYNAMICS3 fpocket rho **0.714**; the SOLVE ideally gives **rho > 0.714** (annotated site agrees
  BETTER). Also report rho on the intersection set, alongside fpocket rho recomputed on that same set.
- **Crystal-site OVERLAP (the actual wrong-pocket solve):** mean fraction of the DYNAMICS2 crystal
  drug-contact residues (by residue number) recovered by the annotated functional-site residues, over
  the numbering-aligned intersection targets. **Require annotated mean overlap >= 0.25 AND >=
  fpocket mean overlap + 0.10 (absolute) on the same targets** — i.e. the annotated site hits the
  real drug site MATERIALLY more than fpocket's ~0-overlap blind pocket.
- **G2 (discrimination):** AUROC(`functional_site_durability` vs HIGH=1) over feasible targets, higher
  entropy → HIGH. **Require AUROC >= 0.75.** Two-sided Mann-Whitney U p reported.

### VERDICT LADDER
- **SOLVED** = G1 (rho>=0.5, p<0.05) AND crystal-site-overlap gate AND G2 (AUROC>=0.75) — annotated
  functional site beats fpocket's blind pocket → accurate durability for characterized novel/undrugged
  targets. (Strong SOLVED if additionally rho > 0.714.)
- **PARTIAL** = 2 of the 3 gate blocks met.
- **NEGATIVE (first-class)** = <=1 met — e.g. the crystal DRUG site != the annotated CATALYTIC site
  for many targets (allosteric / interface drugs: fluoroquinolone QRDR, rifampicin RNA channel), a
  genuine bound; reported honestly, not tuned around.

## APPLICATION (regardless of verdict): ispE
Compute `functional_site_durability` for ispE (E. coli, P62615; the DURABLETARGETS1 NA core) via the
identical pipeline; compare to DYNAMICS3's fpocket value (1.89, advisory).

## Reproducibility
SHA-256 over sorted-key JSON of `payload` (per-target functional residues + durability + overlap +
G1/G2 + ispE), EXCLUDING provenance/runtime. Entropies rounded to 6 decimals. UniProt JSON + ESM
logits cached under `$INTERCEPTA_DATA/dynamics4/`. Run twice → require BYTE-IDENTICAL. No git commit.

## HONEST SCOPE (binds the result BEFORE it is known — carries DYNAMICS caveats + new ones)
- ESM masked-marginal entropy is a **PLM proxy** for mutational tolerance, NOT measured fitness.
- A single **static** definition; misses induced-fit / allosteric / efflux / bypass resistance.
- **Annotation dependence is the new bound:** the method scores only CHARACTERIZED targets with
  UniProt Active/Binding/catalytic-Site features. Targets whose drug site is a non-catalytic
  interface UniProt does not annotate as a functional site (RNA-polymerase channel rpoB, ribosomal
  S12 rpsL, arabinosyltransferase embB, HIV protease) or that lack annotation are INFEASIBLE — a real
  applicability limit, not a failure to hide.
- **Annotated catalytic/substrate site != drug site for interface drugs:** fluoroquinolones bind the
  gyrase/topo QRDR–DNA interface, not the annotated ATPase/active site; if overlap is low for
  gyrA/parC that is genuine biology, reported openly, not corrected.
- Not tuned to pass. If annotated sites do NOT beat fpocket (rho not higher, overlap still low, or
  AUROC drops), the PARTIAL/NEGATIVE bound is the result.
</content>
</invoke>
