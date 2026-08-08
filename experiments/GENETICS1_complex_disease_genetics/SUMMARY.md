# GENETICS1 — Summary

**Verdict: PASS — the THIRD human-disease arm (common / complex / polygenic), popularity-CONTROLLED.**
Reproduced x2 byte-identical, payload sha256 `9e73d1c82b681cbc8b32766da5abc94a151da214b2fd15332dde2de05e2aba25`.

INTERCEPTA covers somatic **cancer** (DEPEND1) and germline **monogenic** disease (MENDEL1). GENETICS1 adds the largest, previously-uncovered human paradigm — **common/complex/polygenic disease** — using **human genetics** as a target-relevance signal that sidesteps the popularity confound that sank generic human single-disease target-ID (DEPEND1/F3CLIN1).

## Dataset (real, cited, frozen — no fabrication)
- **Open Targets Platform 26.06** (CC0) GraphQL: full associated-target lists for **27 pre-registered common/complex/polygenic diseases** (T2D, CAD, IBD, RA, asthma, schizophrenia, Alzheimer, Parkinson, MS, SLE, psoriasis, obesity, hypertension, ...; cancers + cystic-fibrosis excluded as DEPEND1/MENDEL1 territory). Frozen `genetics1_dataset.parquet` (173,042 rows, sha `fc292ef8...`).
- **NCBI gene2pubmed + gene_info** (public): gene-level publication counts (`gene_pubcounts.json`, sha `1e531696...`) and the **20,596 protein-coding gene** universe.
- **Genome-wide analysis unit:** 20,596 genes x 27 diseases = **556,092 (disease, gene) pairs**.
- Predictor = OT `genetic_association` (L2G/GWAS/ClinVar; evidence-based, not text-mined). Outcome = `clinical>0` (ChEMBL known drug for the indication). Popularity confounder = gene publication count (primary) + OT `literature` (secondary).
- All data live ONLY in `$INTERCEPTA_DATA/genetics1/` (incl. the 282MB gene2pubmed.gz). Nothing committed.

## Results vs pre-registered gates
- **G1 — Nelson-2015 replication (PASS).** Genetically-supported genes enriched for approved/clinical drug targets genome-wide: **Fisher OR = 2.26 (p = 1.2e-63)**; Mantel-Haenszel by disease OR = 2.06 (p = 6e-62); random-gene null emp p = 1e-4. Dose-response: OR 2.26 -> 2.43 -> 2.73 -> 3.03 -> 3.26 -> **5.18** across genetic_association > {0,.05,.1,.2,.3,.5}.
- **G2 — DECISIVE popularity/study-bias null (PASS — genetics beats popularity).** Controlling for gene **publication count**:
  - (2a) fame-decile **matched-permutation null**: emp **p = 1e-4**.
  - (2b) **fame-adjusted Mantel-Haenszel OR = 1.67 (p = 1.6e-31)** at any genetic support, rising dose-responsively and **crossing OR>2 at genetic_association>0.2** (2.01) up to **2.92 at >0.5**.
  - (2c) **logistic** genetic coef **+0.090 (p = 3.2e-37)** beyond fame, **+0.058 (p = 5.9e-16)** beyond fame AND disease-literature jointly.
  - Secondary literature-adjusted MH-OR = 1.32 (p = 8.6e-10).
- **G3 — generalization (PASS).** Leave-one-disease-out fame-adjusted logistic: genetic coef > 0 & p < 0.05 in **27/27** folds; per-disease crude Fisher OR > 1 in **27/27** diseases.

## Honest attenuation and caveats (brutal honesty)
- Popularity explains a **substantial share** of the crude effect: OR **2.26 -> 1.67** after fame adjustment. Genetics is **not** popularity-free at the permissive cut, but retains a highly significant, dose-responsive independent effect, clearing OR>2 only at **moderate/strong** genetic support (score>0.2). Weaker than F3CLIN1, whose dependency signal ROSE under stratification (2.55 -> 2.72); here it is attenuated but survives.
- **Collider caveat (both directions):** publication count / literature are partly *caused by* drug-status (drug-targets mean log-pub 5.28 vs 4.81), so adjusting over-controls -> the true popularity-free effect is **bounded between crude (2.26) and adjusted (1.67)**. A fully clean causal test of the Nelson effect needs a **temporal/prospective** design not runnable on this cross-sectional snapshot.
- **Scope (hard line):** in-silico TARGET-RELEVANCE via genetics — NOT drug-response (B20/B10/B17 remain negative), NOT a molecule, NOT clinical efficacy. Contribution = a popularity-confound-controlled complex-disease router arm + honest abstention where genetic evidence is absent. Intervention still hits the affinity wall (HIT2/B49/B65). `clinical`<->drug-development circularity and ALS/epilepsy genetic heterogeneity flagged.

## Correction trail (transparency)
- **v1 flaw:** top-500-by-OT-overall universe is a **collider** of predictor+outcome -> Berkson bias -> spurious OR **0.07**. Fixed to the correct **genome-wide** universe (gate numbers unchanged).
- **Pre-freeze bug caught:** an intermediate set pub=0 for genes unlisted-for-a-disease -> spurious fame-adjusted MH 0.70. Fixed to use **real** NCBI publication counts for every gene -> 1.67. The PASS depends on this correct construction.

## LEDGER verdict (one line)
GENETICS1 = PASS (reproduced x2, sha 9e73d1c8): the third human-disease arm — common/complex/polygenic — via human genetics, popularity-CONTROLLED. Genetically-supported genes enrich for approved/clinical drug targets genome-wide (Fisher OR 2.26, p 1e-63; dose-response to 5.18) and the enrichment SURVIVES the study-attention null (gene-publication-count-adjusted Mantel-Haenszel OR 1.67, p 1.6e-31, crossing OR>2 at genetic>0.2; logistic genetic coef p 3e-37 beyond fame, p 6e-16 beyond fame+literature; 27/27 leave-one-disease-out). HONEST: popularity explains much of the crude effect (2.26->1.67 attenuation) and the proxies partly over-control a collider, so the popularity-free effect is bounded [1.67, 2.26] — a real but attenuated signal, weaker than F3CLIN1's. SCOPE: target-relevance only, cross-sectional OT 26.06, not response/molecule/clinical; intervention still affinity-wall-gated. Data OT 26.06 + NCBI gene2pubmed, $INTERCEPTA_DATA only, not committed.
