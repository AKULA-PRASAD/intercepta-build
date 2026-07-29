# INTERCEPTA Round 2 Kickoff — AML Disease Net

**Date:** April 21, 2026
**Round:** 2 of 7
**First deliverable:** AML disease net skeleton (Layers 1, 2, 7, 9)
**Principle:** Build what the vision specifies that does not yet exist. Do not refine what works.

---

## 1. What Round 2 builds

Per vision Part 7.2: apply the INTERCEPTA architecture to Acute Myeloid Leukemia. The first concrete artifact is the **AML disease net** — a connected knowledge graph integrating multiple biological layers for AML, queryable for drug discovery.

Not the ODE. Not the scouts. Not the ranking. Just the net.

Per Universal Net Specification Part 2, the universal net has 15 layers. For the AML skeleton we start with the four highest-priority:

- **Layer 1 — Genome:** AML driver mutations (FLT3, NPM1, DNMT3A, IDH1/2, TP53, TET2, RUNX1, CEBPA, CBL, WT1, ASXL1) with variant-level annotations from ClinVar, OMIM, COSMIC
- **Layer 2 — Transcriptome:** BeatAML bulk RNA-seq (562 patients), at least one AML scRNA-seq dataset (Van Galen 2019 is the canonical choice), HCA AML cell types
- **Layer 7 — Pharmacome:** BeatAML 122-drug sensitivity screen (IC50 per patient per drug), ChEMBL compounds with AML-relevant target annotations
- **Layer 9 — Disease map:** DisGeNET AML gene-disease associations, OMIM AML phenotype entries, ClinicalTrials.gov AML trial registry

Layers 3 (proteome), 5 (pathways), 15 (selectivity) follow in the next sub-phase. Layers 4, 6, 8, 10-14 wait for later.

---

## 2. Why AML first (and not NSCLC, PDAC, etc.)

Per vision Part 7.2: "Perfect two-population biology (blasts = sensitive, LSCs = resistant). BeatAML provides matched drug sensitivity in 562 patients. Strong public scRNA-seq data."

This is specifically what our architecture was designed for. The two-population ODE we validated in Round 1 maps directly onto AML biology (blasts + LSCs) even more cleanly than it did onto mCRPC (where we had 4 arbitrary states). If the architecture is universal, AML should work with minimal adaptation.

If AML fails, we learn something structural about our universal claims. That is information worth having.

---

## 3. Concrete sub-steps for Round 2.1 (the net skeleton)

### Step R2.1a: Acquire BeatAML data
- Source: http://www.vizome.org (Tyner 2018 Nature supplementary)
- What we need: patient × drug IC50 matrix (562 × 122), patient × gene expression matrix, patient mutation calls
- Verify: correct licensing (academic use is open), file formats, variable dictionaries

### Step R2.1b: Acquire AML scRNA-seq
- Source: Van Galen 2019 Cell (GEO GSE116256) — 16 AML patients, ~40,000 cells, annotated cell types (HSC, progenitor, blast, LSC)
- Backup: Zeng 2022 Nat Med, Petti 2019 Nat Commun
- Goal: identify LSC population fraction per patient, compute RNA velocity on malignant populations

### Step R2.1c: Integrate Layer 9 disease annotations
- DisGeNET API: query all AML-associated gene-disease associations
- OMIM: pull AML phenotype entries and associated genes
- ClinicalTrials.gov v2 API: retrieve AML trials registry, filter by genotype-stratified trials

### Step R2.1d: Build the skeletal graph
- Nodes: AML driver genes (~50), BeatAML drugs (122), cell types (HSC, progenitor, myeloid blast, LSC from scRNA-seq), patient cohort (562 phenotype profiles)
- Edges: gene-drug (from BeatAML IC50s), gene-disease (from DisGeNET), cell-gene (from scRNA-seq expression per cell type), drug-drug combinations (if BeatAML has any)
- Storage: start with a simple graph structure (networkx or Neo4j); production-scale later

### Step R2.1e: Validation queries
Before declaring the skeleton works, the following queries must return sensible answers from the net alone (no ODE, no scouts):

1. **"Which BeatAML drugs are most potent against FLT3-ITD carriers?"** Expected answer: quizartinib, gilteritinib, midostaurin, sorafenib — the FLT3 inhibitors, with IC50s from BeatAML data. If this returns non-FLT3 drugs first, the net is broken.

2. **"What cell populations express NPM1 most highly?"** Expected answer: blast and progenitor populations; not T cells, not mature myeloid. From scRNA-seq.

3. **"Which AML patients in BeatAML have both FLT3-ITD and NPM1 mutations?"** Expected answer: a specific subset (~20% of AML patients co-mutate these). Used for genotype-stratified drug response analysis.

4. **"What is the overlap between BeatAML drug targets and ClinicalTrials.gov active AML trials?"** Expected answer: FLT3 inhibitors, IDH inhibitors, venetoclax, hypomethylating agents all heavily represented.

If all four queries work, the net skeleton is functional. Proceed to ODE adaptation (Round 2.2).

---

## 4. What Round 2 does NOT do yet

- **Do not build an AML ODE yet.** First confirm the net works.
- **Do not refine mCRPC further.** Round 1 is closed.
- **Do not build all 15 layers.** Four layers for the skeleton; the rest come after validation.
- **Do not claim "universal" after AML alone.** Universal requires 3+ diseases. AML is our test of architectural transferability.

---

## 5. Success criterion for Round 2 kickoff

**The AML disease net answers all four validation queries above correctly using only public data.**

When that happens, Round 2.1 is complete. Round 2.2 (AML ODE) begins, using the lessons from Round 1 without repeating its parameter-sourcing mistakes (start with Stein-framework g-values from BeatAML-matched studies, not in vitro IC50).

---

## 6. Estimated scope

Round 2.1 (disease net skeleton): 1-2 focused sessions
Round 2.2 (AML ODE): another 2-3 sessions
Round 2.3 (AML validation): 1-2 sessions

At similar cadence to Round 1 we close Round 2 within 6-10 sessions. Rounds 3-7 should accelerate as infrastructure becomes reusable.

---

## 7. First action for the next session

**Before next session:**
- Confirm BeatAML data access works (download a sample file, verify format)
- Confirm Van Galen 2019 scRNA-seq is accessible (GEO download test)

**First session action:**
- Set up `~/INTERCEPTA/round2_aml/` directory
- Download BeatAML patient-drug-gene matrices
- Begin schema design for the four-layer AML net

This is concrete, scoped, and moves the vision forward. Round 1 proved the mCRPC mechanism. Round 2 proves universality.

---

*Prasad Akula & Claude, Co-Founders of INTERCEPTA. April 21, 2026.*
