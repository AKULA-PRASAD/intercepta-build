# MENDEL1 — Mendelian (germline monogenic) intervention-mode + druggability-triage arm

**Verdict: PASS (new validated Mendelian coverage arm) + a first-class NEGATIVE on the structural-druggability sub-arm.**
Reproduced x2 byte-identical, payload sha256 `cb1be2437b386ed839129b3dadf7af7836ae3ca319b14f17b449af7e4b78d1ae`.

## What this arm adds
The first INTERCEPTA coverage for **human germline monogenic disease** — a disease class with a *different zero-data shape*
than every prior arm. The causal gene is genetically ESTABLISHED (OMIM/ClinVar/UniProt), so the task is not
popularity-confounded target-ID (the DEPEND1/F3CLIN1 near-random negative) but **reasoning from a proven causal gene to a
credible intervention MODE, with an honest small-molecule feasibility triage that ABSTAINS where no small molecule can work.**

## Ground truth (n=28, every triple REAL + cited; ground_truth.json)
Balanced across three modes: RESTORE_SM=11 (potentiate/correct/chaperone/cofactor/stabilizer/bypass), INHIBIT_SM=7
(block over-active target / druggable downstream node), NOT_SM=10 (replace / gene therapy / ASO — the fail-safe class).
Exemplars: CFTR->ivacaftor, TTR->tafamidis, GLA->migalastat, SMN1->risdiplam, RET->selpercatinib, PIK3CA->alpelisib,
TSC2->everolimus (downstream) vs DMD/F8/GAA/HTT/SOD1-> replacement/ASO/gene.

## Pre-registered result (gate frozen in PREREG.md before scoring)
- **G1 — mode accuracy: PASS.** Mechanism-first 3-class accuracy **0.857** (24/28) vs majority baseline **0.393** and a
  naive direction-only baseline **0.464**. (Gate: >=0.60.)
- **G2 — FAIL-SAFE (hard integrity gate): PASS.** **0 of 10** true NOT_SM genes received a small-molecule call. Every
  error the system makes is a *conservative abstention* (predicts NOT_SM when a small-molecule route actually exists),
  never a false small-molecule promise. Contrast: the naive direction baseline commits **10** fail-safe violations.
- **G3 — does fpocket structural druggability add value? NEGATIVE.** fpocket best-pocket Druggability Score gives only
  weak univariate separation (AUROC **0.636**, SM-feasible vs NOT), and when *used in the decision* (Variant A) it
  **lowers** balanced accuracy (-0.033) **and breaks the fail-safe** (F8: a secreted coagulation factor scores a spurious
  druggable pocket 0.654 -> wrongly routed to a small-molecule call). Structural druggability answers "is there a pocket,"
  not "can a small molecule fix this disease."

## Honest scientific findings (why this is not a tautology)
1. **Mode DIRECTION is near-known-biology, but feasibility is NOT.** The invention is the *feasibility gate* that produces
   the NOT_SM/abstain class. It is what beats the baseline and eliminates unsafe calls; direction alone (naive) scores worse
   and is unsafe.
2. **The determinant of small-molecule feasibility for a LoF gene is MECHANISM, not pocket:** whether there is *residual
   protein to rescue*. `mut_class == null` (GAA/IDUA/ADA/HEXA — enzymes with excellent druggable pockets: 0.74/0.14/0.92/0.71)
   correctly routes to replacement, whereas `missense_misfold` (GLA/CFTR/GBA) routes to a chaperone/potentiator. fpocket
   cannot see this — it high-scores the null enzymes.
3. **fpocket is not just useless here, it is unsafe:** high spurious pockets on secreted/replacement targets (F8) would
   generate false small-molecule promises. Reported first-class.
4. **Declared blind spots held exactly** (pre-registered before scoring): downstream-node druggability (TSC2->mTOR,
   NF1->MEK, VHL->HIF2a) and splice/paralog bypass (SMN1->risdiplam) are missed — but *safely*, as abstentions.

## Scope / limits (honest)
In-silico; n=28 hand-curated seed (not a census); MODE + feasibility TRIAGE only — NOT a molecule, NOT a potency/affinity
claim (the zero-shot affinity wall of HIT2/B49/B65 stands and is out of scope). "sm_feasible" = a documented target-directed
small-molecule mechanism exists, not that it is efficacious/safe for every allele (several are allele-dependent, e.g.
migalastat only for amenable GLA missense). The TOXIC_AGG->stabilizer branch is supported by only n=2 (TTR, HBB) — the
least-generalizable rule. HTT absent from AlphaFold DB (fpocket N/A; mechanism triage unaffected). Not wet-lab.
Router-wiring deferred (standalone build per directive).

## LEDGER one-liner
MENDEL1 (new Mendelian coverage arm): PASS — a mechanism-first intervention-MODE triage classifies germline-monogenic
causal genes 0.857 vs 0.393 majority and is FAIL-SAFE (0/10 not-small-molecule cases mis-promised a drug); with a
first-class NEGATIVE that structural druggability (fpocket on AlphaFold) does NOT add and is unsafe (breaks the fail-safe
on F8) — feasibility is set by mechanism (residual-protein: null vs misfold), not by pocket. Reproduced x2, sha cb1be243.
In-silico, n=28 cited seed, triage-not-molecule.
