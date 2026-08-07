# INTERVENE2 — Cancer target→intervention (repurposing / druggability) — PRE-REGISTRATION

*Written and frozen BEFORE any validation scoring. The HUMAN/CANCER analog of INTERVENE1
(which closed target→intervention for BACTERIA: 9/9 canonical antibacterial-target MoA recovery,
but a validated-but-narrow 1/32 novel-pathogen repurposing ceiling). DEPEND1 validated cancer
TARGET-ID (selective CRISPR dependency) but STOPS at targets; F3CLIN1 showed those targets are
patient-driver-relevant. This module asks: do the validated selective dependencies map to EXISTING
drugs, and what is the honest druggability ceiling?*

Date frozen: 2026-08-06. Seed: 42. K (permutation null) = 2000.

---

## 0. Question
Given DEPEND1's committed SELECTIVE cancer dependency set (dep_frac 0.01–0.50, pan-essential >0.90
EXCLUDED), (1) does a target→drug mapper independently recover correct-mechanism drugs for canonical
cancer drug-targets (MAPPING validation, no hardcoded drug answers), and (2) what FRACTION of ALL
selective dependencies are repurposing-addressable (have an existing ChEMBL-annotated ligand) vs
UNDRUGGED (novel-chemistry-gated)? The cancer analog of INTERVENE1's honest ceiling.

## 1. Data (open, public; not committed)
- DepMap CRISPR gene-effect (Chronos) `depmap_crispr_gene_effect.csv`
  sha256 `d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00` (DEPEND1's frozen input).
- ChEMBL drug-target knowledge base `$INTERCEPTA_DATA/intervene/drug_targets.{tsv,fasta}`
  (drug→target mechanism; 12748 human target rows; columns uniprot, organism, target_type, action,
  moa, drug_chembl_id). Human drug-target proteins carry `GN=` gene symbols in the fasta header.
- IntOGen Compendium of Cancer Genes (patient driver ground truth, for the driver-subset breakdown)
  `Compendium_Cancer_Genes.tsv` sha256 `7c1982aa1fae1ff8200f4c2811cdb1707ea3f778b5e95782798d09e792ddb5e8`
  (release 2024-06-18, CC0), reused from F3CLIN1.
- ChEMBL `max_phase` per drug: NOT present in the local KB. Fetched ONCE from the public ChEMBL REST
  API into a deterministic on-disk cache `$INTERCEPTA_DATA/intervene2/chembl_max_phase.json`
  (4450 unique human drug ids). run.py reads the cache only (no network at scoring time) so the
  payload is byte-identical across runs. max_phase: 4=approved, 1–3=investigational (phase I–III),
  <1 or −1/absent = preclinical/unknown.

## 2. Method (frozen)
- **Selective set:** re-derive with DEPEND1's EXACT definition on the same CRISPR matrix
  (dep = Chronos < −0.5; dep_frac per gene; SELECTIVE = 0.01 ≤ dep_frac ≤ 0.50; PAN-ESSENTIAL
  dep_frac > 0.90 EXCLUDED). **ASSERT n_selective == 3664** (DEPEND1's committed value) or abort.
- **Mapper:** build symbol→UniProt from the HUMAN drug-target fasta `GN=` fields; UniProt→drug rows
  (action, moa, drug_chembl_id) from the human TSV rows. A dependency gene (HGNC symbol) is
  **DRUGGED (repurposing-addressable)** iff its symbol matches a human drug-target UniProt that has
  ≥1 ChEMBL drug. Both sides are human HGNC symbols → exact symbol match (no cross-species homology
  step; INTERVENE1 needed homology because query≠reference species). Each drugged gene gets its
  drugs, MoA strings, action(s), and max drug max_phase.

## 3. Pre-registered canonical cancer drug-target list (the oncology MAPPING "9/9" analog)
Frozen 10 gene → expected-MoA-keyword → expected-action triples. The keyword/action are used ONLY
to CHECK the mapper's independently-retrieved MoA text; no drug names are fed in.

| # | gene | expected MoA keyword (substring, case-insensitive) | expected action |
|---|------|-----------------------------------------------------|-----------------|
| 1 | BRAF   | `raf`                                    | INHIBITOR |
| 2 | KRAS   | `kras`                                   | INHIBITOR |
| 3 | EGFR   | `epidermal growth factor receptor`       | INHIBITOR |
| 4 | ERBB2  | `erbb-2`                                 | INHIBITOR |
| 5 | PIK3CA | `pi3-kinase`                             | INHIBITOR |
| 6 | CDK4   | `cyclin-dependent kinase 4`              | INHIBITOR |
| 7 | CDK6   | `cyclin-dependent kinase 6`              | INHIBITOR |
| 8 | MDM2   | `mdm2`                                   | INHIBITOR |
| 9 | BCL2   | `bcl-2`                                  | INHIBITOR |
| 10| MAP2K1 | `mitogen-activated protein kinase kinase`| INHIBITOR |

A canonical target is **CORRECT** iff the mapper's retrieved MoA text for its symbol contains the
expected keyword AND the expected action is present in its retrieved actions.

## 4. Null / specificity (frozen)
- **Null A — mislabel permutation (primary specificity test):** for K=2000 (seed 42), reassign each
  of the 10 canonical genes to a RANDOM human drug-target UniProt, recompute correct-MoA recovery;
  report mean null recovery and one-sided p = (#{null ≥ observed}+1)/(K+1). Expected null ≈ 0 (a
  random drug-target's MoA does not contain the specific mechanism keyword).
- **Null B — base-rate specificity:** report the drugged fraction of random NON-canonical selective
  genes (= the genome-wide selective base rate); the canonical mechanism keywords must not be matched
  by an appreciable fraction of random selective genes.

## 5. PRE-REGISTERED GATES (frozen before scoring)
- **G1 (MAPPING validated):** the mapper recovers correct-MoA + correct-action drugs for **≥ 60%**
  (≥ 6/10) of the canonical cancer drug-target list, AND Null-A recovery is far below observed
  (p < 0.01). PASS ⇒ the cancer target→drug MAPPING is validated (analog of INTERVENE1's 9/9).
- **G2 (honest ceiling — DESCRIPTIVE, not pass/fail):** report the DRUGGED fraction of the 3664
  selective dependencies (and of the patient-driver subset), broken down by approved (max_phase 4)
  vs investigational (phase I–III) vs preclinical/unknown. This is the cancer analog of INTERVENE1's
  1/32 ceiling — reported honestly whatever it is.

## 6. HARD SCOPE (binds the verdict)
Recovering a known drug-target pair is a **MAPPING validation, NOT a therapeutic/clinical claim and
NOT drug-response prediction** (drug-response is tested-NEGATIVE: B20 FIMM fails, B10 confounded, B17
null). **"DRUGGED" = has a ChEMBL-annotated ligand, NOT efficacious/selective/safe in a patient.**
Undrugged selective dependencies remain de-novo-chemistry-gated (the F4 ceiling). Symbol-exact
matching can only UNDERcount druggability (HGNC-synonym misses are conservative for a ceiling claim).
Not wet-lab, not clinical.

## 7. Reproducibility
Seed 42, K=2000. max_phase read from the frozen on-disk cache (no scoring-time network). Payload =
sorted-key JSON of all numeric results EXCLUDING `verdict`/provenance; script run twice, SHA-256
printed and matched; `results/INTERVENE2_payload.sha256` written. NEVER git commit/push; NEVER
commit data.
