# HOSTCTX2 — Host-exchange / medium curation on malaria — SUMMARY

**VERDICT: NEGATIVE, robust across 3 pre-registered media — no rescue.** Orchestrator-verified (prereg-frozen
anti-circularity host set; baseline anchor reproduced OR 2.469; sha reproduced). Reproduced ×2 byte-identical.
**payload sha256:** `e1fa792ddab868369e3fac1787d87dd781d939571c2884d0283bb777cd5b4178`
**Evidence tier:** COMPUTED (in-silico enrichment). n=1 parasite.

## Design (controlled A/B; only exchange bounds change)
Same iPfal19 GEM, Zhang-2018 truth, ID-map, and OR>3 & p<0.01 gate as GENERALIZE5. Host-RBC-available nutrient
set FROZEN by independent published citations BEFORE scoring — anchored on RPMI 1640 (Moore 1967; the medium
*P. falciparum* is cultured in continuously, Trager & Jensen 1976) + established salvage biology (hypoxanthine
Divo 1985, hemoglobin Goldberg 2005, isoleucine Liu 2006, pantothenate Saliba 1998, host lipid pool Mi-Ichi
2006). **Anti-circularity confirmed:** membership fixed by citation, never by OR/Zhang effect; only WT-growth
feasibility (outcome-blind) was computed at design time.

## Result (baseline vs curated)
| medium | WT | OR | p | precision | recall | n_ess(map) | gate |
|---|---|---|---|---|---|---|---|
| baseline (open) | 31.40 | **2.469** | 2.2e-3 | 0.797 | 0.201 | 69 | FAIL |
| PRIMARY (RPMI+Hx+Hb) | 15.57 | 2.431 | 3.1e-4 | 0.783 | **0.304** | 106 | FAIL |
| STRICT (minimal salvage) | 15.56 | 2.202 | 1.0e-3 | 0.769 | 0.304 | 108 | FAIL |
| PERMISSIVE (+RBC purines) | 31.29 | 2.226 | 1.2e-3 | 0.772 | 0.286 | 101 | FAIL |

**No medium clears OR>3; none even raises OR above baseline** (curation slightly lowers it). Better p reflects
more genes called, not tighter enrichment. **Precision-collapse guard: clean NEGATIVE, not artifact** —
precision holds 0.77–0.78 (≥0.5), essential set grows modestly 69→106 (<2×, no balloon).

## Honest mechanism (why it partly worked but not enough)
Unlike E-Flux (HOSTCTX1, byte-identical), curation DOES move the set: PRIMARY adds **28 new true-positive
essentials, 0 losses** (recall 0.20→0.30) — closing spurious salvage forces biosynthesis and makes genuine
essentials load-bearing. But it also adds **9 false positives**, so the true:false ratio of new calls (~76%)
≈ the baseline ratio (~80%) → enrichment (OR) is unchanged. Changing network content/boundary is
*directionally correct* (does what expression context couldn't) but **insufficient** to clear OR>3. 190
experimentally-essential genes remain FBA-dispensable — residual topology bypass persists.

## Failure modes reported (not hidden)
- **GEM lipid gap-fill ceiling:** iPfal19 cannot synthesize its biomass membrane-lipid pool de novo; closing
  `EX_lipid_c` makes WT infeasible → kept open as host-scavenged lipid (Mi-Ichi 2006), with the explicit caveat
  that lipid-biosynthesis essentials cannot be recovered by this model.
- **Topology bypass persists:** boundary curation cannot shut the residual salvage routes.

## Meaning
Combined with GENERALIZE5 (plain FBA FAIL) and HOSTCTX1 (E-Flux NEGATIVE), this is the **third confirmed
NEGATIVE**. The malaria wall is structural and only *partially* addressable by boundary curation (recall up,
enrichment flat). A genuine rescue would require explicit **host–parasite compartment modeling** and a GEM
with **de-novo lipid biosynthesis** — i.e. better model *content*, beyond what iPfal19 + boundary edits allow.
