# GENERALIZE5 — FBA essentiality on a PARASITE (*Plasmodium falciparum*, malaria) — SUMMARY

**GATE: FAIL — honest first-class negative** (same OR>3 AND p<0.01 gate as every bacterium; frozen before
scoring; orchestrator-verified). Reproduced ×2 byte-identical.
**payload sha256:** `276ee9b4c91973360692eff29d3553821f1bd9bccc628529fd5fef30e34eae8e`
**Evidence tier:** COMPUTED (in-silico enrichment; not wet-lab). n=1 parasite, blood-stage.

## Result
Over **424/475 mapped** metabolic genes (89% mapped — a clean map, so this is a real effect-size result, NOT
an INCONCLUSIVE namespace artifact): **OR 2.469, Fisher p 0.00217, precision 0.797, recall 0.201, AUROC 0.559.**
Contingency both 55 / FBA-only 14 / exp-only 218 / neither 137. p passes (significant, high precision) but
**OR 2.47 < 3 fails the pre-registered bar** → at the bacterial rigor standard, FBA-essentiality does **not**
generalize to the malaria parasite. Sensitivity def (MIS≤0.2): OR 1.55, p 0.064 → also FAIL.

## Sources
- GEM: **iPfal19** (curated *P. falciparum* 3D7, PARADIGM/Carey-Untaroiu-Papin; 475 genes) sha 7a19f5b7.
- Experimental truth: **Zhang et al. 2018 Science piggyBac saturation mutagenesis** (essential = phenotype
  "Non-Mutable in CDS"), via PlasmoDB redistribution (Science supplement paywalled) sha b8790819.

## Why it falls short (honest mechanism, not excuse)
1. **Base-rate compression:** 64% of the model's mapped metabolic genes are experimentally essential in
   *Plasmodium* — a high background rate mechanically caps the OR (precision 0.80 sits just above base rate
   0.64). The OR>3 bar was calibrated on bacteria with lower metabolic-essential base rates.
2. **Host-dependent metabolism → low recall (0.20):** *P. falciparum* salvages metabolites from the host
   erythrocyte; the default-medium GEM finds alternate routes, so 218 experimentally essential genes read as
   FBA-dispensable — exactly the pre-registered honest deployment risk for host-embedded parasites.

## Meaning
A real but weak signal (significant, high-precision, low-recall) that does **not** meet the bacterial standard
— mapping the boundary of where FBA-essentiality transfers from free-living bacteria to a host-dependent
eukaryotic parasite. Scope: enrichment only; one parasite/stage/model; not drug-target/clinical; not wet-lab.
