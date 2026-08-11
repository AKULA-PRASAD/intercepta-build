# NUCLEIC1 — nucleic-acid (siRNA) intervention design for undruggable targets (PRE-REGISTRATION)

*Locked 2026-08-11, before building the engine or scoring any target. The program's intervention half is the
weak side: small-molecule novel-target affinity is CLOSED at power (AFFINITY2/D2), and INTERVENE2 found the
large majority of validated selective cancer dependencies are UNDRUGGED (de-novo-chemistry-gated). RNAi needs
no binding pocket, so it **sidesteps the affinity wall** and reaches undruggable mRNA targets. MODALITY1 already
*recommends* ASO/siRNA for the right targets but the program has **no nucleic-acid DESIGN** — NUCLEIC1 builds
that missing module (Layer D5) behind MODALITY1's triage. Honest up front: the siRNA design SCIENCE is mature;
the contribution here is **systemic** (the first modality in the composite that turns undruggable target-IDs
into concrete, scored interventions, under the same abstention/provenance discipline) — NOT a new efficacy
algorithm. Every claim is scoped accordingly.*

## The engine (deterministic; cited, independently-validated rules; NO training data, NO ViennaRNA)
Input: a target mRNA (Ensembl canonical transcript cDNA). Enumerate all 19-mer duplex cores (21-nt with 3′-UU
overhangs). Score each by published, cited criteria — implemented faithfully to spec (verified in V1):
- **Reynolds 2004** 8-criterion rational-design set (GC 30–52%, low 3′-sense internal stability, position
  preferences A19/T10/A3, absence of G/C at 13, etc.).
- **Ui-Tei 2004** 4 rules (A/U at antisense 5′ end; G/C at sense 5′ end; ≥4 A/U in the antisense 5′ 7-mer; no
  GC stretch > 9).
- **Thermodynamic end-asymmetry** (Khvorova/Schwarz): antisense 5′ end less stable than sense 5′ end, computed
  from a nearest-neighbor ΔG table (deterministic; no folding tool).
- **Filters:** exclude immunostimulatory motifs (5′-UGUGU, GUCCUUCAA), homopolymer runs ≥4, extreme GC.
Composite efficacy score = documented weighted sum of satisfied criteria (weights fixed here, NOT fitted).
Off-target flag: antisense seed (positions 2–8) exact-match count against a reference transcript set (a human
3′UTR/CDS reference if fetchable; otherwise reported as DEFERRED, not faked).

## Validation (honest — no new-model claim)
- **V1 implementation fidelity:** deterministic unit tests — each rule reproduces its published spec on worked
  examples (pass/fail, byte-checked).
- **V2 positive control:** a FROZEN set of literature-validated POTENT siRNAs (cited, `positive_controls.json`)
  must score in the top fraction vs random 19-mers drawn from the same transcripts — pre-registered gate:
  potent-vs-random rank AUROC ≥ 0.65 (small n; honest wide CI). If it fails, that is reported first-class.
- *(Enhancement, not required: if a clean open measured-efficacy benchmark is obtainable via a reliable source,
  add held-out Spearman. Not blocking; absence is stated, not hidden.)*

## Systemic result (the actual contribution — measured)
For the **top-N = 30** (frozen) UNDRUGGED selective cancer dependencies from INTERVENE2 (the highest-confidence
undruggable targets; symbols frozen in DATA.md before scoring), fetch each canonical transcript and run the
engine. Report **coverage**: the fraction that yield ≥3 candidates passing all rule-gates + the off-target flag.
This quantifies how much of the program's undruggable set the new modality converts into concrete interventions.

## Integration
Wire behind `MODALITY1`'s `ASO_siRNA` recommendation: when the router recommends siRNA for a target, NUCLEIC1
emits the ranked candidate designs with per-rule provenance — the intervention half now produces an actual
design where before it stopped at "use an siRNA."

## Honest scope (binds every claim)
Implements CITED, independently-validated design rules (not a new/better efficacy model); outputs are in-silico
DESIGN HYPOTHESES, not validated knockdowns; demonstrated on a top-N set (not exhaustive); off-target is a
first-pass seed filter; not clinical. The novelty is systemic (first undruggable-reaching modality in the
composite), stated as such.

## Rigor
Reproduce ×2 byte-identical (deterministic; no RNG except a fixed-seed random-19-mer control, seed 42).
`results/NUCLEIC1_metrics.json` (sorted keys) + `payload.sha256`. Ensembl sequences + any reference set cached
to `$INTERCEPTA_DATA/nucleic1`, never committed. No gate changed post-hoc; deviations appended as dated CORRECTIONS.
