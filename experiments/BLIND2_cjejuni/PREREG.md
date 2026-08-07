# BLIND2 — pre-registered PROSPECTIVE-blind essentiality test on *Campylobacter jejuni* NCTC 11168

**Registered (Stage 1) BEFORE the experimental essential-gene SET was fetched, parsed, or used to build any prediction.**
This is the SECOND, independent prospective-blind essentiality validation, run under the identical protocol as BLIND1
(*N. gonorrhoeae*). Making the flagship result **n = 2** is the single most credibility-strengthening addition for the
program. Predictions are locked (hashed) first; the experimental answer is scored only in Stage 2. The lock sha recorded
below is the pre-reveal blindness commitment (the orchestrator commits the lock file; I cannot commit).

## Organism & rationale (Stage 0)
*Campylobacter jejuni* subsp. *jejuni* **NCTC 11168** (= ATCC 700819), genome NC_002163.
- **Genuinely never used** in ANY prior INTERCEPTA experiment. Verified: `jejuni` / `Campylobacter` appear in **0**
  experiment files; the ever-used organism token set is
  {ecoli, mtb, paeruginosa, bsubtilis, hpylori, salmonella, efaecalis, calbicans, pfalciparum, tbrucei, lmajor,
  kpneumoniae, saureus, abaumannii, ngonorrhoeae} — C. jejuni is not among them.
  (Note: *H. pylori* was the a-priori-preferred new-clade candidate but is DISQUALIFIED — `hpylori` is in the MET2/NEWBUG
  FBA-generalization panels, 33 code hits. Excluded honestly.)
- **NEW CLADE — epsilon-proteobacteria.** Every prior essentiality organism is a gamma-proteobacterium, Firmicute, or
  Actinobacterium. C. jejuni adds genuine phylogenetic breadth (the exact reason H. pylori was attractive).
- **WHO / clinical priority.** Leading bacterial cause of human gastroenteritis worldwide; **fluoroquinolone-resistant
  *Campylobacter* is a WHO priority / CDC "serious threat" AMR pathogen**; associated with Guillain–Barré syndrome.

## Deployment scenario (deliberate, honest hard path)
No curated BiGG genome-scale model exists for *C. jejuni* → we use a **de-novo CarveMe reconstruction from the UniProt
reference proteome** (UP000000799, 1623 proteins, default complete-medium carve, SCIP MILP solver). This is the real
"new pathogen, no curated model" deployment case — the same honest, weaker path used in BLIND1 (not a curated best case).
The GEM is built from the genome/proteome ALONE; no essentiality information enters the reconstruction or the FBA.

## Locked prediction (Stage 1 output)
COBRApy single-gene-deletion FBA on the CarveMe GEM; a gene is **FBA-essential if its knockout growth < 1% of WT**
(identical rule to BLIND1 and CROSSVAL). The full per-gene call (UniProt accession + symbol + fba 0/1 + KO growth ratio)
is written to `results/LOCKED_predictions.tsv` and the essential-accession set is hashed to
`results/LOCKED_predictions.sha256`. This computation is a deterministic function of the metabolic network only and is
provably independent of which genes are experimentally essential.

## Pre-registered experimental source (fixed now, fetched only in Stage 2)
**I WILL score against DEG accession `DEG1049`** — *Campylobacter jejuni* NCTC 11168 essential genome, **Mandal, Jiang &
Kwon (2017)** *BMC Genomics* 18:616, **Tn-seq** (166 essential genes), same strain NCTC 11168. Chosen (pre-reveal) over
the alternative NCTC 11168 set DEG1031 (Metris 2011) **because DEG1049 is a purely experimental Tn-seq screen**, whereas
Metris 2011 combined in-vivo data with their own in-silico FBA model — using it could leak model-derived essentiality into
the "experimental" truth. DEG1050 (strain 81-176) is rejected to avoid a strain gap.
- **Blindness note (transparent):** to choose the adjudication method I inspected the DEG1049 *identifier format only*
  (gene symbol + GI number; no locus-tag column populated). I did NOT use essential-set membership to build any
  prediction, and could not — the FBA lock is answer-independent. Full essential-set parsing happens only in Stage 2.

## Adjudication (fixed now)
Primary/robust: **sequence-homology bridge** — map DEG1049's essential PROTEIN sequences (from `DEG10.aa.gz`) onto our
CarveMe proteome by **mmseqs easy-search, pident ≥ 90** (same-species ortholog cutoff, set once, not swept), defining the
experimental-essential set in our accession space, then score the SAME LOCKED predictions (sha-verified unchanged). This
is the identical, namespace-independent method that adjudicated BLIND1 (whose symbol match failed on a locus-tag artifact).

## Pre-registered hypothesis & decision rule (fixed now — IDENTICAL to BLIND1)
**H1:** the locked FBA-essential set is enriched for the experimental essential set (DEG1049), 2×2 Fisher
**odds ratio > 3 AND p < 0.01** over the GEM (metabolic-subproteome) genes.
- **PASS** ⇒ prospective-blind evidence that the FBA-essentiality mechanism signal predicts experimental essentiality on a
  second, genuinely novel, pre-registered pathogen from a NEW clade → the flagship becomes n = 2.
- **FAIL** ⇒ reported first-class as an honest negative (e.g., sparse de-novo GEM for this microaerophilic organism, or the
  signal does not transfer to epsilon-proteobacteria) — recorded, not hidden or re-run to a better number.

## Scope (what a PASS does and does not show)
Essentiality-enrichment only; in-silico FBA vs a published Tn-seq screen (not a wet-lab experiment we ran);
prospective-BLIND in the lock/held-out sense; de-novo model; species/strain-level; NOT drug-target / selectivity /
clinical. Precision/recall are bounded by the metabolic subproteome.

## Sources & hashes (provenance)
- GEM proteome: UniProt UP000000799, `https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP000000799&format=fasta`
  → `$INTERCEPTA_DATA/blind2/cjejuni.fasta`  sha256 `1d978fc06e3a48d5e8721f1793a6682e05076ffb80f66cd0fd8bb247b285a9b4`
- GEM: CarveMe de-novo `$INTERCEPTA_DATA/blind2/cjejuni.xml` sha256 `368482f1b07da2071c29950f416e260d86d060f9de330b8ff0b19f4cb0c13600`
  (552 genes, 1566 reactions, WT growth 35.13)
- Essentiality: DEG `DEG1049` (Mandal 2017), sequences from `$INTERCEPTA_DATA/expval_deg/DEG10.aa.gz` (local, pre-existing).

## LOCKED-predictions commitment (blindness audit trail)
- `results/LOCKED_predictions.tsv` sha256 (essential-accession payload):
  **`dc42f715e4d88aa0006c63626da069f7f7eb21e172bdff4c4cdeabb715881506`**
- GEM: 552 genes, WT growth 35.133, **45 FBA-essential** genes predicted (frozen).
- Stage-1 locked BEFORE Stage-2 reveal. Recorded here as the pre-reveal blindness commitment.

---
## REVEAL OUTCOME (Stage 2, filled after the lock was recorded)
**PASS.** Sequence-homology bridge (mmseqs, pident≥90) adjudication of the LOCKED predictions (lock sha
`dc42f715…` verified intact — predictions unchanged). DEG1049's 166 essential proteins mapped into our accession space;
over the 552 locked GEM genes the 2×2 contingency is **12 both / 33 FBA-only / 43 exp-only / 464 neither** →
**odds ratio 3.92, Fisher p = 6.5e-04, precision 0.267, recall 0.218** → clears the pre-registered gate (OR>3, p<0.01).
- **n = 2 achieved:** a SECOND independent prospective-blind confirmation, on a genuinely novel pre-registered pathogen
  from a NEW clade (epsilon-proteobacteria), that FBA-essentiality predicts experimental essentiality.
- **Honest comparison to BLIND1** (OR 6.13, p 4.2e-6, prec 0.78, rec 0.10): BLIND2 is a weaker but clearly positive
  result — OR 3.92 sits closer to the gate boundary, precision is lower (0.27 vs 0.78) while recall is higher
  (0.22 vs 0.10). Consistent with a sparse de-novo GEM (45 FBA-essential of 552) for a microaerophilic organism.
- **Reproduced x2 byte-identical** — Stage-2 payload sha256 `47ad76aa900cfc2c5b14d0a8cae5805f4e7c3a838d83caf2d20e2d3c48dd3637`.
- **Meaning:** genuine prospective-blind evidence, replicated. Essentiality-enrichment only; de-novo GEM; in-silico vs a
  published Tn-seq screen; not drug-target/clinical; not wet-lab.
