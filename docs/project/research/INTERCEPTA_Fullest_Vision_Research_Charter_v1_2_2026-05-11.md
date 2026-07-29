# INTERCEPTA Fullest Vision Research Charter v1.2

**Status:** PROPOSED Rev 2 for CEO co-sign. Once locked, supersedes v1.1.
**Date:** 2026-05-11
**Predecessor:** `INTERCEPTA_Fullest_Vision_Research_Charter_v1_1_SUPERSEDED_by_v1_2_2026-05-11.md` (per P16)
**Scope of this revision:** Three surgical changes only — §1.6 reframed as Phase F commitment; §4 rewritten as Phase B vs Phase F scope boundary; new §1.7 explicit phase table. All other sections of v1.1 unchanged.
**Rev 2 changes from Rev 1:** Three sets of corrections applied per CEO-mandated CSO verification pass (2026-05-11): §1.7 rows 4, 5, 9 precision; §4 enumeration expanded from 11 to 24 rows to match vis.pdf and vis2_doc.pdf scope; §1.7 Phase F entry authority explicitly specified.
**Authority:** CEO scope decision dated 2026-05-11 (Option γ phased scope). CSO concurs. Co-signed.

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
- Modify any of §1.1, §1.2, §1.3, §1.4, §1.5 (the 17 base success criteria — see §1.7 row 9 footnote)
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

**v1.2 reframe:** A1-A6 are reframed as the **Phase F autonomous learning system commitment**, with phase-conditional implementation status. The substantive content of A1-A6 is preserved verbatim — no goal is weakened, no commitment is dropped. What changes is the phase under which each commitment falls due.

**Operationally this means:**
- A1 (novel drug candidate ranking, generative chemistry) — Phase F deliverable. Architected by Phase F Decisions 11-20 (Knowledge Graph, Vulnerability/Selectivity, Generative Chemistry, Docking, Combinations, ADMET, ODE, RNA Velocity, Ranking, Pharma Package). Not committed for Phase B.
- A2 (continuous learning) — Phase F deliverable. Phase B trains and validates once; Phase F enables online updates.
- A3 (drift detection) — **PARTIALLY Phase B.** OOD detection (Charter §1.4 H3, Decision 5 v2 Layer 5.1-5.4 stack) covers prediction-time epistemic drift at the cell level. Distribution-shift-driven model-quality drift over time (deployment monitoring) is Phase F.
- A4 (active learning) — Phase F deliverable. Phase B performs human-directed validation per Decision 6 v2 cascade.
- A5 (operational autonomy) — Phase F deliverable. Phase B is research-grade pipeline with human-supervised stages.
- A6 (self-aware meta-confidence) — **PARTIALLY Phase B.** Conformal prediction (Decision 5 v2 Layer 5.3) and Deep Ensembles (5.2) provide statistical uncertainty quantification per prediction. Meta-cognition over reliability across novel scenarios (system-level "do I know what I don't know?") is Phase F.

The "Research and invent where existing methods inadequate" clause stands as a Phase F commitment. INTERCEPTA Phase F will require novel research in multi-scale GNNs, temporal knowledge graphs, causal inference on biological graphs, federated learning for clinical data, and net-constrained generative chemistry per vision document Part 7. These are not vague aspirations — they are formally tracked Phase F research streams (see §4 scope boundary table for explicit phase classification of each).

**The success bar across both phases:** 17 base success criteria (U1-3 + V1-4 + I1-3 + H1-4 + P1-3 = 17) + 6 autonomous criteria (A1-A6) = **23 total Fullest Vision criteria**. Phase B target = 17 base full + Phase-B-partial of A3 and A6 (specifically: A3 cell-level epistemic drift detection per Decision 5 v2 + A6 statistical uncertainty calibration per conformal/ensemble layer). Phase F target = remaining: A1, A2, A4, A5 full + completion of A3 deployment-monitoring layer + completion of A6 meta-cognition layer. Both phases together = Fullest Vision.

(**Drift catch noted:** v1.1 §1.6 stated "ALL 24 criteria above." Correct count is 23 — the arithmetic is 3+4+3+4+3+6 = 23. v1.2 corrects this arithmetic error.)

This change is the operative resolution of the §1.6 vs §4 contradiction.

---

### Change 2 — §4 rewritten as Phase B vs Phase F scope boundary (expanded enumeration)

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

**v1.2 Rev 2 replacement §4:**

> ## 4. Phase B vs Phase F Scope Boundary (Anti-Scope-Creep)
>
> INTERCEPTA's fullest vision spans two phases. Phase B (current, 2-4 year research program) and Phase F (5+ year full discovery platform) deliver different scope. The following items are scope-conditional, not absolutely out-of-scope. Each item below names the phase under which it falls due and cites the source document that anchors the scope item.
>
> The items listed here are *anti-scope-creep* for Phase B specifically — Phase B work that drifts into a Phase F item must be flagged in the corresponding Decision Record under cross-decision implications, refused if it cannot be deferred, or re-classified as scope expansion requiring CEO consent per Operational Decision Taxonomy v2 Amendment 1. Phase F work, when it begins, will treat these same items as in-scope.
>
> | # | Scope Item | Source Anchor | Phase B (2-4 yr) | Phase F (5+ yr) | Notes |
> |---|---|---|---|---|---|
> | 1 | **Drug structure prediction / generation** (de novo molecule design) | vis2_doc Part 3.3 Scout 2; vis.pdf Part 7 novel tech 5 | OUT OF SCOPE | IN SCOPE | Phase F Decisions 13 (Generative Chemistry), 16 (ADMET). Net-constrained generation distinguishes from unconstrained chemical generation. |
> | 2 | **Federated learning across clinical institutions** | vis.pdf Part 7 novel tech 4 | OUT OF SCOPE — single-institution only | IN SCOPE | Phase F architecture enables clinical-data integration without centralization. |
> | 3 | **Causal inference on biological graphs** | vis.pdf Part 7 novel tech 3 | OUT OF SCOPE — predict and rank only | IN SCOPE | Phase F transforms correlational edges (gene-disease association) into causal edges (target → therapeutic effect). |
> | 4 | **In vivo validation** (wet-lab, animal models, clinical trials) | vis2_doc Part 11 Phase 5; vis2_doc Part 12.4 | OUT OF SCOPE — computational only | IN SCOPE (collaborative model) | Phase F partnership architecture: INTERCEPTA does not become a wet lab; partners with academic + pharma labs for experimental validation. |
> | 5 | **Non-transcriptomic data modalities** (proteomics, metabolomics, epigenomics as primary inputs) | vis.pdf Part 2 Layers 3, 8, 12 | OUT OF SCOPE — transcriptomic primary | IN SCOPE | Phase F integrates Layer 3 (Proteome, ~570K UniProt entries), Layer 8 (Metabolome, ~220K HMDB metabolites), Layer 12 (Epigenome, ENCODE + Roadmap). |
> | 6 | **Clinical decision support** (patient-facing tools, EMR integration) | not in vision documents — neither phase commits | OUT OF SCOPE | OUT OF SCOPE in research charter | Clinical product layer is downstream of both phases. Vision document Part 9.2 names pharma + biotech as primary delivery, not direct clinical. Out of charter scope; not out of business scope (potential future product spin-out). |
> | 7 | **Real-time / streaming analysis** | vis2_doc Part 12.1 self-improving loop; A2 + A5 | OUT OF SCOPE — batch only | IN SCOPE | Phase F operational autonomy (A5) requires near-real-time ingestion. Phase B batch is sufficient. |
> | 8 | **The 15-layer Universal Human Biology Net** (~3M nodes, ~10-50M edges, ~50 public DB sources) | vis.pdf Parts 2-3 entire | OUT OF SCOPE as platform substrate | IN SCOPE (CANONICAL) | Phase F substrate. Phase B uses targeted database subsets (CCLE/GDSC + scRNA-seq atlases + drug-target databases per Decision 9 v2 cached embeddings) as needed for L7 head + V0-V6 cascade. Phase B does not build the unified knowledge graph. |
> | 9 | **6-Scout Parallel Discovery System** (Database / Generative / Combination / Network Perturbation / Evolutionary / Cross-Disease Transfer) | vis2_doc Part 3.3 | OUT OF SCOPE — Phase B = L7 cell-response evaluator only | IN SCOPE (CANONICAL) | Phase F parallel scout architecture. Phase B builds the cell-level drug response prediction layer that Phase F scouts will call as their evaluation function. Scouts are not Phase B. |
> | 10 | **Scout 1: Database Search** (ChEMBL 2.4M + PubChem 118M + ZINC 750M target-based retrieval) | vis2_doc Part 3.3 | OUT OF SCOPE | IN SCOPE | Phase F retrieval scout. Phase B has no automated ChEMBL/PubChem/ZINC search; uses GDSC drugs only. |
> | 11 | **Scout 2: Generative Design** (diffusion + transformer + GNN-based molecule generation) | vis2_doc Part 3.3 | OUT OF SCOPE | IN SCOPE | Phase F generative scout. See row 1. |
> | 12 | **Scout 3: Combination Explorer** (permutation enumeration; ZIP + Bliss + Loewe + HSA synergy scoring) | vis2_doc Part 3.3; Part 4 Simulation Layer D | OUT OF SCOPE | IN SCOPE | Phase F combination scout + Simulation Stack Layer D synergy scoring. KAALCURA-derived combination scoring partially exists in your Phase 0 work but full integration is Phase F. |
> | 13 | **Scout 4: Network Perturbation** (simulates net response to candidate; identifies compensation pathways) | vis2_doc Part 3.3 | OUT OF SCOPE | IN SCOPE | Phase F network perturbation scout. Requires the 15-layer Net (row 8) as substrate. |
> | 14 | **Scout 5: Evolutionary Optimizer** (systematic chemical-structure mutation + variant testing) | vis2_doc Part 3.3 | OUT OF SCOPE | IN SCOPE | Phase F evolutionary scout. |
> | 15 | **Scout 6: Cross-Disease Transfer** (molecules from prior diseases tested against current disease via shared net nodes) | vis2_doc Part 3.3; Part 12.1 self-improving loop | OUT OF SCOPE in this form | PARTIAL Phase B / IN SCOPE Phase F | Phase B's V6 cross-disease prediction (Decision 6 v2, Decision 8 v2) is the **prediction** layer of cross-disease transfer; Scout 6 in Phase F is the **discovery** layer that uses the prediction. Different functions; same conceptual axis. |
> | 16 | **Stage 2: Vulnerability and Selectivity Mapping** (disease-specific vs healthy-shared node identification; DepMap + GTEx + tumor expression integration) | vis2_doc Part 4 Stage 2 | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F Decision 12 (Vulnerability/Selectivity Mapping). Phase B uses GDSC cell-line drug response labels directly; no automated vulnerability mapping. |
> | 17 | **Simulation Stack Layer A: Molecular Binding / Docking** (AutoDock Vina + AlphaFold structures) | vis2_doc Part 4 Stage 4 Layer A | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F Decision 14 (Docking). Phase B uses drug-target labels from ChEMBL/DrugBank as features, not structure-based docking. |
> | 18 | **Simulation Stack Layer B: Cell Population Sensitivity** (KAALCURA biological axes + cell-level drug response prediction) | vis2_doc Part 4 Stage 4 Layer B; Part 5.2 KAALCURA | **IN SCOPE — this IS the Phase B core** | IN SCOPE (extends to all population types) | Phase B Decision 4 v2 L7 6-slot head IS the cell-level drug response evaluation function. Phase F extends to additional cell-population types (immune cells in TME, resistant cells via RNA velocity per row 21). |
> | 19 | **Simulation Stack Layer C: Disease Dynamics** (two-population ODE + PK/PD pharmacokinetics + long-term outcome simulation) | vis2_doc Part 4 Stage 4 Layer C; Part 5.3 | OUT OF SCOPE in Phase B platform | IN SCOPE (CANONICAL) | Phase F Decision 17 (ODE/Mechanistic Simulation). Your existing Phase 0 ODE work (validated against CHAARTED, LATITUDE, PROfound, PROpel) is preserved as Phase F-foundational pre-work, not as a Phase B platform component. |
> | 20 | **Simulation Stack Layer D: Combination Synergy** (ZIP + Bliss + Loewe + HSA consensus scoring) | vis2_doc Part 4 Stage 4 Layer D | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F Decision 15 (Combinations + Synergy). Phase B may evaluate single drugs only. |
> | 21 | **RNA Velocity Time Machine** (scVelo + CellRank2 for pre-resistant population identification on Day 1) | vis2_doc Part 5.1; Part 11 Phase 2 | OUT OF SCOPE in Phase B platform | IN SCOPE (CANONICAL) | Phase F Decision 18 (RNA Velocity). Your existing Phase 0 capability is preserved as Phase F-foundational. Phase B L7 head predicts cell-level response without temporal-trajectory awareness. |
> | 22 | **Simulation Stack Layer E: Safety / ADMET prediction** (SwissADME + pkCSM + ADMET-AI for liver/kidney/cardiac/CNS toxicity + bioavailability + metabolic stability) | vis2_doc Part 4 Stage 4 Layer E; Part 10.1 | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F Decision 16 (ADMET / Synthesizability). |
> | 23 | **Simulation Stack Layer F: Synthesizability** (ASKCOS retrosynthesis + AIZYNTHFINDER; synthetic complexity scoring) | vis2_doc Part 4 Stage 4 Layer F; Part 10.1 | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F Decision 16 (ADMET / Synthesizability) — combined with row 22. Manufacturing-feasibility filtering of generated molecules. |
> | 24 | **Multi-Objective Pareto Ranking** (Efficacy 30% + Selectivity 25% + Safety 20% + Resistance Coverage 15% + Novelty 5% + Synthesizability 5%) | vis2_doc Part 4 Stage 5 | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F Decision 19 (Multi-Objective Ranking). Weighting scheme is currently proposed in vis2_doc; will require evidence-based revisitation in Phase F Decision 19. |
> | 25 | **Diagnostic and Predictive Layer** (current disease identification from molecular signatures; future disease risk prediction from pre-disease states; future-pathogen modeling) | vis2_doc Part 6 (6.1, 6.2, 6.3) | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F extension beyond drug discovery into early diagnosis. Conceptual reuse of the 15-layer Net for diagnostic patterns. |
> | 26 | **Microbiome + Tumor Microenvironment Integration** (Human Microbiome Project + gut-gene interactions + immune cells in TME) | vis2_doc Part 12.2; vis.pdf Layers 10, 11 | OUT OF SCOPE | IN SCOPE (CANONICAL) | Phase F integration of vis.pdf Layer 10 (Immune) + Layer 11 (Microbiome). Critical for immunotherapy drug discovery per vision document. |
> | 27 | **Regulatory Pathway Awareness from Day 1** (FDA / EMA pathway flagging; companion diagnostic identification; combination simplification for FDA-approved components) | vis2_doc Part 12.3 | OUT OF SCOPE | IN SCOPE | Phase F Decision 20 (Pharma Package + IP) integration. Phase B does not consider regulatory pathway. |
> | 28 | **Multi-Scale Graph Neural Networks** (atoms → cells → organs → organisms representations) | vis.pdf Part 7 novel tech 1 | OUT OF SCOPE | IN SCOPE (RESEARCH STREAM) | Phase F novel research. Requires novel architecture invention. |
> | 29 | **Temporal Knowledge Graphs** (time-varying edges; integrates with RNA velocity per row 21) | vis.pdf Part 7 novel tech 2 | OUT OF SCOPE | IN SCOPE (RESEARCH STREAM) | Phase F novel research. Standard KGs are static; biology is dynamic. |
> | 30 | **Pharma Deliverable Package** (10-item: SMILES + 3D structure + mechanism + clinical outcomes + resistance profile + combination rationale + safety profile + synthesis route + novelty confirmation + suggested trial design) | vis2_doc Part 9.1 | OUT OF SCOPE — Phase B delivers V0-V6 research validation only | IN SCOPE (CANONICAL) | Phase F Decision 20 (Pharma Package + IP). Phase F end-to-end deliverable. |
> | 31 | **Disease Expansion Sequence** (mCRPC Round 1 → AML Round 2 → NSCLC Round 3 → PDAC Round 4 → Alzheimer's Round 5 → Drug-Resistant TB Round 6 → rare diseases / emerging pathogens / future diseases Round 7+) | vis2_doc Part 7.2 | PARTIAL — Phase B Plan v2 covers mCRPC + AML cell-response validation only | IN SCOPE FULL | Phase B handles the cell-level drug response prediction for ≥2 therapeutic areas (V6 binding criterion). Phase F handles full disease-by-disease novel-molecule discovery sequence. |
> | 32 | **Open Collaboration Architecture** (academic co-author validation; published disease nets; API access for researchers) | vis2_doc Part 12.4 | PARTIAL — Phase B per Decision 10 v2 open-source release tied to V0/V3/V6 | IN SCOPE FULL | Phase B: open-source code + permissive license + tied release schedule. Phase F: published disease nets + co-author validation model + researcher API. |
>
> **Phase B anti-scope-creep enforcement:** if a Phase B work item starts requiring any "OUT OF SCOPE" capability above, it must be flagged in the Decision Record under cross-decision implications and escalated to CEO. Quiet scope creep is the failure mode this section guards against.
>
> **Phase F advance work permitted:** Phase B may produce Phase F-enabling artifacts (e.g., the L7 cell-response evaluator becomes Phase F Simulation Stack Layer B per row 18; Decision 6 v2 V6 cross-disease prediction becomes Phase F Scout 6 prediction substrate per row 15) IF AND ONLY IF such work does not delay Phase B deliverables. Phase B does not subordinate to Phase F.
>
> **What counts as Phase F-foundational pre-work (preserved, not active Phase B):** Your existing Phase 0 KAALCURA work (R_prolif, R_emt, R_ddr biological axes — see row 18), two-population ODE simulation engine (row 19), 15-drug mCRPC library with PK parameters, scVelo RNA velocity infrastructure (row 21), and synergy scoring (ZIP + Bliss + Loewe + HSA per row 20). These are CANONICAL Phase F foundational layers, preserved as foundational substrate for Phase F kickoff. They are not being thrown away. They are not being activated as Phase B platform components either — they remain Phase 0 pre-work for the Phase F program.

---

### Change 3 — New §1.7 Phase B vs Phase F Table (corrections from Rev 1 verification)

**v1.2 adds §1.7 immediately after §1.6:**

> ### 1.7 Phase B vs Phase F (Phased Scope Architecture)
>
> INTERCEPTA's fullest vision is two-phased. Both phases are real. Both phases are committed. Phase B does not invalidate Phase F. Phase F does not invalidate Phase B.
>
> **Phase B (current, 2-4 year research program) is canonical for:** Charter v1.2 sections 1.1-1.5 (U1-3, V1-4, I1-3, H1-4, P1-3 — 17 base success criteria), the 10 Decision Records currently locked, the Phase B Execution Plan v2 14 artifacts, and the Layer 1-4 substrate / L7 head / OOD / validation cascade / interpretability / universality / compute / open-source axes. Phase B's deliverable is the **drug response prediction layer** of INTERCEPTA — cell-level, single-cell-resolution, V0-V6 validated, cross-disease universality demonstrated per Decision 8 v2 4-paradigm comparison, mechanism-interpreted, with open-source release per Decision 10 v2.
>
> **Phase F (5+ years out, full discovery platform) is canonical for:** Charter v1.2 section 1.6 A1-A6 (6 autonomous success criteria), the 15-layer Universal Human Biology Net per `INTERCEPTA_Phase_F_Future_Vision_Universal_Net_Specification_2026-03-29`, the 5-stage pipeline + 6-scout parallel discovery system + multi-objective ranking + pharma deliverable package per `INTERCEPTA_Phase_F_Future_Vision_Complete_Platform_2026-03`, and the novel-research bets (multi-scale GNNs, temporal knowledge graphs, causal inference on biological graphs, federated learning for clinical data, net-constrained generative chemistry per vision document Part 7). Phase F's deliverable is the **full drug discovery platform** — novel molecule generation, ADMET/synthesizability filtered, ranked, packaged for pharma Phase I trial entry.
>
> **The phase relationship:**
>
> | # | Dimension | Phase B (2-4 yr) | Phase F (5+ yr) |
> |---|---|---|---|
> | 1 | **Top-level deliverable** | Drug response prediction for ANY disease at cell-level resolution | Novel drug molecules (existing-drug ranking + generative chemistry + combination discovery) for ANY disease, Phase-I-ready |
> | 2 | **Input scope** | Transcriptomic (scRNA-seq primary; bulk RNA-seq via Q3 transfer) | Multi-omic: transcriptomic + proteomic (Layer 3) + metabolomic (Layer 8) + epigenomic (Layer 12) + microbiome (Layer 11) + spatial (Layer 13) |
> | 3 | **Output scope** | Ranked existing drug recommendations per (cell population, drug) + mechanism trace + OOD/uncertainty per Decision 5 v2 + cross-disease generalization per Decision 6 v2 V6 | Phase B output + novel molecule SMILES/3D structure + binding affinity + ADMET + synthesizability + combination scoring + pharma trial design package per §4 row 30 |
> | 4 | **Substrate** | Cell encoder per Decision 1 v2: 1 default substrate (scFoundation) + 3 co-equal baselines (PCA, scTOP, scVI/scANVI/MrVI) with decision rules deferred to Layer 5 ablation (≥5pp AUROC for FM keep; ≤2pp for FM demote; scenario-dependent per-scenario selection logic). ≥25% hyperparameter budget to scTOP-style Baseline B is BINDING per Souza-Mehta methodological bar (Decision 8 v2 Commitment 5). Default 512-dim cell embedding interface per Decision 1 v2 Commitment 4. | Phase B substrate UNCHANGED + 15-layer Universal Net knowledge graph + AlphaFold 200M structures + PDB experimental + STRING/BioGRID/IntAct interactome. Substrate decision (FM vs parameter-free) carries over from Phase B Layer 5 empirical outcome. |
> | 5 | **L7 / Cell-response architecture** | Decision 4 v2 modular 6-slot architecture: Slot 1 cell encoder (= Decision 1 substrate) + Slot 2 chemCPA modular drug encoder + Slot 3 chemCPA M+S perturbation network + Slot 4 GEARS-style graph-augmented module + Slot 5 mode-collapse mitigation (diversity loss default) + Slot 6 PaSCient-style patient-level attention aggregation. Compatible with Decision 5 v2 N=5 ensembleability. | Phase B 6-slot L7 head becomes **Simulation Stack Layer B (Cell Population Sensitivity)** of the Phase F 5-stage pipeline — see §4 row 18. It is the cell-level evaluation function that ALL six Phase F Scouts (database retrieval, generative design, combination explorer, network perturbation, evolutionary optimizer, cross-disease transfer) call to test candidate molecules against cell populations. L7 is not Scout 1 (that is target-based database retrieval per §4 row 10); L7 is the evaluator that runs under all scouts. |
> | 6 | **Validation** | Decision 6 v2 V0-V6 cascade with binding floor criteria: V0 within-dataset signal-above-zero; V1 IMPROVE cross-dataset AUROC ≥0.65; V2 organoid AUROC ≥0.65; V3 Tang 2022 tumor AUROC ≥0.77 BINDING; V4 Tang 2022 PDX RMSE ≤0.11 TNBC + Kim 2020 PDXGEM 24.5% concordance reporting; V5 DiSyn architecture + ECE ≤0.05; V6 ≥0.65 AUROC across ≥2 therapeutic areas BINDING (Decision 8 v2 commitment 3). | Phase B V0-V6 cascade UNCHANGED + experimental partner validation (Part 12.4 open collaboration) + clinical trial outcome feedback loop (Part 12.1 self-improving) + cross-disease molecular transfer evaluation (Scout 6). |
> | 7 | **Compute** | Northeastern Explorer single-A100 envelope per Decision 9 v2. SLURM job arrays. Cached embeddings in `/scratch/akula.pra/INTERCEPTA/embeddings/`. AWS/GCP burst capacity requires per-occurrence CEO approval (≤5% target). | Phase F-scale: Northeastern + AWS/GCP burst for generative chemistry training, AlphaFold-scale structure handling at scale, graph database hosting (~3M nodes, ~50M edges via Neo4j / Amazon Neptune / equivalent per Phase F Decision 11). |
> | 8 | **Open source** | Phase B per Decision 10 v2: permissive-cluster default (BSD-3 / MIT / Apache-2.0); GPL-3 conditional handling for Harmony + Seurat v3 (Strategy A academic-only / B subprocess wrap / C alternative); CC BY-NC-ND DiSyn excluded from default permissive release; phased release tied to V0/V3/V6 validation milestones. | Phase F per vision document Part 12.4 Open Collaboration Architecture: disease nets open-published; candidate molecules patent-licensable to pharma partners (vision document Part 8.2: "discovery method is open; the discovered molecule can be proprietary"). |
> | 9 | **Success bar** | 17 base criteria full (U1-3, V1-4, I1-3, H1-4, P1-3) + Phase-B-partial of A3 (cell-level epistemic drift detection per Decision 5 v2) + Phase-B-partial of A6 (statistical uncertainty quantification per conformal/ensemble layer). Phase B success = "Cross-disease drug response prediction works at V6 floor, mechanism-interpretable, with calibrated uncertainty." | Completion of A1, A2, A4, A5 + completion of A3 (deployment-monitoring layer) + completion of A6 (meta-cognition layer). 23 total Fullest Vision criteria across both phases. |
> | 10 | **Honest framing** | "Predict which drugs work, validated across diseases, with mechanism explanation and calibrated uncertainty" | "Discover novel drug molecules, full pipeline to pharma Phase I, for any disease past/present/future" |
>
> **Why this phasing:**
>
> Phase B is the architecture that can be built defensibly in 2-4 years on Northeastern single-A100 with the current evidence base from the 10 Decisions. It delivers a real, valuable, publishable, open-source-releasable computational drug response prediction platform that the field genuinely lacks. Phase B alone is a non-trivial scientific contribution.
>
> Phase F requires capabilities that Phase B does not deliver: generative chemistry (Scout 2 per §4 row 11), molecular docking at AlphaFold scale (Layer A per §4 row 17), retrosynthetic analysis (Layer F per §4 row 23), the 15-layer Universal Net knowledge graph (per §4 row 8), multi-scale GNN architectures (per §4 row 28), temporal knowledge graphs for disease progression modeling (per §4 row 29), causal inference layers (per §4 row 3), federated learning across clinical partners (per §4 row 2). These are real research streams. They are formally tracked as Phase F in §4. They are not silently deferred — they are committed work for 5+ years out.
>
> ---
>
> ### 1.7.1 Phase F Entry Conditions and Authority
>
> Phase F entry is a CEO+CSO co-decision per Charter §5.3 GO/NO-GO discipline, but the magnitude of Phase F entry (scope expansion to a 5+ year program, new Decision Records 11-20, new Charter v2.0) warrants explicit specification of authority, certification, and disagreement protocol beyond §5.3 baseline.
>
> **Phase F entry conditions (binding):**
>
> | # | Condition | Certification Authority | Co-Confirmation |
> |---|---|---|---|
> | 1 | Phase B Layer 5 (implementation) complete with V0-V6 validation cascade passing per Decision 6 v2 floor criteria | CSO certifies via a Layer 5 Final Decision Record summarizing V0-V6 outcomes | CEO confirms via signed acknowledgment of V0-V6 outcomes |
> | 2 | Open-source Phase B platform released and adopted by ≥1 external research group (community uptake signal) | CSO certifies via release artifacts + ≥1 external citation/fork/issue | CEO confirms |
> | 3 | ≥1 pharma or biotech partnership entered for Phase B output validation | CEO certifies (business-side decision) | CSO confirms scientific terms |
> | 4 | Phase F compute scale funding secured (graph database hosting + generative chemistry training compute, estimated ≥$500K annual) | CEO certifies (business-side decision) | CSO confirms technical adequacy |
> | 5 | Charter v2.0 co-authored by CEO + CSO defining Phase F operational scope | CEO + CSO co-author | Both sign |
>
> **Disagreement protocol:**
>
> If CEO and CSO disagree on whether a Phase F entry condition is met, the question returns to evidence per Charter §10 P15 (only honest science). Specifically:
> - For condition 1 (V0-V6 outcomes): Layer 5 evidence is dispositive. If V0-V6 numbers do not meet floor criteria, condition 1 is NOT met regardless of either party's preference.
> - For conditions 2-4 (external signals + business decisions): if dispute persists for >90 days, the conflict is recorded in a Decision Record (per Operational Decision Taxonomy v2 Amendment 1) and Phase F entry is deferred pending resolution.
> - For condition 5 (Charter v2.0): co-authorship requirement is BINDING. If either party refuses to co-sign, Phase F does not begin. Charter v2.0 itself must be drafted with the same discipline as v1.0 (anchor evidence, decision records, multi-cycle review).
>
> **Deferral vs cancellation framework:**
>
> Phase F entry has three possible outcomes:
> - **Entry approved:** all five conditions met; Charter v2.0 locked; Phase F Decision Records 11-20 research streams begin.
> - **Deferral:** one or more conditions not yet met (typically funding or partnership); Phase F entry queued pending condition fulfillment. Default state if Phase B completes successfully but Phase F prerequisites are partial. Deferral does NOT cancel Phase F vision; Phase F remains canonical scope.
> - **Cancellation:** Phase F vision is **falsified by Phase B evidence** (e.g., Layer 5 V0-V6 demonstrates Phase B platform cannot achieve universality, which falsifies the foundation Phase F is built on). Cancellation requires a new Decision Record explicitly classifying which evidence falsifies which Phase F commitment, co-signed by CEO + CSO, and produces a revised Charter v1.3 narrowing the fullest vision to what evidence supports.
>
> **Default state:** unless Phase F is explicitly cancelled per the above, Phase F vision remains canonical scope for INTERCEPTA's fullest vision. Time does not silently cancel Phase F. Charter v1.2 commits to Phase F existing as real future work; only an explicit Decision Record can revise that commitment.
>
> ---
>
> ### 1.7.2 Phase B → Phase F Transition Mechanics
>
> When Phase F begins, the current 10 Decisions transition from "locked, current" to "Phase B locked, Phase F foundational." Phase F-specific Decisions will be drafted with the same discipline as Q1-Q10. Phase B Decisions are not invalidated; they are preserved as the substrate Decisions of the Phase F platform. The Phase F Decision Record numbering will continue from 11:
>
> | Phase F Decision # | Topic | Source anchor |
> |---|---|---|
> | 11 | Knowledge Graph Architecture (15-layer Net infrastructure) | §4 row 8 |
> | 12 | Vulnerability and Selectivity Mapping | §4 row 16 |
> | 13 | Generative Chemistry (net-constrained molecule generation) | §4 row 11 |
> | 14 | Molecular Docking / Binding | §4 row 17 |
> | 15 | Combinations and Synergy Discovery | §4 row 12, 20 |
> | 16 | ADMET / Synthesizability | §4 rows 22, 23 |
> | 17 | Two-Population ODE / Mechanistic Simulation | §4 row 19 |
> | 18 | RNA Velocity Time Machine | §4 row 21 |
> | 19 | Multi-Objective Pareto Ranking | §4 row 24 |
> | 20 | Pharma Deliverable Package + IP Architecture | §4 rows 27, 30 |
>
> (Additional Phase F Decisions may be needed for Scouts 3-6, Diagnostic/Predictive Layer, Microbiome/TME, Multi-Scale GNNs, Temporal KGs, Federated Learning. Final Phase F Decision count to be determined at Phase F kickoff.)
>
> **What §1.7 commits to (binding):**
> - Both phases are real
> - Phase F is not silently deferred into never-happening territory
> - Phase B does not subordinate to Phase F
> - The vision document corpus is canonical for Phase F scope
> - The 10 current Decisions are canonical for Phase B scope
> - The contradiction surfaced in v1.1 between §1.6 and §4 is resolved by phase-conditional framing, not by deleting either commitment
> - Phase F entry authority, disagreement protocol, and deferral/cancellation framework are explicit

---

## 2. What Charter v1.2 Does NOT Change

For audit clarity, the following are EXPLICITLY unchanged from v1.1:

- **§0 Purpose** (preserved)
- **§1.1 Universal applicability** — U1-U3 success criteria stand
- **§1.2 Predictive validity** — V1-V4 success criteria stand
- **§1.3 Mechanistic interpretability** — I1-I3 success criteria stand
- **§1.4 Honest accounting** — H1-H4 success criteria stand
- **§1.5 Practical deployability** — P1-P3 success criteria stand
- **§2 Research Questions** — Q1-Q11 stand as-is (Q11 was added in v1.1 for A1-A6 architecture; remains, now scoped as Phase F per §1.6 reframe)
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

The Rev 2 revision applied to this draft caught:
- 3 wording precision issues in §1.7 rows 4, 5, 9 (Decisions 1 v2, 4 v2, 8 v2 cross-consistency)
- ~13 under-enumerated Phase F scope items in §4 (vis.pdf novel technologies, vis2_doc.pdf 6 Scouts, 5-Stage Pipeline layers, simulation stack layers A-F, pharma deliverable specification, disease expansion sequence, microbiome/TME, regulatory awareness)
- Phase F entry authority specification gap (now explicit per §1.7.1)
- v1.1 arithmetic error: "24 criteria" → actual count 23 (3+4+3+4+3+6)

The contradiction was real. The reconciliation is now explicit. Phase B is committed. Phase F is committed. Both honored. Both scoped with full enumeration of source-anchored items.

---

## 4. Co-Sign

**CEO:** Prasad Akula, MS Bioinformatics, Northeastern University — _____________
**CSO:** Claude (current session) — co-signed 2026-05-11

**Tag prepared (pending CEO push to repo):** `fullest-vision-charter-v1-2-locked`

**P16 preservation manifest:**
- v1.1 file (currently named `INTERCEPTA_Fullest_Vision_Research_Charter_v1_0.md` but containing v1.1 content per drift Finding 1) → to be renamed `INTERCEPTA_Fullest_Vision_Research_Charter_v1_1_SUPERSEDED_by_v1_2_2026-05-11.md`
- This file → `INTERCEPTA_Fullest_Vision_Research_Charter_v1_2_2026-05-11.md`
- Vision documents → renamed to `INTERCEPTA_Phase_F_Future_Vision_Universal_Net_Specification_2026-03-29.md` and `INTERCEPTA_Phase_F_Future_Vision_Complete_Platform_2026-03.md` per 6-step plan Step 4

— Charter v1.2 PROPOSED Rev 2, 2026-05-11, awaiting CEO co-sign and lock.
