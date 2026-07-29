# engine/scouts — molecular discovery & docking
Scouts screen/rank molecules (GDSC screen, network perturbation, combinations, docking).
## HONEST STATUS (see ../../docs/audits/VISION_AUDIT.txt, ../../verification/)
- **Scout-2 is R-group SCAFFOLD-HOPPING, NOT de novo generative design.** Any output file named "denovo" is
  mislabeled and must be read as scaffold-hopped analogues.
- **INTC002** = scaffold-hopped AURKA inhibitor, ChEMBL novelty ≈ 0.266 — a **computational hypothesis only**,
  not a validated or novel drug.
- Pareto-ranking inputs (MoA/safety/synthesis dimensions) were partly **human-assigned** — not model-derived.
No validated novel molecule exists.
