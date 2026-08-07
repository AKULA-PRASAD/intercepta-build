# DARK1 — pre-registered SAFETY / abstention-integrity test at the DARK-PROTEOME boundary

**Registered (Stage 1) BEFORE any scoring. Gates frozen below.** This tests the vision's OWN named deepest
frontier (VISION.md line 40-42: *"a truly novel fold with no sequence/structure homolog and no reference ligand
breaks target-ID, affinity-ranking, and scaffold transfer simultaneously ... the 'dark proteome' case is the
deepest version of the vision"*). The whole composite's integrity claim is: **fire a validated signal where its
transfer condition holds; ABSTAIN where none does.** The untested extreme is a protein that is genuinely
un-analyzable: NO detectable sequence homolog to anything drugged, NO usable/trustworthy structure, NO reference
ligand. **The POINT of this test is whether the system FAILS SAFE (abstains) or FAILS DANGEROUS (emits a
false-confident target call) at that outer edge.** A false-confident call on a dark protein is the WORST outcome
and is reported first-class as a CRITICAL integrity failure if it occurs.

This is NOT a discovery test. Nothing is expected to be "discovered" on dark proteins. The WIN is that the system
KNOWS it cannot analyze them and says so, while STILL firing on genuinely analyzable (drugged) input.

## Sets (both REAL, constructed by objective pipeline filters — no cherry-pick)

**DARK set (target 20-40 proteins).** Operationalized as proteins that are dark to BOTH target-ID signals:
- **No sequence homolog to any drugged protein:** ZERO mmseqs hits (e <= 1e-3, `-s 5.7`) against the ChEMBL
  drug-target reference (`intervene/drug_targets.fasta`, 2148 drugged proteins). Verified; hit-count reported.
- **No usable/trustworthy structure:** mean AlphaFold pLDDT (mean over CA-atom B-factors) **< 50**, OR no
  AlphaFold model exists. Per the vision's own pipeline rule ("gate on pLDDT/PAE"), a mean-pLDDT<50 model is NOT
  trustworthy enough to run structural homology on — that untrustworthiness IS the dark signal.
- **No reference ligand:** dark proteins are not themselves drug targets (not in the reference).
- Candidate POOL (for efficiency only; the two hard gates above define darkness): UniProt reviewed proteins
  carrying a disordered-region annotation, length 50-300, retrieved sorted by accession (deterministic). Each is
  then hard-filtered by the two gates. Candidates that turn out to HAVE a drugged homolog or a confident
  structure are DROPPED (reported as verification counts).

**CONTROL set (target ~20 proteins).** Real human ChEMBL drug targets (organism=Homo sapiens, SINGLE PROTEIN),
sampled deterministically (sorted-unique, fixed stride) from `drug_targets.tsv`; each with a fetchable AlphaFold
model (mean pLDDT >= 50). These SHOULD NOT be abstained on. (They are in the reference, so a strong sequence
homolog exists — legitimately: a known drugged protein must fire. Best NON-SELF homolog also reported so firing
is not read as pure self-identity tautology.)

## Signals run on BOTH sets (the composite's target-ID channels, faithfully reproduced)
1. **Sequence homology → drug targets** (INTERVENE1/GENERALIZE1 rule): mmseqs easy-search vs
   `drug_targets.fasta`, e <= 1e-3. **FIRES** iff best hit has bits > 0 and e <= 1e-3.
2. **Structural homology → drugged folds** (FOLD1/GENERALIZE2 rule, pLDDT-GATED): fetch AlphaFold structure;
   the structural channel is **usable only if mean pLDDT >= 50** (the vision's pLDDT gate). If usable, Foldseek
   easy-search the structure vs a 403-structure drugged-fold reference (FOLD1 `refstruct/`, cached ChEMBL
   drug-target AlphaFold structures); **FIRES** iff best `alntmscore` (TM) >= 0.5 (FOLD1 same-fold threshold).
   If mean pLDDT < 50 or no model, the structural channel CANNOT fire (abstains) — this is the correct dark
   behavior. **DANGER DIAGNOSTIC:** the UNGATED best Foldseek TM is also computed for dark proteins; if it is
   >= 0.5 that is a would-be false-confident structural call that ONLY the pLDDT gate prevents (a near-miss;
   reported loudly as evidence the gate is load-bearing).

**Per-protein composite verdict (frozen abstention rule).** A **target call** (FIRE) is emitted iff the sequence
signal fires OR the pLDDT-gated structural signal fires. Confidence tier = high (both fire), moderate (one),
none (ABSTAIN — neither fires). "High/moderate-confidence target call" == FIRE. This faithfully reproduces the
composite's rule: no discovery-grade signal above threshold -> ABSTAIN.

## PRE-REGISTERED GATES (frozen; this is a safety/integrity test)
- **G1 (CRITICAL — fail-SAFE):** the system ABSTAINS (emits NO target call) on **>= 90%** of the DARK proteins.
- **G2 (discrimination — not uselessly conservative):** the system FIRES (does NOT abstain) on **>= 70%** of the
  CONTROL proteins.
- **PASS = G1 AND G2.** The composite correctly abstains at the dark boundary while still firing on analyzable
  input.
- **FAIL of G1** = the system emits false-confident target calls on un-analyzable proteins == a CRITICAL
  integrity failure (fail-dangerous). Reported loudly, not re-run to a better number.
- **FAIL of G2** = it abstains on everything (uselessly conservative). Reported as-is.
- Additionally reported first-class: (i) count of any DARK false-confident calls; (ii) any UNGATED structural
  near-miss (dark protein with ungated TM >= 0.5 caught only by the pLDDT gate); (iii) verification hit-counts
  (dark seq-hits must all be 0; candidates dropped for having a drugged homolog / confident structure).

## Reproducibility
All network inputs (UniProt sequences, AlphaFold structures, pool list, frozen set membership) are fetched once
by `build.py` and cached under `$INTERCEPTA_DATA/dark1/`. `run.py` is pure scoring over the cached mmseqs/
foldseek/pLDDT tables; best-hit extraction uses max(bits)/max(TM) so it is order-independent and deterministic.
SHA-256 over sorted-key JSON payload (excluding `verdict`/`provenance`) is printed and must match across 2 runs.

## Scope / honest bounds
Tests abstention integrity at the homology-null + structure-null boundary; CPU-only; in-silico; not wet-lab.
n = one dark set + one control set. "Dark" is operationalized by two objective computational gates, not by a
proof that no homolog exists anywhere in nature. A PASS shows the composite fails SAFE at its stated outer edge;
it does not solve the dark-proteome problem (that remains open — the honest boundary this maps).
