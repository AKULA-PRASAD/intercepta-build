# GENETICCLASS1 — disease-class deployment envelope for zero-data genetic target-ID (PRE-REGISTRATION)

*Locked 2026-08-11, before computing any class-level statistic. Extends the transfer-condition principle from
ORGANISM classes (the FBA target-ID arm: bacteria FULL / parasite CAPPED / virus ABSTAIN) to DISEASE classes
for the human-genetics target-ID arm. GENETICS1 established a POOLED genetic-support→clinical-precedence signal
(OR 2.26, fame-attenuated to ~[1.67,2.26]) across 27 complex diseases and a per-disease OR, but NEVER a
per-disease-CLASS deployment envelope or a class-aware abstention gate. This builds that: for which disease
classes does zero-data genetic target-ID transfer, and where should the composite router cap/abstain?
Coverage-characterization (not a new algorithm), validated on cached Open Targets. Falsify-first: a class with
no robust signal is reported as an ABSTAIN class, first-class.*

## Data (cached; no new data)
Genome-wide universe rebuilt exactly as GENETICS1/MR1 — **20,596 NCBI protein-coding genes × 27 diseases**
(`$INTERCEPTA_DATA/genetics1/`: parquet + `Homo_sapiens.gene_info.gz` + `gene_pubcounts.json`); `genetic_association`
and `clinical` (ChEMBL precedence) from the OT slice, 0 elsewhere; `drug = clinical>0`. **The full universe is
mandatory** — the parquet evidence-subset is collider-biased (MR1 lesson: it inverts the OT signal to OR 0.6).

## Frozen disease-class mapping (6 classes; assigned by standard therapeutic-area/EFO-MONDO ontology, before scoring)
- **immune_inflammatory (10):** psoriasis, inflammatory bowel disease, multiple sclerosis, ankylosing spondylitis,
  systemic lupus erythematosus, rheumatoid arthritis, psoriatic arthritis, atopic eczema, type 1 diabetes, asthma.
- **neuro_psychiatric (6):** major depressive disorder, Alzheimer disease, amyotrophic lateral sclerosis, epilepsy,
  schizophrenia, Parkinson disease.
- **cardiovascular (3):** hypertension, coronary artery disorder, heart failure.
- **metabolic (3):** obesity, type 2 diabetes, metabolic dysfunction-associated steatotic liver disease.
- **respiratory_fibrotic (2):** chronic obstructive pulmonary disease, idiopathic pulmonary fibrosis.
- **musculoskeletal_renal (3):** osteoarthritis, osteoporosis, chronic kidney disease.

## Per-class statistics (computed on the genome-wide universe, pooled within class)
1. **Enrichment:** Fisher OR (genassoc>0 vs drug=1) with 95% CI; **Mantel–Haenszel OR stratified by disease**
   within the class (guards against a single disease driving it); genassoc-AUROC for drug.
2. **Fame control (GENETICS1's known confound):** grouped (by-disease) logistic `drug ~ z(genassoc) + z(logpub)`;
   report the genassoc coefficient sign + bootstrap 95% CI per class — does the signal survive fame adjustment?

## Pre-registered per-class GATE (the deployment envelope → router transfer-condition table)
Per class, grade the genetic target-ID arm:
- **FULL** iff MH-OR 95% CI-lower > 1.5 **AND** the fame-adjusted genassoc coefficient CI-lower > 0.
- **CAPPED** iff MH-OR CI-lower > 1.0 but fails a FULL criterion (signal present but fame-confounded or weak).
- **ABSTAIN** iff MH-OR CI-lower ≤ 1.0 (no robust class-level signal).
This yields a disease-class transfer-condition table — the human-genetics analog of the FBA organism-class table.

## Hypothesis (falsifiable)
The genetic target-ID signal is **non-uniform across disease classes** — stronger where human genetics is
well-powered/mechanistically-direct (immune/metabolic) and weaker/absent where it is not (e.g., psychiatric).
PASS = the envelope discriminates (≥1 FULL class AND ≥1 non-FULL class, each by the locked gate). If all classes
are FULL or all ABSTAIN, that uniform result is reported honestly as-is.

## Integration
Emit `disease_class_transfer_table.json` (class → grade + evidence) for the composite router, making the
human-genetics arm disease-class-aware (as FBA is organism-class-aware) with cited abstention.

## Rigor / scope
Reproduce ×2 byte-identical (deterministic; bootstrap seed 42). Honest scope: characterizes the *deployment
envelope* of an existing validated arm across disease classes (coverage, not a new method); retrospective, OT
clinical-precedence as ground truth (not clinical validation); class assignment is a frozen ontology choice.
`results/GENETICCLASS1_metrics.json` (sorted keys) + `payload.sha256`; no data committed.
