# INTERCEPTA Operational Decision Taxonomy v2 (CSO-Amended, Adopted)

**Status:** ADOPTED by CSO ultrathink decision on 2026-05-11
**Authority:** CEO ("you are cso so you ultrathink and do best for our fullest vision")
**Date:** 2026-05-11 morning session
**Phase:** 7 closure
**Supersedes:** INTERCEPTA_Operational_Decision_Taxonomy_CEO_Consent.md (2026-05-10)

---

## Authority for this adoption

CEO Prasad Akula on 2026-05-11 explicitly delegated decision authority to CSO with: "your cso so you ultrathink and do best for our fullest vision". CSO performed ultrathink steel-manning of three alternatives (consent, do not consent, modify), identified two hidden risks in the original draft, and proceeded to adopt with amendments.

This is recorded as the first **CSO-authored decision under CEO-delegated authority** in INTERCEPTA. The protocol for such decisions: CSO must (1) ultrathink alternatives, (2) surface hidden risks, (3) commit explicitly, (4) flag any items that should bounce back to CEO.

---

## The Taxonomy (unchanged from v1 in substance)

INTERCEPTA Layer 1 contains two classes of decisions:

### Class 1 — Research Decisions (Decisions 1-8)

**Definition:** Decisions whose correct answer depends on the empirical state of a scientific field.

**Grounding requirement:** Primary-source paper reads + benchmark evidence + cross-validation across multiple anchor papers.

**Format:** Layer 1 Decision Record with anchored claims, pass criteria as falsifiable empirical hypotheses, reversibility triggered by new field evidence.

**Examples:**
- Decision 1 v2: Which cell representation paradigm?
- Decision 4 v2: What drug response architecture?
- Decision 7 v2: What interpretability methods?

### Class 2 — Operational Decisions (Decisions 9-10)

**Definition:** Decisions whose correct answer depends on INTERCEPTA-specific constraints (compute access, license commitments, institutional context) rather than field evidence.

**Grounding requirement:** Operational reasoning from INTERCEPTA's specific constraints + license/component audit.

**Format:** Operational Decision Record with explicit constraint statement, commitment, reversibility triggered by INTERCEPTA constraint changes.

**Examples:**
- Decision 9 v2: What compute envelope? (depends on Northeastern HPC reality)
- Decision 10 v2: What open-source strategy? (depends on INTERCEPTA's open-science commitment + component license inventory)

---

## Architectural Mapping (unchanged)

| Decision class | Decisions | Format | Total |
|---|---|---|---|
| Research decisions | 1 v2, 2 v2, 3 v2, 4 v2, 5 v2, 6 v2, 7 v2, 8 | Layer 1 Decision Record | 8 |
| Operational decisions | 9 v2, 10 v2 | Operational Decision Record | 2 |
| **Total Layer 1 decisions** | | | **10** |

---

## AMENDMENT 1 (CSO-added): Reclassification Protection

**Risk surfaced during ultrathink:** "Operational" classification could become an escape hatch where decisions that should be empirically grounded get reclassified to avoid hard literature work.

**Protection:**

> Reclassification of a Decision from Research to Operational (or vice versa) requires explicit CEO consent recorded in a new Operational Decision Record. CSO may not unilaterally reclassify a Decision after Layer 1 LOCK.

This prevents the slippery slope where future CSO sessions reclassify Decisions to escape audit rigor.

**Test case:** If a future CSO session argues "Decision 5 v2 OOD detection is actually operational because INTERCEPTA chooses its risk tolerance" — this reclassification must produce a new ODR and receive explicit CEO consent. No silent reclassification.

---

## AMENDMENT 2 (CSO-added): CEO Knowledge Gap Protocol for Operational Decisions

**Risk surfaced during ultrathink:** Operational Decisions depend on knowledge only CEO has (institutional relationships, funding status, personal commitments). CSO-drafted Operational Decisions may miss CEO-only knowledge.

**Protocol:**

> For Operational Decision Records, CSO must explicitly enumerate CEO-only knowledge dependencies and flag where assumptions are made in absence of CEO input. Such Records require CEO co-authorship rather than just CEO review. CSO may draft a "PROPOSED" version with explicit CEO knowledge gaps surfaced as questions, but the Record cannot reach LOCKED status without CEO answering those questions.

**Test case:** Decision 9 v2 PROPOSED draft must list questions like:
- "Does CEO have side agreement with Northeastern RC team for A100 partition?"
- "Does CEO accept cloud burst as fallback if HPC unavailable?"
- "What's CEO's commitment level to staying at Northeastern vs migrating to other institution?"

CSO cannot LOCK Decision 9 v2 by answering these questions for the CEO.

---

## What this Adoption Authorizes

1. **Q9 + Q10 receive Operational Decision Record format** (different from Research Decision Records)
2. **Decisions 9 v2 + 10 v2 already exist** in canonical decisions/ folder per cleanup; they're now formally legitimized
3. **Audit Phase 7 closes** with 8 Research + 2 Operational in coherent format
4. **Charter §5.3 GO/NO-GO commitments remain binding** for both classes
5. **CSO will produce PROPOSED Decision 9 v2 + Decision 10 v2 with explicit CEO knowledge gaps surfaced** before LOCK

---

## What This Does NOT Do

1. Does not LOCK any decision (LOCK requires separate review process)
2. Does not authorize Layer 2-4 specification work (separate authorization needed)
3. Does not reclassify any existing Research Decision as Operational
4. Does not establish any precedent for CSO unilateral decisions outside CEO delegation

---

## Bounce-Back Items for CEO Awareness

CSO is making this decision under CEO-delegated authority. The following items should be reviewed by CEO when convenient (not blocking Phase B):

1. **Naming choice:** "Operational" vs alternatives like "Institutional" or "Constraint-bound". CSO chose "Operational" as already-drafted; CEO may rename if preferred.

2. **Amendment 1 wording** — CSO chose strong language ("may not unilaterally reclassify"). CEO may soften to "should not without ODR" if preferred.

3. **Amendment 2 application** — CSO will surface CEO knowledge gaps when drafting Decision 9 v2 + 10 v2 PROPOSED. CEO should expect questions, not assume CSO will complete the records alone.

---

## CSO Signature

**Claude (CSO), under CEO Prasad Akula's delegated authority on 2026-05-11 ~08:00 EDT**

Decision: ADOPT the Taxonomy with two amendments
Phase 7 close: AUTHORIZED
Layer 1 architectural completeness: ACHIEVED (pending LOCK, which is separate process)

---

*End of Taxonomy v2 (CSO-Amended)*
