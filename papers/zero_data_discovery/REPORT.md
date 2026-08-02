# Zero-data drug discovery: an honest map of what transfers, what doesn't, and a self-improving loop that knows its limits

*A consolidation of the INTERCEPTA "zero-data disease" research arc (2026-07/08). Written to be understandable without
reference to INTERCEPTA: it is a set of falsifiable claims about the behaviour of computational drug-discovery
capabilities when a target/pathogen has NO activity data — only its sequence, structure, and transferable prior
knowledge. Every number traces to a committed, pre-registered, reproduced-×2 experiment (LEDGER.md).*

## The question
When a new pathogen appears with **zero activity data** — no known inhibitors, no assays, no training labels — how far
can a computational system get toward credible drug candidates from **sequence and transferable knowledge alone**, and
**where exactly does it break**? This arc builds each capability, validates it on well-understood organisms/targets (the
proving ground), and — crucially — reports the honest boundary of each, controlled against the trivial baselines the
field often skips.

## The findings (each a controlled, reproduced result)

**1. Target identification from sequence is dominated by generic conservation.**
Ranking a pathogen's proteome for druggable targets by transferring druggability from *other* organisms' known targets
(leave-organism-out homology) recovers known targets only about as well as a **generic conservation null** — homology to
*any* related protein (AUROC ≈ 0.64 vs 0.72 null; TID1). Adding **intrinsic structural pocket druggability** (fpocket on
predicted AlphaFold structures — a signal that is conservation-free *by construction*) does **not** meaningfully help:
it is near-random alone (AUROC 0.54) and adds only a whisper after conditioning on conservation (held-out ΔAUROC +0.005,
partial coef 0.07 vs conservation 0.70; TID2). **Conclusion: for zero-data target-ID, "how conserved is this protein"
(≈0.73 AUROC) is the robust workhorse; neither target-specific homology nor pocket geometry beats it. The practical,
honest recipe is rank-by-conservation + host-nonhomology selectivity + calibrated abstention** (abstention is
well-calibrated: the ~92% of proteins with no homolog are correctly flagged low-confidence, and the committed-to
minority is enriched for true targets). **This degrades monotonically across kingdoms** (TID3): target recovery falls
bacteria → parasite → fungus as the held-out organism becomes phylogenetically isolated from the reference, and the
kingdom-isolated fungus recovers *none* of its targets — homology transfer weakens with evolutionary distance.
**Critically, the abstention does NOT track this failure** (the fungus abstains at the same rate yet recovers nothing —
confidently wrong), so the honest boundary is sharp: **zero-data target-ID works only for organisms with reasonably-close
characterized relatives, and silently fails on phylogenetically isolated pathogens** — a real limitation for the
truly-novel-pathogen case the vision targets. **And this silent failure is not cheaply fixable** (TID4): across an
expanded 11-organism panel, no label-free query-time signal (homological connectedness, closest-relative proximity)
predicts whether target-ID will succeed for a given organism (best Spearman −0.31; organism-level abstention worse than
random) — well-connected pathogens can recover nothing while distant ones recover well. So the system genuinely cannot
tell, from sequence alone, *when it is out of its depth* — a hard limitation for deploying on a novel pathogen. **But a genuinely orthogonal signal DOES break the ceiling** (MET1): mechanistic FBA gene-essentiality — computed from an organism's own genome-scale metabolic model, not from homology — enriches strongly for drug targets (odds ratio 8.6) and adds target-ID signal *beyond* conservation (5-fold-CV ΔAUROC +0.132, essentiality outweighing conservation 0.71 to 0.35) on E. coli's metabolic subproteome. So the ceiling is specific to *homology-based* signals; a mechanistic layer is the path through it — bounded, for now, to metabolic targets. Building metabolic models DE NOVO from each proteome (CarveMe, UniProt-keyed by construction) shows this **generalizes across bacteria** (MET2): FBA-essentiality enriches for drug targets universally (odds ratio 5.8–18.5 in E. coli, M. tuberculosis, P. aeruginosa) and adds beyond conservation in 2/3 + pooled — a genuine, generalizing mechanistic capability (more modest with de-novo default-medium models than the curated E. coli one).

**2. Structure-based binding carries a real but weak zero-data signal.**
Docking compounds into a target's pocket with **zero target activity data** separates real binders from non-binders
significantly (Mann-Whitney p=0.0001) but weakly — near-random *early* enrichment (AUROC 0.63, EF1% ≈ 1.25; C1 on
SARS-CoV-2 Mpro). This reproduces the field's known "docking ranks poorly prospectively" ceiling on our own setup. The
one reliable free upgrade (GNINA CNN rescoring, ~2×) is Linux/CUDA-only and was infeasible on the available hardware —
so the honest output of the binding stage is *pose-plausible candidate hypotheses, not potency-ranked leads*.

**3. The pieces compose end-to-end from a proteome.**
The validated capabilities wire into one zero-data pipeline — proteome → target-ID → pocket → docking → ADMET/synth →
ranked, confidence-tiered candidate shortlist — and run end-to-end on a real pathogen (M. tuberculosis, zero TB activity
data; E2E1). It self-reports every limit: the composite target ranking does not beat conservation, docking is weak at
the top, and the output is explicitly *computational hypotheses, not validated hits*. The value is demonstrating the
shape of the system at small scale, honestly bounded.

**4. A self-improving loop that helps where it has signal — and knows where it doesn't.**
Feeding a model's **own conformally-confident predictions** back as pseudo-labels ("the system learns from its own
validated findings") **modestly but consistently improves** a task in-domain (median ΔAUROC +0.011, 6/6 tasks; SIL1) —
and the **confidence-gating is the guardrail**: ungated or shuffled/fake feedback does *not* help and clearly hurts
(shuffled −0.043), while conformal confidence genuinely identifies trustworthy self-knowledge (gated pseudo-label
accuracy 0.886 vs 0.772 pool). But the benefit is a **near-domain phenomenon**: on **novel chemistry** (compounds unlike
training) it becomes a wash — barely-positive median but a coin-flip across targets (SIL2) — so self-accumulated
in-domain knowledge does **not** reliably cross the novel-chemistry information ceiling. **Conclusion: a self-improving
loop is real and safe when gated by calibrated confidence, but its reach is bounded to the regime where the model
already has signal.**

## What is genuinely contributed
- A **well-controlled negative-boundary** on zero-data target identification: conservation is the ceiling; more homology
  (sequence, structural, or learned) mostly re-encodes it — a result the field's positive-publication bias rarely
  produces, established here against degree/conservation nulls with calibrated abstention.
- A **rigorous demonstration of a self-improving loop and its anti-self-deception guardrail** (with the shuffled/ungated
  negative controls most such claims omit), tied to calibrated conformal prediction — plus its honest boundary
  (near-domain only).
- The **reusable discipline** throughout: pre-registration, reproduce-×2, trivial-baseline/null controls, verdict
  honesty (auto-verdicts that over-read a coin-flip median were corrected pre-commit, repeatedly), and explicit scope.

## Honest scope and what remains gated
All results are retrospective and in-silico, on open data, on a modest pathogen/target panel. None is a validated hit, a
drug, or a clinical claim. The recurring theme is an **information ceiling**: for genuinely novel chemistry/targets,
transfer-based signals are weak and self-accumulation cannot manufacture information that isn't there. Crossing that
ceiling requires *new information* — prospective assays, wet-lab, or 3D/experimental data — which is a resource decision,
not a computation. What the arc delivers is an honest map of exactly how far sequence-and-transfer-only discovery
reaches, and where — and why — it stops.
