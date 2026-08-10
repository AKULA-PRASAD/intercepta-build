# AFFINITY1 — Training-Data Leakage Audit (Boltz-2)

*Independent audit of whether the AFFINITY1 benchmark (Boltz-2 co-folding affinity vs AutoDock Vina on
the CHEMBL204 thrombin set) can legitimately be described as **zero-shot** with respect to Boltz-2.
Reconstructed from public sources + this repo. Last updated 2026-08-09.*

## Question
Is Boltz-2's affinity performance on our benchmark a zero-shot result, or is it (partly) recall of
training data? A "zero-shot" claim requires the target and ligands to be **outside** Boltz-2's training.

## Two independent leakage channels
- **Channel A — structure memorization** (co-folding backbone): if thrombin's fold is in the PDB
  training set, the pocket is recalled, not predicted. Affects pose quality; weakly affects the affinity claim.
- **Channel B — affinity-label memorization** (the affinity head): if the head trained on thrombin–ligand
  affinities, the AUROC is partly recall of labels. **This is the decisive channel.**

## Evidence — VERIFIED FACTS (Boltz-2 technical report, bioRxiv 10.1101/2025.06.14.659707)
1. **Affinity head training corpora:** binding-affinity measurements from **PubChem, ChEMBL, and BindingDB**,
   standardized with the **ChEMBL Structure Pipeline**; a "hit-to-lead affinity training set" plus a
   BindingDB/ChEMBL "protein-ligand distillation" set.
2. **Structure model cutoff:** "every PDB structure up to the training date cutoff of **2023-06-01**."
   Thrombin (PDB 1OYT, deposited 2002) is inside this window.
3. **Boltz-2's own leakage control:** exclude training proteins with **≥90% sequence identity to proteins
   in Boltz-2's *own* validation/test sets**. Their held-out affinity sets are **FEP+ (OpenFE/Schrödinger),
   MF-PCBA, and a KLIFS virtual screen** — **thrombin / CHEMBL204 / MoleculeACE are not among them.**
4. **Our benchmark provenance:** `benchmark_data/CHEMBL204_Ki.csv` / `test_novelty.csv` are a **ChEMBL
   thrombin (CHEMBL204) Ki extract** (via MoleculeACE) — the *same source database* as Boltz-2's affinity data.
5. Boltz-2's paper itself reports affinity accuracy binned by **max-Tanimoto-to-training-set** similarity —
   i.e., the authors acknowledge performance is similarity-to-training dependent.

## Inference
- **STRONG (high confidence, not byte-proof):** because the head trained on ChEMBL/BindingDB, thrombin is
  one of the most data-rich targets in those databases, and thrombin was **not** in Boltz-2's held-out sets
  (so their 90%-identity filter would not remove it), **thrombin and its ChEMBL ligands — our exact
  benchmark compounds and affinities — were almost certainly in Boltz-2's affinity training set.**
- **Conclusion: this benchmark is NOT a zero-shot evaluation of Boltz-2 and must not be described as one.**

## What CANNOT be verified (honest limit)
Byte-level, per-compound confirmation is **impossible with public information**: Boltz-2 has not released
its exact affinity-training manifest (training code "coming soon"). Step "exact-match our 553 SMILES
against Boltz's training ligands" is therefore **blocked**, not passed. The provenance argument makes
contamination near-certain; it remains a strong inference, not a checksum.

## Corrected nuance (a self-correction on an earlier over-claim)
An earlier analysis claimed the 0.68 AUROC is "largely leakage-inflated interpolation, true zero-shot ≈
chance." **The data does not support that.** Discrimination is roughly **flat** across chemical-similarity
bins (AUROC 0.60–0.68 across `nn_tan` bins; Spearman(nn_tan, prob | actives)=0.095), with no steep
similarity gradient. So:
- **Contamination of the training set ≠ demonstrated inflation of this score.**
- The "zero-shot" *label* is indefensible (provenance), but the **quantitative effect** of contamination
  on the 0.68 is **unknown/unquantified** — not "it's all recall."
- Caveat: `nn_tan` measures similarity to the *MoleculeACE* actives, not to *Boltz's* training set (which
  we cannot access), so this is evidence *against a strong gradient*, not proof of no effect.

## Confidence summary
- Not zero-shot w.r.t. Boltz-2: **high confidence** (verified provenance + structural inference).
- Magnitude of leakage's effect on the AUROC: **unknown** (no measurable similarity gradient; manifest unavailable).

## Defensible vs indefensible statements
**Defensible:** "Boltz-2's affinity head and our benchmark share ChEMBL/BindingDB provenance; thrombin and
its ligands were almost certainly in training, so AFFINITY1 is **not a zero-shot evaluation of Boltz-2**."
· "Boltz's absolute discrimination on thrombin actives is **moderate (AUROC ≈0.68)**."
**Indefensible (must not claim):** "zero-shot affinity"; "Boltz beats docking zero-shot"; any
novel-target / novel-chemotype generalization; any prospective-utility implication.

## What a TRUE zero-shot test requires
A **temporal or contamination-controlled holdout**: affinities **published after** Boltz-2's data window,
and/or a target absent from ChEMBL/BindingDB pre-cutoff, evaluated specifically on chemotypes with low
max-Tanimoto to Boltz's training — and **powered** on novel chemotypes (our benchmark has only 5 novel
actives, which cannot support any novel-chemotype conclusion).
