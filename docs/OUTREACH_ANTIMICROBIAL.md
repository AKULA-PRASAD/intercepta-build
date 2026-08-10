# Antimicrobial wet-lab outreach — the #1 validation ask (ready to adapt & send)

*Purpose: secure ONE microbiology collaborator to run a pre-registered CRISPRi essentiality test of a
computationally-nominated antibacterial target. This is the single highest-leverage action for the program —
it converts an in-silico nomination into the first real-world confirmation. Everything here is honest by
design; the repo does the convincing. Drafts, not messages I will send — Prasad reviews, fills `[…]`,
confirms the current PI/contact, and sends.*

## Who to target (in priority order)
- Academic microbiology / bacterial-genetics labs already running **CRISPRi in *E. coli* K-12** (Mobile-CRISPRi /
  dCas9 systems) — lowest friction, our protocol is written for exactly this.
- Antimicrobial-resistance / neglected-disease groups and core facilities with routine bacterial knockdown.
- Synthetic-biology labs with dCas9 strains on hand.

## The honest one-paragraph hook
> We built and openly released a fully pre-registered, leakage- and confound-controlled computational method
> that nominates essential, host-non-homologous antibacterial targets **from a genome alone, with zero drug
> data**. It is validated *in silico* against experimental gene-knockout essentiality across six organisms
> (odds ratios 5–64, incl. held-out WHO priority pathogens) and in an analyst-blind, lock-before-reveal suite
> across three domains of life (4/7 novel organisms pass, failures on mapped boundaries) — but **it has never
> been tested in a living cell.** We are looking for one collaborator to run a single, cheap, pre-registered
> CRISPRi knockdown (~$200–400, ~2–3 weeks) of a target we nominate. It is designed to be turnkey and it
> **cannot return an uninformative answer**: a growth defect confirms a zero-data computational nomination;
> no defect falsifies it and recalibrates our method. Either outcome is publishable, and you are a co-author.

## The exact ask (turnkey)
- **Experiment:** pre-registered CRISPRi essentiality knockdown in *E. coli* K-12 MG1655 of one nominated
  broad-spectrum target — top picks **dxr/ispC** (MEP isoprenoid pathway; fosmidomycin target) or **murA**
  (cell-wall; fosfomycin target) — vs a non-targeting control, plus a known-essential positive control (**ftsZ**)
  and a dispensable negative control (**lacZ**).
- **Pre-registered readout & gate:** targeting guide reduces growth ≥5× vs non-targeting control (p<0.01, n≥3).
  ≥5× → first prospective wet-lab confirmation of a computational nomination. <5× → the prediction is wrong,
  reported as a first-class negative and the nominating signal is recalibrated.
- **What's already done for you:** real, specificity-checked sgRNA sequences (NCBI RefSeq NC_000913.3, not
  invented), controls, and the pre-registered analysis are in
  `experiments/CRISPRIDESIGN1_wetlab_ready/PROTOCOL.md` + `PREREG.md`. Cost/time ≈ $200–400 / 2–3 weeks, standard bench.
- **Honest scope (stated up front):** the sgRNAs are *predicted*, the "predicted efficiency" is a *heuristic*,
  and target essentiality is a *computational prediction* — **this experiment is exactly the test of whether
  that prediction is true in a real cell.** No clinical, drug, or selectivity claim is made.

## What the collaborator gets
Co-authorship; the turnkey protocol + pre-registered analysis; a rigorous, reproducible, open analysis layer
(pre-registration, reproduce-×2, first-class negatives; MIT-licensed; no controlled data). The bottleneck we
lack is precisely their asset — a bench.

## Cold-email draft (≈150 words — adapt, fill [ ], send)
> **Subject:** One pre-registered CRISPRi test of a zero-data antibacterial-target prediction (co-authorship)
>
> Dear Dr. [Name],
>
> I lead an open, pre-registered computational program (INTERCEPTA) that nominates essential, host-non-homologous
> antibacterial targets from a genome alone, with no drug data. It's validated in silico against experimental
> knockout essentiality across six organisms (incl. held-out WHO priority pathogens), but has never been tested
> in a cell. I'm looking for one collaborator to run a single, turnkey CRISPRi knockdown in *E. coli* K-12 of a
> target we nominate (top picks dxr/ispC or murA), with non-targeting + ftsZ/lacZ controls — a pre-registered
> ~$200–400, ~2–3-week experiment. The design (real sgRNAs, controls, locked readout) is ready:
> github.com/AKULA-PRASAD/intercepta-build → `experiments/CRISPRIDESIGN1_wetlab_ready/`. It cannot return an
> uninformative result, and either outcome is publishable with you as co-author. Would a 20-minute call this
> or next week be worth your time?
>
> Best regards, Prasad Akula — akula.pra@northeastern.edu

## What NOT to say (integrity guardrails)
No "drug", no "cure", no "validated target", no clinical/selectivity claims, no "any disease". The claim is
narrow and exact: *a zero-data computational method nominates essential targets; this is the first cellular test.*
