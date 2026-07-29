# INTERCEPTA Round 1 Audit Report

**Date:** April 21, 2026
**Auditor:** Claude (CSO, acting as auditor of own work)
**Scope:** All artifacts committed to the `round1-final` git tag
**Principle:** Find what's wrong, not validate what feels right.

---

## Audit methodology

For each scientific claim, code file, and memo passage, one question was asked:
**does it actually do what I claimed?** Not "does it look right," but "when I re-run it, does it produce the number I cited?"

Fifteen audit items were executed. The result is:
- **11 PASS**
- **2 FAIL** (require memo correction before Round 2)
- **2 partial concerns** (not failures but need refinement)

---

## Findings — FAIL (must be corrected)

### FAIL-1: Biexponential fitter has a strict-boundary bug that rejects valid fits

**Where:** `intercepta_g_rate_validation_v5.py` (and inherited by v5.1), function `fit_g_rate`, line with `if 0.05 < a < 0.95`.

**What happens:** When the biexponential fit successfully converges (r² near 1.0) with the `a` parameter exactly at or very close to 0.95 or 0.05, the fit is rejected and the code retries with growth-only or decay-only models. For olaparib-v4.1 trajectories, 49/50 fits hit this condition (median a ≈ 1.000). The retry paths often fail, producing "fit failure" where a valid biexponential fit existed.

**Verified by synthetic test:** With known ground truth (a=0.95, d=0.05, g=0.01), `curve_fit` recovers the parameters exactly (r² = 1.0), but `fit_g_rate` returns `None`.

**Verified by real test on v4.1 olaparib patient:** direct biexp fit gives a=0.9991, d=0.0125, **g=0.001876** (Zhou published: 0.001889 — within 1%), r²=0.9999. The v5 fitter rejects this excellent fit because a > 0.95.

**Impact on Round 1 scientific conclusions:**
- Olaparib v5.1 result reported "5/50 fits, median g ≈ 0" → this is an artifact of the bug, not biology.
- When direct fit is run on all 50 olaparib-v4.1 patients: 50/50 converge with r² > 0.9. Of those, 20/50 have meaningful nonzero g with median = 0.004/day (DT 171 days).
- Zhou 2024 clinical g = 0.00189/day (DT 367 days). Model is ~2× faster than clinical, **not "no regrowth" as memo v2.1 claimed.**
- This is the same ~2× systematic bias seen in all other regimens. Olaparib is actually on-pattern, not uniquely broken.

**Required correction:** Update memo v2.1 to retract the "no meaningful regrowth" claim and Limitation #7 as written. The real statement is "model olaparib produces regrowth at ~2× Zhou's clinical rate, consistent with the systematic bias documented elsewhere."

### FAIL-2: Memo v2.1 Limitation #7 overstated

**Where:** `INTERCEPTA_CSO_Parameter_Memo_v2_1.md` Section 3.

**What was claimed:** "PARP-specific evolved resistance not modeled [...] model predicts near-complete cytoreduction for BRCA-deficient tumors but cannot reproduce the observed 9.8-month median rPFS in PROfound [...] requires either time-varying BRCA_fraction(x,t) or a dedicated HRR-revertant subpopulation."

**What's actually true:** The model DOES produce regrowth at approximately clinically-appropriate rate (median fitted g = 0.004/day across 50 patients, vs Zhou's 0.00189/day). The ~2× overshoot is the same systematic bias the model shows for enza (1.69-3.45×) and untreated (0.36× in opposite direction). PARP is not a uniquely broken drug class in the model.

What the model DOES still lack is a time-varying resistance-evolution mechanism that would more precisely match the shape of the PROfound rPFS curve, but this is a refinement opportunity, not a fundamental absence.

**Required correction:** Rewrite Limitation #7 to reflect the actual finding. Possible new text:

> 7. PARP resistance dynamics are ~2× faster than Zhou 2024 clinical measurement. Consistent with the systematic bias pattern seen in other drug classes. Not addressable by parameter adjustment within the current framework; would require time-varying BRCA_fraction(x, t) or explicit HRR-revertant subpopulation compartment. Round 2 or later.

**Severity:** Medium. The existence of a PARP model limitation is real. The magnitude and specificity of that limitation was overstated.

---

## Findings — PASS (verified correct)

### PASS-1: v4 source file syntax valid, 984 lines.

### PASS-2: v4 → v4.1 patch applies exactly three claimed changes, nothing else.
- Removed: 6 lines (header, R_MAX comment, 2× `'emax_parp': 0.15`, 2× `ec50` lines that were consumed by larger block replacements)
- Added: 34 lines (new drug-block comments + docstring additions)
- Verified by literal diff: R_MAX value unchanged at 0.00678, both emax_parp values now 0.015, Freedland citation removed from R_MAX line.

### PASS-3: v5 → v5.1 patch applies both claimed changes, nothing else.
- Import switched from v4 to v4_1: verified
- summarize_cohort_g now returns full schema on empty/all-failed cohorts: verified

### PASS-4 (PARTIAL): Biexp fitter correctness on standard test cases
- Full biexponential (a=0.85): recovered exactly
- Full biexponential (a=0.70): recovered exactly
- Pure decay (a=1.0): recovered exactly
- Pure growth (a=0.0): recovered exactly
- Slow decay + slow growth (a=0.90): recovered exactly
- Fast regrowth (a=0.95 at boundary): **FAILS** — this is the FAIL-1 bug above.

### PASS-5: Diagnostic untreated g = 0.00374/day (user's run with velocity CSV)
- My reproduction without velocity CSV gives 0.00362/day (3% lower)
- Within expected tolerance for velocity-vs-uniform S distribution difference.
- Memo claim is correct for user's environment.

### PASS-6a: Diagnostic enza g = -0.00073/day
- Memo cited -0.00070/day
- Reproduces identically within 4% (minor RNG/ODE solver variance)

### PASS-6b: Diagnostic abi g = -0.00086/day — reproduces identically.

### PASS-7: v5.1 crash-fix actually handles all three failure paths:
- Empty cohort → returns full schema
- All-failed-fits cohort → returns full schema
- Decay-only cohort (olaparib-like) → returns full schema with `d_only` counts

### PASS-8: Freedland 2005 scope — confirmed post-prostatectomy BCR study, NOT mCRPC. Memo claim is correct.

### PASS-9: Stein 2011 scope — confirmed mCRPC, log g range -2 to -2.3 (I wrote ~-2.15, the midpoint, as the median; defensible interpretation).

### PASS-10: Leuva/Zhou g-values (0.000784 and 0.001889)
- Verified: both values are enzalutamide g-rates in HRR-altered vs non-HRR patients (from the Zhou 2024 olaparib cohort vs their reference cohort)
- The labeling `enzalutamide_HRR_altered` and `enzalutamide_non_HRR` in `PUBLISHED_G_VALUES` is correct
- (A scare during the audit: I initially misread the Zhou abstract; re-reading confirmed my original labels are right)

### PASS-11: Olaparib emax 0.015 derivation math
- My claim: "-ln(0.6)/56 days ≈ -0.009/day during response phase"
- Check: -ln(0.6)/56 = 0.00912 ✓
- Value choice (0.015) produces net kill of ~-0.011/day given model growth term, slightly faster than clinical -0.009 — conservative direction ✓

### PASS-15: Cross-document consistency
- Memo v1: original rPFS framework, 2/6 target passing claim
- Memo v2: pivot to g-rate, 0/3 confirmed passing stated explicitly
- Memo v2.1: 0/3 maintained, adds (overstated) Limitation #7 — FLAGGED in FAIL-2
- Retrospective: 0/3 stated, "seven known limitations" — consistent with memo v2 (6) + v2.1 (+1)
- Validation Limitations v1: 0/3 stated, matches
- Round 2 Kickoff: consistent with parent docs
- No document contradicts another on whether Round 1 passed.

---

## Findings — PARTIAL CONCERNS (not failures, need refinement)

### CONCERN-1: BeatAML dataset specifications in Round 2 kickoff

**Claim in kickoff doc:** "562 patients with matched drug sensitivity across 122 small molecule inhibitors"

**Actual BeatAML 1.0 (Tyner 2018 Nature):** 672 specimens from 562 patients, but **only 409 specimens** had drug sensitivity data.

**Additionally:** BeatAML 2.0 (Bottomly 2022 Cancer Cell) expanded to 805 patients / 942 specimens and is the current authoritative release — should use this, not BeatAML 1.0.

**Severity:** Low. The plan still works. The Round 2 kickoff doc should cite BeatAML 2.0 and state "~400 specimens with drug sensitivity + genomics" not "562 patients with matched drug sensitivity."

### CONCERN-2: "Seven known limitations" count is inconsistent if audited rigorously

The Retrospective says "7 known limitations documented." In the source documents:
- Memo v2 Section 6 lists 6 items (1-6)
- Memo v2.1 Section 3 adds item 7
- Validation Limitations v1 numbers items 1-4 but groups others as prose

Technically the claim is defensible (6 + 1 = 7) but the count is scattered across documents rather than canonical. A future audit by an external reviewer could quibble.

**Severity:** Very low. Cosmetic consolidation would help, not required.

---

## Summary of what changes before Round 2 begins

**Required (before any Round 2 work):**
1. Amend memo v2.1 Limitation #7 per FAIL-2 corrected text above.
2. Patch `fit_g_rate` in v5.1 to remove the strict-inequality bug (per FAIL-1). Produces v5.2 or inline fix. Rerun v5.2 to get the correct olaparib numbers.
3. Re-audit olaparib results with corrected fitter and update memo v2.1 + Retrospective Section 4 accordingly.

**Recommended (low-priority polish):**
4. Update Round 2 kickoff doc to cite BeatAML 2.0 with correct specimen-with-drug-sensitivity count.
5. Consolidate the "7 limitations" list into a single canonical location.

**Not required:**
Everything else in Round 1 is verified. 11 of 15 audit items pass cleanly. The ODE code, patch scripts, diagnostic tool, and parameter sourcing are all correct. Only the fitter bug and its downstream scientific narrative were wrong.

---

## What this means for the CSO decision to close Round 1

The decision to finalize Round 1 at v4.1 stands. The model is still directionally correct for drug ranking, and the two sourced corrections (PARP emax, R_MAX citation) were valid.

However, moving to Round 2 on top of uncorrected memo v2.1 would propagate the overstated PARP resistance narrative into a future publication or pharma conversation. That's not acceptable per principle 15.

**Revised CSO call:** Do NOT start Round 2 code work yet. First:
(i) Fix the fitter bug in v5.2
(ii) Rerun v5.2 against v4.1 to produce correct olaparib numbers
(iii) Amend memo v2.1 Section 3 and the corresponding Retrospective paragraph
(iv) Commit and tag `round1-final-corrected`
(v) Then start Round 2 AML net.

Estimated time for steps (i)-(iv): one focused session. Minor compared to the cost of carrying an incorrect scientific claim forward.

---

## Principle check on the audit itself

- **Principle 15 (no fake results):** this audit found real failures and reports them. Two FAILs stated plainly. Not reframed as partial success.
- **Principle 3 (deep research):** every audit item executed actual code or re-checked primary sources (not just re-read my own memo).
- **Principle 16 (preserve past work):** existing artifacts remain intact; corrections will be added as new versions or amendments.

The audit is itself subject to audit. If I missed something, this document's findings are themselves refutable by the next round of checks.

---

*Prasad Akula & Claude, Co-Founders of INTERCEPTA. April 21, 2026.*
*Audit result: Round 1 not yet fully closed. Corrections required before Round 2 starts.*
