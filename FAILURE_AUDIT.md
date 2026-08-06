# INTERCEPTA — CSO Failure Audit (all wrongs, honestly; real solution or honest gate for each)

*Companion to `VISION_MAP.md`. Rule: no failure hidden, no claim inflated, no "solution" that is really
motion. Each item: the failure → evidence → root cause → is it compute-solvable? → the REAL solution (with a
concrete next experiment) or an honest GATE. Ordered by how much it blocks the fullest vision. 2026-08-05.*

---

## The master constraint (name it first, don't bury it)
**F0 — The therapeutic endpoint is entirely un-validated in lab or clinic.** Every ultimate claim
(target → drug → cure) is in-silico. Zero wet-lab, zero clinical, zero patients.
- **Root cause:** zero budget, no laboratory. Structural, not fixable by code.
- **Compute-solvable? NO.**
- **Real solution (honest):** (1) The defensible SUCCESS we can own is *validated computational target
  PRIORITIZATION*, not "drug discovery" — and we have earned that (prospective-blind BLIND1, 6-organism
  panel). (2) The strongest experimental proxy available zero-budget is validation against *published*
  experimental screens (essentiality: PEC/DEG/DeJesus/CRISPRi/Giaever/Zhang) — done, real. (3) True
  therapeutic success requires an experimental partner or a public wet-lab campaign. That is a **strategic
  dependency, not a code task** — state it; never let a computational result be dressed as a therapeutic one.

---

## Tier 1 — real failures with a real compute solution now being attacked
**F1 — Intervention half is NARROW (repurposing covers 1/32 of a novel pathogen's targets).**
- Evidence: INTERVENE1 — 9/9 known-pharmacology recovery (real) but N. gonorrhoeae coverage 1/32 (sequence
  homology only reaches targets with a *close* drugged homolog).
- Root cause: sequence homology is blind to remote/structural analogues.
- **Compute-solvable? TESTED — NO.** The proposed fix (STRUCTREPURPOSE1: structural repurposing) was run with
  a mandatory null guard and came back **NEGATIVE**. Structure *validates* known pharmacology (G1 11/11) but
  does **not** expand novel-pathogen coverage: raw structural coverage 18/32 looked like a jump from 1/32, but
  a random-protein null matched **25/32** (more than drug targets) — the "gain" was a fold-census artifact
  (FOLD2 quantified). After null+plausibility, honest coverage **stays 1/32**. The mandatory guard caught
  exactly the false claim this audit named.
- **Real solution (REVISED, honest):** intervention narrowness is **not repurposing-fixable** — sequence *or*
  structure. Repurposing is fundamentally bounded to targets with a *genuine* drugged homolog; for a novel
  pathogen most essential targets have none, so novel-target intervention is **de-novo-chemistry-GATED (see
  F4)**, not a coverage bug. The honest deliverable: repurposing covers the small drugged-homolog fraction
  (validated); the rest is experiment/chemistry-gated and must be labelled so — no false "expanded coverage".

**F2 — FBA-essentiality FAILS on host-dependent organisms (parasites; and by extension human/cancer).**
- Evidence: GENERALIZE5 malaria OR 2.47 (sub-threshold). HOSTCTX1: expression context (E-Flux) does NOT fix
  it — the wall is *structural* (GPR bypass topology, not flux magnitude).
- Root cause: host-salvage "workaround" reactions in the network keep true essentials looking dispensable.
- **Compute-solvable? TESTED — NO, not with FBA.** Three verified negatives now: plain FBA (GENERALIZE5),
  expression-context E-Flux (HOSTCTX1), and host-exchange/medium curation (HOSTCTX2). Boundary curation was
  *directionally* correct (recall 0.20→0.30) but OR stayed flat (2.43<3) — enrichment never improved.
- **Real solution — REALIZED (DEPEND1, Wave 3, VERIFIED G1/G2/G3 PASS):** metabolic FBA is the wrong signal
  for host-embedded biology; the **functional-DEPENDENCY layer** is the right one and now clears the bar —
  selective dependency recovers known cancer targets (0.80), **generalizes to held-out disjoint lines** (0.80,
  the F3 gap), and a **label-free expr→dependency** arm beats baseline (the zero-data case). So the F2↔F3
  redirection is not just a direction — it is validated: for the host-embedded class, dependency > metabolic
  essentiality. **Remaining honest gaps:** DEPEND1 is cancer cell-line (not patient/clinical); the label-free
  arm is validated on held-out DepMap lines, **not yet transferred to a true zero-screen novel pathogen**
  (parasite/intracellular) — that organism-transfer is the next real test. Do NOT claim clinical or
  novel-pathogen success.

## Tier 2 — real weaknesses needing an honest fix or an honest downgrade
**F3 — The human-disease / oncology line (V1–V18+) is WEAK, and one claim was already downgraded.**
- Evidence: most signals single-cohort (BeatAML); small effect sizes (ρ ≈ 0.05–0.2); **V14 external
  drug-specificity DOWNGRADED — not robust**; **N1 mechanistic-coherence claim WITHDRAWN**. The one genuinely
  promising piece is the *functional-inference layer* (V15–V18: expr→CRISPR-dependency rescues FLT3/BCL2
  prediction where direct transcriptomics fails) — but cell-line / ex-vivo, single cohort.
- Root cause: patient data is scarce/one-cohort; drug-response signal is mostly generic proliferation.
- **Compute-solvable? PARTIALLY.**
- **Real solution — PARTIALLY ADVANCED (DEPEND1):** (1) **Honesty first — VISION_MAP still states human-disease
  is weaker than the bacterial result** (the *drug-response* line remains single-cohort). (2) BUT the
  functional-dependency *target-ID* layer — the real human lead — is now **validated with held-out
  generalization** (DEPEND1 G2: recovery holds on disjoint cell lines, closing the single-cohort criticism
  *for the target-ID layer specifically*) plus a label-free arm (G3). So the human **target-ID** claim rises
  from HYPOTHESIS toward COMPUTED-validated (cell-line). (3) **Still GATED:** the *patient/clinical* endpoint
  and the *drug-response* transfer line (V-series) remain single-cohort/weak — DEPEND1 is cell-line dependency,
  not clinical outcome. The next real human experiment is external replication on an independent patient/tumor
  cohort; until then no clinical claim.

**F4 — Molecule half is a demonstrated ceiling (novel-target potency ≈ chance).**
- Evidence: HIT1/HIT2/B48/B65 — docking heuristic (not ΔG); within-series potency ~chance without target
  activity data; generation → developable *hypotheses*, not validated inhibitors.
- Root cause: no bioactivity data for novel targets; physics-only scoring is weak.
- **Compute-solvable? Only for WELL-STUDIED targets** (public ChEMBL bioactivity → proteochemometric/QSAR,
  B49) — NOT for the novel targets the vision cares about.
- **Real solution (honest boundary):** keep molecule outputs labelled "pose-plausible developable
  hypotheses" (already enforced); offer real potency ranking ONLY where bioactivity data exists, and say so.
  The novel-target molecule problem is data-gated — not a bug to fix, a limit to state.

## Tier 3 — real but managed limitations (documented, not hidden)
- **F5 — FBA fine-ranking doesn't generalize; binary-enrichment only; low recall** (AUROC ~0.6; chance in
  Mtb). Managed: REACH1 (conservation breadth) partially closes recall at a precision cost; engine uses
  rank_score + multi-signal composition; the validated claim is binary enrichment. Honest.
- **F6 — Generalization frontier is n=1 per class** (one virus/fungus/parasite). Managed: labelled "frontier
  probes, not population claims." Real solution: more organisms per class (cheap compute) to harden.
- **F7 — Engine confidence SATURATES at genome scale** (88% "high"). Managed: report rank_score; confidence
  meaningful only in the emit-if-positive regime (CALIB1). Documented.
- **F8 — Tooling coverage gaps** (AlphaFold DB excludes viral structures). Managed: PDB-based viral references
  (GENERALIZE3, 21/30). Real solution: fuller PDB references for un-covered classes.

---

## CSO bottom line — the real path to TRUE success (not a false claim)
1. **What we can honestly claim as success today:** a rigorously validated, prospective-blind, reproducible
   computational **target-prioritization** engine for bacterial (and, with caveats, eukaryotic) pathogens,
   with a mapped generalization frontier and every boundary stated. Real and rare. This is fundable/publishable
   *as what it is*.
2. **The false claim to never make:** that this is "drug discovery" or solves "any disease incl. human/
   clinical." Molecule potency (F4), the therapeutic endpoint (F0), and human-disease (F3) are gated.
3. **Highest-leverage REAL compute work, ranked:** (a) STRUCTREPURPOSE1 — fix intervention narrowness [running];
   (b) HOSTCTX2 — network-boundary fix for host-dependent target-ID [running]; (c) confront F3 — external
   replication of the human functional-inference layer OR downgrade the claims; (d) harden the frontier (n>1).
4. **The real dependency for the ULTIMATE (therapeutic) vision:** experimental/clinical validation — a partner
   or public experimental campaign. Not solvable alone; pursued only if it genuinely accelerates the vision,
   and never faked in the interim.
