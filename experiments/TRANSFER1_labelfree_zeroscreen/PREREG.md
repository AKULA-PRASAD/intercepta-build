# TRANSFER1 — Label-free zero-screen dependency prediction for a host-embedded organism — PRE-REGISTRATION

*Written and frozen BEFORE any scoring against the held-out truth. Rigor constitution: truth over vision,
falsify-first, negatives first-class, reproduce ×2 byte-identical, pre-registered numeric gates, MANDATORY
conservation-null guard. This is the most false-claim-prone test in the program: a bogus "we can predict a
novel pathogen's targets with no screen" claim would be catastrophic. The decisive guard is the CONSERVATION
NULL — the transferred signal must BEAT mere conservation, not merely recover the conserved core.*

Date frozen: 2026-08-05. Seed: 42. Bootstrap resamples: 2000.

---

## 0. The question (COMPOSITE2 un-gating test)
The COMPOSITE2 router ABSTAINS on a novel host-dependent pathogen because we have no VALIDATED dependency
signal that needs no screen of its own. DEPEND1 validated functional-dependency for cancer cell lines INCLUDING
a label-free expr→dependency arm, but that arm was validated on held-out DepMap cell LINES, never on a true
zero-screen ORGANISM. Can we legitimately un-gate the router? I.e. can we predict a host-embedded organism's
essential/dependency genes LABEL-FREE (no screen for it) and BEYOND a trivial conservation baseline?

DESIGN: treat *P. falciparum* as a SIMULATED zero-screen organism. Predict its essential genes purely by
transferring the essentiality/dependency status of its human/yeast orthologs (reference organisms that HAVE
been screened). Validate against its held-out real screen (Zhang 2018), which is NEVER used to build the
prediction. The decisive question is whether the transfer beats a conservation-only null.

## 1. Data (open, public; not committed)
- TARGET proteome: `$INTERCEPTA_DATA/tid1/proteomes/pfalciparum.fasta` (UniProt, 5361 proteins).
- HELD-OUT VALIDATION TRUTH (never used to build prediction): Zhang 2018 essentiality via the PlasmoDB
  annotation `$INTERCEPTA_DATA/generalize5/Pf3D7_gene_annotations.csv` column `Zhang Phenotype`
  (essential = "Non - Mutable in CDS"). Same source/definition as GENERALIZE5. The annotation's `Uniprot IDs`
  column links proteome UniProt accessions → PF3D7 gene IDs.
- REFERENCE (SOURCE, screened) organism 1 — HUMAN: DepMap CRISPR/Chronos gene-effect
  `/Users/kalki/kaalcura/data/depmap_crispr_gene_effect.csv` (frozen sha256
  `d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00`; reused from DEPEND1). Human proteome
  for orthology: `$INTERCEPTA_DATA/tid1/proteomes/human.fasta` (UniProt, GN= gene symbols).
- REFERENCE organism 2 — YEAST: *S. cerevisiae* essentials from DEG `$INTERCEPTA_DATA/generalize4/deg_euk/
  deg_annotation_e.csv` (rows with organism == "Saccharomyces cerevisiae"; 1110 essential gene names; same
  source as GENERALIZE4). Yeast proteome fetched from UniProt (reviewed, organism 559292, 6733 proteins) at
  `$INTERCEPTA_DATA/transfer1/scerevisiae.fasta`.
- NOTE (no leakage): DEG also contains *Plasmodium falciparum* rows — these are NOT used (would leak the
  target). Only yeast rows are used from DEG.

## 2. Orthology (FROZEN a priori)
mmseqs2 `easy-rbh` reciprocal-best-hit (`~/miniconda3/envs/bioinfo/bin/mmseqs`, v18): P. falciparum proteome
vs human proteome, and vs yeast proteome. Thresholds FROZEN: `-e 1e-5 -c 0.5 --cov-mode 0` (default sensitivity
`-s 5.7`). Only RBH-mappable genes are adjudicable for a transfer prediction; genes with no ortholog are
"no ortholog" (predicted NOT essential by transfer). Orthology coverage and percent-identity distribution are
reported honestly. Mapping: proteome UniProt acc → human UniProt (RBH) → human gene symbol (via human.fasta
`GN=`); proteome UniProt acc → yeast UniProt (RBH) → yeast gene name (via yeast.fasta `GN=`).

## 3. Unit of analysis and universe
The unit is the **PF3D7 gene** (deduped: multiple UniProt accessions of one PF3D7 gene are collapsed; the gene
has an ortholog if ANY of its accessions has an RBH; its ortholog is essential/selective if ANY does).
**Universe U** = PF3D7 genes reachable from the proteome that carry a Zhang phenotype label. Adjudication is at
this gene level. Coverage of U by orthology is reported (this is the honest denominator).

## 4. Reference dependency/essentiality labels (FROZEN; reuse DEPEND1/GENERALIZE4 definitions)
- HUMAN (DepMap, reuse DEPEND1): dependent call Chronos effect < −0.5; `dep_frac(g)` = fraction of lines
  dependent. **PAN/COMMON-ESSENTIAL**: `dep_frac > 0.90`. **SELECTIVE**: `0.01 ≤ dep_frac ≤ 0.50`
  (the context-specific, non-trivial dependency band — the DEPEND1 selective set).
- YEAST (DEG): binary essential set (S. cerevisiae). Yeast has no selective/pan resolution, so it contributes
  only to the COMMON-essential and conservation arms.

## 5. LABEL-FREE prediction variants (FROZEN a priori — use NO Plasmodium screen)
A PF3D7 gene is predicted essential/dependency if:
- **(a) COMMON-essential transfer**: its human ortholog is PAN/COMMON-essential (DepMap dep_frac>0.90) OR its
  yeast ortholog is DEG-essential. (Conserved-core essentiality.)
- **(b) SELECTIVE-dependency transfer**: its human ortholog is in the DepMap SELECTIVE band. (The non-trivial,
  context-specific dependency signal — the one that would justify a NEW capability.)
- **(c) COMBINED**: (a) OR (b).

## 6. MANDATORY conservation-null baselines (the decisive guard)
- **NULL-A (conservation-only)**: PF3D7 gene has ANY human OR yeast RBH ortholog at all (mere conservation).
- **NULL-B (pan-essential triviality)**: separate the transfer signal into its PAN/COMMON-essential (conserved
  core) fraction vs its SELECTIVE fraction, and report whether any signal exists BEYOND the pan-essential/
  conserved-core fraction.

## 7. Scoring (2×2 Fisher one-sided "greater"; base rate reported)
Over Universe U, for each predictor (NULL-A, variant a, b, c) build the 2×2 vs Zhang-essential and report
OR, Fisher p, precision, recall, and the Zhang base rate in U.

**DECISIVE "beyond-conservation" test** (transfer-positive ⊆ conservation-positive, so the formal test of
"does ortholog essentiality add signal beyond ortholog PRESENCE" is a 2×2 restricted to genes WITH an
ortholog): among genes that HAVE any ortholog, test predictor-positive vs Zhang. Computed for variant (c), and
separately for the PAN/COMMON arm and the SELECTIVE-only arm (selective orthologs that are NOT also pan/common).
Also report a bootstrap 95% CI (seed 42, 2000 resamples) on the difference `OR_transfer(c) − OR_NULL-A`.

## 8. PRE-REGISTERED GATES (fixed here, before scoring)
- **G1 (transfer works vs Zhang)**: combined transfer (variant c) predicts Zhang essentiality with **OR > 3
  AND Fisher p < 0.01** over U.
- **G2 (DECISIVE — beats conservation, non-trivial)**: BOTH
  (i) transfer(c) enrichment is SIGNIFICANTLY ABOVE the NULL-A conservation-only baseline — operationally the
      bootstrap 95% CI on `OR_transfer(c) − OR_NULL-A` excludes 0 (transfer OR strictly above conservation OR);
  AND
  (ii) the SELECTIVE arm carries signal BEYOND the pan-essential/conserved-core fraction — operationally the
      SELECTIVE-only within-ortholog 2×2 shows OR > 1 with p < 0.05 (selective orthologs, over and above the
      conserved core, are still enriched for Zhang essentiality).
- **VERDICTS**:
  - **PASS = G1 AND G2** → a real, non-trivial transferable dependency signal exists → the router may
    un-gate host-embedded organisms WITH stated caveats.
  - **PARTIAL = G1 only** (transfer predicts Zhang, but the signal is ONLY the conserved-core/pan-essential
    fraction; selective/beyond-conservation fails G2) → conservation already covers it; the router should KEEP
    abstaining on novel host-embedded organisms, or offer ONLY the conserved-core (which conservation already
    provides), and must NOT claim label-free selective-dependency prediction.
  - **NEGATIVE = neither** (transfer does not even beat the OR>3 bar vs Zhang).

## 9. Optional expr→dependency arm — HONEST non-applicability (decided a priori)
DEPEND1's expr→dependency Ridge LEARNS expression↔dependency COVARIATION across a PANEL of ~1000 cell-line
contexts. The Malaria Cell Atlas data in the annotation provides only 4 developmental-stage mean-expression
columns (Ring/Trophozoite/Schizont/Gametocyte) for ONE organism — not a panel of independently-screened
contexts. There is no per-context dependency label to regress against for Plasmodium (that is precisely the
held-out truth we may not use), and 4 stage-means cannot support a cross-context expr→dependency map. The
paradigm therefore does NOT apply to a single organism. This is reported as a stated limitation, NOT forced.

## 10. Reproducibility
All RNG seeded (42). Payload = sorted-key JSON of all numeric results EXCLUDING `verdict`/provenance
(`git_sha`,`timestamp_utc`,`python`,`sklearn`,`runtime`). Script run twice; SHA-256 of payload printed and
matched; `results/payload.sha256` written. NEVER git commit/push. NEVER commit data.
