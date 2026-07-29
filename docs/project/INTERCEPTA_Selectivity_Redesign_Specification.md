# INTERCEPTA Selectivity Layer Redesign — Specification

**Subject:** Replace mCRPC-hardcoded `step6_gtex_selectivity.py` and `step6_fix_gtex.py` with a disease-parameterized selectivity module.
**Spec status:** LOCKED before code, per Round 2 discipline (P3 — research before code).
**Authors:** Prasad Akula and Claude (CSO), Co-Founders of INTERCEPTA
**Date:** 2026-05-06
**Predecessor:** Round 2.2c spec (`round2-2c-spec-locked`) — same locked-design discipline applied here.

---

## 1. Why this redesign exists

The current `step6_gtex_selectivity.py` and `step6_fix_gtex.py` were written for mCRPC and are mCRPC-specific by design, not by accident. Round 2 disease-net builds for AML and GBM produce selectivity output JSON with `prostate_tpm` as a literal field name and `prostate_tpm=0` as the value — meaningless for non-prostate diseases.

What's hardcoded:
- GTEx column search: `'prostate' in c.lower()` — only finds prostate
- Gene list: `['AR', 'KLK3', 'TMPRSS2', 'NKX3-1', 'FOLH1', ...]` — mCRPC-specific (KLK3 = PSA, AR = androgen receptor)
- Mutation frequency input file: `step2_mutation_frequencies.csv` — produced by mCRPC pipeline only
- Output schema: `"prostate_tpm": <value>` field name written verbatim to disease net JSON
- Safety classification labels: `'PROSTATE-SEL'`, `'LOW-IN-PROST'`

This is not a single-variable patch. It is a module rewrite. The redesign is locked here before any code is written.

---

## 2. Falsifiable design hypothesis

**H1:** A disease-parameterized selectivity module that takes a `disease_id` as input and outputs `tissue_tpm_by_tissue` + `selectivity_ratio` will produce equivalent or better mCRPC selectivity output to the current hardcoded module, AND will produce valid non-zero selectivity output for AML, GBM, and NSCLC disease nets.

**Falsification criteria:**
- For mCRPC: top-20 selectivity-ranked genes by the new module must include at least 8 of the current module's top-20 (allowing for legitimate ranking drift, but not silent regression).
- For AML: at least one of FLT3, NPM1, FLT3-ITD, IDH1, IDH2 must produce a numerical selectivity ratio (i.e., the disease-tissue lookup must succeed).
- For GBM: at least one of EGFR, IDH1, PTEN, TP53 must produce a numerical selectivity ratio.
- For NSCLC: at least one of EGFR, KRAS, ALK, ROS1 must produce a numerical selectivity ratio.

If any disease cannot produce numerical output, the redesign FAILS.

---

## 3. Disease-tissue mapping (locked table)

Verified against GTEx v8 (54 tissues including 11 brain regions, plus Whole Blood). Source: GTEx v8 documentation (PMC7737656, biorxiv.org/content/10.1101/787903).

| Disease ID | Primary tissue (GTEx v8 column name) | Comparator handling | Notes |
|---|---|---|---|
| `mcrpc` | `Prostate` | Single tissue | Original use case — preserved |
| `aml` | `Whole_Blood` | Single tissue | GTEx has NO bone marrow. Whole_Blood is the closest hematopoietic proxy. Document this honestly in output. |
| `gbm` | `Brain_Cortex` | Multi-tissue: also include all 11 brain regions in comparator denominator | GTEx has 11 distinct brain regions. Selectivity must use the union. |
| `nsclc` | `Lung` | Single tissue | |
| `crc` | `Colon_Sigmoid`, `Colon_Transverse` | Multi-tissue: average both colon regions | If we add CRC in future. |
| `brca` | `Breast_Mammary_Tissue` | Single tissue | If we add breast cancer in future. |

**Locked rule: each disease has exactly one config record.** The config is in a single source-of-truth YAML/JSON file at `~/INTERCEPTA/configs/disease_tissue_mapping.json`. Any future disease addition requires (a) verifying GTEx tissue name from official GTEx tissue list, (b) adding to the config, (c) NEVER hardcoding in the selectivity script.

**Honest limitation noted in spec:** The AML → Whole_Blood mapping is a known compromise. AML originates in bone marrow, but GTEx does not have a bone marrow tissue. Whole blood is the closest hematopoietic proxy available in GTEx. Future work could supplement with HPA (Human Protein Atlas) bone marrow data or BLUEPRINT epigenome data. For Round 2.2c-era pipeline, Whole_Blood is acceptable with documentation.

---

## 4. Disease gene list source convention (locked)

**Locked rule: gene lists come from disease-specific config files**, not from the selectivity script.

| Disease ID | Gene list source | Path | Status |
|---|---|---|---|
| `mcrpc` | mCRPC config | `~/INTERCEPTA/configs/genes_mcrpc.json` | NEW — extract from current step6_fix_gtex.py |
| `aml` | AML config | `~/INTERCEPTA/configs/genes_aml.json` | NEW — extract from MUTATION_GENES list in build_multimodal_features.py + AML pathway genes |
| `gbm` | GBM config | `~/INTERCEPTA/configs/genes_gbm.json` | NEW — extract from gbm_disease_net_action1.json existing gene list (458 genes) |
| `nsclc` | NSCLC config | `~/INTERCEPTA/configs/genes_nsclc.json` | NEW — to be created from EGFR/KRAS/ALK + KEGG NSCLC pathway when Workstream B begins |

Each config file format (locked):
```json
{
  "disease_id": "aml",
  "disease_full_name": "Acute Myeloid Leukemia",
  "gtex_primary_tissue": "Whole_Blood",
  "gtex_comparator_tissues": ["Whole_Blood"],
  "gtex_comparator_strategy": "single_tissue",
  "key_target_genes": ["FLT3", "NPM1", "DNMT3A", "IDH1", "IDH2", "RUNX1", "CEBPA", "TET2", "TP53", "ASXL1", "KIT", "KMT2A", "NRAS", "KRAS", "WT1"],
  "tissue_proxy_caveat": "GTEx has no bone marrow tissue. Whole_Blood is closest hematopoietic proxy."
}
```

Source-of-truth principle: **the selectivity script never decides which genes are 'key' for a disease.** That decision is data, in a config file, version-controlled.

---

## 5. New module architecture (locked)

**Filename:** `step6_selectivity_v2.py`

**Old files (preserved per P16, NOT edited):** `step6_gtex_selectivity.py`, `step6_fix_gtex.py`. Tagged in git as historical.

**API:**
```python
def compute_selectivity(disease_id: str,
                        gtex_data_path: Path,
                        config_dir: Path,
                        output_dir: Path) -> dict
```

**Inputs:**
- `disease_id`: one of `{mcrpc, aml, gbm, nsclc}` (extensible via config)
- `gtex_data_path`: path to `gtex_median_tpm.gct.gz` (existing — already downloaded for Round 1)
- `config_dir`: `~/INTERCEPTA/configs/`
- `output_dir`: `~/INTERCEPTA/results/`

**Output JSON schema (locked):**
```json
{
  "disease_id": "aml",
  "disease_full_name": "Acute Myeloid Leukemia",
  "primary_tissue": "Whole_Blood",
  "comparator_tissues": ["Whole_Blood"],
  "tissue_proxy_caveat": "GTEx has no bone marrow tissue. Whole_Blood is closest hematopoietic proxy.",
  "n_genes_evaluated": 15,
  "selectivity_per_gene": {
    "FLT3": {
      "primary_tissue_tpm": 12.4,
      "other_tissues_mean_tpm": 8.3,
      "other_tissues_max_tpm": 56.7,
      "selectivity_vs_mean": 1.49,
      "selectivity_vs_max": 0.22,
      "max_other_tissue": "Pituitary",
      "safety_classification": "MODERATE_TISSUE_SELECTIVE"
    },
    "NPM1": { "..." }
  },
  "computed": "2026-05-07T00:00:00",
  "module_version": "step6_selectivity_v2"
}
```

**No `prostate_tpm` field.** All field names are disease-agnostic. The disease identity is captured by `disease_id` and `primary_tissue` keys.

**Safety classification labels (locked, disease-agnostic):**
- `HIGHLY_SELECTIVE`: selectivity_vs_mean > 10
- `TISSUE_SELECTIVE`: selectivity_vs_mean > 3
- `MODERATE_TISSUE_SELECTIVE`: selectivity_vs_mean > 1.5
- `UBIQUITOUS`: 0.5 ≤ selectivity_vs_mean ≤ 1.5
- `LOW_IN_TARGET_TISSUE`: selectivity_vs_mean < 0.5
- `NOT_EXPRESSED`: primary_tissue_tpm < 1.0

Old labels (`'PROSTATE-SEL'`, `'LOW-IN-PROST'`) are retired.

---

## 6. Implementation requirements (binding)

These are not suggestions. They are spec.

1. **Fail-closed on any missing input.** If `disease_id` is not in config, abort with explicit error. If GTEx data is missing, abort. If gene list config is missing, abort. No silent zeros.

2. **No hardcoded disease names anywhere in `step6_selectivity_v2.py`.** Search the source for the string "prostate" — should appear only in docstrings or comments referring to the original mCRPC use case, never in logic.

3. **GTEx column lookup must use the config's `gtex_primary_tissue` value verbatim.** Substring matching is forbidden — too easy to false-match (e.g., "Brain" matching multiple tissues unintentionally).

4. **Multi-tissue comparator handling.** When `gtex_comparator_strategy = "multi_tissue"` (e.g., GBM with 11 brain regions), the script must average across the listed tissues for the comparator denominator AND properly handle the "other tissues" = (all 54 - listed comparator tissues).

5. **Output is one JSON per disease, written to a deterministic path** `<output_dir>/step6_selectivity_<disease_id>.json`. Old `step6_gtex_selectivity.csv` is no longer written.

6. **Module is callable from disease-net pipeline scripts.** All disease-net builders (mCRPC, AML, GBM future) must import and call `compute_selectivity(disease_id=...)`. No copy-paste.

7. **All metrics computed deterministically** — same input always produces same output. No random sampling.

---

## 7. Downstream consumers requiring update (locked list)

Every consumer of the old selectivity output must be updated. If we miss one, that consumer breaks silently. List below is exhaustive based on chat history audit.

| Consumer | What it consumes | Required change |
|---|---|---|
| `step1_complete_gene_drug_net.py` | reads `prostate_tpm` from old JSON | switch to `selectivity_per_gene[<gene>][primary_tissue_tpm]` |
| `mcrpc_unified_net.json` | has `selectivity` dict with `prostate_tpm` | regenerated with new module |
| `gbm_disease_net_action1.json` | has `selectivity` dict with `prostate_tpm: 0` (BUG) | regenerated with new module |
| `aml_disease_net.json` (if exists) | likely has same bug | regenerated with new module |
| `intercepta_pharma_deliverable_v1.py` (item 6: ADMET/selectivity) | extracts `prostate_tpm` for selectivity reporting | switch to `primary_tissue_tpm` |
| `INTERCEPTA_Round1_Pharma_Deliverable.json` (already shipped) | has hardcoded mCRPC `prostate_tpm` field | NOT regenerated — preserve as historical
 record per P16. New disease deliverables use new schema. |
| Any future Workstream B NSCLC ODE generalization | will need selectivity input | uses new module from start |

---

## 8. Migration plan (locked)

**Phase 1 — Config files** (~30 min):
- Create `~/INTERCEPTA/configs/` directory
- Write `disease_tissue_mapping.json` with the table from Section 3
- Write `genes_mcrpc.json` (extract from current step6_fix_gtex.py)
- Write `genes_aml.json` (extract from build_multimodal_features.py MUTATION_GENES)
- Write `genes_gbm.json` (extract from gbm_disease_net_action1.json existing genes)
- NOT writing `genes_nsclc.json` yet — defer to Workstream B

**Phase 2 — New module** (~60-90 min):
- Write `step6_selectivity_v2.py` per Section 5 API
- Unit-test on mCRPC (must produce equivalent output to old module)
- Unit-test on AML (must produce non-zero output for FLT3/NPM1/etc.)
- Unit-test on GBM (must produce non-zero output for EGFR/IDH1/etc.)

**Phase 3 — Downstream consumer updates** (~30-45 min):
- Update `step1_complete_gene_drug_net.py` schema reads
- Update `intercepta_pharma_deliverable_v1.py` schema reads
- Run regression on existing mCRPC pipeline — must produce equivalent end-to-end output

**Phase 4 — Disease net regeneration** (~30 min):
- Regenerate `aml_disease_net.json` with new selectivity values
- Regenerate `gbm_disease_net_action1.json` with new selectivity values
- Verify both have non-zero selectivity for at least 5 genes

**Phase 5 — Testing & commit** (~30 min):
- End-to-end smoke tests for each disease
- Commit + tag `selectivity-redesign-shipped`

**Total estimated effort:** 3-5 hours of focused work. Across 1-2 sessions.

---

## 9. What this redesign will NOT do

To prevent scope creep:

- **Will NOT add new disease support beyond mCRPC, AML, GBM.** NSCLC config waits for Workstream B kickoff.
- **Will NOT change the selectivity computation algorithm itself.** We're parameterizing what the existing algorithm operates on. The math (TPM ratios, thresholds, classification cutoffs) stays the same.
- **Will NOT compute novel safety metrics** (toxicity, off-target binding, etc.). Those are downstream of selectivity, not part of this redesign.
- **Will NOT touch the GTEx data download mechanism.** GTEx data already exists locally per Round 1 (`~/INTERCEPTA/data/gtex_median_tpm.gct.gz`).
- **Will NOT modify Round 1 pharma deliverable JSON.** Per P16, that historical artifact stands.
- **Will NOT touch step7-step9** (chembl, opentargets, metabolome) even though they may have similar issues. Each is a separate redesign if needed.

---

## 10. Falsifiable success criteria

Redesign is complete and successful when ALL of the following are true:

1. `step6_selectivity_v2.py` runs without errors for `disease_id ∈ {mcrpc, aml, gbm}`
2. Output JSON has no `prostate_tpm` field for AML or GBM (only `primary_tissue_tpm`)
3. AML output: ≥1 of [FLT3, NPM1, IDH1, IDH2, FLT3-ITD] has non-zero `primary_tissue_tpm`
4. GBM output: ≥1 of [EGFR, IDH1, PTEN, TP53] has non-zero `primary_tissue_tpm`
5. mCRPC output: top-20 selectivity-ranked genes overlap ≥8/20 with old module output (legitimate ranking, not regression)
6. `intercepta_pharma_deliverable_v1.py` produces valid ADMET/selectivity output for all three diseases
7. Round 1 mCRPC end-to-end pipeline produces equivalent output (regression test)

Until ALL 7 criteria hold, the redesign is not complete.

---

## 11. Process audit

| Principle | Applied as |
|---|---|
| P3 (research before code) | This spec written before code. GTEx tissue names verified against GTEx v8 documentation (54 tissues, 11 brain regions, no bone marrow). Disease-tissue mapping table grounded in real GTEx data. |
| P4 (fix structure, don't tune) | The redesign is structural (parameterization), not parameter tuning. No threshold adjustments to make output "look nicer." |
| P15 (only correct, honest, real science) | AML → Whole_Blood mapping limitation explicitly disclosed in tissue_proxy_caveat field. No silent zeros. No unstated assumptions. |
| P16 (preserve past work) | Old `step6_gtex_selectivity.py` and `step6_fix_gtex.py` NOT modified. Round 1 pharma deliverable JSON NOT regenerated. New module is `step6_selectivity_v2.py` — additive, not replacing. |

---

## 12. Entry conditions for implementation

Before any line of `step6_selectivity_v2.py` is written:

- [x] This spec committed and tagged `selectivity-redesign-spec`
- [x] GTEx data verified present at `~/INTERCEPTA/data/gtex_median_tpm.gct.gz`
- [ ] Configs directory created and populated (Phase 1)
- [ ] Phase 2 implementation begins after configs exist

---

## 13. Why this is honest

The pre-Round-2 state had a real bug that produced silently-wrong output for AML and GBM. The right response to that bug is not "patch the variable name" — it's "redesign the module to take disease as input, because that's what the bug is telling us about the architecture."

Round 2 closure identified this. The spec locks the redesign before code. The discipline that produced Round 2.2c (locked spec, fail-closed, real data, honest limits) is applied here too.

If implementation reveals a problem the spec didn't anticipate, the spec is not adjusted to fit the implementation — the implementation pauses, the spec is amended (or the work documented as a known limit), and we proceed.

This is the same discipline. Different artifact.

---

*Locked design. No code yet. Implementation begins after this is committed.*

— Prasad Akula & Claude (CSO)
2026-05-06
