# META1 — The Transfer Law (retrospective meta-analysis of committed FBA-vs-experimental results)

**Reproduced x2 byte-identical.** `payload.sha256 = 7514a746de248f39a29e44a75aad22cf01fe6a4bb375d84ef4681eddb4aa63b0`
Retrospective meta-analysis of our OWN committed in-silico metrics JSONs. Correlational, small-n,
NOT new wet-lab evidence. Does NOT re-open or flip any committed pass/fail verdict.

## INTEGRITY NOTE — parsing bug caught and fixed (first-class)
The first pass read N. gonorrhoeae from `BLIND1_reveal.json` (a symbol-match artifact that mapped only
1/613 genes -> OR 0), NOT from the correct sequence-bridge file `BLIND1_reveal_seqbridge.json` (OR 6.13,
Fisher p 4.24e-6, precision 0.781 — the adjudication comparable to BLIND2-7's mmseqs bridge). That
mislabeled our flagship blind PASS as a "genuine null," which is impossible (OR>>1 requires
lift>1). **Fixed:** the parser now reads the seqbridge reveal; N. gonorrhoeae correctly enters as a
PASS (base_rate 0.389, precision-lift **2.01**, fair-gate PASS). Full audit printed OR/precision/
base_rate/lift for all 19 organisms; this was the ONLY corrupted row — every other row parsed sanely
(all OR>1 rows had lift>1). No organism entered the regression/reclassification with a null OR.

## Dataset
**19 unique organisms assembled, 0 unparseable** (12 bacteria, 1 archaea, 6 eukaryote; 11 curated
GEMs, 8 de-novo CarveMe). **15 committed PASS / 4 committed FAIL.** Sources: CROSSVAL_curated (6),
VALIDATE_essentiality_deg (2 ESKAPE), BLIND1-7 (7), GENERALIZE4/5 + HARDENF1/P1 (4). E. coli /
K. pneumoniae / M. tuberculosis each had a second de-novo GEM/truth-set result — kept as a
within-organism sensitivity set, not double-counted. PARARESOLVE1/2 used as a within-Pf base-rate
demonstration.

The 4 committed FAILs: S. pneumoniae (bacteria, de-novo), K. phaffii (yeast), P. falciparum, T. brucei
(parasites). NOTE: C. albicans (p=4e-3) PASSES (OR 13.9); the "highly significant but sub-gate fungus
(p~4e-5)" in the brief is **K. phaffii** (BLIND5). Among prokaryotes, 11/12 bacteria + the archaeon
PASS; the lone bacterial "fail" (S. pneumoniae) is underpowered, not a true null.

## Driver results (effect sizes, CORRECTED)
| Hypothesis | Test | Result | Read |
|---|---|---|---|
| H1 GEM size/quality | Spearman log_OR ~ n_gem_genes | rho=+0.55, p=0.014 (n=19) | strongest single driver |
| H1 | curated vs de-novo, pass rate (MWU) | p~0.06 (curated pass more) | marginal, same direction |
| H1 | log_OR ~ adjudicable FBA-ess count | rho=+0.35, p=0.14 | ns |
| H1 | log_OR ~ FBA-essential *fraction* | rho=+0.12, p=0.61 | ns (fraction != driver; absolute size is) |
| H2 base rate (across-organism) | Spearman log_OR ~ base_rate | rho=-0.33, p=0.17 | weak/ns across organisms |
| H2 base rate (WITHIN organism) | PARARESOLVE iPfal19 | base 0.64->OR 2.47 FAIL; base 0.46->OR 3.67 PASS | decisive — same GEM, gate flips on base rate alone |
| H3 host-dependence | pass rate | 1/3 host-dep pass vs 14/16 free-living; MWU p=0.25 | directional, underpowered (n=3) |
| H4 domain (euk) | Spearman log_OR ~ euk | rho=-0.39, p=0.096 | eukaryote->lower OR, marginal |
| Multivariable | OLS log_OR ~ base_rate+log(n_fba)+euk+host | R2=0.29, adj R2=0.085; NO predictor p<0.05 (all CIs span 0); VIF<2.3 | underpowered — drivers inseparable multivariably |
| Logistic on pass | statsmodels Logit | near-separation, directional only, not evidence | — |

## Driver ranking (honest, univariate-only survives)
1. **GEM size/quality** — the only robustly significant driver (n_gem_genes rho=+0.55, p=0.014;
   curated>de-novo pass p~0.06). Bigger/curated reconstructions transfer better.
2. **Domain (prokaryote > eukaryote)** — directional (rho=-0.39, p=0.096), not significant.
3. **Host-dependence** — directional failure signal (1/3 pass) but n=3, ns; fully collinear with
   "eukaryote" (all 3 host-dependent organisms are eukaryotes) so H3/H4 are not separable here.
4. **Base rate across organisms** — weak/ns; but a real WITHIN-organism confound (below).

**Multivariable verdict: UNDERPOWERED / DIRECTIONAL-ONLY.** n=19, 4 fails; the four candidate drivers
are mutually entangled (all host-dependent organisms are eukaryotes; eukaryote GEMs are also smaller
and drawn from higher-base-rate screens). No predictor is individually significant in the joint model
(adj R2=0.085). We cannot cleanly attribute the boundary to any single cause.

## KEY deliverable — is the OR>3 gate base-rate-confounded? **YES.**
1. **Within-organism, decisive (PARARESOLVE, unaffected by the fix):** identical GEM (iPfal19) on
   P. falciparum vs a high-base-rate screen (Zhang piggyBac, base 0.64) gives OR 2.47 -> FAIL, but vs a
   lower-base-rate screen (Bushell barseq, base 0.46) gives OR 3.67 -> PASS. Same biology, same model;
   the gate flips purely on base rate. High base rate compresses OR toward 1 even at high precision
   (Pf-Zhang precision 0.80 but base 0.64 => lift only 1.24).
2. **A real-signal-under-compression FAIL exists:** K. phaffii is a committed FAIL (OR 2.36) yet
   carries a strongly significant enrichment (Fisher p=4.0e-5, precision-lift 1.7). The raw OR>3 gate
   suppresses it.

### Proposed base-rate-FAIR gate (SECONDARY LENS — does NOT flip any committed verdict)
Augment "OR>3" with **Fisher p<0.01 AND precision-lift (precision / base_rate) >= 1.5** (equivalently
report the base-rate-invariant LR+). CORRECTED reclassification table (4 committed FAILs):
| organism | OR | base_rate | precision | precision-lift | OR-gate | fair-gate | interpretation |
|---|---|---|---|---|---|---|---|
| K. phaffii | 2.36 | 0.170 | 0.293 | 1.73 | FAIL | **PASS** | REAL signal, OR-compressed |
| P. falciparum | 2.47 | 0.644 | 0.797 | 1.24 | FAIL | fail | compressed & genuinely small (precision 0.80 barely beats base 0.64) |
| S. pneumoniae | 2.96 | 0.162 | 0.357 | 2.20 | FAIL | fail (p=0.06) | underpowered (only 5 co-essential genes) |
| T. brucei | 0.64 | 0.323 | 0.238 | 0.74 | FAIL | fail | genuine null (FBA no better than base rate; 337-gene GEM) |

(For reference, N. gonorrhoeae — now correctly parsed — is OR 6.13, lift 2.01: PASS under BOTH gates.)
So of 4 fails: 1 real-signal-under-compression (K. phaffii), 1 compressed-but-truly-small
(P. falciparum), 1 underpowered (S. pneumoniae), 1 genuine failure (T. brucei).

## The honest quantitative transfer law
Transfer is driven, in order of evidential strength, by **(1) GEM size/curation quality** (only
significant driver, rho~+0.55) and directionally by **(2) being prokaryotic/free-living rather than a
eukaryotic host-dependent parasite**; the pass/fail **OR>3 gate is base-rate-confounded** (proven
within-organism), so some eukaryote "fails" (notably the K. phaffii fungus, p=4e-5) are real signal
compressed by high experimental base rates, not absence of signal. With the parsing fix, **all 12
prokaryotes-plus-archaeon effectively transfer** (11/12 bacteria + archaeon PASS; the one bacterial
"fail," S. pneumoniae, is underpowered). The single genuine null is **T. brucei** — a tiny 337-gene
de-novo GEM (21 FBA-essential), a coverage failure consistent with driver #1. The boundary is best
described as **"model quality x base-rate-fair effect size,"** not a hard prokaryote/eukaryote wall.

## Honest scope / limits
Small n (19; 4 fails) -> multivariable separation underpowered (adj R2=0.085, no predictor significant).
Heterogeneous truth sets (Tn-seq/INSeq/CRISPR/curated-annotation/piggyBac/barseq) and heterogeneous GEM
sources are themselves confounds; base rate is partly a truth-set artifact (PARARESOLVE proves it).
domain/host/coverage/base-rate are mutually collinear. Correlational, in-silico only; explains the
observed boundary, is NOT new wet-lab evidence, does not re-open any committed verdict. OR=0 organisms
were Haldane-Anscombe-corrected (+0.5/cell) for finite log_OR.
