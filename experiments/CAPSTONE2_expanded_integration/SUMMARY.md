# CAPSTONE2 — SUMMARY (integration proof of the fully-expanded composite)

**PASS against the frozen pre-registered gate (PREREG.md). Reproduced ×2 byte-identical, payload sha256
`d091582373d0e68c27b2f54ca439f056d5c5a2aae6ba3ebb145cf83546721708`.**

Drove the AUTONOMOUS router (`decide_auto`, ROUTERAUTO1 + COMPOSITE4) across 10 representative inputs — one per
covered class + two fail-safe cases — from objective `ProteomeFeatures`, and checked the gate frozen *before*
COMPOSITE4/AMR1 existed. No new science: composition of committed, reproduced-×2, validated arms.

## Result per case
| Case | Detected class | Signals fired | Conf | Modality |
|---|---|---|---|---|
| Bacterium (held-out K. pneumoniae) | bacterium | conservation_breadth, fba_essentiality, structural_homology | full | (pathogen: abstain) |
| Archaeon (M. maripaludis) | archaeon | conservation_breadth, fba_essentiality | full | (abstain) |
| Fungus (K. phaffii) | free_eukaryote | conservation_breadth, fba_essentiality | full | (abstain) |
| Virus (SARS-CoV-2) | virus | structural_homology (FBA correctly NOT fired) | full | (abstain) |
| Host-dep parasite +GEM (Toxoplasma) | host_dependent_parasite | fba_essentiality | **capped** | (abstain) |
| Human cancer (melanoma) | human_cancer | functional_dependency | full | SMALL_MOLECULE_INHIBITOR |
| Human monogenic (Pompe/GAA) | human_monogenic | causal_gene | full | ENZYME_PROTEIN_REPLACEMENT |
| Human complex (T2D, GWAS) | human_complex_disease | genetic_association | **capped** | SMALL_MOLECULE_INHIBITOR |
| **FAIL-SAFE** dark proteome | unknown | — | — | ABSTAIN |
| **FAIL-SAFE** novel zero-screen parasite | host_dependent_parasite | — (abstains, no GEM) | — | ABSTAIN |

## Gates
- **G1 routing correctness — PASS:** all 8 clear cases auto-detect the correct class and fire their validated
  signal(s) at earned confidence (host-dep-parasite + complex fired CAPPED, honoring their attenuated bounds).
- **G2 fail-safe abstention (HARD) — PASS:** both fail-safe cases abstain with **zero** signals fired, zero
  mis-fires (DARK1 / TRANSFER1 preserved).
- **G3 intervention fail-safe (HARD) — PASS:** **0** infeasible modality recommendations across all cases
  (every rec is a member of its feasible_set or ABSTAIN).
- **G5 honesty labels — PASS:** the capped/attenuated arms carry the flag; pathogen modality abstains (MODALITY1
  validated on human disease only); affinity wall / wet-lab / clinical labeled GATED.
- **G4 verdict-stability — PASS:** payload hashes ONLY `verdict_skeleton()` (class, fired signals, abstain,
  capped, modality) → reproduces byte-identical, immune to the reason-prose drift documented in LEDGER.

## Honest scope
This is "any disease → **honest decision coverage**, not a universal model": a validated-signal answer where a
signal transfers, an explicit abstention where none does. Every output is a target-PRIORITIZATION or
feasibility-TRIAGE **hypothesis with provenance** — not a drug, not clinical, not wet-lab-validated. The
small-molecule modality branch still hits the affinity wall (AFFINITY1, GPU-gated); wet-lab (CRISPRIDESIGN1)
and clinical remain out of scope by nature. The pathogen modality stage abstains because MODALITY1 was validated
on human disease, not pathogen intervention — stated, not hidden.
