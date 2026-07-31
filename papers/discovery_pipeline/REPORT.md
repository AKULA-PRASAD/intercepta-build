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

## 3f. Turning the rigor on ourselves — does the enrichment survive on novel chemistry? (B45)

Our enrichment (B42/B43) used Bemis–Murcko scaffold splits, which the literature shows **overestimate** VS performance
because train/test still share substantial 2D similarity (arXiv:2406.00873). B45 audits this. **A transparent
self-correction happened first:** the pre-registered Butina *cluster* split failed its own validity check — it was not
actually harder than the scaffold split (cross-set NN-Tanimoto 0.428 vs 0.425), so that run was discarded (not
committed as a result) and the design amended (dated, in the prereg) to a **tuning-free** method: stratify the
scaffold-split test set by each compound's nearest-neighbor Tanimoto to training, and measure enrichment on genuinely
**novel** chemistry (NN<0.4). Result: the capability **survives** — panel-mean AUROC falls from full-test **0.837** to
novel-chemistry **0.786**, with **5/6 targets still >0.65** (STK33 0.90, Kir2.1 0.87, m1 0.80, orexin-1 0.76, 3CLpro
0.77). A real optimism gradient exists (AUROC drops 0.16 from the ≥0.5 to the <0.3 similarity band), so the scaffold
numbers were somewhat inflated; and **HIV is an honest weak spot** (novel-band AUROC 0.61 — largely
similarity-driven). **We therefore adopt the novel-band (NN<0.4) numbers as the honest generalization estimate going
forward**, not the scaffold-split numbers. Retrospective, in-silico; enrichment ≠ proven activity; not wet-lab.
(payload e437713b)

## 3g. Honest external footing on an unbiased community benchmark — LIT-PCBA (B46)

Our enrichment so far was on TDC HTS targets with our own splits. B46 places the ligand-based channel on **LIT-PCBA**
(Tran-Nguyen et al., JCIM 2020) — the community's *unbiased* VS benchmark (15 targets, realistic 1:1000–1:20000
imbalance), under the honest NN<0.4 lens from B45 and with cross-label dedup for leakage. On the 10 targets with enough
actives for a supervised split (5 too-sparse targets skipped, not forced): **median full-test AUROC 0.781, 9/10 > 0.70**
(FEN1 0.95, VDR 0.87, PKM2 0.86, GBA 0.84), and it **survives to novel chemistry** (panel-mean NN<0.4 AUROC **0.725**).
This median AUROC is **competitive with published ligand-based/ML methods on LIT-PCBA** (typically ~0.7–0.8). We flag
one thing honestly: our EF@1% (median ~13) is **inflated by the inactive subsampling** and is *not* comparable to
published full-ratio EF (Vina ~0.9, GNINA ~2.1, best ML ~4–5; arXiv:2605.01681) — AUROC is the fair, ratio-independent
metric. Honest weak spots: TP53 (0.68) and MTORC1 (novel-band 0.52, similarity-driven). No SOTA claim — an honest
placement of our channel on the unbiased benchmark. Retrospective, in-silico; enrichment ≠ proven activity; not
wet-lab. (payload 33d754cd)

## 3h. The structure-based channel — docking, and its orthogonality (B47)

Everything prior is ligand-only. B47 adds the **structure-based** channel: AutoDock Vina docking into the target
pocket — the first genuinely *new information source* (the receptor) in the program. On 3 LIT-PCBA targets with
co-crystal receptors (FEN1/MAPK1/ESR1_ant; 60 actives + 120 decoys each; Vina seed=42/cpu=8, byte-deterministic),
docking enriches **above chance (panel-mean AUROC 0.658)** and — crucially — is **orthogonal to the ligand channel**
(mean Spearman 0.27 vs co-crystal similarity). That orthogonality is the prerequisite for a fusion gain, which B48
tests. **Honest framing:** docking beat the *unsupervised* co-crystal-similarity baseline (0.51) here, but that
baseline is much weaker than our *supervised* QSAR (B46 median 0.78) — so docking is not the strongest channel, and
its early enrichment is weak (EF@5% 1.3–1.7×, consistent with docking's known weakness on unbiased data). Its value is
the complementary signal, not raw superiority. Heuristic score (not binding ΔG), rigid receptor, obabel prep, 3
targets, subsampled; not wet-lab; no SOTA claim. (payload 24d5b0f6)

## 3i. The payoff — does new orthogonal information break the ceiling? (B48)

B47 added a structure-based channel orthogonal to the ligand channel (Spearman 0.27). B48 is the decisive test the
whole arc built toward: does fusing the strong ligand-QSAR with the orthogonal docking channel beat the best single
channel? On 3 LIT-PCBA targets (eval ligands held out of QSAR training; leakage-controlled logistic fusion via
scaffold-CV out-of-fold), the answer is a clean **no**: panel-mean AUROC QSAR **0.835** (best single) vs
logistic-fusion **0.821** (Δ −0.014), and the same on novel chemistry (0.71 vs 0.74). Naive equal-weight rank fusion is
worse still (0.695) — averaging in weaker channels *hurts*; the leakage-controlled weighted fusion is smart enough to
recover ≈QSAR but cannot exceed it. **This extends the integration negative-envelope (§3, B32→B38) to a genuinely new
information source** — the 3D receptor. Despite being orthogonal, docking is not *additive*: the ligand QSAR already
captures the accessible discriminative signal. It is the strongest confirmation yet of the program's thesis — the
bottleneck is **information, not combination**. Retrospective, 3 targets, subsampled, heuristic docking; not wet-lab;
no SOTA claim. First-class negative. (payload 68c5b043)

## 3j. The "any disease" axis — proteochemometric pan-target generalization (B49)

Every QSAR so far needs the target's own ligand data. B49 probes the universal-platform axis: can we predict activity
for a target whose ligands were never seen, using **ligand ⊕ protein (ESM-2)** features and **leave-protein-out** CV
across 14 proteins? Result: weak generalization *exists* (mean PCM AUROC 0.599, 10/15 unseen targets >0.60), but it is
**carried entirely by ligand chemistry, not the protein representation** — a pooled *ligand-only* model actually scores
higher (0.636), so the ESM-2 embedding adds no usable target-specific signal and slightly dilutes (Δ −0.038). This is
literature-consistent (protein-language-model embeddings capture limited target-specific bioactivity) and it falsifies,
in this setup, the "any disease *via protein features*" route: there is a general "active-like" chemical signal that
transfers across targets, but naive PCM cannot make it target-specific. Notably B49 *uses* the low-active targets B46
had to skip (pooling). Retrospective, in-silico, seq truncated to 1022, decoys not property-matched; not wet-lab; no
SOTA claim. (payload 755706ee)

## 3k. The engine — closed-loop, uncertainty-guided in-silico discovery (B51)

B48 showed you cannot combine fixed scores past the ceiling; B49 that you cannot represent past it. The remaining lever
is *which data you acquire*. B51 builds the closed Design–Make–Test loop: against a hidden real-bioactivity oracle
(LIT-PCBA; 300 actives + 10,000 inactives, labels revealed only on "test"), a model-guided loop iteratively trains,
scores the pool, selects a batch, and reveals labels. **Closed-loop discovery works:** at a fixed 1,600-compound budget
(~15% of pool), model-guided acquisition recovers **~2.8× more real actives than random** (FEN1 dramatic at ~4.8×), and
the honest explore/exploit tradeoff is exactly as literature predicts — **UCB ≥ greedy ≥ uncertainty for hit recall**,
but **uncertainty gives the better end-model** (untested-pool AUROC 0.602 vs greedy 0.582). The robust win is
model-guided ≫ random; strategy differences are small but directionally correct. This is the first result that
demonstrates INTERCEPTA as an *engine* rather than a set of static modules — and it is the constructive counterpart to
the integration negatives: value comes not from combining scores but from **using calibrated predictions to decide what
to measure next**. In-silico DMTA proxy on real labels (not a live assay), 3 targets, subsampled pool; finding actives
fast ≠ a drug; not wet-lab. (payload e71129f4)

## 3l. External SOTA footing for the generator — GuacaMol (B52)

Our design module (B33 BRICS-GA) had only ever been scored on our own objectives. B52 places it on the community
GuacaMol goal-directed benchmark (Brown et al. 2019) with the *exact* published scoring functions (6 of 20 tasks), vs
the published leaderboard. Honest calibration: the GA **genuinely optimises but is below SOTA** — mean score **0.568 vs
published Graph-GA 0.893** (clears Best-of-Dataset on 2/6). The gap is smallest on MPO (Osimertinib 0.802 vs 0.953) and
largest exactly where **exact structural reconstruction** is required (C11H24 isomers 0.258; rediscovery/similarity
~0.66) — consistent with the analog-level reach seen in B42. So the generator is a real optimiser but would need a
stronger backbone (graph-GA / SMILES-LSTM / RL) to reach SOTA. Outputs are computational hypotheses, not validated
molecules; no SOTA claim; not wet-lab. (payload d67f949d)

## 3m. A boundary condition on ligand-structure sufficiency — the data-regime crossover (B53)

The program's central working principle is *ligand-structure sufficiency*: when actives are plentiful, 2D ligand
structure carries the accessible signal and neither combination nor representation adds to it (B32–B38, B44, B48). B53
tests its **boundary**: since docking needs no ligand data, does structure-based information overtake ligand-based as
known actives N become scarce? On 3 LIT-PCBA targets (scaffold-held-out test; sweep N∈{5..160} training actives;
ligand-QSAR + ligand-similarity vs N-independent Vina docking), the pre-registered "crossover on ≥2/3 targets" is
**false (1/3)** — but the honest reading *refines* the principle rather than rejecting it. The crossover is real yet
**conditional on docking informativeness**: on MAPK1 (kinase, well-defined pocket) docking AUROC 0.633 beats the ligand
QSAR in the scarce regime and is overtaken only near N≈80; on FEN1 (0.485) and VDR (0.409) docking is *below random*, so
nothing crosses and ligand wins by docking's failure, not its own strength. This yields a new low-confidence working
principle — **structure-based information helps when data is scarce only where the docking model exceeds random for that
target (target/receptor-class-dependent, often unmet)**. Two by-products: ligand *similarity* was the weakest channel at
every N (so "consensus fingerprints stay competitive at low N" is weakened — the trained model, not similarity, carries
low-N ligand performance); and rank-fusion *hurt* wherever a below-random channel was averaged in (strengthening B48).
Honest caveat: B53's power is itself bounded by docking fidelity — below-random docking on 2/3 targets most plausibly
reflects an accessible-protocol limitation, and the competing decoy-artifact hypothesis (property-matched decoys) is not
yet excluded. Retrospective, in-silico, 3 targets; not wet-lab. (payload 1ba9729c)

## 3n. Decomposing enrichment — decoy-bias and analog-bias are independent, and the honest residual is small (B54)

The field studies two enrichment biases separately — physicochemical/decoy bias (property-matched decoys; DUD-E,
DeepCoy) and analog/similarity bias (AVE; Wallach & Heifets; MUV). B54 asks the unresolved question: are they
*independent* sources or the same phenomenon, and what binding signal survives *both* controls? A 2×2 factorial on 8
LIT-PCBA targets ({random vs property-matched decoys} × {random-split vs novel-chemistry NN<0.4 actives}) gives a clean
decomposition. Standard AUROC **0.790** falls to **0.628** with both controls; the decoy-bias effect (+0.075) and
analog-bias effect (+0.087) are comparable, and their **interaction is ≈0 (−0.019) — the two biases are independent and
additive**. Quantitatively, ~56% of the enrichment headroom above chance is bias (analog ⊕ decoy) and ~44% is an
irreducible binding-relevant signal — but that residual is strong for only a minority of targets (FEN1 0.80, PKM2 0.67,
VDR 0.66; five of eight near-chance). This **recalibrates the program's positive thread**: our B42/B43/B46 enrichment
(~0.78) was single-controlled at most and overstated the true binding signal, whose honest ceiling on doubly-controlled
data is ~0.63. It yields a new working principle — **VS enrichment biases are approximately independent/additive, so
honest evaluation must control both** — and partially vindicates the decoy-artifact wild-card while falsifying its
catastrophic form (residual > chance). Caveat: 6-descriptor matching is a *lower bound* on decoy artifact (finer
matching could shrink the residual further); 8 targets; not wet-lab. (payload 494d30c7)

## 3o. Trying to graduate P6 — and discovering DUD-E cannot support the test (B55)

A working principle must survive an external benchmark family. B55 attempted to replicate P6 (bias
independence/additivity, B54) on DUD-E — a different construction (ChEMBL actives, property-matched topology-dissimilar
ZINC decoys). It could not: the pre-registered novel-chemistry (NN<0.4) analog-control arm is **empty on all 8 targets**
because DUD-E actives are extraordinarily analog-clustered (panel-mean leave-one-out NN-Tanimoto **0.71**; only ~4.6%
of actives are NN<0.4). A sharper by-product: every DUD-E active has a *distinct Murcko scaffold* (unique-scaffold ratio
≈1.0) yet mean NN is 0.71 — so **scaffold-splitting does not control analog similarity on DUD-E**, and "scaffold-split
novelty" is illusory there (a concrete methodological warning: use explicit NN-distance, not scaffold split, for analog
control on clustered benchmarks). Integrity note: the initial factorial run emitted a NaN "P6 fails" verdict; that
unsupported conclusion was discarded (not committed) and the runner refocused to this honest diagnostic (prereg amended,
dated). **P6's status is therefore unchanged — externally untested, neither replicated nor falsified** — and its
external replication is deferred to a chemically-diverse benchmark (MUV). Retrospective, in-silico, 8 targets; not
wet-lab. (payload 09a0eb27)

## 3p. Graduating P6 — the bias-independence law replicates on a second benchmark family (B56)

A working principle must survive a different benchmark family. After a Phase-2 review disqualified DUD-E (B55: actives
too analog-clustered to run the test) and MUV (designed-unbiased → nothing to decompose; ~30 actives), the correct
instrument is the TDC/Butkiewicz PubChem-HTS panel — verified to have diverse actives (~46–54% NN<0.4) *and* natural
biases. Running the B54 factorial verbatim there, **P6 replicates cleanly: interaction −0.0005** (B54: −0.019), with
decoy-effect +0.050 and analog-effect +0.100 (B54: +0.075, +0.087) and doubly-controlled residual 0.677 (B54: 0.628).
Per-target interactions are all within ±0.013. The two enrichment biases are therefore **independent and additive
across two benchmark families and multiple target classes**, with a mechanistic rationale (they act on geometrically
different axes — chemical-space *similarity* vs *physicochemical-property* distribution). A refinement: **analog bias is
consistently ≥ decoy bias.** An internal-consistency check strengthens confidence: HIV's enrichment is almost entirely
analog-driven here (analog +0.196, residual ≈ chance), *independently reproducing* the "HIV is similarity-driven"
finding of B45. Honest boundary: both families are PubChem-HTS-derived, so this is a *moderate* (not maximal) external
test — P6 is not tested against a fundamentally different decoy paradigm (property-matched ZINC, à la DUD-E), because no
benchmark offers diverse actives *and* that construction (an inherent data limit). P6 is thus a **replicated principle
with a mechanism, not yet a universal one.** Retrospective, in-silico, 5 targets; not wet-lab. (payload 32469564)

## 3q. Why is the residual target-dependent? — an honest null (B57)

B54/B56 left the doubly-debiased binding signal (A1B1) strongly target-dependent (≈chance for HIV/ALDH1/KAT2A; ~0.77–
0.80 for STK33/FEN1). B57 asks whether a simple target property predicts it — the natural hypothesis being SAR
ruggedness / activity-cliff density (rugged landscapes defeat descriptor QSAR). Across the 13 targets with a reproduced
residual, **no measured property explains it** (all |Spearman| < 0.5, n=13): activity-cliff density −0.36 (correct sign
but weak, below the pre-registered −0.5 bar), assay-type −0.39 (an artifact — one phenotypic target), active-diversity
+0.28, n_actives +0.09. So the residual's target-dependence is **not** captured by cliff density, diversity, assay
type, or data richness. Honest bounds: n=13 is underpowered (the −0.36 cliff signal is directionally right and may be a
real weak effect), the cliff metric is a crude threshold operationalization (a continuous roughness index could do
better), and residual seed-noise attenuates the correlation — so this is "not confirmed at this power," not "no effect."
The practical consequence: we can quantify that ~half of ligand-based VS enrichment is bias (P6) and that the residual
varies by target, but we **cannot yet predict *which* targets retain real signal** — that remains open. Retrospective,
in-silico meta-analysis, n=13; not wet-lab. (payload dc4c6654)

## 3r. Re-powering the residual mechanism — roughness matters, but only partly (B58)

B57's null (no property explains the residual) was underpowered (n=13) and used a crude single-threshold cliff metric.
B58 re-tests with a principled multi-scale roughness index (ROGI, reimplemented dependency-free and validated: rough
0.42 > smooth 0.17) and more targets (n=19; LIT-PCBA + TDC/Butkiewicz HTS). Result: the doubly-debiased residual is
still **not cleanly predicted by any single property** (no |Spearman| ≥ 0.5), but **SAR roughness is a genuine partial
driver** — ROGI correlates −0.42 (correct sign: rougher landscape ⇒ less irreducible signal) and clearly **beats the
crude cliff density (−0.22)**. So B57's flat null was partly a crude-metric/low-power artifact (vindicating its
self-critique); a proper roughness index recovers a moderate, real effect. A suggestive secondary signal: the two
phenotypic (cell-based antiviral) endpoints have the lowest residuals — consistent with activity not being a single
binding-event function there (underpowered, flagged not claimed). The honest conclusion is a **partial, multifactorial**
mechanism (candidate low-confidence principle: *post-debiasing signal decreases with landscape roughness*), and a
methodological point (principled ROGI > threshold cliff). We do **not** achieve a predictive rule for "when is
ligand-based VS trustworthy" — the dominant driver likely needs 3D/pocket features, continuous potency, or larger n.
Retrospective, in-silico meta-analysis, n=19; ROGI reimplemented (validated, not bit-exact); not wet-lab. (payload 54865883)

## 3s. Does the residual depend on assay format? — a null that bounds B58 (B59)

B58 flagged a *suggestive* assay-type signal (Spearman −0.44), but it rested on only 2 phenotypic targets. B59 tests
whether it generalizes to a powerable **biochemical (isolated-protein) vs cell-based (functional + phenotypic)**
dichotomy across the 19 targets (confirmatory/post-hoc; residuals already committed). It does not: biochemical vs
cell-based median residual **0.597 vs 0.646** (Mann–Whitney two-sided p=0.71; one-sided biochem>cell p=0.36;
rank-biserial −0.11 — if anything cell-based is marginally higher), and a sensitivity analysis excluding the 3
ambiguous targets stays null (p=0.23). So B58's assay-type signal was **driven by the 2 phenotypic antiviral points, not
a general assay-format effect**, and the *pure* phenotypic test is infeasible (only 2 such datasets exist). The residual's
target-dependence therefore remains **unexplained** — consistent with B57/B58 — and we do not claim a phenotypic
mechanism. This is a first-class null that correctly bounds an over-eager reading of B58. Confirmatory/post-hoc, n=19;
not wet-lab. (payload 2d7628c5)

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
shipped package; controlled/patient data are never committed. Shipped tools: `intercepta {info, rank, synergy, admet, synth, prioritize, generate, discover, screen}` (9th tool `screen` = the consolidated virtual-screening engine: calibrated QSAR + applicability-domain + conformal + the B51 active-learning loop; `intercepta.screen.VirtualScreener`). Experiment index with payload hashes: B30 af66698f · B30b 50cc195c · B31 c6edd9bc ·
B32 81996f21 · B32b 7d7a305c · B33 d91f0470 · B34 6c4b5e81 · B35 04c20605 · B36 ea088da2 · B37 c8d16b06 · B38 c17e47f4 · B39 23a7ae0c · B40 e62417bf · B41 359486bf · B42 9d99060e · B43 daca99a2 · B44 1120c3d3 · B45 e437713b · B46 33d754cd · B47 24d5b0f6 · B48 68c5b043 · B49 755706ee · B51 e71129f4 · B52 d67f949d · B53 1ba9729c · B54 494d30c7 · B55 09a0eb27 · B56 32469564 · B57 dc4c6654 · B58 54865883 · B59 2d7628c5.
