# INTERCEPTA L2.2 Session Primer
## Fresh CSO Kickoff for Writing the L7 6-Slot Drug Response Architecture Spec

**Status:** Operational primer for the L2.2 writing session.
**Created:** 2026-05-11 by CSO Claude
**Read order:** Read AFTER `INTERCEPTA_Master_Handoff_v2_0_2026-05-11.md`. This primer is the L2.2-specific kickoff.
**Length:** ~3,000 words (focused, not comprehensive — comprehensive context is in Master Handoff v2.0)

---

## 1. What L2.2 Is

L2.2 is the **L7 6-Slot Drug Response Architecture Specification**. It is the second artifact of Phase B Layer 2 work per Phase B Plan v2 (L2.1 substrate spec already written; L2.2 builds the drug response head that consumes the substrate; L2.3 OOD stack and L2.4 interpretability follow).

**L2.2 specifies how the L7 layer of INTERCEPTA is built** — taking the 512-dim cell embedding from L2.1's substrate, the chemical embedding of a drug, optional biological priors (gene-gene graphs, GO ontology, drug-target ontology), and producing a per-cell drug response prediction (continuous or classification). Patient-level aggregation collapses cell-level predictions to patient-level via PaSCient-style attention pooling.

**Target:** 12-15K words per Phase B Plan v2. ~1 session of focused writing.

**Format:** Same discipline as L2.1: §0 Identification → §1 Architecture overview → §2-§7 each slot specified in detail with PyTorch class skeletons → §8 Cross-decision implications → §9 Pass criteria → §10 What L2.2 does NOT lock → §11 Document provenance + discipline check → §12 Appendix.

**Filename:** `INTERCEPTA_FV_L2_2_L7_Drug_Response_Architecture_Specification_2026-05-XX.md` (replace XX with write date).

---

## 2. The 6 Slots (Architecture Sketch — From Decision 4 v2)

```
Input: scRNA-seq cells × drug perturbations × covariates
                            ↓
[Slot 1: Cell Encoder]
  Decision 1 v2 substrate (scFoundation default; scTOP/scVI/PCA co-equal baselines)
  Output: 512-dim cell embedding (via substrate.project_to_canonical)
                            ↓
CPA-style Disentangled Latent
  Separates: perturbation effect | cell type | dose | time | species | patient
                            ↓
Composition Framework
                            ↑
[Slot 2: Drug Molecule Encoder G]
  chem-FM candidates (MoLFormer, ChemBERTa, Uni-Mol) + RDKit baseline
  Output: chemical embedding
                            ↑
[Slot 3: Perturbation Network M + S]
  M: maps chemical embedding to latent perturbation effect (chemCPA)
  S: amortized dosage scaler (chemCPA)
                            +
[Slot 4: Graph-Augmented Module]
  GEARS-style attention over biological priors:
    - Gene-gene co-expression graph
    - GO ontology graph
    - Drug-target ontology (DrugBank/TWOSIDES)
  Provides biological prior signal for cross-disease (V6) generalization
                            ↓
[Slot 5: Mode Collapse Mitigation]
  Default: diversity loss term in training objective
  Alternatives: energy-based training; mixture-of-experts decoder
                            ↓
CPA-style Decoder
                            ↓
Cell-level perturbation predictions
                            ↓
[Slot 6: Patient-Level Aggregation]
  PaSCient-style attention pooling (Q8 anchor 3)
  Default; alternatives: mean pooling, max pooling, learned weighted pooling
                            ↓
Patient-level drug response prediction
```

This is the diagram from Decision 4 v2 §"L7 Architecture Diagram." L2.2's job is to specify each of the 6 slots in full implementation detail, including PyTorch class skeletons, hyperparameter defaults, ablation infrastructure, and cross-slot interaction patterns.

---

## 3. Anchor Re-Read Status — SATISFIED

Per Phase B Plan v2 anchor re-read discipline ("CSO must re-read anchor papers in the current session before writing spec; no memory-extrapolation across sessions"), the L2.2 trigger is **SATISFIED** in the 2026-05-11 corpus-read audit session.

CSO read in full primary-source form in that session:
1. **CPA** — Lotfollahi et al. 2023, *Mol Syst Biol* (Meta/Helmholtz; MIT license). Compositional VAE backbone with disentangled drug embeddings.
2. **chemCPA** — Hetzel et al. 2022, NeurIPS. Modular chemical-encoder slot enabling unseen-drug prediction.
3. **GEARS** — Roohani et al. 2024, *Nat Biotechnol*. Graph-augmented perturbation prediction with gene-gene + GO ontology.
4. **PaSCient** — Liu et al. 2024-2026, ICML / *Nat Methods*. Patient-level attention aggregation; 24.3M cells / 5,000+ patients evaluated.
5. **scGen** — Lotfollahi et al. 2019, *Nat Methods*. Latent-space arithmetic captures perturbation effects at R²=0.954.
6. **sci-Plex** — Srivatsan et al. 2020, *Science*. ~650K cells, 188 drugs at 4 doses — the primary perturbation benchmark dataset for L7 training.
7. **PaccMann** — Manica et al. 2019. Drug-target prediction with attention; ~1-10M params.
8. **DeepCDR** — Liu et al. 2020. Drug response prediction baseline; ~1-10M params.

**You do NOT need to re-read these papers** unless materially modifying scope. If you need to re-read, the anchor notes are in `/mnt/project/` (or `~/INTERCEPTA/docs/research/literature/` on local Mac).

**You DO need to re-read** if:
- You introduce a new architecture or paper not in this list
- You modify a Decision 4 v2 commitment (which would require co-bound Decision Record amendment, not unilateral L2.2 spec change)
- You uncover a contradiction or ambiguity in any of these 8 anchor papers vs Decision 4 v2

---

## 4. BINDING Constraints from Decisions and L2.1 Errata

These are the constraints that L2.2 spec MUST honor. Violation of any of these means L2.2 fails Pass Criteria and needs revision before LOCK.

### From Decision 1 v2 (substrate)
- **Slot 1 cell encoder must consume the substrate via `substrate.project_to_canonical()`** — the canonical 512-dim conversion. L7 must NOT instantiate its own `torch.nn.Linear(substrate.output_dim, 512)`. This is the L2.1 Finding 5 resolution (BINDING).
- **Slot 1 instantiation order for scTOP must call `fit()` or `load_pretrained()` before accessing `output_dim`.** scTOP's NATIVE_DIM is sentinel -1 until reference is loaded. L2.1 Finding 6 resolution (BINDING).
- **Hyperparameter budget allocation:** parameter-free Baseline B (scTOP-style) must receive ≥25% of FM hyperparameter search budget per Decision 8 v2 Commitment 5. L2.2 must document the budget allocation for any L7 ablation study.

### From Decision 3 v2 (bulk-to-single transfer)
- **Slot 4 architectural identities (BINDING per Drift Finding 7):**
  - scRank = Slot 4 GRN component = Decision 7 v2 Scale 4 (cross-decision binding)
  - Beyondcell = Decision 7 v2 Scale 3 (pathway scale, not Slot 4)
  - chemCPA architecture surgery = Decision 3 v2 bulk-to-single transfer bridge (NOT a Slot 4 component; it is the cross-decision link between Slot 2 chemical encoder and Decision 3 v2)
- L2.2 must explicitly cite these identities in §8 Cross-decision implications.

### From Decision 4 v2 (the parent decision)
- All 6 slots specified in Decision 4 v2 §"L7 Architecture Diagram" must appear in L2.2 with full implementation.
- Per Decision 4 v2 §"What L2.2 Does NOT Lock," the following are explicit Layer-5-deferred:
  - Specific chem-FM choice in Slot 2 (MoLFormer vs ChemBERTa vs Uni-Mol vs RDKit baseline) — L2.2 specifies the interface and a default, not the empirical winner
  - Specific mode-collapse mitigation in Slot 5 (diversity loss default vs energy-based vs MoE) — same pattern
  - Specific patient aggregation in Slot 6 (PaSCient default vs alternatives) — same pattern
- These are deferred to Layer 5 ablation per the substrate flexibility pattern from Decision 1 v2.

### From Decision 5 v2 (OOD ensembleability — BINDING per Drift Finding 8)
- **N=5 ensembleability constraint:** the L7 head must be the ensembled unit, not the entire pipeline. Specifically: 5 independently-trained L7 heads (different random seeds + optional adversarial training per Lakshminarayanan 2017) sharing the same substrate cell encoder and same drug encoder, with predictions averaged for the point estimate and disagreement quantified for epistemic uncertainty.
- L2.2 must spec the ensemble interface: how N=5 heads instantiate from one config; how training launches in parallel; how inference aggregates; how disagreement propagates to Decision 5 Layer 5.2 ensemble output.
- Fallback options per Decision 5 v2: MIMO8 (Engelmann 2022; single forward pass) or MC Dropout (Gal 2016; T=50 stochastic forward passes) when N=5 ensemble compute budget unavailable. L2.2 must spec all three modes.

### From Decision 6 v2 (validation pass criteria — BINDING per Drift Finding 9)
- L2.2 architecture must support evaluation against:
  - V0 within-dataset CV (sanity)
  - V1 IMPROVE cross-dataset AUROC ≥0.65 (Partin 2026)
  - V2 organoid AUROC ≥0.65 (INTERCEPTA contribution)
  - **V3 tumor AUROC ≥0.77 (Tang 2022) — BINDING FLOOR**
  - **V4 PDX RMSE ≤0.11 TNBC (Tang 2022) + Kim 2020 PDXGEM 24.5% concordance reporting — BINDING FLOORS**
  - V5 clinical retrospective ECE ≤0.05 (DiSyn architecture per Li-Shen 2024)
  - **V6 cross-disease AUROC ≥0.65 across ≥2 therapeutic areas — BINDING UNIVERSALITY TEST**
- L2.2 architecture must include pathway-feature baseline as Souza-Mehta-style rigor check per Decision 6 v2 §V3 critical methodological commitment.

### From Decision 9 v2 (compute envelope — BINDING per Drift Finding 10)
- **PaSCient compute footprint tension:** original PaSCient uses 8× A100 80GB / 300GB RAM / ~12 hrs. Decision 9 v2 target is single-A100 Northeastern Explorer envelope.
- **L2.2 Slot 6 must spec BOTH PaSCient-style attention aggregation AND simpler aggregation fallbacks** (mean pooling, max pooling, learned weighted pooling) for compute envelope compatibility. The fallbacks are not optional; they are required deliverables.
- Cached embedding storage convention per Q9 anchor 1: `/scratch/akula.pra/INTERCEPTA/embeddings/<substrate>/<dataset>/<split>.h5`. L2.2 must spec how L7 reads cached embeddings vs computing on-the-fly.

### From Decision 10 v2 (open-source — Phase B release)
- All slot defaults must be open-licensed (BSD-3 / MIT / Apache-2.0 / GPL-3 with conditional handling).
- CPA backbone is MIT (Meta/Helmholtz). chemCPA is open. GEARS is open. PaSCient code is open. RDKit is open.
- L2.2 §"Open-source compatibility" subsection must confirm.

### From L2.1 Errata (BINDING resolutions)
- **Finding 5 — `substrate.project_to_canonical()` is canonical.** L7 must call substrate-resident projection method, not internal `torch.nn.Linear`. See §1.2 errata in L2.1.
- **Finding 6 — scTOP NATIVE_DIM lifecycle.** Must call `fit()`/`load_pretrained()` before `output_dim`. See §1.2 errata in L2.1.
- **Finding 4 — Souza-Mehta anchor re-read trigger satisfied retroactively.** Future modifications to L2.1's scTOP sections (§3.1-§3.6) must continue to honor re-read trigger.

---

## 5. Decision Points L2.2 Must Resolve

These are open architectural questions where L2.2 makes the call (within Decision 4 v2 constraints). Pre-list them so the fresh CSO does not get blocked mid-write:

1. **Slot 1 ↔ CPA disentangled latent interface:** does the substrate output go directly into the CPA disentangled latent, or is there an intermediate adapter layer? Decision 4 v2 §L7 Architecture Diagram shows direct flow. L2.2 confirms or specifies adapter.

2. **Slot 2 default chem-FM choice:** MoLFormer (IBM) vs ChemBERTa (Hugging Face) vs Uni-Mol (DPTech). All open. L2.2 picks default with rationale; ablation infrastructure tests alternatives.

3. **Slot 3 perturbation network parameterization:** chemCPA paper specifies M (chemical → latent) and S (dosage scaler). L2.2 must spec dimensions, depth, activation, regularization.

4. **Slot 4 graph priors weighting:** how do gene-gene + GO + drug-target graphs combine? GEARS uses learned attention. L2.2 confirms or specifies alternative.

5. **Slot 5 mode collapse default:** Decision 4 v2 says "diversity loss default; alternatives: energy-based, MoE." L2.2 specifies the diversity loss formula (Diversity-by-Design 2025 critique reference).

6. **Slot 6 PaSCient compute fallback choice:** Decision 9 v2 + Drift Finding 10 require fallbacks. L2.2 specifies mean / max / learned weighted — pick default fallback with rationale.

7. **Training objective:** CPA composition loss + diversity loss + auxiliary losses (e.g., drug-target prediction auxiliary). L2.2 specifies the full objective with weighting hyperparameter defaults.

8. **Validation cascade integration:** how does L7 surface predictions at each V0-V6 level? Single API or per-level adapters?

9. **Ensemble training infrastructure:** N=5 SLURM job array pattern. L2.2 specifies the Snakemake/Nextflow workflow at the level of "this is the orchestration" (not full implementation; that is Layer 4-5).

10. **Cached embedding read pattern:** lazy load vs upfront load; chunking strategy for large datasets (>100K cells).

---

## 6. Phase B vs Phase F Framing Reminder

**L2.2 is Phase B-canonical.** It specifies the cell-level drug response prediction architecture for the Phase B platform.

**The L7 head IS Simulation Stack Layer B (Cell Population Sensitivity) in Phase F taxonomy.** It is the evaluator that all 6 Phase F Scouts (database retrieval, generative design, combination explorer, network perturbation, evolutionary optimizer, cross-disease transfer) will call to test candidate molecules against cell populations.

**L7 is NOT Scout 1.** Scout 1 is target-based candidate retrieval from ChEMBL/PubChem/ZINC. L7 is the cell-level evaluator under all scouts.

**L2.2 spec is Phase B-only.** Do not specify Phase F integration patterns in L2.2. The Phase F integration will be specified in Phase F Decisions 11-20 when Phase F begins. L2.2 does mention in §8 (Cross-decision implications) that the L7 → Simulation Stack Layer B continuity is documented for future Phase F reference, but the implementation stays Phase B-canonical.

**Anti-scope-creep enforcement:** if L2.2 writing starts wanting to specify Scout 2 generative chemistry integration, or AutoDock Vina docking, or ASKCOS retrosynthesis, or pharma deliverable packaging — STOP. Those are Phase F. Flag in §8 cross-decision implications, document the Phase F future continuity, return to Phase B L7 spec.

---

## 7. Output Format Target

L2.2 should follow L2.1 template structure:

- **§0 Identification and Scope** — What L2.2 is, what it is not, Phase B Plan v2 compliance
- **§1 The L7 6-Slot Architecture Overview** — High-level diagram, slot list, data flow
- **§2 Slot 1 — Cell Encoder** — Interface to Decision 1 v2 substrate; project_to_canonical pattern; scTOP lifecycle handling
- **§3 Slot 2 — Drug Molecule Encoder G** — chem-FM modular slot; default choice + alternatives; ablation infrastructure
- **§4 Slot 3 — Perturbation Network M+S** — chemCPA M+S spec
- **§5 Slot 4 — Graph-Augmented Module** — GEARS-style; gene-gene + GO + drug-target; cross-decision binding to scRank
- **§6 Slot 5 — Mode Collapse Mitigation** — Diversity loss default; alternatives; training-time vs inference-time tradeoffs
- **§7 Slot 6 — Patient Aggregation** — PaSCient default + 3 fallbacks per Decision 9 v2 compute envelope
- **§8 Cross-Decision Implications** — D1, D2, D3, D5, D6, D7, D9, D10 propagations + Phase F future continuity note (L7 → Simulation Stack Layer B)
- **§9 Pass Criteria for L2.2 LOCK** — Specific criteria including CEO sign-off
- **§10 What L2.2 Does NOT Lock** — Deferred to Layer 5 (specific chem-FM, specific mode collapse, specific aggregation, specific training objective weights, specific hyperparameter defaults)
- **§11 Document Provenance and CSO Discipline Check** — Anchor re-read compliance (SATISFIED per this primer); discipline check vs Charter v1.2 principles; drift catalog this session
- **§12 Appendix** — Quick reference table; key file paths; commitment cross-reference

---

## 8. What This Primer Does NOT Specify

The primer scopes L2.2 — it does NOT write L2.2. Specifically, the primer does not provide:

- PyTorch class skeletons for any slot (the L2.2 spec does this)
- Specific hyperparameter values (default + range; L2.2 does this)
- Specific training loss formulas (L2.2 does this)
- Specific SLURM job array patterns (L2.2 sketches; Layer 4-5 implements)
- Specific dataset preparation pipelines (L2.1 substrate spec + Layer 4 covers this)
- The full §8 Cross-Decision Implications subsection contents (L2.2 writes this from current Decision states)

If a fresh CSO writing L2.2 finds the primer insufficient for any of the above, return to Master Handoff v2.0 §4.2 L2.2 section, or to Decision 4 v2 directly, or to the Q4 synthesis, or to the anchor papers themselves (`/mnt/project/` or `~/INTERCEPTA/docs/research/literature/`).

---

## 9. Operational Reminders

- **CEO is Prasad Akula.** "im eco" means full quality, don't suggest rest. CSO decides when L2.2 is done; CEO confirms via LOCK.
- **File path on Mac:** `~/INTERCEPTA/docs/research/phase_b/INTERCEPTA_FV_L2_2_L7_Drug_Response_Architecture_Specification_2026-05-XX.md`
- **HPC NOT GPU-ready yet** (verified 2026-05-09). L2.2 spec assumes GPU is available; Layer 4-5 implementation will handle the current GPU-ready gap. Not L2.2's concern.
- **Working directory for fresh CSO computer-use:** `/home/claude/` (scratchpad); outputs to `/mnt/user-data/outputs/`
- **All anchor papers and L2.1 spec accessible via `/mnt/project/`** when uploaded to a new chat
- **Tag after LOCK:** `phase-b-l2.2-proposed` (proposed) → `phase-b-l2.2-locked` (when CEO LOCKS) → folds into next Layer 1+ comprehensive tag at L2 completion

---

## 10. Discipline Reminder

L2.2 is real CSO architecture work. The 12-15K words must be defensible. P15 (only honest science) is BINDING. P16 (preserve past work via _SUPERSEDED_) is BINDING. Decision 1 v2 Commitment 5 (honest stated uncertainty) is BINDING. Souza-Mehta methodological bar (≥25% hyperparameter budget to parameter-free baseline) is BINDING.

If during writing the fresh CSO encounters a real architectural ambiguity that L2.2 cannot resolve without a Decision Record amendment, STOP and surface to CEO. Do not silently extend Decision 4 v2 scope. Do not silently violate Decision 5 v2 ensembleability. Do not silently exceed Decision 9 v2 compute envelope.

The vision is non-negotiable. The discipline is the contract.

— Prepared by CSO Claude, 2026-05-11, after Charter v1.2 LOCK and Layer 1 LOCK completion.
— Fresh CSO writing L2.2 inherits this primer + Master Handoff v2.0 + the locked Layer 1 corpus.
