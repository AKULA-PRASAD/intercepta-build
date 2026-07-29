# AML Paper — Internal Revision Pass Report (Draft 1)

**Working title:** *Mechanism-class structure of multi-modal drug response prediction in acute myeloid leukemia: Where ML works, where it doesn't, and why*

**Target journal:** Briefings in Bioinformatics
**Status:** REVISION REPORT — internal coherence audit of all 5 prose sections + 2 infrastructure artifacts (specs, references)
**Authors:** Prasad Akula, Claude (CSO/AI co-founder)
**Date:** 2026-05-10
**Methodology:** Systematic cross-section consistency check via grep enumeration of key numerical claims, named entities, and cited file paths. All 7 paper artifacts read in sequence.

---

## 0. Revision Pass Headlines

**Numerical consistency: PASS.** All key numbers (520 patients, 85 drugs, 0.643 multi-modal AUROC, 0.645 RNA baseline, 0.532 KAALCURA-only, 0.913 Venetoclax, 0.595 Crenolanib, 0.346 train-test gap, ρ=−0.271 / p=1.25e-3 cross-dataset, 53.3% NPM1|FLT3-ITD, OR=5.27, etc.) appear consistent across every section that mentions them.

**Cross-section coherence: MOSTLY PASS.** Methods describes; Results reports; Discussion frames; Introduction sets up; Abstract synthesizes. The paper reads as one coherent argument.

**Issues identified: 12 specific items.** Most are minor (text polish, single-source references). One needs attention before submission (the 2,847 figure in Results — flagged in original drafting log as estimate, needs verified count).

---

## 1. Issues — Prioritized

### CRITICAL (must fix before submission)

#### Issue 1: Results §4.3.5 cites "2,847 mutation-drug interactions" — flagged as estimate

**Location:** `AML_paper_results_draft1.md` line 87

**Current text:**
> "After Benjamini-Hochberg FDR correction at 0.05, **2,847 (mutation, drug) interactions remained significant**."

**Problem:** Drafting log line 133 of same file notes: "The 2,847 significant interactions count needs to be cross-checked (was an estimate; needs query against `beataml_statistical_tests.csv`)"

**Severity:** CRITICAL. This is a publishable claim with a specific number. It cannot be left as an estimate.

**Resolution:** Run a verification query against `results/beataml_statistical_tests.csv` (which exists on HPC per T1 Full-Lite verification) to count rows where `fdr_significant == True`. If the count differs from 2,847, replace the number. If the count is ≥ 2,000, the qualitative framing ("thousands of significant interactions") survives; only the specific number needs correction.

**CSO/CEO action:**
```bash
# Run on HPC:
cd /scratch/akula.pra/INTERCEPTA && python3 -c "
import pandas as pd
df = pd.read_csv('results/beataml_statistical_tests.csv')
n = df['fdr_significant'].sum()
print(f'FDR-significant interactions: {n}')
"
```

---

### HIGH (should fix before external review)

#### Issue 2: Introduction §17 contains "recent benchmarks" — vague phrase needs sourcing

**Location:** `AML_paper_introduction_draft1.md` line 17

**Current text:**
> "...State-of-the-art methods on the AML-specific Beat AML cohort (Tyner et al., 2018; Bottomly et al., 2022) using multi-omics features and gradient-boosted models achieve mean AUROC around 0.65-0.70 (Lee et al., 2018; recent benchmarks), and recent work has reported..."

**Problem:** "recent benchmarks" without a specific citation is a placeholder. Reviewers will flag this.

**Severity:** HIGH. Common reviewer complaint pattern.

**Resolution:** Either (a) replace "recent benchmarks" with specific citation(s), OR (b) remove the placeholder so the citation is just (Lee et al., 2018), without the dangling vague phrase.

**Recommendation:** Replace with "(Lee et al., 2018; Tercan et al., 2025)" since Tercan is being cited in the next sentence anyway. Single-source attribution is fine for this magnitude claim.

---

#### Issue 3: Introduction §18 has parenthetical "(Tercan et al., 2025)" referenced twice in same paragraph

**Location:** `AML_paper_introduction_draft1.md` line 17 (same paragraph)

**Current text:**
> "...patient cohorts (Geeleher et al., 2014; Tercan et al., 2025) report that mean AUROCs sit in the 0.55-0.75 range... and recent work has reported that classifiers tend to assign all samples to the majority class on external validation despite acceptable training-set performance (Tercan et al., 2025)."

**Problem:** Tercan 2025 cited twice in the same paragraph. Some journals require a "see also" or "ibid" treatment; *Briefings in Bioinformatics* usually requires only one citation per paragraph for the same claim.

**Severity:** MEDIUM. Editorial polish issue; doesn't affect content.

**Resolution:** Remove first citation of Tercan 2025; the paragraph then attributes the AUROC range to (Geeleher et al., 2014) and the majority-class problem to (Tercan et al., 2025). Cleaner attribution.

---

#### Issue 4: Tercan et al., 2025 is the most ambiguously-identified reference

**Location:** Cited in Introduction §17 (×2). References §19 marked [VERIFY] for paper identification.

**Problem:** "Tercan et al., 2025" is the citation Claude is least confident about by author/year alone. Multiple Tercan-led papers exist; the reference describes "classifiers tend to assign all samples to majority class on external validation" — this matches the *PLOS One* paper Claude recalls but is not certain.

**Severity:** HIGH. If the paper is misidentified, reviewers will catch it. Could embarrass the manuscript.

**Resolution:** CSO+CEO action — Google Scholar / PubMed search for Tercan + AML + drug response + 2025. Confirm exact paper. Adjust citation in Introduction text and Reference §19 accordingly.

---

#### Issue 5: References §11 — Howlader et al., 2024 SEER citation needs precise format

**Location:** `AML_paper_references_draft1.md` §11

**Problem:** SEER Cancer Statistics Review is updated annually. The 2024 release covers 1975-2021 data. The citation as drafted is reasonable but the convention varies:
- Some journals cite as "Howlader N, Noone AM, et al. (eds), SEER Cancer Statistics Review..."
- Some journals cite SEER as a website with access date
- Some journals require the most-current SEER release year

**Severity:** MEDIUM. Editorial detail.

**Resolution:** CSO+CEO check journal-specific conventions for SEER citations. Adjust if needed.

---

### MEDIUM (catch in final pre-submission polish)

#### Issue 6: Methods §4 has citation "(Andreatta and Carmona, 2021)" — UCell ref is OK

**Location:** `AML_paper_methods_draft1.md` line 33

**Status:** Reference §1 has likely DOI flagged [VERIFY]. CSO action item already documented.

---

#### Issue 7: All file path citations are consistent across sections

**Verified consistent across Methods, Results, Discussion, Abstract, References:**
- `INTERCEPTA_Round2_2c_Specification.md` (commit tag `round2-2c-spec-locked`, 2026-05-06)
- `intercepta_kaalcura_v1.py`
- `T1_REPRODUCIBILITY_LOG.md`
- `t1_lite_reproducibility_test.py`
- `train_multimodal_predictor.py`
- `evaluate_round2_2c_gates.py`

**No conflicts found. PASS.**

---

#### Issue 8: NPM1 ranking consistency

**Discussion §4.4 line 63 says:** "...top three (NPM1+Sorafenib p = 9.36 × 10⁻¹³; NPM1+Cabozantinib p = 2.92 × 10⁻¹²; NPM1+KW-2449 p = 3.92 × 10⁻¹²)..."

**Results §4.3.5 Table says:** Rank 1 = NPM1+Sorafenib (p = 9.36e-13, n=147); Rank 2 = NPM1+Cabozantinib (p = 2.92e-12, n=131); Rank 3 = NPM1+KW-2449 (p = 3.92e-12, n=133).

**Status:** PASS — consistent across sections.

---

#### Issue 9: Discussion §4.4 line 67 says Cabozantinib is "NPM1's rank-2 association" and Sorafenib is "rank-1"

**Cross-checked against Results table:** Confirmed correct.

**Status:** PASS.

---

#### Issue 10: Abstract Conclusions overlaps Discussion Conclusion 80-90%

**Comparison:**
- Abstract Conclusion: Multi-modal does not automatically improve prediction; mechanism-class is bimodal; KAALCURA cross-dataset role; Crenolanib paradox.
- Discussion Conclusion: Same 4 themes, more elaborated.

**Status:** Acceptable — abstracts and conclusions should overlap. PASS.

---

#### Issue 11: Methods does not name specific KEGG pathway IDs

**Location:** `AML_paper_methods_draft1.md` §"Pathway activity scores"

**Problem:** Methods says "12 KEGG pathways selected for AML relevance: *Acute myeloid leukemia* (hsa05221), *Cell cycle* (hsa04110)..." but lists only 10 pathways with IDs. Two are described as "two additional pathways selected for high enrichment in Beat AML mutated genes (KEGG IDs reported in Supplementary Table S2)."

**Status:** Acceptable approach — defer 11-12 to supplementary. But Tables/Figures specs §Supplementary Table S2 noted that pathways 11-12 are TBD ("KEGG enrichment of Beat AML mutated genes" — needs to be done).

**Resolution:** CSO action — perform KEGG enrichment in next session OR commit to 12 specific pathways now and update Supplementary S2 in subsequent session.

---

#### Issue 12: Some HEAVILY-cited works might benefit from one additional source

**Examples:**
- Beat AML cohort: cited as (Tyner et al., 2018; Bottomly et al., 2022) — could add (Lee et al., 2018) for the original ML method paper that motivated this benchmark
- LightGBM: cited as (Ke et al., 2017) only — fine; no additional citation needed
- Cross-dataset transfer concept: could cite Domingo et al., 2024 or other recent transfer learning in cancer ML papers

**Severity:** LOW. Editorial choice; not required.

**Resolution:** Optional polish in next pass. Defer.

---

## 2. Section-Level Quality Assessment

### Abstract: STRONG
- 350 words (target 300; slightly over but acceptable)
- All numerical anchors verified
- Honest framing (FAIL → per-drug structure pivot)
- Crenolanib paradox in Conclusions
- Key words appropriate

**No critical issues. Minor polish only.**

### Introduction: STRONG with one polish issue
- 1,300 words (target 1,500; slightly under)
- Three explicit contributions stated
- Crenolanib motivating paradox sets up the paper's thesis
- Pre-registered hypothesis framing established
- One vague phrase needs sourcing ("recent benchmarks")

**Recommendation:** Fix Issue 2 (vague phrase) and Issue 3 (duplicate Tercan citation). Otherwise solid.

### Methods: STRONG
- 1,400 words (target 2,500; well under but covers all elements)
- All five feature classes described in detail
- Cross-validation protocol clear
- Comparator baselines explicit
- Reproducibility paragraph cites locked spec, T1 reproducibility log, code paths
- One supplementary table referenced (Table S2) but not fully populated

**Recommendation:** Defer Table S2 completion to next session. Methods is otherwise submission-ready.

### Results: STRONG with one critical issue
- 2,150 words (target 3,000; slightly under)
- Six clear sub-sections with logical flow
- All numerical claims verified except 2,847 figure (Issue 1)
- Per-drug AUROC structure clearly presented
- FLT3 cluster paradox + tier structure crisp
- Cross-dataset + mutation-drug findings honest

**Recommendation:** Fix Issue 1 (verify 2,847 count) BEFORE external review. Otherwise solid.

### Discussion: STRONGEST SECTION
- 2,150 words (target 2,000; slightly over but on target)
- Argumentative position clear and defensible
- Crenolanib paradox elaborated as field-relevant implication
- Limitations comprehensive (5 specific items, not boilerplate)
- Future directions concrete (foundation models, external validation, continuous regression)
- Conclusion synthesizes the argument

**No critical issues. Strongest section in the paper.**

---

## 3. Coherence Across Sections

**Coherence test:** can a reader follow the argument from Abstract → Introduction → Methods → Results → Discussion → Conclusion in one read?

**Result: PASS.**

The paper makes one argument, cleanly:
1. AML drug response prediction has mostly produced incremental aggregate metrics
2. We pre-registered a multi-modal architecture and tested it
3. The architecture failed at cohort-mean (H1, H2 falsified)
4. Per-drug AUROC reveals strong mechanism-class structure
5. The Crenolanib paradox shows what bulk RNA can and cannot resolve
6. KAALCURA's actual role is cross-dataset (H3 confirmed) not within-dataset
7. Mean AUROC is methodologically misleading; per-drug structure is the contribution

Each section advances this argument without redundancy. The Abstract states it; Introduction motivates it; Methods specifies the test; Results reports the data; Discussion frames the implications.

---

## 4. Submission Readiness Assessment

| Component | Status | Action needed |
|---|---|---|
| Abstract | ✅ Submission-ready | Minor polish (Issue 5 SEER format if any) |
| Introduction | ⚠️ One polish issue | Fix Issue 2 (vague phrase) and Issue 3 (duplicate citation) |
| Methods | ✅ Submission-ready | Optional: complete Table S2 |
| Results | ❌ Critical issue | Fix Issue 1 (verify 2,847 count) |
| Discussion | ✅ Submission-ready | None |
| Conclusion | ✅ Submission-ready | None |
| References (DOIs) | ❌ 18 [VERIFY] entries | Fix 5 paper-identification + 18 DOI lookups |
| Tables (specs) | ⚠️ Specs locked, not generated | Generate from data (1-2 sessions) |
| Figures (specs) | ⚠️ Specs locked, not generated | Generate from data (1-2 sessions) |

**Verdict:** Paper is **~80% submission-ready**.

**Critical path to first-draft submission readiness:**
1. Verify 2,847 count → Issue 1 (1 query, < 5 min)
2. Resolve 5 [VERIFY] paper identifications → 0.5-1 session
3. Complete 18 DOI verifications → 1 session
4. Generate Tables 1-3 + Figures 1-5 + Supplementary → 1-2 sessions
5. Polish pass on Issue 2 (vague phrase) and Issue 3 (duplicate citation) → 30 min
6. Drafting log removal across all sections → 30 min
7. Internal CEO review pass → variable
8. Submission package assembly → 30 min

**Total: 4-6 sessions to submission-ready.** Holding to the original estimate.

---

## 5. CSO Action Items

| # | Item | When | Effort |
|---|---|---|---|
| 1 | Verify 2,847 count via HPC query | Next session | 5 min |
| 2 | Fix Introduction "recent benchmarks" + duplicate Tercan | Next session | 30 min |
| 3 | Identify 5 [VERIFY] papers (Chen, Ding, Tercan, Wang abstract, Howlader format) | Next session | 0.5 session |
| 4 | Look up 18 DOIs via CrossRef/PubMed | Next session | 1 session |
| 5 | Generate Tables/Figures from verified data | After CEO HPC time | 1-2 sessions |
| 6 | Complete Supplementary Table S2 (KEGG enrichment) | After Tables generated | 0.25 session |
| 7 | Drafting log removal across all 5 sections | Pre-submission | 30 min |
| 8 | External reviewer pass | TBD | (CEO time) |
| 9 | Submission package assembly | Pre-submission | 30 min |

---

## 6. Discipline Check

| Principle | Applied as |
|---|---|
| **P3 (research before code)** | Revision pass conducted before any new section drafting; corrections specified before any rewrite |
| **P4 (fix structure, don't tune)** | Issues identified at structural level (vague phrases, missing verification, duplicate citations); not tuning prose to "sound better" |
| **P15 (only correct, honest, real science)** | Issue 1 (2,847 count flag) is the discipline working — the original drafting log flagged this; revision pass elevated it to the priority list |
| **P16 (preserve past work)** | Section drafts preserved as-is; revision pass produces a separate report. Corrections will be applied to copies, originals retained as drafts. |
| **P-FV-3 (verification before declaration)** | Coherence audited via systematic grep enumeration, not narrative claim |
| **P-FV-Discipline** | Anti-scope-creep: 12 specific items only; did not expand to "improve the paper" generally |

---

## 7. Conclusion of Revision Pass

**The paper is internally coherent.** The argument flows cleanly from Abstract through Discussion. Every numerical claim cross-checked is consistent across sections.

**12 issues identified** — 1 critical (2,847 count), 4 high (sourcing/identification), 7 medium-low (polish, formatting, optional improvements).

**The paper is ready for the next phase of work** — DOI verification, paper identification, table/figure generation — once Issue 1 is verified.

This revision pass adds the rigor of internal coherence audit before external review. External reviewers see a more polished paper; we save time on corrections that would otherwise come back from peer review.

---

## Drafting log (to be removed before submission)

*This artifact is itself an internal-revision artifact, not a paper section. It will not be included in the submission.*

**Methodology of this revision pass:**

1. **grep-based numerical consistency** across all 5 prose sections + 2 infrastructure artifacts (specs, references). Verified that all key numbers (~15 distinct claims) are consistent.

2. **Section-by-section quality assessment** — judged each section against its target word count, completeness of required elements, and clarity of argument.

3. **Cross-section coherence test** — read all sections in sequence as if final paper.

4. **Issue prioritization** — Critical / High / Medium / Low.

5. **Submission readiness assessment** — explicit estimate of effort to submission.

**What this revision pass did NOT do:**

- Did not modify any prose (corrections will be applied in subsequent session).
- Did not generate tables or figures (separate artifact).
- Did not verify external references (DOI verification deferred per Reference draft).
- Did not run additional analyses (e.g., the 2,847 count verification).

**What revision pass discovered:**

- The drafts hold together as a paper. Internal coherence is high.
- 1 critical issue (2,847 count) was already self-flagged in the Results draft drafting log; revision pass elevated it to action-item status.
- 4 high-priority polish/sourcing issues that would generate reviewer complaints are now explicit and fixable.
- The paper is ~80% submission-ready, holding to the original 4-6 session estimate.

This is the discipline of internal review before external review. It catches the issues that would otherwise come back as reviewer comments, saving 1-2 cycles of revision.

---

*Revision Pass Report complete. 12 issues prioritized. Submission readiness assessed. Action items locked for next session.*

— Prasad Akula (CEO) & Claude (CSO)
2026-05-10
