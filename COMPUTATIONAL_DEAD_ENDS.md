# COMPUTATIONAL_DEAD_ENDS.md
*Directions that should receive **no more compute**, with code-cited proof. "Dead" = the repo has
demonstrated the signal is absent or bounded on today's public data, so additional GPU-hours cannot change
the conclusion. Reopen a line ONLY if the specified new information appears (each entry states the trigger).*

### D1 — A label-free, homology-independent NON-METABOLIC mechanism signal. **CLOSED.**
**Proof (code):** own-conservation-breadth AUROC **0.9078**; six signal classes fail the +0.03 gate —
NONMET1 Δ+0.021, PLMESS1 Δ+0.0082, REGNET1 Δ**−0.0056**, MULTISIG1 ensemble ~0.908, PLMSTRUCT1 (structure-
aware) Δ+0.008 (`experiments/{NONMET1,PLMESS1,REGNET1,MULTISIG1,PLMSTRUCT1}/results/*.json`).
**Why permanent:** without labels, the only transferable signal *is* conservation; there is no residual for a
new label-free CPU signal to capture. **Reopen only if:** curated mechanism *labels* or a fundamentally new
data modality (not another sequence/graph transform) becomes available.

### D2 — Novel-target / novel-chemotype AFFINITY via docking, QSAR, PCM, or co-folding on current benchmarks. **CLOSED (gated).**
**Proof (code):** docking AUROC **0.428** (`HIT2`); QSAR novel-chemotype **0.90→0.67** (`HIT1`); PCM protein
features add nothing (`B49`); active-learning collapses on novel chemistry (`B65`); Boltz-2 co-folding was
**training-leaked** and **novel-split n=5 ≈ 0.52** (`AFFINITY1/results/scored.csv` + `LEAKAGE_AUDIT.md`).
**Why:** all are interpolation within a similarity/training manifold; the novel split — the only thing that
matters for the vision — is chance. **Reopen only if:** the OOD testbed (roadmap R2) shows a method beating
the wall on a *leakage-controlled* novel-target split. Not before — this is a proven money-pit.

### D3 — Single-agent human DRUG-RESPONSE from baseline molecular profiles. **CLOSED.**
**Proof:** cross-dataset ceiling ρ**+0.212**; within-cancer clinical AUROC **0.504** (p=0.43); inferred
functional layer **fails external replication** (`ENG §2.1/2.7/2.8`; six-front, `STATE_OF_THE_VISION.md`).
**Why permanent:** the drug-specific-response information is **not in baseline profiles** — an information
limit, not a modeling limit. **Reopen only if:** *measured functional/perturbation* response data in the
relevant system becomes available (that is experimental data, outside the compute-only scope).

### D4 — More disease-class BREADTH arms / more router coverage / re-benchmarking the achievable core. **STOP.**
**Proof:** the program's own record — "CPU-arm expansion ≈ 0 marginal value"; `STATE_OF_THE_VISION.md`:
"re-litigating a settled question… the same hypothesis in new clothes, returning the same answer."
**Why:** adds documentation, not information toward the vision.

### D5 — Molecule GENERATION (de-novo / scaffold-hop) without a validated novel-target scorer. **STOP.**
**Proof:** generator below SOTA (`B52`); and there is **no validated novel-target scoring function to optimize
against** (D2). Generating molecules you cannot rank is motion, not progress. Note: prior "de novo molecules"
were **scaffold-hopped analogues, relabeled** (`INTEGRITY_SWEEP.md`). **Reopen only if:** D2's gate opens.

### D6 — Structural REPURPOSING for coverage expansion. **CLOSED.**
**Proof:** apparent gain is a promiscuity artifact — 18/32 vs a random null of 25/32; honest novel-target
coverage stays **1/32** (`STRUCTREPURPOSE1`, `LEDGER:63`). **Why:** the "signal" is decoy-set structure, not biology.

### D7 — ipTM / interface-confidence as an AFFINITY proxy. **CLOSED.**
**Proof:** ipTM saturates (~0.95 for actives *and* inactives) on the Mac-MPS pilot (`AFFINITY_IPTM1/CPU_IPTM_FINDING.md`);
strictly weaker than the trained affinity head, which is itself D2-bounded.

### D8 — Re-running program-level AUDITS / re-deriving the same verdict. **STOP (meta-dead-end).**
**Proof:** the verdict is stable across repeated audits and is gated on evidence not in the repo; re-auditing
is the D3-class loop applied to the review itself. **One audit is enough; the missing input is data.**

---
**Net:** compute belongs ONLY in roadmap R1–R4 (and R5 *iff* R2's alarm fires). Every direction above is either
information-limited (no signal exists to find) or interpolation-bounded (only novel-split performance matters,
and it is chance) — additional GPU-hours are, with proof, wasted there.
