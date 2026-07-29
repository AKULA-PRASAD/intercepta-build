# INTERCEPTA Phase B Layer 4 — Artifact 4.3
## Failure Modes Specification

**Status:** PROPOSED for CEO LOCK (per Charter v1.2 §5.3 GO/NOGO discipline)
**Date:** 2026-05-11
**Author:** Claude (CSO)
**Predecessor artifacts:** Layer 2 + Layer 3 of Phase B COMPLETE; L4.1 + L4.2 PROPOSED
**Parent decisions:** Decision 6 v2 (F0-F7 taxonomy + hard/soft termination); Decision 8 v2 Commitment 4 (failure-mode characterization mandatory); Charter v1.2 §3 termination criteria + §10 P15 honest science
**Phase:** B (drug response prediction platform; 2-4 year horizon per Charter v1.2 §1.7)
**Phase F mapping:** Phase B failure modes extend in Phase F to federation failures (cross-institution disagreement), regulatory-grade failure modes (audit-trail loss), prospective trial failure modes (enrollment, adherence).
**Target length per Phase B Plan v2:** 3-4K words
**Filename:** INTERCEPTA_FV_L4_3_Failure_Modes_Specification_2026-05-11.md

---

## §0 Identification and Scope

### 0.1 What This Document Is

L4.3 is the **Failure Modes Specification** — the third and final artifact of Phase B Layer 4. L4.3 catalogs the specific ways INTERCEPTA's Layer 5 build can fail, separated into **empirical failures** (predictions are wrong per Decision 6 v2 F0-F7 taxonomy) and **infrastructure failures** (code crashes, OOMs, data corruption, cache invalidation, SLURM failures, environment drift). For each failure mode, L4.3 specifies the detection mechanism, recovery procedure, escalation path, and reporting requirement.

L4.3 answers: "when (not if) something breaks during Layer 5 build, what is the operational response that respects Charter principles and preserves the work to date?"

### 0.2 What This Document Is Not

L4.3 is NOT:
- A bug tracker (operational, not strategic)
- A disaster recovery plan for Northeastern Explorer (cluster-operations, not INTERCEPTA-specific)
- A regulatory failure reporting protocol (Phase F)
- An incident review process (operational; emerges naturally from Layer 5)
- A "blameless postmortem" cultural document (separate culture work; L4.3 specifies what gets investigated, not how blame attribution works)

### 0.3 Why Failure Modes Specification Is BINDING

Per Decision 8 v2 Commitment 4 BINDING: "For every (paradigm × disease × tissue × drug) combination that fails the V6 criterion, the failure mode must be classified per the F1-F7 taxonomy." This makes failure-mode classification not optional engineering hygiene but a Charter §1.3 falsifiability requirement: **a drug-discovery system that doesn't know when it fails is dangerous; INTERCEPTA's value proposition depends on quantified failure modes.**

L4.3 is therefore the operational instantiation of Decision 8 v2 Commitment 4 + Charter §10 P15 (only honest science).

### 0.4 Phase B Plan v2 Compliance

- Layers 2-3 of Phase B COMPLETE 2026-05-11
- L4.1 + L4.2 PROPOSED 2026-05-11
- **L4.3 → PROPOSED (this document)**
- After L4.3 LOCK → **Layer 4 of Phase B COMPLETE**
- Then Phase 8 audit → Layer 5 code starts

### 0.5 Document Conventions

- **BINDING** — failure mode classification or recovery procedure cannot be modified without amendment + CEO+CSO co-sign
- **DEFAULT** — specific detection thresholds Layer-5-revisitable per §11.5
- **F0-F7** — Decision 6 v2 + Decision 8 v2 empirical failure taxonomy (unchanged)
- **I1-I12** — L4.3 infrastructure failure taxonomy (this document)
- Recovery procedures use "**preserve via _SUPERSEDED_**" per Charter v1.2 §10 P16 BINDING

### 0.6 Anchor Re-Read Compliance

No new anchor re-read required for L4.3; consumes Decisions 6 v2 + 8 v2 + Charter §3 + §10 directly. Q5 anchor (Theunissen 2025) implicit in failure-mode detection challenges.

---

## §1 Two Failure-Mode Classes

### 1.1 Empirical Failures (F0-F7) — Predictions Are Wrong

These are **Decision 6 v2 + Decision 8 v2 BINDING** taxonomy. The model produces a prediction; the prediction is wrong; we classify why.

| Code | Name | What happens |
|---|---|---|
| F0 | Model cannot learn | Training error doesn't converge; architecture broken |
| F1 | Cross-resolution mismatch | Bulk → single-cell prediction degrades |
| F2 | Cross-platform batch effect | Smart-seq2 vs 10x Genomics signal differs |
| F3 | Cross-tissue context loss | Tissue-specific regulation not captured |
| F4 | Cross-species transfer break | Mouse-trained fails on human |
| F5 | Drug class OOD | New MoA class outside training |
| F6 | Disease class OOD | New therapeutic area outside training |
| F7 | Patient population gap | Demographic / clinical-state mismatch |

**Detection:** L3.2 56 pass criteria + V-evaluator failure-mode classifiers per L3.1. **Recovery:** L3.1 TerminationLogic hard / soft / pass-with-reservations + Decision 6 v2 specific revision triggers.

### 1.2 Infrastructure Failures (I1-I12) — Code/System Breaks

These are L4.3 contribution; not in any prior Decision. The code crashes, the cache corrupts, the cluster goes down — operational problems that block Layer 5 progress without being scientific failures.

| Code | Name | What happens |
|---|---|---|
| I1 | Environment drift | Conda env on Mac diverges from Explorer; reproducibility broken |
| I2 | Data access blocked | Dataset URL returns 404, paywall, or auth required |
| I3 | Substrate weight download fails | scFoundation 100M checkpoint inaccessible |
| I4 | GPU OOM | A100 80GB exhausted; batch too large |
| I5 | SLURM job failure | Job killed by scheduler / wall-clock / preemption |
| I6 | Cache corruption | Hashed cache key returns wrong tensor or invalid file |
| I7 | Cache invalidation miss | Spec SHA change does not invalidate stale cache |
| I8 | Numerical instability | NaN / Inf in loss, gradient, or prediction |
| I9 | Reproducibility break | Same seed + same code → different result |
| I10 | Cross-platform divergence | Mac local CPU result ≠ Explorer GPU result beyond numerical tolerance |
| I11 | CI / test infrastructure failure | Test suite passes locally but fails on CI (or vice versa) |
| I12 | MLflow / experiment registry loss | Logged experiments lost due to file corruption / disk full |

§3-§5 below specify detection + recovery per code.

### 1.3 The Critical Distinction

**F0-F7 are scientific outcomes.** Per Charter §10 P15: honest reporting is mandatory. F failures get documented + reported in publications.

**I1-I12 are engineering events.** They are debugged + fixed; they do not appear in publications except as "we encountered X during development, resolved by Y." Failure to detect I-codes early causes F-codes to be misattributed (e.g., I8 numerical instability mis-classified as F0 model-cannot-learn).

The two classes interact: an I-code can MASK an F-code (a NaN-producing implementation bug looks like F0); detecting and resolving I-codes is prerequisite to honest F-code classification.

---

## §2 Empirical Failure Modes F0-F7: L4.3 Operational Layer

### 2.1 F0 — Model Cannot Learn

**Decision 6 v2 hard termination trigger.**

**Detection:**
- V0 evaluator: training loss does not decrease over 100 epochs; OR validation AUROC < 0.55 across all 5 folds; OR per-fold variance < 0.01 (model produces constant prediction)
- Automated: V0-C4 check in L3.2 fails for all 4 substrates

**Recovery procedure:**
1. CSO inspects training curves + loss components
2. Verify L7 forward pass produces non-trivial gradients (L4.2 §3.4 overfitting sanity test)
3. Common causes: learning rate too low/high, loss function bug, label leak, frozen substrate
4. If architectural: revise L2.2; advance to Charter §3 termination review
5. **Per P16:** mark superseded L2.2 spec as `_SUPERSEDED_by_v3` and create v3

**Escalation:** CEO + CSO joint decision on whether F0 across all 4 substrates triggers Charter §3 termination review.

### 2.2 F1 — Cross-Resolution Mismatch (Bulk → scRNA-seq)

**Detection:** V3 evaluator inspecting bulk-trained model on single-cell or scRNA-seq evaluation; AUROC degrades > 0.10 vs same-modality V0/V1.

**Recovery:** Decision 3 v2 chemCPA bridge revision; revisit L2.2 §4 Slot 3 implementation; verify bulk → single-cell encoder pre-training.

**Escalation:** Soft termination per Decision 6 v2 if F1 is broadly present in V3; CEO + CSO joint revision.

### 2.3 F2 — Cross-Platform Batch Effect

**Detection:** V1 evaluator + IMPROVE workflow; CCLE → GDSC AUROC differs from GDSC → CCLE by > 0.10.

**Recovery:** Decision 2 v2 harmonization revision; scANVI / MrVI / Harmony comparison ablation at L7-fixed.

**Escalation:** Soft termination if F2 broadly present at V1.

### 2.4 F3 — Cross-Tissue Context Loss

**Detection:** V3 + V4 evaluator with per-cancer-type stratification; some cancer types underperform substantially (AUROC variance > 0.10 across cancer types).

**Recovery:** Tissue-specific covariate engineering; revisit L2.2 §6 PaSCient attention; spatial features (Phase F).

**Escalation:** Pass-with-reservations possible; document per-cancer-type performance honestly.

### 2.5 F4 — Cross-Species Transfer Break

**Detection:** N/A in Phase B (INTERCEPTA does not commit to mouse → human transfer in Phase B). If V6 includes mouse data, would be re-classified.

**Phase F scope:** EVA-60M mouse → human anti-TNF demonstration is Paradigm B-specific.

### 2.6 F5 — Drug Class OOD

**Detection:** L2.3 OODStack flags novel drug class predictions as epistemic OOD; threshold ≥ 70% epistemic on failed novel-class predictions per Decision 5 v2 Pass 4.

**Recovery:** Documented Layer 5 caveat — predictions on novel drug classes flagged as low-confidence; not used for clinical decision support.

**Escalation:** F5 is EXPECTED behavior, not a failure of the system; it is a failure of confidence-without-abstention. Per Decision 5 v2 + L2.3, abstention is the correct response.

### 2.7 F6 — Disease Class OOD

**Detection:** V6 evaluator. Per L3.2 V6-C5 BINDING: ≥ 70% of V6 failed predictions correctly attributed to epistemic OOD.

**Recovery:** If F6 detected AND OOD attribution adequate → expected behavior; document. If F6 detected AND OOD attribution inadequate (< 70% epistemic) → Decision 5 v2 hard termination check; OOD stack architecture revision required.

**Escalation:** Per Decision 8 v2 termination criteria — V6 failure across all paradigms (no paradigm achieves ≥ 0.65 on ≥ 2 therapeutic areas) triggers Charter §1.1 universality narrowing.

### 2.8 F7 — Patient Population Gap

**Detection:** V5 + V6 evaluator with demographic stratification; specific patient subpopulations underperform.

**Recovery:** Documented Layer 5 caveat — predictions on specific demographics flagged; broader training cohort (Phase F).

**Escalation:** Pass-with-reservations; demographic limitations honestly reported in publications.

### 2.9 F0-F7 Reporting Requirements (BINDING per Decision 8 v2 Commitment 4)

Every failed prediction in V0-V6 evaluations MUST be classified into F0-F7. CascadeReport.cross_level_reporting includes per-V-level F-code distribution. This is BINDING per Decision 6 v2 7-element mandatory reporting (element 6) + Decision 8 v2 Commitment 4.

---

## §3 Infrastructure Failure Modes I1-I12

### 3.1 I1 — Environment Drift

**Detection:**
- `conda env export` on Mac ≠ on Explorer (computed nightly)
- CI Mac runner produces different test results than Explorer
- Specific symptom: identical code + identical seed → different output

**Recovery:**
1. Pin exact versions in environment.yml (no `>=`, only `==` or `~=`)
2. Use conda-lock for fully-resolved lockfile
3. Document environment drift events in `~/INTERCEPTA/docs/operational/env_drift_log.md`

**Prevention:** L4.1 §2.2 Stage 1 deliverable 1.2 specifies pinned environment.yml + conda-lock as default.

**Escalation:** If drift recurs > 3 times during Stage 1-2, switch to container-based environment (Docker / Singularity).

### 3.2 I2 — Data Access Blocked

**Detection:**
- Dataset loader returns 404 / 403 / auth failure
- L3.3 §2.4 risk register lists AD + T2D as HIGH access risk

**Recovery:**
1. Identify alternative public mirror (Zenodo, FigShare, institutional repositories)
2. Use cached local copy if previously downloaded (cache-only mode)
3. If data is permanently inaccessible: trigger L3.3 §2.2 FALLBACK grid (UC + AD + RA)
4. If multiple V6 diseases inaccessible: soft terminate V6 per Decision 6 v2; Charter §1.1 scope narrowed

**Escalation:** CEO decision on whether to accept reduced V6 grid OR pursue data access agreement (institutional / pharma collaboration; Phase F-ish but may be pursued in Phase B Layer 5 if blocker).

### 3.3 I3 — Substrate Weight Download Fails

**Detection:** Hugging Face / scFoundation / UCE / scGPT weight URLs return failure; L2.1 substrate load_pretrained() fails.

**Recovery:**
1. Use authoritative mirror (Hugging Face official, original lab repos)
2. Cache weights locally on Explorer; redistribute via institutional storage
3. If specific FM permanently inaccessible: fall back to remaining FM family members (Decision 1 v2 substrate flexibility BINDING)

**Escalation:** If scFoundation inaccessible (likely default): switch default to UCE per L2.1 J4 alternative.

### 3.4 I4 — GPU OOM

**Detection:** PyTorch CUDA OutOfMemoryError; SLURM job exits with OOM signal.

**Recovery procedure:**
1. Reduce batch size (default 64 → 32 → 16)
2. Enable gradient accumulation (effective batch size preserved)
3. Enable activation checkpointing (memory-vs-compute trade-off)
4. For OOD KDE: use streaming computation (not full-matrix in memory)
5. For L2.4 Scale 5 EIG: use Captum's batch-attribution mode

**Prevention:** L4.2 §3.4 integration tests run at full V0 batch size to surface OOM early.

**Escalation:** Persistent OOM at minimal batch → request larger GPU (H100 80GB if available; AWS burst per Decision 9 v2 CEO-approved 5%).

### 3.5 I5 — SLURM Job Failure

**Detection:**
- SLURM exit code non-zero
- Job killed by wall-clock limit
- Preemption on shared cluster (rare on Explorer; common on AWS spot)
- Node hardware failure

**Recovery procedure:**
1. Per L4.1 §11.5 J10: auto-retry up to 3× with exponential backoff (1hr, 4hr, 16hr)
2. After 3 retries → alert CEO + CSO
3. Cache predictions written per-cell; partial progress preserved across job restarts
4. For wall-clock failures: increase --time= ceiling; for OOM: see I4

**Prevention:** L3.3 §5.2 SLURM array submissions include `--requeue` flag.

**Escalation:** Per-cell SLURM failures > 10% of V6 grid triggers cluster-team escalation at Northeastern.

### 3.6 I6 — Cache Corruption

**Detection:**
- Cache file exists but read fails (corrupt h5)
- Cached tensor shape mismatch with expected
- Cache key collision (different specs producing same key)

**Recovery procedure:**
1. Delete corrupt cache entry
2. Recompute from spec; re-cache
3. Validate hash key collision: include L2.x spec SHA in cache key (already specified in L4.1 §10.2)

**Prevention:** Cache write atomicity via temp-file + rename. h5 file integrity check on write completion.

**Escalation:** Repeated corruption (> 5 events) → switch from h5 to zarr (multi-file, more robust to partial writes).

### 3.7 I7 — Cache Invalidation Miss

**Detection:**
- L2.x spec changes; downstream cached results do NOT invalidate
- Symptom: changing L7 architecture produces same numbers as before (impossible if cache fresh)

**Recovery:**
1. Manual cache invalidation: `rm -rf /scratch/akula.pra/INTERCEPTA/embeddings/{substrate}/`
2. Fix cache-invalidation bug in `intercepta.data.cache`
3. Re-run affected stage

**Prevention:** L4.2 §2.5 reproducibility test: "spec SHA changes → cache invalidates → re-run produces different cache key." Failure of this test BLOCKS Stage 2 handoff.

**Escalation:** Cache-invalidation miss in production triggers spec-SHA audit of all prior cached results.

### 3.8 I8 — Numerical Instability

**Detection:**
- NaN / Inf in loss, gradient, prediction tensors
- Captum IG produces NaN attribution (common with hidden-state baseline)
- Bonferroni correction with raw_p = 0 → division-by-zero

**Recovery procedure:**
1. Check for division-by-zero, log-of-zero, sqrt-of-negative
2. Add epsilon to denominators (1e-8 standard)
3. Clip log inputs to [1e-10, ∞)
4. For Captum IG: switch to gradient-only baseline if hidden-state produces NaN
5. Add `torch.autograd.set_detect_anomaly(True)` during debugging

**Prevention:** L4.2 §5.3 edge case tests include all-zero predictions + all-same-prediction ensemble.

**Escalation:** Persistent I8 in a specific stage → architectural review of that stage's mathematical operations.

### 3.9 I9 — Reproducibility Break

**Detection:**
- L4.2 §2.5 reproducibility test fails: same seed → different result
- Common causes: non-deterministic CUDA ops; missing seed for new RNG source; multi-GPU training without `torch.manual_seed_all`

**Recovery procedure:**
1. Set `torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False`
2. Set `CUBLAS_WORKSPACE_CONFIG=:4096:8` env var
3. Use `torch.use_deterministic_algorithms(True)` (catches missed non-determinism)
4. Identify offending op; replace with deterministic alternative (often slower; accepted trade-off)

**Prevention:** Reproducibility test at every Stage 4-5 handoff per L4.2 §3.4 + §3.5.

**Escalation:** Persistent non-determinism in a specific op may force algorithmic change.

### 3.10 I10 — Cross-Platform Divergence

**Detection:**
- Mac local CPU result ≠ Explorer GPU result beyond float32 numerical tolerance (~1e-5)
- Symptom: CI passes on GitHub Actions; integration test fails on Explorer

**Recovery procedure:**
1. Inspect float32 vs float64 precision differences
2. Check for CPU-specific paths (MKL vs MPS on Mac; CUDA on Explorer)
3. Accept platform-specific tolerance: ≤ 1e-4 for full-stack tests; ≤ 1e-5 for unit tests
4. Reproducibility tests pin to one platform per test (GPU on Explorer for FM tests; CPU for substrate-agnostic tests)

**Prevention:** L4.2 §2.4 GPU tests run on Explorer nightly; CPU tests run on CI; platform-specific test paths marked.

### 3.11 I11 — CI / Test Infrastructure Failure

**Detection:**
- Test passes locally; fails on CI (or vice versa)
- CI workflow timeout
- Coverage report not generated

**Recovery procedure:**
1. Reproduce CI environment locally via container if possible
2. Check CI runner specs (vCPU count, memory) vs local
3. Mark flaky tests with `@pytest.mark.flaky(reruns=3)` only with CSO approval
4. Persistent CI-only failures → investigate CI environment drift (I1 special case)

**Prevention:** Pre-commit hooks ensure most failures caught locally before push.

### 3.12 I12 — MLflow / Experiment Registry Loss

**Detection:**
- MLflow database file missing / corrupt
- Logged experiments lost
- Cannot reconstruct Souza-Mehta matched-budget audit trail

**Recovery procedure:**
1. Daily backup of MLflow file backend to scratch (cron job from Stage 1)
2. Restore from latest backup; re-log lost runs from cache (if possible)
3. **If audit trail permanently lost:** per Charter §10 P15 BINDING — must be reported in publications; not silently re-run

**Prevention:** Daily MLflow backup is L4.1 §10.1 mandatory deliverable.

**Escalation:** Audit trail loss is publishable caveat per honest science principle.

---

## §4 Failure-Mode Detection Matrix

| Failure | Detection Source | Detection Latency | Severity |
|---|---|---|---|
| F0 | V0 evaluator | Stage 7 Day 1 | Hard term |
| F1 | V3 evaluator | Stage 7 V3 | Soft term |
| F2 | V1 evaluator | Stage 7 V1 | Soft term |
| F3 | V3/V4 per-cancer stratification | Stage 7 | Pass-with-reservations |
| F4 | V6 (Phase B N/A) | Phase F | N/A |
| F5 | OODStack | Stage 5+7 | Expected (abstain) |
| F6 | OODStack + V6 | Stage 8 | Per Decision 8 v2 termination |
| F7 | V5/V6 demographic strat | Stage 7+8 | Pass-with-reservations |
| I1 | CI + nightly env check | Daily | Block stage handoff |
| I2 | Data loader | Stage 2 onward | Block dependent V-level |
| I3 | Substrate load_pretrained() | Stage 3 | Block downstream stages |
| I4 | PyTorch CUDA OOM | Stage 3-8 | Recover via batch reduction |
| I5 | SLURM exit code | Stage 7-8 | Auto-retry 3× |
| I6 | Cache read failure | Any stage | Recompute from spec |
| I7 | Reproducibility test fail | Stage handoff | Block handoff until fixed |
| I8 | NaN/Inf detector | Stage 3-8 | Block computation; debug |
| I9 | Reproducibility test fail | Per stage handoff | Block handoff |
| I10 | Cross-platform CI / Explorer | Per stage handoff | Block handoff |
| I11 | CI workflow | Per push | Block merge |
| I12 | MLflow daily integrity check | Daily | Restore from backup |

---

## §5 Reporting Requirements (BINDING per Charter §10 P15)

### 5.1 F-Code Reporting

Every published INTERCEPTA result MUST include:
- Per-V-level F-code distribution of failed predictions
- Quantified failure rate per F-code
- OOD attribution rate for failed predictions (≥ 70% epistemic per Decision 5 v2 Pass 4 BINDING)
- For V6: 4-paradigm × F-code matrix per Decision 8 v2 Commitment 4

### 5.2 I-Code Reporting

I-codes typically NOT in publications (they are engineering artifacts), EXCEPT:
- **I12 (audit trail loss):** publishable caveat per honest science
- **I9 (reproducibility break) unresolved:** publishable caveat
- **I2 (data access blocked) causing reduced V6 grid:** publishable caveat documenting scope limitation

Per Charter §10 P15: dishonest engineering becomes dishonest science when it shapes reported results.

### 5.3 Operational Log

`~/INTERCEPTA/docs/operational/failure_log.md` records every I-code event with:
- Date / stage
- Detection mechanism
- Recovery action taken
- Time to resolution
- Lessons learned

Reviewed at Stage 7 + Stage 8 handoffs.

---

## §6 Recovery Procedure Pattern (Generic)

Per Charter v1.2 §10 P16 BINDING ("preserve past work via supersession"):

1. **Detect** — automated or CSO inspection
2. **Triage** — classify as F-code (scientific) or I-code (engineering)
3. **Preserve** — any prior spec / artifact / result that requires revision is marked `_SUPERSEDED_by_v{N+1}`
4. **Revise** — create new version of the affected artifact
5. **Re-run** — affected stage with new artifact
6. **Verify** — re-test per L4.2 stage handoff criteria
7. **Document** — failure log entry; if F-code, prepare publication caveat

This pattern is BINDING for every recovery procedure in §2-§3.

---

## §7 Cross-Cutting Recovery Principles

### 7.1 Cache First, Recompute Second

Always check whether the failure can be resolved by re-reading a valid cached artifact (L4.1 §10.2 cache pattern). Recompute only if cache invalid / corrupt / inaccessible.

### 7.2 Single-Substrate Failure Does Not Block Cascade

Per L4.1 §8.6 BINDING Souza-Mehta matched-pair: if 1 of 4 substrates fails at V0, the other 3 continue. The matched-pair report documents which substrate failed and at what stage.

### 7.3 Soft Terminations Are Not Pivots

Per Decision 6 v2 + Charter §3: soft termination triggers Decision revision (not vision narrowing). Only hard termination (V0 F0 across all substrates; V3 broadly < 0.65; V6 all paradigms < 0.55) triggers Charter §3 termination review.

### 7.4 Honest Reporting on All Failures

Per Charter §10 P15: every F-code event in publications; every material I-code event in operational log. No silent retries that hide failures.

### 7.5 Recovery Time Caps

If a single I-code event consumes > 1 wall-clock week without resolution: escalate to CEO; consider scope reduction or alternative path.

---

## §8 Pass Criteria for L4.3 LOCK

### 8.1 Coverage Pass Criteria (BINDING)

- **A1:** F0-F7 empirical failure taxonomy preserved from Decision 6 v2 + Decision 8 v2
- **A2:** I1-I12 infrastructure failure taxonomy enumerated with detection + recovery + escalation per code
- **A3:** Detection matrix §4 maps all 19 failure codes to detection source + latency + severity
- **A4:** Reporting requirements §5 BINDING per Charter §10 P15
- **A5:** Generic recovery procedure pattern §6 BINDING per Charter §10 P16

### 8.2 Cross-Decision Compatibility (BINDING)

- **X1:** L4.3 consumes Decision 6 v2 F0-F7 taxonomy; preserves verbatim
- **X2:** L4.3 consumes Decision 8 v2 Commitment 4 (failure-mode classification mandatory); §5.1 enforces
- **X3:** L4.3 consumes Charter v1.2 §3 termination + §10 P15 + P16; §6 recovery pattern BINDING
- **X4:** L4.3 consumes L4.1 stage handoff structure; per-stage failure mappings in §4
- **X5:** L4.3 consumes L4.2 test infrastructure; detection mechanisms reference test suite

### 8.3 Documentation Pass Criteria

- **D1:** Layer 4 of Phase B COMPLETE after L4.3 LOCK
- **D2:** Phase 8 audit consumes Layer 4 specs
- **D3:** Drift catalog this session: 0 new instances

### 8.4 CEO Sign-Off

L4.3 advances from PROPOSED to LOCKED when:
1. CEO reviews §2 F-code recovery procedures + §3 I-code recovery procedures + §5 reporting requirements
2. CEO confirms §11.5 J-items are within CSO authority
3. CEO co-signs Charter §5.3-style
4. Tag phase-b-l4.3-locked pushed to origin
5. **After L4.3 LOCK: Layer 4 of Phase B is COMPLETE.**

### 8.5 Critical Reminder

After L4.3 LOCK, the only remaining work before code is **Phase 8 Audit** — the pre-implementation coherence review that verifies all 10 Phase B Layer 2-4 specs compose into an internally consistent buildable system. This is the final gate before Stage 1 (Foundation) starts.

---

## §9 What L4.3 Does NOT Lock

- Specific monitoring tools (Layer 5 operational)
- Specific paging / alerting integrations (Layer 5)
- Phase F federation failure modes
- Regulatory failure reporting protocols (Phase F)
- Incident review meeting structure (operational culture)

---

## §10 Cross-Decision Implications

- **Charter v1.2 §3 (termination criteria) ↔ L4.3 §2 + §7.3:** termination decisions traceable to specific failure modes
- **Charter v1.2 §10 P15 (honest science) ↔ L4.3 §5:** reporting BINDING
- **Charter v1.2 §10 P16 (preserve past work) ↔ L4.3 §6:** _SUPERSEDED_ pattern BINDING
- **Decision 5 v2 Pass 4 ↔ L4.3 §2.7 (F6 + OOD attribution):** integration constraint
- **Decision 6 v2 (F0-F7 + hard/soft termination) ↔ L4.3 §2:** taxonomy preserved verbatim
- **Decision 8 v2 Commitment 4 ↔ L4.3 §2.9:** classification BINDING for publications
- **L4.1 (stages) ↔ L4.3 §4 detection matrix:** per-stage failure mappings
- **L4.2 (testing) ↔ L4.3 §3 detection:** test infrastructure detects most I-codes

---

## §11 Provenance and Appendix

### 11.1 Provenance

L4.3 written by Claude (CSO, 2026-05-11). Consumes Decisions 6 v2 + 8 v2; L4.1 + L4.2 specs; Charter v1.2 §3 + §10. After L4.3 LOCK, Layer 4 of Phase B is COMPLETE.

### 11.2 Discipline Check Per Charter v1.2 Principles

- **P3 (research before code):** ✅ failure modes specified before Layer 5 build encounters them
- **P15 (only honest science):** ✅ §5 reporting BINDING; §7.4 explicit
- **P16 (preserve past work):** ✅ §6 _SUPERSEDED_ pattern BINDING for all recovery
- **Charter §5.3:** ✅ §8 pass criteria explicit
- **Charter v1.2 §1.7 phase discipline:** ✅ Phase F items noted but not specified

### 11.3 Drift Catalog This Session

New drift instances introduced: 0.

### 11.4 Layer 4 Phase B Status

| Artifact | Status | Words |
|---|---|---|
| L4.1 Implementation Order | PROPOSED | 4,858 |
| L4.2 Testing | PROPOSED | 4,327 |
| **L4.3 Failure Modes** | **PROPOSED** | (this artifact) |

**After L4.3 LOCK: Layer 4 of Phase B is COMPLETE.**

### 11.5 CSO Judgment Items (Layer 5 Revisitable)

| # | Decision | Default | Alternatives | Revisit Trigger |
|---|---|---|---|---|
| J1 | Auto-retry count for SLURM | 3 | 5 (more) / 1 (less) | Per-cell empirical failure rate |
| J2 | Recovery time cap before CEO escalation | 1 week | 2 weeks | Operational tempo |
| J3 | I8 epsilon for divide-by-zero | 1e-8 | 1e-6 / 1e-10 | Numerical empirics |
| J4 | Cache invalidation policy | spec SHA based | timestamp based | If spec SHA volatile |
| J5 | MLflow backup frequency | daily | hourly / weekly | I12 frequency |
| J6 | Flaky test reruns | 3 max | 5 / 0 | Tier 2 Monte Carlo stability |
| J7 | Environment drift container fallback | only after 3 drift events | always Docker | Cluster Docker support |
| J8 | F-code classification by CSO or auto | CSO review | auto-classifier | Volume |
| J9 | Operational log review cadence | Stage 7 + Stage 8 handoff | weekly | Detection latency |
| J10 | Cross-platform numerical tolerance | 1e-4 system / 1e-5 unit | tighter / looser | Float precision empirics |

### 11.6 Honest Limitations (per Charter §10 P15 BINDING)

- **Failure modes will surface that L4.3 does not anticipate.** L4.3 catalogs the failures we can predict; real Layer 5 will produce novel failure modes. The operational log is the mechanism for capturing unanticipated failures.
- **I-code recovery procedures are best-effort.** A novel form of NaN may not match §3.8 standard remedies.
- **Cross-platform numerical tolerance is set by empirical observation, not theoretical bound.** Tightening or loosening is Layer 5 J10.
- **The detection matrix §4 assumes test suite catches I-codes early.** L4.2 test pyramid must hold up.
- **Auto-retry SLURM (3×) may mask transient cluster issues.** Cluster-team escalation threshold §3.5 is judgment-based.

### 11.7 Failure Mode Quick Reference

**F-codes (empirical, Decision 6 v2 + 8 v2 BINDING):**
F0 model-cannot-learn / F1 cross-resolution / F2 cross-platform / F3 cross-tissue / F4 cross-species (Phase F) / F5 drug-class-OOD / F6 disease-class-OOD / F7 patient-pop-gap

**I-codes (infrastructure, L4.3 BINDING):**
I1 env-drift / I2 data-blocked / I3 substrate-download / I4 GPU-OOM / I5 SLURM-fail / I6 cache-corrupt / I7 cache-invalidation-miss / I8 NaN-Inf / I9 reproducibility-break / I10 cross-platform-divergence / I11 CI-failure / I12 MLflow-loss

### 11.8 Key File Paths

- This spec: `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L4_3_Failure_Modes_Specification_2026-05-11.md`
- L4.1 (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L4_1_Implementation_Order_Specification_2026-05-11.md`
- L4.2 (predecessor): `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L4_2_Testing_Specification_2026-05-11.md`
- Failure log (future): `~/INTERCEPTA/docs/operational/failure_log.md`
- Operational dir (future): `~/INTERCEPTA/docs/operational/`

---

— L4.3 PROPOSED 2026-05-11 by Claude (CSO).
— Awaiting CEO co-sign and `phase-b-l4.3-locked` tag.
— **After L4.3 LOCK: Layer 4 of Phase B is COMPLETE.** Next: Phase 8 Audit (pre-implementation coherence review of all Phase B Layer 2-4 specs), then Layer 5 (CODE STARTS).
