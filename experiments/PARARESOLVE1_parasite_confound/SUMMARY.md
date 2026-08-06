# PARARESOLVE1 — Isolating the GEM axis of the parasite FBA-essentiality confound — SUMMARY

**VERDICT: The GEM axis is a MAJOR driver, and the "iPfal19 is uniquely broken" story is only PARTLY true —
but GEM choice does NOT close the Plasmodium<->Toxoplasma gap, and the specific salvage-topology mechanism is
NOT supported.** A nuanced, honest split — reported without spin. Reproduced x2 byte-identical.
**payload sha256:** `2bbbf68cac59c4296a63fe4471381f113952d152ce327c93b52fc6c82253183e`
**Evidence tier:** COMPUTED (in-silico enrichment vs published screens; not wet-lab).

## What was controlled (the isolation)
Same organism (*P. falciparum*), same screen (Zhang 2018 piggyBac), same gate (OR>3 & p<0.01), same ID-map,
same estimator (sample OR + math.comb hypergeometric) — **only the genome-scale reconstruction varied.**
Pipeline validated: the reference **iPfal19 reproduces GENERALIZE5 EXACTLY** — OR 2.469, p 2.17e-3,
precision 0.797, recall 0.201, contingency 55/14/218/137, n=424 mapped.

## The controlled swap (Zhang 2018, gate OR>3 & p<0.01)
| GEM | team / kind | genes | map | OR | p | prec | rec | base rate | gate |
|---|---|---|---|---|---|---|---|---|---|
| iPfal19 | PARADIGM / **reference** | 475 | 424 | 2.469 | 2.2e-3 | 0.797 | 0.201 | 0.644 | FAIL |
| **Chiappino-Pepe 2017** | EPFL / **INDEPENDENT** | 325 | 324 | **1.034** | 0.53 | 0.673 | 0.171 | 0.651 | **FAIL** |
| **Abdel-Haleem 2018 iAM-Pf480** | UCSD / **INDEPENDENT** | 480 | 473 | **3.074** | 2.4e-4 | 0.821 | 0.185 | 0.630 | **PASS** |
| iPfal17 precursor | PARADIGM / same-lineage | 479 | 377 | 2.461 | 1.2e-3 | 0.790 | 0.263 | 0.645 | FAIL |
| gf_Pfalciparum3D7 | PARADIGM / same-lineage | 465 | 460 | 1.030 | 0.55 | 0.684 | 0.083 | 0.646 | FAIL |
| gf_no_ortho_Pfalciparum3D7 | PARADIGM / same-lineage | 410 | 405 | 0.859 | 0.73 | 0.667 | 0.092 | 0.689 | FAIL |

Anchors for scale: iPfal19 **2.469 (FAIL)**, *T. gondii* iTgo2020 **14.10 (PASS)**.

### Independence evidence (honest)
The two PRIMARY GEMs are independent **reconstructions/teams** (Chiappino-Pepe: Hatzimanikatis lab, EPFL,
thermodynamics-based, 325 genes; Abdel-Haleem iAM-Pf480: Palsson lab, UCSD, genus-comparative, 480 genes) vs
iPfal19 (Carey/Untaroiu/Papin, PARADIGM, U. Virginia, 475 genes). Fetched openly from PARADIGM's
`models/published/` redistribution (SHAs recorded). They are NOT independent at the *knowledgebase* level —
all Pf GEMs share KEGG/MPMP/PlasmoDB and earlier reconstructions (iPfal17's SBML id is literally
`plata_orig_xml`, i.e. PARADIGM's lineage was seeded from Plata 2010). "Independent" = independent team, not
independent biochemical knowledge.

## What the swap shows (brutally honest)
1. **GEM choice dominates the within-*Plasmodium* result.** Six reconstructions of the *same organism* against
   the *same screen* span **OR 0.86 -> 3.07** and recall 0.08 -> 0.26. The result is a property of the model,
   not of "*Plasmodium* biology" as an immutable fact -> the GEM axis is real and large.
2. **iPfal19 is NOT uniquely broken.** One independent GEM (iAM-Pf480) **PASSES** (OR 3.07) where iPfal19
   fails, and iPfal19 (2.47) sits mid-pack, above 3 of the 5 other reconstructions. So the pre-registered
   "at least 1 independent GEM passes -> the failure was GEM-specific" branch **fired.** The confound resolves
   **substantially toward the GEM axis.**
3. **BUT GEM choice does NOT close the *Plasmodium*<->*Toxoplasma* gap — do NOT overclaim.** The *best*
   independent Pf GEM (3.07) barely clears the bar and is **4.6x weaker than Toxoplasma's 14.10.** And the
   **experimental base rate stays ~0.63-0.69 across ALL six Pf GEMs** vs 0.42 for Toxo — base rate is
   organism-intrinsic and GEM-invariant, so it mechanically compresses every Pf OR regardless of curation.
   The independent GEMs also **DISAGREE** (1.03 vs 3.07), so "swap the GEM and Plasmodium passes" is false.
   A residual *Plasmodium* biology / base-rate component survives the swap.

## Mechanistic salvage-bypass test — NEGATIVE for the specific hypothesis
For each FBA false-negative (exp-essential but FBA-dispensable), we categorized WHY it is dispensable:
GPR_redundant (isozyme) / salvage_import (a blocked-reaction metabolite is importable) / internal_reroute.
| | iPfal19 (FAIL) | iTgo2020 (PASS) |
|---|---|---|
| false negatives | 218 | 113 |
| GPR_redundant | 100 | 30 |
| salvage_import | 107 | 72 |
| internal_reroute | 11 | 11 |
| **salvage-explained frac (of non-redundant FN)** | **0.907** | **0.867** |

**The predicted separation does NOT appear.** Toxoplasma's false-negatives are *also* dominated by
salvageable products (0.87), essentially as much as Plasmodium's (0.91). So the mechanistic claim
"*iPfal19*'s FNs are salvageable but Toxo's are not" is **NOT supported** — the PASS/FAIL difference is driven
by the **number** of false-negatives (iPfal19 recall 0.20 vs Toxo 0.51), not by a qualitatively different
bypass mechanism. **Honest caveat:** both models run fully-open media (221 / 240 importable species), so the
"salvage_import" category is near-saturated and has limited discriminating power — this is a boundary of the
test, reported not hidden.

## Which axis the combined evidence supports
**GEM topology is confirmed as a major axis** (huge within-Plasmodium variance; iPfal19 not uniquely bad; an
independent GEM passes) — this vindicates HARDENP1's *direction* of correction. **But not to the exclusion of
biology/base-rate:** no Pf reconstruction reaches Toxo-level enrichment, base rate is GEM-invariant at ~0.64,
and the salvage-topology *mechanism* specifically is falsified. The disciplined statement: **the malaria FBA
failure is substantially — but not entirely — GEM-dependent; a base-rate/biology residual remains, and the
Plasmodium<->Toxoplasma gap is multi-causal, not a pure GEM artifact.**

## Residual confounds that remain UNRESOLVED (stated plainly)
- **Screen technology (Zhang piggyBac vs Sidik CRISPR): NOT controllable CPU-only.** No genome-wide
  saturating *Plasmodium* CRISPR essentiality screen was obtainable; the Pf CRISPR-KO literature is
  gene-by-gene, not genome-scale. The CRISPR-vs-piggyBac axis stays a standing limitation.
- **Organism biology:** controlled *within* Plasmodium by the swap, but the Plasmodium-vs-Toxoplasma
  comparison still crosses organisms.
- **Base rate** (~0.64 Pf vs 0.42 Tg): reported per model, GEM-invariant, not eliminated.
- **Knowledgebase non-independence:** all Pf GEMs share upstream biochemistry; independence is team-level only.

## Provenance
Models (sha256, first 16): iPfal19 `7a19f5b77aa0b1d4`, Chiappino-Pepe `1dba71ff42b588a4`, iAM-Pf480
`2d047a34e383d89b`, iPfal17 `614fe67a4158fa3b`, gf `9c8b5c5aa37bf1b2`, gf_no_ortho `ca5092500413ead0`.
Independent GEMs fetched from github.com/maureencarey/paradigm `models/published/`. Zhang 2018 truth (same
file as GENERALIZE5). iTgo2020 + Sidik 2016 reused from HARDENP1. cobra 0.31.1, GLPK, KO growth rounded 6dp.
Estimator frozen to sample OR + math.comb hypergeometric. Gate frozen in PREREG.md before scoring.
Reproduced x2 byte-identical, payload sha256 `2bbbf68cac59c4296a63fe4471381f113952d152ce327c93b52fc6c82253183e`.
NOT git-committed; data not committed.
