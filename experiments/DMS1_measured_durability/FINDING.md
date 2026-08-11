# DMS1 — FEASIBILITY VERDICT: the durability axis (D9) is not cleanly reopenable with current open data

**Status: NOT-EXECUTABLE-AS-DESIGNED (honest feasibility bound, not a scored result).** DMS1 pre-registered a
clean, non-circular reopen of D9 durability via the "measured DMS fitness" trigger: test whether measured DMS
mutational-tolerance separates resistance positions (CARD) from others, head-to-head vs the failed proxies
(AMR1 conservation 0.556; DYNAMICS5 PLM-entropy 0.446). Deep-research feasibility (all data cached, checked
before any scoring) shows the design cannot be instantiated non-circularly, for a concrete, evidenced reason.

## The blocking finding (evidence, 2026-08-11)
The **observable** (measured DMS fitness) and the **label** (curated resistance positions) do not co-occur on
the same proteins:
- **Proteins WITH DMS fitness = resistance ENZYMES / DHFR:** `BLAT_ECOLX` (TEM-1 β-lactamase, L=286) matches CARD
  only as a **protein-homolog model** ("TEM-1", identity 1.00) — a resistance *gene*, carrying **0 resistance-SNP
  positions**; best CARD *variant*-model match identity 0.09. `AACC1_PSEAI` (AAC, L=177): best CARD match 0.18.
  `DYR_ECOLI` (DHFR, L=159): best CARD homolog "dfrA35" 0.27 (acquired dfr genes, different sequence) — no clean
  variant-model. → **no per-position resistance labels** for the DMS-covered proteins.
- **Proteins WITH CARD resistance-position labels = drug TARGETS** (gyrA, rpoB, pncA, katG, rpsL, …, DYNAMICS5's
  198-target / 1162-position panel): ProteinGym has **no DMS** for any of them (a repo-wide index scan returned
  only `DYR_ECOLI`, which itself does not align to a CARD variant-model).
- **Net:** the measured-fitness landscape and the resistance-liability ground truth exist for *disjoint* protein
  sets. A non-circular, multi-target measured durability test cannot be built from current open data.

## Why the other trigger (FEP/MD ΔΔG) is also blocked (from the prior ultra-analysis)
The AMR1 durability panel has no drug-matched fragile-vs-durable contrast (durable targets are undrugged → no
drug-bound structure, no resistance mutations → FEP ΔΔG undefined), and a novel alchemical-FEP campaign run
blind over the HPC relay is inherently iterative (the forbidden trial-and-error).

## Honest verdict (D9 update)
**D9 durability stays CLOSED, and the gate is now precisely characterized:** it is not merely "GPU-gated" — it is
gated on a **missing dataset that pairs per-position mutational fitness with resistance-liability on the same
panel of actual drug targets** (e.g., DMS-under-drug-selection of gyrA/rpoB/folA/pncA across organisms). Neither
pre-registered reopen-trigger (FEP/MD ΔΔG; measured DMS fitness) is executable non-circularly with today's open
data. This is a genuine attempt's honest result, recorded so future work (or that specific dataset) can reopen
it — not a scored negative, and not forced into a fake n=1 demonstration.

## What would reopen it (the concrete gate)
A multi-target, drug-selection DMS (or FEP-tractable drug-bound structures) covering ≥~10 antibacterial drug
targets with both (a) per-position fitness and (b) resistance-liability labels. That is a **data-acquisition /
wet-lab** dependency, not a computation — consistent with `COMPUTATIONAL_COMPLETENESS_LEDGER.md` (durability ∈
the resource-gated residual).

*No `results/` metrics are written: DMS1 produced a feasibility verdict, not a score. CARD + DMS data cached in
`$INTERCEPTA_DATA`, never committed.*
