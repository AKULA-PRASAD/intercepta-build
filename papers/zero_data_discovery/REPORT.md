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
tell, from sequence alone, *when it is out of its depth* — a hard limitation for deploying on a novel pathogen. **But a genuinely orthogonal signal DOES break the ceiling** (MET1): mechanistic FBA gene-essentiality — computed from an organism's own genome-scale metabolic model, not from homology — enriches strongly for drug targets (odds ratio 8.6) and adds target-ID signal *beyond* conservation (5-fold-CV ΔAUROC +0.132, essentiality outweighing conservation 0.71 to 0.35) on E. coli's metabolic subproteome. So the ceiling is specific to *homology-based* signals; a mechanistic layer is the path through it — bounded, for now, to metabolic targets. Building metabolic models DE NOVO from each proteome (CarveMe, UniProt-keyed by construction) shows the essentiality↔drug-target ENRICHMENT is broad across bacteria (MET2: odds ratio 5.8–18.5 in the organisms with enough targets to test), and the *beyond-conservation* ceiling-break REPLICATES in the two bacteria with enough drug targets for a reliable estimate (E. coli +0.053, M. tuberculosis +0.040) — a genuine replication. Broader bacterial generalization is honestly NOT ESTABLISHED (nor disproven): most bacteria have too few known drug targets (≤20) to test reliably — the limit is ground-truth sparsity, not the signal. (An initial 3-organism run over-claimed 'generalizes'; an expanded 7-bacteria panel tempered it to this honest picture.) Finally, because a discovery pipeline consumes a *ranked* shortlist rather than a regression coefficient, we ask whether that gain reaches the *top* of the list where target-ID decisions are made (MET3): adding essentiality to the ranking lifts precision-at-k substantially on E. coli (0.28→0.35, enrichment 4.9→6.2× over prevalence, top candidates recovering real essential-metabolic targets — AcrB, IspF, MurG) but only marginally on M. tuberculosis (+0.015, ≈ one extra target — the global-AUROC gain does not fully reach the top of that list). So the mechanistic signal is a genuine *practical* front-half improvement, clearly organism-dependent in magnitude: strong where it lands, real but weak where the list is already harder.

Crucially, this mechanistic win is scoped to *metabolic* targets — FBA is blind to roughly half of all drug targets (proteases, polymerases, ribosomal and structural proteins, the kind a novel pandemic often presents). We tested the obvious extension to that FBA-blind half — PPI-network topology essentiality (network hubs/bottlenecks), a mechanistic signal independent of homology *if the network is measured* (MET4). The naive result looked like a second ceiling-break: on a non-homology experimental interaction network, centrality added ΔAUROC +0.128 beyond conservation. But it does not survive the confound that matters most here: **study bias**. Drug targets are the most-studied proteins in existence, so they accumulate experimental interaction edges from research attention rather than biology (reverse causation). Study-intensity alone (literature-derived) predicts drug-targethood at AUROC 0.826, and once it is controlled — or once one uses a coexpression network that scores every gene uniformly regardless of study effort — the entire lift collapses (+0.128 → −0.004). So PPI-network centrality is *not* a confound-robust mechanistic signal for non-metabolic targets; it is largely a study-bias artifact. This is an important negative: it sharply separates FBA-essentiality (a genuine mechanism, which survived every control) from network centrality (which does not), and it means the non-metabolic half of target space remains genuinely hard — no clean, information-honest mechanistic signal for it has been found. (The first, unconfounded run would have been a false "mechanism generalizes" claim; the falsify-first protocol caught it before it was recorded.)

**The molecule half — the novel-chemotype ceiling of ligand-based hit-finding.**
Target identification is only half of discovery; the other half is producing candidate molecules for a target with no
activity data. This half has the same information-ceiling spine, and the field hides it: a 2025 audit of the standard
LIT-PCBA benchmark shows "zero-shot" virtual-screening scores are inflated by *analog leakage* and do not measure
recovery of genuinely novel chemotypes. We measured that ceiling directly (HIT1) on 30 curated ChEMBL targets
(MoleculeACE): given known binders, rank a library by chemical similarity (transfer) or by a learned model (QSAR on
ECFP4), and evaluate on actives split into analogs vs scaffold-*novel* chemotypes. Aggregate potency-ranking works well
(median AUROC 0.81 similarity / 0.90 learned) but is **analog-driven** (analog-vs-inactive AUROC 0.82). On scaffold-novel
chemotypes a learned model degrades sharply — 0.90 → 0.67 AUROC — but, importantly, does *not* collapse to random: it
retains a modest, noisy, above-random signal in most targets. So ligand-based hit-finding rides mostly on chemical
analogy, yet — unlike the target-ID conservation ceiling, where nothing beat conservation for a novel target — a learned
ligand model keeps partial traction on novel chemistry. This is a *soft* ceiling. (An automatic verdict initially read
this as a clean "learning generalizes beyond analogy"; that rested on a tautology — novel actives were *defined* as
low-similarity, so the similarity baseline was rigged to fail — and was corrected before recording. Caveats: this is
potency-transfer among measured binders, not needle-in-haystack screening; novel actives are rare in the data, so the
novel estimate is low-powered; the physics/structure floor for novel chemotypes — the only signal that does not depend on
chemical analogy at all — is the next test.)

**The front half — mechanism + selectivity, and a therapeutic-validity warning about the conservation workhorse.**
Target *recovery* is not the same as finding a *safe* target. FRONT1 extends the established antimicrobial-target framework
(essentiality + metabolic chokepoint + host non-homology), done fully zero-data (a metabolic model built de novo from the
genome + human-homology), and — the step the field's case-study papers skip — benchmarks it against the conservation
baseline and tests therapeutic validity. Two findings. First (recovery): mechanistic essentiality is the driver (it
reconfirms the MET result); metabolic *chokepoint* adds signal in E. coli but not M. tuberculosis, and soft selectivity is
weak — so chokepoint and selectivity do not robustly add beyond conservation+essentiality. Second, and more important
(safety): **ranking targets by conservation is therapeutically dangerous.** The proteins that are most conserved are exactly
the ones with essential human counterparts (host-toxic if inhibited) — in E. coli the host-toxic targets have a mean
homology bitscore of 123 vs 29 for the rest — so a conservation ranker actively *promotes* unsafe targets. And adding
selectivity as a soft feature does *not* reliably fix this: it removes host-toxic targets from the top of the list in two of
three organisms but, where those targets are also metabolically essential, the composite still surfaces them. The actionable
conclusion is that selectivity must be enforced as a **hard host-non-homology filter** (which removes all host-toxic targets
by construction), not learned as a soft feature — a concrete correction to the naive "rank by conservation" recipe.

Building that correction into the pipeline (E2E2) then exposes an honest tension that *both* recipes get wrong. The
corrected pipeline (mechanistic essentiality + hard host-non-homology filter + calibrated abstention) is safe by
construction — its shortlist contains no host-toxic targets, whereas the naive conservation shortlist would include several.
At the top of the list the recall looks nearly preserved. But the deeper cost is large and structural: a blunt
sequence-level host-non-homology filter *permanently excludes* 35–52% of all known drug targets — the ones that have a human
homolog — from the searchable space, even though many such targets are drugged *selectively* in practice by exploiting
binding-site differences a sequence filter cannot see. So neither recipe is right: ranking by conservation is unsafe, and
the sequence-level safety fix over-excludes. Genuinely correct selectivity requires binding-site-level pathogen-vs-host
difference reasoning — structural, not sequence-homology — which sequence transfer cannot provide. It is the same
information ceiling in a new place: sequence is enough to flag danger crudely, but not to reason about true selectivity.

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
