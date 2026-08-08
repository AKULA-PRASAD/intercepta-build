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
- Status: **metabolic BUILT** (FBA, validated VAL-ESS/CROSSVAL/BLIND1–7); **non-metabolic CLOSED×3** (MET4 PPI, NONMET1
  synteny, REGNET1 regulatory — all failed; PLMESS1 = 4th attempt via PLM embeddings, running); **regulatory/signaling/
  dynamic/whole-cell = MISSING/OPEN.**
- Transfer-condition: FBA transfers where the GEM encodes genuine biosynthetic dependence (fails on host-scavengers, sparse
  GEMs; META1/FAIRGATE bound it).

**S2 — TARGET identification.** Which protein/node to intervene on.
- Status: **BUILT (narrow-but-validated).** essentiality (FBA), conservation-breadth (the non-metabolic workhorse, AUROC
  0.91), structural class-ID (viruses, GENERALIZE2/3), functional dependency (cancer, DEPEND1), genetics (complex, GENETICS1),
  causal-gene (monogenic, MENDEL1). Silent-failure on phylogenetically-isolated organisms (TID4) is a known limit.

**S3 — PRIORITIZATION, SAFETY, EXPERIMENT-DESIGN.** Rank, filter unsafe, decide what to test.
- Status: **BUILT.** multi-axis best-intervention (BESTINT1), hard host-non-homology safety filter (FRONT1/E2E2),
  resistance/condition-robustness, calibrated confidence (CALIB1), VOI experiment-prioritization (EXPDESIGN1, ~8× wet-lab
  efficiency). Honest bound: durability/resistance-liability from static biology = CLOSED (AMR1); OOD abstention guarantee
  degrades (CONFORMAL1: 94%→55%).

**S4 — INTERVENTION design.** Target → therapy.
- Status: **PARTIAL/mostly-unbuilt (the weak half).** modality triage ✓ (MODALITY1, fail-safe), repurposing ✓-narrow
  (INTERVENE1/2, ~1–7% coverage), ADMET ✓ (B30), synthesizability ✓ (B31), generation ✓-standalone (B33). **Novel-target
  binding affinity = OPEN/GPU-GATED** (docking≈chance HIT2; QSAR analog-bound HIT1; PCM null B49; active-learning null B65;
  co-folding CPU-infeasible AFFINITY1). Structural repurposing = CLOSED (promiscuity, STRUCTREPURPOSE1).

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
1. PLMESS1 (running) — learned-representation attack on the non-metabolic gap + AI-domain probe.
2. Uncertainty productionization — ship class-conditional (Mondrian) conformal into the engine (CONFORMAL1 showed marginal
   is vacuous for targets); genuine, honest, closes a real hole.
3. Knowledge-integration — a calibrated multi-signal posterior with honest joint uncertainty (careful: not to overlap the
   substrate's rank-aggregation trivially).
- **What NOT to do in Wave 1:** a 5th non-metabolic-mechanism attempt if PLMESS1 fails (see §4-O2); more shallow disease-class
  coverage arms (diminishing-returns, per the audit); anything requiring GPU dressed up as CPU.

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
- **E:** learned PLM (ESM-2) embeddings (PLMESS1, RUNNING). *[detection: ΔAUROC-beyond-conservation <+0.03 OR fails
  study-bias/leakage checks.]*
- **Terminal honest fallback (if E fails):** **STOP attacking the non-metabolic mechanism on CPU** (four independent
  principled closures = a real scientific bound). Accept **conservation-breadth (AUROC 0.91) as the ceiling** for the
  non-metabolic half; route deeper mechanism to Wave-2 GPU foundation-models OR to experimental data. **Do NOT run a random
  5th attempt** — that would be the trial-and-error we forbid.

### O3 — Identify a TARGET for a novel organism/disease
- **A:** the class-matched validated signal (FBA/dependency/genetics/structure) at earned confidence. *[detection: the signal's
  pre-registered gate (OR>3/RR-fair, etc.) fails on the class.]*
- **B:** if the primary signal is out-of-domain → fire the supporting signal (conservation-breadth + host-safety).
- **C:** if none transfers (dark proteome / novel zero-screen parasite) → **ABSTAIN** (DARK1/TRANSFER1 proven fail-safe).
- **Terminal:** abstention is a valid answer — "no trustworthy target from computation alone; needs experimental data."

### O4 — Prioritize + guarantee SAFETY + spend experiments well
- **A:** hard host-non-homology safety filter + multi-axis score + VOI experiment-prioritization (EXPDESIGN1). *[detection:
  a host-toxic target reaches the shortlist — caught by the hard filter's construction test.]*
- **B (durability):** predict resistance-liability from static biology (AMR1). *[detection: AUROC 0.556 < 0.70 → FAILED.]*
  → fallback: resistance/evolvability **dynamics simulation** (Wave-2, GPU) OR flag durability as UNKNOWN and defer to experiment.
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
- **D:** **co-folding (Boltz-2) affinity** — GPU-GATED. *[detection (when GPU available): the AFFINITY1 GPU benchmark —
  AUROC ≥0.60 AND > docking 0.4285 AND novel-vs-inactive ≥0.60; else FAIL.]*
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
1. **Do NOT re-attack the non-metabolic mechanism after PLMESS1** (MET4/NONMET1/REGNET1 + PLMESS1 = 4 closures) — accept the
   conservation ceiling; the next move there is GPU/experimental, not another CPU signal.
2. **Do NOT use docking/QSAR/PCM to claim novel-target potency** (HIT2/HIT1/B49/B65 negatives).
3. **Do NOT predict patient drug-RESPONSE from baseline profiles** (B10/B20 tested-negative).
4. **Do NOT rank targets by conservation as if safe** (FRONT1: most-conserved = host-toxic); use the hard host-non-homology filter.
5. **Do NOT use structural repurposing for coverage gain** (STRUCTREPURPOSE1 promiscuity).
6. **Do NOT predict resistance-liability from static biology** (AMR1 null); it needs dynamics.
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
- **NOW (CPU, autonomous):** PLMESS1 (running) → verify honestly (leakage guard). Then, per §4-O2 terminal rule, EITHER a
  genuine positive (foundation-model capability) OR stop the non-metabolic attack and consolidate. Then Wave-1 items 2–3.
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
  └ non-metabolic (CLOSED×3; PLMESS1=4th) ──X (conservation-breadth is the ceiling)          │
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
  binding-affinity ranking (O6 — the field's open wall); (b) a homology-independent non-metabolic MECHANISM signal (OPEN if
  PLMESS1 fails — 4 closures); (c) de-novo mechanism inference from a raw phenotype (O1 deep case); (d) causal disease
  modeling; (e) resistance-evolvability dynamics (the AMR1 follow-on). These are where "invention/novelty" genuinely lives —
  and most are GPU- or data-gated, or genuinely unsolved.
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
- **State now:** PLMESS1 running; no GPU; no wet-lab; WebSearch budget exhausted (fetch-by-known-endpoint still works);
  Phase-1 ~20–25%; publication honesty-pass done; MASTER_PLAN + contingency tree in place.
- **Immediate next (autonomous):** await PLMESS1 → branch on §4-O2 (bank if positive [verify leakage first]; if negative,
  enter **S-A**: stop CPU non-metabolic, consolidate).
- **Parallel-available-now (CPU, autonomous, modest):** remaining publication prep — a ≤25-word title; the off-class-TM and
  study-matched-cancer nulls (small re-analyses); these are ENGINEERING finishing touches, not needle-movers.
- **Blocked-pending-acquisition (the needle-movers — need the human):** GPU (→ intervention half), wet-lab collaborator
  (→ real-world jump). **These are the honest top of the backlog and I cannot self-acquire them.**
- **Honest statement of the autonomous frontier:** the CPU-only, open-data, zero-budget invention space is **near its honest
  end**. After PLMESS1 (and the modest publication finishing touches), the genuinely value-adding moves are **acquisitions**
  (GPU, bench) and **dissemination** — not more autonomous CPU experiments. I will say this plainly rather than manufacture
  motion.

## 14. Executive synthesis (one screen — nothing missed)
The vision = best intervention for any disease, computationally. We are ~20–25% of the fullest *computational* platform and
~3/10 real-world: **deep in metabolic target-ID + validation methodology, empty in the molecule half / systems-biology
breadth / simulation / foundation-model reasoning / causal.** The pipeline (S0→S6) is BUILT through target-ID +
prioritization + governance; the **two gates** that gate everything downstream are a **GPU** (→ the intervention/affinity
half) and a **wet-lab bench** (→ real-world confirmation). The non-metabolic-mechanism door is closed ×3 (PLMESS1 = the 4th
and last CPU try; then stop). Every objective has a pre-registered failure signal and a pre-planned fallback (§4), and every
*combination* of outcomes has a pre-planned response (§12). What NOT to do is enumerated (§5). The honest top of the backlog
is **acquisitions (GPU, collaborator) + publication of the validated core+negatives** — not more CPU experiments, which are
near their honest end. Truth over vision: we are 100% ready to *execute* what is buildable/known, honest that the rest needs
resources or genuine open-science inventions we name explicitly and do not fake.
