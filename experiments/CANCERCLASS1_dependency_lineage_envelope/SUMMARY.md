# CANCERCLASS1 — cancer-lineage deployment envelope for dependency target-ID: RESULT (honest, pre-reg gate NOT met)

**Reproduced ×2 byte-identical (sha c12bd3a). DepMap 22Q2 CRISPR (1,840 lines, 15,659 genes after excluding
1,049 pan-essential) × 22 cancer lineages, validated against IntOGen cancer drivers.** Data accessed via the
open figshare mirror of DepMap (the portal was behind a verification wall). Completes the human-arm envelope
picture (genetic → GENETICCLASS1; cancer → here).

## Verdict: the pre-registered FULL gate is NOT met by any lineage (first-class, reported as-is)
**No cancer lineage's selective dependencies STRONGLY recover IntOGen drivers** (FULL = enrichment ≥3 AND
permutation p<0.05 → 0/22). The pre-registered hypothesis ("envelope discriminates with ≥1 FULL class") therefore
**FAILS**. The envelope is a weaker two-level split:
- **CAPPED (14 lineages):** modest driver-recovery (enrichment 1.5–3× or p<0.05). Strongest: **lymphocyte**
  (enr 3.00, p 0.005 — just below FULL), **skin** (2.35, p 0.044), **colorectal** (2.33, p 0.045), breast/gastric/
  pancreas/liver/plasma_cell/peripheral_nervous_system (~1.9×, p≈0.12).
- **ABSTAIN (8 lineages):** no recovery above null — **bone, central_nervous_system, cervix, kidney, ovary,
  soft_tissue, upper_aerodigestive, uterus**.

## Honest reading (and why it's weaker than DEPEND1's pooled 0.80)
- Per lineage, dependency target-ID recovers **broad IntOGen drivers** only **modestly** (best ~3×), and not at
  all in a third of lineages. This is a genuine, calibrating bound on the cancer arm's lineage-level driver-
  relevance.
- The gap from DEPEND1 (pooled recovery@10 = 0.80) is honest and expected: DEPEND1 recovered **~26 curated KNOWN
  ACTIONABLE targets** (small, high-precision, oncogene-addiction cases); this uses the **~4,479-gene IntOGen
  driver set** (broad — includes tumor suppressors and context-specific drivers not expected to be selective
  dependencies), and a coarse lineage-selective score. So "modest driver-recovery per lineage" and "strong
  actionable-target recovery pooled" are both true and not in conflict.
- Non-circular: IntOGen drivers (from patient mutation data) are independent of the DepMap dependency observable.

## Contribution / integration
`cancer_lineage_transfer_table.json` = the cancer-arm deployment envelope: fire the dependency arm at **CAPPED**
confidence in 14 lineages (modest driver-relevance), **ABSTAIN** for driver-recovery in 8 (bone/CNS/ovary/…).
The honest decision-coverage analog of GENETICCLASS1 (disease-class) and the FBA organism-class table — with the
honest twist that at the lineage level, no context reaches FULL-grade driver-recovery.

## Scope
Cell-line dependency (DepMap), target-RELEVANCE (IntOGen driver overlap), NOT patient/clinical; a deployment-
envelope characterization of a validated arm (DEPEND1), not a new method. Reproduce: `python build_cancerclass1.py`.
