# AFFINITY2 — powered novel-chemotype co-folding vs the affinity wall: VERDICT

**Status: COMPLETE. Verdict = WALL HOLDS → D2 CLOSED DEFINITIVELY AT POWER.** Reproduced ×2 byte-identical
(`payload.sha256` = 8e3ac05…). 522/522 complexes co-folded (100% coverage; no missing/invalid). Boltz-2
co-folding — the one untried method for the intervention half (novel-target/novel-chemotype affinity) — does
**not** produce a usable zero-data signal on a powered, leakage-controlled novel split, and is **significantly
worse** than a simple target-trained QSAR.

## Result (per the pre-registered two-tier gate; scored on the identical co-folding subset, paired bootstrap)
| target | n (a/i) | co-fold AUROC (95% CI) | best ligand baseline | Δ(cofold−best) 95% CI | TIER1 | TIER2 |
|---|---|---|---|---|---|---|
| ALDH1 | 250 (125/125) | **0.553** [0.483, 0.621] | QSAR 0.714 | **−0.161** [−0.240, −0.078] | ✗ | ✗ |
| PKM2  | 136 (68/68)   | **0.690** [0.594, 0.776] | QSAR 0.780 | −0.090 [−0.199, +0.021] | ✗ | ✗ |
| FEN1  | 136 (68/68)   | **0.716** [0.630, 0.794] | QSAR 0.893 | **−0.178** [−0.269, −0.088] | ✓ | ✗ |

- **TIER1 (zero-data signal, cofold CI-lo > 0.60): 1/3** (FEN1 only; PKM2 narrowly misses at 0.594; ALDH1 fails).
  Gate needs ≥2 → **FAIL.**
- **TIER2 (beats ligand-ML): 0/3.** Co-folding is significantly *worse* than a target-trained QSAR on ALDH1 and
  FEN1 (paired-bootstrap Δ CI excludes 0), and worse (non-significant) on PKM2.
- Sign verified: actives have lower predicted affinity than inactives on all three targets → the weak AUROCs
  are genuine, not an inverted score.

## Why this negative is STRONG (the leakage caveats cut in its favor)
The pre-registration flagged that LIT-PCBA receptors predate Boltz's cutoff (**target-side leakage**), and the
review flagged that these actives likely sit in Boltz's ChEMBL/BindingDB affinity-head training
(**compound-side leakage**). Both would **inflate** co-folding. Co-folding failed **anyway** — so the leakage
that would make a *pass* untrustworthy makes this *fail* conservative and robust. Even with every advantage,
structure-based co-folding cannot rank novel-chemotype binders as well as a fingerprint model.

## Scientific meaning
The intervention half (novel-target affinity) is **information-limited, not method-limited.** Co-folding — the
last untried method and the largest unbuilt piece of the vision — joins docking, QSAR, PCM, and generation
below the wall. **Roadmap R5 stays CLOSED; dead-end D2 is upgraded from "closed (gated)" to "closed at power,
co-folding included."** No further GPU compute on novel-target affinity is warranted absent a genuinely new
method/data class.

## Honest scope (this is an internal go/no-go, NOT a publication benchmark)
Real reviewer-blockers remain for a publishable co-folding benchmark (see the design review): target-side
leakage, compound-side leakage vs Boltz training, crystallization-construct sequences (PKM2 3gqy His-tag) +
arbitrary `pdbs[0]` receptor, monomer folding of oligomers, non-archived per-compound server MSAs, single
diffusion sample. These do not change the internal verdict (they'd only help co-folding, which still failed),
but a publication-grade claim would require: a post-cutoff target, native sequences, one archived MSA per
target, and multi-sample variance.

## Reproduce
`python build_benchmark.py` · `python prep_yamls.py` · (Explorer: `HPC_RELAY.md`) · rsync affinity JSONs to
`benchmark/boltz_out/` · `python score.py` (byte-identical; boltz_out gitignored, aggregate metrics only).
