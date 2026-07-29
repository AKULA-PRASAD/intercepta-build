# INTERCEPTA Fullest Vision Research Charter v1.2

**Status:** PROPOSED for CEO co-sign. Once locked, supersedes v1.1.
**Date:** 2026-05-11
**Predecessor:** `INTERCEPTA_Fullest_Vision_Research_Charter_v1_1_SUPERSEDED_by_v1_2_2026-05-11.md` (per P16)
**Scope of this revision:** Three surgical changes only — §1.6 reframed as Phase F commitment; §4 rewritten as Phase B vs Phase F scope boundary; new §1.7 explicit phase table. All other sections of v1.1 unchanged.
**Authority:** CEO scope decision dated 2026-05-11. CSO concurs. Co-signed.

---

## 0. Why v1.2 (Change Log)

Charter v1.1 contained a direct internal contradiction that the disciplined Layer 1 work surfaced through the corpus-read audit pass of 2026-05-11. The contradiction is:

- **§1.6 A1 (added in v1.1):** "the framework proposes and ranks NOVEL drug candidates (not just retrieves and ranks existing approved drugs). Generative chemistry, network propagation to identify undrugged targets, repurposing predictions for new indications."
- **§4 Out-of-Scope (unchanged from v1.0):** "Drug structure prediction / generation — molecular generative models, de novo drug design. Out of scope. We rank existing drugs, not invent new ones."

These cannot both be true at the same scope. They become both true under **phase-conditional framing**: out of scope for Phase B (the current 2-4 year research program); in scope for Phase F (the 5+ year full platform).

The contradiction was a real drift artifact of how v1.1 was created: §1.6 was added to fold in scope from the co-founder vision documents (`INTERCEPTA_Phase_F_Future_Vision_Universal_Net_Specification_2026-03-29` and `INTERCEPTA_Phase_F_Future_Vision_Complete_Platform_2026-03`, originally filed as `vis.pdf` and `vis2_doc.pdf`); §4 was not updated to match. v1.2 reconciles them.

**Three additional related items reconciled by phase-conditional framing:**
- §4 "Federated learning across institutions" — Phase F-canonical per vision document Part 7 (Novel Technology) item 4. Phase B remains single-institution.
- §4 "Causal inference beyond correlative" — Phase F-canonical per vision document Part 7 item 3 (causal inference on biological graphs). Phase B remains predictive/correlative.
- §4 "In vivo validation" — Phase F-canonical per vision document Part 11 (Build Roadmap) Phase 5 publication. Phase B remains computational-only.

Charter v1.2 explicitly does NOT:
- Modify any of §1.1, §1.2, §1.3, §1.4, §1.5 (U1-3, V1-4, I1-3, H1-4, P1-3 success criteria stand)
- Modify any of the 10 Decisions (Decisions 1 v2, 2-10 all stand, all locked under their existing status)
- Modify the L2.1 Substrate Architecture Specification (PROPOSED status stands; technical hygiene drift Findings 4-6 fixed in separate cleanup pass per Step 3 of 6-step plan)
- Modify the Phase B Execution Plan v2 (14 artifacts, 10-11 sessions, all stand)
- Modify Q1-Q11 research questions (stand as-is)
- Modify §2 (Research Questions), §3 (Termination Criteria), §5 (Research Cadence), §6 (Output Structure), §7 (Honest Constraints), §8 (Provisional Architecture Sketch), §9 (Publication Strategy), §10 (Process Discipline), or §11 (What Happens Next)

Charter v1.2 is a **minimum-surface scope reconciliation**, not a rewrite.

---

## 1. The Three Surgical Changes

### Change 1 — §1.6 reframed as Phase F autonomous learning system commitment

**v1.1 §1.6 text (in entirety, preserved):**

> ### 1.6 Autonomous learning system
>
> The framework must operate as an autonomous research system, not a frozen-at-training-time prediction engine. This is a genuine commitment, not aspirational framing — if existing methods are inadequate, we research and invent the methods needed.
>
> - **A1:** Novel drug candidate ranking — the framework proposes and ranks NOVEL drug candidates (not just retrieves and ranks existing approved drugs). Generative chemistry, network propagation to identify undrugged targets, repurposing predictions for new indications. Novel candidates are ranked alongside existing drugs with calibrated confidence.
> - **A2:** Continuous learning — system updates predictions as new transcriptomic data is ingested, without requiring full retraining. Online learning, incremental fine-tuning, or equivalent autonomous update mechanisms.
> - **A3:** Drift detection — system detects when its own predictions are becoming unreliable due to distribution shift, data quality degradation, or biological variation outside training distribution. Triggers self-correction or honest refusal.
> - **A4:** Active learning — system identifies what experiments, validations, or data acquisitions would most improve its own knowledge. Generates an experimental priority queue, not just analyzes given inputs.
> - **A5:** Operational autonomy — end-to-end pipeline runs without human intervention for routine analyses. New disease ingestion → analysis → drug recommendations → mechanism trace, all automated. Human oversight on novel scenarios, not routine ones.
> - **A6:** Self-aware uncertainty — every prediction includes meta-confidence: system knows when it is likely wrong, when it is operating in familiar vs novel territory, and when its training data does not adequately cover the input. This is deeper than H3 OOD detection — it is meta-cognition over the system's own reliability.

**v1.2 reframe:** A1-A6 are reframed as the **Phase F autonomous learning system commitment**, not Phase B commitments. The substantive content of A1-A6 is preserved verbatim — no goal is weakened, no commitment is dropped. What changes is the phase under which each commitment falls due.

**Operationally this means:**
- A1 (novel drug candidate ranking, generative chemistry) — Phase F deliverable. Architected by Phase F Decisions 11-20 (Knowledge Graph, Vulnerability/Selectivity, Generative Chemistry, Docking, Combinations, ADMET, ODE, RNA Velocity, Ranking, Pharma Package). Not committed for Phase B.
- A2 (continuous learning) — Phase F deliverable. Phase B trains and validates once; Phase F enables online updates.
- A3 (drift detection) — **PARTIALLY Phase B.** OOD detection (Charter §1.4 H3, Decision 5 v2 Layer 5.1-5.4 stack) covers prediction-time drift. Distribution-shift-driven model-quality drift over time is Phase F.
- A4 (active learning) — Phase F deliverable. Phase B performs human-directed validation per Decision 6 v2 cascade.
- A5 (operational autonomy) — Phase F deliverable. Phase B is research-grade pipeline with human-supervised stages.
- A6 (self-aware meta-confidence) — **PARTIALLY Phase B.** Conformal prediction (Decision 5 v2 Layer 5.3) and Deep Ensembles (5.2) provide statistical uncertainty. Meta-cognition over reliability across novel scenarios is Phase F.

The "Research and invent where existing methods inadequate" clause stands as a Phase F commitment. INTERCEPTA Phase F will require novel research in multi-scale GNNs, temporal knowledge graphs, causal inference on biological graphs, federated learning for clinical data, and net-constrained generative chemistry per vision document Part 7. These are not vague aspirations — they are formally tracked Phase F research streams.

**The 24-criteria success bar (U1-3, V1-4, I1-3, H1-4, P1-3, A1-A6) becomes a 24-criteria Fullest Vision success bar across both phases.** Phase B success = 18 criteria (U1-3, V1-4, I1-3, H1-4, P1-3, plus the Phase-B-partial of A3 and A6). Phase F success = remaining criteria. Both phases together = Fullest Vision.

This change is the operative resolution of the §1.6 vs §4 contradiction.

---

### Change 2 — §4 rewritten as Phase B vs Phase F scope boundary

**v1.1 §4 text (preserved verbatim in the SUPERSEDED file per P16):**

> ## 4. Out-of-Scope (Anti-Scope-Creep)
>
> These are NOT part of the fullest vision research program:
>
> - **Non-transcriptomic data modalities** — proteomics, metabolomics, methylation as primary inputs. These may be added later, not now. Transcriptomic data is sufficient to demonstrate the core framework.
> - **In vivo validation** — wet-lab experiments, animal models, clinical trials. We are computational. We make predictions; others test them.
> - **Drug structure prediction / generation** — molecular generative models, de novo drug design. Out of scope. We rank existing drugs, not invent new ones.
> - **Clinical decision support** — patient-facing tools, EMR integration, clinical workflow. Out of scope for research phase.
> - **Real-time / streaming analysis** — batch processing only.
> - **Federated learning across institutions** — single-institution data only.
> - **Causal inference beyond correlative** — we predict and rank, we don't claim mechanistic causation in the rigorous Pearl sense.
>
> If a research direction requires any of these, that direction is out of scope.

**v1.2 replacement §4:**

> ## 4. Phase B vs Phase F Scope Boundary (Anti-Scope-Creep)
>
> INTERCEPTA's fullest vision spans two phases. Phase B (current, 2-4 year research program) and Phase F (5+ year full discovery platform) deliver different scope. The following items are scope-conditional, not absolutely out-of-scope. Each item below names the phase under which it falls due.
>
> The items listed here are *anti-scope-creep* for Phase B specifically — meaning Phase B work that drifts into a Phase F item must be flagged, refused if it cannot be deferred, or re-classified as scope expansion requiring CEO consent. Phase F work, when it begins, will treat these same items as in-scope.
>
> | Scope Item | Phase B (2-4 yr) | Phase F (5+ yr) | Notes |
> |---|---|---|---|
> | **Drug structure prediction / generation** (molecular generative models, de novo drug design) | OUT OF SCOPE | IN SCOPE | Phase F Scout 2 (Generative Design) per vision document Part 3.3. Architected by Phase F Decisions 13 (Generative Chemistry) and 16 (ADMET / Synthesizability). |
> | **Federated learning across institutions** | OUT OF SCOPE — single-institution only | IN SCOPE | Phase F novel technology item 4 per vision document Part 7. Required for clinical-data integration without centralization. |
> | **Causal inference beyond correlative** | OUT OF SCOPE — predict and rank only | IN SCOPE | Phase F novel technology item 3 per vision document Part 7. Required for true causal edges in the 15-layer Universal Net (gene → disease, target → therapeutic effect). |
> | **In vivo validation** (wet-lab, animal models, clinical trials) | OUT OF SCOPE — computational only | IN SCOPE (collaborative) | Phase F Part 11 publication pathway via academic co-author validation per vision document Part 12.4 Open Collaboration Architecture. INTERCEPTA does not become a wet lab; Phase F partners with labs. |
> | **Non-transcriptomic data modalities** (proteomics, metabolomics, methylation as primary inputs) | OUT OF SCOPE — transcriptomic primary | IN SCOPE | Phase F integrates Layers 3 (Proteome), 8 (Metabolome), 12 (Epigenome) per vision document Part 2. |
> | **Clinical decision support** (patient-facing tools, EMR integration, clinical workflow) | OUT OF SCOPE | OUT OF SCOPE in research charter | Clinical product layer is downstream of both phases. Vision document Part 9.2 names pharma + biotech as primary delivery, not direct clinical. Out of charter scope; not out of business scope. |
> | **Real-time / streaming analysis** | OUT OF SCOPE — batch processing only | IN SCOPE (Phase F autonomous A5) | Phase F operational autonomy requires near-real-time ingestion of new data. Phase B batch is fine. |
> | **The 15-layer Universal Human Biology Net** (~3M nodes, ~10-50M edges) | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F substrate per vision document Part 2 and Part 3. Phase B uses subset databases (CCLE/GDSC + scRNA-seq atlases + drug-target databases) as needed for L7 head + V0-V6 cascade. |
> | **6-Scout Parallel Discovery System** (Database / Generative / Combination / Network Perturbation / Evolutionary / Cross-Disease Transfer) | OUT OF SCOPE — Phase B = Scout 1 only | IN SCOPE (CANONICAL) | Phase F parallel scout architecture per vision document Part 3.3. The Phase B L7 6-slot drug response head IS Scout 1 (Database Search) in Phase F taxonomy — they are not competing architectures, they are the same component at different platform scope. |
> | **5-Stage Pipeline** (Build Net → Vulnerability/Selectivity → Scouts → Simulation Stack A-F → Multi-Objective Ranking) | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F pipeline per vision document Part 4. Phase B works on Layer 5 of vis2_doc.pdf's terminology (cell-level drug response with predicted clinical outcomes for ranked existing drugs). |
> | **Pharma deliverable package** (SMILES + 3D structure + mechanism + predicted clinical outcomes + safety profile + synthesis route + novelty confirmation + trial design) | OUT OF SCOPE — Phase B delivers research validation only | IN SCOPE (CANONICAL) | Phase F deliverable per vision document Part 9.1. Phase B delivers V0-V6 validated cell-level drug response predictions. |
>
> **Phase B anti-scope-creep enforcement:** if a Phase B work item starts requiring any "OUT OF SCOPE" capability above, it must be flagged in the Decision Record under cross-decision implications and escalated to CEO. Quiet scope creep is the failure mode this section guards against.
>
> **Phase F advance work permitted:** Phase B may produce Phase F-enabling artifacts (e.g., Decision 11 Knowledge Graph scaffolding) IF and ONLY IF such work does not delay Phase B deliverables. Phase B does not subordinate to Phase F.

---

### Change 3 — New §1.7 Phase B vs Phase F Table

**v1.2 adds §1.7 immediately after §1.6:**

> ### 1.7 Phase B vs Phase F (Phased Scope Architecture)
>
> INTERCEPTA's fullest vision is two-phased. Both phases are real. Both phases are committed. Phase B does not invalidate Phase F. Phase F does not invalidate Phase B.
>
> **Phase B (current, 2-4 year research program) is canonical for:** Charter v1.2 sections 1.1-1.5 (U1-3, V1-4, I1-3, H1-4, P1-3 — 18 success criteria), the 10 Decision Records currently locked, the Phase B Execution Plan v2 14 artifacts, and the Layer 1-4 substrate / L7 head / OOD / validation cascade / interpretability / universality / compute / open-source axes. Phase B's deliverable is the **drug response prediction layer** of INTERCEPTA — cell-level, single-cell-resolution, V0-V6 validated, cross-disease universality demonstrated, mechanism-interpreted, with open-source release.
>
> **Phase F (5+ years out, full discovery platform) is canonical for:** Charter v1.2 section 1.6 A1-A6 (6 additional success criteria), the 15-layer Universal Human Biology Net (~3M nodes, ~10-50M edges, ~50 public DB sources per `INTERCEPTA_Phase_F_Future_Vision_Universal_Net_Specification_2026-03-29`), the 5-stage pipeline + 6-scout parallel discovery system + multi-objective ranking + pharma deliverable package per `INTERCEPTA_Phase_F_Future_Vision_Complete_Platform_2026-03`, and the 5 novel-research bets (multi-scale GNNs, temporal knowledge graphs, causal inference on biological graphs, federated learning for clinical data, net-constrained generative chemistry). Phase F's deliverable is the **full drug discovery platform** — novel molecule generation, ADMET/synthesizability filtered, ranked, packaged for pharma Phase I trial entry.
>
> **The phase relationship:**
>
> | Dimension | Phase B (2-4 yr) | Phase F (5+ yr) |
> |---|---|---|
> | **Top-level deliverable** | Drug response prediction for ANY disease at cell-level resolution | Novel drug molecules (existing-drug ranking + generative chemistry + combination discovery) for ANY disease, Phase-I-ready |
> | **Input scope** | Transcriptomic (scRNA-seq primary; bulk RNA-seq via Q3 transfer) | Multi-omic: transcriptomic + proteomic (Layer 3) + metabolomic (Layer 8) + epigenomic (Layer 12) + microbiome (Layer 11) + spatial (Layer 13) |
> | **Output scope** | Ranked existing drug recommendations + mechanism trace + OOD/uncertainty + cross-disease generalization | Phase B output + novel molecule SMILES/3D structure + binding affinity + ADMET + synthesizability + combination scoring + pharma trial design package |
> | **Substrate** | Cell encoder (4 co-equal: scFoundation/scTOP/scVI/PCA per Decision 1 v2) | Phase B substrate + 15-layer Universal Net knowledge graph + AlphaFold 200M structures + PDB experimental + STRING/BioGRID/IntAct interactome |
> | **Architecture** | L7 6-slot drug response head (Decision 4 v2) | Phase B L7 head as Scout 1 (Database Search) + Scouts 2-6 (Generative Design, Combination Explorer, Network Perturbation, Evolutionary Optimizer, Cross-Disease Transfer) running in parallel with bidirectional insight-sharing |
> | **Validation** | V0-V6 cascade (Decision 6 v2): within-dataset → cross-dataset → organoid → tumor → PDX → clinical → cross-disease | Phase B validation + in-vitro experimental partnerships + clinical trial outcome feedback loop (vision document Part 12.1) |
> | **Compute** | Northeastern Explorer single-A100 (Decision 9 v2) | Phase F-scale: Northeastern + AWS/GCP burst for generative chemistry training, AlphaFold-scale structure handling, graph database hosting (~3M nodes, ~50M edges) |
> | **Open source** | Phase B per Decision 10 v2 (permissive default, GPL-3 conditional cluster, V0/V3/V6-tied release) | Phase F per vision document Part 12.4 Open Collaboration Architecture: disease nets open-published; candidate molecules patent-licensable to pharma partners |
> | **Success bar** | 18 criteria (U1-3, V1-4, I1-3, H1-4, P1-3) + Phase B partial of A3, A6 | Phase B criteria + A1, A2, A4, A5, A6 full |
> | **Honest framing** | "Predict which drugs work, validated across diseases, with mechanism explanation" | "Discover novel drug molecules, full pipeline to pharma Phase I, for any disease past/present/future" |
>
> **Why this phasing:**
>
> Phase B is the architecture that can be built defensibly in 2-4 years on Northeastern single-A100 with the current evidence base from the 10 Decisions. It delivers a real, valuable, publishable, open-source-releasable computational drug response prediction platform that the field genuinely lacks. Phase B alone is a non-trivial scientific contribution.
>
> Phase F requires capabilities that Phase B does not deliver: generative chemistry (Scout 2), molecular docking at AlphaFold scale, retrosynthetic analysis, the 15-layer Universal Net knowledge graph, multi-scale GNN architectures, temporal knowledge graphs for disease progression modeling, causal inference layers, federated learning across clinical partners. These are real research streams. They are formally tracked as Phase F. They are not silently deferred — they are committed work for 5+ years out.
>
> **Phase F entry conditions (advisory; binding criteria set at Phase F kickoff):**
> 1. Phase B Layer 5 (implementation) complete with V0-V6 validation cascade passing
> 2. Open-source Phase B platform released and adopted by external research groups
> 3. At least one pharma or biotech partnership entered for Phase B output validation
> 4. Funding secured for Phase F compute scale (graph database hosting, generative chemistry training)
> 5. CEO + CSO co-sign on Phase F entry, with new Phase F charter (Charter v2.0) co-authored
>
> **Phase B → Phase F transition:** when Phase F begins, the current 10 Decisions transition from "locked, current" to "Phase B locked, Phase F foundational." Phase F-specific Decisions (Decision 11 Knowledge Graph, Decision 12 Vulnerability/Selectivity, Decision 13 Generative Chemistry, Decision 14 Docking, Decision 15 Combinations, Decision 16 ADMET, Decision 17 ODE/Mechanistic Sim, Decision 18 RNA Velocity, Decision 19 Multi-Objective Ranking, Decision 20 Pharma Package + IP) will be drafted with the same discipline as Q1-Q10. Phase B Decisions are not invalidated; they are preserved as the substrate Decisions of the Phase F platform.
>
> **What §1.7 commits to (binding):**
> - Both phases are real
> - Phase F is not silently deferred into never-happening territory
> - Phase B does not subordinate to Phase F
> - The vision document corpus is canonical for Phase F scope
> - The 10 current Decisions are canonical for Phase B scope
> - The contradiction surfaced in v1.1 between §1.6 and §4 is resolved by phase-conditional framing, not by deleting either commitment

---

## 2. What Charter v1.2 Does NOT Change

For audit clarity, the following are EXPLICITLY unchanged from v1.1:

- **§0 Purpose** (preserved)
- **§1.1 Universal applicability** — U1-U3 success criteria stand
- **§1.2 Predictive validity** — V1-V4 success criteria stand
- **§1.3 Mechanistic interpretability** — I1-I3 success criteria stand
- **§1.4 Honest accounting** — H1-H4 success criteria stand
- **§1.5 Practical deployability** — P1-P3 success criteria stand
- **§2 Research Questions** — Q1-Q11 stand as-is (Q11 was added in v1.1 for A1-A6 architecture; remains, now scoped as Phase F)
- **§3 Termination Criteria** (preserved)
- **§5 Research Cadence** (preserved — Phase B Plan v2 stands)
- **§6 Output Structure** (preserved)
- **§7 Honest Constraints** (preserved)
- **§8 Provisional Architecture Sketch** (preserved — superseded operationally by L2.1 PROPOSED + Decisions 1-10, but Charter §8 text stands as the Phase B architectural target)
- **§9 Publication Strategy** (preserved)
- **§10 Process Discipline** (preserved — P15 only-honest-science and P16 _SUPERSEDED_ preservation are doubly binding under phase-conditional scope)
- **§11 What Happens Next** (preserved — updated by Master Handoff and Session Primer documents, not by Charter edits)

The 10 Decision Records, the L2.1 Substrate Specification, the Phase B Execution Plan v2, the Operational Decision Taxonomy v2, the Master Handoff, the Session Primer, and the 10 Q-syntheses are all UNCHANGED by Charter v1.2.

The drift findings 3-11 surfaced in the 2026-05-11 corpus-read audit are technical hygiene corrections to be applied in the Layer 1 LOCK pass per Step 3 of the 6-step plan. They are not Charter v1.2 changes.

---

## 3. Discipline Statement for v1.2

Charter v1.2 is issued because the disciplined Layer 1 work — corpus-wide audit by CSO on 2026-05-11 — surfaced a real contradiction between v1.1 §1.6 (added) and v1.1 §4 (not updated). Discipline working as intended: P15 (only honest science) caught the drift; P16 (preserve past work) frames the reconciliation; the operational decision taxonomy (CSO Amendment 1: scope reclassification requires CEO consent) governed the resolution.

This is not scope expansion. This is scope reconciliation with phase-conditional honesty.

The contradiction was real. The reconciliation is now explicit. Phase B is committed. Phase F is committed. Both honored.

---

## 4. Co-Sign

**CEO:** Prasad Akula, MS Bioinformatics, Northeastern University — _____________
**CSO:** Claude (current session) — co-signed 2026-05-11

**Tag prepared (pending CEO push to repo):** `fullest-vision-charter-v1-2-locked`

**P16 preservation manifest:**
- v1.1 file (currently named `INTERCEPTA_Fullest_Vision_Research_Charter_v1_0.md` but containing v1.1 content per drift Finding 1) → to be renamed `INTERCEPTA_Fullest_Vision_Research_Charter_v1_1_SUPERSEDED_by_v1_2_2026-05-11.md`
- This file → `INTERCEPTA_Fullest_Vision_Research_Charter_v1_2_2026-05-11.md`
- Vision documents → renamed to `INTERCEPTA_Phase_F_Future_Vision_Universal_Net_Specification_2026-03-29.md` and `INTERCEPTA_Phase_F_Future_Vision_Complete_Platform_2026-03.md` per 6-step plan Step 4

— Charter v1.2 PROPOSED 2026-05-11, awaiting CEO co-sign and lock.
