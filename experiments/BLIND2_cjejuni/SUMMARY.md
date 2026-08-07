# BLIND2 — SUMMARY (prospective-blind essentiality test #2)

## One line
**PASS.** On *Campylobacter jejuni* NCTC 11168 (epsilon-proteobacteria — a NEW clade, WHO/CDC-priority AMR pathogen,
never used before), LOCKED de-novo FBA-essentiality predictions are enriched for experimental essentiality (DEG1049,
Mandal 2017 Tn-seq): **OR 3.92, Fisher p 6.5e-04, precision 0.267, recall 0.218** -> clears the pre-registered gate
(OR>3 & p<0.01). This makes the prospective-blind flagship **n = 2**.

## Protocol (identical to BLIND1)
- **Stage 0** organism chosen by novelty + WHO priority + open genome-wide essentiality screen + obtainable GEM, NOT by
  predicted ease. H. pylori (preferred new clade) was DISQUALIFIED for prior use (MET2/NEWBUG panels); C. jejuni chosen,
  same epsilon-proteobacterial clade, 0 prior uses.
- **Stage 1 (LOCK)** de-novo CarveMe GEM from the UniProt proteome ALONE -> COBRApy single-gene-deletion FBA (essential if
  KO growth <1% WT) -> results/LOCKED_predictions.tsv + sha256. No experimental data consulted. Deterministic x2.
- **Stage 2 (REVEAL)** fetch DEG1049; mmseqs sequence-homology bridge (pident>=90) maps essential proteins into our
  accession space; score the SAME locked predictions (sha-verified intact); 2x2 Fisher (one-sided). Reproduced x2
  byte-identical.

## Result
| metric | BLIND2 (C. jejuni) | BLIND1 (N. gonorrhoeae) |
|---|---|---|
| clade | epsilon-proteobacteria (NEW) | beta-proteobacteria |
| GEM | de-novo CarveMe (552 genes, 45 FBA-ess) | de-novo CarveMe (619 genes, 32 FBA-ess) |
| essentiality | DEG1049 Mandal 2017 Tn-seq (166) | DEG1055 Remmele 2014 (751) |
| contingency (both/FBAonly/exponly/neither) | 12 / 33 / 43 / 464 | 25 / 7 / 216 / 371 |
| odds ratio | **3.92** | 6.13 |
| Fisher p | **6.5e-04** | 4.2e-06 |
| precision / recall | 0.267 / 0.218 | 0.78 / 0.10 |
| gate OR>3 & p<0.01 | **PASS** | PASS |

## Honest verdict
A genuine, weaker-but-positive prospective-blind replication. OR 3.92 sits nearer the gate boundary than BLIND1's 6.13;
precision is lower (0.27 vs 0.78) and recall higher (0.22 vs 0.10) — the expected profile of a sparse de-novo GEM for a
fastidious microaerophile. The signal transfers to a new phylogenetic clade. Scope is essentiality-enrichment only:
in-silico FBA vs a published Tn-seq screen (not wet-lab), de-novo model, not drug-target/selectivity/clinical.

## Provenance / hashes
- proteome cjejuni.fasta sha256 1d978fc06e3a48d5e8721f1793a6682e05076ffb80f66cd0fd8bb247b285a9b4
- GEM cjejuni.xml sha256 368482f1b07da2071c29950f416e260d86d060f9de330b8ff0b19f4cb0c13600
- LOCK (blindness commitment) sha256 dc42f715e4d88aa0006c63626da069f7f7eb21e172bdff4c4cdeabb715881506
- Stage-2 payload sha256 47ad76aa900cfc2c5b14d0a8cae5805f4e7c3a838d83caf2d20e2d3c48dd3637 (reproduced x2)
- data under \$INTERCEPTA_DATA/blind2/ (NOT committed); code + results under this dir.
