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
