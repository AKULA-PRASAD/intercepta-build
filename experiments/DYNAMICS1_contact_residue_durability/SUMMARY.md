# DYNAMICS1 — SUMMARY

**Verdict: PASS (first-class, pre-registered, reproduced x2 BYTE-IDENTICAL, payload sha256
`fb6984c040869d869b6a770336b151137ed8297f7870abd960460f68f625a176`).**
First durability signal: **drug-contact-residue mutational tolerance separates HIGH- vs
LOW-resistance-liability targets where AMR1's whole-protein biology failed.**

## Pre-registered test (frozen in PREREG.md before scoring)
Hypothesis: liability is set by mutational tolerance of the specific DRUG-CONTACT residues, not
whole-protein conservation. Feature = mean ESM-2 (t30 150M) masked-marginal Shannon entropy over
drug-contact residues (<=4.5 A from the bound ligand) of a drug-bound PDB structure.
Gate = AUROC >= 0.75 AND MWU p < 0.05 AND AUROC > AMR1's 0.556.

## Result (n=15 feasible; 7 HIGH / 8 LOW; katG, pncA infeasible = no drug-bound structure)
| analysis | n (H/L) | AUROC | MWU p |
|---|---|---|---|
| PRIMARY mean contact entropy (gated) | 15 (7/8) | 0.839 | 0.029 |
| AMR1 whole-protein composite (ref) | 17 (9/8) | 0.556 | 0.74 |
| AMR1 F1 whole-protein conservation | 17 | 0.569 | - |
| secondary max contact entropy | 15 | 0.804 | - |
| secondary mean substitution-LLR | 15 | 0.839 | - |
| sensitivity drop pure substrates | 13 (7/6) | 0.833 | 0.051 |
| sensitivity clinical-drug-only | 10 (7/3) | 0.857 | 0.117 |

Gate PASSED on the pre-registered primary. Contact-residue dynamics lifts separation from
chance-level (0.556) to 0.839 - the follow-on AMR1's honest bound demanded.

## Mechanistic vindication (rpsL)
AMR1 failure mode: rpsL is the MOST whole-protein-conserved target yet HIGH-liability.
DYNAMICS1 resolves it: streptomycin-contact Lys on S12 (Lys46/47/91, K43-equivalents) have
masked-marginal entropy 2.65-2.68 nats (near-maximal tolerance) - matching clinical single-step
K43R escape. rpoB RRDR mean 2.75, inhA 1.92 (HIGH, tolerant); LOW cores uniformly constrained
(dxr 0.14, murA 0.18, murB 0.22, murG 0.32, ddlB 0.27). Signal invisible at whole-protein
resolution is visible at contact-residue resolution.

## Honest bounds (bind the PASS)
- Significance is n-fragile: effect size stable and beats AMR1 across every subset (AUROC
  0.83-0.86) but p<0.05 holds only for the full 15-target primary; drop-substrate p 0.051,
  clinical-drug-only (7H/3L) p 0.117. Small-n demonstration/bound, not a population estimate.
- Ligand-type confound (pre-declared): LOW mixes clinical drugs, research inhibitors, and 2 pure
  substrates (murG, murB) whose contacts are catalytically constrained by construction. AUROC
  holds (0.833) without them but significance weakens - signal real but partly ligand-aided.
- Within-HIGH misses: folP mean entropy 0.038, gyrA 0.51, embB 0.92 look constrained on the mean
  (their MAX contact entropy is high: 2.04/2.80); HIGH signal carried by rpoB/rpsL/inhA.
- ESM entropy is a PLM proxy for tolerance, NOT measured fitness; a single static structure
  misses induced-fit/allosteric/efflux/activator-loss resistance (activator-loss is why
  prodrug-activators katG, pncA are infeasible here).

## Reproducibility
Deterministic CPU ESM-2 (offline cache); structures+logits under $INTERCEPTA_DATA/dynamics1/.
Run x2 -> identical payload sha256 fb6984c0...; ESM masked-marginal recompute from scratch
(cache deleted) reproduced bit-identical entropies. No git commit; no data committed.

## One-line LEDGER verdict
PASS (pre-registered, reproduced x2, sha fb6984c0): drug-contact-residue mutational tolerance
(ESM-2 masked-marginal entropy) is the FIRST durability signal - separates HIGH/LOW resistance
liability at AUROC 0.839 / MWU p 0.029 (n=15, 7H/8L), beating AMR1's whole-protein 0.556/p0.74;
mechanistically the rpsL streptomycin-contact K43-equiv Lys entropy ~2.66 (max-tolerant) is the
exact residue AMR1's whole-protein conservation missed. BOUND: significance n-fragile
(drop-substrate p0.051, clinical-drug-only 7H/3L p0.117, AUROC holds 0.83-0.86); ligand-type
heterogeneous; ESM entropy is a PLM proxy not measured fitness; static structure misses
efflux/induced-fit; n=15 in-silico demonstration, not a population estimate.
