# TRANSFERLAW1 — can the transfer-condition principle be made an a-priori law? VERDICT: HONEST NEGATIVE

**Reproduced ×2 byte-identical (`payload.sha256` = 2452ba3…). 18-organism panel + 6 P. falciparum reconstructions.**
A pre-registered attempt to convert the program's central *qualitative* transfer-condition principle into an
*a-priori, non-circular, quantitative* predictor — computable from a GEM's topology **before any validation** —
**FAILS**. Metabolic-autonomy topology does **not** predict whether FBA-essentiality target-ID transfers.

## Result (score S = z(log10_reactions) − z(blocked_fraction) − z(exchange_fraction) + z(gpr_coverage); GEM topology ONLY)
- **H1 — S vs transfer strength:** Spearman ρ(S, log OR) = **0.12**, 95% CI **[−0.42, 0.64]** (includes 0). **FAIL.**
- **H2 — S separates gate pass/fail:** AUROC = **0.625** (< 0.75 gate; barely above chance). **FAIL.**
- **H3 — within-organism P. falciparum GEM-swap:** across the 6 reconstructions (OR 0.86–3.07), ρ(S, OR) =
  **0.03, p = 0.96** — **no signal.** *(The metrics show a nominal "PASS" only because the pre-registered H3
  gate ρ>0 was too weak a threshold; the real value ρ≈0 means the autonomy score does NOT order the
  reconstructions by transfer. Reported transparently rather than changing the locked gate.)*

**The glaring misses that make the negative concrete:** *B. subtilis* has the **lowest** S (−3.44) yet passes
strongly (OR 12.48); *K. phaffii* has a **high** S (+1.61) yet fails (OR 2.36). The score does not track transfer.

## Interpretation (honest, non-circular)
The transfer-condition principle is **real but qualitative** — it is **not reducible to a-priori GEM topology.**
Because S used *only* model structure (zero experimental essentiality, zero OR — enforced), this negative is
clean: it is not a circularity artifact. **It bounds META1:** META1's directional "coverage predicts transfer"
hint was carried by **outcome-entangled** features (`n_fba_essential`, derived from the essentiality calls;
`base_rate`, from the lab data) — quantities *not available before validation*. Stripped to genuinely a-priori
topology, the predictive signal disappears. **There is no deployable a-priori transfer predictor from model
structure alone.**

## Why this is a valuable first-class negative (the vision's meta-question, answered honestly)
"Find drugs for any disease from minimal data" implies *knowing in advance where zero-data discovery will
work.* TRANSFERLAW1 tests that at the sharpest point and answers: **you cannot predict, from a new organism's
GEM alone, whether FBA target-ID will transfer to it — the deployment envelope requires the experimental
outcome (or base-rate), not just the model.** The transfer-condition principle stays an *operational, after-the-
fact* framework (route/abstain given a validation), not an *a-priori* law. This is a genuine, honest limit on
"know before you test," and it strengthens the manuscript's own framing (Limitation 14) with a pre-registered
falsification rather than an assertion.

## Discipline (no p-hacking)
The degenerate `biomass_synth_fraction` (saturated at 1.0 — GEMs are gap-filled to grow by construction) was
dropped **before** any S↔OR was computed, with documented reason (PREREG CORRECTION 2026-08-11); the four
remaining features and their mechanistic signs were **not** re-tuned to the data; the score was run **once** and
reported as-is. The alternative — iterating features until they predicted — is exactly the p-hacking this
design refused.

## Reproduce
`python compute_features.py` (topology features, cached) · `python score_law.py` (byte-identical; metabolic
conda env for COBRApy). GEMs/outcomes are existing committed/open artifacts; no new data committed.
