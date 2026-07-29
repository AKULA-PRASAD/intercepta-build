# Decision log — INTERCEPTA build (append-only)

## 2026-07-29 — D1: Seed a clean, separate Phase-B build repo
Decision: create `~/INTERCEPTA_BUILD` distinct from the 22 GB exploration tree (`~/INTERCEPTA`) and the audit
repo (`~/kaalcura`). Rationale: the build must contain only verified, reproduced, provenance-tracked work; the
exploration repos carry falsified/abandoned branches that would blur the ledger. Reversible.

## 2026-07-29 — D2: Phase B scope = transcriptomic drug-response prediction, not therapy selection
Decision: build against the near-term, achievable, evidence-supported goal (Phase B), not the falsified
therapy-selection claim. Rationale: LEDGER V1 (a real transferable signal exists) supports Phase B; the
selection coordinate is falsified at power (<5%). Novel ideas (velocity time machine) stay in the ledger as
untestable until the specified data exists — not in the build path.

## 2026-07-29 — D3: The bar is +0.212, established in-repo by B1 before any new modeling
Decision: no new model is accepted until B1 reproduces the leakage-free ceiling inside this repo, and every
future model is measured against it with the full falsification battery + external replication. Rationale:
Constitution rules 3 & 8 — bar before boast, positives guilty until proven innocent.

## 2026-07-29 — D4: Data referenced by sha256 manifest, never committed
Decision: inputs stay out of git; `INTERCEPTA_DATA` env var + `data/MANIFEST.md` sha256 verification at load.
Rationale: reproducibility without shipping 1.5 GB of public data or risking a silent data swap.

## 2026-07-29 — D5: B2 is a null → stop tuning models, pursue the missing data next
Decision: B2 confirmed +0.212 as the public cell-line ceiling (adding R_prolif and driver mutations both
null, reproduced ×2). We will NOT keep adding features/architectures to chase a public-data ceiling that the
evidence says is real. Rationale: Constitution rules 4–5 (compress; negatives first-class) — the informative
next lever is DATA, not modeling. Next experiments target the two things the ledger says are missing:
(B3) patient transfer — does the GDSC-trained map rank response in a real tumor cohort (TCGA/clinical
expression), the first cell-line→patient generalization test; and (B4, human-gated) controlled-access
RCTs with treatment×biomarker design to revisit the falsified selective-axis question with adequate power.
No more "beat the ceiling on cell lines" experiments unless a new public dataset materially changes the setup.

## 2026-07-29 — D6: L1 is PARTIAL — patient transfer is real but non-specific; do not claim drug-level prediction
Decision: B3 shows the GDSC map transfers to real BeatAML patients (diagonal ρ=+0.054, perm p=0.0005) but the
signal is NOT drug-specific (diag≈off-diagonal, p=0.12) and does not beat a proliferation-only transfer. So we
record L1 as a genuine-but-bounded milestone: "cell-line models carry a real, generic chemosensitivity signal
into patients; drug-level patient prediction is NOT established." We will NOT advertise patient drug selection.
Rationale: Constitution rules 3, 8, 9 — the specificity/proliferation controls failed, so the strong claim is
not earned. What would earn it (pre-registered for a future rung): matched-platform patient data (RNA-seq
train, e.g. GDSC RNA-seq or PDX), larger per-drug patient n, and a specificity-preserving method
(drug-conditioned / residual-on-proliferation modeling). L2 (controlled trials, human-gated) unchanged.

## 2026-07-29 — D7: L1b PASSES and replicates — a real (weak) drug-level patient signal; hold the claim to what replicated
Decision: B3b (matched RNA-seq platform + proliferation-residualized) found a drug-specific cell-line→patient
signal (diag−off +0.040, perm p=0.010); B3c replicated it with INDEPENDENT GDSC1 labels (+0.051, p=0.0015, 59
drugs). Both reproduced ×2. We record L1b as PASSED and the vision advances toward L3. **But the claim is
bounded to exactly what replicated:** weak (ρ≈0.07–0.08), one patient cohort (BeatAML, AML only), two label
screens. We will NOT say "validated patient drug predictor." Rationale: Constitution rules 3/9 — the positive
survived permutation + specificity + proliferation-residualization + independent-label replication, so it is
believed; it has NOT survived a second patient cohort or cross-cancer test, so those stay open. Next real gate
(D8): a SECOND independent patient drug-response cohort (other AML functional cohorts, or a solid-tumor
PDX/ex-vivo cohort) — likely controlled-access = human gate. Also outward/gated and NOT auto-done: publishing
the repo to GitHub (needs Prasad's remote+auth) and L2 dbGaP/EGA trials — surfaced to Prasad, not faked.
