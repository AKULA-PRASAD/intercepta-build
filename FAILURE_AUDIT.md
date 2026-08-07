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

**F2 — FBA-essentiality is GEM/organism-specific on host-dependent organisms (NOT a categorical failure).**
- ⚠ **CORRECTED (HARDENP1, Wave 4).** The n=1 framing of this failure ("FBA fails on host-embedded biology")
  was an overgeneralization. On *Plasmodium* FBA fails (GENERALIZE5 OR 2.47; HOSTCTX1 expression + HOSTCTX2
  boundary curation both NEGATIVE). **But on a second host-dependent parasite, *Toxoplasma gondii*, FBA PASSES
  strongly (HARDENP1 OR 14.10, recall 0.51).** So host-embeddedness does NOT predict FBA failure.
- Corrected root cause + confound status (**PARARESOLVE1, 3487e6c**): the **GEM axis is a major driver** —
  swapping in independent Pf GEMs spans OR 0.86→3.07 and one (iAM-Pf480) *passes* → not uniquely iPfal19. **But
  GEM choice does NOT close the Pf↔Toxo gap** (base rate is GEM-invariant ~0.65 vs 0.42; a base-rate/biology
  residual survives), and the specific **"salvage-bypass topology" mechanism is FALSIFIED** (salvage-FN
  fraction iPfal19 0.907 ≈ Toxo 0.867). **Screen-tech axis PROBED (PARARESOLVE2)**: the clean Pf-CRISPR test is
  data-gated (no genome-wide Pf CRISPR screen), so probed via a 3rd technology (Bushell barseq-KO) — the
  pass/fail verdict is NOT screen-tech-robust (iPfal19↔iAM-Pf480 swap pass/fail across screens), so the tech
  axis is not exonerated, but the *failure mechanism* IS (recall ~0.2 everywhere). **Sharpened honest reading:
  the OR>3 gate is knife-edge at Plasmodium's noise floor and verdict flips are largely a base-rate artifact —
  so "Plasmodium FBA passes/fails" is NOT a stable single fact.** What is stable: Plasmodium sits near the noise
  floor (recall ~0.2) regardless of GEM/screen, while Toxoplasma is robustly strong (recall 0.51) — the Pf↔Toxo
  gap never closes. Root cause is multi-causal (GEM topology × truth base-rate × screen sampling), not a clean
  single mechanism.
- **Compute-solvable? Organism/GEM-dependent, incompletely.** A good GEM can flip it (iAM-Pf480 passes), but
  we cannot a-priori predict which GEM will work (COMPOSITE3 flags uncertainty), and the residual is unresolved.
  Honest
  confound on the n=2 comparison: different GEM curation teams + different screen technologies.
- **Complementary signal (DEPEND1, Wave 3, VERIFIED G1/G2/G3 PASS):** where FBA is weak/unavailable, the
  **functional-DEPENDENCY layer** is a validated alternative — selective dependency recovers known cancer
  targets (0.80), **generalizes to held-out disjoint lines** (0.80, the F3 gap), and a **label-free
  expr→dependency** arm beats baseline. *(Post-HARDENP1 framing: dependency and FBA are COMPLEMENTARY
  host-embedded signals — dependency where a screen exists, FBA where a good-topology GEM exists — not "one
  replaces the other".)* **Remaining honest gaps:** DEPEND1 is cancer cell-line (not patient/clinical); the label-free
  arm is validated on held-out DepMap lines. **Organism-transfer to a true zero-screen novel pathogen — now
  TESTED (TRANSFER1, 37caa0d): it FAILS.** The selective-dependency signal does not survive transfer to a
  zero-screen parasite (OR 0.90, chance); only conserved-core transfers (redundant with REACH1 conservation),
  at ~28% orthology coverage. **Honest boundary established:** for a novel host-embedded pathogen with no
  screen, we can offer only the conserved-core (via conservation), NEVER selective targets — the composite
  router correctly abstains there. So DEPEND1's win is real *where the organism (or its close domain) has a
  screen* (human cancer), and does NOT extend to novel-pathogen zero-data discovery. Do NOT claim clinical or
  novel-pathogen success.

## Tier 2 — real weaknesses needing an honest fix or an honest downgrade
**F3 — The human-disease / oncology *drug-response prediction* line is TESTED-AND-LARGELY-NEGATIVE (consolidated).**
- **Consolidated evidence (F3 is NOT an untested gap — it was attacked five ways and mostly fails):**
  - **B20 (FIMM/Malani, a genuine 2nd patient cohort): FAILS to replicate** — the decisive external test.
  - **B10 (TCGA patient outcome): CONFOUNDED** — the raw signal is cancer-type, not drug-level prediction.
  - **B17 (clinical outcome): HONEST NEGATIVE** — inferred-FLT3-dependency does not mark FLT3i survival benefit.
  - **B9 (PDXE-PRISM): NULL**; **B11: NULL** (no novel BeatAML marker replicates cross-system); **V14 DOWNGRADED**
    (PDXE drug-specificity not robust); **N1 WITHDRAWN**. Only B7/B3c are weak/borderline/same-cohort.
- Root cause: patient drug response is dominated by non-cell-autonomous factors (microenvironment/immune/stroma)
  + cross-institution assay differences + tiny effect sizes — a hard, field-wide gap, and retrospective cohort
  mining has been exhausted here without a robust positive.
- **Compute-solvable? For *response prediction* — NO (evidence says so).** More retrospective replications would
  be cohort-shopping toward a false positive; do not run them.
- **Real solution — the HONEST REFRAME (not more replication):**
  (1) **DOWNGRADE the human *drug-response prediction* claim to NEGATIVE/gated** — tested five ways, largely
  fails; needs prospective clinical data we do not have. State this plainly; make no patient-response claim.
  (2) **The validated human deliverable is dependency *TARGET-ID*, not response prediction** — DEPEND1 (which
  genes are selective cancer dependencies) generalizes across held-out cell lines and recovers known targets.
  Its patient RELEVANCE is now **VALIDATED (F3CLIN1, f741774, PASS)**: selective cell-line dependencies are
  enriched for patient-tumor drivers (IntOGen, OR 2.55, p 3.4e-26) and the enrichment **survives study-bias
  controls** (publication-matched null + Mantel–Haenszel OR 2.72) with a recurrence dose-response. So the human
  *target-ID* claim is COMPUTED-validated with a genuine cell-line→patient RELEVANCE bridge — a real, honest,
  *different* claim from response prediction. **Hard scope line: F3CLIN1 is target-relevance ONLY — it does NOT
  rescue drug-response prediction (still negative) and is NOT clinical validation.**
  (3) The *clinical endpoint* (patient outcome) remains **GATED — needs prospective data** (≡ F0). No shortcut.

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
