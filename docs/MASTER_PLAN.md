# INTERCEPTA — MASTER PLAN (end-to-end, first-principles → fullest vision, with A→Z contingencies)

*The single connected map: where the vision starts, where it ends, every stage between, what to do / what NOT to do /
what's next at each — and for every critical objective a contingency chain (Plan A→B→C…) each triggered by a
**pre-registered failure signal**, so we always know WHICH thing is failing and WHY before moving to the fallback. Grounded
only in committed evidence (LEDGER.md, experiments/*, the Phase-1 audit, the contribution audit). Honest tiers throughout:
BUILT · PARTIAL · CLOSED(negative) · OPEN(unsolved science) · GPU-GATED · DATA-GATED · EXPERIMENT-GATED. No vision inflation;
gated/open frontiers are named, not pretended solved. Last updated 2026-08-08.*

---

## 0. How to read this
- **§1** end state + honest current position. **§2** the 7-stage end-to-end pipeline (the spine). **§3** the ordered master
  sequence (phases). **§4** the A→Z contingency tree (the heart of the ask). **§5** the closed-door register (what NOT to do).
  **§6** the resource-gate map. **§7** operating discipline (why it's non-random). **§8** critical path + immediate next.
- **The rule that makes it non-random:** every objective has a *pre-registered gate*; failing the gate is the *detection
  signal* that triggers the pre-planned fallback. We do not improvise fallbacks; they are written here in advance.

---

## 1. The end state, and the honest current position
**Fullest vision (end state):** a computational system that, from minimal data, reasons to the best therapeutic
intervention for **any** disease — including never-seen ones — rigorously and honestly.

**Honest current position (from the two audits, evidence-cited):**
- **~20–25%** of the *fullest computational vision* (Phase-1 audit): deep in ONE scientific domain (metabolic-essentiality
  target-ID) + validation methodology; shallow/off-the-shelf in structure & ML; near-empty in the molecule/intervention
  half, systems-biology breadth, simulation/dynamics, foundation-model reasoning, causal modeling.
- **~3/10** real-world contribution today (contribution audit): a rigorous, reproducible, honest **map of where zero-data
  target-ID works and fails**, well-controlled **negatives**, and a fail-safe abstaining engine — no lab-validated target,
  no drug, no capability the field lacks.
- **Two phases (do not mix):** Phase 1 = the strongest computational platform (no wet-lab). Phase 2 = real-world validation
  (wet-lab, collaborators, clinical). We are in Phase 1.

---

## 2. The end-to-end pipeline (the connected spine — 7 stages)
*Each stage: what it is · status · the transfer-condition (when its signal is trustworthy) · what feeds it / what it feeds.*

**S0 — INPUT & representation.** Accept a disease as a genome / causal gene / phenotype / screen.
- Status: **PARTIAL.** genome ✓ (pathogens), causal gene ✓ (MENDEL1), GWAS ✓ (GENETICS1), phenotype→gene ✓ retrieval
  (PHENO1), dependency screen ✓ (DEPEND1). Missing: raw phenotype→de-novo mechanism (OPEN); imaging/EHR/multi-omics input.
- Feeds → S1/S2 via the autonomous class detector (ROUTERAUTO1).

**S1 — MECHANISM understanding.** Infer the biology that makes a node matter.
- Status: **metabolic BUILT** (FBA, validated VAL-ESS/CROSSVAL/BLIND1–7); **non-metabolic DEFINITIVELY CLOSED** — 4 signal
  classes each failed (MET4 PPI, NONMET1 synteny, REGNET1 regulatory, PLMESS1 PLM-embedding) AND their ensemble upper-bound
  failed (MULTISIG1); conservation-breadth (0.908) is the accepted ceiling. **regulatory/signaling/dynamic/whole-cell = MISSING/OPEN.**
- Transfer-condition: FBA transfers where the GEM encodes genuine biosynthetic dependence (fails on host-scavengers, sparse
  GEMs; META1/FAIRGATE bound it).

**S2 — TARGET identification.** Which protein/node to intervene on.
- Status: **BUILT (narrow-but-validated).** essentiality (FBA), conservation-breadth (the non-metabolic workhorse, AUROC
  0.91), structural class-ID (viruses, GENERALIZE2/3), functional dependency (cancer, DEPEND1), genetics (complex, GENETICS1),
  causal-gene (monogenic, MENDEL1). Silent-failure on phylogenetically-isolated organisms (TID4) is a known limit.

**S3 — PRIORITIZATION, SAFETY, EXPERIMENT-DESIGN.** Rank, filter unsafe, decide what to test.
- Status: **BUILT.** multi-axis best-intervention (BESTINT1), hard host-non-homology safety filter (FRONT1/E2E2),
  resistance/condition-robustness, calibrated confidence (CALIB1), VOI experiment-prioritization (EXPDESIGN1, ~8× wet-lab
  efficiency). Honest bound: durability from WHOLE-PROTEIN static biology = CLOSED (AMR1) — but drug-CONTACT-residue DYNAMICS
  gives a first signal (DYNAMICS1, AUROC 0.84, n-fragile); OOD abstention guarantee
  degrades (CONFORMAL1: 94%→55%).

**S4 — INTERVENTION design.** Target → therapy.
- Status: **PARTIAL/mostly-unbuilt (the weak half).** modality triage ✓ (MODALITY1, fail-safe), repurposing ✓-narrow
  (INTERVENE1/2, ~1–7% coverage), ADMET ✓ (B30), synthesizability ✓ (B31), generation ✓-standalone (B33). **Novel-target
  binding affinity** — standard tools FAIL (docking≈chance HIT2; QSAR analog-bound HIT1; PCM null B49; active-learning null
  B65); co-folding (Boltz-2) is the credible SOTA but is **GPU-gated even at small-candidate scale** (empirically confirmed
  2026-08-09: a CPU pilot on ~20 candidates produced 0/20 in ~48 min and was stopped — the affinity head's diffusion sampling
  is the expensive part; an earlier "CPU-feasible small-candidate" reframe was tested and RETRACTED). Structural repurposing = CLOSED (promiscuity, STRUCTREPURPOSE1).

**S5 — VALIDATION.** In-silico confidence → wet-lab → clinical.
- Status: in-silico ✓ (reproduced ×2, blind protocol); **wet-lab = EXPERIMENT-GATED** (CRISPRIDESIGN1 turnkey design ready,
  needs a lab); **clinical = EXPERIMENT-GATED + tested-negative** for response prediction (B10/B20).

**S6 — INTEGRATION & GOVERNANCE.** Route, abstain, calibrate, reproduce.
- Status: **BUILT.** composite router + transfer-condition gating + abstention (COMPOSITE1–4), autonomous class detection
  (ROUTERAUTO1), end-to-end integration proof (CAPSTONE2, fail-safe), verdict-stable reproducibility. The program's genuine
  strength alongside methodology.

---

## 3. The master sequence (ordered by leverage; what-to-do / what-NOT / next)
**WAVE 1 — CPU-feasible Phase-1 inventions (do now, no new resources).** Ordered by leverage:
1. PLMESS1 (DONE → 4th closure) + MULTISIG1 (DONE → the ensemble-ceiling closure). The non-metabolic-mechanism question is
   now **definitively closed** (individually and combined); conservation-breadth (0.908) is the accepted ceiling.
2. Uncertainty productionization — ship class-conditional (Mondrian) conformal into the engine (CONFORMAL1 showed marginal
   is vacuous for targets); genuine, honest, closes a real hole (NOTE: CONFORMAL1 also showed it degrades OOD — productionize
   with the OOD-widening rule, §19).
3. Knowledge-integration — a calibrated multi-signal posterior with honest joint uncertainty (careful: MULTISIG1 already
   showed the non-metabolic signal-union is collinear with conservation, so gains here are modest by construction).
- **What NOT to do in Wave 1:** any further non-metabolic-mechanism attempt — CLOSED individually (4 signals) AND at the
  ensemble upper-bound (MULTISIG1); more shallow disease-class coverage arms (diminishing-returns); anything requiring GPU
  dressed up as CPU.

**WAVE 2 — GPU-gated Phase-1 (the biggest % of the remaining vision; needs a GPU — a resource decision).** In priority:
1. Zero-shot affinity via co-folding (Boltz-2) — the 14-weight intervention half; spec ready (AFFINITY1 GPU_BENCHMARK_SPEC).
2. Foundation-model mechanism reasoning for the non-metabolic half (only if PLMESS1/embeddings hint signal).
3. MD / dynamics (resistance evolvability — the AMR1 follow-on; PK/PD).

**WAVE 3 — DATA-gated Phase-1.** Curated eukaryote GEMs (lift the blind-eukaryote fails); a genome-wide P. falciparum CRISPR
screen (resolves the parasite confound); larger curated regulatory/interaction networks (only if a fresh signal-class warrants).

**PHASE 2 — real-world (only after Phase-1 is genuinely mature; per the sequencing directive).** Wet-lab CRISPRi of a
nominated target (CRISPRIDESIGN1) → collaborator; then prospective novel-pathogen test; then clinical.

**PARALLEL CHANNEL — dissemination.** Publish the *validated core + negative map* (the genuine ~3/10 contribution) at a
methods/reproducibility venue; it does not require Phase-1 completion and delivers the real value to the world. Framing fixes
from the red-team (ANTICIPATED_REVIEWS.md) applied first (soften "prospective-blind"/"law"; wall off post-hoc).

---

## 4. THE CONTINGENCY TREE — Plan A→Z per critical objective, each with its FAILURE-DETECTION signal
*Format: **A** primary → *[detection: the pre-registered signal that proves A failed]* → **B** fallback → … → **terminal
honest fallback** (accept the bound / route to experiment / abstain). We move A→B without pause, but only after the detection
signal fires — never on a hunch.*

### O1 — Accept ANY disease as input
- **A:** genome/gene/GWAS/screen/phenotype inputs via the autonomous detector. *[detection: detector mis-routes or
  over-fires on a class — caught by the CAPSTONE2 fail-safe test / 93 unit tests.]*
- **B:** if a new input type has no validated route → **ABSTAIN with an explicit "unsupported input" flag** (never guess).
- **Terminal:** raw-phenotype→de-novo-mechanism is **OPEN** — we honestly restrict to retrieval over known maps (PHENO1),
  not de-novo inference. Do NOT fake de-novo inference.

### O2 — Infer NON-METABOLIC mechanism (the #1 core gap)
- **A:** FBA metabolic essentiality. *[status: BUILT + validated for the metabolic half.]*
- **B:** PPI-network centrality (MET4). *[detection: lift collapses under a study-bias control (+0.128→−0.004) → FAILED.]*
- **C:** conserved genomic context / synteny (NONMET1). *[detection: ΔAUROC-beyond-conservation +0.016 < +0.03 gate → FAILED.]*
- **D:** curated regulatory master-regulator influence (REGNET1). *[detection: OR 0.52, ΔAUROC −0.006 → FAILED, clean null.]*
- **E:** learned PLM (ESM-2) embeddings (PLMESS1). *[detection: ΔAUROC-beyond-conservation +0.008 <+0.03; study-bias-ctrl
  −0.0006 → **FAILED** 2026-08-08, reproduced, baseline consistency-checked vs NONMET1.]*
- **F (the ENSEMBLE upper-bound, not a new signal):** combine all four signals (MULTISIG1). *[detection: full-ensemble
  ΔAUROC-beyond-conservation +0.019 logistic / +0.009 GBM <+0.03; drop-one ablation — no signal clears; embedding not the
  driver → **FAILED** 2026-08-08, reproduced (sha e6badcb7).]* This is the honest way to close the question definitively
  without a random 5th *new signal*: test the best-case COMBINATION.
- **Terminal honest fallback — NOW ACTIVE & DEFINITIVE (E and F both failed):** the non-metabolic mechanism is closed
  **both individually (4 signal classes) AND at the ensemble upper-bound (MULTISIG1)** — a decisive scientific bound.
  **Conservation breadth (AUROC 0.908) is the accepted, unbeatable ceiling** for the non-metabolic half. The ONLY untested
  lever is a larger/structure-aware PLM or mechanism data (GPU/DATA-gated, Wave-2/3). **No further CPU attempts** — the
  objective is completed and closed, not open.

### O3 — Identify a TARGET for a novel organism/disease
- **A:** the class-matched validated signal (FBA/dependency/genetics/structure) at earned confidence. *[detection: the signal's
  pre-registered gate (OR>3/RR-fair, etc.) fails on the class.]*
- **B:** if the primary signal is out-of-domain → fire the supporting signal (conservation-breadth + host-safety).
- **C:** if none transfers (dark proteome / novel zero-screen parasite) → **ABSTAIN** (DARK1/TRANSFER1 proven fail-safe).
- **Terminal:** abstention is a valid answer — "no trustworthy target from computation alone; needs experimental data."

### O4 — Prioritize + guarantee SAFETY + spend experiments well
- **A:** hard host-non-homology safety filter + multi-axis score + VOI experiment-prioritization (EXPDESIGN1). *[detection:
  a host-toxic target reaches the shortlist — caught by the hard filter's construction test.]*
- **B (durability):** predict resistance-liability. **A** = whole-protein static biology (AMR1) *[detection: AUROC 0.556 →
  FAILED]* → **B** = drug-CONTACT-residue DYNAMICS (DYNAMICS1, ESM entropy at contact residues) *[AUROC 0.839, MWU p 0.029,
  beats AMR1; **PARTIAL PASS** 2026-08-08 — but n-FRAGILE (n=15; subset p 0.05–0.12), a demonstration not a validated
  predictor]* → **C** = larger target set / fitness-scan / experimental confirmation (DATA/EXPERIMENT-gated) to firm up n.
- **B (abstention trust):** conformal confidence. *[detection: CONFORMAL1 — OOD essential-class coverage 55% ≪ 90%.]*
  → fallback: **make OOD abstention more conservative** / report confidence as not-guaranteed-out-of-distribution (do not
  claim nominal coverage on a novel organism).

### O5 — Choose the intervention MODALITY
- **A:** mechanism×localization fail-safe recommender (MODALITY1). *[detection: an infeasible modality is recommended —
  caught by the hard fail-safe (0/43).]*
- **B:** where features are absent or the class is out of MODALITY1's validated (human-disease) scope → **ABSTAIN** (pathogen
  modality currently abstains — honest).
- **Terminal:** modality is a CLASS recommendation, never a molecule; the molecule is O6.

### O6 — Produce a real INTERVENTION for the target (the hardest objective)
- **A:** repurpose an existing drug (INTERVENE1/2). *[detection: novel-target coverage ceiling — ~1/32; measured.]*
- **B:** structural repurposing to expand coverage (STRUCTREPURPOSE1). *[detection: gain is a promiscuity artifact under a
  null → FAILED.]*
- **C:** zero-shot binding-affinity ranking for a novel target — docking (HIT2), QSAR (HIT1), PCM (B49), active-learning
  (B65). *[detection: each ≈ chance / null on the pre-registered gate → all FAILED on CPU.]*
- **D:** **co-folding (Boltz-2) affinity — GPU-GATED even at small-candidate scale (EMPIRICALLY CONFIRMED 2026-08-09).**
  A prior deep-analysis note claimed this was CPU-feasible for ~20-candidate ranking (~3 h); I RAN it and that claim was
  WRONG — the CPU pilot produced **0/20 predictions in ~48 min wall / ~90 min CPU** and was stopped as impractical. Root
  cause: my ~10 min/complex figure was AFFINITY1's *structure-only* time; the **affinity head adds many diffusion samples**,
  pushing per-complex CPU time to tens of minutes–hours → even ~20 complexes don't finish in a session. So the reframe is
  RETRACTED: affinity co-folding needs a GPU. *[detection stays the GPU benchmark: AUROC ≥0.60 AND > 0.4285 AND
  novel-vs-inactive ≥0.60. See experiments/AFFINITY1_cofolding_zeroshot/CPU_PILOT_FINDING.md.]*
- **E:** physics-based (MM-GBSA / FEP-lite) rescoring — GPU/compute-gated.
- **Terminal honest fallback:** if D/E fail or stay unavailable → **novel-target affinity is OPEN science**; route the
  validated target to **experimental screening** (Phase 2) rather than emit a fake potency-ranked lead. NEVER present a
  pose-plausible hypothesis as a validated lead.

### O7 — VALIDATE in reality (cross from Phase 1 to Phase 2)
- **A:** wet-lab CRISPRi knockdown of a nominated target (CRISPRIDESIGN1 turnkey). *[detection: growth defect ≥5× vs control
  → confirmed; <5× → the prediction is WRONG (first-class negative) → recalibrate the signal that nominated it.]*
- **B:** if no lab/collaborator → the collaboration ask + turnkey protocol + the preprint are the instruments to GET one
  (a professor, a course, a neglected-disease effort). *[detection: no partner after outreach → escalate channels.]*
- **C:** cheaper variant — MIC of a commercial pathway inhibitor vs the organism (if a drugged target).
- **Terminal:** until a wet-lab result exists, all target/molecule outputs remain **pre-registered hypotheses** — stated as
  such, never as validated.

### O8 — INTEGRATE + govern "any disease"
- **A:** composite router fires validated signals per class, abstains otherwise (CAPSTONE2). *[detection: a mis-fire or a
  verdict-skeleton drift — caught by the pre-registered CAPSTONE2 gate + regression tests.]*
- **B:** new validated arm → add additively (verdict-stable); unvalidated → abstain. *Do NOT expand coverage without a
  passing validation.*

### O9 — DISSEMINATE (deliver the real contribution)
- **A:** publish the validated core + negative map (methods/repro venue) + preprint. *[detection: reviewer novelty
  objection — pre-empted by ANTICIPATED_REVIEWS.md; framing fixes applied first.]*
- **B:** if the flagship is judged insufficiently novel → reframe as a negative-results / reproducibility paper (its genuine
  strength) rather than a discovery paper. *Do NOT inflate to force a discovery framing.*
- **C:** collaboration outreach in parallel (the wet-lab ask is the lever above 3/10).

---

## 5. The CLOSED-DOOR / ANTI-PATTERN register (what NOT to do — with evidence)
1. **Do NOT re-attack the non-metabolic mechanism** — CLOSED individually across 4 signal classes (MET4/NONMET1/REGNET1/
   PLMESS1) AND at the ensemble upper-bound (MULTISIG1) — accept the conservation ceiling (0.908); the next move there is
   GPU (structure-aware PLM) or experimental data, not another CPU signal or combination.
2. **Do NOT use docking/QSAR/PCM to claim novel-target potency** (HIT2/HIT1/B49/B65 negatives).
3. **Do NOT predict patient drug-RESPONSE from baseline profiles** (B10/B20 tested-negative).
4. **Do NOT rank targets by conservation as if safe** (FRONT1: most-conserved = host-toxic); use the hard host-non-homology filter.
5. **Do NOT use structural repurposing for coverage gain** (STRUCTREPURPOSE1 promiscuity).
6. **Do NOT predict resistance-liability from WHOLE-PROTEIN static biology** (AMR1 null) — use drug-CONTACT-residue DYNAMICS
   (DYNAMICS1: AUROC 0.84, beats AMR1; n-fragile, treat as a demonstration pending larger-n/experimental confirmation).
7. **Do NOT trust a marginal/OOD abstention guarantee at nominal rate on a novel organism** (CONFORMAL1: 94%→55%).
8. **Do NOT spawn shallow coverage arms or run GPU-work on CPU or overclaim** (audits).
9. **Do NOT do random trial-and-error** — every step pre-registered with a failure signal (this document).

---

## 6. Resource-gate map (so we always know WHY something is blocked)
- **CPU-now (do autonomously):** Wave-1 items; the parallel publication prep.
- **GPU-gated (resource decision — the single highest-leverage unlock, the 14-weight intervention half):** co-folding
  affinity (AFFINITY1 spec), foundation-model reasoning, MD/dynamics.
- **DATA-gated:** curated eukaryote GEMs; a Pf CRISPR screen; larger curated networks. (Fetchable open data is NOT gated —
  proven by autonomously sourcing the Abasy GRN for REGNET1.)
- **EXPERIMENT-gated (Phase 2, needs a person + a bench):** wet-lab validation, clinical.

---

## 7. Operating discipline (why this plan is non-random)
Pre-register every gate before running · reproduce ×2 byte-identical · control nulls/leakage/study-bias · report negatives
first-class · honest tiers · abstention-integrity over coverage · **each objective's failure-detection signal is written in
advance (§4), and the fallback is pre-planned — we never improvise the next move.** A negative is a completed step (it closes
a door and redirects resource), not a failure to hide.

---

## 8. Critical path & immediate next actions
- **NOW (CPU, autonomous):** the non-metabolic mechanism line is DEFINITIVELY CLOSED (PLMESS1 4th closure + MULTISIG1
  ensemble-ceiling closure, both verified/reproduced). Remaining CPU-buildable = modest ENGINEERING only (uncertainty
  productionization, knowledge-graph integration); the high-value CPU frontier is exhausted.
- **THE ONE RESOURCE THAT MOVES THE % MOST:** a **GPU** → unlocks the intervention half (O6-D) — the biggest single chunk of
  the remaining ~75–80%. Name it; do not fake around it.
- **THE ONE THING THAT MOVES REAL-WORLD CONTRIBUTION MOST (Phase 2):** one **wet-lab CRISPRi test** (O7-A) — converts the
  whole in-silico edifice to confirmed; needs a collaborator (O7-B / O9-C).
- **PARALLEL:** publish the validated core + negatives (O9-A) — delivers the genuine contribution now.

---

## 9. Definition of done + honest completion
- **Phase-1 computational done** when: every reachable disease class is covered-or-honestly-abstaining; both halves are
  built-or-honestly-bounded; integration is proven end-to-end; every wall is characterized; and the GPU/data-gated items are
  either done (given resources) or precisely specced. **Current: ~20–25% of the fullest computational vision** (audit).
- **Phase-2 real-world done** when: ≥1 nominated target is wet-lab-confirmed; a collaborator reproduces; and — the far end —
  a validated intervention. **Current: 0% (no wet-lab).**
- The honest end state we can reach on CPU + open data alone is a **rigorous, validated, honest ~one-fifth computational
  platform + a decisive negative map** — everything beyond needs GPU, data, or a bench. This plan names exactly which, and
  what to do when each is unblocked or each Plan-A fails.

---

# PART II — the deeper connective layers (dependency DAG · invention/engineering/acquisition · combination matrix · state machine)

## 10. The dependency DAG (what unlocks what — the true connected critical path)
*Objectives/builds as nodes; "→" = enables/unlocks. This is the connective tissue: it shows the LONGEST POLES, not just a list.*

```
S0 input+autodetect ─┬─> S2 target-ID ─> S3 prioritize/safety ─> S5(in-silico confidence) ─┐
 (BUILT)             │      (BUILT)           (BUILT)                                        │
 S1 mechanism ───────┘                                                                       │
  ├ metabolic FBA (BUILT) ─────────────────────────────────────────────────> feeds S2       │
  └ non-metabolic (CLOSED: 4 signals + ensemble MULTISIG1) ──X (conservation-breadth is the ceiling)  │
                                                                                             v
S4 intervention:  modality (BUILT) ─> repurpose (narrow) ──X coverage ceiling            S6 governance
                                       └> NOVEL-TARGET AFFINITY  ==[GPU-GATE]==> co-folding  (BUILT: router,
                                          (OPEN on CPU; the 14-weight half)     /physics       abstain, CAPSTONE2)
                                                                                   │
S7 VALIDATION: in-silico ─────────────────────────────==[WET-LAB GATE]==> CRISPRi test ─> prospective ─> clinical
O9 DISSEMINATION: publish validated core+negatives  (PARALLEL — blocks nothing, delivers the real ~3/10 now)
```
**Longest poles (the two gates that gate everything downstream):**
1. **GPU gate** → unlocks novel-target affinity (O6-D) → the entire **intervention half** (14 weight) → real molecule
   outputs → meaningful molecule-side Phase-2. *Nothing on the molecule side moves without it.*
2. **Wet-lab gate** → unlocks O7 → converts the whole in-silico edifice to **confirmed** → the ~3/10→higher real-world jump
   → prospective → clinical. *Nothing real-world moves without it.*
**Everything else is either already BUILT (left of the gates) or a modest CPU deepening that does not cross a gate.** So the
connected truth: **two acquisitions (a GPU, a bench) are the critical path to the fullest vision — not more CPU experiments.**

## 11. Invention vs Engineering vs Acquisition (honest tagging — "every step an invention" is NOT literally true)
*The directive says "every step a genuine invention." Truth-over-vision requires I disagree precisely: the remaining steps
split three ways, and the biggest %-movers are ACQUISITIONS, not inventions. Pretending otherwise would be a false claim.*

- **GENUINE INVENTIONS still required (open science — nobody has solved these; do NOT fake):** (a) zero-shot novel-target
  binding-affinity ranking (O6 — the field's open wall); (b) de-novo mechanism inference from a raw phenotype (O1 deep case);
  (c) causal disease modeling. (Resistance-evolvability dynamics — formerly on this list — is now PARTIALLY BUILT: DYNAMICS1
  gave a first contact-residue durability signal, AUROC 0.84 n-fragile; firming it up is DATA/EXPERIMENT-gated, not a new
  CPU invention.) These are where "invention/novelty" genuinely lives — and most are GPU- or data-gated, or genuinely unsolved.
- **CLOSED — no longer an open invention target:** a homology-independent non-metabolic MECHANISM signal on CPU is
  DEFINITIVELY closed (4 signal classes + the MULTISIG1 ensemble upper-bound all fail to beat conservation-breadth 0.908);
  the only untested lever is a GPU-scale structure-aware PLM or experimental mechanism data — an ACQUISITION, not a CPU invention.
- **ENGINEERING (known method, just build/run — NOT inventions; call them what they are):** class-conditional-conformal
  productionization; knowledge-graph integration; autonomous-detector refinement; modality-recommender generalization;
  **running** co-folding/MD (the methods exist — the block is GPU compute, not invention).
- **ACQUISITION (get a resource/data — zero invention, highest leverage):** a **GPU**; a **wet-lab collaborator**; curated
  eukaryote GEMs; a genome-wide *P. falciparum* CRISPR screen; larger curated networks.
**Honest breakdown of the remaining ~75–80%:** it is dominated by **acquisitions + a few genuinely-open inventions**, with a
thin layer of engineering. This is why "keep spawning CPU experiments" cannot close it — and why the plan's top actions are
acquisitions + publication, not an infinite CPU experiment stream.

## 12. The COMBINATION / SCENARIO matrix (the explicit "other combination plans" — parallel & cross-objective)
*Beyond the per-objective A→Z chains (§4), the real world presents COMBINATIONS of outcomes. Here is the pre-planned response
to each combination, so we "go without pause" but never randomly. Rule: **publication (O9) + acquisition outreach (GPU +
collaborator) run in PARALLEL in every scenario** — they block nothing and deliver/unlock the most.*

| Scenario (combination of states) | Detection | Pre-planned combined response |
|---|---|---|
| **S-A: PLMESS1 fails + no GPU + no bench** (most-likely near-term) | PLMESS1 ΔAUROC<0.03/leakage; no resources | **Consolidate + publish** the validated core+negatives (O9); pursue GPU + collaborator acquisitions in parallel; **STOP CPU experiment spawning** (compute frontier mapped). Honest default. |
| **S-B: PLMESS1 succeeds** | ΔAUROC≥0.03, survives leakage+study-bias | Bank the foundation-model non-metabolic signal; extend to more organisms (data-permitting, ENGINEERING); integrate into the engine; update manuscript. Then S-A for the rest. |
| **S-C: GPU acquired** | resource available | Run AFFINITY1 GPU benchmark (O6-D). Pass→intervention half opens (biggest %-jump); Fail→physics/MD (O6-E); Fail→route target to experimental screening (O6-terminal). In parallel: foundation-model mechanism (O2-E'/causal). |
| **S-D: wet-lab collaborator secured** | partner + bench | Run CRISPRi (O7-A) on the top broad-spectrum nominated target. ≥5× defect→**first real-world confirmation** (the ~3/10→higher jump); <5×→prediction wrong→recalibrate the nominating signal (first-class negative). |
| **S-E: GPU AND bench both absent long-term** | time passes, no resources | Terminal honest state: the vision is **bounded at the validated compute-only platform + negative map** until resources arrive; publish, keep the ask open, **do not fake progress**. This is an acceptable, honest end for the autonomous phase. |
| **S-F: publication rejected as "insufficient novelty"** | editor/reviewer verdict | Reframe as a negative-results/reproducibility paper (its genuine strength, per ANTICIPATED_REVIEWS); bioRxiv preprint stands regardless; the contribution is unchanged. |
| **S-G: a committed result fails to reproduce / a confound found** | reproduce-×2 mismatch / null control | Retract/down-tier in the LEDGER immediately (as done for V14/N1, the "host-embedded" rule, EXPDESIGN1-G2, CONFORMAL1 marginal); integrity over preservation. |

**Combined-fallback logic (no pause, not random):** at any moment, execute the S-row matching the current state; when a
detection signal fires, transition to the matching S-row; keep O9 + acquisition-outreach running in parallel throughout.

## 13. Current-state decision table (given the state RIGHT NOW → exact next action)
- **State now (updated 2026-08-08):** PLMESS1 **DONE → 4th closure** AND MULTISIG1 **DONE → ensemble-ceiling closure** — the
  non-metabolic mechanism is now closed **individually (4 signals) AND at the ensemble upper-bound**; **Scenario S-A is
  ACTIVE**; no GPU; no wet-lab; Phase-1 ~20–25% (of the fullest COMPUTATIONAL platform; ~5–8% of the fullest END-TO-END
  vision, Part IV); MASTER_PLAN I–IV + contingency tree in place; publication honesty-pass + manuscript Part-III fold-in +
  collaboration-brief refresh done.
- **Immediate next (autonomous, per S-A):** the non-metabolic CPU line is DEFINITIVELY CLOSED (individual + ensemble — no
  further attempts). The remaining genuinely-CPU-buildable items are modest (uncertainty productionization, knowledge-graph
  integration) and are honestly ENGINEERING, not needle-movers. The CPU-experiment frontier is at its honest end — the
  needle-movers now require acquisitions (GPU → intervention half; a bench → real-world + the closed loop) that need the human.
- **Parallel-available-now (CPU, autonomous, modest):** remaining publication prep — a ≤25-word title; the off-class-TM and
  study-matched-cancer nulls (small re-analyses); these are ENGINEERING finishing touches, not needle-movers.
- **Blocked-pending-acquisition (the needle-movers — need the human):** GPU (→ intervention half), wet-lab collaborator
  (→ real-world jump). **These are the honest top of the backlog and I cannot self-acquire them.**
- **Honest statement of the autonomous frontier:** the CPU-only, open-data, zero-budget invention space is **at its honest
  end** for the high-value questions. With the non-metabolic mechanism now closed both individually and at the ensemble
  upper-bound (MULTISIG1), the genuinely value-adding moves are **acquisitions** (GPU, bench) and **dissemination** — not more
  autonomous CPU experiments. A handful of modest ENGINEERING items remain (uncertainty productionization, knowledge-graph
  integration); I will label them as such and not present them as needle-movers.

## 14. Executive synthesis (one screen — nothing missed)
The vision = best intervention for any disease, computationally. We are ~20–25% of the fullest *computational* platform and
~3/10 real-world: **deep in metabolic target-ID + validation methodology, empty in the molecule half / systems-biology
breadth / simulation / foundation-model reasoning / causal.** The pipeline (S0→S6) is BUILT through target-ID +
prioritization + governance; the **two gates** that gate everything downstream are a **GPU** (→ the intervention/affinity
half) and a **wet-lab bench** (→ real-world confirmation). The non-metabolic-mechanism door is now DEFINITIVELY closed — 4 signal
classes individually (MET4/NONMET1/REGNET1/PLMESS1) AND the ensemble upper-bound (MULTISIG1). Every objective has a
pre-registered failure signal and a pre-planned fallback (§4), and every
*combination* of outcomes has a pre-planned response (§12). What NOT to do is enumerated (§5). The honest top of the backlog
is **acquisitions (GPU, collaborator) + publication of the validated core+negatives** — not more CPU experiments, which are
near their honest end. Truth over vision: we are 100% ready to *execute* what is buildable/known, honest that the rest needs
resources or genuine open-science inventions we name explicitly and do not fake.

---

# PART III — the ULTIMATE connective layer (every dot connected: data-flow contracts · full traceability of 160 experiments · the closed feedback loop · the composition law · cross-cutting threads · failure-cascade · the logical spine)

*This part closes the gaps Parts I–II left implicit: it makes every logical connection EXPLICIT — how each stage's output
becomes the next stage's input, how all 160 committed experiments map onto the pipeline, how results FEED BACK to improve the
engine, how per-class models COMPOSE into "any disease," how uncertainty/safety/bias thread THROUGH every stage, and how a
failure at any node CASCADES. Every connection is grounded in a committed experiment; none is invented.*

## 15. The pipeline as a connected data-flow graph (stage I/O contracts — no orphan dots)
*Each stage: `INPUT ⇒ OUTPUT ⇒ CONSUMER`. Read top-to-bottom = the forward pass; §17 adds the backward (feedback) edges.*

- **S0 Input+detect:** `{genome | causal-gene | GWAS | CRISPR-screen | HPO-phenotype}` ⇒ `{biology_class + data-descriptors}`
  ⇒ **S1/S2** (via ROUTERAUTO1/class_detector). *Orphan closed:* raw-phenotype enters only via PHENO1 retrieval → candidate
  gene → re-enters as a "causal-gene" input; de-novo-from-phenotype is OPEN and routes to ABSTAIN.
- **S1 Mechanism:** `{genome, GEM}` ⇒ `{FBA-essential set + confidence}` (metabolic); the non-metabolic branch emits **only
  conservation-breadth** (4 closures MET4/NONMET1/REGNET1/PLMESS1 + the MULTISIG1 ensemble ceiling) ⇒ **S2**. *Connection:* S1's transfer-condition (GEM
  encodes real biosynthetic dependence; META1/FAIRGATE) decides whether its output is trusted or capped.
- **S2 Target-ID:** `{class, S1 outputs, proteome, reference targets}` ⇒ `{ranked targets + per-target signal-provenance +
  confidence-tier}` ⇒ **S3**. *Connection:* the class picks the signal (FBA/dependency/genetics/structure/conservation) per
  the transfer table (§18); silent-failure risk (TID4) is carried as a confidence caveat.
- **S3 Prioritize/Safety/ExpDesign:** `{S2 targets}` ⇒ `{host-safe, multi-axis-ranked (BESTINT1), VOI-ordered (EXPDESIGN1)
  shortlist + calibrated confidence (CALIB1) + explicit abstentions}` ⇒ **S4** *and* **S5** (which targets to test first).
  *Connection:* the hard host-non-homology filter (FRONT1/E2E2) is a GATE — nothing unsafe passes to S4.
- **S4 Intervention:** `{target + mechanism + localization}` ⇒ `{modality-class (MODALITY1) + repurposing-candidate
  (INTERVENE1/2) OR an explicit "novel-affinity = OPEN/GPU-gated" flag}` ⇒ **S5**. *Connection:* the SM-inhibitor branch is
  gated by the affinity wall (HIT2/AFFINITY1) — it emits a *feasibility class*, never a validated potent molecule.
- **S5 Validation:** `{shortlist + intervention}` ⇒ `{in-silico confidence (reproduced ×2); a turnkey wet-lab design
  (CRISPRIDESIGN1); and — once run — an experimental result}` ⇒ **S6** *and* **feedback to S1/S2** (§17). *Connection:* this
  is the Phase-1→Phase-2 boundary; everything above is in-silico hypothesis, everything at/after the experimental result is
  real-world.
- **S6 Governance (wraps all):** routes (class detector), **abstains** where no signal transfers, propagates confidence,
  enforces provenance/reproducibility, composes (§18). *Connection:* S6 is the only stage that can emit a *final* answer or a
  *final abstention* — it is the integrity gate on the whole graph.

## 16. Full traceability — all 160 experiments mapped onto the pipeline (every dot → its objective + status)
*Grouped by pipeline node (representative IDs; status in caps). This connects the entire experimental corpus to the plan.*

- **S2 Target-ID core (metabolic) — VALIDATED:** MET1/MET2/MET3 (mechanism breaks the conservation ceiling), VAL-ESS/CROSSVAL
  (6 curated GEMs, OR 4–45), PREDVAL (per-target scorecard), REACH1 (conservation-breadth recovers non-metabolic essentials),
  BESTINT1 (multi-axis). Blind: BLIND1/2/3/6 PASS, BLIND4/5/7 FAIL (analyst-blind, 4/3 split).
- **S1 Mechanism non-metabolic — CLOSED (4 signals + ensemble):** MET4 (PPI/study-bias), NONMET1 (synteny/collinear), REGNET1
  (regulatory/clean null), PLMESS1 (PLM/re-encodes conservation), + MULTISIG1 (the ensemble of all four still doesn't beat
  conservation). ⇒ conservation-breadth (0.908) is the accepted, definitive ceiling.
- **S2 Target-ID other classes:** viruses → FOLD1/2, GENERALIZE1/3, HARDENV1 (structural class-ID, PASS n=5); fungi/eukaryote
  → GENERALIZE4, HARDENF1 (PASS); parasites → GENERALIZE5, HARDENP1, HOSTCTX1/2, PARARESOLVE1/2 (GEM/base-rate-bounded);
  cancer → DEPEND1, F3CLIN1 (dependency + patient-driver); monogenic → MENDEL1; complex → GENETICS1; phenotype-input → PHENO1.
- **S2 Target-ID negatives/bounds:** TID1/2 (conservation ceiling), TID3 (kingdom degradation), TID4 (silent failure),
  TRANSFER1 (dependency doesn't transfer label-free).
- **S3 Prioritize/Safety/ExpDesign:** FRONT1/FRONT2/E2E2 (selectivity/safety), CONDROB1 + SYNLETH1/2 (robustness), CALIB1
  (calibration), EXPDESIGN1 (VOI ~8× efficiency), AMR1 (durability — CLOSED for static biology), CONFORMAL1 (OOD abstention
  bound).
- **S4 Intervention:** MODALITY1 (modality triage), INTERVENE1/2/3 (repurposing, narrow), B30/B30b (ADMET), B31
  (synthesizability), B33/B40/B52 (generation). **Affinity wall (CLOSED/GPU-gated):** HIT1/HIT2, C1, B46/B47/B48/B49,
  B55/B56/B63, B65, AFFINITY1 (co-folding, GPU-gated), STRUCTREPURPOSE1 (promiscuity).
- **S5 Validation + Feedback:** CRISPRIDESIGN1 (turnkey wet-lab design), EXPVAL/BROADSPEC/DRUGGABLE/PANBACT/PREDVAL
  (deployment predictions), NEWBUG/SAUREUS (held-out); **feedback:** SIL1 (self-improving loop works in-domain), SIL2 (washes
  under shift), B45/B51/B65 (active-learning bounds).
- **S6 Governance/Integration:** SUBSTRATE1–5, ENGINE/engine_v1, discovery_engine, COMPOSITE1–4, ROUTERAUTO1, DARK1
  (abstention-integrity), CAPSTONE1/2 (end-to-end proofs); method inventions META1 (transfer principle), FAIRGATE1 (base-rate
  gate).
- **Era-1 cancer (bounds that shaped the plan):** B1–B23 — drug-response intrinsic ceiling (B1/B2), clinical null (B10/B17),
  external-replication failure (B20/B21) ⇒ the "clinical response prediction = tested-negative" bound; synergy B24–B29 (PARTIAL).

## 17. The CLOSED FEEDBACK LOOP (the biggest missing connection — forward↔backward)
*Parts I–II were a forward pass. The fullest vision is a LOOP: an experimental result must flow BACK to improve the engine.
That edge exists in evidence but was never wired into the plan. Here it is, with its honest bound.*
- **Forward:** S0→…→S5 nominates a target/intervention + a turnkey experiment (CRISPRIDESIGN1).
- **Backward (S5 ⇒ S1/S2):** a wet-lab result (or any new labeled data) re-enters via the substrate's **continuous-absorption
  guardrail** (SUBSTRATE3) as high-tier evidence, and **recalibrates the nominating signal** (a confirmed essential raises
  that signal's weight; a refuted one lowers it). Mechanism proven in-silico: **SIL1** (conformally-gated self-improving loop
  improves in-domain, 6/6 tasks) — *but* **SIL2** (the loop washes out under distribution shift) and **CONFORMAL1** (OOD
  confidence degrades 94%→55%) together impose the HARD RULE: **the feedback loop may only trust self-/near-domain labels;
  on a novel organism it must widen uncertainty and defer to real experimental labels — never bootstrap confident labels
  out-of-distribution.** This connects the negatives (SIL2, CONFORMAL1) to the loop's safe design.
- **Consequence for the vision:** true closed-loop autonomy is **gated on real experimental labels** (Phase 2). Until then the
  loop safely improves only within validated domains. This is why O7 (wet-lab) is the master unlock — it is the ONLY input
  that closes the loop honestly.

## 18. The COMPOSITION LAW ("book of validated models" → "any disease")
*How the pieces become the whole — the meta-level connection.* "Any disease" is NOT one model; it is the **union of per-class
validated signal-models, each fired only inside its transfer domain, composed by the router, with abstention everywhere else**
(composite-architecture reframe). The **transfer-condition principle IS the composition operator:**
`answer(disease) = ⊕_class [ signal_class if transfer-condition(class) holds, at earned confidence ] ; else ABSTAIN`.
- Coverage today = the union of validated domains: bacteria/archaea (FBA full), fungi (FBA capped), viruses (structure),
  cancer (dependency), monogenic (mode), complex (genetics capped), + conservation-breadth everywhere as the workhorse.
- The frontier = the complement (where no model transfers) → **honest abstention** (DARK1/TRANSFER1). Growth of "any disease"
  = adding validated domains (each a new "chapter"), never forcing one model onto biology it doesn't fit. CAPSTONE2 is the
  proof the composition operates end-to-end and fails safe.

## 19. CROSS-CUTTING THREADS (wired through EVERY stage — not per-stage afterthoughts)
- **Uncertainty thread (S2→S6):** CALIB1 (ordinal confidence) → CONFORMAL1 (marginal is vacuous for the target class; even
  class-conditional degrades OOD) → **RULE propagated to every stage: every output carries a confidence; on a novel
  organism/class, widen/cap it (COMPOSITE3 cap) and never claim nominal coverage OOD.**
- **Base-rate / study-bias thread:** FAIRGATE1 (risk-ratio gate) + META1 + the study-bias controls (F3CLIN1/GENETICS1/MET4) →
  **RULE: every enrichment/relevance claim uses base-rate-fair + study-bias-controlled statistics** (this is why several
  positives survived and several tempting ones were killed).
- **Safety thread (gate before S4):** hard host-non-homology filter (FRONT1/E2E2) → **RULE: no target reaches intervention
  design without passing it** (conservation-ranking-as-safety is CLOSED — most-conserved = host-toxic).
- **Provenance/reproducibility thread (all stages):** pre-registration + reproduce-×2 + first-class negatives + LEDGER →
  **RULE: every output tagged with evidence-tier + reproduce-sha; a result that fails to reproduce or a confound found is
  retracted immediately** (V14/N1, host-embedded rule, EXPDESIGN1-G2, CONFORMAL1-marginal all retracted/down-tiered).

## 20. FAILURE-CASCADE map (if a node fails, what downstream is affected → the systemic response)
- **S1 mechanism fails for a class** (non-metabolic; host-scavenger GEM) → S2 falls back to conservation-breadth or **abstains**
  → S3/S4 run only on what S2 emits; if S2 abstains, the **whole pipeline abstains** (never fabricates). *Terminal: honest "no
  trustworthy target from computation; needs experimental data."*
- **S4 affinity is OPEN/GPU-gated** → S5 cannot validate a *novel* molecule → route to **repurposing** (if a drug exists) or
  **experimental screening**; never emit a fake potent lead.
- **S5 wet-lab unavailable** → the loop (§17) cannot close → the engine stays bounded to in-silico hypotheses + validated
  domains; **publish the validated core + negatives** (the value that does NOT need the loop closed).
- **S6 mis-fire risk** → caught by CAPSTONE2 fail-safe + 93 unit tests + DARK1; a detected mis-fire → abstain + fix before any
  claim. **Every cascade terminates in ABSTENTION or EXPERIMENT-ROUTING — never in fabrication.** This is the integrity
  invariant of the whole graph.

## 21. Phase-1→Phase-2 trigger, resource ROI, and per-stage KPIs (so progress is measurable, not vibes)
- **Phase-1-complete trigger (computational):** all reachable classes covered-or-abstaining ∧ both halves built-or-honestly-
  bounded ∧ integration proven (CAPSTONE2 ✓) ∧ every wall characterized ∧ GPU/data-gated items specced. *Status: the
  un-gated CPU portion is essentially done; ~20–25% of the fullest vision because the gated/open majority remains.*
- **Phase-2 trigger (real-world):** a collaborator + a nominated target ⇒ run CRISPRIDESIGN1 (O7). This is the ONLY trigger
  that starts the closed loop (§17).
- **Acquisition ROI ordering (highest first):** **GPU** (unlocks the 14-weight intervention half) ≈ **wet-lab bench**
  (unlocks real-world + the loop) ≫ curated eukaryote GEMs / Pf screen (unlock specific bounded gaps) ≫ **more CPU
  experiments (~0 marginal — the frontier is mapped).**
- **Per-stage KPIs (measurable):** S2 = odds/risk-ratio + analyst-blind pass-rate (now 4/7) ; S3 = precision@k + abstention-
  integrity (0 mis-fire — held) ; S4 = modality accuracy (0.814) + repurposing coverage (~1–7%) ; S5 = reproduce-×2 (held
  throughout) + [future] wet-lab confirm-rate ; S6 = fail-safe pass (CAPSTONE2 ✓) + test suite (93/93).

## 22. THE LOGICAL SPINE (the single "why" chain — every link justified by evidence)
Vision = best intervention for any disease **⇒** needs mechanism→target→intervention→validation (S1–S5) **⇒** but label-free
transfer is bounded by biological invariants (**transfer-condition principle**, META1) **⇒** so build per-class validated
signals + compose + abstain (COMPOSITE/CAPSTONE) **⇒** the one signal that breaks the conservation ceiling is mechanistic
FBA-essentiality, and it is **metabolic-scoped** (MET1–3; non-metabolic CLOSED ×4 + ensemble (MULTISIG1)) **⇒** target-ID is therefore validated but
*narrow*, strongest for pathogens (VAL-ESS/BLIND) **⇒** the intervention half needs zero-shot affinity, which is **OPEN/GPU-
gated** (HIT2/AFFINITY1) **⇒** so no validated novel molecule is producible on CPU **⇒** real-world truth needs a **wet-lab**
result to close the loop (§17), which is **experiment-gated** (CRISPRIDESIGN1 ready) **⇒** therefore the honest reachable end
on CPU+open-data is a **validated, reproducible target-ID method + an honest negative map + a fail-safe composing engine**
(≈3/10 real contribution, ~20–25% of the computational vision) **⇒** and the needle-movers are exactly two acquisitions (a
**GPU**, a **bench**) + **publication** — each named, none faked. *Every arrow above is a committed experiment or audit; this
is the connected chain from the vision to the next concrete action, with no missing dot.*

---

# PART IV — THE FULLEST-VISION ARCHITECTURE (the complete component tree, honestly status-tagged)

*Honest correction: the S0–S6 pipeline in Parts I–III is INTERCEPTA's CURRENT THIN SLICE — a target-ID-centric, mostly-pathogen,
mostly-metabolic spine. The FULLEST vision ("best therapeutic intervention for ANY disease, from minimal data, all the way to
the clinic") is a far larger platform. This Part enumerates the ENTIRE architecture it must contain — 7 layers, ~70
components — so nothing is missing, each tagged: **BUILT · PARTIAL · SEED(toy) · MISSING · OPEN(unsolved science) · GPU-gated ·
DATA-gated · EXPERIMENT-gated · CLINICAL-gated.** The current slice is a small highlighted subset; most of the vision is
MISSING/gated, and this Part says exactly what and why.*

**Honest recomputation of completeness against THIS fullest architecture:** the ~20–25% figure was of the narrower "fullest
*computational* platform buildable without experiments." Against the fullest **end-to-end vision** below (which includes all
disease classes, all scales, all modalities, preclinical, and clinical), INTERCEPTA is **~5–8%** — deep in one sliver (Layer
C metabolic target-ID + Layer F methodology), essentially empty in Layers A(breadth), D(most modalities), E(translation),
and much of B and F. This is the honest denominator the earlier % understated.

## Layer A — Disease universe & multimodal representation (accept ANY disease)
- **A1 Disease taxonomy across ALL classes:** infectious (bacterial ✅/viral PARTIAL/fungal PARTIAL/parasitic PARTIAL/prion
  MISSING), cancer (PARTIAL: dependency), genetic (monogenic PARTIAL/complex PARTIAL), **immune/autoimmune/inflammatory
  MISSING**, **metabolic-disease MISSING**, **cardiovascular MISSING**, **neurodegenerative/psychiatric MISSING**,
  **developmental/rare beyond-gene MISSING**, **aging MISSING**, environmental/toxic MISSING, idiopathic/**never-seen** (the
  north-star case: PARTIAL via abstention only).
- **A2 Multimodal disease input:** genome ✅ · transcriptome SEED · proteome SEED · phenotype/HPO PARTIAL(PHENO1) · GWAS
  PARTIAL(GENETICS1) · CRISPR-screen PARTIAL(DEPEND1) · **epigenome / metabolome / microbiome / single-cell / spatial /
  imaging / EHR-clinical / epidemiology / patient-trajectory = MISSING.**
- **A3 Disease-state & context representation** (tissue, stage, comorbidity, patient sub-population): **MISSING.**

## Layer B — Multi-scale biological understanding (mechanism at every scale)
- **B1 Molecular:** sequence ✅ · static structure PARTIAL(off-the-shelf AF/fpocket) · **dynamics/MD OPEN/GPU-gated** ·
  **complexes/co-folding GPU-gated** · biophysics MISSING.
- **B2 Networks:** metabolism ✅(FBA) · transcriptional regulation CLOSED-as-target-signal(REGNET1) but as a MODEL MISSING ·
  **signaling MISSING** · **epigenetic regulation MISSING** · PPI/interactome PARTIAL-negative(MET4) · **immune networks
  MISSING** · host–pathogen PARTIAL-negative(HOSTCTX).
- **B3 Cell:** **whole-cell models MISSING** · cell-state/single-cell MISSING · cell–cell communication MISSING.
- **B4 Tissue/organ/organism:** physiology/spatial MISSING · **PK/PD MISSING** · multi-organ MISSING.
- **B5 Population/evolution:** GWAS PARTIAL(GENETICS1) · **resistance/evolution dynamics PARTIAL** — DYNAMICS1 contact-residue
  durability signal (AUROC 0.84, n-fragile) works where AMR1 whole-protein static-biology
  fails) · epidemiology MISSING.
- **B6 Causal:** association PARTIAL(GENETICS1) · **causal graphs / counterfactuals / Mendelian-randomization / perturbation
  modeling = OPEN/MISSING** (a whole domain, ~untouched).

## Layer C — Target / intervention-point identification (the current strength — but narrow)
- **C1 Essentiality:** metabolic ✅(validated); **non-metabolic CLOSED ×4 + ensemble (MULTISIG1)** (conservation-breadth is the ceiling).
- **C2 Functional dependency:** ✅(cancer, DEPEND1); does not transfer label-free (TRANSFER1).
- **C3 Genetics/causal-gene:** PARTIAL(GENETICS1/MENDEL1). **C4 Structural class-ID:** PARTIAL(viruses).
- **C5 Systems/network targets** (master regulators, network controllability, **combination/multi-target**): MISSING/negative.
- **C6 Non-protein & hard targets** (RNA, DNA, PPI interfaces, **allosteric**, **degradation-tractable**): MISSING.
- **C7 Synthetic lethality / collateral vulnerability:** SEED(INTERVENE3/SYNLETH) · context-specific targets MISSING.

## Layer D — Intervention design (the fullest MODALITY space — mostly MISSING)
- **D1 Small molecules:** de-novo generation SEED(B33/B40) · **novel-target binding affinity — GPU-gated even at
  small-candidate scale** (empirically confirmed: CPU pilot 0/20 in ~48 min, retracted the "CPU-feasible" reframe;
  HIT2/AFFINITY1/CPU_PILOT_FINDING) · ADMET ✅-standalone · synthesizability ✅-standalone · developability PARTIAL.
- **D2 Repurposing:** PARTIAL-narrow(INTERVENE1/2). **D3 Modality selection:** PARTIAL(MODALITY1, triage-only).
- **D4 Biologics** (antibodies/proteins): MISSING. **D5 Nucleic-acid** (ASO/siRNA/mRNA/gene-therapy/**gene-editing**): MISSING
  (only named in MODALITY1's taxonomy). **D6 Targeted degradation** (PROTAC/molecular-glue): MISSING. **D7 Peptides/macrocycles:**
  MISSING. **D8 Cell therapies** (CAR-T): MISSING. **D9 Combinations:** SEED(synergy B24–29). **D10 Delivery/formulation:** MISSING.

## Layer E — Validation & translation (in-silico → clinic → real-world)
- **E1 In-silico validation:** ✅(reproduced ×2, analyst-blind). **E2 Experiment design/active-learning:** PARTIAL(EXPDESIGN1),
  loop bounded(SIL2). **E3 Wet-lab:** EXPERIMENT-gated (CRISPRIDESIGN1 turnkey design ready). **E4 Preclinical** (organoid/
  animal/tox): MISSING/EXPERIMENT-gated. **E5 Clinical-trial design & simulation, biomarkers, patient stratification:**
  MISSING/CLINICAL-gated (response-prediction tested-NEGATIVE, B10/B20). **E6 Regulatory / real-world-evidence / pharmacovigilance:**
  MISSING.

## Layer F — Meta / AI capabilities (cross-cutting engines)
- **F1 Foundation models** (sequence/structure/chem/multimodal): SEED(ESM embeddings used; PLMESS1) · **training/large models
  GPU-gated.** **F2 Reasoning / agentic orchestration:** MISSING. **F3 Causal inference engine:** OPEN/MISSING.
- **F4 Simulation** (MD, systems-dynamics, PK/PD, evolutionary): OPEN/GPU-gated. **F5 Active/continual/closed-loop learning:**
  SEED(SIL1/2) bounded to in-domain. **F6 Uncertainty/calibration:** PARTIAL✅(CALIB1/CONFORMAL1 — OOD bound known).
  **F7 Explainability/provenance:** ✅. **F8 Multi-objective optimization:** SEED(BESTINT1). **F9 Knowledge integration/graphs:**
  PARTIAL. **F10 Reproducibility/governance:** ✅(the genuine strength). **F11 Safety/ethics/bias governance:** PARTIAL(host-safety
  filter; abstention) · broader ethics MISSING.

## Layer G — Deployment & real-world operation
- **G1 Any-disease routing + abstention:** PARTIAL✅(router, CAPSTONE2 — narrow coverage). **G2 Clinician/researcher interface:**
  MISSING(CLI only). **G3 Continuous update from new data (the closed loop):** SEED, EXPERIMENT-gated (§17). **G4 Collaboration/
  data-sharing infrastructure:** PARTIAL(docs). **G5 Equity/access/cost, global-health deployment:** MISSING.

## How Part IV connects back to the S0–S6 slice (the honest mapping)
The S0–S6 pipeline = {A1-partial, A2-partial} → {B2-metabolism, B6-association} → {C1–C4} → {C-safety + F6/F8} →
{D1-affinity-gated, D2/D3} → {E1, E2-seed, E3-gated} → {F/G governance}. **Everything in Layers A(breadth), B(scales beyond
metabolism), C5–C7, D4–D10, E4–E6, F1–F5(most), G2/G5 is MISSING or gated** — that is the "lots and lots missing" you named,
now enumerated so it is not a vague gap but a concrete, prioritized backlog.

## What this reveals for "what to do / what's next" (honest, non-random)
1. **The vision is ~5–8% built end-to-end** — most of it is MISSING (whole modalities, scales, disease classes, translation)
   or OPEN/gated (affinity, causal, simulation, foundation-model training, wet-lab, clinical). The earlier ~20–25% was of a
   narrower denominator; against the fullest architecture it is smaller, and I state that plainly.
2. **The MISSING items split the same 3 ways (§11):** most are **ACQUISITION** (data modalities A2, GPU for D1/F1/F4,
   wet-lab/clinical for E3–E6) or **genuine OPEN inventions** (causal B6/F3, novel-target affinity D1, dynamics F4) — only a
   thin engineering layer is pure CPU-buildable now (e.g., broaden A1 disease-class arms where open data exists; F9 knowledge
   graph; F5 loop hardening). **This confirms: more CPU experiments cannot build the fullest vision — data, GPU, wet-lab, and
   a few field-level open inventions are the real content.**
3. **Highest-leverage additions to the CURRENT slice, in order (each honestly tiered):** (a) GPU → D1 affinity + F1/F4 (the
   biggest computational chunk); (b) wet-lab → E3 → closes the loop (§17); (c) open-data CPU arms for uncovered A1 classes
   where a validated signal plausibly exists (immune/metabolic-disease via genetics — extends GENETICS1) — modest but genuine;
   (d) causal engine (F3/B6) — a genuine open-science build, attempt only with a study-bias-robust design.
4. **What we will NOT pretend:** we will not claim Layers D4–D10 / E4–E6 / B3–B4 exist or are near — they are MISSING and most
   need biology, data, or experiments we do not have. Naming them completes the map; building them is gated, not imminent.
