# GENERALIZE1 — pre-registered BLIND generalization test: does the label-free method point at the right intervention target for an EMERGING VIRUS?

**Registered (Stage 1) BEFORE scoring against any known-drug-target answer.** This is the North Star's
central, previously-untested claim: *"any disease, including unknown or emerging."* Everything validated so
far (FBA gene-essentiality on genome-scale metabolic models) is bacterial-metabolism machinery that **does
not exist for a novel virus**. This test asks whether a purely label-free, homology-anchored signal — with
no metabolic model and no essentiality screen — can blindly identify the correct intervention targets of an
emerging viral pathogen.

## Pathogen & rationale
**SARS-CoV-2** as a stand-in emerging pathogen: (a) genuinely emerged novel; (b) tiny proteome (~29 mature
proteins) so the ranking is fully auditable; (c) the validated intervention targets are unambiguously known
*after the fact*, giving an objective ground truth to score against.

## Deployment scenario (deliberate, with hard leakage control)
The scenario is "a new virus, nothing drugged against it or its relatives yet." To enforce this, **every
coronaviral entry is removed from the drug-target reference** (24 rows: 23 "Severe acute respiratory syndrome
coronavirus 2" + 1 "Severe acute respiratory syndrome-related coronavirus"). Any signal must therefore come
from **non-coronaviral** drugged proteins (HCV, HIV, rhinovirus, influenza, herpes, and all non-viral drug
targets). This makes it a true "does the emerging virus resemble something humanity has drugged before,
without having drugged it or its family" test.

## Method (label-free; the known COVID answer is never consulted to produce the ranking)
1. Fetch the SARS-CoV-2 mature proteome (polyproteins pp1a/pp1ab split into nsp1–16 via UniProt chain
   features; plus structural/accessory proteins S, E, M, N, ORF3a/6/7a/7b/8/9b/10).
2. mmseqs each mature viral protein vs the **coronavirus-free** ChEMBL drug-target reference
   (`drug_targets.fasta`), e-value ≤ 1e-5.
3. Score each protein = best drug-target-homolog bitscore (0 if no hit ≥ threshold). Rank descending. This
   is the label-free "intervention-target-worthiness" ranking. No COVID drug knowledge enters it.

## Ground truth (revealed/fixed now, used ONLY in Stage 2 scoring)
Clinically **approved** SARS-CoV-2 antiviral targets:
- **nsp5** (Mpro / 3C-like main protease) — nirmatrelvir (Paxlovid), ensitrelvir.
- **nsp12** (RdRp) — remdesivir, molnupiravir.
Conservative POSITIVE set P = {nsp5, nsp12}. (Secondary, not required: nsp3/PLpro, nsp13/helicase.)

## Pre-registered hypothesis & decision rule (fixed now, before scoring)
**H1:** the two approved-drug targets rank at the top of the label-free druggability ranking.
- **PASS** ⇔ **both** nsp5 (Mpro) AND nsp12 (RdRp) are in the **top-5** of the ~29-protein ranking, AND both
  have a genuine non-coronaviral drugged homolog (bitscore > 0 after leakage removal).
- **PARTIAL** ⇔ exactly one of {nsp5, nsp12} is in the top-5 (reported as such, not upgraded).
- **FAIL** ⇔ neither is in the top-5 — reported first-class as an honest negative: the label-free signal does
  not generalize to point at viral intervention targets. Recorded, not re-run to a better number, not hidden.

I also pre-commit to reporting the **full ranked table** of all proteins (so the reader sees where the true
targets fall and what outranks them), and the top-5 precision.

## What this does and does NOT show
Even a PASS shows only that the method *ranks the correct druggable targets highly from sequence homology
alone* — an in-silico target-prioritization signal on one virus. It does NOT establish an actual drug, potency,
resistance, host toxicity, or clinical effect; it is not wet-lab; n=1 pathogen (a single generalization data
point, explicitly not a claim about all viruses). A PASS would be the first evidence the approach extends
beyond bacterial metabolism toward the North Star's "any/emerging disease" scope; a FAIL honestly bounds the
method to organisms with metabolic-model machinery.

---
## REVEAL OUTCOME (Stage 2 — appended after Stage 1 is committed)
**Result: FAIL — honest negative (reproduced ×2, payload sha d58f9e7e).** At the pre-registered threshold
(e ≤ 1e-5), **0 of 30** SARS-CoV-2 mature proteins had ANY non-coronaviral drugged-*sequence* homolog. A
relaxed diagnostic probe (e = 100, max sensitivity) found only noise (best hit e ≈ 0.13, ~29% identity over
31 residues). The approved-drug targets nsp5/Mpro and nsp12/RdRp did **not** clear the gate (no detectable
homolog; their apparent rank positions #5/#11 are input-order artifacts among all-zero scores, so the gate
requires bits > 0 to count — corrected in `score.py`).

**Meaning (honest):** the SEQUENCE-homology intervention signal that works for bacteria (INTERVENE1 — where a
pathogen's drugged homologs are evolutionarily close) does **not** generalize to a divergent emerging virus.
Cross-family viral sequence identity (e.g. SARS-CoV-2 Mpro vs picornaviral 3C protease; RdRp vs HCV NS5B /
HIV RT) is below sequence-detection limits. This is a genuine boundary of the method, reported first-class,
not re-run to a better number.

**What it points to (hypothesis, tested separately in GENERALIZE2, not claimed here):** the enzyme FOLDS
(chymotrypsin-like protease fold; right-hand RdRp fold) are conserved even when sequence is not, so a
STRUCTURAL-homology bridge (Foldseek) is the correct tool for cross-family viral target prioritization.
This negative is precisely what motivates the structural follow-up.
