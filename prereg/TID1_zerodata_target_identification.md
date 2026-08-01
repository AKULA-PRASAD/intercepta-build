# TID1 — Zero-data target identification: recover known druggable/essential targets from a pathogen proteome ALONE, by cross-organism homology transfer, validated leave-organism-out (finalized 2026-07-31, PRE-RESULT)

(TID1 = Target-IDentification chapter 1 — the first FRONT-HALF capability. Unrelated to the historical aspirational "Phase F".)

## Vision alignment (all 5 questions, answered)
Front-half capability (disease→target), **zero-data-native** (pathogen proteome/sequence only; NO disease-specific
activity data, NO known inhibitors), built as the **first adapters on a minimal LIVING substrate** (VISION principles
1,4,6). Q1 capability: target identification + essentiality + selectivity. Q2 generalizes beyond a benchmark: yes — the
mechanism is *transfer*, disease-agnostic. Q3 matters for a never-seen disease: yes — this IS the "new pathogen genome,
no data" path (research: homology is THE load-bearing zero-data lever; Paxlovid/SARS-CoV-2 precedent). Q4 if it succeeds:
raises confidence a new pathogen could be triaged to targets in hours. Q5 if it fails: eliminates "homology transfer
alone suffices," forcing structure (Foldseek/ESMFold) or mechanistic (GEM) capabilities earlier.

## Phase-0 hypothesis-space (4 paradigms investigated → this selection)
Investigation (4 parallel threads) established: KG/graph-ML (TxGNN/Open Targets) is strong where curated biology exists
but **cold-starts on truly novel diseases**; **comparative/functional-genomics homology transfer is the zero-data-native
path** (works from sequence alone — chosen); LLM/agentic is orchestration glue, not a truth source; the enduring
architecture is an **ontology-grounded, provenance/confidence-tiered LIVING substrate with pluggable adapters**. The
field's real weak spot (2 threads independently) = the **honest validation harness** (degree-null, leave-out, temporal,
leak-audit) — our differentiator. TID1 builds the zero-data-native signal AND the substrate, under those guardrails.

## The zero-data contract (binding)
May use ONLY: the target organism's protein sequences + general/transferable knowledge from OTHER organisms. May NOT
use: the target organism's own essentiality/target labels for any prediction (leave-organism-out), nor any
disease-specific activity data. Ground-truth labels are read ONLY at final evaluation.

## Data (OPEN, fetched/verified at build; feasibility-gated)
- **Proteomes:** UniProt reference proteomes for a documented pathogen panel + human (free). Panel (≥5, diverse):
  e.g. *E. coli*, *M. tuberculosis*, *S. aureus*, *P. aeruginosa*, *S. pneumoniae* (+ SARS-CoV-2 as a viral case).
- **Essentiality ground truth + transfer source:** OGEE v3 (freely downloadable essential-gene calls across organisms)
  — provides BOTH the leave-organism-out transfer source AND each organism's held-out essential-gene truth.
- **Druggable-target ground truth (secondary):** documented drug targets per organism from Open Targets / ChEMBL /
  DrugBank-derived lists (whichever is freely obtainable; sourced, never hand-invented).
- **Homology tool:** mmseqs2 installed in a FRESH `bioinfo` conda env (bioconda) — never the canonical env (the
  numpy/rogi lesson). ESM-2 embedding homology is a candidate SECOND adapter (extensibility demo), not v1.

## Design — first adapters on a minimal living substrate
For each protein in organism X's proteome, emit Biolink-typed, CURIE-identified, provenance+confidence-TIERED records:
- **Adapter-E (essentiality transfer):** best mmseqs2 homolog among OTHER organisms' OGEE-essential proteins → score =
  f(%identity, coverage); confidence tier from homolog quality; **abstain** if no homolog above threshold.
- **Adapter-D (druggability transfer):** homology to known druggable/drug-target proteins → druggability score.
- **Adapter-S (selectivity):** human-subtraction — penalize/flag proteins homologous to the human proteome (anti-target).
- **Compose:** ranked target list = query over the append-only store; each target carries provenance (which homolog,
  which organism, %id) + confidence tier + abstain flag. Adding an adapter re-ranks WITHOUT core changes (extensibility);
  a recovered+validated target becomes a tier-up record (the self-improving loop, demonstrated once). Guardrail:
  self-generated records stay quarantined at low tier — never used as ground truth.

## Metrics (leave-organism-out; per organism + panel)
Recovery of held-out KNOWN essential genes (primary) and documented drug targets (secondary): **AUROC, precision@k,
enrichment**, each vs three nulls — (1) random, (2) **degree/abundance null** (protein length / homolog-count only),
(3) **human-homolog-only** baseline. Plus phylogenetic distance to nearest characterized organism; abstention rate +
precision-on-abstained-vs-predicted.

## Hypotheses (pre-registered)
- **H1 (zero-data recovery):** leave-organism-out homology transfer recovers known essential/druggable targets **above
  random AND degree nulls** (panel-median AUROC > null + a margin; precision@k > null).
- **H2 (transfer degrades with distance):** recovery is higher for organisms with close characterized relatives, lower
  for distant — quantified (the honest boundary; expected).
- **H3 (selectivity):** human-subtraction improves druggable-target precision@k (fewer anti-targets).
- **H4 (abstention calibrated):** proteins the system abstains on have lower ground-truth target-precision than
  predicted ones → it knows what it doesn't know.
- **H0 (first-class):** transfer ≈ degree null → homology alone is insufficient here; forces structure/mechanistic
  capabilities earlier. Reported honestly.

## Honesty / scope
Retrospective recovery of KNOWN targets (proving ground), not prospective/wet-lab. Uses reference proteomes (ORF-calling
is a mature upstream step, noted, not the tested part). Essentiality ≠ druggability ≠ achievable drug (stated).
Orphan/"dark" proteins (10–30%, no homolog) are QUARANTINED and reported out-of-scope (research boundary). Leave-
organism-out + degree-null + human-subtraction guardrails are mandatory (the field's leakage/degree-bias failure modes).
Not a clinical claim.

## Reproducibility
Deterministic (mmseqs2 fixed params/seed, fixed thresholds, fixed panel, seeded any sampling). Reproduce ×2 byte-
identical (payload sha256 over per-organism recovery metrics + per-target records). Output:
`experiments/TID1_zerodata_target_identification/results/TID1_metrics.json`. Envs: `bioinfo` (mmseqs2), `intercepta-build`
(analysis). Build is feasibility-gated: (1) create `bioinfo` env + verify mmseqs2; (2) fetch + verify OGEE + proteomes
(MANIFEST rows w/ sha256); (3) smoke-test on 1 organism pair before the full leave-organism-out panel (the B63 no-blind-
run lesson).

---

## AMENDMENT (2026-07-31, PRE-BUILD — essentiality → druggability ground truth; feasibility-driven, nothing run)
Gate-2 feasibility check: **OGEE v3 is down and DEG is not cleanly programmatically accessible** (JS sites / redirects /
timeouts), so the OGEE/DEG essentiality ground truth + transfer source is **not obtainable** now. Rather than force it
(the B62 infeasibility lesson), the PRIMARY signal + ground truth pivots to **DRUGGABILITY TRANSFER**, which is fully
reachable, ID-matched to the proteomes, and arguably more on-point for target-ID:
- **Ground truth (per organism):** a protein is a "known drug target" iff its UniProt entry carries a **ChEMBL (and/or
  DrugBank) cross-reference**. Obtained via UniProt REST; ID-consistent with the reference proteome. Verified sizes
  (ChEMBL xref): *M. tuberculosis* 131, *E. coli* 182, *P. aeruginosa* 47, *P. falciparum* 52 — adequately powered;
  SARS-CoV-2 = 3 (kept as a QUALITATIVE viral case only, excluded from powered stats). *S. aureus* NCTC8325 (10) dropped
  / to be replaced by a better-annotated strain.
- **Signal:** each pathogen protein's best mmseqs2 homology to KNOWN drug-target proteins from OTHER organisms
  (leave-organism-out over the panel), NOT to the held-out organism's own targets. Human proteome used only for
  **subtraction/selectivity** (Adapter-S). **Essentiality (Adapter-E) is DEFERRED** to a later chapter if OGEE/DEG
  becomes accessible (a clean extensibility demo: a new adapter plugs into the same substrate).
- **Panel (powered, leave-organism-out):** *M. tuberculosis* (83332), *E. coli* K12 (83333), *P. aeruginosa* PAO1
  (208964), *P. falciparum* (36329) [+ SARS-CoV-2 (2697049) qualitative]. Hypotheses H1–H4 unchanged; H1 now = recovery
  of the **UniProt-annotated drug-target set** above random + degree + human-homolog nulls. Note druggability-transfer is
  expected to be strongest for conserved druggable families; the degree-null + leave-organism-out guard against triviality.
Documented; original essentiality framing retained above as the record.
