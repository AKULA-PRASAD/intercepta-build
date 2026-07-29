# INTERCEPTA Phase 1 Errata Log — 2026-05-10

**Status:** Phase 1 of audit remediation complete
**Scope:** Errors verified in CSO Self-Audit (`/mnt/user-data/outputs/INTERCEPTA_CSO_Self_Audit_2026-05-10.md`)
**Method:** Primary-source verification via web_search before each correction; new files replace old; old files deleted from both sandbox and outputs

---

## Errors Corrected (5 of 7 audit findings)

### Error #1 — Q5 conformal prediction note (SEVERE: fabricated authorship) — CORRECTED

**Old file (deleted):** `q5_ood_detection/conformal_prediction_scrna.md`
- Attributed paper to fabricated "Khoshchehreh et al., 2025"
- No DOI, no PMID
- Speculative content

**New file:** `q5_ood_detection/lopez_de_castro_2025_conformal_prediction.md`
- Authors verified: López-De-Castro M, García-Galindo A, González-Gomariz J, Armañanzas R
- DOI 10.1093/bioinformatics/btaf521 (Oxford Bioinformatics 41(10), Oct 2025)
- PMID 40973204, PMC PMC12506889
- Senior author: Rubén Armañanzas (Univ Navarra DATAI)
- License: CC BY 4.0
- Code: github.com/digital-medicine-research-group-UNAV/conformalized_single_cell_annotator
- Method details: 10 batched experiments × 3 annotation taxonomies × 3 non-conformity measures (now verified, not speculated)

**Drift Instance #25:** RESOLVED.

---

### Error #2 — Q6 PDXGEM note (SEVERE: placeholder dressed as anchor) — CORRECTED

**Old file (deleted):** `q6_validation/pdxgem_clinical_validation.md`
- Attributed paper to fabricated "Lee et al. 2020+"
- Speculative content throughout
- No DOI, no specific results

**New file:** `q6_validation/kim_2020_pdxgem.md`
- Authors verified: Kim Y, Kim D, Cao B, Carvajal R, Kim M
- DOI 10.1186/s12859-020-03633-z (BMC Bioinformatics 21:288, July 2020)
- PMID 32631229, PMC PMC7336455
- bioRxiv preprint: 10.1101/686667 (June 2019)
- First author Youngchul Kim (Moffitt Cancer Center Biostatistics & Bioinformatics)
- Web app: pdxgem.moffitt.org
- 4-step pipeline now described accurately
- 6 drug-cancer pairs verified: paclitaxel + trastuzumab (breast), 5FU + cetuximab (CRC), gemcitabine (pancreatic), erlotinib (NSCLC)
- Specific quantitative result verified: 600 initial probesets → 147 CCE biomarkers (24.5%) → 145 with positive variable importance
- PDX-patient gap honestly quantified

**Drift Instance #26:** RESOLVED.

---

### Error #3 — Q6 DiSyn note (MODERATE: unattributed) — CORRECTED

**Old file (deleted):** `q6_validation/disyn_2025_patient_transfer.md`
- No first author
- No DOI
- No journal
- Specific percentages cited without source attribution

**New file:** `q6_validation/li_shen_2024_disyn.md`
- Authors verified: Li K*, Shen B*, Feng F, Li X, Wang Y, Feng N, Tang Z, Ma L, Li H (* equal first)
- Journal: *Journal of Pharmaceutical Analysis* (ScienceDirect S2095177924002259)
- PMC PMC12268049, PMID 40678484
- Senior author: Hong Li (Shanghai Institute of Nutrition and Health; LiHongCSBLab)
- License: CC BY-NC-ND 4.0 (non-commercial — affects INTERCEPTA commercial use planning)
- Code: github.com/LiHongCSBLab/DiSyn
- 4-step DiSyn pipeline now described accurately (DSN + data synthesis + iterative training + unsupervised pretraining)
- Validation: TCGA + I-SPY2 + NIBR PDXE (3 patient/PDX datasets, verified)
- Note: previously-cited specific percentages (5.44%/12.17%/10.73%) flagged as "from preprint version, not verified against PMC abstract"

**Drift Instance #27:** RESOLVED.

---

### Error #4 — Partin/IMPROVE status (MINOR: outdated) — CORRECTED

**Old file (deleted):** `q6_validation/partin_2025_improve_benchmark.md`
- Cited as "arxiv preprint as of 2026 cutoff"

**New file:** `q6_validation/partin_2026_improve_benchmark.md`
- Updated to reflect peer-reviewed status: *Briefings in Bioinformatics* DOI 10.1093/bib/bbaf667, January 12, 2026
- First author verified: Alexander Partin
- Senior author verified: Rick L. Stevens
- Full 20-author roster preserved in citation
- arXiv ID 2503.14356 retained as preprint reference
- 5 datasets + 6 standardized models verified from arXiv abstract
- Two-metric framework (absolute + relative performance) preserved

**Drift Instance #4:** RESOLVED.

---

### Error #5 — Q10 EVA licensing (MINOR: incorrect) — CORRECTED

**File:** `q10_open_source/open_source_landscape.md` (in-place edit)

**Old entry:**
```
| EVA (Q8) | Scienta — likely proprietary | Industry | **Closed** |
```

**New entry:**
```
| EVA (Q8) | huggingface.co/Scienta-Lab + GitHub Scienta-Lab | **Partially open** (60M-parameter open weights on HF) + commercial deployment via Scienta partnerships | Production-ready (open variant) |
```

**Source:** Scienta Lab launch announcement Feb 12, 2026 + huggingface.co Scienta-Lab organization. Open 60M variant confirmed. Updated text in §1 and §2 of the landscape file accordingly.

**Implication for Decision 8 (universality):** EVA disease-specific FM coverage is now available open-source for I&I; INTERCEPTA can use EVA in its multi-FM portfolio without proprietary barriers (at least for the 60M variant).

**Drift Instance #5:** RESOLVED.

---

### Error #6 — Q5 inflated composite (METHODOLOGICAL) — CORRECTED

**Old file (deleted):** `q5_ood_detection/deep_ensembles_mc_dropout.md`
- Combined Lakshminarayanan 2017 (NeurIPS) + Gal & Ghahramani 2016 (ICML) into one "anchor 3" to inflate Q5 anchor count

**New files:**
1. `q5_ood_detection/lakshminarayanan_2017_deep_ensembles.md` — proper standalone anchor for Deep Ensembles (NeurIPS 2017, arXiv 1612.01474)
2. `q5_ood_detection/gal_2016_mc_dropout.md` — proper standalone anchor for MC Dropout (ICML 2016, arXiv 1506.02142)

**Q5 anchor count:** Now honestly 6 (Theunissen 2025 + López-De-Castro 2025 + Lakshminarayanan 2017 + Gal 2016 + Engelmann 2022 + Liu 2020 energy-based). Meets locked entry condition floor of 5.

**Drift Instance #28:** RESOLVED.

---

## Errors NOT Addressed in Phase 1 (deferred to subsequent phases)

### Error #7 (METHODOLOGICAL) — Q9 and Q10 lack real paper anchors

**Status:** UNRESOLVED. Awaits Phase 7 (reclassification of Q9/Q10 as Operational Decisions rather than Layer 1 literature-grounded Decisions).

**Detail:** All "anchors" in Q9 and Q10 are composite CSO synthesis rather than primary-source paper reads. The honest path is to reclassify Decisions 9 and 10 as "Operational/Strategic Decisions" — a separate category from literature-grounded Decision Records 1-8. This is a Charter clarification (not amendment) and is the next CSO action item after Phase 1.

### Q7 + Q8 first-author attributions

**Status:** PARTIALLY RESOLVED via the audit but not yet rewritten in files. The audit identified missing first authors in Q7 Benchmarking interpretability note, Q8 TEDDY note, Q8 PaSCient note. These notes still need first-author attribution added. Deferred to Phase 5 (Q7 re-do) and Phase 6 (Q8 re-do).

### Q4-Q8 thin synthesis quality

**Status:** UNRESOLVED. The audit flagged Q4 synthesis (455w) through Q10 synthesis (227w) as below Charter §5.2 standard. These will be rewritten properly during Phase 2-6 (Q4 through Q8 re-do passes).

---

## Updated Layer 1 State

After Phase 1:

| Q | Anchor count | Notes |
|---|---|---|
| Q1 | 8 | Unchanged — strong from original |
| Q2 | 6 | Unchanged — strong from original |
| Q3 | 7 | Unchanged — adequate from original |
| Q4 | 6 | Tight notes; needs Phase 2 deepening |
| Q5 | **6 (corrected)** | Composite split; conformal note rewritten; now honestly 6 anchors |
| Q6 | **4 (corrected)** | 3 of 4 notes rewritten with verified authorship; meets entry-condition floor |
| Q7 | 4 | Awaits Phase 5 deepening + first-author attributions |
| Q8 | 5 | Awaits Phase 6 deepening (highest priority — universality is the vision) |
| Q9 | 0 paper anchors (3 composite synthesis docs) | Awaits Phase 7 reclassification |
| Q10 | 0 paper anchors (2 composite synthesis docs) + EVA correction | Awaits Phase 7 reclassification |

**Total verified primary-source anchor reads (Phase 1 complete):** ~36 papers across Q1-Q6. Q7-Q8 contain 9 thin notes pending deepening. Q9-Q10 contain 0 paper anchors pending reclassification.

---

## Drift Catalog Update

Cumulative drift before Phase 1: **30 instances**
- #25 fabricated Khoshchehreh attribution → RESOLVED Phase 1
- #26 PDXGEM placeholder dressed as anchor → RESOLVED Phase 1
- #27 DiSyn unattributed → RESOLVED Phase 1
- #28 Q5 composite inflation → RESOLVED Phase 1
- #29 Q9/Q10 closed without real anchors → DEFERRED Phase 7
- #30 meta-drift (claiming "no new drift" while drift occurred) → ACKNOWLEDGED; audit mechanism now operational

**New drift this Phase 1 cycle:** 0. All corrections verified primary-source before writing.

**Cumulative drift unchanged at 30 instances; 4 of the 6 audit-identified instances now RESOLVED.**

---

## Phase 1 Discipline Check

- **P3 (research before code):** ✅ All corrections were research output, not code
- **P15 (only correct/honest/real science):** ✅ Every correction primary-source-verified before writing; audit's verified errors corrected
- **P16 (preserve past work):** ✅ Errata notes in each corrected file preserve the audit trail; deleted files removed only after replacements verified
- **P-FV-1 through P-FV-3:** ✅ Maintained throughout

---

## Next CSO Action Item

**Phase 2: Re-do Q4 (Drug Response Prediction Architecture).** Charter-grounded re-reading of the 6 Q4 papers already named (DeepCDR, PaccMann, sci-Plex, CPA, GEARS, scGen) — but with the Q1-Q3 word-count standard (~2000+ words per note), proper first-author attribution, methodological depth, and a substantive Q4 synthesis (~2000+ words) and revised Decision 4 record. Estimate: 1-2 sessions of focused work.

OR if CEO prefers different phase priority:
- **Phase 3 (Q5):** Re-do Q5 synthesis and Decision 5 with corrected anchor set (already 6 anchors strong)
- **Phase 4 (Q6):** Re-do Q6 synthesis and Decision 6 with corrected anchor set (4 anchors, all now verified)
- **Phase 6 (Q8):** Re-do Q8 — highest strategic priority because universality IS the vision

CSO recommendation: **Phase 3 + Phase 4 first** (Q5 and Q6 syntheses, since their anchors are now corrected and verified; the synthesis + Decision rewrites are the natural next step after Phase 1). Then Phase 6 (Q8). Then Phase 2 (Q4). Then Phase 5 (Q7). Then Phase 7 (Q9/Q10 reclassification).

Awaiting CEO direction.

— Claude (CSO), 2026-05-10
