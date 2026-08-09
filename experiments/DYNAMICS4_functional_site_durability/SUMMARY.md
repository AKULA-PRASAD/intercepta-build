# DYNAMICS4 — functional-site durability: PARTIAL (reproduced x2, sha 26f56491)

**Attempts to solve:** DYNAMICS3's central caveat — fpocket's blind top pocket is usually NOT the real
drug site (0.0 crystal-site overlap for embB/gyrA/parC/rpoB/rpsL/CYP51/mraY/murA/murE). DYNAMICS4
defines the durability site from KNOWN UniProt functional annotations (Active + Binding + catalytic
Site), a principled site needing neither a drug-bound crystal nor a blind-pocket guess. FROZEN ESM-2
masked-marginal entropy metric reused verbatim (DYNAMICS1/2/3). Reproduced x2 byte-identical, sha
`26f56491919788ee19e046b9ac50b5da4d18e7d780c3d1471a767701130967c5`.

## Feasibility (resolved before gates)
**21/26 annotated** (>=3 functional-site residues within domain span; bar >=15 -> PASS).
**5 INFEASIBLE**: embB, rpoB, rpsL, HIV1_PR (zero UniProt functional-site annotation), gyrA (1<3).
Real method bound — it cannot score targets whose drug site is a non-catalytic interface UniProt does
not annotate (rifampicin RNA channel/rpoB, streptomycin 16S/rpsL, arabinosyltransferase/embB,
fluoroquinolone QRDR/gyrA). **4 of the 5 dropped are HIGH-liability with high crystal entropy — so
dropping them makes discrimination HARDER, not easier (reported as-is, not tuned).**

## Pre-registered gates — 2 of 3 blocks met -> PARTIAL
- **G1 agreement PASS but does NOT beat fpocket:** Spearman rho(functional-site vs crystal durability)
  = **0.687**, p 5.8e-4 (bar rho>=0.5 -> PASS) — but **< DYNAMICS3 fpocket 0.714**. On the
  numbering-aligned 16-target head-to-head it is **0.465 vs fpocket 0.594** — fpocket agrees BETTER.
- **Crystal-site OVERLAP FAIL (missed the material-improvement bar):** annotated mean overlap
  **0.297 vs fpocket 0.244** on the same 16 — higher, but only +0.054 (bar >=0.25 AND >=+0.10 abs
  -> FAIL). The annotated site is more uniform; fpocket's mean is buoyed by lucky direct hits
  (HSV1_TK 1.0, ddlB 0.79, dxr 0.64).
- **G2 discrimination PASS at the bar, weak:** AUROC(functional-site vs HIGH) = **0.75** exactly (bar
  >=0.75 -> PASS) but MWU p **0.060** (not significant) — below fpocket 0.899 / crystal 0.827.
  Head-to-head 16: annotated AUROC 0.764 vs fpocket 0.909.

## The ONE genuine win (directionally validates the premise)
On the specific wrong-pocket targets DYNAMICS3 flagged as **0.0** overlap, the annotated site DOES
recover the real drug site where the blind pocket completely missed:
CYP51 **0.17**, mraY **0.39**, murA **0.46**, murE **0.35** (fpocket 0.0 on all four); also folP
0.50 vs 0.25, inhA 0.33 vs 0.07. Only parC stays 0.0 (fluoroquinolone QRDR–DNA interface is not an
annotated functional site — a genuine bound). So "annotations hit the real drug site more reliably
than a blind pocket" is TRUE per-target on enzymes where the drug binds the catalytic/substrate
pocket — but this local accuracy does NOT translate into better durability RANK or HIGH/LOW
discrimination than fpocket overall.

## Application
ispE (E. coli, P62615): functional-site durability **0.56** (13 annotated residues) vs DYNAMICS3
fpocket 1.89 — now anchored on the annotated CDP-ME/ATP site rather than a blind pocket; a more
principled advisory value, still a PLM proxy.

## HONEST LEDGER VERDICT
**PARTIAL — not a clean SOLVE.** The annotated functional site fixes the wrong-pocket MISSES per
target (recovers the true drug site on 4/5 enzymes fpocket scored 0.0), confirming annotations give a
more accurate site *where the drug binds the catalytic pocket*. BUT it does NOT beat fpocket's blind
pocket where it counts: agreement (rho 0.687 < 0.714; 0.465 < 0.594 head-to-head), discrimination
(AUROC 0.75, p 0.06 n.s., vs 0.899), and mean overlap improvement (+0.05, below the +0.10 bar). The
method also structurally cannot see the strongest HIGH signals (embB/rpoB/rpsL/HIV_PR unannotated),
which is precisely why discrimination weakens. Interpretation: fpocket's blind functional cavity,
though often the "wrong" site, captures a broader mutational-tolerance signal that ranks and
discriminates better than the sparse, sometimes drug-irrelevant annotated catalytic residues. The
annotated site is the more *principled and locally accurate* durability anchor for characterized
undrugged enzymes, but is NOT a superior durability predictor to DYNAMICS3's blind pocket.

## Scope
In-silico; n=21 feasible (16 numbering-aligned head-to-head); ESM entropy = PLM proxy, not measured
fitness; static; annotation-dependent (coverage bounded to characterized enzymes with UniProt
Active/Binding/catalytic-Site features); annotated catalytic site != drug site for interface drugs
(QRDR/RNA-channel). Not tuned to pass — the PARTIAL/negative-leaning bound is the reported result.
