---
title: "INTERCEPTA Master Audit Protocol v1.0"
subtitle: "Foundation-First, FDA-Grade Scientific Audit"
authors:
  - "Prasad Akula (CEO, Audit Authority)"
  - "Claude (CSO, Audit Director)"
date: "2026-05-10"
status: "AUTHORIZED 2026-05-10 — binding"
binding: "Charter v2.0, P-FV-Discipline, Charter §9 (Scientific Honesty)"
supersedes: "None (this is the first audit protocol)"
---

# INTERCEPTA Master Audit Protocol v1.0

## 0. Purpose and Authority

### 0.1 Purpose

This protocol governs a foundation-first, FDA-grade scientific audit of the INTERCEPTA project as it stood at git commit `e265f87` on 2026-05-10. The audit was triggered by a contradictory result on the M1 falsification gate first contact (silhouette = -0.0079 on Travaglini SS2 with Geneformer-V2-104M_CLcancer, against a charter-specified threshold of > 0.05) combined with a CEO directive that no further forward progress occurs until the foundation is verified, from the root of the project, with no compromises.

The audit's purpose is to establish, with documented evidence, whether each layer of the project — vision and charter, prior validated results, architectural choices, implementation, and result interpretation — is sound, partially sound, or defective. Where defects are found, the audit produces corrective and preventive actions before the project advances.

### 0.2 Authority

The CEO holds final authority on findings, charter revisions, and direction changes. The CSO holds operational authority over audit execution: choice of tests, interpretation of evidence, and recommendations.

The protocol itself, once authorized by the CEO and tagged in git, is the binding standard for the entire audit. Deviations from the protocol require explicit CEO authorization, recorded in writing.

### 0.3 Binding Documents

This audit is binding under:

- **INTERCEPTA Charter v2.0** (`docs/charter/build/INTERCEPTA_Charter_v2.0.pdf`, 161 pages, tag `charter-v2.0`)
- **Operating Principle P-FV-Discipline** ("we rewrite if our work doesn't match charter standards; no compromise on vision; applies to past, present, future")
- **Charter §9, Scientific Honesty** (declared-fixed isn't fixed until verified end-to-end)
- **CEO directive 2026-05-10**: full re-examination from root, multi-day, no compromises

### 0.4 Scope

In scope:

- Layer 0: Vision and charter (all 18 chapters of v2.0)
- Layer 1: Prior Tier 1 validated results (KAALCURA-3 GDSC, disease KAALCURAs, LuCA NSCLC, Travaglini SS2 file integrity, foundation models)
- Layer 2: M1 architectural choices (model selection, dataset choice, falsification gate metric, mechanism axis design)
- Layer 3: M1 implementation (cell_processing v0.1.2 module, all 8 files, pipeline behavior)
- Layer 4: M1 result interpretation (silhouette = -0.0079, mean separations, OOD distances)

Out of scope (defer to future audits):

- M2 disease KAALCURA layer (covered in Layer 1 audit only insofar as prior results are concerned; not the future-state architecture)
- M3+ milestones (charter §13 future gates beyond M1)
- Operational infrastructure beyond what M1 touches (HPC quotas, environment management, etc., except where they affect M1 results)

## 1. Severity Grading Rubric

Every finding emerging from the audit MUST be assigned exactly one severity grade. The rubric is deterministic: each grade has objective criteria. A finding cannot straddle grades; if uncertain, the higher grade applies.

### 1.1 Critical

A finding is **Critical** if any of the following holds:

- A claim in charter v2.0 is false in a way that invalidates a stated falsification gate, deliverable, or capability claim
- A previously reported Tier 1 result cannot be reproduced from raw inputs
- A previously reported Tier 1 result was computed with methodology that, on review, does not support the claim made about it (e.g. label leakage, cherry-picked metric, unjustified preprocessing)
- An architectural choice introduces an irrecoverable bias that the architecture cannot detect
- An implementation defect produces results that materially differ from what the architecture specifies (e.g. embeddings extracted from wrong layer, tokenization corrupted)
- A safety, ethics, or compliance commitment in charter §5 is violated by the implemented system

**Critical findings HALT all forward progress.** Audit continues, but no new development, no new milestones, no new commits beyond audit findings until Critical findings are resolved with documented CAPA.

### 1.2 Major

A finding is **Major** if any of the following holds:

- A claim in charter v2.0 is overstated or imprecise but not false
- A reported result is reproducible but its presentation does not adequately disclose limitations
- An architectural choice is suboptimal but not invalidating; an alternative would meaningfully better serve the vision
- An implementation defect produces results that are subtly different from specification but the difference does not invalidate downstream conclusions on this run
- Documentation, audit trail, or provenance is insufficient to defend a claim under external scrutiny

Major findings do not halt progress but BLOCK the next milestone tag until resolved with documented CAPA.

### 1.3 Minor

A finding is **Minor** if:

- A claim is accurate but ambiguously phrased and could be misread
- A test methodology is correct but presentation, formatting, or naming is inconsistent
- An implementation detail differs from convention without functional impact
- An output artifact is missing metadata or context that a reviewer would expect

Minor findings are addressed in the next normal commit cycle, do not block tags, but must be tracked.

### 1.4 Observation

A finding is an **Observation** if:

- A pattern, choice, or convention warrants documentation as institutional knowledge
- An alternative approach exists that may or may not be preferable
- A risk has been identified but is not currently materialized
- A precedent set by this audit may need to be re-applied later

Observations are filed for future reference and do not block anything.

### 1.5 No Implicit Pass

A subject of audit is NEVER implicitly graded. Every Audit Item (defined below) MUST be explicitly graded **PASS / Critical / Major / Minor / Observation / INCONCLUSIVE** before that item is considered closed.

**INCONCLUSIVE is a valid grade.** It indicates that available evidence does not yet support a definitive grading. INCONCLUSIVE blocks forward progress as if it were Major, until escalated to a definitive grade.

## 2. Audit Phases

The audit proceeds in five phases, executed in strict order. A later phase may not begin until the prior phase is sealed (defined below).

### 2.1 Phase A — Charter Audit (Layer 0)

**Purpose:** Verify that the spec itself is correct, internally consistent, and aligned with the vision before any implementation is tested against it.

**Method:**
- Read each of the 18 chapters of charter v2.0 with adversarial eye
- For each load-bearing claim, classify as: (a) verified empirical fact, (b) reasoned argument, (c) aspiration, (d) placeholder
- For each falsification gate (§13 explicitly, others where present), evaluate: is the metric appropriate, is the threshold defensible, is the dataset appropriate
- For each architectural commitment (§6), evaluate: implementable, testable, aligned with §1 vision
- Identify internal contradictions and omissions

**Output:** `docs/research/audit/A_charter_audit.md` containing:
- Per-chapter findings list
- Cross-chapter contradiction list
- Spec-completeness gap list (vision-relevant items not yet specified)
- Severity-graded summary
- Phase A Seal entry (defined in §3)

**Acceptance Criteria for Phase A Seal:**
- All 18 chapters reviewed and findings listed
- Every load-bearing claim either accepted with evidence or graded Critical/Major
- Every falsification gate evaluated against §1 vision
- All Critical findings have proposed CAPA
- CEO has reviewed and authorized phase to seal

### 2.2 Phase B — Prior Results Audit (Layer 1)

**Purpose:** Verify that previously reported Tier 1 results are real, reproducible, and presented honestly.

**Method:**
- Identify every Tier 1 number stated in charter v2.0, in `intercepta_100_results.txt`, or in the conversation memory
- For each, attempt to reproduce from raw inputs and saved code
- Audit fold splits, label sources, and statistical procedures for leakage and bias
- Test each result against an adversarial null (random labels, shuffled features, untrained baseline)
- Classify each result as REPRODUCIBLE / REPRODUCIBLE-WITH-CAVEATS / NOT-REPRODUCIBLE / UNTESTABLE

**Output:** `docs/research/audit/B_tier1_audit.md` containing:
- Per-result reproducibility report
- Methodological audit (fold integrity, label source, leakage check)
- Adversarial null comparison
- Severity-graded summary
- Phase B Seal entry

**Acceptance Criteria for Phase B Seal:**
- Every Tier 1 number traced to its source code and raw inputs
- Every result reproduced or explicitly marked UNTESTABLE with reason
- Every Critical or Major finding has proposed CAPA
- CEO has reviewed and authorized phase to seal

### 2.3 Phase C — Architecture Audit (Layer 2)

**Purpose:** Verify that the architectural choices made for M1 are defensible, optimal-or-justified, and aligned with charter.

**Method:**
- For each architectural choice in M1 (model family, model variant, capacity, pretraining corpus, validation dataset, falsification gate metric, mechanism axis selection), compare against:
  - Available alternatives in the literature/landscape (per §3 of charter)
  - Charter §6 specification
  - Charter §1 vision
  - Practical constraints (compute, time, data availability)
- Reproduce the decision rationale, then evaluate whether the rationale survives scrutiny
- Where rationale is missing, flag it
- Test each choice for evidence of bias toward convenience over correctness

**Output:** `docs/research/audit/C_architecture_audit.md` containing:
- Decision-by-decision audit
- Alternative-not-taken analysis
- Bias-toward-convenience assessment
- Severity-graded summary
- Phase C Seal entry

**Acceptance Criteria for Phase C Seal:**
- Every M1 architectural choice has documented rationale
- Every choice has been compared against at least one alternative
- All Critical findings have proposed CAPA
- CEO has reviewed and authorized phase to seal

### 2.4 Phase D — Implementation Audit (Layer 3)

**Purpose:** Verify that the cell_processing v0.1.2 module faithfully implements the architecture specified in charter §6.4.

**Method:**
- Line-by-line review of all 8 module files (`__init__.py`, `_patches.py`, `embeddings.py`, `fm_backends.py`, `mechanism_axes.py`, `pipeline.py`, `tokenization.py`, `uncertainty.py`)
- For each function, identify intent, then verify implementation matches intent
- Cross-check against upstream Geneformer source where applicable
- Execute the H1–H6 hypothesis tree (and any expansion that emerges) in full depth, with each hypothesis broken into testable sub-questions
- Reproduce one cell's full pipeline manually, byte-by-byte, comparing each intermediate against module output

**Output:** `docs/research/audit/D_implementation_audit.md` containing:
- Module-by-module review findings
- Hypothesis tree results, fully populated
- Manual-reproduction comparison
- Severity-graded summary
- Phase D Seal entry

**Acceptance Criteria for Phase D Seal:**
- Every function reviewed
- Every hypothesis in H1–H6 (and expansions) tested or marked INCONCLUSIVE with reason
- All Critical findings have proposed CAPA
- CEO has reviewed and authorized phase to seal

### 2.5 Phase E — Result Synthesis (Layer 4)

**Purpose:** With Phases A–D evidence in hand, produce the honest, evidence-based interpretation of the M1 first-contact result.

**Method:**
- Synthesize findings from all prior phases
- State precisely what the silhouette = -0.0079 result means in light of accumulated evidence
- Identify which charter claims are confirmed, refuted, or require revision
- Identify which architectural choices are confirmed, refuted, or require revision
- Identify which implementation details are confirmed, refuted, or require revision

**Output:** `docs/research/audit/E_result_synthesis.md` containing:
- Synthesis of prior phases
- Final interpretation of M1 first contact
- Itemized list of revisions required
- Phase E Seal entry

**Acceptance Criteria for Phase E Seal:**
- Every Critical and Major finding from A–D addressed in synthesis
- Final M1 verdict is one of: VERIFIED-PASS, VERIFIED-FAIL-AS-EXPECTED, VERIFIED-FAIL-DUE-TO-IDENTIFIED-CAUSE, BLOCKED-BY-FOUNDATIONAL-DEFECTS
- CEO has reviewed and authorized phase to seal

### 2.6 Phase F — Decision and Path Forward

**Purpose:** Translate audit findings into concrete next actions: charter revisions, code rewrites, prior-result amendments, milestone re-planning.

**Method:**
- For each finding requiring action, specify: action, owner, dependencies, acceptance criteria
- Where charter v2.0 requires revision, draft charter v2.1 changes for CEO review
- Where prior results require revision, draft amendment notes
- Where code requires rewrite, specify scope and acceptance test
- Where M1 plan requires revision, propose updated milestones

**Output:** `docs/research/audit/F_decision_and_plan.md` containing:
- Action item list with severities and dependencies
- Charter v2.1 change proposal (if any)
- Tier 1 result amendments (if any)
- Code rewrite scope (if any)
- Updated M1 plan
- Phase F Seal entry (closes the audit)

**Acceptance Criteria for Phase F Seal (Audit Closure):**
- Every Critical and Major finding has an action item
- Every action item has an owner and acceptance criteria
- CEO has reviewed and authorized audit closure
- A new git tag `audit-foundation-2026-05` is created at this point

## 3. Phase Sealing Procedure

Each phase ends with a **Seal**, a formal written closure authorized by the CEO. The Seal procedure prevents premature closure and goalpost moving.

### 3.1 Seal Components

A Phase Seal consists of:

1. **Findings Summary** — count by severity
2. **Critical Findings List** — each with proposed CAPA
3. **Open Items** — anything INCONCLUSIVE with explanation
4. **Evidence Index** — list of files, commands, and outputs that constitute the audit trail for this phase
5. **CSO Recommendation** — proposed phase outcome (CLEAN-CLOSE / CLOSE-WITH-FINDINGS / BLOCK-AT-CRITICAL)
6. **CEO Authorization** — explicit text in conversation: "Phase X sealed" or "Phase X re-open: <reason>"
7. **Git Commit** — the seal is committed to git as part of the phase output document

### 3.2 No Seal Without Evidence

A phase cannot be sealed if any of the following holds:

- A planned test was skipped without explicit CEO authorization
- A finding is marked PASS without adversarial review
- A finding is marked INCONCLUSIVE for more than three audit-working-days without escalation
- The audit trail (commands, outputs, file paths) is incomplete

### 3.3 Reopening

A sealed phase may be reopened by either CEO or CSO if new evidence emerges that contradicts a sealed finding. Reopening follows the original phase procedure with the new evidence appended.

## 4. Audit Trail Requirements

Every test, every diagnostic, every result that contributes to a finding MUST satisfy traceability requirements.

### 4.1 Required Artifacts

For each test:

- **Date and time** of execution (ISO 8601, with timezone)
- **System** on which the test ran (Mac hostname, HPC node, etc.)
- **Software environment** (conda env, Python version, package versions for relevant libraries)
- **Exact command** that was run, copy-pastable, executable in isolation
- **Raw output** of the command, in full, preserved as a file
- **Interpretation** linking the raw output to the audit finding

### 4.2 Storage

All audit artifacts live under `docs/research/audit/evidence/<phase_letter>/`, organized by test ID. Test IDs follow the pattern `<phase>.<finding>.<test_index>`, e.g., `D.H4.1` for Phase D, hypothesis H4, sub-test 1.

### 4.3 Immutability

Once an evidence file is committed to git, it is immutable. Re-runs produce new files with new test IDs (e.g. `D.H4.1.rerun-2026-05-12`), not modifications to existing files. The audit trail accumulates; it does not erase.

### 4.4 No Conversation-Only Findings

A finding is not part of the audit if it exists only in this conversation. Every finding referenced in any phase output document MUST have a corresponding evidence file in `evidence/`.

## 5. Adversarial Review Requirement

A finding may not be graded PASS without adversarial review.

### 5.1 What Adversarial Review Means

Adversarial review is an active, deliberate attempt by the CSO to falsify the proposed PASS finding. It includes:

- Considering whether the test could PASS by accident (statistical chance, narrow conditions, lucky baseline)
- Testing the same claim with an alternative method, alternative dataset, or alternative metric
- Asking what an external reviewer hostile to the project would say
- Identifying the strongest available counter-evidence and explaining why it does not overturn the finding

### 5.2 Documented Adversarial Review

Each PASS finding's evidence file MUST contain a section titled "Adversarial Review" with:

- The strongest objection considered
- The counter-evidence weighed
- Why the PASS still holds despite the objection

If no objection survives consideration, the finding still requires the adversarial review section explicitly stating "No surviving objections found after deliberate review of [list of attacks tried]."

### 5.3 No Convenience PASS

A PASS finding must NOT be reached because moving on is convenient. The CSO is on the record as having attempted to fail the finding before reaching PASS.

## 6. CAPA Structure for Findings Above Minor

Every Critical and Major finding requires a Corrective Action / Preventive Action plan.

### 6.1 Required CAPA Fields

- **Finding ID** (unique, of the form `<phase>.<seq>`, e.g., `D.07`)
- **Severity** (Critical / Major)
- **Description** (one paragraph, plain language)
- **Root Cause** (technical, not symptomatic)
- **Corrective Action** (what we do to fix this specific instance)
- **Preventive Action** (what we change in the system so it does not recur)
- **Acceptance Test** (how we verify the corrective action worked)
- **Owner** (CEO or CSO)
- **Status** (OPEN / IN-PROGRESS / VERIFIED-CLOSED)

### 6.2 No Closing Without Verification

A CAPA cannot be marked VERIFIED-CLOSED until the Acceptance Test has been executed and produced documented evidence of correction.

### 6.3 CAPA Drives Charter and Code

Where CAPA requires charter revision, the corrective action includes a draft change to the affected chapter, and the preventive action includes a process change to detect future drift.

Where CAPA requires code rewrite, the corrective action includes the rewrite scope and the preventive action includes a regression test added to the codebase.

## 7. Hard Rules

The following rules apply throughout the audit and override convenience or schedule pressure.

### 7.1 No Goalpost Moving

Acceptance criteria specified in this protocol are FROZEN at protocol authorization. They may be amended only by a written CEO directive recorded in this protocol's revision history. Mid-test redefinition of what counts as PASS is prohibited.

### 7.2 No Premature Closure

A phase, finding, or test that lacks evidence does not close. INCONCLUSIVE is the correct status; it blocks forward progress and forces escalation.

### 7.3 No Hiding Findings

Findings that emerge but do not fit the current phase are recorded immediately and routed to the appropriate phase. They are not deferred without explicit CEO authorization.

### 7.4 No Single-Reviewer PASS

The CSO may not unilaterally seal a phase. Every Seal requires explicit CEO authorization in conversation.

### 7.5 Scope Discipline

Findings on subjects outside audit scope (per §0.4) are recorded as Observations and routed to a future audit. They do not expand the current audit's scope without CEO authorization.

### 7.6 Stop on Critical

Discovery of a Critical finding triggers an immediate halt of all forward project work (not just the audit; the whole project). The audit continues to characterize the Critical finding fully. Forward work resumes only when the Critical finding is closed via CAPA.

## 8. Audit Working Conventions

### 8.1 Vocabulary

- **Audit Item:** a discrete subject of audit (one chapter, one Tier 1 number, one architectural decision, one module function, one hypothesis sub-test)
- **Finding:** a graded conclusion on an Audit Item
- **Evidence:** a file under `evidence/` with raw output supporting a finding
- **Seal:** the formal closure of a phase
- **CAPA:** Corrective Action / Preventive Action plan for a Critical/Major finding

### 8.2 Naming

- Findings: `<phase>.<seq>` (e.g. `A.01`, `D.17`)
- Tests: `<phase>.<hypothesis>.<sub>` (e.g. `D.H4.2`)
- Evidence files: `<test_id>.txt` or `<test_id>.json` or `<test_id>.<ext>`
- Phase outputs: `<phase>_<title>.md` (e.g. `A_charter_audit.md`)

### 8.3 Charter Cross-Reference

Every finding referencing a charter section uses the form `Charter v2.0 §X.Y`. The first such reference in a phase output document also includes the chapter title. Subsequent references use the section number alone.

### 8.4 Time Logging

Each test records its start time, end time, and total wall-clock duration. Time tracking is for audit-trail completeness, not for time-management; we work to closure on each item without optimizing for speed.

## 9. Protocol Amendments

This protocol may be amended only with explicit CEO authorization recorded in the revision history below. The amendment effective date is the date of authorization.

### Revision History

- **v1.0, 2026-05-10** — Initial protocol, drafted by CSO. Pending CEO authorization.

## 10. CEO Authorization Block

This protocol is in DRAFT status until the CEO records authorization here, after which it becomes the binding standard for the audit.

```
AUTHORIZATION: GRANTED 2026-05-10

CEO: Prasad Akula
Date: 2026-05-10
Signature line: "Authorized as INTERCEPTA Audit Protocol v1.0, binding."

CSO: Claude
Date: 2026-05-10
Signature line: "Drafted in good faith under P-FV-Discipline."
```

Once authorized, this protocol governs the audit through Phase F Seal.

## End of Protocol v1.0
