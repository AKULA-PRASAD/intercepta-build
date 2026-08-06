# TRANSFER1 — Label-free zero-screen dependency prediction for a host-embedded organism — SUMMARY

**VERDICT: PARTIAL (G1 PASS, G2 DECISIVE FAIL).** Transferring reference-ortholog essentiality predicts
P. falciparum essentiality above the OR>3 bar, but the entire beyond-conservation gain is the
PAN-ESSENTIAL / CONSERVED-CORE fraction. The SELECTIVE-dependency transfer (the signal that would justify a NEW
label-free capability) carries NO signal beyond conservation. Consequence: the COMPOSITE2 router should KEEP
ABSTAINING on novel host-embedded pathogens, or at most offer only the conserved-core, which conservation
breadth (REACH1) already provides. We must NOT claim label-free selective-dependency prediction for a
zero-screen organism. Reproduced x2 byte-identical.

- Payload SHA-256 (reproduced x2): ef47a342019173a410274423740fa0a1b4ec4d8a5181bea656af5502356b33b1
- Env: scipy Fisher + sklearn (intercepta-build), mmseqs2 v18 (bioinfo), CPU-only. Seed 42, 2000 bootstrap.
- Scope: in-silico orthology-transfer; held-out published screen (NOT wet-lab); ONE organism.

## Design (falsify-first)
P. falciparum treated as a SIMULATED zero-screen organism. Its essential genes are predicted LABEL-FREE by
transferring the essentiality/dependency status of its human (DepMap) and yeast (DEG) reciprocal-best-hit
orthologs, using NO Plasmodium screen. Predictions validated against the HELD-OUT Zhang 2018 piggyBac screen
(essential = "Non - Mutable in CDS"), never used to build the prediction. Decisive guard: essential genes are
broadly conserved, so orthology-transfer trivially recovers the conserved core; the un-gating-worthy signal
must BEAT a conservation-only baseline.

## Orthology coverage (honest denominator)
mmseqs2 easy-rbh (e<=1e-5, cov>=0.5 bidirectional): 1298 human RBH pairs, 1077 yeast RBH pairs, median identity
0.33 (cross-phylum). Universe U = 5215 PF3D7 genes carrying a Zhang label. Only 1437/5215 = 28% of U have ANY
human/yeast ortholog: P. falciparum is phylogenetically distant, so ~72% of adjudicable genes have no
detectable reference ortholog and are un-adjudicable by transfer (a hard ceiling on recall). Zhang base rate in
U = 0.62 (high; mechanically compresses odds ratios, as in GENERALIZE5).

## G1 - does transfer predict Zhang essentiality? PASS
Combined transfer (ortholog is human-pan-essential OR yeast-essential OR human-selective) vs Zhang over U:
OR = 3.82, Fisher p = 3e-54, precision 0.84, recall 0.23 -> clears the pre-registered OR>3 & p<0.01 bar.
Per-arm over U: common-essential OR 5.55 (prec 0.89); selective OR 1.96 (prec 0.76); combined OR 3.82.

## G2 (DECISIVE) - does it BEAT conservation and carry non-trivial (selective) signal? FAIL
- Conservation NULL-A ("gene has ANY ortholog at all") already predicts Zhang essentiality: OR = 2.13,
  p = 1e-29, precision 0.74 (vs base rate 0.62). Mere conservation is itself informative.
- G2i (transfer > conservation): PASS. OR_transfer - OR_conservation = 1.69, bootstrap 95% CI [1.17, 2.39]
  (excludes 0). So "the ortholog is essential" does add over "an ortholog merely exists."
- G2ii (selective beyond conserved-core): FAIL - the decisive negative. Isolating the SELECTIVE-only arm
  (selective orthologs that are NOT also pan/common) among ortholog-havers: OR = 0.90, p = 0.78 - NOT enriched
  for Zhang essentiality; indistinguishable from (slightly below) chance. The entire beyond-conservation gain
  comes from the COMMON/pan-essential arm (within-ortholog OR 4.61, p 3e-30). The selective-dependency signal -
  the DEPEND1-style context-specific dependency that would justify a genuinely NEW label-free capability - does
  NOT transfer to Plasmodium essentiality.
- NULL-B (pan-essential triviality): confirmed. 70% of the transfer-positive set is the pan/common
  conserved-core fraction; the remaining 30% (selective-only) carries no signal. The transferable signal IS
  essentially the conserved core.

G2 = G2i AND G2ii = FAIL (per PREREG, PASS required BOTH). -> VERDICT PARTIAL.

## What this means for the router (the actual decision)
- Do NOT un-gate the COMPOSITE2 router to claim label-free SELECTIVE-dependency prediction for a novel
  host-embedded organism. That capability is UNSUPPORTED here: the DEPEND1 selective-dependency signal does not
  survive organism-transfer to a zero-screen parasite (selective-only OR 0.90).
- What DOES transfer is exactly what we already had: broadly-conserved-core essentiality (pan-essential
  machinery). This is redundant with REACH1 conservation breadth (AUROC 0.86); it is not a new capability.
- Therefore the router should KEEP ABSTAINING on novel host-embedded pathogens for the DEPENDENCY signal, and
  any conserved-core essential list it emits must be labelled as conservation-derived (not selective
  dependency) and capped at the ~28% orthology-adjudicable fraction. This is the constitution's abstention
  integrity working as designed - the "we can predict a novel pathogen's targets with no screen" claim is
  correctly NOT made.

## Optional expr->dependency arm - not applicable (stated, not forced)
DEPEND1's expr->dependency Ridge learns expression<->dependency covariation across a PANEL of ~1000 cell-line
contexts. The Malaria Cell Atlas annotation provides only 4 developmental-stage mean-expression columns for ONE
organism, with no per-context dependency label to regress against (that IS the held-out truth). Four
stage-means cannot support a cross-context expr->dependency map; the paradigm does not apply to a single
organism. Reported as a limitation, not attempted as a false positive.

## Honest scope / threats
In-silico orthology-transfer; held-out PUBLISHED screen (not wet-lab); n=1 organism, blood-stage truth. RBH is
a strict orthology criterion - a looser homology map might raise coverage but would not manufacture a selective
signal that the strict, high-precision map shows is absent. The negative (selective does not transfer) is the
first-class result.

## Reproducibility
run.py -> results/TRANSFER1_metrics.json (sorted keys) + results/payload.sha256. Payload = sorted-key JSON of
numeric results excluding verdict/provenance; run twice, identical (ef47a342...). Seed 42. mmseqs RBH inputs
cached at $INTERCEPTA_DATA/transfer1/. No git commit/push; no data committed.
