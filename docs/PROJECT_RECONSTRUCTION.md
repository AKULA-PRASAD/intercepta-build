# INTERCEPTA — Project Reconstruction & Honest State (as of 2026-08-04)

*A from-the-record reconstruction for a senior scientist joining the team. Every claim traces to CONSTITUTION.md,
VISION.md, LEDGER.md, the commit history, or `papers/zero_data_discovery/REPORT.md`. Where this doc relies on commit
headlines / working memory rather than a full re-read of a row, it says so.*

## The one-sentence throughline
Across every arc the project has run — cell-line drug response, functional inference, module integration, virtual-screening
theory, zero-data target-ID, and the molecule half — the recurring, hard-won result is an **INFORMATION CEILING**: you
cannot *combine* or *transfer* your way past information that isn't in the data. Crossing it requires **new information**
(perturbation-in-patient, prospective, wet-lab, or 3D/experimental). The program's single most differentiated asset is not
a model — it is the **rigor methodology** (Constitution + pre-registration + reproduce-×2 + falsify-first + first-class
negatives) that has repeatedly caught its own over-reads before they were committed.

## The story in five acts
- **Act 0 — Reckoning.** The original "universal net" (15-layer Neo4j graph, 6 scouts, KAALCURA, RNA-velocity time machine,
  two-population ODE; "any disease, novel molecules, therapy selection") largely did not survive rigor. Commit `9c5d79c`
  removed **14 fabricated artifacts**. This is the founding trauma the Constitution exists to prevent (`INTEGRITY_SWEEP.md`).
- **Act 1 — Honest cancer-first engine (B1–B23).** Verified: +0.212 cross-dataset cell-line drug-response signal (V1) and a
  **well-powered null that nothing beats it** (V7); textbook AML mutation→drug mechanism (V4–6/V12); weak, drug-specific,
  proliferation-independent patient transfer (V9). Clinically **null within cancer type** (B10). The **functional-inference
  arc** (B12–B22) rescued FLT3/BCL2 in BeatAML (V15–V20) then **failed external replication** (B20/B21); B23/V22 unified it:
  the functional advantage is **target-tautological** and the ceiling is **modality-general**. Reorientation: the real lever
  is **perturbation measured in patients** (Track-1, unfunded).
- **Act 2 — Synergy, the clean generalizer (B24–B29).** Combination synergy **generalizes to unseen pairings of known
  drugs** (V23) — externally replicated, calibrated, shipped (`SynergyRanker`) — but **not to novel drugs**.
- **Act 3 — Modules + the integration verdict (B30–B52).** Standalone modules shipped (ADMET B30, synthesizability B31,
  target-ID B34, generation B33/B39–B41, screening engine). The **integration ladder B32→B38** is a decisive negative:
  **whole is not > parts; the bottleneck is INFORMATION, not combination.** VS theory (B53–B65) quantified the small honest
  binding signal (P6: decoy-bias and analog-bias are independent/additive) and showed the extrapolation gap to novel
  chemistry is **signal-loss, not a correctable modeling error**.
- **Act 4 — North-star reframe (2026-07-31).** Objective corrected to **discovering the best intervention for ANY disease,
  incl. never-seen ones, with zero activity data, within hours.** This front is **label-free** and therefore **orthogonal**
  to all the label-dependent ceilings above. Benchmarks became supporting tools only.
- **Act 5 — Zero-data arc (current).** Target-ID from sequence is dominated by **generic conservation** (TID1); pocket
  druggability doesn't beat it (TID2); it **degrades across kingdoms and silently fails on isolated pathogens** (TID3) and
  the system **can't cheaply tell when it's out of its depth** (TID4). **Mechanism breaks the ceiling** — the arc's first
  real positive: **FBA gene-essentiality** adds beyond conservation (MET1), **replicates** in E. coli + M. tuberculosis
  (MET2), gives a **better ranked shortlist** (MET3) — but its non-metabolic extension via PPI-centrality was a **study-bias
  artifact** (MET4, negative). Binding is weak zero-data (C1); the pieces **compose end-to-end** on M. tuberculosis (E2E1);
  a **self-improving loop** works in-domain, guarded by calibrated confidence, but only near-domain (SIL1/SIL2). The
  **molecule half** just opened: ligand hit-finding is **analog-driven with a soft novel-chemotype ceiling** (HIT1); the
  structure-only **physics floor** test (HIT2, thrombin docking) is in progress.

## Evidence tiers (honest ledger)
- **Verified / reproduced-×2:** +0.212 ceiling (V1/V7); AML mutation→drug mechanism (V4–6/V12); weak drug-specific patient
  transfer (V9); synergy generalizes for known-drug pairs (V23); ADMET/synth modules beat trivial (B30/B31); integration is
  NOT whole>parts (B32–B38); conservation target-ID ceiling (TID1–4); **FBA-essentiality breaks the ceiling for metabolic
  targets** (MET1–3); guarded in-domain self-improving loop (SIL1).
- **Falsified / downgraded:** therapy-selection coordinate (<5%); functional-inference external generalization (B20/V19–20);
  literal "any disease / novel molecules"; PPI-centrality mechanism for non-metabolic targets (MET4); de-novo generation
  (was scaffold-hopping).
- **Genuine generalizing positives:** synergy on known drugs (V23); FBA-essentiality mechanism (MET1–3, metabolic scope).
- **Unknown / untested:** anything prospective or wet-lab; front-half disease→mechanism→target reasoning; a study-bias-robust
  non-metabolic zero-data mechanism; whether physics recovers novel chemotypes (HIT2, pending).

## Biggest risks / what must never be repeated
1. Promoting a **single-cohort/single-organism positive** to "generalizes" without external replication — the project's
   repeated failure mode (V14, V19/V20→B20, MET2 3-org over-claim).
2. Mistaking a **protocol failure** for an information ceiling (B53: below-random docking was likely rigid-receptor/prep).
3. Subtle **confounds that fake positives** — study bias (MET4), novelty-definition tautology (HIT1), decoy/analog bias
   (B54 recalibrated B42/B43 down). Any un-double-controlled enrichment is provisional.
4. Re-introducing any **non-reproduced or fabricated** artifact (the cardinal sin; Act 0).

## The biggest structural gap (where the leverage is)
The **front half** (disease understanding · mechanism inference · target prioritization as reasoning) and the **extensible,
provenance-/confidence-tiered "living substrate"** ("any disease → a query"; continuous absorption, Charter U2) are marked
**✗ absent** in the capability map. The program has strong **back-half** capability + **world-class validation methodology**;
the vision's hardest part is largely unbuilt. That gap — not another molecule-scoring module — is the leverage.

**First front-half chapter done (FRONT1, 2026-08-04):** selective mechanistic target discovery (essentiality + metabolic
chokepoint + host non-homology, zero-data, benchmarked vs conservation). Result: essentiality (MET) is the recovery driver;
chokepoint/selectivity don't robustly add beyond it. **Key finding: ranking targets by conservation is therapeutically
DANGEROUS** — host-toxic targets (human core-essential homologs) are the most conserved (E. coli bitscore 123 vs 29), so
conservation promotes unsafe targets, and soft selectivity doesn't reliably fix it → selectivity must be a **hard
host-non-homology filter**. The front half is now partially addressed (mechanism + a selectivity correction); disease
understanding, richer mechanism inference, and the extensible living substrate remain ✗.

## What is missing before a large new bet (stated, not invented)
- **Any experimental/prospective validation** — the whole zero-data arc is retrospective; the vision's true metric is untested.
- **A resource decision** — every "cross the ceiling" path (wet-lab, 3D/co-folding, GPU rescoring, prospective assays) is
  blocked by zero-budget / CPU-only / no-wet-lab / no-collaboration constraints. Which constraints can flex determines what
  is even possible.
- **A falsifiable operational definition of the front-half task** (disease understanding / mechanism inference) that is
  testable on the proving ground — to be designed before building.

## Not verified in this reconstruction pass (read directly if a decision depends on them)
`docs/aspirational_original/`, legacy `engine/` modules, AML-era manuscripts, and the individual AML metrics files (trusted
via the LEDGER's reproduced-×2 attestations, not re-run this pass); LEDGER rows B59–B65 and the zero-data rows were taken
from commit headlines + working memory (authored this session), not a fresh full re-read.
