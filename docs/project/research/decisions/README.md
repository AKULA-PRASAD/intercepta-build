# INTERCEPTA Fullest Vision -- Decision Records

**Charter reference:** fullest-vision-charter-v1.1

This directory holds formal decision records for GO/NO-GO decisions and major architectural commitments.

## Cadence (per charter §5.3)

- After Layer 1: GO/NO-GO on commitment to specific method classes
- After Layer 2: GO/NO-GO on architectural commitment
- After Layer 3: GO/NO-GO on validation plan adequacy
- After Layer 4: GO/NO-GO on implementation start

## Naming convention

INTERCEPTA_FV_Decision_NN_topic.md (zero-padded number)

## Required content per decision record

1. Decision statement (one sentence)
2. Date and signatories (CEO + CSO)
3. Options considered
4. Chosen option with rationale
5. Trade-offs explicitly named
6. Citations supporting decision
7. Reversibility assessment (can this be unwound? cost?)
8. Tag reference (fullest-vision-decision-N-locked)

---

## Filename Convention Note (added 2026-05-11)

**v2 content without explicit `_v2` filename marker:**

Decisions 2-10 contain v2 content per audit Phase 2-9 remediation work (May 10, 2026). Their headers explicitly state "Decision X v2 ... PROPOSED" but their filenames do NOT carry a `_v2` suffix because they were re-written in place during the audit cycle rather than versioned with new filenames.

**Decision 1 is the ONLY case** where v1 → v2 supersession is filename-explicit:
- `INTERCEPTA_FV_Decision_1_v1_Q1_method_class_SUPERSEDED_by_v2_REVISED.md` — v1, archived per P16
- `INTERCEPTA_FV_Decision_1_v2_Q1_method_class_REVISED.md` — v2 canonical (triggered by Phase 6 Souza & Mehta evidence)

Reason for asymmetry: Decision 1 was already in PROPOSED state when Phase 6 evidence forced revision. Decisions 2-10 were each first-written as v2 during their respective Phase 2-9 audit remediation.

**To read v2 content for any Decision:** Open the file with the higher Decision number (or REVISED suffix where present); check header for "v2" version marker.

