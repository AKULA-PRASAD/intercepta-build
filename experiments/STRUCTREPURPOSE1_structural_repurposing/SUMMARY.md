# STRUCTREPURPOSE1 — Structural drug repurposing vs the sequence baseline — SUMMARY

**VERDICT: NEGATIVE** — G1 (validation) PASS, G2 (expansion) fails the mandatory NULL/promiscuity guard.
Orchestrator-verified (prereg frozen before scoring; agent run-logs show sha reproduced ×2 byte-identical;
metrics confirm the numbers). **payload sha256:** `6fb7d520227a86746d299c35d12fef58c4763795a83a8faa401f36842d1d31a8`
**Evidence tier:** COMPUTED (in-silico fold homology; AF models). n=1 novel pathogen.

## What was built
- Drug-target STRUCTURE reference: AlphaFold **v6** for 2118 ChEMBL drug-target accessions → **2009 fetched /
  109 404**; Foldseek DB.
- Query A (validation): 11 canonical E. coli antibacterial targets.
- Query B (coverage): the 32 FBA-essential N. gonorrhoeae targets (BLIND1 accessions 404 in AF DB → mapped to
  FA 1090 orthologs at 98.7–100% identity; 32/32 obtained).
- **NULL reference (decisive):** size- and organism-composition-matched random NON-drug proteins (n=2009).

## Findings
- **G1 validation — PASS (11/11).** Structural best-homolog independently recovered the correct drug-class MoA
  for all 11 canonical targets at TM 0.94–1.00 (MurA/fosfomycin, gyrase+topo/fluoroquinolone, RpoB/rifamycin,
  DHFR, DHPS, D-Ala-D-Ala, Alr, DXR). Matches INTERVENE1's sequence 9/9 — the structural mapper recovers real
  pharmacology.
- **G2 expansion — NEGATIVE (promiscuity).** INTERVENE1 sequence coverage 1/32; raw structural at TM≥0.50 =
  18/32 (looks like a jump) **but the random-protein NULL = 25/32 — MORE than drug targets.** Threshold sweep:
  0.40 → 30 vs 31; 0.50 → 18 vs 25; 0.60 → 14 vs 19 (drug-target never clears the null). Per-query
  strictly-better-than-null 7/32; specific **and** enzyme-family-plausible = **1** (ispC/dxr, dtTM 0.96 vs
  randTM 0.46) — the *same single target* sequence already covered. Guard (n_dt≥2×n_rand AND ≥3 margin) fails
  decisively; spurious top hits confirm mechanistically (tmk→"mitochondrial complex I", gmk→"Ca channel").

## Honest conclusion (and what it changes)
Structure **validates** (G1 11/11) but does **NOT** genuinely expand the addressable-target fraction beyond
sequence's 1/32 once promiscuity is controlled: at the "same-fold" threshold an essential bacterial enzyme
finds a same-fold neighbor in almost any large structure set (drug-target or random alike), so raw structural
"coverage" is a **fold-census artifact**, not repurposing signal (FOLD2's warning, now quantified). The
mandatory null caught exactly the false claim the constitution named. **Honest coverage remains 1/32.**
→ Revises FAILURE_AUDIT **F1**: the intervention narrowness is **not** repurposing-fixable (sequence *or*
structure); repurposing is fundamentally bounded to targets with a genuine drugged homolog, so novel-target
intervention is **de-novo-chemistry-gated (F4)**, not a coverage bug. Scope: in-silico hypotheses; no
whole-cell/selectivity claims; AF-DB coverage bounds the reference; n=1 novel pathogen.
