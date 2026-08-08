# PHENO1 — Pre-registration (FROZEN before final scoring)

**Arm / gap:** Every prior INTERCEPTA arm requires a genome / known gene / screen as INPUT. Real diseases
PRESENT as a **phenotype** (symptoms), often before a gene is known. This builds the **phenotype-INPUT front
door**: a set of HPO phenotype terms → a ranked list of candidate causal genes, which then hands off to the
validated genetic arms (MENDEL1 monogenic / GENETICS1 complex). It extends the INPUT modality of the composite
system toward the fullest "any disease" case.

**HONEST SCOPE (binds every claim, frozen):** this is **RETRIEVAL over KNOWN HPO→gene associations** — a
validated lookup+ranking — **NOT de-novo mechanism inference** for a never-seen phenotype (that is the OPEN
frontier per INVENTION_ROADMAP "Deeper frontiers"; it is explicitly NOT attempted here). The deliverable
identifies **candidate** genes; it does NOT validate them, does NOT produce a molecule (the affinity wall
HIT2/B49/B65 still gates intervention), and does NOT itself perform mechanism inference. Value = a phenotype
front-door that feeds candidate genes INTO MENDEL1/GENETICS1.

## Data (REAL, cited, frozen BEFORE scoring; data only in `$INTERCEPTA_DATA/pheno1/`, never committed)
Human Phenotype Ontology (HPO), release **2026-06-23** (hp/releases/2026-06-23), open (HPO license). Files +
SHA-256 (verified by run.py before scoring):
- `phenotype.hpoa` — disease → HPO annotations. sha `89004f85b253f980ffe84218d2c080665cbf67a57bbb322111d6a2db5eb31dff`
- `genes_to_disease.txt` — disease → causal gene(s) + association_type. sha `a247027ae9944e34545e0a91060243ff6c118681c06379b9721af1ee4f39286a`
- `genes_to_phenotype.txt` — (provenance only; not used in scoring). sha `26cb7ee00c73b5777f6e5ad43323c941e1fcef1d191592f332d7929f3ea1ab3f`
- `phenotype_to_genes.txt` — (provenance only; not used in scoring). sha `1386a4dd3ea046f5a5971f4011a3711a9d7928d60961e2e7b757b6860c63c778`
- `hp.obo` — the HPO DAG (is_a) for ancestor propagation + IC. sha `a5092cbdf605f568403cf7380d9173014015692433b2cc631bc5c1b053876b1b`

Source: https://purl.obolibrary.org/obo/hp/hpoa/ and https://purl.obolibrary.org/obo/hp.obo (fetch-once,
`fetch_data.py`).

## Task, ground truth, and the LEAKAGE control (the crux)
- **Disease phenotype profile** = the set of HPO terms annotated to a disease with `aspect == P` (phenotypic
  abnormality) and `qualifier != NOT`, in `phenotype.hpoa`. Inheritance/onset/modifier aspects are excluded.
- **Ground-truth causal gene(s)** for a disease = genes in `genes_to_disease.txt` (association_type
  MENDELIAN / POLYGENIC / UNKNOWN, all retained; a MENDELIAN-only robustness cut is reported in G3).
- **Candidate gene universe** = all genes appearing in `genes_to_disease.txt` (deterministic, sorted).
- **LEAKAGE control (leave-one-disease-out, mandatory).** `genes_to_phenotype` is derived FROM disease
  annotations, so a gene's phenotype profile trivially contains the test disease's own phenotypes → scoring a
  disease against that would be circular. Instead each **gene profile is built from disease annotations
  MINUS the held-out disease**: for test disease D with candidate gene g, g's profile is the union of the
  propagated HPO terms of *all other* diseases g causes; g's own contribution from D is removed. A gene that
  causes ONLY D therefore has an EMPTY profile and is (correctly) unrecoverable — that singleton-gene fraction
  is an inherent honest bound, reported, and such cases count as MISSES (not silently dropped).

## Scoring (PRE-REGISTERED, deterministic — fixed before any metric was computed)
1. **Ancestor propagation:** each disease/gene term set is closed over `is_a` ancestors from `hp.obo`
   (alt_ids mapped to primary; obsolete terms dropped).
2. **Information content:** `IC(t) = -ln( n_diseases_with_t_in_propagated_profile / N_diseases )` over the full
   disease corpus (a global term-rarity statistic; not a D→g label).
3. **Retrieval score** for (disease D, gene g) = **cosine similarity of IC-weighted binary term vectors**
   (vector[t] = IC(t) if t in propagated set else 0; L2-normalized). Gene vector is the LODO profile above.
   Genes ranked by `(-score, gene_symbol)` (symbol tie-break → deterministic).
4. **Baselines:** (a) **frequency-prior** = rank genes by LODO pleiotropy degree (# other diseases the gene
   causes), tie-break by symbol — the "always guess the usual suspect genes" popularity null; (b) **random** =
   analytic expectation + permutation null (K=10000, seed=42) drawing a random gene per disease.
5. **Metrics:** recall@1, recall@5, recall@10 and MRR (a disease is a HIT@k if ANY true gene is in the top-k;
   RR uses the BEST rank among true genes). Reported for ranker, frequency-prior, random.

## Abstention rule (PRE-REGISTERED, fixed constants — abstention-integrity over coverage)
ABSTAIN (return no ranking) for disease D iff the phenotype profile is too small/nonspecific to discriminate:
- fewer than **N_MIN = 3** distinct DIRECT phenotype terms, **OR**
- the disease's most specific direct term has **IC below the median IC** across all annotated terms
  (i.e. no term more specific than a typical term).

Abstained diseases are NOT scored for retrieval; the **abstention rate** is reported. The rule is validated in
G2 (below): it must target genuinely harder cases.

## Pre-registered gates (numbers fixed before final scoring)
- **G1 (PRIMARY — retrieval lift over the popularity null):** on the NON-abstained cohort, the ranker
  **recall@10 exceeds the frequency-prior baseline recall@10 by ≥ 0.10 absolute** AND ranker **MRR exceeds**
  baseline MRR, with the per-disease reciprocal-rank improvement significant at **p < 0.01** (paired Wilcoxon
  signed-rank), AND ranker MRR exceeds the random-permutation null at **empirical p < 0.01** (K=10000, seed=42).
- **G2 (abstention integrity — first-class):** the abstention rule is well-targeted, i.e. recall@10 on the
  would-be-scored ABSTAINED cases is **lower** than recall@10 on the SCORED cases (abstention removes genuinely
  harder profiles, it is not arbitrary). Abstention rate reported.
- **G3 (generalization/robustness — supporting):** the G1 lift (recall@10 margin ≥ 0.10 and MRR lift) **holds**
  on the MENDELIAN-only ground-truth subset (the cohort that feeds MENDEL1). recall@1 lift also reported.

**Overall verdict rule (frozen):**
- **PASS** = **G1 AND G2** → a validated phenotype-input retrieval front door extending the "any disease" INPUT
  modality into the genetic arms.
- **NEGATIVE (first-class honest bound)** = G1 fails (no lift over the frequency-prior/random null) → an honest
  bound: HPO phenotype overlap does not recover causal genes above popularity. Reported plainly; NOT tuned to pass.

## Honesty / determinism
Retrieval over KNOWN associations (validated lookup+ranking), NOT de-novo mechanism inference (OPEN, not
attempted). Identifies candidate genes only; does not validate them or produce therapy (affinity wall stands).
LODO removes the circularity; singleton-gene diseases are an honest unrecoverable bound (reported, counted as
misses). IC uses the full corpus (global rarity, symmetric). Fixed seed 42; deterministic sparse linear algebra;
symbol tie-breaks; payload SHA-256 over sorted-key JSON excluding verdict/provenance. Reproduce ×2 byte-identical.
