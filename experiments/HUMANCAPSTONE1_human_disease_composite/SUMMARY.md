# HUMANCAPSTONE1 — the unified human-disease composite (end-to-end): RESULT

**Reproduced ×2 byte-identical (sha de856da); full suite 114/114 (7 new tests).** The human analog of the
pathogen-side CAPSTONE: the disease-class-aware COMPOSITE router driven end-to-end over a frozen panel of 10
representative human diseases spanning every reachable class + validated arm. Ties this session's builds into
one operational capability: GENETICCLASS1 (class envelope) → COMPOSITE5 (class-aware genetic arm) → + MENDEL1
(monogenic) + DEPEND1 (cancer dependency).

## The human-disease decision-coverage table
| disease | route | arm / grade |
|---|---|---|
| melanoma (cancer) | shortlist | functional_dependency (DEPEND1) |
| cystic fibrosis (monogenic, CFTR given) | mode | causal_gene (MENDEL1) |
| Duchenne (monogenic, gene not declared) | **ABSTAIN** | descriptor-absent |
| coronary artery disease | shortlist | genetic **FULL** |
| rheumatoid arthritis | shortlist | genetic **FULL** |
| Parkinson disease | shortlist | genetic **FULL** |
| idiopathic pulmonary fibrosis | shortlist | genetic **FULL** (provisional) |
| type 2 diabetes | shortlist | genetic **CAPPED** |
| osteoarthritis | **ABSTAIN** | class-level (musculoskeletal_renal, GENETICCLASS1) |
| undiagnosed / idiopathic (no data) | **ABSTAIN** | no transferable signal |

**7/10 signal-backed, 3/10 cited abstentions; 3 arms exercised (dependency, causal-gene, genetic); genetic
FULL ×4, CAPPED ×1.** Both abstention TYPES are demonstrated first-class: a **class-level** ABSTAIN (osteoarthritis
— GENETICCLASS1 showed genetic target-ID does not robustly transfer for musculoskeletal/renal) and a
**descriptor-absent** ABSTAIN (Duchenne without a declared causal gene; undiagnosed with no data).

## What it delivers (and its honest scope)
- **"Any human disease" as honest decision-coverage, not a universal model** — the composite applies the arm whose
  validated transfer condition holds for the input's class and **refuses, with a cited reason, where none does.**
  This is the human-side realization of the program's core thesis.
- Every fired arm traces to a committed, reproduced validation (DEPEND1 cancer dependency; MENDEL1 monogenic mode;
  GENETICS1 + GENETICCLASS1 genetic, now class-graded). Deliverables are target-**relevance** / intervention-**mode**
  ranked hypotheses — **not** drugs, not clinical. Retrospective. Pure router logic (data-free, deterministic).
- Coverage is bounded by the validated arms: cancer (dependency), monogenic (causal gene given), complex disease
  (genetic, class-graded). Classes/inputs outside these correctly ABSTAIN.

## Reproduce
`python run.py` (byte-identical) · `pytest tests/test_humancapstone.py` (7 tests) · full suite 114/114.
