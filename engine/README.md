# engine/ — INTERCEPTA computational modules (code only; data via ../data/MANIFEST.md)

Imported from `~/INTERCEPTA/code` during consolidation. **Code only** — no data, no results, no models.
Each module's `README.md` states its HONEST status against the verified evidence (`../LEDGER.md`,
`../verification/`, `../docs/audits/`). Where in-code docstrings overclaim (legacy), the module README is
authoritative. Nothing here is a validated clinical tool.

| Module | What it is | Honest status |
|---|---|---|
| `ode/` | phenotype/PK-PD ODE models | Directional combination-RANKING, NOT quantitative predictor (2/6 trials, 0/3 g-rate) |
| `net/` | multi-layer disease knowledge-graph builders | Real infrastructure; "universal 15-layer net" is aspirational |
| `scouts/` | molecular discovery / docking | Scout-2 = scaffold-hopping NOT de novo; INTC002 = hypothesis (novelty 0.266) |
| `kaalcura/` | R_prolif/R_emt/R_ddr axes | R_prolif ≈ GGI (validated proliferation prognostic, NOT novel); no therapy selection |
| `velocity/` | scVelo RNA-velocity pipeline | "Time-machine/pre-resistance" NOT TESTABLE on current data |
| `cell_fm/` | Geneformer embedding/tokenization | Third-party model, downloaded externally, never vendored |
| `aml/` | BeatAML analysis + round2 multimodal | Multimodal AUROC 0.643 (FALSIFIED pre-reg ≥0.70); verified wins = NPM1→Cabo, NRAS→MEK, DNMT3A→Dasatinib |
| `synergy_pk/` | synergy + PK + stratification | Exploratory; earlier PK sourcing bug fixed in ODE v4.1 |
| `pipeline/` | orchestration, loaders, jobs, round3 GBM | Infrastructure / live-test |
| `audit/` | self-audit + reproducibility scripts | Generates the honest ledgers — a core asset |
