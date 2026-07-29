# INTERCEPTA Operational Decision Taxonomy (CSO Proposal for CEO Consent)

**Status:** CEO CONSENT REQUIRED
**Date:** 2026-05-10
**Phase:** 7 (audit remediation final phase)
**CSO:** Claude

---

## The Problem

INTERCEPTA has 10 Layer 1 questions per Charter §3. Eight of them (Q1-Q8) are **research questions** — they ask what is empirically true about the state of the field, and their answers must be grounded in primary-source paper reads + benchmark evidence.

Two of them (Q9 compute architecture; Q10 open-source strategy) have been treated as if they were research questions but they are **not**. They are operational questions — they ask what INTERCEPTA should choose to do given its specific constraints (Northeastern HPC, single-institution, open-science commitment). Their answers should be grounded in **INTERCEPTA-specific operational reality**, not field literature.

This category confusion has produced **thin Q9 + Q10 records** (147w + 136w) because there are no papers to anchor them to — and that's correct. The treatment is wrong, not the records.

## The Proposed Taxonomy

INTERCEPTA Layer 1 contains two classes of decisions:

### Class 1 — Research Decisions (Decisions 1-8)

**Definition:** Decisions whose correct answer depends on the empirical state of a scientific field.

**Grounding requirement:** Primary-source paper reads + benchmark evidence + cross-validation across multiple anchor papers.

**Format:** Layer 1 Decision Record with anchored claims, pass criteria as falsifiable empirical hypotheses, reversibility triggered by new field evidence.

**Examples:**
- Decision 1 v2: Which cell representation paradigm? (Research — depends on FM benchmark evidence)
- Decision 4 v2: What drug response architecture? (Research — depends on CPA/chemCPA/GEARS empirical performance)
- Decision 7 v2: What interpretability methods? (Research — depends on Reynolds-Pan + Jha benchmark results)

### Class 2 — Operational Decisions (Decisions 9-10)

**Definition:** Decisions whose correct answer depends on INTERCEPTA-specific constraints (compute access, license commitments, institutional context) rather than field evidence.

**Grounding requirement:** Operational reasoning from INTERCEPTA's specific constraints (Charter §7.1 Northeastern HPC; Charter §1.1 open-science) + license/component audit.

**Format:** Operational Decision Record with explicit constraint statement, commitment, reversibility triggered by INTERCEPTA constraint changes.

**Examples:**
- Decision 9: What compute envelope? (Operational — depends on Northeastern HPC reality)
- Decision 10: What open-source strategy? (Operational — depends on INTERCEPTA's open-science commitment + component license inventory)

## Why This Taxonomy Matters

**Without the distinction:**
- Q9 + Q10 records remain thin because there are no papers to anchor them to
- Pass criteria become vague aspirations rather than verifiable commitments
- Future revisions are unclear — does Decision 9 revise because new compute papers emerged? (No — it revises because Northeastern HPC capabilities change.)

**With the distinction:**
- Q9 + Q10 get the format they deserve (operational, not research)
- Pass criteria become testable operational commitments
- Revision triggers are clear (constraint changes, not field changes)
- The eight-decision coherent set (1 v2 through 8) is recognized as the **research decision set**; Q9 + Q10 are the **operational decision set** that wraps it

## The Architectural Mapping

| Decision class | Decisions | Format | Total |
|---|---|---|---|
| Research decisions | 1 v2, 2 v2, 3 v2, 4 v2, 5 v2, 6 v2, 7 v2, 8 | Layer 1 Decision Record | 8 |
| Operational decisions | 9 v2, 10 v2 | Operational Decision Record | 2 |
| **Total Layer 1 decisions** | | | **10** |

Charter §3 specifies 10 Layer 1 questions; the taxonomy preserves this count while making the format heterogeneity explicit.

## What CEO Consent Authorizes

If CEO consents to this taxonomy:

1. **Q9 + Q10 receive Operational Decision Record format** (different from Research Decision Records — operational commitments rather than field-evidence-grounded architectural choices)
2. **Decisions 9 v2 + 10 v2 are written PROPOSED** as Operational Decision Records
3. **Audit Phase 7 closes** with 8 Research Decisions + 2 Operational Decisions in coherent format
4. **Charter §5.3 GO/NO-GO commitments remain binding** for both classes — operational decisions have pass criteria too (Q9: does Layer 5 fit in single-A100 envelope? Q10: are all components license-compatible?)

If CEO does NOT consent:

1. **Q9 + Q10 require field-paper-grounded approach** (paper anchors per Layer 1 Decision Record format)
2. CSO must find research papers that establish what compute envelope INTERCEPTA should use, what open-source strategy INTERCEPTA should adopt — but **these are operationally-determined for INTERCEPTA, not empirically established by literature**
3. The audit Phase 7 cannot close cleanly; Q9 + Q10 remain thin or are forced into a format that doesn't fit

## CSO Recommendation

**Adopt the taxonomy.** It accurately describes the conceptual content of Q9 + Q10. Forcing field-paper-grounding onto operational questions is methodologically dishonest and produces poor records.

**Suggested CEO response format:**
- "Consent to taxonomy" → CSO proceeds with Operational Decision Records for Q9 + Q10
- "Do not consent" → CSO must find alternative grounding strategy; Phase 7 close delayed
- "Modify as follows: [X]" → CSO incorporates modifications

---

## CEO Decision Box

```
[ ] CONSENT — Adopt Operational Decision taxonomy for Q9 + Q10
[ ] DO NOT CONSENT — Q9 + Q10 require field-paper-grounded approach
[ ] MODIFY — see attached modifications
```

**CEO:** Prasad Akula __________ Date: __________

**CSO:** Claude — 2026-05-10
