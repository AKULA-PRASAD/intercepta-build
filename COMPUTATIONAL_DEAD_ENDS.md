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

### D2 — Novel-target / novel-chemotype AFFINITY via docking, QSAR, PCM, or co-folding. **CLOSED AT POWER (co-folding included, 2026-08-11).**
**Proof (code):** docking AUROC **0.428** (`HIT2`); QSAR novel-chemotype **0.90→0.67** (`HIT1`); PCM protein
features add nothing (`B49`); active-learning collapses on novel chemistry (`B65`). **Co-folding now settled at
power (`AFFINITY2`, reproduced ×2, sha 8e3ac05):** Boltz-2 on a leakage-controlled ECFP-Tanimoto<0.40 novel
split, 522 complexes across 3 LIT-PCBA targets — zero-data TIER1 passes only **1/3** (FEN1 CI-lo 0.630; PKM2
0.594 misses; ALDH1 0.483), and co-folding is **significantly WORSE than a target-trained QSAR** on 2/3
(ALDH1 Δ−0.161 CI[−0.24,−0.08]; FEN1 Δ−0.178 CI[−0.27,−0.09]; PKM2 Δ−0.090 ns). The earlier AFFINITY1 novel-
split n=5≈0.52 was underpowered; AFFINITY2 is the powered closure. **Leakage cuts in the negative's favor:**
target-side (receptors predate Boltz cutoff) + compound-side (actives likely in Boltz's ChEMBL/BindingDB
training) would only INFLATE co-folding, which failed anyway. **Why:** all methods are interpolation within a
similarity/training manifold; the novel split is at/below chance. **Reopen only if:** a genuinely new
method/data class beats this same leakage-controlled powered gate. Co-folding is now a proven money-pit too.

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

### D9 — DURABILITY via masked-PLM entropy at drug-contact / resistance sites. **CLOSED (falsified at scale, 2026-08-10).**
**Proof (code, reproduced ×2, sha `caea6b90`):** DYNAMICS5 tested the DYNAMICS1 premise at power — n=198 targets,
1,143 CARD-documented resistance positions, within-protein paired design. Resistance sites are **not** higher-
entropy than matched controls: one-sided Wilcoxon p=**0.99997** (opposite direction), mean ΔH=**−0.22**,
positive-fraction **0.41**, position-level AUROC **0.446** (below chance), clustered-perm p=**1.0**; verdict
**CEILING** (`experiments/DYNAMICS5_resistance_site_entropy/results/DYNAMICS5_metrics.json`). **Why:** DYNAMICS1's
n=15 AUROC 0.84 was a small-n artifact; the signal is absent (or slightly reversed — resistance sites tend to be
functionally important/conserved, i.e., lower tolerance). **This closes the durability-entropy axis** (previously
mis-ranked as roadmap R1). Reopen ONLY with a different, powered observable (FEP/MD ΔΔG or measured DMS fitness).
**Both reopen-triggers investigated 2026-08-11 (DMS1, feasibility verdict) → still gated, gate now precise:**
FEP/MD ΔΔG has no drug-matched fragile-vs-durable structures (durable targets are undrugged) + is relay-fragile;
measured DMS fitness exists only for resistance ENZYMES (TEM-1 β-lactamase/AAC/DHFR — CARD homolog models, 0
resistance-SNP positions), while the CARD-labelled drug targets (gyrA/rpoB/…) have no DMS — observable and label
are on DISJOINT proteins. The true gate is a **missing dataset pairing per-position fitness with resistance
labels on the same drug-target panel** (data-acquisition/wet-lab), not more computation
(`experiments/DMS1_measured_durability/FINDING.md`).
