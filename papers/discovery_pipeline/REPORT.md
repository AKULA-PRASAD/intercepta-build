# Computational modules of a drug-discovery pipeline: five rigorously-validated components and a negative envelope on their integration

**INTERCEPTA build — technical report (2026-07-30).** Every quantitative claim here traces to a pre-registered,
byte-identically-reproduced (×2) experiment with a committed metrics JSON; see `LEDGER.md` and `experiments/`.
This report makes **no clinical claim and no novel-drug claim**; it reports validated *computational* components and
an honest bound on integrating them.

---

## Abstract

We build and rigorously validate, on open data, computational modules spanning all five *code-addressable* stages of
a drug-discovery pipeline — (1) target identification, (2) molecular design, (3) efficacy, (4) ADMET/safety,
(5) synthesizability — each pre-registered, benchmarked against honest baselines and (where one exists) the published
leaderboard, and reproduced twice byte-identically. We then ask the platform-level question — *does composing the
modules beat their parts?* — and answer it decisively in the negative across **six increasingly-powerful
experiments**: neither scalar fusion, feature-level fusion, a shallow learned representation, nor a deep molecular
foundation model (ChemBERTa, 77M-molecule pretraining) robustly beats a raw-structure baseline on held-out outcomes.
The mechanistic reason is that the modules' information is largely recoverable from structure; the bottleneck is
**information/data, not representation**. The contribution is therefore (a) a set of honestly-scoped, reproducible,
standalone modules and (b) a rigorous *negative envelope* on their integration — a result the field's incentives
usually suppress.

---

## 1. Method — the rigor protocol (shared by every experiment)

Governed by `CONSTITUTION.md`. Each experiment: **pre-registers** hypotheses + a fixed decision rule *before results*
(`prereg/B*.md`); fixes seed=42; compares against **honest baselines** (trivial/predict-the-mean/base-rate) and, where
available, the **published leaderboard**; uses **scaffold splits** (generalization to novel chemistry) or
leave-group-out CV (generalization to unseen diseases/combinations); controls **confounds** and **leakage**
(canonical-SMILES exclusion of any training molecule from held-out sets); judges **effect size, not just p-value**;
records **negatives as first-class**; and is **reproduced ×2 byte-identically** (a payload sha256 over the
deterministic metrics). Data provenance (public sources + sha256 + access class) is logged in `data/MANIFEST.md`.

Two methodology self-corrections were made mid-study and documented (not hidden): a pre-registered coefficient-sign
sub-test in B34 that failed due to multicollinearity/suppression (adjudicated on robust AUROC criteria instead), and
an unpaired-variance bar in B32b that was replaced by proper paired statistics (B35) — both recorded transparently in
`LEDGER.md`.

---

## 2. The five validated modules (each reproduced ×2)

| # | Module | Headline result (held-out) | Honest scope | Ref |
|---|---|---|---|---|
| 1 | Target identification | Genetic/functional evidence predicts clinic-reached targets **beyond a popularity baseline** | enrichment, not proof | B34 |
| 2 | Molecular design | Goal-directed GA optimizes developability, beats seed + random, 100% valid | optimization over known chemistry, not de novo discovery | B33 |
| 3 | Efficacy | +0.212 transfer ceiling (intrinsic) + generalizing drug-synergy signal | cell-line, not clinical | V1/V23 (prior; `papers/intercepta_engine/`) |
| 4 | ADMET / safety | Beats trivial on **22/22** TDC tasks; calibrated conformal uncertainty | in-silico screening filter, not a safety guarantee | B30/B30b |
| 5 | Synthesizability | Predicts retrosynthetic solvability AUROC **0.91**, scaffold-robust | algorithmic proxy, not a lab guarantee | B31 |

**#4 ADMET (B30).** Morgan/ECFP4-2048 + 17 RDKit physchem → HistGradientBoosting, on the TDC ADMET Benchmark Group
(22 tasks, official scaffold-split 5-seed protocol). Beats the trivial baseline by >1 sd on **22/22** tasks; median
**82%** of the trivial→published-SOTA gap closed. Near-SOTA on several (bbb AUROC 0.893 vs SOTA 0.924; dili 0.911;
hia 0.950; cyp3a4_veith PR-AUC 0.866; caco2 MAE 0.291 vs 0.256); honestly weak but still >trivial on hard/small tasks
(half_life Spearman 0.168, vdss 0.270, bioavailability 0.700). No SOTA claim — a competent, honest mid-leaderboard
baseline. Shipped `intercepta.admet.ADMETPredictor` + CLI. (payload af66698f)

**#4 uncertainty (B30b).** (i) The applicability-domain flag was *validated*: per-molecule error rises with Tanimoto
AD distance in **20/22** tasks (15/22 BH-FDR<0.05, mean Spearman +0.128) — AD distance is a genuine but *weak*
continuous reliability weight; the binary 95th-pct flag is a weaker separator (kept as a soft weight, not a hard
gate). (ii) Inductive conformal intervals (regression) and prediction-sets (classification) achieve empirical
coverage within ±0.05 of nominal on the scaffold test (regression 0.906/0.813; classification 0.899/0.786 at
90%/80%) — calibrated *even under scaffold shift*. (payload 50cc195c)

**#5 Synthesizability (B31).** Predicts AiZynthFinder retrosynthetic solvability (RAscore/ChEMBL, 179k/20k) from the
same featurizer. Random split AUROC **0.911** (published RAscore 0.93–0.95, same model family); Bemis–Murcko scaffold
split **0.908±0.002** — beats oriented-SAscore (0.847) and trivial (0.5) on both; generalization gap only 0.003
(synthesizability is far more structure-local than the +0.212 drug-response signal). Shipped `intercepta.synth`. (payload c6edd9bc)

**#1 Target-ID (B34).** Open Targets Platform v26.06 (12,000 target-disease pairs × 40 diseases). Label = reached
clinic; features = 6 non-clinical evidence datatypes; confound = `literature` (study popularity). Leave-**disease**-out
CV: popularity alone is near-chance (AUROC **0.522**); genetic_association alone **0.741**; full non-clinical evidence
**0.839** (AUPRC 0.754 vs prevalence 0.293) — clinic-reached-target prediction is driven by genuine genetic/functional
evidence, **not** study bias (a B10-style confound test, here *passed*; consistent with Nelson-2015 genetic support).
Not shipped as a tool (would duplicate Open Targets' own scores) — the validated finding is the deliverable. (payload 6c4b5e81)

**#2 Molecular design (B33).** A BRICS fragment-recombination genetic algorithm optimizing developability
(QED×synthesizability) over ChEMBL seeds. GA mean objective **0.715** (best 0.879) beats both baselines — the ChEMBL
seed population (0.427) and no-selection random recombination (0.167) — at 100% validity, uniqueness, and novelty. It
also *exposes reward-hacking*: single-objective (QED-only) optimization is less synthesizable (SAscore 2.40) than the
multi-objective run (2.10), demonstrating why multi-objective is necessary. Shipped `intercepta.generate`. Scope:
optimization over *known* chemistry, **not** de novo drug discovery; every output is a computational hypothesis. (payload d91f0470)

---

## 3. The integration study — a negative envelope (B32 → B38)

The platform-level hypothesis: composing the modules beats their parts on a *held-out* real-world outcome (primarily
ClinTox clinical-toxicity failure, extended to 7 tox/safety outcomes). Six experiments of escalating rigor and power:

| Exp | Integration approach | Result |
|---|---|---|
| B32 | scalar late-fusion (logistic on 12 module outputs) | composite 0.819 < best single module (ppbr_az 0.831); direct structure 0.857. **Negative.** |
| B32b | feature-level fusion (structure ⊕ module features) | S+M 0.920 > S 0.906 (Δ+0.013) but sub-1sd. **Non-decisive.** |
| B35 | paired re-adjudication (correct statistics) | per-seed Δ+0.019 (Wilcoxon p=0.019) but molecule-level bootstrap p=0.30 (CI includes 0). **Power-limited.** |
| B36 | multi-outcome feature-fusion (7 outcomes) | mean Δ −0.009, 0/7 significant, Wilcoxon p=0.47, CI includes 0. **Decisive negative.** |
| B37 | shallow learned representation (multi-task MLP embedding) | within-tox-domain transfer only (skin +0.063) but mean +0.018, not robust; embedding-alone worse. **Mixed/negative.** |
| B38 | deep foundation model (ChemBERTa, 77M-molecule pretraining) | mean Δ −0.007, 1/7 significant, Wilcoxon p=0.23, CI includes 0; FM-alone worse. **Negative.** |

**Decisive conclusion.** No integration approach — from simple fusion to a deep foundation model — robustly beats a
raw Morgan+physchem structure baseline on these held-out outcomes. The mechanistic explanation is direct: the ADMET
and synthesizability modules are themselves Morgan+physchem gradient-boosted trees, so their outputs are largely
functions of the same structure features (redundant by construction); and even a foundation model with *learned*
fingerprints (B38) adds no general signal, transferring only weakly *within* the toxicity domain. **The bottleneck is
information/data, not representation.** INTERCEPTA's value is its standalone validated modules, not their integration.
(payloads 81996f21, 7d7a305c, 04c20605, ea088da2, c8d16b06, c17e47f4)

---

## 3b. The assembled pipeline works as a tool (B39)

The integration *predictor* claim fails (§3), but the modules used for their **intended purpose** — as a generator +
filters — compose into a working discovery tool. `intercepta.discover.DiscoveryPipeline` runs a goal-directed BRICS
genetic algorithm (design, B33) optimizing **F = drug-likeness × synthesizability (B31) × predicted-safety (B30
hERG/AMES/DILI)** over ChEMBL seeds. Result (reproduced ×2, payload 23a7ae0c): the pipeline yields candidates at mean
developability **F 0.504** (best 0.627) vs the ChEMBL seed population **0.185**, at **100% validity, uniqueness, and
novelty**; and the multi-objective demonstrably shifts the output vs a QED-only run — **more synthesizable** (SAscore
2.16 vs 2.40) and **safer** (predicted-safety 0.80 vs 0.67). Honest caveat, reported: only **56%** of top candidates
fall inside the ADMET applicability domain — the rest are novel chemistry where the safety calls are unreliable, and
optimizing against in-silico predictors invites gaming. This is a computational *prioritization* demonstration —
every candidate is a hypothesis, not a validated, novel, safe, or practically-synthesizable drug. It shows the
platform *running end-to-end*, honestly bounded; it does not contradict §3 (which concerns using module outputs as a
combined *predictor*).

**Target-conditioned generation (B40).** The pipeline can be aimed at a chosen disease/target by attaching a
validated activity QSAR to the objective (`× P(target-active)`). On HIV (QSAR scaffold AUROC 0.806), conditioning
raises the mean predicted P(HIV-active) of generated candidates to **3.96×** the unconditioned pipeline (1.81× the
ChEMBL seeds), at validity/novelty 1.0 and preserved drug-likeness/synthesizability — genuinely steering design
toward the target. It also surfaces an honest **activity-vs-safety trade-off** (predicted safety 0.43 vs 0.80): the
HIV-active-like chemistry the QSAR favors is predicted more toxic. Reported transparently (payload e62417bf);
shipped `intercepta discover --target-hts`. Activity is QSAR-*predicted*, not measured; candidates remain hypotheses.

## 3c. Retrospective validation against external truth (B42)

Every result in §2–3b validates against our *own* predictors (circular). B42 is the first test against **external
ground truth — real known drugs/actives.** (i) **Scoring:** on HIV (scaffold split), the activity model enriches
*real* actives with strong early recognition — AUROC **0.806**, BEDROC(α=80.5) **0.94**, EF@1% **7.4×**. (ii)
**Generator:** in the GuacaMol rediscovery setting, the BRICS-GA reaches analog-level similarity to all 3 held-out
target drugs (celecoxib 0.60, troglitazone 0.57, thiothixene 0.48), each improving +0.18–0.25 over the best seed
molecule. So the pipeline demonstrably recovers external truth — it enriches real actives and reaches the chemical
neighborhood of real drugs. **Honest bounds:** rediscovery is analog-level (~0.5–0.6 Tanimoto), not exact
reconstruction (fragment-recombination reach limit); enrichment is one target; retrospective and in-silico;
similarity ≠ proven activity; not wet-lab. This is the program's strongest computational-validation evidence and
the main mitigation of the circular-validation risk. (payload 9d99060e)

## 3d. Generality of the enrichment across target classes (B43)

B42's external-truth enrichment was one target (HIV). B43 applies the same protocol to a diverse 6-target panel
(antiviral, 2×GPCR, ion channel, kinase, viral protease). **All 6 enrich** real actives (AUROC>0.7 & EF@1%>3):
panel-mean AUROC **0.835** (range 0.76–0.89), mean EF@1% **13.2×** (HIV 5.0×, m1-muscarinic 8.8×, orexin-1 11.1×,
Kir2.1 19.2×, SARS-CoV-2-3CLpro 9.5×, STK33 25.8×). So the scoring's recovery of real actives is **general across
target classes, not HIV-specific** — the strongest evidence that the screening capability transfers. Retrospective,
in-silico, real-actives-vs-decoys on scaffold splits; low-active screens (78–172 actives) are harder but still
enrich; enrichment ≠ proven activity; not wet-lab. (payload daca99a2)

## 3e. Ligand-based 3D scaffold hopping — the boundary of feasible computation (B44)

The full retrieval stack so far is 2D (Morgan fingerprints). B44 asks whether **ligand-based 3D** (RDKit O3A shape +
pharmacophore overlay onto known actives) adds the one capability 2D structurally lacks: retrieving actives on a
**novel scaffold** (2D-dissimilar to the references — *scaffold hopping*). This is also the **last computationally-
feasible rung**: no receptor docking engine is installed (Vina/smina/gnina absent; only Open Babel), and a fragile
docking/MD install is declined on reproducibility grounds. On HIV, 8 scaffold-cluster reference actives, single
ETKDGv3+MMFF conformer per molecule, O3A max-over-references vs Morgan-Tanimoto max-over-references. On the 1,181
novel-scaffold actives vs decoys, 3D gives a small **global**-ranking edge (AUROC **0.634** vs 2D 0.589, Δ+0.045) but
**no early-recognition gain** — the part that matters for screening (EF@1% 3D 2.54× vs 2D 2.71×; BEDROC 0.738 vs
0.803, 3D slightly worse). The pre-registered H1 (conjunction of a global *and* an early-enrichment gain) is therefore
**FALSE**; H2 (3D above chance, AUROC>0.6 & EF@1%>2) is TRUE. **Honest verdict:** single-conformer ligand-based 3D does
not beat the 2D spine where it should most help; the 2D fingerprint remains the operative retrieval tool. This is
consistent with the program-wide finding that the bottleneck is **information/physical truth, not representation**, and
it marks the edge of what is buildable without new data or a structure-based infrastructure decision. Retrospective,
single-conformer (an ensemble approximation), heuristic overlay (not a binding energy), one target, decoys not
property-matched; enrichment ≠ proven activity; not wet-lab. (payload 1120c3d3)

## 4. What is novel, and what is not (honest)

- **Competent reproduction, not novel:** the ADMET (B30), synthesizability (B31), goal-directed design (B33), and
  target-genetic-support (B34) results are rigorous, honest reproductions of known methods/findings — not new
  capabilities.
- **Genuinely novel contributions:** (a) the **integration negative envelope** (B32→B38) — a systematic, powered
  demonstration that module integration (up to a deep FM) does not beat raw structure on these outcomes, which the
  field's publication incentives rarely produce; (b) the surrounding **rigorous-negative methodology** (pre-registration,
  reproduce-×2, confound/leakage control, effect-size adjudication, transparent self-correction) as a reusable
  discipline; alongside the program's prior **six-front intrinsic-ceiling** result (V7). There are **no novel positive
  capabilities** here — every positive is a reproduction or a confirmation of prior work. Stated plainly.

---

## 5. Scope & limitations

Cell-free/structure-only predictions on public medicinal-chemistry and evidence datasets; scaffold-split or
leave-group-out generalization only. Small positive classes on several held-out outcomes; survivorship confounding in
approval/clinical labels; curated evidence scores (Open Targets) carry some circularity; ChemBERTa results reflect one
model/pooling choice. None of these modules is a clinical, regulatory, or safety determination, and none demonstrates
a real, better, or practically-synthesizable novel drug.

---

## 6. Remaining gates (not reachable in code)

The honest fullest-vision frontier is now **not more modeling**. Against "any drug for any disease" this is validated
computational corners (≈1–5% of the literal grand challenge). The next steps are hard gates requiring new resources:
**(i)** more/different **data** (the shown integration bottleneck); **(ii)** **experimental/wet-lab** validation of a
designed molecule; **(iii)** prospective **clinical** validation (`prereg/TRACK1_SAP.md`, a multi-year study). These
are human/collaboration decisions, not computations.

---

## 7. Reproducibility

Every result maps to a committed `experiments/B*/run.py` + `results/B*_metrics.json` + a payload sha256, reproduced
twice byte-identically; every inferential analysis is pre-registered in `prereg/`; 30 data-free unit tests cover the
shipped package; controlled/patient data are never committed. Shipped tools: `intercepta {info, rank, synergy, admet, synth, prioritize, generate, discover}`. Experiment index with payload hashes: B30 af66698f · B30b 50cc195c · B31 c6edd9bc ·
B32 81996f21 · B32b 7d7a305c · B33 d91f0470 · B34 6c4b5e81 · B35 04c20605 · B36 ea088da2 · B37 c8d16b06 · B38 c17e47f4 · B39 23a7ae0c · B40 e62417bf · B41 359486bf · B42 9d99060e · B43 daca99a2 · B44 1120c3d3.
