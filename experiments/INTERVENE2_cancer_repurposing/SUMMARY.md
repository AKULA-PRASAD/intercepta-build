# INTERVENE2 — Cancer target→intervention (repurposing / druggability) — SUMMARY

**Verdict: G1 PASS (mapping validated) · G2 honest ceiling reported.** Reproduced x2 byte-identical.
Payload SHA-256: `8f3ac2d639270af3a3ebee52c8597727bcfab0ab2010bb02fc5a73b1ffeb73eb`.

The HUMAN/CANCER analog of INTERVENE1 (bacteria: 9/9 antibacterial-target MoA recovery, narrow 1/32
novel-pathogen repurposing ceiling). DEPEND1 validated cancer TARGET-ID (selective CRISPR dependency);
F3CLIN1 showed those targets are patient-driver-relevant. INTERVENE2 closes the target→intervention
loop on the achievable (repurposing) slice and reports the honest druggability ceiling. The shape is
exactly as predicted: **the target→drug MAPPING recovers known cancer pharmacology perfectly, but the
large majority of validated selective dependencies are UNDRUGGED (de-novo-chemistry-gated).**

## DEPEND1 selective set reproduced? YES
Re-derived on the same DepMap Chronos matrix with DEPEND1's EXACT frozen definition (dep = effect <
−0.5; SELECTIVE = dep_frac 0.01–0.50; pan-essential > 0.90 EXCLUDED). Reproduced **n_selective = 3664**
exactly (assert in code), pan-essential = 1020, over a 17931-gene universe. No definition drift.

## G1 — canonical cancer drug-target MoA recovery (MAPPING validation): PASS
Recovery = **10/10 (100%)**. The mapper (gene symbol → human ChEMBL drug-target UniProt → drugs/MoA/
action; no drug names fed in) independently retrieved a drug whose MoA text + action matches the known
mechanism for every pre-registered canonical target: BRAF→RAF-kinase inhibitor, KRAS→GTPase-KRas
inhibitor, EGFR→EGFR inhibitor, ERBB2→erbB-2 inhibitor, PIK3CA→PI3-kinase inhibitor, CDK4/CDK6→CDK
inhibitor, MDM2→p53/Mdm2 inhibitor, BCL2→Bcl-2 inhibitor, MAP2K1→MEK/MAP-kinase-kinase inhibitor.
Analog of INTERVENE1's antibacterial 9/9.

**Null / specificity (mapping is specific, not promiscuous):**
- Mislabel-permutation null (K=2000, seed 42): reassigning each canonical gene to a random drug-target
  protein gives mean recovery **0.2%** (p = 5e-4). The recovery is not a lucky base rate.
- Only **16 of 3664** selective genes match ANY canonical MoA keyword (the 10 true targets + a few
  paralogs, e.g. NRAS matching a "RAS" keyword) — the specific mechanisms are not assigned to random
  dependencies.
- Base rate: random non-canonical selective genes are drugged at 6.5% (the genome-wide selective rate),
  vs 100% for the canonical set.

## G2 — honest druggability CEILING (descriptive) — the headline
Of the **3664** validated selective dependencies, only **248 (6.8%)** have ANY existing ChEMBL-annotated
ligand (repurposing-addressable); **3416 (93.2%) are UNDRUGGED** — no existing drug, so de-novo-chemistry-
gated (the F4 ceiling). This is the cancer analog of INTERVENE1's narrow 1/32 bacterial ceiling.

| selective dependencies | n | fraction |
|---|---|---|
| DRUGGED — approved drug (max_phase 4) | 167 | 4.6% |
| DRUGGED — investigational only (phase I–III) | 81 | 2.2% |
| DRUGGED — preclinical/unknown | 0 | 0.0% |
| **UNDRUGGED (no ChEMBL ligand)** | **3416** | **93.2%** |

max_phase from a frozen ChEMBL-REST cache (4450 human drug ids; fetched once, read deterministically at
scoring time — no network in the scored run).

**Patient-driver subset (IntOGen, reused from F3CLIN1):** the 240 selective∩driver genes are ~3.4×
more druggable (**48/240 = 20.0%**) than non-driver selective genes (5.8%) — consistent with drivers
being better-studied/targeted — but **80% of even the driver-relevant selective dependencies remain
undrugged.** So the ceiling is real even where target relevance is strongest.

## HARD SCOPE (binds the claim)
- Recovering a known drug-target pair is a **MAPPING validation, NOT a therapeutic/clinical claim and
  NOT drug-response prediction** — drug-response is tested-NEGATIVE elsewhere (B20 FIMM fails, B10 TCGA
  confounded, B17 BeatAML null). This must never be read as clinical validation.
- **"DRUGGED" = has a ChEMBL-annotated ligand, NOT efficacious/selective/safe in a patient.**
- UNDRUGGED selective dependencies remain de-novo-chemistry-gated (the F4 ceiling).
- Symbol-exact matching (both sides HGNC) can only UNDERcount druggability (HGNC-synonym misses are
  conservative for a ceiling claim), so the true drugged fraction is ≥ 6.8%.
- Cancer cell-line dependency layer; NOT wet-lab, NOT clinical, NOT a novel-pathogen result.

## Reproducibility
run.py → results/INTERVENE2_metrics.json (sorted keys) + results/INTERVENE2_payload.sha256. Payload =
sorted-key JSON of numeric results (excludes verdict/provenance); run twice, identical
(`8f3ac2d639270af3a3ebee52c8597727bcfab0ab2010bb02fc5a73b1ffeb73eb`). Seed 42, K=2000, CPU-only. No git
commit/push; no data committed.
